# Multi-Provider Architecture - Avoiding Vendor Lock-in

## Overview

Kuberan uses a **provider-agnostic architecture** to avoid dependency on any single API. Multiple data providers are supported with automatic fallback and smart routing.

**Primary Provider:** MASSIVE API (formerly Polygon.io) - 11 free tier reference endpoints  
**Status:** Phase 0 cleanup completed, Phase 1-16 MASSIVE integration starting  
**Last Updated:** December 2, 2025

---

## Current Provider Status

### Active Providers
1. **MASSIVE API** (Primary) - Reference endpoints only (free tier)
   - Ticker discovery and metadata
   - Corporate actions (splits, dividends)
   - Financial news
   - Options contracts metadata
   - Rate limit: 5/min, 300/hour, 7,200/day

2. **YFinance** - Historical prices and real-time quotes (free, unlimited)

3. **Alpha Vantage** - ETF data and analysis (25 calls/day free tier)

### Phase 0 Decisions
- **TickerConfig Model:** RETAINED (active, 27 references) - Will migrate to MASSIVE-driven discovery in Phase 1
- **ticker_config_repository:** RETAINED (used by config_loader.py) - Will replace with MASSIVE provider in Phase 1-2
- **tickers.yaml:** RETAINED (seeding mechanism) - Will remove after MASSIVE ticker discovery in Phase 1

---

## Design Principles

### 1. Provider Abstraction
- **Interface-based design**: Common interface for all providers
- **Pluggable providers**: Easy to add/remove providers
- **No direct provider calls**: All access through abstraction layer
- **Provider-agnostic models**: Data models don't reference specific providers

### 2. Smart Routing
- **Best provider selection**: Choose optimal provider per data type
- **Automatic fallback**: Switch to backup provider on failure
- **Load balancing**: Distribute calls across providers
- **Rate limit awareness**: Track limits per provider

### 3. Data Quality
- **Multi-source validation**: Compare data across providers
- **Conflict resolution**: Handle discrepancies intelligently
- **Provider scoring**: Track reliability and accuracy
- **Automatic provider rotation**: Use best-performing provider

---

## Provider Capabilities Matrix

| Data Type | MASSIVE (Primary) | Alpha Vantage | Finnhub | yfinance | Strategy |
|-----------|-------------------|---------------|---------|----------|----------|
| **Ticker Discovery** | ✅ Comprehensive | ⚠️ Limited | ⚠️ Limited | ❌ None | **Primary: MASSIVE** |
| **Ticker Metadata** | ✅ Excellent | ⚠️ Basic | ⚠️ Basic | ✅ Good | **Primary: MASSIVE, Backup: yfinance** |
| **Real-time Quotes** | ❌ Paid tier | ⚠️ 15-min delay | ✅ Real-time | ✅ Real-time | **Primary: yfinance/Finnhub** |
| **Historical Prices** | ❌ Paid tier | ✅ 20+ years | ✅ Good | ✅ Excellent | **Primary: yfinance, Backup: Alpha Vantage** |
| **Corporate Actions** | ✅ Splits, Dividends | ✅ Historical | ⚠️ Basic | ✅ Excellent | **Primary: MASSIVE, Backup: yfinance** |
| **Financial News** | ✅ With sentiment | ✅ With sentiment | ✅ Excellent | ❌ None | **Primary: MASSIVE, Backup: Finnhub** |
| **Options Metadata** | ✅ Contract specs | ✅ Basic | ❌ None | ✅ Excellent | **Primary: MASSIVE (metadata), yfinance (pricing)** |
| **Technical Indicators** | ❌ Paid tier | ✅ 40+ indicators | ❌ None | ✅ Calculate locally | **Primary: Alpha Vantage, Backup: Local** |
| **Fundamental Data** | ⚠️ Deprecated API | ✅ Excellent | ⚠️ Basic | ✅ Good | **Primary: Alpha Vantage, Backup: yfinance** |
| **ETF Data** | ❌ Limited | ✅ Excellent | ❌ None | ✅ Good | **Primary: Alpha Vantage** |

### Rate Limits Comparison

| Provider | Free Tier Limit | Cost | Kuberan Usage |
|----------|----------------|------|---------------|
| **MASSIVE** | 5/min, 7,200/day | Free | **Primary** - Metadata enrichment |
| **Alpha Vantage** | 5/min, 25/day | Free | **Secondary** - ETF data only |
| **Finnhub** | 60/min | Free | **Tertiary** - News fallback |
| **yfinance** | Unlimited* | Free | **Primary** - Price data |

*Unofficial API, rate limits unknown

---

## Architecture Design

### Provider Interface

