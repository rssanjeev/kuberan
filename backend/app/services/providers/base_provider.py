"""
Base provider interface and shared types.

All data providers (Alpha Vantage, Finnhub, yfinance, etc.) must implement
the BaseProvider abstract class to be compatible with the multi-provider system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class DataType(str, Enum):
    """Types of financial data that can be fetched."""
    REAL_TIME_QUOTE = "real_time_quote"
    HISTORICAL_PRICES = "historical_prices"
    TECHNICAL_INDICATOR = "technical_indicator"
    FUNDAMENTAL_DATA = "fundamental_data"
    NEWS = "news"
    DIVIDENDS = "dividends"
    SPLITS = "splits"
    EARNINGS = "earnings"
    ANALYST_RATINGS = "analyst_ratings"
    PRICE_TARGETS = "price_targets"
    FOREX = "forex"
    CRYPTO = "crypto"
    COMMODITIES = "commodities"
    ECONOMIC_INDICATORS = "economic_indicators"
    OPTIONS = "options"
    MARKET_STATUS = "market_status"


class ProviderCapability(str, Enum):
    """
    Provider's capability level for a specific data type.
    
    EXCELLENT: Primary data source, comprehensive coverage, high reliability
    GOOD: Secondary source, good coverage, reliable
    BASIC: Tertiary source, limited coverage, use as fallback
    NONE: Not supported by this provider
    """
    EXCELLENT = "excellent"
    GOOD = "good"
    BASIC = "basic"
    NONE = "none"


class ProviderHealth(BaseModel):
    """Health status of a provider."""
    is_healthy: bool
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_response_time_ms: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls
    
    @property
    def reliability_score(self) -> float:
        """
        Calculate reliability score (0.0 to 1.0).
        
        Factors:
        - Success rate (70% weight)
        - Recent failures (20% weight)
        - Response time (10% weight)
        """
        # Base score from success rate
        score = self.success_rate * 0.70
        
        # Penalty for consecutive failures
        failure_penalty = min(self.consecutive_failures * 0.05, 0.20)
        score -= failure_penalty
        
        # Response time bonus/penalty (faster = better)
        if self.average_response_time_ms:
            if self.average_response_time_ms < 500:  # Very fast
                score += 0.10
            elif self.average_response_time_ms < 1000:  # Fast
                score += 0.05
            elif self.average_response_time_ms > 3000:  # Slow
                score -= 0.05
            elif self.average_response_time_ms > 5000:  # Very slow
                score -= 0.10
        
        return max(0.0, min(1.0, score))


class ProviderException(Exception):
    """Base exception for provider errors."""
    pass


class RateLimitException(ProviderException):
    """Raised when provider rate limit is exceeded."""
    
    def __init__(self, provider_name: str, retry_after: Optional[int] = None):
        self.provider_name = provider_name
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {provider_name}"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        super().__init__(message)


class BaseProvider(ABC):
    """
    Abstract base class for all data providers.
    
    All providers must implement this interface to be compatible with
    the multi-provider system.
    
    Key Responsibilities:
    - Fetch financial data from external APIs
    - Report capabilities for each data type
    - Track rate limits and quota usage
    - Provide health status
    - Handle errors gracefully
    """
    
    def __init__(self, name: str, priority: int = 2):
        """
        Initialize provider.
        
        Args:
            name: Provider name (e.g., "AlphaVantageProvider")
            priority: Provider priority (1=primary, 2=backup, 3=tertiary)
        """
        self.name = name
        self.priority = priority
        self.health = ProviderHealth(is_healthy=True)
        self.rate_limiter = None  # Set by subclass if needed
        self.tier = "free"  # "free", "basic", "premium", "enterprise"
        
        logger.info(
            f"Initialized {name}",
            extra={"priority": priority, "tier": self.tier}
        )
    
    # ==================== Data Retrieval Methods ====================
    
    @abstractmethod
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Fetch real-time quote for ticker.
        
        Returns:
            {
                "symbol": "AAPL",
                "price": 150.00,
                "change": 2.50,
                "change_percent": 1.69,
                "volume": 50000000,
                "timestamp": "2025-11-16T10:30:00Z"
            }
        """
        pass
    
    @abstractmethod
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Fetch historical OHLCV prices.
        
        Args:
            ticker: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            [
                {
                    "date": "2025-11-16",
                    "open": 148.50,
                    "high": 151.00,
                    "low": 147.00,
                    "close": 150.00,
                    "volume": 50000000
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    async def get_technical_indicator(
        self,
        ticker: str,
        indicator: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Fetch technical indicator data.
        
        Args:
            ticker: Stock symbol
            indicator: Indicator name (SMA, EMA, RSI, MACD, BBANDS, etc.)
            params: Indicator parameters (e.g., {"period": 14, "timeframe": "daily"})
        
        Returns:
            {
                "indicator": "RSI",
                "ticker": "AAPL",
                "timeframe": "daily",
                "parameters": {"period": 14},
                "data": [
                    {"date": "2025-11-16", "value": 65.4},
                    ...
                ]
            }
        """
        pass
    
    @abstractmethod
    async def get_fundamental_data(
        self,
        ticker: str,
        data_type: str
    ) -> Optional[Dict]:
        """
        Fetch fundamental data.
        
        Args:
            ticker: Stock symbol
            data_type: Type of fundamental data (overview, income_statement,
                      balance_sheet, cash_flow, earnings, etc.)
        
        Returns:
            Dictionary with fundamental data (structure varies by data_type)
        """
        pass
    
    @abstractmethod
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """
        Fetch news articles.
        
        Args:
            ticker: Optional stock symbol to filter news
            limit: Maximum number of articles
        
        Returns:
            [
                {
                    "title": "Article title",
                    "url": "https://...",
                    "published": "2025-11-16T10:00:00Z",
                    "source": "Reuters",
                    "summary": "Article summary...",
                    "sentiment": "positive",  # If available
                    "sentiment_score": 0.75    # If available
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    async def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch dividend history.
        
        Returns:
            [
                {
                    "date": "2025-11-15",
                    "amount": 0.25
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    async def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """
        Fetch stock split history.
        
        Returns:
            [
                {
                    "date": "2025-06-01",
                    "split_ratio": "4:1"
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """
        Fetch earnings data.
        
        Returns:
            {
                "historical": [
                    {
                        "date": "2025-Q3",
                        "eps_actual": 1.50,
                        "eps_estimate": 1.45,
                        "revenue": 50000000000
                    },
                    ...
                ],
                "upcoming": [
                    {
                        "date": "2025-Q4",
                        "eps_estimate": 1.60
                    }
                ]
            }
        """
        pass
    
    # ==================== Metadata Methods ====================
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """
        Check provider health status.
        
        Should make a lightweight API call to verify connectivity.
        Updates internal health metrics.
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[DataType, ProviderCapability]:
        """
        Get provider capabilities for each data type.
        
        Returns:
            {
                DataType.REAL_TIME_QUOTE: ProviderCapability.EXCELLENT,
                DataType.HISTORICAL_PRICES: ProviderCapability.GOOD,
                DataType.TECHNICAL_INDICATOR: ProviderCapability.NONE,
                ...
            }
        """
        pass
    
    @abstractmethod
    def get_rate_limits(self) -> Dict[str, Optional[int]]:
        """
        Get current rate limits for this provider.
        
        Returns:
            {
                "per_minute": 60,
                "per_day": 1000,
                "per_month": None  # Unlimited
            }
        """
        pass
    
    # ==================== Helper Methods ====================
    
    def record_success(self, response_time_ms: Optional[float] = None):
        """Record successful API call."""
        self.health.is_healthy = True
        self.health.last_success = datetime.now()
        self.health.consecutive_failures = 0
        self.health.total_calls += 1
        self.health.successful_calls += 1
        
        if response_time_ms:
            # Update rolling average response time
            if self.health.average_response_time_ms is None:
                self.health.average_response_time_ms = response_time_ms
            else:
                # Exponential moving average (alpha = 0.3)
                self.health.average_response_time_ms = (
                    0.7 * self.health.average_response_time_ms +
                    0.3 * response_time_ms
                )
    
    def record_failure(self, error: Exception):
        """Record failed API call."""
        self.health.last_failure = datetime.now()
        self.health.consecutive_failures += 1
        self.health.total_calls += 1
        self.health.failed_calls += 1
        
        # Mark as unhealthy after 3 consecutive failures
        if self.health.consecutive_failures >= 3:
            self.health.is_healthy = False
            
            logger.warning(
                f"Provider {self.name} marked unhealthy",
                extra={
                    "consecutive_failures": self.health.consecutive_failures,
                    "success_rate": self.health.success_rate,
                    "error": str(error)
                }
            )
    
    @property
    def reliability_score(self) -> float:
        """Get reliability score (0.0 to 1.0)."""
        return self.health.reliability_score
    
    @property
    def capabilities(self) -> Dict[DataType, ProviderCapability]:
        """Convenience property for get_capabilities()."""
        return self.get_capabilities()
    
    def __repr__(self) -> str:
        return (
            f"{self.name}(priority={self.priority}, "
            f"tier={self.tier}, "
            f"reliability={self.reliability_score:.2f})"
        )
