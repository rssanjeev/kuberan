"""
MASSIVE provider implementation.

Uses MASSIVE API (similar to Polygon.io) for comprehensive US stock market data.
Perfect for bulk data collection with generous rate limits.

Best for: All US stocks tickers, historical data (2 years), end-of-day prices,
          corporate actions, technical indicators, reference data.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx

from app.core.logging_config import get_logger
from app.core.api_metrics import api_metrics
from app.repositories.provider_repository import provider_repository
from app.models.provider import DataSource
from ..base_provider import (
    BaseProvider,
    DataType,
    ProviderCapability,
    ProviderHealth,
    ProviderException,
    RateLimitException
)
from ..adaptive_rate_limiter import AdaptiveRateLimiter

logger = get_logger(__name__)


class MassiveProvider(BaseProvider):
    """
    MASSIVE provider - US stocks comprehensive data.
    
    Strengths:
    - 5 API calls per minute (300/hour, 7,200/day theoretical)
    - 100% US market coverage (all NYSE, NASDAQ, etc.)
    - 2 years historical data
    - End-of-day prices (reliable, complete)
    - Corporate actions (splits, dividends)
    - Technical indicators
    - Minute-level aggregates
    - Reference data (company info, exchanges)
    - Direct API access (no MCP dependency)
    
    Limitations:
    - US stocks only (no international)
    - End-of-day data (not real-time intraday)
    - Rate limit: 5 calls/min (but sufficient for 300 tickers/hour)
    
    Use cases:
    - PRIMARY for bulk ticker discovery (all US stocks)
    - PRIMARY for historical data collection (2 years)
    - PRIMARY for end-of-day prices (reliable, complete)
    - PRIMARY for corporate actions (splits, dividends)
    - EXCELLENT for building comprehensive market database
    """
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(
        self,
        api_key: str,
        priority: int = 1,  # Higher priority than Alpha Vantage for bulk ops
        tier: str = "basic"
    ):
        """
        Initialize MASSIVE provider.
        
        Args:
            api_key: MASSIVE API key
            priority: Provider priority (1=primary for bulk ops)
            tier: Subscription tier (basic is default)
        """
        super().__init__(
            name="MassiveProvider",
            priority=priority
        )
        
        self.api_key = api_key
        self.tier = tier
        self.base_url = self.BASE_URL
        
        # Rate limits: 5 calls/min
        # Conservative: 5/min = 300/hour = 7,200/day theoretical
        # Practical: ~4,500/day accounting for retries and overhead
        per_minute = 5
        per_day = 4500  # Conservative daily estimate
        
        # Initialize adaptive rate limiter
        self.rate_limiter = AdaptiveRateLimiter(
            provider_name=self.name,
            per_minute=per_minute,
            per_day=per_day
        )
        
        self._rate_limits = {
            "per_minute": per_minute,
            "per_day": per_day
        }
        
        logger.info(
            f"Initialized MASSIVE provider",
            extra={
                "tier": tier,
                "rate_limit_per_min": per_minute,
                "rate_limit_per_day": per_day
            }
        )
    
    def get_capabilities(self) -> Dict[DataType, ProviderCapability]:
        """
        Get provider capabilities for different data types.
        
        Returns:
            Dictionary mapping data types to capability levels
        """
        return {
            # Core strengths
            DataType.REAL_TIME_QUOTE: ProviderCapability.BASIC,  # EOD only
            DataType.HISTORICAL_PRICES: ProviderCapability.EXCELLENT,  # 2 years
            DataType.TECHNICAL_INDICATOR: ProviderCapability.GOOD,
            DataType.FUNDAMENTAL_DATA: ProviderCapability.GOOD,  # Reference data
            
            # Corporate actions
            DataType.DIVIDENDS: ProviderCapability.EXCELLENT,
            DataType.SPLITS: ProviderCapability.EXCELLENT,
            DataType.EARNINGS: ProviderCapability.GOOD,
            
            # Limited/not supported
            DataType.NEWS: ProviderCapability.NONE,
            DataType.ANALYST_RATINGS: ProviderCapability.NONE,
            DataType.PRICE_TARGETS: ProviderCapability.NONE,
            DataType.MARKET_STATUS: ProviderCapability.BASIC,
            
            # Additional
            DataType.FOREX: ProviderCapability.NONE,
            DataType.CRYPTO: ProviderCapability.NONE,
            DataType.COMMODITIES: ProviderCapability.NONE,
            DataType.ECONOMIC_INDICATORS: ProviderCapability.NONE
        }
    
    def get_rate_limits(self) -> Dict:
        """Get current rate limit configuration."""
        return {
            **self._rate_limits,
            "remaining": self.rate_limiter.get_remaining_quota()
        }
    
    async def health_check(self) -> ProviderHealth:
        """
        Check provider health and connectivity.
        
        Returns:
            ProviderHealth object with status and metrics
        """
        try:
            start_time = datetime.now()
            
            # Simple API call to check connectivity (get ticker list)
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/tickers",
                    params={
                        "apikey": self.api_key,
                        "limit": 1
                    }
                )
                response.raise_for_status()
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ProviderHealth(
                provider_name=self.name,
                is_healthy=True,
                response_time_ms=response_time * 1000,
                success_rate=self.reliability_score,
                last_success=datetime.now(),
                rate_limit_remaining=self.rate_limiter.get_remaining_quota()
            )
        
        except Exception as e:
            logger.error(
                f"MASSIVE health check failed: {str(e)}",
                extra={"error": str(e)},
                exc_info=True
            )
            
            return ProviderHealth(
                provider_name=self.name,
                is_healthy=False,
                error_message=str(e),
                success_rate=self.reliability_score,
                rate_limit_remaining=self.rate_limiter.get_remaining_quota()
            )
    
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Fetch real-time quote (actually end-of-day for MASSIVE).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote data dictionary or None if failed
        """
        try:
            # Wait for rate limit clearance
            await self.rate_limiter.acquire(priority=0)
            
            # Track API call
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="previous_close",
                status="pending"
            )
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v2/aggs/ticker/{ticker}/prev",
                    params={"adjusted": "true", "apikey": self.api_key}
                )
                
                # Update rate limiter from response headers
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    api_metrics.record_api_call(
                        provider="MASSIVE",
                        endpoint="previous_close",
                        status="rate_limited"
                    )
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            # Parse MASSIVE response format
            if data and "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                
                quote_data = {
                    "ticker": result.get("T", ticker),
                    "price": result.get("c", 0.0),  # Close price
                    "open": result.get("o", 0.0),
                    "high": result.get("h", 0.0),
                    "low": result.get("l", 0.0),
                    "volume": result.get("v", 0),
                    "quote_timestamp": datetime.fromtimestamp(result.get("t", 0) / 1000).isoformat(),
                    "change": result.get("c", 0.0) - result.get("o", 0.0),
                    "change_percent": ((result.get("c", 0.0) - result.get("o", 0.0)) / result.get("o", 1.0) * 100) if result.get("o", 0.0) > 0 else 0.0,
                    "provider": DataSource.POLYGON.value
                }
                
                self.record_success()
                api_metrics.record_api_call(
                    provider="MASSIVE",
                    endpoint="previous_close",
                    status="success"
                )
                
                logger.info(
                    f"Fetched EOD quote for {ticker}",
                    extra={"ticker": ticker, "price": quote_data["price"]}
                )
                
                return quote_data
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            self.record_failure()
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="previous_close",
                status="error"
            )
            logger.error(
                f"Failed to fetch quote for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE quote fetch failed: {str(e)}")
    
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Fetch historical price data (up to 2 years).
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y)
            interval: Data interval (1d for daily)
            
        Returns:
            List of historical price dictionaries or None if failed
        """
        try:
            # Wait for rate limit clearance
            await self.rate_limiter.acquire(priority=0)
            
            # Calculate date range
            end_date = datetime.now()
            
            period_map = {
                "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
                "6mo": 180, "1y": 365, "2y": 730, "max": 730  # MASSIVE limit: 2 years
            }
            days = period_map.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            # Format dates for MASSIVE API
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
            
            # Track API call
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="aggregates",
                status="pending"
            )
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}",
                    params={
                        "apikey": self.api_key,
                        "adjusted": "true",
                        "sort": "asc"
                    }
                )
                
                # Update rate limiter
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    api_metrics.record_api_call(
                        provider="MASSIVE",
                        endpoint="aggregates",
                        status="rate_limited"
                    )
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            # Parse MASSIVE aggregates response
            if data and "results" in data:
                prices = []
                
                for bar in data["results"]:
                    prices.append({
                        "ticker": ticker,
                        "timestamp": datetime.fromtimestamp(bar.get("t", 0) / 1000).isoformat(),
                        "open": bar.get("o", 0.0),
                        "high": bar.get("h", 0.0),
                        "low": bar.get("l", 0.0),
                        "close": bar.get("c", 0.0),
                        "volume": bar.get("v", 0),
                        "vwap": bar.get("vw", 0.0),  # Volume-weighted average price
                        "transactions": bar.get("n", 0),
                        "provider": DataSource.POLYGON.value
                    })
                
                self.record_success()
                api_metrics.record_api_call(
                    provider="MASSIVE",
                    endpoint="aggregates",
                    status="success"
                )
                
                logger.info(
                    f"Fetched {len(prices)} historical prices for {ticker}",
                    extra={"ticker": ticker, "count": len(prices), "period": period}
                )
                
                return prices
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            self.record_failure()
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="aggregates",
                status="error"
            )
            logger.error(
                f"Failed to fetch historical prices for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE historical fetch failed: {str(e)}")
    
    async def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch dividend history.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of dividend dictionaries or None if failed
        """
        try:
            # Wait for rate limit clearance
            await self.rate_limiter.acquire(priority=0)
            
            # Track API call
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="dividends",
                status="pending"
            )
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/dividends",
                    params={
                        "ticker": ticker,
                        "apikey": self.api_key
                    }
                )
                
                # Update rate limiter
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    api_metrics.record_api_call(
                        provider="MASSIVE",
                        endpoint="dividends",
                        status="rate_limited"
                    )
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            # Parse dividends
            if data and "results" in data:
                dividends = []
                
                for div in data["results"]:
                    dividends.append({
                        "ticker": ticker,
                        "ex_dividend_date": div.get("ex_dividend_date"),
                        "payment_date": div.get("payment_date"),
                        "record_date": div.get("record_date"),
                        "declaration_date": div.get("declaration_date"),
                        "amount": div.get("cash_amount", 0.0),
                        "frequency": div.get("frequency", ""),
                        "provider": DataSource.POLYGON.value
                    })
                
                self.record_success()
                api_metrics.record_api_call(
                    provider="MASSIVE",
                    endpoint="dividends",
                    status="success"
                )
                
                logger.info(
                    f"Fetched {len(dividends)} dividends for {ticker}",
                    extra={"ticker": ticker, "count": len(dividends)}
                )
                
                return dividends
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            self.record_failure()
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="dividends",
                status="error"
            )
            logger.error(
                f"Failed to fetch dividends for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE dividend fetch failed: {str(e)}")
    
    async def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch stock split history.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of split dictionaries or None if failed
        """
        try:
            # Wait for rate limit clearance
            await self.rate_limiter.acquire(priority=0)
            
            # Track API call
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="splits",
                status="pending"
            )
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/splits",
                    params={
                        "ticker": ticker,
                        "apikey": self.api_key
                    }
                )
                
                # Update rate limiter
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    api_metrics.record_api_call(
                        provider="MASSIVE",
                        endpoint="splits",
                        status="rate_limited"
                    )
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            # Parse splits
            if data and "results" in data:
                splits = []
                
                for split in data["results"]:
                    splits.append({
                        "ticker": ticker,
                        "execution_date": split.get("execution_date"),
                        "split_from": split.get("split_from", 1),
                        "split_to": split.get("split_to", 1),
                        "ratio": split.get("split_to", 1) / split.get("split_from", 1),
                        "provider": DataSource.POLYGON.value
                    })
                
                self.record_success()
                api_metrics.record_api_call(
                    provider="MASSIVE",
                    endpoint="splits",
                    status="success"
                )
                
                logger.info(
                    f"Fetched {len(splits)} splits for {ticker}",
                    extra={"ticker": ticker, "count": len(splits)}
                )
                
                return splits
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            self.record_failure()
            api_metrics.record_api_call(
                provider="MASSIVE",
                endpoint="splits",
                status="error"
            )
            logger.error(
                f"Failed to fetch splits for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE split fetch failed: {str(e)}")
    
    # Unimplemented methods (not supported by MASSIVE or not needed)
    
    async def get_technical_indicator(
        self,
        ticker: str,
        indicator: str,
        **kwargs
    ) -> Optional[Dict]:
        """Not implemented - use Alpha Vantage for technical indicators."""
        raise NotImplementedError("Technical indicators not implemented for MASSIVE")
    
    async def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """Not implemented - use ticker details endpoint instead."""
        raise NotImplementedError("Use fetch_ticker_details for company info")
    
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """Not implemented - MASSIVE doesn't provide news."""
        raise NotImplementedError("News not supported by MASSIVE")
    
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """Not implemented - use Alpha Vantage for earnings."""
        raise NotImplementedError("Earnings not implemented for MASSIVE")
    
    async def fetch_analyst_ratings(self, ticker: str) -> Optional[List[Dict]]:
        """Not implemented - MASSIVE doesn't provide analyst ratings."""
        raise NotImplementedError("Analyst ratings not supported by MASSIVE")
    
    async def fetch_price_targets(self, ticker: str) -> Optional[Dict]:
        """Not implemented - MASSIVE doesn't provide price targets."""
        raise NotImplementedError("Price targets not supported by MASSIVE")
    
    async def get_market_status(self) -> Optional[Dict]:
        """Get market status (open/closed)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/marketstatus/now",
                    params={"apikey": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "market": data.get("market", "unknown"),
                    "server_time": data.get("serverTime", ""),
                    "exchanges": data.get("exchanges", {}),
                    "provider": DataSource.POLYGON.value
                }
        except Exception as e:
            logger.error(
                f"Failed to get market status",
                extra={"error": str(e)},
                exc_info=True
            )
            return None
    
    # MASSIVE-specific methods
    
    async def fetch_ticker_details(self, ticker: str) -> Optional[Dict]:
        """
        Fetch detailed ticker information (reference data).
        
        ENHANCED (Phase 3): Maps all 30+ MASSIVE fields to CompanyOverview model.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Ticker details dictionary with complete MASSIVE data or None if failed
        """
        try:
            await self.rate_limiter.acquire(priority=0)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/tickers/{ticker}",
                    params={"apikey": self.api_key}
                )
                
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                # Handle 404 gracefully - ticker not found or delisted
                if response.status_code == 404:
                    logger.warning(
                        f"Ticker details not found (404 - may be delisted or invalid)",
                        extra={"ticker": ticker, "status_code": 404}
                    )
                    return None
                
                response.raise_for_status()
                data = response.json()
            
            if data and "results" in data:
                result = data["results"]
                
                # Extract address information
                address_data = result.get("address", {})
                
                # Extract branding information
                branding_data = result.get("branding", {})
                
                # Map all MASSIVE fields to CompanyOverview model structure
                mapped_data = {
                    # ==================== Core Identification ====================
                    "ticker": result.get("ticker", ticker),
                    "name": result.get("name", ""),
                    
                    # ==================== MASSIVE-Specific Identifiers ====================
                    "cik": result.get("cik"),
                    "composite_figi": result.get("composite_figi"),
                    "share_class_figi": result.get("share_class_figi"),
                    "ticker_root": result.get("ticker_root"),
                    
                    # ==================== Classification ====================
                    "type": result.get("type"),  # CS, ETF, ADRC, etc.
                    "market": result.get("market"),  # stocks, crypto, fx, otc
                    "locale": result.get("locale"),  # us, global
                    "primary_exchange": result.get("primary_exchange"),  # XNAS, XNYS, etc.
                    
                    # ==================== Company Information ====================
                    "description": result.get("description"),
                    "sic_code": result.get("sic_code"),
                    "sic_description": result.get("sic_description"),
                    
                    # ==================== Contact Information ====================
                    "homepage_url": result.get("homepage_url"),
                    "phone_number": result.get("phone_number"),
                    
                    # Address fields (structured from MASSIVE response)
                    "address1": address_data.get("address1"),
                    "city": address_data.get("city"),
                    "state": address_data.get("state"),
                    "postal_code": address_data.get("postal_code"),
                    
                    # ==================== Branding ====================
                    "logo_url": branding_data.get("logo_url"),
                    "icon_url": branding_data.get("icon_url"),
                    
                    # ==================== Financial Metrics ====================
                    "market_cap": result.get("market_cap"),
                    "total_employees": result.get("total_employees"),
                    
                    # Share information
                    "share_class_shares_outstanding": result.get("share_class_shares_outstanding"),
                    "weighted_shares_outstanding": result.get("weighted_shares_outstanding"),
                    "round_lot": result.get("round_lot", 100),  # Default 100
                    
                    # ==================== Currency ====================
                    "currency_name": result.get("currency_name"),
                    "currency_symbol": result.get("currency_symbol"),
                    
                    # ==================== Dates & Status ====================
                    "list_date": result.get("list_date"),
                    "active": result.get("active"),
                    "delisted_utc": result.get("delisted_utc"),
                    "last_updated_utc": result.get("last_updated_utc"),
                    
                    # ==================== Metadata ====================
                    "provider": DataSource.POLYGON.value,
                    "metadata_sources": ["MASSIVE"],  # Track data source
                    
                    # ==================== Extended Data ====================
                    # Store any additional fields that don't fit the schema
                    "extended_data": {
                        k: v for k, v in result.items()
                        if k not in {
                            "ticker", "name", "cik", "composite_figi", "share_class_figi",
                            "ticker_root", "type", "market", "locale", "primary_exchange",
                            "description", "sic_code", "sic_description", "homepage_url",
                            "phone_number", "address", "branding", "market_cap", "total_employees",
                            "share_class_shares_outstanding", "weighted_shares_outstanding",
                            "round_lot", "currency_name", "currency_symbol", "list_date",
                            "active", "delisted_utc", "last_updated_utc"
                        }
                    }
                }
                
                logger.info(
                    "Fetched complete ticker details from MASSIVE",
                    extra={
                        "ticker": ticker,
                        "fields_mapped": len([v for v in mapped_data.values() if v is not None]),
                        "has_branding": bool(branding_data),
                        "has_address": bool(address_data)
                    }
                )
                
                return mapped_data
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch ticker details for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE ticker details fetch failed: {str(e)}") from e
    
    async def fetch_related_companies(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch related companies (peers, competitors, correlated stocks) for a ticker.
        
        PHASE 4: Related Tickers Implementation
        
        Endpoint: GET /v1/related-companies/{ticker}
        
        Returns companies with similar business models, market sectors, or price correlations.
        Useful for competitive analysis, sector tracking, and portfolio diversification.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of related company dictionaries with relationship details or None if failed
            
        Example Return:
            [
                {
                    "ticker": "MSFT",
                    "name": "Microsoft Corporation",
                    "market_cap": 2800000000000,
                    "similarity_score": 0.85
                },
                {
                    "ticker": "GOOGL",
                    "name": "Alphabet Inc Class A",
                    "market_cap": 1900000000000,
                    "similarity_score": 0.78
                }
            ]
        """
        try:
            await self.rate_limiter.acquire(priority=0)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/related-companies/{ticker}",
                    params={"apikey": self.api_key}
                )
                
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                # Handle 404 gracefully - no related companies found
                if response.status_code == 404:
                    logger.warning(
                        f"No related companies found for ticker (404)",
                        extra={"ticker": ticker}
                    )
                    return None
                
                response.raise_for_status()
                data = response.json()
            
            if data and "results" in data:
                results = data["results"]
                
                # Transform to simplified format
                related_companies = []
                
                for company in results:
                    related_companies.append({
                        "ticker": company.get("ticker"),
                        "name": company.get("name"),
                        "market_cap": company.get("market_cap"),
                        "similarity_score": company.get("similarity_score", 0.0),
                        "sector": company.get("sector"),
                        "industry": company.get("industry"),
                        "relationship_type": self._infer_relationship_type(
                            company.get("similarity_score", 0.0)
                        ),
                        "extended_data": company  # Store full response
                    })
                
                logger.info(
                    f"Fetched {len(related_companies)} related companies for {ticker}",
                    extra={
                        "ticker": ticker,
                        "related_count": len(related_companies)
                    }
                )
                
                return related_companies
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch related companies for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE related companies fetch failed: {str(e)}") from e
    
    def _infer_relationship_type(self, similarity_score: float) -> str:
        """
        Infer relationship type based on similarity score.
        
        Args:
            similarity_score: 0.0 to 1.0 similarity score
            
        Returns:
            Relationship type string
        """
        if similarity_score >= 0.8:
            return "direct_competitor"
        elif similarity_score >= 0.6:
            return "sector_peer"
        elif similarity_score >= 0.4:
            return "correlated"
        else:
            return "loosely_related"
    
    async def fetch_financials(
        self,
        ticker: str,
        timeframe: str = "annual",
        limit: int = 4
    ) -> Optional[List[Dict]]:
        """
        Fetch financial statements (income, balance sheet, cash flow) for a ticker.
        
        PHASE 5: Financials Implementation
        
        ⚠️ DEPRECATED ENDPOINT: Will be removed February 23, 2026
        
        Endpoint: GET /vX/reference/financials
        
        Returns quarterly and annual financial statements derived from SEC filings (XBRL).
        Includes income statement, balance sheet, cash flow statement, and comprehensive income.
        
        Args:
            ticker: Stock ticker symbol
            timeframe: "annual" or "quarterly" (default: annual)
            limit: Number of periods to return (default: 4)
            
        Returns:
            List of financial statement dictionaries or None if failed
            
        Example Return:
            [
                {
                    "ticker": "AAPL",
                    "cik": "0000320193",
                    "fiscal_period": "Q1",
                    "fiscal_year": "2025",
                    "fiscal_date_ending": "2024-12-28",
                    "filing_date": "2025-01-30",
                    "income_statement": {
                        "revenues": 119575000000,
                        "cost_of_revenue": 67772000000,
                        "gross_profit": 51803000000,
                        "operating_income": 36818000000,
                        "net_income": 33916000000,
                        "basic_earnings_per_share": 2.09
                    },
                    "balance_sheet": {
                        "total_assets": 353514000000,
                        "total_liabilities": 279414000000,
                        "total_equity": 74100000000
                    },
                    "cash_flow_statement": {
                        "operating_cash_flow": 40330000000,
                        "investing_cash_flow": -1780000000,
                        "financing_cash_flow": -27280000000
                    }
                }
            ]
        """
        try:
            await self.rate_limiter.acquire(priority=0)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "apikey": self.api_key,
                    "ticker": ticker,
                    "timeframe": timeframe,
                    "limit": limit,
                    "sort": "filing_date",
                    "order": "desc"
                }
                
                response = await client.get(
                    f"{self.base_url}/vX/reference/financials",
                    params=params
                )
                
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                # Handle 404 gracefully - no financial data available
                if response.status_code == 404:
                    logger.warning(
                        f"No financial data found for ticker (404)",
                        extra={"ticker": ticker, "timeframe": timeframe}
                    )
                    return None
                
                response.raise_for_status()
                data = response.json()
            
            if data and "results" in data:
                results = data["results"]
                
                # Transform to simplified format
                financials = []
                
                for filing in results:
                    # Extract common fields
                    financial_data = {
                        "ticker": filing.get("ticker", [ticker])[0] if isinstance(filing.get("ticker"), list) else ticker,
                        "cik": filing.get("cik"),
                        "fiscal_period": filing.get("fiscal_period"),
                        "fiscal_year": filing.get("fiscal_year"),
                        "fiscal_date_ending": filing.get("end_date"),
                        "filing_date": filing.get("filing_date"),
                        "timeframe": filing.get("timeframe"),
                        "source_filing_url": filing.get("source_filing_url")
                    }
                    
                    # Extract financial statements
                    if "financials" in filing:
                        financials_dict = filing["financials"]
                        
                        # Income Statement
                        if "income_statement" in financials_dict:
                            income = financials_dict["income_statement"]
                            financial_data["income_statement"] = {
                                "revenues": self._get_financial_value(income, "revenues"),
                                "cost_of_revenue": self._get_financial_value(income, "cost_of_revenue"),
                                "gross_profit": self._get_financial_value(income, "gross_profit"),
                                "operating_expenses": self._get_financial_value(income, "operating_expenses"),
                                "operating_income": self._get_financial_value(income, "operating_income_loss"),
                                "net_income": self._get_financial_value(income, "net_income_loss"),
                                "basic_earnings_per_share": self._get_financial_value(income, "basic_earnings_per_share"),
                                "diluted_earnings_per_share": self._get_financial_value(income, "diluted_earnings_per_share")
                            }
                        
                        # Balance Sheet
                        if "balance_sheet" in financials_dict:
                            balance = financials_dict["balance_sheet"]
                            financial_data["balance_sheet"] = {
                                "total_assets": self._get_financial_value(balance, "assets"),
                                "current_assets": self._get_financial_value(balance, "current_assets"),
                                "noncurrent_assets": self._get_financial_value(balance, "noncurrent_assets"),
                                "total_liabilities": self._get_financial_value(balance, "liabilities"),
                                "current_liabilities": self._get_financial_value(balance, "current_liabilities"),
                                "noncurrent_liabilities": self._get_financial_value(balance, "noncurrent_liabilities"),
                                "total_equity": self._get_financial_value(balance, "equity"),
                                "stockholders_equity": self._get_financial_value(balance, "equity_attributable_to_parent")
                            }
                        
                        # Cash Flow Statement
                        if "cash_flow_statement" in financials_dict:
                            cash_flow = financials_dict["cash_flow_statement"]
                            financial_data["cash_flow_statement"] = {
                                "operating_cash_flow": self._get_financial_value(
                                    cash_flow, "net_cash_flow_from_operating_activities"
                                ),
                                "investing_cash_flow": self._get_financial_value(
                                    cash_flow, "net_cash_flow_from_investing_activities"
                                ),
                                "financing_cash_flow": self._get_financial_value(
                                    cash_flow, "net_cash_flow_from_financing_activities"
                                ),
                                "net_change_in_cash": self._get_financial_value(
                                    cash_flow, "net_cash_flow"
                                )
                            }
                    
                    # Store complete raw data for reference
                    financial_data["raw_data"] = filing
                    
                    financials.append(financial_data)
                
                logger.info(
                    f"Fetched {len(financials)} financial statements for {ticker}",
                    extra={
                        "ticker": ticker,
                        "timeframe": timeframe,
                        "periods": len(financials)
                    }
                )
                
                return financials
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch financials for {ticker}",
                extra={"ticker": ticker, "timeframe": timeframe, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE financials fetch failed: {str(e)}") from e
    
    def _get_financial_value(self, data: Dict, key: str) -> Optional[float]:
        """
        Extract financial value from nested dictionary structure.
        
        MASSIVE financials have structure: {"key": {"value": <number>, "unit": "USD"}}
        
        Args:
            data: Dictionary containing financial data
            key: Key to extract
            
        Returns:
            Numeric value or None if not found
        """
        if key in data and isinstance(data[key], dict) and "value" in data[key]:
            return data[key]["value"]
        return None
    
    async def fetch_all_tickers(self, limit: int = 1000) -> Optional[List[Dict]]:
        """
        Fetch list of all available tickers.
        
        Args:
            limit: Maximum number of tickers to return
            
        Returns:
            List of ticker dictionaries or None if failed
        """
        try:
            await self.rate_limiter.acquire(priority=0)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/tickers",
                    params={
                        "apikey": self.api_key,
                        "active": "true",
                        "limit": limit,
                        "market": "stocks"
                    }
                )
                
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            if data and "results" in data:
                tickers = []
                
                for ticker in data["results"]:
                    tickers.append({
                        "ticker": ticker.get("ticker", ""),
                        "name": ticker.get("name", ""),
                        "market": ticker.get("market", ""),
                        "locale": ticker.get("locale", ""),
                        "primary_exchange": ticker.get("primary_exchange", ""),
                        "type": ticker.get("type", ""),
                        "active": ticker.get("active", True),
                        "currency_name": ticker.get("currency_name", "USD"),
                        "cik": ticker.get("cik", ""),
                        "composite_figi": ticker.get("composite_figi", ""),
                        "last_updated_utc": ticker.get("last_updated_utc", ""),
                        "provider": DataSource.POLYGON.value
                    })
                
                logger.info(
                    f"Fetched {len(tickers)} tickers from MASSIVE",
                    extra={"count": len(tickers)}
                )
                
                return tickers
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch ticker list",
                extra={"error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE ticker list fetch failed: {str(e)}")
    
    async def fetch_ticker_types(
        self,
        asset_class: Optional[str] = None,
        locale: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Fetch official ticker type classifications from MASSIVE.
        
        Reference endpoint: GET /v3/reference/tickers/types
        Returns all ticker types (CS, ETF, ADRC, PFD, etc.) with descriptions.
        
        Args:
            asset_class: Filter by asset class (stocks, options, crypto, fx, indices)
            locale: Filter by locale (us, global)
            
        Returns:
            List of ticker type dictionaries or None if failed
            
        Example Response:
            [
                {
                    "code": "CS",
                    "description": "Common Stock",
                    "asset_class": "stocks",
                    "locale": "us"
                },
                {
                    "code": "ETF",
                    "description": "Exchange Traded Fund",
                    "asset_class": "stocks",
                    "locale": "us"
                }
            ]
        """
        try:
            await self.rate_limiter.acquire(priority=0)
            
            params = {"apikey": self.api_key}
            if asset_class:
                params["asset_class"] = asset_class
            if locale:
                params["locale"] = locale
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/reference/tickers/types",
                    params=params
                )
                
                self.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    raise RateLimitException(f"Rate limit exceeded for {self.name}")
                
                response.raise_for_status()
                data = response.json()
            
            if data and "results" in data:
                types = []
                
                for ticker_type in data["results"]:
                    types.append({
                        "code": ticker_type.get("code", ""),
                        "description": ticker_type.get("description", ""),
                        "asset_class": ticker_type.get("asset_class", ""),
                        "locale": ticker_type.get("locale", ""),
                    })
                
                logger.info(
                    f"Fetched {len(types)} ticker types from MASSIVE",
                    extra={
                        "count": len(types),
                        "asset_class": asset_class,
                        "locale": locale
                    }
                )
                
                return types
            
            return None
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch ticker types",
                extra={"error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"MASSIVE ticker types fetch failed: {str(e)}")



# Singleton instance
import os
_api_key = os.getenv("MASSIVE_KEY")
if _api_key:
    massive_provider = MassiveProvider(api_key=_api_key)
else:
    logger.warning("MASSIVE_KEY not set in environment, singleton not initialized")
    massive_provider = None