```python
# backend/app/services/providers/base_provider.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class DataType(Enum):
    """Types of financial data."""
    REAL_TIME_QUOTE = "real_time_quote"
    HISTORICAL_PRICES = "historical_prices"
    TECHNICAL_INDICATORS = "technical_indicators"
    FUNDAMENTAL_DATA = "fundamental_data"
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    DIVIDENDS = "dividends"
    SPLITS = "splits"
    NEWS = "news"
    EARNINGS = "earnings"
    ANALYST_RATINGS = "analyst_ratings"
    OPTIONS = "options"
    FOREX = "forex"
    CRYPTO = "crypto"
    ECONOMIC_DATA = "economic_data"
    COMMODITIES = "commodities"

class ProviderCapability(Enum):
    """Provider capability levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    BASIC = "basic"
    NONE = "none"

class BaseProvider(ABC):
    """Abstract base class for all data providers."""
    
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.rate_limiter = None
        self.capabilities: Dict[DataType, ProviderCapability] = {}
        self.priority: int = 0  # Lower = higher priority
        self.reliability_score: float = 1.0  # 0.0 to 1.0
        self.last_failure: Optional[datetime] = None
        self.consecutive_failures: int = 0
    
    @abstractmethod
    def supports(self, data_type: DataType) -> bool:
        """Check if provider supports this data type."""
        pass
    
    @abstractmethod
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """Get real-time stock quote."""
        pass
    
    @abstractmethod
    async def get_historical_prices(self, ticker: str, start_date: datetime, 
                                   end_date: datetime, interval: str) -> Optional[Dict]:
        """Get historical price data."""
        pass
    
    @abstractmethod
    async def get_income_statement(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get income statement."""
        pass
    
    @abstractmethod
    async def get_balance_sheet(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get balance sheet."""
        pass
    
    @abstractmethod
    async def get_cash_flow(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get cash flow statement."""
        pass
    
    @abstractmethod
    async def get_dividends(self, ticker: str) -> Optional[Dict]:
        """Get dividend history."""
        pass
    
    @abstractmethod
    async def get_splits(self, ticker: str) -> Optional[Dict]:
        """Get stock split history."""
        pass
    
    @abstractmethod
    async def get_news(self, ticker: str, limit: int = 10) -> Optional[List[Dict]]:
        """Get news articles."""
        pass
    
    @abstractmethod
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """Get earnings data."""
        pass
    
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        try:
            # Attempt a lightweight test call
            return True
        except Exception:
            return False
    
    def record_success(self):
        """Record successful API call."""
        self.consecutive_failures = 0
        # Gradually improve reliability score
        self.reliability_score = min(1.0, self.reliability_score + 0.01)
    
    def record_failure(self):
        """Record failed API call."""
        self.last_failure = datetime.now()
        self.consecutive_failures += 1
        # Degrade reliability score
        self.reliability_score = max(0.0, self.reliability_score - 0.05)
```

### Provider Implementations

#### 1. Alpha Vantage Provider

```python
# backend/app/services/providers/alphavantage_provider.py

from .base_provider import BaseProvider, DataType, ProviderCapability
from typing import Dict, List, Optional
from datetime import datetime

class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage data provider."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.priority = 2  # Medium priority
        
        # Define capabilities
        self.capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.BASIC,  # 15-min delay
            DataType.HISTORICAL_PRICES: ProviderCapability.EXCELLENT,
            DataType.TECHNICAL_INDICATORS: ProviderCapability.EXCELLENT,
            DataType.FUNDAMENTAL_DATA: ProviderCapability.EXCELLENT,
            DataType.INCOME_STATEMENT: ProviderCapability.EXCELLENT,
            DataType.BALANCE_SHEET: ProviderCapability.EXCELLENT,
            DataType.CASH_FLOW: ProviderCapability.EXCELLENT,
            DataType.DIVIDENDS: ProviderCapability.EXCELLENT,
            DataType.SPLITS: ProviderCapability.EXCELLENT,
            DataType.NEWS: ProviderCapability.EXCELLENT,
            DataType.EARNINGS: ProviderCapability.GOOD,
            DataType.FOREX: ProviderCapability.EXCELLENT,
            DataType.CRYPTO: ProviderCapability.GOOD,
            DataType.ECONOMIC_DATA: ProviderCapability.EXCELLENT,
            DataType.COMMODITIES: ProviderCapability.EXCELLENT,
        }
        
        # Rate limiter: 5/min, 25/day
        from app.services.stock.alphavantage_service import AlphaVantageRateLimiter
        self.rate_limiter = AlphaVantageRateLimiter()
    
    def supports(self, data_type: DataType) -> bool:
        """Check support for data type."""
        capability = self.capabilities.get(data_type, ProviderCapability.NONE)
        return capability != ProviderCapability.NONE
    
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """Get real-time quote (15-min delayed)."""
        try:
            await self.rate_limiter.acquire()
            result = await mcp_alphavantage_GLOBAL_QUOTE(symbol=ticker)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.error(f"Alpha Vantage quote failed: {e}")
            return None
    
    async def get_historical_prices(self, ticker: str, start_date: datetime, 
                                   end_date: datetime, interval: str = "daily") -> Optional[Dict]:
        """Get historical prices."""
        try:
            await self.rate_limiter.acquire()
            
            if interval == "daily":
                result = await mcp_alphavantage_TIME_SERIES_DAILY_ADJUSTED(
                    symbol=ticker, outputsize="full"
                )
            elif interval == "weekly":
                result = await mcp_alphavantage_TIME_SERIES_WEEKLY_ADJUSTED(symbol=ticker)
            elif interval == "monthly":
                result = await mcp_alphavantage_TIME_SERIES_MONTHLY_ADJUSTED(symbol=ticker)
            else:
                result = await mcp_alphavantage_TIME_SERIES_INTRADAY(
                    symbol=ticker, interval=interval, outputsize="full"
                )
            
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.error(f"Alpha Vantage historical prices failed: {e}")
            return None
    
    async def get_income_statement(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get income statement."""
        try:
            await self.rate_limiter.acquire()
            # Use MCP tool (need to verify exact function name)
            result = await mcp_alphavantage_INCOME_STATEMENT(symbol=ticker)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.error(f"Alpha Vantage income statement failed: {e}")
            return None
    
    # ... implement all other methods
```

