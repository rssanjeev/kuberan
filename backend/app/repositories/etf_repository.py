"""
ETF Repository.

Data access layer for ETF-related operations.
Handles database CRUD for ETF profiles, comparisons, and queries.
"""

from typing import List, Optional
from datetime import datetime
from app.core.logging_config import get_logger
from app.models.provider import ETFProfile, ETFComparison

logger = get_logger(__name__)


class ETFRepository:
    """
    Repository for ETF data access.
    
    Provides async database operations for:
    - ETF profile storage and retrieval
    - ETF comparison caching
    - Stock-to-ETF lookup
    - Popular ETF queries
    """
    
    async def save_etf_profile(self, profile: ETFProfile) -> ETFProfile:
        """
        Save or update ETF profile in database.
        
        Args:
            profile: ETFProfile model instance
            
        Returns:
            Saved ETFProfile with database ID
            
        Note:
            Uses upsert based on ticker (replaces existing profile)
        """
        try:
            # Check if profile exists
            existing = await ETFProfile.find_one(ETFProfile.ticker == profile.ticker)
            
            if existing:
                # Update existing profile
                existing.name = profile.name
                existing.net_assets = profile.net_assets
                existing.net_expense_ratio = profile.net_expense_ratio
                existing.portfolio_turnover = profile.portfolio_turnover
                existing.dividend_yield = profile.dividend_yield
                existing.inception_date = profile.inception_date
                existing.leveraged = profile.leveraged
                existing.holdings = profile.holdings
                existing.total_holdings = profile.total_holdings
                existing.sector_allocations = profile.sector_allocations
                existing.top_10_holdings = profile.top_10_holdings
                existing.source_provider = profile.source_provider
                existing.fetched_at = profile.fetched_at
                existing.last_updated = datetime.utcnow()
                existing.extended_data = profile.extended_data
                
                await existing.save()
                
                logger.info(
                    "Updated existing ETF profile",
                    extra={"ticker": profile.ticker, "holdings": profile.total_holdings}
                )
                return existing
            else:
                # Insert new profile
                await profile.insert()
                
                logger.info(
                    "Saved new ETF profile",
                    extra={"ticker": profile.ticker, "holdings": profile.total_holdings}
                )
                return profile
                
        except Exception as e:
            logger.error(
                "Failed to save ETF profile",
                extra={"ticker": profile.ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_etf_profile(self, ticker: str) -> Optional[ETFProfile]:
        """
        Retrieve ETF profile by ticker.
        
        Args:
            ticker: ETF ticker symbol (case-insensitive)
            
        Returns:
            ETFProfile if found, None otherwise
        """
        try:
            ticker = ticker.upper().strip()
            profile = await ETFProfile.find_one(ETFProfile.ticker == ticker)
            
            if profile:
                logger.info(
                    "ETF profile retrieved from database",
                    extra={"ticker": ticker, "holdings": profile.total_holdings}
                )
            else:
                logger.info(
                    "ETF profile not found in database",
                    extra={"ticker": ticker}
                )
            
            return profile
            
        except Exception as e:
            logger.error(
                "Failed to retrieve ETF profile",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_all_etf_profiles(self) -> List[ETFProfile]:
        """
        Get all ETF profiles from database.
        
        Returns:
            List of all ETFProfile objects
            
        Note:
            Used for screening and filtering operations
        """
        try:
            logger.debug("Fetching all ETF profiles")
            
            etfs = await ETFProfile.find_all().to_list()
            
            logger.info(
                "Fetched all ETF profiles",
                extra={"count": len(etfs)}
            )
            
            return etfs
            
        except Exception as e:
            logger.error(
                "Failed to fetch all ETF profiles",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def search_etfs_by_stock(
        self,
        symbol: str,
        min_weight: Optional[float] = None
    ) -> List[ETFProfile]:
        """
        Find all ETFs that hold a specific stock.
        
        Args:
            symbol: Stock symbol to search for
            min_weight: Minimum weight threshold (optional)
            
        Returns:
            List of ETFProfile objects holding the stock
            
        Note:
            Uses MongoDB array query to search holdings
        """
        try:
            symbol = symbol.upper().strip()
            
            logger.info(
                "Searching ETFs by stock symbol",
                extra={"symbol": symbol, "min_weight": min_weight}
            )
            
            # Query ETFs where holdings array contains the symbol
            # MongoDB syntax: holdings.symbol matches
            query = {"holdings.symbol": symbol}
            
            etfs = await ETFProfile.find(query).to_list()
            
            # Filter by weight if specified
            if min_weight is not None:
                filtered_etfs = []
                for etf in etfs:
                    for holding in etf.holdings:
                        if holding.get('symbol') == symbol and holding.get('weight', 0) >= min_weight:
                            filtered_etfs.append(etf)
                            break
                etfs = filtered_etfs
            
            logger.info(
                "ETFs found holding stock",
                extra={"symbol": symbol, "count": len(etfs)}
            )
            
            return etfs
            
        except Exception as e:
            logger.error(
                "Failed to search ETFs by stock",
                extra={"symbol": symbol, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def save_comparison(self, comparison: ETFComparison) -> ETFComparison:
        """
        Save ETF comparison result to cache.
        
        Args:
            comparison: ETFComparison model instance
            
        Returns:
            Saved comparison with database ID
        """
        try:
            # Check if comparison exists
            existing = await ETFComparison.find_one(
                ETFComparison.comparison_key == comparison.comparison_key
            )
            
            if existing:
                # Update existing comparison
                existing.overlap_by_weight = comparison.overlap_by_weight
                existing.overlapping_holdings_count = comparison.overlapping_holdings_count
                existing.ticker1_in_ticker2_pct = comparison.ticker1_in_ticker2_pct
                existing.ticker2_in_ticker1_pct = comparison.ticker2_in_ticker1_pct
                existing.sector_drift = comparison.sector_drift
                existing.overlapping_holdings = comparison.overlapping_holdings
                existing.overweight_holdings = comparison.overweight_holdings
                existing.underweight_holdings = comparison.underweight_holdings
                existing.ticker1_stats = comparison.ticker1_stats
                existing.ticker2_stats = comparison.ticker2_stats
                existing.comparison_date = datetime.utcnow()
                existing.fetched_at = datetime.utcnow()
                
                await existing.save()
                
                logger.info(
                    "Updated existing ETF comparison",
                    extra={
                        "comparison_key": comparison.comparison_key,
                        "overlap": comparison.overlap_by_weight
                    }
                )
                return existing
            else:
                # Insert new comparison
                await comparison.insert()
                
                logger.info(
                    "Saved new ETF comparison",
                    extra={
                        "comparison_key": comparison.comparison_key,
                        "overlap": comparison.overlap_by_weight
                    }
                )
                return comparison
                
        except Exception as e:
            logger.error(
                "Failed to save ETF comparison",
                extra={"comparison_key": comparison.comparison_key, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_cached_comparison(
        self,
        comparison_key: str
    ) -> Optional[ETFComparison]:
        """
        Retrieve cached ETF comparison.
        
        Args:
            comparison_key: Sorted ticker combination (e.g., "QQQ_SPY")
            
        Returns:
            ETFComparison if found, None otherwise
        """
        try:
            comparison = await ETFComparison.find_one(
                ETFComparison.comparison_key == comparison_key
            )
            
            if comparison:
                logger.info(
                    "Cached comparison retrieved",
                    extra={"comparison_key": comparison_key}
                )
            else:
                logger.info(
                    "Cached comparison not found",
                    extra={"comparison_key": comparison_key}
                )
            
            return comparison
            
        except Exception as e:
            logger.error(
                "Failed to retrieve cached comparison",
                extra={"comparison_key": comparison_key, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_popular_etfs(self, limit: int = 20) -> List[ETFProfile]:
        """
        Get popular ETFs (by assets under management).
        
        Args:
            limit: Maximum number of ETFs to return
            
        Returns:
            List of popular ETFs sorted by net_assets descending
        """
        try:
            logger.info("Fetching popular ETFs", extra={"limit": limit})
            
            # Sort by net_assets descending
            etfs = await ETFProfile.find().sort([("net_assets", -1)]).limit(limit).to_list()
            
            logger.info(
                "Popular ETFs retrieved",
                extra={"count": len(etfs)}
            )
            
            return etfs
            
        except Exception as e:
            logger.error(
                "Failed to retrieve popular ETFs",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_all_etf_tickers(self) -> List[str]:
        """
        Get list of all ETF tickers in database.
        
        Returns:
            List of ticker symbols
            
        Note:
            Used for batch operations and comparisons
        """
        try:
            logger.info("Fetching all ETF tickers")
            
            # Projection: only return ticker field
            etfs = await ETFProfile.find().project(ETFProfile.ticker).to_list()
            tickers = [etf.ticker for etf in etfs if etf.ticker]
            
            logger.info("All ETF tickers retrieved", extra={"count": len(tickers)})
            
            return tickers
            
        except Exception as e:
            logger.error(
                "Failed to retrieve ETF tickers",
                extra={"error": str(e)},
                exc_info=True
            )
            raise


# Singleton instance
etf_repository = ETFRepository()
