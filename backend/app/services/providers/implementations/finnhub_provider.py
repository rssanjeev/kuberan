"""
Finnhub provider implementation.

Real-time market data provider specializing in:
- Real-time quotes
- Company news
- Earnings calendars
- Analyst recommendations
- Price targets

Best for: Real-time quotes, news, earnings events.
"""

from typing import Dict, List, Optional
from datetime import datetime
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


class FinnhubProvider(BaseProvider):
    """
    Finnhub provider - real-time market data.
    
    Strengths:
    - Excellent real-time quotes
    - Comprehensive company news
    - Earnings calendars
    - Analyst ratings and price targets
    - Fast response times
    
    Limitations:
    - Rate limit: 60 calls/minute (free tier)
    - No technical indicators
    - No historical data beyond basic
    - Limited fundamental data
    
    Use cases:
    - Real-time quote backup (when Alpha Vantage unavailable)
    - Primary for news and analyst data
    - Earnings calendar events
    """
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(
        self,
        api_key: str,
        priority: int = 3
    ):
        """
        Initialize Finnhub provider.
        
        Args:
            api_key: Finnhub API key
            priority: Provider priority (3=backup)
        """
        super().__init__(
            name="FinnhubProvider",
            priority=priority
        )
        
        self.api_key = api_key
        self.tier = "free"  # Finnhub only has free tier
        self.base_url = self.BASE_URL
        
        # Initialize adaptive rate limiter (60/minute for free)
        self.rate_limiter = AdaptiveRateLimiter(
            provider_name=self.name,
            per_minute=60,
            per_day=None  # No daily limit specified
        )
        
        self._rate_limits = {
            "per_minute": 60,
            "per_day": None
        }
        
        # Define capabilities
        self._capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.EXCELLENT,
            DataType.HISTORICAL_PRICES: ProviderCapability.BASIC,  # Limited
            DataType.TECHNICAL_INDICATOR: ProviderCapability.NONE,
            DataType.FUNDAMENTAL_DATA: ProviderCapability.GOOD,  # Company profile
            DataType.NEWS: ProviderCapability.EXCELLENT,
            DataType.DIVIDENDS: ProviderCapability.NONE,
            DataType.SPLITS: ProviderCapability.NONE,
            DataType.EARNINGS: ProviderCapability.EXCELLENT,
            DataType.ANALYST_RATINGS: ProviderCapability.EXCELLENT,
            DataType.PRICE_TARGETS: ProviderCapability.EXCELLENT,
            DataType.FOREX: ProviderCapability.GOOD,
            DataType.CRYPTO: ProviderCapability.GOOD,
            DataType.COMMODITIES: ProviderCapability.NONE,
            DataType.ECONOMIC_INDICATORS: ProviderCapability.NONE,
            DataType.OPTIONS: ProviderCapability.NONE,
            DataType.MARKET_STATUS: ProviderCapability.GOOD
        }
        
        logger.info(
            "FinnhubProvider initialized",
            extra={"priority": priority, "per_minute": 60}
        )
    
    async def _acquire_rate_limit(self, priority: int = 0):
        """Acquire rate limit permission before making request."""
        if self.rate_limiter:
            await self.rate_limiter.acquire(priority)
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Finnhub API.
        
        Args:
            endpoint: API endpoint (e.g., "/quote")
            params: Query parameters
        
        Returns:
            API response as dict
        """
        if params is None:
            params = {}
        
        params["token"] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            
            # Update rate limits from headers if available
            if self.rate_limiter:
                headers = response.headers
                if "X-Ratelimit-Limit" in headers:
                    limit = int(headers["X-Ratelimit-Limit"])
                    self.rate_limiter.update_limits(per_minute=limit)
            
            return response.json()
    
    # ==================== Data Retrieval Methods ====================
    
    @api_metrics.track_api_call(provider="finnhub", data_type="quote")
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Fetch real-time quote from Finnhub.
        
        Endpoint: /quote
        """
        try:
            await self._acquire_rate_limit(priority=1)
            
            data = await self._make_request("/quote", {"symbol": ticker})
            
            if not data or data.get("c") is None:
                logger.warning(f"No quote data for {ticker}")
                return None
            
            # Parse timestamp
            timestamp = datetime.fromtimestamp(data["t"]) if data.get("t") else datetime.now()
            
            quote_data = {
                "ticker": ticker,
                "price": float(data["c"]),  # Current price
                "open": float(data.get("o", 0)),
                "high": float(data["h"]),
                "low": float(data["l"]),
                "previous_close": float(data.get("pc", 0)),
                "change": float(data.get("d", 0)),  # Change
                "change_percent": float(data.get("dp", 0)),  # Change percent
                "quote_timestamp": timestamp,
                "volume": None,  # Finnhub quote doesn't include volume
                "extended_data": {
                    "finnhub_raw": data
                }
            }
            
            # Save to repository
            saved_quote = await provider_repository.save_stock_quote(quote_data, DataSource.FINNHUB)
            
            logger.info(
                "Real-time quote fetched and saved",
                extra={"ticker": ticker, "price": quote_data["price"], "source": "finnhub"}
            )
            
            # Return API-friendly format
            return {
                "symbol": ticker,
                "price": quote_data["price"],
                "open": quote_data["open"],
                "high": quote_data["high"],
                "low": quote_data["low"],
                "previous_close": quote_data["previous_close"],
                "change": quote_data["change"],
                "change_percent": quote_data["change_percent"],
                "timestamp": timestamp.isoformat(),
                "source": "finnhub"
            }
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch quote from Finnhub: {str(e)}")
    
    @api_metrics.track_api_call(provider="finnhub", data_type="historical")
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Fetch historical prices (basic support).
        
        Finnhub has limited historical data support.
        Use other providers for comprehensive historical data.
        
        Endpoint: /stock/candle
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Calculate time range
            from datetime import datetime, timedelta
            end = datetime.now()
            
            # Map period to days
            period_map = {
                "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
                "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
            }
            days = period_map.get(period, 30)
            start = end - timedelta(days=days)
            
            # Map interval to resolution
            resolution_map = {
                "1m": "1", "5m": "5", "15m": "15", "30m": "30",
                "1h": "60", "1d": "D", "1wk": "W", "1mo": "M"
            }
            resolution = resolution_map.get(interval, "D")
            
            data = await self._make_request("/stock/candle", {
                "symbol": ticker,
                "resolution": resolution,
                "from": int(start.timestamp()),
                "to": int(end.timestamp())
            })
            
            if not data or data.get("s") != "ok":
                logger.warning(f"No historical data for {ticker}")
                return None
            
            # Convert to standard format
            result = []
            timestamps = data.get("t", [])
            opens = data.get("o", [])
            highs = data.get("h", [])
            lows = data.get("l", [])
            closes = data.get("c", [])
            volumes = data.get("v", [])
            
            for i in range(len(timestamps)):
                result.append({
                    "date": datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d"),
                    "timestamp": datetime.fromtimestamp(timestamps[i]).isoformat(),
                    "open": opens[i],
                    "high": highs[i],
                    "low": lows[i],
                    "close": closes[i],
                    "volume": volumes[i]
                })
            
            # Sort by date (newest first)
            result.sort(key=lambda x: x["date"], reverse=True)
            
            return result
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch historical data: {str(e)}") from e
    
    async def get_technical_indicator(
        self,
        ticker: str,
        indicator: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Technical indicators not supported by Finnhub."""
        raise ProviderException("Technical indicators not supported by Finnhub - use Alpha Vantage")
    
    async def get_fundamental_data(
        self,
        ticker: str,
        data_type: str
    ) -> Optional[Dict]:
        """
        Fetch fundamental data (company profile).
        
        Endpoint: /stock/profile2
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            if data_type.upper() == "PROFILE":
                data = await self._make_request("/stock/profile2", {"symbol": ticker})
                return data
            else:
                raise ProviderException(f"Fundamental data type {data_type} not supported by Finnhub")
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch fundamental data: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="finnhub", data_type="news")
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """
        Fetch company news.
        
        Endpoint: /company-news
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            if not ticker:
                raise ProviderException("ticker is required for Finnhub news")
            
            # Get news from last 7 days
            from datetime import datetime, timedelta
            end = datetime.now()
            start = end - timedelta(days=7)
            
            data = await self._make_request("/company-news", {
                "symbol": ticker,
                "from": start.strftime("%Y-%m-%d"),
                "to": end.strftime("%Y-%m-%d")
            })
            
            if not data:
                return []
            
            result = []
            saved_count = 0
            
            for article in data[:limit]:
                # Parse timestamp
                published_at = datetime.fromtimestamp(article["datetime"]) if article.get("datetime") else datetime.now()
                
                news_data = {
                    "ticker": ticker,
                    "title": article.get("headline"),
                    "url": article.get("url"),
                    "published_at": published_at,
                    "source": article.get("source"),
                    "summary": article.get("summary"),
                    "sentiment": None,  # Not provided by Finnhub
                    "extended_data": {
                        "category": article.get("category"),
                        "image": article.get("image"),
                        "related": article.get("related", [])
                    }
                }
                
                # Save to repository
                await provider_repository.save_news_article(news_data, DataSource.FINNHUB)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "title": news_data["title"],
                    "url": news_data["url"],
                    "published": published_at.isoformat(),
                    "source": news_data["source"],
                    "summary": news_data["summary"],
                    "sentiment": None,
                    "sentiment_score": None
                })
            
            if saved_count > 0:
                logger.info(
                    f"News articles fetched and saved",
                    extra={"ticker": ticker, "count": len(result), "saved": saved_count}
                )
            
            return result
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            logger.warning(f"Failed to fetch news: HTTP {e.response.status_code}")
            return []
        except Exception as e:
            logger.warning(f"Failed to fetch news: {str(e)}")
            return []
    
    async def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """Dividend data not supported by Finnhub."""
        raise ProviderException("Dividend data not supported by Finnhub - use yfinance or Alpha Vantage")
    
    async def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """Stock split data not supported by Finnhub."""
        raise ProviderException("Stock split data not supported by Finnhub - use yfinance or Alpha Vantage")
    
    @api_metrics.track_api_call(provider="finnhub", data_type="earnings")
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """
        Fetch earnings calendar.
        
        Endpoint: /calendar/earnings
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            data = await self._make_request("/calendar/earnings", {"symbol": ticker})
            
            return data
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch earnings: {str(e)}") from e
    
    # ==================== Finnhub-Specific Methods ====================
    
    @api_metrics.track_api_call(provider="finnhub", data_type="analyst_ratings")
    async def get_analyst_ratings(self, ticker: str) -> Optional[Dict]:
        """
        Fetch analyst recommendations.
        
        Endpoint: /stock/recommendation
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            data = await self._make_request("/stock/recommendation", {"symbol": ticker})
            
            return {"recommendations": data}
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch analyst ratings: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="finnhub", data_type="price_targets")
    async def get_price_targets(self, ticker: str) -> Optional[Dict]:
        """
        Fetch price targets.
        
        Endpoint: /stock/price-target
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            data = await self._make_request("/stock/price-target", {"symbol": ticker})
            
            return data
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitException("Finnhub rate limit exceeded")
            raise ProviderException(f"HTTP error from Finnhub: {e.response.status_code}") from e
        except Exception as e:
            raise ProviderException(f"Failed to fetch price targets: {str(e)}") from e
    
    # ==================== Metadata Methods ====================
    
    async def health_check(self) -> ProviderHealth:
        """Check provider health by fetching a test quote."""
        try:
            test_ticker = "AAPL"
            quote = await self.get_real_time_quote(test_ticker)
            
            if quote and quote.get("price"):
                return self.health
            else:
                raise ProviderException("Health check failed - no data returned")
        
        except Exception as e:
            logger.error(f"Finnhub health check failed: {str(e)}")
            return self.health
    
    def get_capabilities(self) -> Dict[DataType, ProviderCapability]:
        """Return provider capabilities."""
        return self._capabilities.copy()
    
    def get_rate_limits(self) -> Dict[str, Optional[int]]:
        """Return rate limits."""
        if self.rate_limiter:
            return {
                "per_minute": self.rate_limiter.per_minute_limit,
                "per_day": self.rate_limiter.per_day_limit
            }
        return self._rate_limits.copy()