#### 2. Finnhub Provider

```python
# backend/app/services/providers/finnhub_provider.py

class FinnhubProvider(BaseProvider):
    """Finnhub data provider."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.priority = 1  # High priority for real-time data
        
        self.capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.EXCELLENT,
            DataType.HISTORICAL_PRICES: ProviderCapability.GOOD,
            DataType.NEWS: ProviderCapability.EXCELLENT,
            DataType.EARNINGS: ProviderCapability.EXCELLENT,
            DataType.ANALYST_RATINGS: ProviderCapability.EXCELLENT,
            DataType.CRYPTO: ProviderCapability.GOOD,
            DataType.FOREX: ProviderCapability.GOOD,
        }
        
        # Rate limiter: 60/min
        from app.services.stock.finnhub_service import FinnhubRateLimiter
        self.rate_limiter = FinnhubRateLimiter()
    
    def supports(self, data_type: DataType) -> bool:
        capability = self.capabilities.get(data_type, ProviderCapability.NONE)
        return capability != ProviderCapability.NONE
    
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """Get real-time quote."""
        try:
            await self.rate_limiter.acquire()
            # Use existing Finnhub integration
            result = await finnhub_client.get_quote(ticker)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.error(f"Finnhub quote failed: {e}")
            return None
    
    # ... implement other methods
```

#### 3. yfinance Provider

```python
# backend/app/services/providers/yfinance_provider.py

class YFinanceProvider(BaseProvider):
    """Yahoo Finance (yfinance) data provider."""
    
    def __init__(self):
        super().__init__()
        self.priority = 1  # High priority - free and reliable
        
        self.capabilities = {
            DataType.REAL_TIME_QUOTE: ProviderCapability.EXCELLENT,
            DataType.HISTORICAL_PRICES: ProviderCapability.EXCELLENT,
            DataType.FUNDAMENTAL_DATA: ProviderCapability.GOOD,
            DataType.INCOME_STATEMENT: ProviderCapability.GOOD,
            DataType.BALANCE_SHEET: ProviderCapability.GOOD,
            DataType.CASH_FLOW: ProviderCapability.GOOD,
            DataType.DIVIDENDS: ProviderCapability.EXCELLENT,
            DataType.SPLITS: ProviderCapability.EXCELLENT,
            DataType.EARNINGS: ProviderCapability.GOOD,
            DataType.OPTIONS: ProviderCapability.EXCELLENT,
            DataType.FOREX: ProviderCapability.BASIC,
            DataType.CRYPTO: ProviderCapability.BASIC,
        }
        
        # No official rate limiter (unofficial API)
        # Implement conservative rate limiting
        self.rate_limiter = SimpleRateLimiter(max_per_minute=30)
    
    def supports(self, data_type: DataType) -> bool:
        capability = self.capabilities.get(data_type, ProviderCapability.NONE)
        return capability != ProviderCapability.NONE
    
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """Get real-time quote using yfinance."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            self.record_success()
            return {
                "symbol": ticker,
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "timestamp": datetime.now()
            }
        except Exception as e:
            self.record_failure()
            logger.error(f"yfinance quote failed: {e}")
            return None
    
    async def get_historical_prices(self, ticker: str, start_date: datetime, 
                                   end_date: datetime, interval: str = "1d") -> Optional[Dict]:
        """Get historical prices."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, interval=interval)
            
            self.record_success()
            return hist.to_dict('index')
        except Exception as e:
            self.record_failure()
            logger.error(f"yfinance historical prices failed: {e}")
            return None
    
    async def get_income_statement(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get income statement."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            if period == "annual":
                financials = stock.financials
            else:
                financials = stock.quarterly_financials
            
            self.record_success()
            return financials.to_dict('index')
        except Exception as e:
            self.record_failure()
            logger.error(f"yfinance income statement failed: {e}")
            return None
    
    # ... implement other methods
```

