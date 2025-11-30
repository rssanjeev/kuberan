"""
Metadata Enrichment Service - Provider-based metadata collection and enhancement.

Strategy: MASSIVE-first approach for foundational data
- MASSIVE: Primary source for company reference data (detailed, structured)
- YFinance: Fallback and historical enrichment (unlimited quota)
- Alpha Vantage: Financial statements only (rate-limited)

SECURITY: Only stores public company information, no sensitive data.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta

from app.core.logging_config import get_logger
from app.services.providers import provider_registry
from app.services.providers.base_provider import DataType
from app.services.providers.load_balancer import load_balancer
from app.repositories.provider_repository import provider_repository
from app.models.provider import CompanyOverview, DataSource

logger = get_logger(__name__)


class MetadataEnrichmentService:
    """
    Provider-based metadata collection and enrichment service.
    
    Strategy: MASSIVE-first for foundational data
    
    Pipeline:
    1. MASSIVE: Collect detailed reference data (company info, IDs, logos)
       - 7,200 calls/day limit
       - Most detailed foundational data
       - Includes CIK, FIGI, official identifiers
       - Logo/branding URLs
       
    2. YFinance: Fallback and historical enrichment
       - Unlimited quota
       - 20+ years historical data
       - Used when MASSIVE quota exhausted
       
    3. Alpha Vantage: Financial statements only
       - Rate-limited (5 calls/day free tier)
       - Income statement, balance sheet, cash flow
       - Use sparingly for detailed fundamentals
    
    LoadBalancer will automatically select best provider based on:
    - Data type requested
    - Provider quota availability
    - Provider reliability
    """
    
    def __init__(self):
        """Initialize metadata enrichment service."""
        # Staleness thresholds (days)
        self.STALENESS_THRESHOLDS = {
            "ETF": 30,      # ETFs change slowly
            "Stock": 7,     # Companies update quarterly
            "Critical": 1   # High-priority watchlist tickers
        }
    
    async def collect_foundation_metadata(self, ticker: str) -> Optional[Dict]:
        """
        Collect foundational company metadata using MASSIVE (Polygon.io) exclusively.
        
        MASSIVE provides:
        - CIK, FIGI identifiers
        - Company logos and branding
        - SIC codes, list dates
        - Employee counts, locale data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Metadata dictionary or None if failed
        """
        try:
            logger.info("Collecting foundation metadata via MASSIVE", extra={"ticker": ticker})
            
            # Get MASSIVE provider directly (avoid re-initializing all providers)
            provider = provider_registry.get_provider_by_name("MassiveProvider")  # Use full name, not prefix
            
            if not provider:
                logger.error("MASSIVE provider not available", extra={"ticker": ticker})
                return None
            
            logger.info(
                "Using MASSIVE provider for foundation data",
                extra={"ticker": ticker, "provider": "MassiveProvider"}
            )
            
            # Use MASSIVE ticker details endpoint for comprehensive metadata
            if not hasattr(provider, 'fetch_ticker_details'):
                logger.error("MASSIVE provider missing fetch_ticker_details method", extra={"ticker": ticker})
                return None
                
            logger.info("Fetching ticker details from MASSIVE", extra={"ticker": ticker})
            details = await provider.fetch_ticker_details(ticker)
            
            if not details:
                logger.warning(
                    "MASSIVE returned no ticker details (ticker may be delisted or invalid)",
                    extra={"ticker": ticker}
                )
                # Mark this ticker as failed so we don't retry it
                await self._mark_ticker_as_failed(ticker, "not_found_in_massive")
                return None
            
            # Map MASSIVE response to our metadata structure
            metadata = self._map_massive_to_metadata(details)
            metadata["source_provider"] = DataSource.POLYGON
            metadata["enrichment_status"] = "foundation"
            metadata["fetched_at"] = datetime.utcnow()
            
            logger.info(
                "Foundation metadata collected via MASSIVE",
                extra={
                    "ticker": ticker,
                    "enrichment_status": metadata["enrichment_status"],  # DEBUG: Verify status before return
                    "has_logo": bool(details.get("branding", {}).get("logo_url")),
                    "has_cik": bool(details.get("cik"))
                }
            )
            
            return metadata
        
        except Exception as e:
            logger.error(
                "Failed to collect foundation metadata via MASSIVE",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return None
    
    def _map_massive_to_metadata(self, massive_details: Dict) -> Dict:
        """
        Map MASSIVE ticker details to our metadata structure.
        
        MASSIVE provides comprehensive reference data:
        - Official identifiers (CIK, FIGI)
        - Detailed address and contact
        - Logo and branding assets
        - Company structure (shares outstanding, type)
        - Market information
        
        Args:
            massive_details: Response from MASSIVE fetch_ticker_details
            
        Returns:
            Mapped metadata dictionary
        """
        # Extract branding
        branding = massive_details.get("branding", {})
        logo_url = branding.get("logo_url")
        icon_url = branding.get("icon_url")
        
        # Extract address
        address = massive_details.get("address", {})
        
        # Build extended_data with MASSIVE-specific fields
        extended_data = {
            # Official identifiers
            "cik": massive_details.get("cik"),
            "composite_figi": massive_details.get("composite_figi"),
            "share_class_figi": massive_details.get("share_class_figi"),
            
            # Branding
            "logo_url": logo_url,
            "icon_url": icon_url,
            
            # SIC classification
            "sic_code": massive_details.get("sic_code"),
            "sic_description": massive_details.get("sic_description"),
            
            # Additional details
            "list_date": massive_details.get("list_date"),
            "total_employees": massive_details.get("total_employees"),
            "active": massive_details.get("active", True),
            "locale": massive_details.get("locale", "us"),
        }
        
        metadata = {
            "ticker": massive_details.get("ticker"),
            "name": massive_details.get("name"),
            "description": massive_details.get("description"),
            "exchange": massive_details.get("primary_exchange"),
            "currency": massive_details.get("currency_name", "usd").upper(),
            "asset_type": self._classify_massive_asset_type(massive_details.get("type")),
            "market_cap": massive_details.get("market_cap"),
            "website": massive_details.get("homepage_url"),
            "country": "US",  # MASSIVE is US-only
            
            # Detailed address
            "address": address.get("address1"),
            "city": address.get("city"),
            "state": address.get("state"),
            "zip_code": address.get("postal_code"),
            "phone": massive_details.get("phone_number"),
            
            # Company structure
            "shares_outstanding": massive_details.get("share_class_shares_outstanding"),
            
            # Store MASSIVE-specific fields in extended_data
            "extended_data": extended_data,
        }
        
        return metadata
    
    def _classify_massive_asset_type(self, massive_type: str) -> str:
        """
        Classify asset type from MASSIVE type field.
        
        MASSIVE types: CS (Common Stock), ETF, ADRC (ADR Common), etc.
        
        Args:
            massive_type: MASSIVE type field
            
        Returns:
            Asset type: "Stock", "ETF", "ADR", etc.
        """
        if not massive_type:
            return "Stock"
        
        massive_type = massive_type.upper()
        
        if massive_type == "ETF":
            return "ETF"
        elif massive_type in ["CS", "COMMON"]:
            return "Stock"
        elif "ADR" in massive_type:
            return "ADR"
        elif "PREFERRED" in massive_type:
            return "Preferred Stock"
        else:
            return "Stock"  # Default
    
    def _get_provider_data_source(self, provider) -> DataSource:
        """
        Map provider class to DataSource enum.
        
        Args:
            provider: Provider instance
            
        Returns:
            DataSource enum value
        """
        provider_name = provider.__class__.__name__
        
        if "Massive" in provider_name:
            return DataSource.POLYGON
        elif "YFinance" in provider_name:
            return DataSource.YFINANCE
        elif "AlphaVantage" in provider_name:
            return DataSource.ALPHA_VANTAGE
        elif "Finnhub" in provider_name:
            return DataSource.FINNHUB
        else:
            return DataSource.YFINANCE  # Default
    
    async def collect_base_metadata(self, ticker: str) -> Optional[Dict]:
        """
        Legacy method - redirects to collect_foundation_metadata.
        
        Maintained for backward compatibility with existing jobs.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Metadata dictionary or None if failed
        """
        logger.info(
            "collect_base_metadata called (legacy) - redirecting to collect_foundation_metadata",
            extra={"ticker": ticker}
        )
        return await self.collect_foundation_metadata(ticker)
    
    async def enrich_with_alpha_vantage(
        self,
        ticker: str,
        existing_metadata: Optional[CompanyOverview] = None
    ) -> Optional[Dict]:
        """
        Stage 2: Enrich metadata with Alpha Vantage OVERVIEW.
        
        This is rate-limited (25 calls/day free tier). Use selectively.
        
        Args:
            ticker: Stock ticker symbol
            existing_metadata: Existing CompanyOverview document to merge with
            
        Returns:
            Enriched metadata dictionary or None if failed
        """
        try:
            logger.info("Enriching with Alpha Vantage", extra={"ticker": ticker})
            
            # Get Alpha Vantage provider from provider registry
            av_provider = provider_registry.get_provider_by_name("AlphaVantageProvider")
            if not av_provider:
                logger.error("Alpha Vantage provider not available")
                return None
            
            # Fetch OVERVIEW data
            overview_data = await av_provider.get_fundamental_data(
                ticker=ticker,
                data_type="OVERVIEW"
            )
            
            if not overview_data:
                logger.warning(
                    "Alpha Vantage returned no data",
                    extra={"ticker": ticker}
                )
                return None
            
            # Extract enhanced fields
            enriched = {
                "pe_ratio": self._safe_float(overview_data.get("PERatio")),
                "peg_ratio": self._safe_float(overview_data.get("PEGRatio")),
                "price_to_book": self._safe_float(overview_data.get("PriceToBookRatio")),
                "dividend_yield": self._safe_float(overview_data.get("DividendYield")),
                "eps": self._safe_float(overview_data.get("EPS")),
                "revenue_ttm": self._safe_float(overview_data.get("RevenueTTM")),
                "profit_margin": self._safe_float(overview_data.get("ProfitMargin")),
                "operating_margin": self._safe_float(overview_data.get("OperatingMarginTTM")),
                "shares_outstanding": self._safe_int(overview_data.get("SharesOutstanding")),
                "address": overview_data.get("Address"),
                "city": overview_data.get("City"),
                "state": overview_data.get("State"),
                "zip_code": overview_data.get("ZipCode"),
                "phone": overview_data.get("Phone"),
                "fiscal_year_end": overview_data.get("FiscalYearEnd"),
            }
            
            # If we have existing metadata, merge it
            if existing_metadata:
                # Merge enhanced fields into existing metadata
                result = {
                    **existing_metadata.dict(exclude={"id"}),
                    **enriched,
                    "source_provider": DataSource.ALPHA_VANTAGE,
                    "enrichment_status": "enriched",
                    "enriched_at": datetime.utcnow(),
                    "fetched_at": datetime.utcnow()
                }
            else:
                # Create new metadata with Alpha Vantage data
                result = {
                    "ticker": ticker,
                    "name": overview_data.get("Name", ticker),
                    "description": overview_data.get("Description"),
                    "sector": overview_data.get("Sector"),
                    "industry": overview_data.get("Industry"),
                    "market_cap": self._safe_float(overview_data.get("MarketCapitalization")),
                    "exchange": overview_data.get("Exchange"),
                    "currency": overview_data.get("Currency", "USD"),
                    "asset_type": overview_data.get("AssetType", "Stock"),
                    **enriched,
                    "source_provider": DataSource.ALPHA_VANTAGE,
                    "enrichment_status": "enriched",
                    "enriched_at": datetime.utcnow(),
                    "fetched_at": datetime.utcnow()
                }
            
            logger.info(
                "Metadata enriched with Alpha Vantage",
                extra={
                    "ticker": ticker,
                    "has_financials": bool(enriched.get("pe_ratio"))
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Failed to enrich with Alpha Vantage",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return None
    
    async def save_metadata(self, metadata: Dict) -> Optional[CompanyOverview]:
        """
        Save metadata to database.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Saved CompanyOverview document or None if failed
        """
        try:
            ticker = metadata["ticker"]
            
            # DEBUG: Log what status we're trying to save
            logger.info(
                "Attempting to save metadata",
                extra={
                    "ticker": ticker,
                    "enrichment_status": metadata.get("enrichment_status"),
                    "source_provider": metadata.get("source_provider")
                }
            )
            
            # Check if metadata already exists
            existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
            
            if existing:
                # Update existing metadata
                for key, value in metadata.items():
                    if key not in ["id", "ticker"] and value is not None:
                        setattr(existing, key, value)
                
                await existing.save()
                
                logger.info(
                    "Updated existing metadata",
                    extra={"ticker": ticker, "enrichment_status": existing.enrichment_status}
                )
                
                return existing
            else:
                # Create new metadata
                overview = CompanyOverview(**metadata)
                await overview.insert()
                
                logger.info(
                    "Created new metadata",
                    extra={"ticker": ticker, "enrichment_status": overview.enrichment_status}
                )
                
                return overview
        
        except Exception as e:
            logger.error(
                "Failed to save metadata",
                extra={"ticker": metadata.get("ticker"), "error": str(e)},
                exc_info=True
            )
            return None
    
    async def should_enrich_ticker(
        self,
        ticker: str,
        asset_type: str,
        market_cap: Optional[float] = None
    ) -> bool:
        """
        Determine if ticker should be enriched with Alpha Vantage.
        
        Prioritization logic:
        1. ETFs: ALWAYS enrich (Alpha Vantage has better ETF data)
        2. Large cap (>$10B): High priority
        3. Mid cap ($2B-$10B): Medium priority
        4. Small cap (<$2B): Low priority (enrich on-demand only)
        
        Args:
            ticker: Stock ticker symbol
            asset_type: "Stock", "ETF", etc.
            market_cap: Market capitalization in USD
            
        Returns:
            True if should enrich, False otherwise
        """
        # ETFs always get enriched
        if asset_type == "ETF":
            logger.info(
                "Ticker marked for enrichment (ETF)",
                extra={"ticker": ticker, "reason": "asset_type=ETF"}
            )
            return True
        
        # Large cap stocks get enriched
        if market_cap and market_cap > 10_000_000_000:  # $10B
            logger.info(
                "Ticker marked for enrichment (large cap)",
                extra={"ticker": ticker, "market_cap": market_cap}
            )
            return True
        
        # Mid cap stocks - medium priority (can be enriched in batches)
        if market_cap and market_cap > 2_000_000_000:  # $2B
            logger.info(
                "Ticker eligible for enrichment (mid cap)",
                extra={"ticker": ticker, "market_cap": market_cap}
            )
            return True
        
        # Small cap and unknown - low priority (enrich on-demand)
        logger.debug(
            "Ticker not prioritized for enrichment",
            extra={"ticker": ticker, "asset_type": asset_type, "market_cap": market_cap}
        )
        return False
    
    async def is_metadata_stale(
        self,
        overview: CompanyOverview,
        threshold_days: Optional[int] = None
    ) -> bool:
        """
        Check if metadata is stale and needs refreshing.
        
        Args:
            overview: CompanyOverview document
            threshold_days: Custom threshold, or use default based on asset type
            
        Returns:
            True if stale, False otherwise
        """
        if not overview.fetched_at:
            return True
        
        # Use custom threshold or default based on asset type
        if threshold_days is None:
            threshold_days = self.STALENESS_THRESHOLDS.get(
                overview.asset_type,
                self.STALENESS_THRESHOLDS["Stock"]
            )
        
        age = datetime.utcnow() - overview.fetched_at
        is_stale = age > timedelta(days=threshold_days)
        
        if is_stale:
            logger.info(
                "Metadata is stale",
                extra={
                    "ticker": overview.ticker,
                    "age_days": age.days,
                    "threshold_days": threshold_days
                }
            )
        
        return is_stale
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        try:
            return float(value) if value not in [None, "", "None", "N/A"] else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int."""
        try:
            return int(float(value)) if value not in [None, "", "None", "N/A"] else None
        except (ValueError, TypeError):
            return None
    
    async def _mark_ticker_as_failed(self, ticker: str, reason: str) -> None:
        """
        Mark a ticker as failed in the database.
        
        This prevents endless retries for tickers that don't exist or are delisted.
        
        Args:
            ticker: Stock ticker symbol
            reason: Reason for failure (e.g., "not_found_in_massive", "delisted")
        """
        try:
            # Check if ticker exists in database
            existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
            
            if existing:
                # Update to mark as failed
                existing.enrichment_status = "failed"
                existing.collection_error = reason
                existing.last_collection_attempt = datetime.utcnow()
                existing.collection_attempts += 1
                await existing.save()
                
                logger.info(
                    "Marked ticker as failed",
                    extra={
                        "ticker": ticker,
                        "reason": reason,
                        "attempts": existing.collection_attempts
                    }
                )
            else:
                # Create minimal entry marked as failed
                overview = CompanyOverview(
                    ticker=ticker,
                    name=ticker,  # Use ticker as name since we don't have details
                    enrichment_status="failed",
                    collection_error=reason,
                    last_collection_attempt=datetime.utcnow(),
                    collection_attempts=1,
                    source_provider=DataSource.POLYGON,
                    fetched_at=datetime.utcnow()
                )
                await overview.insert()
                
                logger.info(
                    "Created failed ticker entry",
                    extra={"ticker": ticker, "reason": reason}
                )
        
        except Exception as e:
            logger.error(
                "Failed to mark ticker as failed",
                extra={"ticker": ticker, "reason": reason, "error": str(e)},
                exc_info=True
            )


# Singleton instance
metadata_enrichment_service = MetadataEnrichmentService()
