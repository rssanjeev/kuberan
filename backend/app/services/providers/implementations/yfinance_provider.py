"""
YFinance provider implementation.

Uses yfinance library for stock data fetching. No API key required.
Best for: Historical data, dividends, splits.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf

from app.core.logging_config import get_logger
from app.core.api_metrics import api_metrics
from app.repositories.provider_repository import provider_repository
from app.models.provider import DataSource
from ..base_provider import (
    BaseProvider,
    DataType,
    ProviderCapability,
    ProviderHealth,
    ProviderException
)

logger = get_logger(__name__)


class YFinanceProvider(BaseProvider):
    """
    yfinance provider - no API key required.
    
    Strengths:
    - Comprehensive historical data (20+ years)
    - Excellent dividend and split history
    - Unlimited quota (no API key)
    - Fast response times
    - Free forever
    
    Limitations:
    - No technical indicators
    - No fundamental data (financial statements)
    - Limited news
    - Real-time data has ~15 min delay
    - No forex/crypto/commodities
    
    Use cases:
    - Primary provider for historical data
    - Fallback for real-time quotes
    - Primary for dividends/splits
    """
    
    def __init__(
        self,
        priority: int = 1
    ):
        """
        Initialize yfinance provider.
        
        Args:
            priority: Provider priority (1=primary, default)
        """
        super().__init__(
            name="YFinanceProvider",
            priority=priority
        )
        
        # Set tier (always free for yfinance)
        self.tier = "free"
        
        # yfinance has no rate limits (generous, but respect their servers)
        self._rate_limits = {
            "per_minute": 2000,  # Very generous
            "per_day": None  # Unlimited
        }
        
        # Define capabilities
        self._capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.GOOD,  # 15min delay
            DataType.HISTORICAL_PRICES: ProviderCapability.EXCELLENT,
            DataType.TECHNICAL_INDICATOR: ProviderCapability.NONE,
            DataType.FUNDAMENTAL_DATA: ProviderCapability.NONE,
            DataType.NEWS: ProviderCapability.BASIC,  # Limited news
            DataType.DIVIDENDS: ProviderCapability.EXCELLENT,
            DataType.SPLITS: ProviderCapability.EXCELLENT,
            DataType.EARNINGS: ProviderCapability.BASIC,
            DataType.ANALYST_RATINGS: ProviderCapability.NONE,
            DataType.PRICE_TARGETS: ProviderCapability.NONE,
            DataType.FOREX: ProviderCapability.NONE,
            DataType.CRYPTO: ProviderCapability.NONE,
            DataType.COMMODITIES: ProviderCapability.NONE,
            DataType.ECONOMIC_INDICATORS: ProviderCapability.NONE,
            DataType.OPTIONS: ProviderCapability.BASIC,
            DataType.MARKET_STATUS: ProviderCapability.NONE
        }
        
        logger.info("YFinanceProvider initialized", extra={"priority": priority})
    
    # ==================== Data Retrieval Methods ====================
    
    @api_metrics.track_api_call(provider="yfinance", data_type="quote")
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Fetch real-time quote (note: 15min delay).
        
        Args:
            ticker: Stock symbol (e.g., AAPL)
        
        Returns:
            {
                "symbol": "AAPL",
                "price": 150.25,
                "change": 2.50,
                "change_percent": 1.69,
                "volume": 50000000,
                "timestamp": "2025-11-16T10:30:00Z",
                "source": "yfinance"
            }
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'currentPrice' not in info:
                logger.warning(f"No quote data for {ticker}")
                return None
            
            quote_data = {
                "ticker": ticker,
                "price": info.get('currentPrice') or info.get('regularMarketPrice'),
                "open": info.get('regularMarketOpen'),
                "high": info.get('regularMarketDayHigh'),
                "low": info.get('regularMarketDayLow'),
                "previous_close": info.get('previousClose'),
                "volume": info.get('regularMarketVolume'),
                "change": info.get('regularMarketChange'),
                "change_percent": info.get('regularMarketChangePercent'),
                "quote_timestamp": datetime.now(),
                "extended_data": {
                    "note": "Data may have 15min delay",
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE'),
                    "fifty_two_week_high": info.get('fiftyTwoWeekHigh'),
                    "fifty_two_week_low": info.get('fiftyTwoWeekLow')
                }
            }
            
            # Save to repository
            saved_quote = await provider_repository.save_stock_quote(quote_data, DataSource.YFINANCE)
            
            logger.info(
                "Real-time quote fetched and saved",
                extra={"ticker": ticker, "price": quote_data["price"], "source": "yfinance"}
            )
            
            # Return API-friendly format
            return {
                "symbol": ticker,
                "price": quote_data["price"],
                "open": quote_data["open"],
                "high": quote_data["high"],
                "low": quote_data["low"],
                "close": quote_data["previous_close"],
                "volume": quote_data["volume"],
                "change": quote_data["change"],
                "change_percent": quote_data["change_percent"],
                "timestamp": quote_data["quote_timestamp"].isoformat(),
                "source": "yfinance",
                "note": "Data may have 15min delay"
            }
        
        except Exception as e:
            raise ProviderException(f"Failed to fetch quote from yfinance: {str(e)}")
    
    @api_metrics.track_api_call(provider="yfinance", data_type="historical")
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Fetch historical OHLCV data.
        
        Args:
            ticker: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            [
                {
                    "date": "2025-11-15",
                    "open": 149.50,
                    "high": 151.20,
                    "low": 148.80,
                    "close": 150.25,
                    "volume": 50000000
                },
                ...
            ]
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return None
            
            # Convert DataFrame to list of dicts and save to repository
            result = []
            saved_count = 0
            
            for date, row in hist.iterrows():
                price_data = {
                    "ticker": ticker,
                    "date": date.strftime("%Y-%m-%d"),  # Repository expects date string
                    "timestamp": date,
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "interval": interval
                }
                
                # Save to repository
                await provider_repository.save_historical_price(price_data, DataSource.YFINANCE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": date.isoformat(),
                    "open": price_data["open"],
                    "high": price_data["high"],
                    "low": price_data["low"],
                    "close": price_data["close"],
                    "volume": price_data["volume"]
                })
            
            logger.info(
                f"Historical data fetched and saved",
                extra={
                    "ticker": ticker,
                    "period": period,
                    "interval": interval,
                    "count": len(result),
                    "saved": saved_count
                }
            )
            
            return result
        
        except Exception as e:
            raise ProviderException(f"Failed to fetch historical data from yfinance: {str(e)}")
    
    async def get_technical_indicator(
        self,
        ticker: str,
        indicator: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Not supported by yfinance."""
        raise ProviderException("Technical indicators not supported by yfinance")
    
    async def get_fundamental_data(
        self,
        ticker: str,
        data_type: str = "overview"
    ) -> Optional[Dict]:
        """Not supported by yfinance."""
        raise ProviderException("Fundamental data not supported by yfinance")
    
    @api_metrics.track_api_call(provider="yfinance", data_type="news")
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """
        Fetch news articles (basic support).
        
        Args:
            ticker: Stock symbol (required for yfinance)
            limit: Maximum number of articles
        
        Returns:
            [
                {
                    "title": "Apple announces...",
                    "url": "https://...",
                    "published": "2025-11-16T10:00:00Z",
                    "source": "Reuters"
                },
                ...
            ]
        """
        if not ticker:
            raise ProviderException("ticker is required for yfinance news")
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            result = []
            saved_count = 0
            
            for article in news[:limit]:
                published_dt = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                
                news_data = {
                    "ticker": ticker,
                    "title": article.get('title'),
                    "url": article.get('link'),
                    "published_at": published_dt,
                    "source": article.get('publisher'),
                    "summary": article.get('summary', ''),
                    "extended_data": {
                        "uuid": article.get('uuid'),
                        "type": article.get('type')
                    }
                }
                
                # Save to repository
                await provider_repository.save_news_article(news_data, DataSource.YFINANCE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "title": news_data["title"],
                    "url": news_data["url"],
                    "published": published_dt.isoformat(),
                    "source": news_data["source"],
                    "summary": news_data["summary"]
                })
            
            if saved_count > 0:
                logger.info(
                    f"News articles fetched and saved",
                    extra={"ticker": ticker, "count": len(result), "saved": saved_count}
                )
            
            return result
        
        except Exception as e:
            logger.warning(f"Failed to fetch news: {str(e)}")
            return []
    
    @api_metrics.track_api_call(provider="yfinance", data_type="dividends")
    async def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch dividend history (EXCELLENT coverage).
        
        Args:
            ticker: Stock symbol
        
        Returns:
            [
                {
                    "date": "2025-11-15",
                    "amount": 0.24
                },
                ...
            ]
        """
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            
            if dividends.empty:
                logger.info(f"No dividend history for {ticker}")
                return []
            
            result = []
            saved_count = 0
            
            for date, amount in dividends.items():
                dividend_data = {
                    "ticker": ticker,
                    "ex_date": date.strftime("%Y-%m-%d"),  # Convert Timestamp to string
                    "amount": float(amount),
                    "currency": "USD"
                }
                
                # Save to repository
                await provider_repository.save_dividend(dividend_data, DataSource.YFINANCE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "amount": float(amount)
                })
            
            logger.info(
                f"Dividend history fetched and saved",
                extra={"ticker": ticker, "count": len(result), "saved": saved_count}
            )
            
            return result
        
        except Exception as e:
            raise ProviderException(f"Failed to fetch dividends from yfinance: {str(e)}")
    
    @api_metrics.track_api_call(provider="yfinance", data_type="splits")
    async def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch stock split history (EXCELLENT coverage).
        
        Args:
            ticker: Stock symbol
        
        Returns:
            [
                {
                    "date": "2020-08-31",
                    "ratio": 4.0,
                    "description": "4-for-1 split"
                },
                ...
            ]
        """
        try:
            stock = yf.Ticker(ticker)
            splits = stock.splits
            
            if splits.empty:
                logger.info(f"No split history for {ticker}")
                return []
            
            result = []
            saved_count = 0
            
            for date, ratio in splits.items():
                split_ratio = float(ratio)
                description = f"{int(split_ratio)}-for-1 split" if split_ratio > 1 else f"1-for-{int(1/split_ratio)} reverse split"
                
                split_data = {
                    "ticker": ticker,
                    "split_date": date,
                    "split_ratio": split_ratio,
                    "split_type": "forward" if split_ratio > 1 else "reverse"
                }
                
                # Save to repository
                await provider_repository.save_split(split_data, DataSource.YFINANCE)
                saved_count += 1
                
                # Add to result for API response
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "ratio": split_ratio,
                    "description": description
                })
            
            logger.info(
                f"Split history fetched and saved",
                extra={"ticker": ticker, "count": len(result), "saved": saved_count}
            )
            
            return result
        
        except Exception as e:
            raise ProviderException(f"Failed to fetch splits from yfinance: {str(e)}")
    
    @api_metrics.track_api_call(provider="yfinance", data_type="earnings")
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """
        Fetch earnings data (basic support).
        
        Args:
            ticker: Stock symbol
        
        Returns:
            {
                "earnings_dates": [...],
                "quarterly_earnings": [...],
                "annual_earnings": [...]
            }
        """
        try:
            stock = yf.Ticker(ticker)
            
            result = {}
            saved_count = 0
            
            # Quarterly earnings
            if hasattr(stock, 'quarterly_earnings') and stock.quarterly_earnings is not None:
                quarterly_df = stock.quarterly_earnings
                result['quarterly_earnings'] = quarterly_df.to_dict()
                
                # Save each quarterly earnings to repository
                for date, row in quarterly_df.iterrows():
                    earnings_data = {
                        "ticker": ticker,
                        "fiscal_period": date.strftime("%Y-Q%q") if hasattr(date, 'strftime') else str(date),
                        "report_date": date if isinstance(date, datetime) else datetime.now(),
                        "eps_actual": row.get('Earnings') if 'Earnings' in row else None,
                        "revenue_actual": row.get('Revenue') if 'Revenue' in row else None,
                        "extended_data": {
                            "earnings_raw": float(row['Earnings']) if 'Earnings' in row else None,
                            "revenue_raw": float(row['Revenue']) if 'Revenue' in row else None
                        }
                    }
                    
                    await provider_repository.save_earnings(earnings_data, DataSource.YFINANCE)
                    saved_count += 1
            
            # Annual earnings
            if hasattr(stock, 'earnings') and stock.earnings is not None:
                result['annual_earnings'] = stock.earnings.to_dict()
            
            # Earnings dates
            if hasattr(stock, 'earnings_dates') and stock.earnings_dates is not None:
                result['earnings_dates'] = stock.earnings_dates.to_dict()
            
            if saved_count > 0:
                logger.info(
                    f"Earnings data fetched and saved",
                    extra={"ticker": ticker, "saved": saved_count}
                )
            
            return result if result else None
        
        except Exception as e:
            logger.warning(f"Failed to fetch earnings: {str(e)}")
            return None
    
    # ==================== Metadata Methods ====================
    
    async def health_check(self) -> ProviderHealth:
        """
        Check provider health.
        
        Tests by fetching quote for AAPL.
        """
        try:
            test_ticker = "AAPL"
            stock = yf.Ticker(test_ticker)
            info = stock.info
            
            if info and 'currentPrice' in info:
                return self.health
            else:
                raise ProviderException("Health check failed - no data returned")
        
        except Exception as e:
            logger.error(f"YFinance health check failed: {str(e)}")
            return self.health
    
    def get_capabilities(self) -> Dict[DataType, ProviderCapability]:
        """Return provider capabilities."""
        return self._capabilities.copy()
    
    def get_rate_limits(self) -> Dict[str, Optional[int]]:
        """Return rate limits."""
        return self._rate_limits.copy()