### Provider Manager (Orchestration Layer)

```python
# backend/app/services/providers/provider_manager.py

from typing import Dict, List, Optional
from .base_provider import BaseProvider, DataType
from .alphavantage_provider import AlphaVantageProvider
from .finnhub_provider import FinnhubProvider
from .yfinance_provider import YFinanceProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ProviderManager:
    """
    Manages multiple data providers with automatic fallback and smart routing.
    
    Features:
    - Provider abstraction: Hide provider-specific details
    - Smart routing: Choose best provider per data type
    - Automatic fallback: Try backup providers on failure
    - Load balancing: Distribute calls across providers
    - Provider health tracking: Monitor reliability and performance
    """
    
    def __init__(self):
        self.providers: List[BaseProvider] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        import os
        
        # Alpha Vantage (if API key available)
        av_key = os.getenv("ALPHA_VANTAGE_KEY")
        if av_key:
            self.providers.append(AlphaVantageProvider(av_key))
            logger.info("Alpha Vantage provider initialized")
        
        # Finnhub (if API key available)
        fh_key = os.getenv("FINNHUB_KEY")
        if fh_key:
            self.providers.append(FinnhubProvider(fh_key))
            logger.info("Finnhub provider initialized")
        
        # yfinance (always available, free)
        self.providers.append(YFinanceProvider())
        logger.info("yfinance provider initialized")
        
        # Sort by priority (lower = higher priority)
        self.providers.sort(key=lambda p: p.priority)
        
        logger.info(f"Provider manager initialized with {len(self.providers)} providers")
    
    def get_providers_for_data_type(self, data_type: DataType) -> List[BaseProvider]:
        """
        Get all providers that support a data type, ordered by priority and reliability.
        
        Args:
            data_type: Type of data needed
            
        Returns:
            List of providers, best first
        """
        providers = [p for p in self.providers if p.supports(data_type)]
        
        # Sort by: priority (lower first), then reliability (higher first)
        providers.sort(key=lambda p: (p.priority, -p.reliability_score))
        
        return providers
    
    async def get_real_time_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get real-time quote with automatic fallback.
        
        Strategy:
        1. Try Finnhub (real-time, high priority)
        2. Try yfinance (real-time, backup)
        3. Try Alpha Vantage (15-min delayed, last resort)
        """
        providers = self.get_providers_for_data_type(DataType.REAL_TIME_QUOTE)
        
        for provider in providers:
            logger.debug(f"Attempting quote for {ticker} from {provider.name}")
            
            result = await provider.get_real_time_quote(ticker)
            
            if result:
                logger.info(
                    f"Quote for {ticker} retrieved successfully",
                    extra={
                        "provider": provider.name,
                        "ticker": ticker,
                        "price": result.get("price")
                    }
                )
                return result
        
        logger.error(f"All providers failed for quote: {ticker}")
        return None
    
    async def get_historical_prices(self, ticker: str, start_date, end_date, 
                                   interval: str = "daily") -> Optional[Dict]:
        """
        Get historical prices with automatic fallback.
        
        Strategy:
        1. Try yfinance (excellent historical data, free)
        2. Try Alpha Vantage (20+ years history, 25/day limit)
        3. Try Finnhub (backup)
        """
        providers = self.get_providers_for_data_type(DataType.HISTORICAL_PRICES)
        
        for provider in providers:
            logger.debug(f"Attempting historical prices for {ticker} from {provider.name}")
            
            result = await provider.get_historical_prices(ticker, start_date, end_date, interval)
            
            if result:
                logger.info(
                    f"Historical prices for {ticker} retrieved successfully",
                    extra={
                        "provider": provider.name,
                        "ticker": ticker,
                        "interval": interval
                    }
                )
                return result
        
        logger.error(f"All providers failed for historical prices: {ticker}")
        return None
    
    async def get_income_statement(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """
        Get income statement with automatic fallback.
        
        Strategy:
        1. Try Alpha Vantage (excellent fundamental data)
        2. Try yfinance (good fundamental data, free)
        3. Try other providers
        """
        providers = self.get_providers_for_data_type(DataType.INCOME_STATEMENT)
        
        for provider in providers:
            logger.debug(f"Attempting income statement for {ticker} from {provider.name}")
            
            result = await provider.get_income_statement(ticker, period)
            
            if result:
                logger.info(
                    f"Income statement for {ticker} retrieved successfully",
                    extra={
                        "provider": provider.name,
                        "ticker": ticker,
                        "period": period
                    }
                )
                return result
        
        logger.error(f"All providers failed for income statement: {ticker}")
        return None
    
    async def get_balance_sheet(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get balance sheet with automatic fallback."""
        providers = self.get_providers_for_data_type(DataType.BALANCE_SHEET)
        
        for provider in providers:
            result = await provider.get_balance_sheet(ticker, period)
            if result:
                logger.info(f"Balance sheet for {ticker} from {provider.name}")
                return result
        
        logger.error(f"All providers failed for balance sheet: {ticker}")
        return None
    
    async def get_cash_flow(self, ticker: str, period: str = "annual") -> Optional[Dict]:
        """Get cash flow with automatic fallback."""
        providers = self.get_providers_for_data_type(DataType.CASH_FLOW)
        
        for provider in providers:
            result = await provider.get_cash_flow(ticker, period)
            if result:
                logger.info(f"Cash flow for {ticker} from {provider.name}")
                return result
        
        logger.error(f"All providers failed for cash flow: {ticker}")
        return None
    
    async def get_dividends(self, ticker: str) -> Optional[Dict]:
        """
        Get dividend history with automatic fallback.
        
        Strategy:
        1. Try yfinance (excellent dividend data)
        2. Try Alpha Vantage (backup)
        """
        providers = self.get_providers_for_data_type(DataType.DIVIDENDS)
        
        for provider in providers:
            result = await provider.get_dividends(ticker)
            if result:
                logger.info(f"Dividends for {ticker} from {provider.name}")
                return result
        
        logger.error(f"All providers failed for dividends: {ticker}")
        return None
    
    async def get_splits(self, ticker: str) -> Optional[Dict]:
        """
        Get stock splits with automatic fallback.
        
        Strategy:
        1. Try yfinance (excellent splits data)
        2. Try Alpha Vantage (backup)
        """
        providers = self.get_providers_for_data_type(DataType.SPLITS)
        
        for provider in providers:
            result = await provider.get_splits(ticker)
            if result:
                logger.info(f"Splits for {ticker} from {provider.name}")
                return result
        
        logger.error(f"All providers failed for splits: {ticker}")
        return None
    
    async def get_news(self, ticker: str, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get news with automatic fallback.
        
        Strategy:
        1. Try Finnhub (excellent news)
        2. Try Alpha Vantage (news with sentiment)
        """
        providers = self.get_providers_for_data_type(DataType.NEWS)
        
        for provider in providers:
            result = await provider.get_news(ticker, limit)
            if result:
                logger.info(f"News for {ticker} from {provider.name}")
                return result
        
        logger.error(f"All providers failed for news: {ticker}")
        return None
    
    async def get_earnings(self, ticker: str) -> Optional[Dict]:
        """
        Get earnings with multi-source merge.
        
        Strategy: Merge data from multiple providers for completeness
        """
        providers = self.get_providers_for_data_type(DataType.EARNINGS)
        
        results = []
        for provider in providers:
            result = await provider.get_earnings(ticker)
            if result:
                results.append({
                    "provider": provider.name,
                    "data": result
                })
        
        if results:
            # Merge earnings data from multiple sources
            merged = self._merge_earnings_data(results)
            logger.info(f"Earnings for {ticker} merged from {len(results)} providers")
            return merged
        
        logger.error(f"All providers failed for earnings: {ticker}")
        return None
    
    def _merge_earnings_data(self, results: List[Dict]) -> Dict:
        """
        Merge earnings data from multiple providers.
        
        Strategy:
        - Combine historical EPS from all sources
        - Take most recent analyst estimates
        - Prefer higher quality data (Finnhub > Alpha Vantage)
        """
        merged = {
            "historical": [],
            "estimates": [],
            "sources": [r["provider"] for r in results]
        }
        
        # Merge historical earnings
        for result in results:
            data = result["data"]
            if "historical" in data:
                merged["historical"].extend(data["historical"])
        
        # Deduplicate by date, keep most recent
        merged["historical"] = list({
            item["date"]: item for item in merged["historical"]
        }.values())
        
        # Sort by date
        merged["historical"].sort(key=lambda x: x["date"], reverse=True)
        
        # Take estimates from highest priority provider
        for result in results:
            data = result["data"]
            if "estimates" in data and data["estimates"]:
                merged["estimates"] = data["estimates"]
                break
        
        return merged
    
    async def health_check_all_providers(self) -> Dict[str, bool]:
        """Check health of all providers."""
        results = {}
        
        for provider in self.providers:
            is_healthy = await provider.health_check()
            results[provider.name] = is_healthy
            
            logger.info(
                f"Provider health check",
                extra={
                    "provider": provider.name,
                    "healthy": is_healthy,
                    "reliability_score": provider.reliability_score,
                    "consecutive_failures": provider.consecutive_failures
                }
            )
        
        return results
    
    def get_provider_stats(self) -> List[Dict]:
        """Get statistics for all providers."""
        stats = []
        
        for provider in self.providers:
            stats.append({
                "name": provider.name,
                "priority": provider.priority,
                "reliability_score": provider.reliability_score,
                "consecutive_failures": provider.consecutive_failures,
                "last_failure": provider.last_failure.isoformat() if provider.last_failure else None,
                "capabilities": len([c for c in provider.capabilities.values() 
                                    if c != ProviderCapability.NONE])
            })
        
        return stats

# Singleton instance
provider_manager = ProviderManager()
```

