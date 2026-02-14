"""
ETF Profile Service.

Handles individual ETF analysis including profile retrieval,
holdings management, sector allocation, and comparable ETF discovery.

SECURITY: No sensitive financial data stored. Only public ETF data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from app.core.logging_config import get_logger
from app.models.provider import ETFProfile, DataSource
from app.repositories.etf_repository import etf_repository
from app.services.providers import provider_manager

logger = get_logger(__name__)


class ETFProfileService:
    """
    Service for ETF profile operations.
    
    Provides comprehensive ETF analysis including:
    - Profile retrieval with caching (30-day TTL)
    - Complete holdings list
    - Sector allocation breakdown
    - Comparable ETF discovery based on overlap
    """
    
    async def get_etf_profile(
        self, 
        ticker: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get complete ETF profile with all data.
        
        Args:
            ticker: ETF ticker symbol (e.g., "SPY", "VOO")
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Complete ETF profile with holdings, sectors, and fundamentals
            
        Raises:
            ValueError: If ticker is invalid
            Exception: If data fetch fails
            
        Example:
            >>> profile = await etf_profile_service.get_etf_profile("SPY")
            >>> print(f"Holdings: {profile['total_holdings']}")
            Holdings: 503
        """
        # Input validation
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        # Validate ticker format (1-5 uppercase letters/numbers)
        if not ticker.isalnum() or len(ticker) > 5:
            raise ValueError(f"Invalid ticker format: {ticker}. Must be 1-5 alphanumeric characters.")
        
        if not ticker:
            raise ValueError("Ticker symbol is required")
        
        logger.info("Fetching ETF profile", extra={"ticker": ticker, "force_refresh": force_refresh})
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_profile = await etf_repository.get_etf_profile(ticker)
            if cached_profile:
                logger.info("ETF profile found in cache", extra={"ticker": ticker})
                return self._profile_to_dict(cached_profile)
        
        # Fetch from Alpha Vantage
        try:
            logger.info("Fetching ETF profile from provider", extra={"ticker": ticker})
            
            # Get Alpha Vantage provider from provider_manager
            alpha_vantage_provider = provider_manager._get_provider_by_name("AlphaVantageProvider")
            if not alpha_vantage_provider:
                error_msg = (
                    "Alpha Vantage provider not available. "
                    "Please configure ALPHA_VANTAGE_KEY environment variable."
                )
                logger.error("Provider not configured", extra={"ticker": ticker})
                raise Exception(error_msg)
            
            # Fetch raw data from provider
            try:
                raw_data = await alpha_vantage_provider.fetch_etf_profile(ticker)
            except Exception as provider_error:
                logger.error(
                    "Provider fetch failed",
                    extra={"ticker": ticker, "provider_error": str(provider_error)},
                    exc_info=True
                )
                raise Exception(f"Failed to fetch ETF data from provider: {str(provider_error)}")
            
            # Validate response data
            if not raw_data:
                raise ValueError(f"No data returned for ticker {ticker}. ETF may not exist or ticker may be invalid.")
            
            # Transform and save to database
            try:
                etf_profile = self._transform_to_profile(ticker, raw_data)
            except Exception as transform_error:
                logger.error(
                    "Data transformation failed",
                    extra={"ticker": ticker, "transform_error": str(transform_error)},
                    exc_info=True
                )
                raise Exception(f"Failed to process ETF data: {str(transform_error)}")
            
            try:
                saved_profile = await etf_repository.save_etf_profile(etf_profile)
            except Exception as db_error:
                logger.error(
                    "Database save failed",
                    extra={"ticker": ticker, "db_error": str(db_error)},
                    exc_info=True
                )
                raise Exception(f"Failed to save ETF profile to database: {str(db_error)}")
            
            logger.info(
                "ETF profile saved successfully",
                extra={
                    "ticker": ticker,
                    "holdings": saved_profile.total_holdings,
                    "sectors": len(saved_profile.sector_allocations)
                }
            )
            
            return self._profile_to_dict(saved_profile)
            
        except ValueError as ve:
            # Re-raise validation errors as-is
            logger.error(
                "ETF validation error",
                extra={"ticker": ticker, "error": str(ve)}
            )
            raise
        
        except Exception as e:
            logger.error(
                "Failed to fetch ETF profile",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"ETF profile fetch failed for {ticker}: {str(e)}")
            raise
    
    async def get_etf_holdings(
        self,
        ticker: str,
        limit: Optional[int] = None,
        min_weight: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get ETF holdings list with optional filtering.
        
        Args:
            ticker: ETF ticker symbol
            limit: Maximum number of holdings to return
            min_weight: Minimum weight threshold (e.g., 0.01 for 1%)
            
        Returns:
            Holdings list with filtering applied
            
        Example:
            >>> holdings = await etf_profile_service.get_etf_holdings("SPY", limit=10)
            >>> print(holdings['holdings'][0])
            {'symbol': 'NVDA', 'weight': 0.0783, 'description': 'NVIDIA CORP'}
        """
        ticker = ticker.upper().strip()
        
        logger.info(
            "Fetching ETF holdings",
            extra={"ticker": ticker, "limit": limit, "min_weight": min_weight}
        )
        
        # Get profile from cache or fetch
        profile = await etf_repository.get_etf_profile(ticker)
        if not profile:
            # Fetch fresh data
            await self.get_etf_profile(ticker)
            profile = await etf_repository.get_etf_profile(ticker)
        
        if not profile:
            raise ValueError(f"ETF profile not found for ticker: {ticker}")
        
        # Filter holdings
        holdings = profile.holdings.copy()
        
        # Apply weight filter
        if min_weight is not None:
            holdings = [h for h in holdings if h.get('weight', 0) >= min_weight]
        
        # Apply limit
        if limit is not None:
            holdings = holdings[:limit]
        
        logger.info(
            "ETF holdings retrieved",
            extra={
                "ticker": ticker,
                "total": profile.total_holdings,
                "returned": len(holdings)
            }
        )
        
        return {
            "ticker": ticker,
            "name": profile.name,
            "total_holdings": profile.total_holdings,
            "returned_count": len(holdings),
            "holdings": holdings,
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
        }
    
    async def get_etf_sectors(self, ticker: str) -> Dict[str, Any]:
        """
        Get ETF sector allocation breakdown.
        
        Args:
            ticker: ETF ticker symbol
            
        Returns:
            Sector allocation with percentages
            
        Raises:
            ValueError: If ticker is invalid
            
        Example:
            >>> sectors = await etf_profile_service.get_etf_sectors("SPY")
            >>> print(sectors['sector_allocations'][0])
            {'sector': 'INFORMATION TECHNOLOGY', 'weight': 0.348, 'weight_pct': 34.8}
        """
        # Input validation
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        if not ticker.isalnum() or len(ticker) > 5:
            raise ValueError(f"Invalid ticker format: {ticker}")
        
        logger.info("Fetching ETF sector allocation", extra={"ticker": ticker})
        
        # Get profile from cache or fetch
        profile = await etf_repository.get_etf_profile(ticker)
        if not profile:
            await self.get_etf_profile(ticker)
            profile = await etf_repository.get_etf_profile(ticker)
        
        if not profile:
            raise ValueError(f"ETF profile not found for ticker: {ticker}")
        
        # Calculate percentages for display
        sectors_with_pct = []
        for sector in profile.sector_allocations:
            sector_data = sector.copy()
            if 'weight' in sector_data:
                sector_data['weight_pct'] = round(sector_data['weight'] * 100, 2)
            sectors_with_pct.append(sector_data)
        
        logger.info(
            "ETF sector allocation retrieved",
            extra={"ticker": ticker, "sectors": len(sectors_with_pct)}
        )
        
        return {
            "ticker": ticker,
            "name": profile.name,
            "sector_allocations": sectors_with_pct,
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
        }
    
    async def get_comparable_etfs(
        self,
        ticker: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Find comparable ETFs based on holdings overlap.
        
        This is a placeholder for Phase 2 (ETF Comparison Service).
        Will calculate overlap with all other ETFs in database.
        
        Args:
            ticker: ETF ticker symbol
            limit: Maximum number of comparables to return
            
        Returns:
            List of comparable ETFs sorted by overlap percentage
            
        Note:
            Full implementation requires ETF Comparison Service (Phase 2)
        """
        ticker = ticker.upper().strip()
        
        logger.info(
            "Fetching comparable ETFs",
            extra={"ticker": ticker, "limit": limit}
        )
        
        # Get the target ETF profile
        profile = await etf_repository.get_etf_profile(ticker)
        if not profile:
            await self.get_etf_profile(ticker)
            profile = await etf_repository.get_etf_profile(ticker)
        
        if not profile:
            raise ValueError(f"ETF profile not found for ticker: {ticker}")
        
        # TODO: Phase 2 - Calculate overlap with all ETFs
        # For now, return empty list with note
        logger.warning(
            "Comparable ETFs feature requires Phase 2 implementation",
            extra={"ticker": ticker}
        )
        
        return {
            "ticker": ticker,
            "name": profile.name,
            "comparables": [],
            "note": "Comparable ETF discovery will be available after Phase 2 (ETF Comparison Service) is implemented"
        }
    
    def _transform_to_profile(
        self,
        ticker: str,
        raw_data: Dict[str, Any]
    ) -> ETFProfile:
        """
        Transform Alpha Vantage raw data to ETFProfile model.
        
        Args:
            ticker: ETF ticker symbol
            raw_data: Raw data from Alpha Vantage ETF_PROFILE API
            
        Returns:
            ETFProfile model instance
        """
        # Extract holdings
        holdings_list = []
        raw_holdings = raw_data.get('holdings', [])
        for holding in raw_holdings:
            holdings_list.append({
                'symbol': holding.get('symbol', ''),
                'description': holding.get('description', ''),
                'weight': float(holding.get('weight', 0)),
                'weight_pct': round(float(holding.get('weight', 0)) * 100, 2)
            })
        
        # Extract sector allocations
        sectors_list = []
        raw_sectors = raw_data.get('sectors', [])
        for sector in raw_sectors:
            sectors_list.append({
                'sector': sector.get('sector', ''),
                'weight': float(sector.get('weight', 0)),
                'weight_pct': round(float(sector.get('weight', 0)) * 100, 2)
            })
        
        # Top 10 holdings
        top_10 = holdings_list[:10] if len(holdings_list) >= 10 else holdings_list
        
        # Create ETFProfile
        return ETFProfile(
            ticker=ticker,
            name=raw_data.get('name'),
            net_assets=float(raw_data.get('net_assets', 0)) if raw_data.get('net_assets') else None,
            net_expense_ratio=float(raw_data.get('net_expense_ratio', 0)) if raw_data.get('net_expense_ratio') else None,
            portfolio_turnover=float(raw_data.get('portfolio_turnover', 0)) if raw_data.get('portfolio_turnover') else None,
            dividend_yield=float(raw_data.get('dividend_yield', 0)) if raw_data.get('dividend_yield') else None,
            inception_date=raw_data.get('inception_date'),
            leveraged=raw_data.get('leveraged'),
            holdings=holdings_list,
            total_holdings=len(holdings_list),
            sector_allocations=sectors_list,
            top_10_holdings=top_10,
            source_provider=DataSource.ALPHA_VANTAGE,
            fetched_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            extended_data=raw_data  # Store complete raw data
        )
    
    def _profile_to_dict(self, profile: ETFProfile) -> Dict[str, Any]:
        """
        Convert ETFProfile model to dictionary for API response.
        
        Args:
            profile: ETFProfile model instance
            
        Returns:
            Dictionary representation for API
        """
        return {
            "ticker": profile.ticker,
            "name": profile.name,
            "fundamentals": {
                "net_assets": profile.net_assets,
                "net_expense_ratio": profile.net_expense_ratio,
                "expense_ratio_pct": round(profile.net_expense_ratio * 100, 4) if profile.net_expense_ratio else None,
                "portfolio_turnover": profile.portfolio_turnover,
                "dividend_yield": profile.dividend_yield,
                "dividend_yield_pct": round(profile.dividend_yield * 100, 2) if profile.dividend_yield else None,
                "inception_date": profile.inception_date,
                "leveraged": profile.leveraged
            },
            "holdings": {
                "total": profile.total_holdings,
                "top_10": profile.top_10_holdings,
                "complete_list": profile.holdings  # Full list
            },
            "sectors": profile.sector_allocations,
            "metadata": {
                "source_provider": profile.source_provider.value if profile.source_provider else None,
                "fetched_at": profile.fetched_at.isoformat() if profile.fetched_at else None,
                "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
            }
        }


# Singleton instance
etf_profile_service = ETFProfileService()
