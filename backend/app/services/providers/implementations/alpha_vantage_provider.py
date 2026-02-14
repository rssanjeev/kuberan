"""
Alpha Vantage provider implementation.

Uses direct API calls to Alpha Vantage REST API for comprehensive financial data.
No MCP dependency - works in all environments (Docker, production, development).

Best for: Real-time quotes, technical indicators, fundamental data,
          forex, crypto, commodities, economic indicators.
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


class AlphaVantageProvider(BaseProvider):
    """
    Alpha Vantage provider - comprehensive financial data.
    
    Strengths:
    - Direct API access (no MCP dependency)
    - Excellent technical indicators (50+ indicators)
    - Strong fundamental data (income statement, balance sheet, cash flow)
    - Forex, crypto, commodities support
    - Economic indicators (GDP, inflation, etc.)
    - Real-time and historical data
    - Works in all environments (Docker, production, development)
    
    Limitations:
    - Rate limits: FREE (5/min, 500/day), PREMIUM (75/min, 1500/day)
    - Requires API key
    - Can be slow during peak hours
    
    Use cases:
    - Primary provider for technical indicators
    - Primary for fundamental data
    - Primary for forex/crypto/commodities
    - Backup for real-time quotes
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(
        self,
        api_key: str,
        priority: int = 2,
        tier: str = "free"
    ):
        """
        Initialize Alpha Vantage provider.
        
        Args:
            api_key: Alpha Vantage API key
            priority: Provider priority (2=backup, default)
            tier: Subscription tier (free, premium, enterprise)
        """
        super().__init__(
            name="AlphaVantageProvider",
            priority=priority
        )
        
        self.api_key = api_key
        self.tier = tier
        self.base_url = self.BASE_URL
        
        # Set rate limits based on tier
        if tier == "free":
            per_minute, per_day = 5, 500
        elif tier == "premium":
            per_minute, per_day = 75, 1500
        elif tier == "enterprise":
            per_minute, per_day = 300, None  # Unlimited daily
        else:
            per_minute, per_day = 5, 500  # Default to free
        
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
        
        # Define capabilities (EXCELLENT for most data types)
        self._capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.EXCELLENT,
            DataType.HISTORICAL_PRICES: ProviderCapability.EXCELLENT,
            DataType.TECHNICAL_INDICATOR: ProviderCapability.EXCELLENT,  # 50+ indicators
            DataType.FUNDAMENTAL_DATA: ProviderCapability.EXCELLENT,
            DataType.NEWS: ProviderCapability.GOOD,
            DataType.DIVIDENDS: ProviderCapability.BASIC,
            DataType.SPLITS: ProviderCapability.BASIC,
            DataType.EARNINGS: ProviderCapability.EXCELLENT,
            DataType.ANALYST_RATINGS: ProviderCapability.NONE,  # Not available
            DataType.PRICE_TARGETS: ProviderCapability.NONE,
            DataType.FOREX: ProviderCapability.EXCELLENT,
            DataType.CRYPTO: ProviderCapability.EXCELLENT,
            DataType.COMMODITIES: ProviderCapability.EXCELLENT,
            DataType.ECONOMIC_INDICATORS: ProviderCapability.EXCELLENT,
            DataType.OPTIONS: ProviderCapability.NONE,
            DataType.MARKET_STATUS: ProviderCapability.GOOD
        }
        
        logger.info(
            "AlphaVantageProvider initialized",
            extra={"priority": priority, "tier": tier, "per_minute": per_minute}
        )
    
    async def _acquire_rate_limit(self, priority: int = 0):
        """Acquire rate limit permission before making request."""
        if self.rate_limiter:
            await self.rate_limiter.acquire(priority)
    
    async def _make_api_call(self, params: Dict, max_retries: int = 3) -> Dict:
        """
        Make API call to Alpha Vantage REST API with retry logic.
        
        Args:
            params: Query parameters for the API call
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            JSON response from API
            
        Raises:
            ProviderException: If API call fails after all retries
            RateLimitException: If rate limit is hit
        """
        # Validate inputs
        if not params:
            raise ProviderException("API call parameters cannot be empty")
        
        if "function" not in params:
            raise ProviderException("API function not specified in parameters")
        
        # Add API key to params
        params["apikey"] = self.api_key
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Check for Alpha Vantage error messages
                    if "Error Message" in data:
                        error_msg = data['Error Message']
                        logger.error(
                            "Alpha Vantage API error",
                            extra={"function": params.get('function'), "error": error_msg}
                        )
                        raise ProviderException(f"Alpha Vantage API error: {error_msg}")
                    
                    # Check for rate limit messages
                    if "Note" in data:
                        note = data["Note"]
                        if "API call frequency" in note or "premium subscription" in note:
                            logger.warning(
                                "Alpha Vantage rate limit warning",
                                extra={"note": note, "tier": self.tier}
                            )
                            raise RateLimitException(f"Rate limit hit: {note}")
                    
                    # Check for empty response
                    if not data or (isinstance(data, dict) and len(data) == 0):
                        raise ProviderException("Empty response from Alpha Vantage API")
                    
                    logger.debug(
                        "Alpha Vantage API call successful",
                        extra={"function": params.get('function'), "attempt": attempt + 1}
                    )
                    
                    return data
                    
            except RateLimitException:
                # Don't retry rate limit errors
                raise
            
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    raise RateLimitException("Rate limit exceeded (HTTP 429)")
                elif e.response.status_code == 404:
                    raise ProviderException(f"Invalid ticker or endpoint not found (HTTP 404)")
                elif e.response.status_code >= 500:
                    # Server errors - retry
                    if attempt < max_retries - 1:
                        logger.warning(
                            "Alpha Vantage server error, retrying",
                            extra={"status_code": e.response.status_code, "attempt": attempt + 1}
                        )
                        continue
                raise ProviderException(f"HTTP error {e.response.status_code}: {e.response.text[:200]}")
            
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        "Alpha Vantage request timeout, retrying",
                        extra={"attempt": attempt + 1, "timeout": 30.0}
                    )
                    continue
                raise ProviderException(f"Request timeout after {max_retries} attempts")
            
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        "Alpha Vantage API call failed, retrying",
                        extra={"error": str(e), "attempt": attempt + 1}
                    )
                    continue
                raise ProviderException(f"API call failed after {max_retries} attempts: {str(e)}")
        
        # If we get here, all retries failed
        raise ProviderException(f"API call failed after {max_retries} attempts: {str(last_error)}")
    
    def _update_rate_limits_from_response(self, response: Dict):
        """Update rate limits from API response headers."""
        if self.rate_limiter and isinstance(response, dict):
            # Alpha Vantage doesn't provide rate limit headers in response
            # But we can detect "Note" messages about rate limits
            if "Note" in response:
                note = response["Note"]
                if "API call frequency" in note or "premium subscription" in note:
                    logger.warning(
                        "Alpha Vantage rate limit message",
                        extra={"note": note}
                    )
    
    # ==================== Data Retrieval Methods ====================
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="quote")
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Fetch real-time quote using GLOBAL_QUOTE API endpoint.
        
        API: https://www.alphavantage.co/query?function=GLOBAL_QUOTE
        """
        try:
            await self._acquire_rate_limit(priority=1)  # High priority
            
            # Call Alpha Vantage API directly
            response = await self._make_api_call({
                "function": "GLOBAL_QUOTE",
                "symbol": ticker
            })
            
            self._update_rate_limits_from_response(response)
            
            if not response or "Global Quote" not in response:
                logger.warning(f"No quote data for {ticker}")
                return None
            
            quote = response["Global Quote"]
            
            quote_data = {
                "ticker": quote.get("01. symbol", ticker),
                "price": float(quote.get("05. price", 0)),
                "open": float(quote.get("02. open", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": float(quote.get("10. change percent", "0%").rstrip('%')),
                "quote_timestamp": datetime.now(),
                "extended_data": {
                    "trading_day": quote.get("07. latest trading day"),
                    "alphavantage_raw": quote
                }
            }
            
            # Save to repository
            saved_quote = await provider_repository.save_stock_quote(quote_data, DataSource.ALPHA_VANTAGE)
            
            logger.info(
                "Real-time quote fetched and saved",
                extra={"ticker": ticker, "price": quote_data["price"], "source": "alphavantage"}
            )
            
            # Return API-friendly format
            return {
                "symbol": quote_data["ticker"],
                "price": quote_data["price"],
                "open": quote_data["open"],
                "high": quote_data["high"],
                "low": quote_data["low"],
                "volume": quote_data["volume"],
                "change": quote_data["change"],
                "change_percent": quote_data["change_percent"],
                "timestamp": quote_data["quote_timestamp"].isoformat(),
                "source": "alphavantage"
            }
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch quote from Alpha Vantage: {str(e)}")
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="historical")
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Fetch historical prices using TIME_SERIES_* API endpoints.
        
        API Functions:
        - TIME_SERIES_INTRADAY (1min, 5min, 15min, 30min, 60min)
        - TIME_SERIES_DAILY (daily data)
        - TIME_SERIES_WEEKLY (weekly data)
        - TIME_SERIES_MONTHLY (monthly data)
        """
        try:
            await self._acquire_rate_limit(priority=0)  # Normal priority
            
            # Determine which API function to use based on interval
            params = {"symbol": ticker}
            
            if interval in ["1min", "5min", "15min", "30min", "60min"]:
                # Use intraday
                params["function"] = "TIME_SERIES_INTRADAY"
                params["interval"] = interval
                params["outputsize"] = "full" if period in ["1y", "2y", "5y", "max"] else "compact"
                time_series_key = f"Time Series ({interval})"
            
            elif interval == "1d":
                # Use daily
                params["function"] = "TIME_SERIES_DAILY"
                params["outputsize"] = "full" if period in ["1y", "2y", "5y", "10y", "max"] else "compact"
                time_series_key = "Time Series (Daily)"
            
            elif interval == "1wk":
                # Use weekly
                params["function"] = "TIME_SERIES_WEEKLY"
                time_series_key = "Weekly Time Series"
            
            elif interval == "1mo":
                # Use monthly
                params["function"] = "TIME_SERIES_MONTHLY"
                time_series_key = "Monthly Time Series"
            
            else:
                raise ProviderException(f"Unsupported interval: {interval}")
            
            # Make API call
            response = await self._make_api_call(params)
            
            self._update_rate_limits_from_response(response)
            
            if not response or time_series_key not in response:
                logger.warning(f"No historical data for {ticker}")
                return None
            
            # Parse time series data and save to repository
            time_series = response[time_series_key]
            result = []
            saved_count = 0
            
            for date_str, values in time_series.items():
                price_data = {
                    "ticker": ticker,
                    "timestamp": datetime.fromisoformat(date_str),
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0)),
                    "interval": interval
                }
                
                # Save to repository
                await provider_repository.save_historical_price(price_data, DataSource.ALPHA_VANTAGE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "date": date_str,
                    "timestamp": price_data["timestamp"].isoformat(),
                    "open": price_data["open"],
                    "high": price_data["high"],
                    "low": price_data["low"],
                    "close": price_data["close"],
                    "volume": price_data["volume"]
                })
            
            # Sort by date (newest first)
            result.sort(key=lambda x: x["date"], reverse=True)
            
            logger.info(
                f"Historical data fetched and saved",
                extra={
                    "ticker": ticker,
                    "interval": interval,
                    "count": len(result),
                    "saved": saved_count
                }
            )
            
            return result
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch historical data from Alpha Vantage: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="daily_prices")
    async def fetch_etf_daily_prices(
        self,
        ticker: str,
        outputsize: str = "compact"
    ) -> Dict[str, Dict]:
        """
        Fetch daily historical prices for ETF using TIME_SERIES_DAILY.
        
        Args:
            ticker: ETF ticker symbol
            outputsize: 'compact' (last 100 data points) or 'full' (20+ years)
        
        Returns:
            Dictionary with date strings as keys, each containing:
            {
                "2025-11-23": {
                    "1. open": "450.12",
                    "2. high": "452.34",
                    "3. low": "449.67",
                    "4. close": "451.89",
                    "5. volume": "12345678"
                },
                ...
            }
        
        API: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Validate outputsize
            if outputsize not in ["compact", "full"]:
                raise ValueError(f"Invalid outputsize: {outputsize}. Must be 'compact' or 'full'.")
            
            # Make API call
            response = await self._make_api_call({
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "outputsize": outputsize
            })
            
            self._update_rate_limits_from_response(response)
            
            # Check for time series data
            if "Time Series (Daily)" not in response:
                logger.error(
                    "No daily price data found in response",
                    extra={
                        "ticker": ticker,
                        "outputsize": outputsize,
                        "response_keys": list(response.keys()) if isinstance(response, dict) else "not_a_dict",
                        "response_sample": str(response)[:500] if response else "empty"
                    }
                )
                raise ProviderException(f"No daily price data available for {ticker}")
            
            time_series = response["Time Series (Daily)"]
            
            logger.info(
                "Daily prices fetched successfully",
                extra={
                    "ticker": ticker,
                    "outputsize": outputsize,
                    "data_points": len(time_series)
                }
            )
            
            return time_series
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch daily prices from Alpha Vantage: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="technical_indicator")
    async def get_technical_indicator(
        self,
        ticker: str,
        indicator: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Fetch technical indicator data.
        
        Alpha Vantage supports 50+ indicators via direct API.
        
        Supported indicators:
        - SMA, EMA, WMA, DEMA, TEMA, TRIMA
        - RSI, MACD, STOCH, ADX, CCI, AROON, BBANDS
        - ATR, AD, OBV, PLUS_DI, MINUS_DI, APO, PPO
        - And many more...
        
        API: https://www.alphavantage.co/query?function={INDICATOR}
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Build function name (Alpha Vantage API uses uppercase indicator names)
            indicator_upper = indicator.upper()
            
            # Prepare API parameters
            api_params = {
                "function": indicator_upper,
                "symbol": ticker,
                "interval": params.get("interval", "daily") if params else "daily",
                "time_period": params.get("period", 14) if params else 14,
                "series_type": params.get("series_type", "close") if params else "close"
            }
            
            # Make API call
            response = await self._make_api_call(api_params)
            
            self._update_rate_limits_from_response(response)
            
            if not response:
                return None
            
            return {
                "indicator": indicator_upper,
                "ticker": ticker,
                "parameters": params or {},
                "data": response
            }
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch technical indicator: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="fundamental_data")
    async def get_fundamental_data(
        self,
        ticker: str,
        data_type: str
    ) -> Optional[Dict]:
        """
        Fetch fundamental data.
        
        API Functions:
        - OVERVIEW: Company overview
        - INCOME_STATEMENT: Income statement
        - BALANCE_SHEET: Balance sheet
        - CASH_FLOW: Cash flow statement
        - EARNINGS: Earnings data
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            data_type_upper = data_type.upper()
            
            # Validate data type
            valid_types = ["OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "EARNINGS"]
            if data_type_upper not in valid_types:
                raise ProviderException(f"Fundamental data type {data_type} not supported")
            
            # Make API call
            response = await self._make_api_call({
                "function": data_type_upper,
                "symbol": ticker
            })
            
            self._update_rate_limits_from_response(response)
            
            return response
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch fundamental data: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="news")
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """
        Fetch news articles.
        
        API: https://www.alphavantage.co/query?function=NEWS_SENTIMENT
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Make API call
            api_params = {
                "function": "NEWS_SENTIMENT",
                "limit": limit
            }
            if ticker:
                api_params["tickers"] = ticker
            
            response = await self._make_api_call(api_params)
            
            self._update_rate_limits_from_response(response)
            
            if not response or "feed" not in response:
                return []
            
            result = []
            saved_count = 0
            
            for article in response["feed"][:limit]:
                # Parse timestamp
                time_published = article.get("time_published", "")
                try:
                    published_at = datetime.strptime(time_published, "%Y%m%dT%H%M%S")
                except ValueError:
                    published_at = datetime.now()
                
                news_data = {
                    "ticker": ticker if ticker else "GENERAL",
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "published_at": published_at,
                    "source": article.get("source"),
                    "summary": article.get("summary"),
                    "sentiment": article.get("overall_sentiment_label"),
                    "extended_data": {
                        "sentiment_score": article.get("overall_sentiment_score"),
                        "topics": article.get("topics", []),
                        "ticker_sentiment": article.get("ticker_sentiment", [])
                    }
                }
                
                # Save to repository
                await provider_repository.save_news_article(news_data, DataSource.ALPHA_VANTAGE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "title": news_data["title"],
                    "url": news_data["url"],
                    "published": published_at.isoformat(),
                    "source": news_data["source"],
                    "summary": news_data["summary"],
                    "sentiment": news_data["sentiment"],
                    "sentiment_score": news_data["extended_data"]["sentiment_score"]
                })
            
            if saved_count > 0:
                logger.info(
                    f"News articles fetched and saved",
                    extra={"ticker": ticker or "GENERAL", "count": len(result), "saved": saved_count}
                )
            
            return result
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.warning(f"Failed to fetch news: {str(e)}")
            return []
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="dividends")
    async def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch dividend history.
        
        Alpha Vantage provides dividend data via TIME_SERIES_DAILY_ADJUSTED.
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Make API call
            response = await self._make_api_call({
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "outputsize": "full"
            })
            
            self._update_rate_limits_from_response(response)
            
            if not response or "Time Series (Daily)" not in response:
                return []
            
            # Extract dividends from adjusted data
            time_series = response["Time Series (Daily)"]
            result = []
            
            for date_str, values in time_series.items():
                dividend = float(values.get("7. dividend amount", 0))
                if dividend > 0:
                    result.append({
                        "date": date_str,
                        "amount": dividend
                    })
            
            return result
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch dividends: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="splits")
    async def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch stock split history.
        
        Alpha Vantage provides split data via TIME_SERIES_DAILY_ADJUSTED.
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Make API call
            response = await self._make_api_call({
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "outputsize": "full"
            })
            
            self._update_rate_limits_from_response(response)
            
            if not response or "Time Series (Daily)" not in response:
                return []
            
            # Extract splits from adjusted data
            time_series = response["Time Series (Daily)"]
            result = []
            
            for date_str, values in time_series.items():
                split_coefficient = float(values.get("8. split coefficient", 1.0))
                if split_coefficient != 1.0:
                    result.append({
                        "date": date_str,
                        "ratio": split_coefficient,
                        "description": f"{int(split_coefficient)}-for-1 split" if split_coefficient > 1 
                                      else f"1-for-{int(1/split_coefficient)} reverse split"
                    })
            
            return result
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch splits: {str(e)}") from e
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="earnings")
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """
        Fetch earnings data.
        
        API: https://www.alphavantage.co/query?function=EARNINGS
        """
        try:
            await self._acquire_rate_limit(priority=0)
            
            # Make API call
            response = await self._make_api_call({
                "function": "EARNINGS",
                "symbol": ticker
            })
            
            self._update_rate_limits_from_response(response)
            
            return response
        
        except RateLimitException:
            raise
        except Exception as e:
            raise ProviderException(f"Failed to fetch earnings: {str(e)}") from e
    
    # ==================== ETF Data Methods ====================
    
    @api_metrics.track_api_call(provider="alpha_vantage", data_type="etf_profile")
    async def fetch_etf_profile(self, ticker: str) -> Dict:
        """
        Fetch complete ETF profile including holdings and sectors.
        
        Uses ETF_PROFILE function from Alpha Vantage API.
        
        Args:
            ticker: ETF ticker symbol (e.g., "SPY", "VOO")
            
        Returns:
            Complete ETF data including:
            - Fund fundamentals (expense ratio, AUM, etc.)
            - Complete holdings list with weights
            - Sector allocations
            
        Raises:
            RateLimitException: If rate limit is exceeded
            ProviderException: If API call fails
            
        API Endpoint: https://www.alphavantage.co/query?function=ETF_PROFILE
        """
        ticker = ticker.upper().strip()
        
        logger.info("Fetching ETF profile from Alpha Vantage", extra={"ticker": ticker})
        
        try:
            # Acquire rate limit permission
            await self._acquire_rate_limit()
            
            # Make API call
            params = {
                "function": "ETF_PROFILE",
                "symbol": ticker
            }
            
            response = await self._make_api_call(params)
            
            # Parse response
            if not response:
                raise ProviderException(f"Empty response for ticker: {ticker}")
            
            # Alpha Vantage ETF_PROFILE structure
            # Response contains root-level fields: net_assets, net_expense_ratio, 
            #                    portfolio_turnover, dividend_yield, inception_date, leveraged
            # Plus arrays: holdings[], sectors[]
            
            etf_data = {
                "name": response.get("name"),
                "net_assets": self._parse_float(response.get("net_assets")),
                "net_expense_ratio": self._parse_float(response.get("net_expense_ratio")),
                "portfolio_turnover": self._parse_float(response.get("portfolio_turnover")),
                "dividend_yield": self._parse_float(response.get("dividend_yield")),
                "inception_date": response.get("inception_date"),
                "leveraged": response.get("leveraged"),
                "holdings": [],
                "sectors": []
            }
            
            # Parse holdings (Alpha Vantage provides "holdings" array)
            raw_holdings = response.get("holdings", [])
            for holding in raw_holdings:
                etf_data["holdings"].append({
                    "symbol": holding.get("symbol"),
                    "description": holding.get("description", holding.get("name")),
                    "weight": self._parse_float(holding.get("weight"))
                })
            
            # Parse sectors (Alpha Vantage provides "sectors" array, NOT "sectorWeights" object)
            raw_sectors = response.get("sectors", [])
            for sector_data in raw_sectors:
                etf_data["sectors"].append({
                    "sector": sector_data.get("sector"),
                    "weight": self._parse_float(sector_data.get("weight"))
                })
            
            self._update_rate_limits_from_response(response)
            
            logger.info(
                "ETF profile fetched successfully",
                extra={
                    "ticker": ticker,
                    "holdings": len(etf_data["holdings"]),
                    "sectors": len(etf_data["sectors"])
                }
            )
            
            return etf_data
        
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(
                "Failed to fetch ETF profile",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise ProviderException(f"Failed to fetch ETF profile: {str(e)}") from e
    
    def _parse_float(self, value) -> Optional[float]:
        """
        Safely parse float value from API response.
        
        Args:
            value: Value to parse (can be string, number, or None)
            
        Returns:
            Float value or None if parsing fails
        """
        if value is None:
            return None
        
        try:
            # Remove percentage signs and commas
            if isinstance(value, str):
                value = value.replace("%", "").replace(",", "")
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # ==================== Metadata Methods ====================
    
    async def health_check(self) -> ProviderHealth:
        """
        Check provider health by fetching a test quote.
        """
        try:
            test_ticker = "IBM"  # Alpha Vantage example ticker
            quote = await self.get_real_time_quote(test_ticker)
            
            if quote and quote.get("price"):
                return self.health
            else:
                raise ProviderException("Health check failed - no data returned")
        
        except Exception as e:
            logger.error(f"Alpha Vantage health check failed: {str(e)}")
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