---

## Service Layer Integration

### Updated Service (Provider-Agnostic)

```python
# backend/app/services/stock/stock_data_service.py

from app.services.providers.provider_manager import provider_manager
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class StockDataService:
    """
    Provider-agnostic stock data service.
    
    All data access goes through provider manager for automatic fallback.
    """
    
    def __init__(self):
        self.provider_manager = provider_manager
    
    async def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current stock price from best available provider."""
        quote = await self.provider_manager.get_real_time_quote(ticker)
        
        if quote:
            return quote.get("price")
        
        return None
    
    async def get_price_history(self, ticker: str, start_date, end_date, 
                               interval: str = "daily") -> Optional[List[Dict]]:
        """Get historical prices from best available provider."""
        data = await self.provider_manager.get_historical_prices(
            ticker, start_date, end_date, interval
        )
        
        if data:
            # Parse and normalize data structure
            return self._normalize_price_history(data)
        
        return None
    
    async def get_financial_statements(self, ticker: str, 
                                      period: str = "annual") -> Optional[Dict]:
        """
        Get all financial statements from best available providers.
        
        Returns consolidated financial data from multiple sources.
        """
        # Fetch from multiple providers in parallel
        income_task = self.provider_manager.get_income_statement(ticker, period)
        balance_task = self.provider_manager.get_balance_sheet(ticker, period)
        cash_flow_task = self.provider_manager.get_cash_flow(ticker, period)
        
        income, balance, cash_flow = await asyncio.gather(
            income_task, balance_task, cash_flow_task,
            return_exceptions=True
        )
        
        return {
            "income_statement": income if not isinstance(income, Exception) else None,
            "balance_sheet": balance if not isinstance(balance, Exception) else None,
            "cash_flow": cash_flow if not isinstance(cash_flow, Exception) else None,
            "period": period
        }
    
    async def get_corporate_actions(self, ticker: str) -> Optional[Dict]:
        """Get dividends and splits from best available providers."""
        dividends_task = self.provider_manager.get_dividends(ticker)
        splits_task = self.provider_manager.get_splits(ticker)
        
        dividends, splits = await asyncio.gather(
            dividends_task, splits_task,
            return_exceptions=True
        )
        
        return {
            "dividends": dividends if not isinstance(dividends, Exception) else [],
            "splits": splits if not isinstance(splits, Exception) else []
        }
    
    async def get_company_news(self, ticker: str, limit: int = 10) -> Optional[List[Dict]]:
        """Get news from best available provider."""
        news = await self.provider_manager.get_news(ticker, limit)
        return news if news else []
    
    async def get_earnings_data(self, ticker: str) -> Optional[Dict]:
        """Get earnings data (merged from multiple providers)."""
        return await self.provider_manager.get_earnings(ticker)
    
    def _normalize_price_history(self, data: Dict) -> List[Dict]:
        """Normalize price history to common format."""
        # Handle different provider formats
        # Convert to consistent structure
        normalized = []
        
        # Implementation depends on provider formats
        # This ensures consistent output regardless of provider
        
        return normalized

# Singleton instance
stock_data_service = StockDataService()
```

