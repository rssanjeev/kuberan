"""
Metadata Enrichment Service - Two-stage metadata collection and enhancement.

Stage 1: YFinance bulk collection (fast, comprehensive, no rate limits)
Stage 2: Alpha Vantage enrichment (detailed, rate-limited, prioritized)

SECURITY: Only stores public company information, no sensitive data.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf

from app.core.logging_config import get_logger
from app.services.providers import provider_registry
from app.repositories.provider_repository import provider_repository
from app.models.provider import CompanyOverview, DataSource

logger = get_logger(__name__)


class MetadataEnrichmentService:
    """
    Two-stage metadata collection and enrichment service.
    
    Pipeline:
    1. YFinance: Fast bulk collection of basic metadata (all tickers)
    2. Alpha Vantage: Selective enrichment with premium data (prioritized)
    
    Prioritization:
    - ETFs: ALWAYS enrich (Alpha Vantage has better ETF data)
    - Large cap (market_cap > $10B): High priority
    - Mid cap ($2B - $10B): Medium priority  
    - Small cap (< $2B): Low priority
    """
    
    def __init__(self):
        """Initialize metadata enrichment service."""
        # Staleness thresholds (days)
        self.STALENESS_THRESHOLDS = {
            "ETF": 30,      # ETFs change slowly
            "Stock": 7,     # Companies update quarterly
            "Critical": 1   # High-priority watchlist tickers
        }
    
    async def collect_base_metadata(self, ticker: str) -> Optional[Dict]:
        """
        Stage 1: Collect base metadata from YFinance.
        
        This is fast and has no rate limits. Use for bulk collection.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Metadata dictionary or None if failed
        """
        try:
            logger.info("Collecting base metadata", extra={"ticker": ticker})
            
            # Fetch from yfinance (synchronous, run in executor)
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            info = await loop.run_in_executor(None, lambda: stock.info)
            
            if not info or len(info) < 3:
                logger.warning(
                    "YFinance returned insufficient data",
                    extra={"ticker": ticker}
                )
                return None
            
            # Classify asset type
            asset_type = self._classify_asset_type(info)
            
            # Extract metadata
            metadata = {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName") or ticker,
                "description": info.get("longBusinessSummary"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "website": info.get("website"),
                "country": info.get("country"),
                "exchange": info.get("exchange"),
                "currency": info.get("currency", "USD"),
                "asset_type": asset_type,
                "source_provider": DataSource.YFINANCE,
                "enrichment_status": "base",
                "fetched_at": datetime.utcnow()
            }
            
            logger.info(
                "Base metadata collected",
                extra={
                    "ticker": ticker,
                    "asset_type": asset_type,
                    "has_description": bool(metadata.get("description"))
                }
            )
            
            return metadata
        
        except Exception as e:
            logger.error(
                "Failed to collect base metadata",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return None
    
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
    
    def _classify_asset_type(self, yfinance_info: Dict) -> str:
        """
        Classify asset type from YFinance data.
        
        Args:
            yfinance_info: YFinance info dictionary
            
        Returns:
            Asset type: "Stock", "ETF", "Fund", etc.
        """
        # Check quoteType field
        quote_type = yfinance_info.get("quoteType", "").upper()
        if quote_type == "ETF":
            return "ETF"
        if quote_type in ["MUTUALFUND", "FUND"]:
            return "Fund"
        
        # Check for fund-specific fields
        if yfinance_info.get("fundFamily"):
            return "ETF"
        if yfinance_info.get("category"):
            return "Fund"
        
        # Default to Stock
        return "Stock"
    
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


# Singleton instance
metadata_enrichment_service = MetadataEnrichmentService()
