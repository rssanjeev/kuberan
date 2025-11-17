"""
Provider Data Models.

Beanie ODM models for storing data fetched from multi-provider system.
All models include source_provider field to track data origin.

Models organized by category:
1. Stock Models: Quotes, historical prices, dividends, splits, earnings
2. Technical Indicators: Flexible schema for 50+ indicators
3. Fundamental Data: Company overview, financials
4. News & Analyst: News articles, ratings, price targets
5. Forex/Crypto/Commodity: Exchange rates and prices
6. Economic Indicators: GDP, CPI, unemployment, etc.
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class DataSource(str, Enum):
    """Data source providers."""
    ALPHA_VANTAGE = "alpha_vantage"
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"
    POLYGON = "polygon"
    IEX = "iex"
    MANUAL = "manual"


class IndicatorType(str, Enum):
    """Technical indicator types."""
    MOVING_AVERAGE = "moving_average"
    OSCILLATOR = "oscillator"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    TREND = "trend"
    MOMENTUM = "momentum"
    OTHER = "other"


# ==================== Stock Models ====================

class StockQuote(Document):
    """
    Real-time or delayed stock quote data.
    
    TTL: 15 minutes (quotes expire quickly)
    Source providers: Alpha Vantage, Finnhub, yfinance
    """
    # Stock identification
    ticker: str  # Stock ticker symbol
    
    # Price data
    price: float  # Current price
    open: Optional[float] = None  # Opening price
    high: Optional[float] = None  # Day high
    low: Optional[float] = None  # Day low
    previous_close: Optional[float] = None  # Previous close
    
    # Volume and change
    volume: Optional[int] = None  # Trading volume
    change: Optional[float] = None  # Price change
    change_percent: Optional[float] = None  # Percentage change
    
    # Metadata
    source_provider: DataSource  # Which provider fetched this
    quote_timestamp: datetime  # When quote was generated
    fetched_at: datetime = Field(default_factory=datetime.utcnow)  # When we fetched it
    is_delayed: bool = False  # True if 15min delayed (e.g., yfinance)
    delay_minutes: Optional[int] = None  # Delay in minutes (0, 15, etc.)
    
    # Extended data (optional)
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    
    class Settings:
        name = "stock_quotes"
        indexes = [
            "ticker",
            "quote_timestamp",
            [("ticker", 1), ("quote_timestamp", -1)],  # Recent quotes for ticker
            "source_provider",
            "fetched_at",
        ]
        # TTL: Expire quotes after 15 minutes
        timeseries_options = {
            "timeField": "quote_timestamp",
            "granularity": "minutes",
            "expireAfterSeconds": 900  # 15 minutes
        }


class StockHistoricalPrice(Document):
    """
    Historical OHLCV (Open, High, Low, Close, Volume) data.
    
    TTL: Keep for 5 years
    Source providers: Alpha Vantage, yfinance, Finnhub
    """
    # Stock identification
    ticker: str
    
    # Date identification
    date: str  # YYYY-MM-DD format
    timestamp: datetime  # Full datetime
    
    # OHLCV data
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Adjusted prices (for splits/dividends)
    adjusted_close: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    interval: str = "1d"  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "stock_historical_prices"
        indexes = [
            "ticker",
            "date",
            [("ticker", 1), ("date", -1)],  # Recent first for ticker
            [("ticker", 1), ("interval", 1), ("date", -1)],  # Interval-specific queries
            "timestamp",
            "source_provider",
        ]
        # TTL: Keep historical data for 5 years
        timeseries_options = {
            "timeField": "timestamp",
            "granularity": "hours",
            "expireAfterSeconds": 157680000  # 5 years
        }


class StockDividend(Document):
    """
    Dividend payment history.
    
    TTL: Keep forever (historical record)
    Source providers: yfinance (EXCELLENT), Alpha Vantage (BASIC)
    """
    # Stock identification
    ticker: str
    
    # Dividend details
    ex_date: str  # Ex-dividend date (YYYY-MM-DD)
    payment_date: Optional[str] = None  # Payment date (YYYY-MM-DD)
    record_date: Optional[str] = None  # Record date
    declaration_date: Optional[str] = None  # Declaration date
    
    # Amount
    amount: float  # Dividend amount per share
    currency: str = "USD"
    
    # Dividend type
    dividend_type: Optional[str] = None  # "regular", "special", "qualified"
    frequency: Optional[str] = None  # "quarterly", "annual", "monthly"
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "stock_dividends"
        indexes = [
            "ticker",
            "ex_date",
            [("ticker", 1), ("ex_date", -1)],  # Dividend history for ticker
            "source_provider",
        ]


class StockSplit(Document):
    """
    Stock split history.
    
    TTL: Keep forever (historical record)
    Source providers: yfinance (EXCELLENT), Alpha Vantage (BASIC)
    """
    # Stock identification
    ticker: str
    
    # Split details
    split_date: str  # Date of split (YYYY-MM-DD)
    split_ratio: float  # Split ratio (2.0 = 2-for-1, 0.5 = 1-for-2)
    split_from: Optional[int] = None  # e.g., 1 in "1-for-2"
    split_to: Optional[int] = None  # e.g., 2 in "1-for-2"
    
    # Description
    description: str  # Human-readable (e.g., "2-for-1 split")
    is_reverse_split: bool = False  # True if reverse split
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "stock_splits"
        indexes = [
            "ticker",
            "split_date",
            [("ticker", 1), ("split_date", -1)],  # Split history for ticker
            "source_provider",
        ]


class StockEarnings(Document):
    """
    Earnings data and calendar events.
    
    TTL: Keep for 2 years
    Source providers: Alpha Vantage (EXCELLENT), Finnhub (EXCELLENT), yfinance (BASIC)
    """
    # Stock identification
    ticker: str
    
    # Earnings period
    fiscal_year: int
    fiscal_quarter: Optional[int] = None  # 1, 2, 3, 4
    fiscal_period: Optional[str] = None  # "Q1", "Q2", "Q3", "Q4", "FY"
    
    # Dates
    report_date: str  # Actual report date (YYYY-MM-DD)
    fiscal_date_ending: Optional[str] = None  # End of fiscal period
    
    # Earnings data
    reported_eps: Optional[float] = None  # Reported EPS
    estimated_eps: Optional[float] = None  # Analyst estimate
    surprise: Optional[float] = None  # Earnings surprise
    surprise_percent: Optional[float] = None  # Surprise percentage
    
    # Revenue
    reported_revenue: Optional[float] = None
    estimated_revenue: Optional[float] = None
    
    # Additional metrics (from detailed providers)
    net_income: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "stock_earnings"
        indexes = [
            "ticker",
            "report_date",
            [("ticker", 1), ("fiscal_year", -1), ("fiscal_quarter", -1)],
            [("ticker", 1), ("report_date", -1)],
            "source_provider",
        ]
        # TTL: Keep earnings for 2 years
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 63072000  # 2 years
        }


# ==================== Technical Indicator Models ====================

class TechnicalIndicator(Document):
    """
    Technical indicator data (supports 50+ indicators).
    
    TTL: 30 days (indicators can be recalculated)
    Source providers: Alpha Vantage (EXCELLENT, 50+ indicators)
    
    Flexible schema to support all indicator types:
    - Moving Averages: SMA, EMA, WMA, DEMA, TEMA, TRIMA
    - Oscillators: RSI, MACD, STOCH, CCI, etc.
    - Volatility: BBANDS, ATR
    - Volume: AD, OBV
    - Trend: ADX, AROON, PLUS_DI, MINUS_DI
    - And many more...
    """
    # Stock identification
    ticker: str
    
    # Indicator identification
    indicator_name: str  # "SMA", "RSI", "MACD", etc.
    indicator_type: IndicatorType  # Category
    
    # Time period
    date: str  # YYYY-MM-DD
    timestamp: datetime
    
    # Parameters (flexible for different indicators)
    parameters: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"period": 14, "series_type": "close"}
    
    # Values (flexible for single or multiple outputs)
    value: Optional[float] = None  # Single value (e.g., SMA, RSI)
    values: Dict[str, float] = Field(default_factory=dict)  # Multiple values (e.g., MACD: {"macd": 0.5, "signal": 0.3, "histogram": 0.2})
    
    # Metadata
    source_provider: DataSource
    interval: str = "daily"  # "1min", "5min", "daily", etc.
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "technical_indicators"
        indexes = [
            "ticker",
            "indicator_name",
            "date",
            [("ticker", 1), ("indicator_name", 1), ("date", -1)],  # Indicator time series
            "indicator_type",
            "source_provider",
        ]
        # TTL: Keep indicators for 30 days
        timeseries_options = {
            "timeField": "timestamp",
            "granularity": "hours",
            "expireAfterSeconds": 2592000  # 30 days
        }


# ==================== Fundamental Data Models ====================

class CompanyOverview(Document):
    """
    Company profile and overview data.
    
    TTL: 90 days (company info changes slowly)
    Source providers: Alpha Vantage (EXCELLENT), Finnhub (GOOD)
    """
    # Company identification
    ticker: str  # Unique identifier
    
    # Basic info
    name: str
    description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Location
    country: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Contact
    website: Optional[str] = None
    phone: Optional[str] = None
    
    # Financial metrics
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    revenue_ttm: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    # Stock info
    exchange: Optional[str] = None
    currency: Optional[str] = None
    shares_outstanding: Optional[int] = None
    
    # Dates
    ipo_date: Optional[str] = None
    fiscal_year_end: Optional[str] = None
    
    # Extended data (provider-specific)
    extended_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "company_overviews"
        indexes = [
            "ticker",  # Unique - one overview per ticker
            "sector",
            "industry",
            "source_provider",
        ]
        # TTL: Keep company data for 90 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
        }


class FinancialStatement(Document):
    """
    Financial statement data (income, balance sheet, cash flow).
    
    TTL: Keep for 5 years
    Source providers: Alpha Vantage (EXCELLENT)
    
    Flexible schema to support all statement types.
    """
    # Company identification
    ticker: str
    
    # Statement type
    statement_type: str  # "income", "balance_sheet", "cash_flow"
    
    # Period
    fiscal_year: int
    fiscal_quarter: Optional[int] = None  # None for annual statements
    fiscal_date_ending: str  # YYYY-MM-DD
    report_date: Optional[str] = None  # When statement was filed
    
    # Currency
    currency: str = "USD"
    
    # Statement data (flexible JSON)
    data: Dict[str, Any] = Field(default_factory=dict)  # All line items
    
    # Common metrics (extracted for easy querying)
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "financial_statements"
        indexes = [
            "ticker",
            "statement_type",
            [("ticker", 1), ("statement_type", 1), ("fiscal_year", -1), ("fiscal_quarter", -1)],
            [("ticker", 1), ("fiscal_date_ending", -1)],
            "source_provider",
        ]
        # TTL: Keep financials for 5 years
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 157680000  # 5 years
        }


# ==================== News & Analyst Models ====================

class NewsArticle(Document):
    """
    News articles related to stocks.
    
    TTL: 30 days
    Source providers: Alpha Vantage (GOOD), Finnhub (EXCELLENT), yfinance (BASIC)
    """
    # Article identification
    url: str  # Article URL (unique identifier)
    
    # Content
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None  # Full content if available
    
    # Related tickers
    tickers: List[str] = Field(default_factory=list)  # Multiple tickers can be mentioned
    
    # Dates
    published_at: datetime  # When article was published
    
    # Source
    source_name: Optional[str] = None  # "Reuters", "Bloomberg", etc.
    source_domain: Optional[str] = None  # "reuters.com"
    author: Optional[str] = None
    
    # Sentiment analysis (if available)
    sentiment_label: Optional[str] = None  # "positive", "negative", "neutral"
    sentiment_score: Optional[float] = None  # -1.0 to 1.0
    
    # Categories/topics
    topics: List[str] = Field(default_factory=list)  # "earnings", "merger", "lawsuit", etc.
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "news_articles"
        indexes = [
            "url",  # Unique - one article per URL
            "published_at",
            "tickers",
            [("tickers", 1), ("published_at", -1)],  # Recent news for ticker
            "sentiment_label",
            "source_provider",
        ]
        # TTL: Keep news for 30 days
        timeseries_options = {
            "timeField": "published_at",
            "granularity": "hours",
            "expireAfterSeconds": 2592000  # 30 days
        }


class AnalystRating(Document):
    """
    Analyst recommendations and ratings.
    
    TTL: 90 days
    Source providers: Finnhub (EXCELLENT)
    """
    # Stock identification
    ticker: str
    
    # Rating details
    rating: str  # "buy", "sell", "hold", "strong buy", "strong sell"
    rating_scale: Optional[str] = None  # e.g., "1-5" where 1=strong buy
    
    # Analyst/firm
    analyst_name: Optional[str] = None
    analyst_firm: Optional[str] = None
    
    # Dates
    rating_date: str  # YYYY-MM-DD
    previous_rating: Optional[str] = None
    rating_change: Optional[str] = None  # "upgrade", "downgrade", "initiated", "reiterated"
    
    # Consensus (if available)
    buy_count: Optional[int] = None
    hold_count: Optional[int] = None
    sell_count: Optional[int] = None
    consensus_rating: Optional[str] = None  # "buy", "hold", "sell"
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analyst_ratings"
        indexes = [
            "ticker",
            "rating_date",
            [("ticker", 1), ("rating_date", -1)],  # Recent ratings for ticker
            "analyst_firm",
            "source_provider",
        ]
        # TTL: Keep ratings for 90 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
        }


class PriceTarget(Document):
    """
    Analyst price targets.
    
    TTL: 90 days
    Source providers: Finnhub (EXCELLENT)
    """
    # Stock identification
    ticker: str
    
    # Price target
    target_price: float
    target_high: Optional[float] = None  # Highest target among analysts
    target_low: Optional[float] = None  # Lowest target
    target_mean: Optional[float] = None  # Mean consensus target
    target_median: Optional[float] = None  # Median consensus target
    
    # Current price context
    current_price: Optional[float] = None
    upside_potential: Optional[float] = None  # Percentage upside/downside
    
    # Analyst info
    analyst_count: Optional[int] = None  # Number of analysts covering
    
    # Dates
    target_date: str  # YYYY-MM-DD
    target_period: Optional[str] = None  # "12 months", "Q4 2025", etc.
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "price_targets"
        indexes = [
            "ticker",
            "target_date",
            [("ticker", 1), ("target_date", -1)],  # Recent targets for ticker
            "source_provider",
        ]
        # TTL: Keep targets for 90 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
        }


# ==================== Forex/Crypto/Commodity Models ====================

class ForexRate(Document):
    """
    Forex exchange rates.
    
    TTL: 30 days
    Source providers: Alpha Vantage (EXCELLENT), Finnhub (GOOD)
    """
    # Currency pair
    from_currency: str  # "USD"
    to_currency: str  # "EUR"
    pair: str  # "USD/EUR"
    
    # Rate data
    exchange_rate: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    
    # Time series data
    date: str  # YYYY-MM-DD
    timestamp: datetime
    
    # OHLC (if available for daily data)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    interval: str = "daily"  # "1min", "5min", "daily", etc.
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forex_rates"
        indexes = [
            "pair",
            "date",
            [("from_currency", 1), ("to_currency", 1), ("date", -1)],
            [("pair", 1), ("date", -1)],
            "timestamp",
            "source_provider",
        ]
        # TTL: Keep forex data for 30 days
        timeseries_options = {
            "timeField": "timestamp",
            "granularity": "hours",
            "expireAfterSeconds": 2592000  # 30 days
        }


class CryptoPrice(Document):
    """
    Cryptocurrency prices.
    
    TTL: 30 days
    Source providers: Alpha Vantage (EXCELLENT), Finnhub (GOOD)
    """
    # Crypto identification
    symbol: str  # "BTC", "ETH", etc.
    name: Optional[str] = None  # "Bitcoin", "Ethereum"
    market: str = "USD"  # Quote currency (USD, EUR, BTC, etc.)
    
    # Price data
    price: float
    
    # Time series data
    date: str  # YYYY-MM-DD
    timestamp: datetime
    
    # OHLCV (if available)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    
    # Change
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    interval: str = "daily"  # "1min", "5min", "daily", etc.
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "crypto_prices"
        indexes = [
            "symbol",
            "date",
            [("symbol", 1), ("market", 1), ("date", -1)],
            "timestamp",
            "source_provider",
        ]
        # TTL: Keep crypto data for 30 days
        timeseries_options = {
            "timeField": "timestamp",
            "granularity": "hours",
            "expireAfterSeconds": 2592000  # 30 days
        }


class CommodityPrice(Document):
    """
    Commodity prices (crude oil, natural gas, metals, etc.).
    
    TTL: 90 days
    Source providers: Alpha Vantage (EXCELLENT)
    """
    # Commodity identification
    commodity: str  # "WTI", "BRENT", "NATURAL_GAS", "COPPER", etc.
    commodity_name: str  # "WTI Crude Oil", "Brent Crude Oil", etc.
    unit: str  # "USD/barrel", "USD/MMBtu", "USD/pound", etc.
    
    # Price data
    price: float
    
    # Time series data
    date: str  # YYYY-MM-DD
    timestamp: datetime
    
    # OHLC (if available)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    
    # Metadata
    source_provider: DataSource
    interval: str = "daily"  # "monthly", "quarterly", "annual", "daily"
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "commodity_prices"
        indexes = [
            "commodity",
            "date",
            [("commodity", 1), ("date", -1)],
            "timestamp",
            "source_provider",
        ]
        # TTL: Keep commodity data for 90 days
        timeseries_options = {
            "timeField": "timestamp",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
        }


# ==================== Economic Indicator Models ====================

class EconomicIndicator(Document):
    """
    Economic indicators (GDP, CPI, unemployment, etc.).
    
    TTL: Keep forever (historical economic data)
    Source providers: Alpha Vantage (EXCELLENT)
    """
    # Indicator identification
    indicator: str  # "GDP", "CPI", "UNEMPLOYMENT", "FEDERAL_FUNDS_RATE", etc.
    indicator_name: str  # "Real GDP", "Consumer Price Index", etc.
    country: str = "USA"  # Country code
    
    # Value
    value: float
    unit: Optional[str] = None  # "billions USD", "percent", "index", etc.
    
    # Period
    date: str  # YYYY-MM-DD (or YYYY-MM, YYYY-QQ)
    period_type: str  # "annual", "quarterly", "monthly"
    
    # Year/quarter breakdown
    year: int
    quarter: Optional[int] = None  # 1, 2, 3, 4
    month: Optional[int] = None  # 1-12
    
    # Metadata
    source_provider: DataSource
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "economic_indicators"
        indexes = [
            "indicator",
            "date",
            [("indicator", 1), ("country", 1), ("date", -1)],
            [("indicator", 1), ("year", -1), ("quarter", -1)],
            "country",
            "source_provider",
        ]
        # No TTL - keep economic data forever