---

## Router Layer (No Changes Needed!)

```python
# backend/app/routers/stocks.py

from app.services.stock.stock_data_service import stock_data_service

@router.get("/stocks/{ticker}/quote")
async def get_quote(ticker: str):
    """
    Get current stock quote.
    
    Automatically uses best available provider (Finnhub > yfinance > Alpha Vantage).
    """
    price = await stock_data_service.get_current_price(ticker)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Quote not available")
    
    return {"ticker": ticker, "price": price}

@router.get("/stocks/{ticker}/history")
async def get_history(ticker: str, start_date: str, end_date: str, 
                     interval: str = Query("daily")):
    """
    Get historical prices.
    
    Automatically uses best available provider (yfinance > Alpha Vantage > Finnhub).
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    history = await stock_data_service.get_price_history(ticker, start, end, interval)
    
    if history is None:
        raise HTTPException(status_code=404, detail="Historical data not available")
    
    return {"ticker": ticker, "data": history}

@router.get("/stocks/{ticker}/financials")
async def get_financials(ticker: str, period: str = Query("annual")):
    """
    Get financial statements.
    
    Automatically uses best available providers for each statement type.
    """
    financials = await stock_data_service.get_financial_statements(ticker, period)
    
    if not any([financials["income_statement"], financials["balance_sheet"], 
               financials["cash_flow"]]):
        raise HTTPException(status_code=404, detail="Financial statements not available")
    
    return financials

@router.get("/stocks/{ticker}/news")
async def get_news(ticker: str, limit: int = Query(10, le=50)):
    """
    Get company news.
    
    Automatically uses best available provider (Finnhub > Alpha Vantage).
    """
    news = await stock_data_service.get_company_news(ticker, limit)
    
    return {"ticker": ticker, "articles": news}
```

---

## Benefits of This Architecture

### 1. **No Vendor Lock-in**
- Easy to add new providers (implement BaseProvider interface)
- Easy to remove providers (just disable in config)
- Can switch providers without code changes

### 2. **Automatic Failover**
- If primary provider fails, automatically tries backup
- No downtime due to single provider issues
- Graceful degradation

### 3. **Smart Provider Selection**
- Uses best provider for each data type
- Routes real-time quotes to Finnhub (best)
- Routes historical data to yfinance (excellent + free)
- Routes technical indicators to Alpha Vantage (only option)

### 4. **Rate Limit Optimization**
- Distributes calls across multiple providers
- Preserves Alpha Vantage quota for unique data (indicators, fundamentals)
- Uses yfinance for bulk historical data (unlimited)
- Uses Finnhub for real-time updates (60/min vs Alpha Vantage's 5/min)

### 5. **Cost Optimization**
- Maximizes free tier usage across providers
- Only pays for premium when needed
- Can compare costs and switch providers easily

### 6. **Data Quality**
- Multi-source validation (compare data across providers)
- Merge earnings data from multiple sources
- Track provider reliability scores

### 7. **Monitoring & Observability**
- Provider health checks
- Reliability scoring
- Failure tracking
- Provider performance statistics

---

## Configuration

### Environment Variables

```bash
# .env

# Alpha Vantage (Technical Indicators, Fundamentals)
ALPHA_VANTAGE_KEY=your_key_here
ALPHA_VANTAGE_ENABLED=true

# Finnhub (Real-time Data, News, Analyst Ratings)
FINNHUB_KEY=your_key_here
FINNHUB_ENABLED=true

# yfinance (always enabled, no key needed)
# YFINANCE_ENABLED=true  # Default: true

# Polygon.io (Optional - Premium alternative)
# POLYGON_KEY=your_key_here
# POLYGON_ENABLED=false

# IEX Cloud (Optional - Alternative provider)
# IEX_KEY=your_key_here
# IEX_ENABLED=false
```

### Provider Priority Configuration

```python
# backend/app/core/config.py

PROVIDER_PRIORITIES = {
    "real_time_quotes": ["Finnhub", "YFinance", "AlphaVantage"],
    "historical_prices": ["YFinance", "AlphaVantage", "Finnhub"],
    "technical_indicators": ["AlphaVantage"],  # Only provider with 40+ indicators
    "fundamental_data": ["AlphaVantage", "YFinance"],
    "news": ["Finnhub", "AlphaVantage"],
    "earnings": ["Finnhub", "AlphaVantage", "YFinance"],  # Multi-source merge
}
```

---

## Migration Path

### Phase 1: Setup Provider Infrastructure (Week 1)
1. Create `BaseProvider` abstract class
2. Implement `AlphaVantageProvider` (wrap existing code)
3. Implement `FinnhubProvider` (wrap existing code)
4. Implement `YFinanceProvider` (new)
5. Create `ProviderManager`

### Phase 2: Migrate Stock Data Service (Week 2)
1. Create `StockDataService` using provider manager
2. Update routers to use new service
3. Test with all three providers
4. Verify fallback behavior

### Phase 3: Add Multi-Source Features (Week 3)
1. Implement earnings data merging
2. Add provider health checks
3. Add reliability scoring
4. Add provider statistics endpoint

### Phase 4: Testing & Monitoring

**Status**: ✅ **COMPLETE** (November 16, 2025)

#### 4.1 API Metrics Tracking Infrastructure ✅

**Completed**: November 16, 2025

**Components**:
- ✅ **4 monitoring models** (`backend/app/models/monitoring.py` - 192 lines)
  - `ProviderAPICall`: Individual call tracking (timeseries, 30-day TTL)
  - `ProviderDailyStats`: Aggregated daily statistics (permanent)
  - `ProviderHealthCheck`: Provider health monitoring (timeseries, 7-day TTL)
  - `RateLimitStatus`: Real-time rate limit tracking (timeseries, 1-hour TTL)

- ✅ **Metrics tracking utilities** (`backend/app/core/api_metrics.py` - 381 lines)
  - `APIMetricsTracker` class with automatic tracking
  - `@api_metrics.track_api_call` decorator for zero-boilerplate monitoring
  - Daily statistics aggregation
  - Rate limit status management
  - Fail-safe design (metrics don't break API calls)

- ✅ **6 REST API endpoints** (`backend/app/routers/monitoring.py` - 540 lines)
  - `GET /monitoring/providers/summary` - All providers today's stats
  - `GET /monitoring/providers/{provider}/stats` - Daily statistics with time range
  - `GET /monitoring/providers/{provider}/recent-calls` - Recent API calls with filters
  - `GET /monitoring/providers/{provider}/performance` - Performance metrics (p50, p95)
  - `GET /monitoring/calls/all` - Cross-provider recent calls
  - `GET /monitoring/stats/aggregate` - Aggregated statistics across providers

- ✅ **TTL configuration** (15 timeseries collections total)
  - 12 data collections (Phase 3)
  - 3 monitoring collections (Phase 4)
  - All created via `backend/app/scripts/configure_timeseries_ttl.py`
  - Automatic expiration prevents unbounded storage growth

- ✅ **Provider decorator integration** (All 3 providers)
  - **YFinanceProvider**: 6 methods decorated (quote, historical, news, dividends, splits, earnings)
  - **AlphaVantageProvider**: 8 methods decorated (quote, historical, technical_indicator, fundamental_data, news, dividends, splits, earnings)
  - **FinnhubProvider**: 6 methods decorated (quote, historical, news, earnings, analyst_ratings, price_targets)
  - Total: 20 data-fetching methods tracking metrics automatically

- ✅ **Documentation** (3 comprehensive guides)
  - [API_METRICS_TRACKING.md](API_METRICS_TRACKING.md) - System architecture and design
  - [METRICS_INTEGRATION_GUIDE.md](METRICS_INTEGRATION_GUIDE.md) - Integration patterns
  - [QUERYING_API_METRICS.md](QUERYING_API_METRICS.md) - REST API and MongoDB queries

- ✅ **Postman collection updated** with 6 monitoring endpoints

**Features**:
- Automatic call tracking (response time, status, errors, ticker)
- Success/failure/timeout/rate_limited detection
- Daily aggregation for long-term analysis
- MongoDB timeseries optimization
- Non-invasive decorator pattern
- REST API for querying metrics
- Ready for frontend dashboards

**Usage Example**:
```python
# Decorator automatically tracks all API calls
@api_metrics.track_api_call(provider="yfinance", data_type="quote")
async def fetch_real_time_quote(self, ticker: str):
    # Method implementation unchanged
    # Tracking happens automatically
```

**Query Example**:
```bash
# Get today's summary for all providers
curl http://localhost:8000/monitoring/providers/summary

# Get last 7 days of yfinance statistics
curl http://localhost:8000/monitoring/providers/yfinance/stats?days=7

# Get recent calls with filters
curl http://localhost:8000/monitoring/providers/yfinance/recent-calls?limit=50&status=success
```

**Benefits**:
- 💰 **Cost monitoring**: Track API usage against free tier limits
- ⚡ **Performance tracking**: Measure response times per provider (p50, p95, p99)
- 🔍 **Debugging**: Full audit trail with error messages
- 📊 **Analytics**: Usage patterns, popular data types
- 🎯 **Optimization**: Identify slow/unreliable providers
- 🚀 **Production-ready**: Metrics tracked automatically when providers are used

#### 4.2 Unit & Integration Testing ⏳

**Tasks**:
1. Unit tests for each provider implementation
2. Integration tests for provider fallback
3. Load testing with simulated provider failures
4. Metrics tracking verification tests

#### 4.3 Monitoring Dashboard ⏳

**Tasks**:
1. Real-time provider status UI
2. API call statistics charts
3. Cost estimation reports
4. Alert configuration (email/SMS)

---

## API Monitoring Endpoint

```python
# backend/app/routers/system.py

@router.get("/system/providers")
async def get_provider_status():
    """Get status and statistics for all data providers."""
    health = await provider_manager.health_check_all_providers()
    stats = provider_manager.get_provider_stats()
    
    return {
        "providers": stats,
        "health": health,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/system/providers/{provider_name}/test")
async def test_provider(provider_name: str):
    """Test specific provider with sample data."""
    # Implementation for testing individual providers
    pass
```

---

## Summary

This **multi-provider architecture** ensures Kuberan:

✅ **Never relies on a single API**
✅ **Automatically falls back** to backup providers
✅ **Optimizes costs** by using free tiers strategically
✅ **Maximizes data quality** through multi-source validation
✅ **Scales easily** by adding new providers
✅ **Monitors provider health** automatically
✅ **Routes intelligently** to best provider per data type

**No vendor lock-in. Maximum resilience. Optimal performance.**
