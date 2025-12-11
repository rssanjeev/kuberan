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
    MASSIVE = "massive"  # MASSIVE API (Polygon-compatible structure)
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
    
    ENHANCED for MASSIVE API (Phase 3): Now captures 30+ fields from ticker overview endpoint.
    
    TTL: 90 days (company info changes slowly)
    Source providers: MASSIVE (PRIMARY - 30+ fields), Alpha Vantage (FALLBACK), Finnhub (FALLBACK)
    """
    # ==================== Core Identification ====================
    ticker: str  # Unique identifier (e.g., "AAPL")
    name: str  # Company name (e.g., "Apple Inc.")
    
    # ==================== MASSIVE-Specific Identifiers ====================
    cik: Optional[str] = None  # SEC Central Index Key (e.g., "0000320193")
    composite_figi: Optional[str] = None  # Bloomberg Global ID (e.g., "BBG000B9XRY4")
    share_class_figi: Optional[str] = None  # Share class FIGI (e.g., "BBG001S5N8V8")
    ticker_root: Optional[str] = None  # Root ticker symbol (e.g., "AAPL")
    
    # ==================== Classification ====================
    type: Optional[str] = None  # Ticker type from MASSIVE (CS, ETF, ADRC, PFD, etc.)
    asset_type: Optional[str] = "Stock"  # Legacy: Stock, ETF, Fund, etc. (for backwards compatibility)
    market: Optional[str] = None  # Market type (stocks, crypto, fx, otc)
    locale: Optional[str] = None  # Locale (us, global)
    primary_exchange: Optional[str] = None  # Primary exchange MIC code (XNAS, XNYS, etc.)
    
    # ==================== Company Information ====================
    description: Optional[str] = None  # Company description
    sector: Optional[str] = None  # Business sector
    industry: Optional[str] = None  # Industry classification
    sic_code: Optional[str] = None  # Standard Industrial Classification code
    sic_description: Optional[str] = None  # SIC description
    
    # ==================== Contact Information ====================
    homepage_url: Optional[str] = None  # Company website
    phone_number: Optional[str] = None  # Contact phone (e.g., "+1 408 996-1010")
    
    # Address (structured)
    address1: Optional[str] = None  # Address line 1 (e.g., "One Apple Park Way")
    city: Optional[str] = None  # City (e.g., "Cupertino")
    state: Optional[str] = None  # State (e.g., "CA")
    postal_code: Optional[str] = None  # Postal/ZIP code (e.g., "95014")
    
    # Legacy fields (for backwards compatibility with Alpha Vantage data)
    country: Optional[str] = None  # Country
    address: Optional[str] = None  # Full address string (legacy)
    zip_code: Optional[str] = None  # Legacy zip code field
    website: Optional[str] = None  # Legacy website field
    phone: Optional[str] = None  # Legacy phone field
    
    # ==================== Branding ====================
    logo_url: Optional[str] = None  # Primary logo URL
    icon_url: Optional[str] = None  # Icon/favicon URL
    
    # ==================== Financial Metrics ====================
    market_cap: Optional[float] = None  # Market capitalization
    total_employees: Optional[int] = None  # Total number of employees
    
    # Share information
    shares_outstanding: Optional[int] = None  # Legacy field
    share_class_shares_outstanding: Optional[int] = None  # Shares outstanding for this class
    weighted_shares_outstanding: Optional[int] = None  # Weighted shares outstanding
    round_lot: Optional[int] = None  # Round lot size (typically 100)
    
    # Additional metrics (Alpha Vantage/Finnhub)
    pe_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    revenue_ttm: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    # ==================== Currency ====================
    currency: Optional[str] = None  # Legacy currency field
    currency_name: Optional[str] = None  # Currency name (e.g., "usd")
    currency_symbol: Optional[str] = None  # Currency symbol (e.g., "$")
    
    # ==================== Dates & Status ====================
    list_date: Optional[str] = None  # IPO/listing date (YYYY-MM-DD)
    ipo_date: Optional[str] = None  # Legacy IPO date field
    fiscal_year_end: Optional[str] = None  # Fiscal year end
    
    active: Optional[bool] = None  # Is ticker actively traded
    delisted_utc: Optional[str] = None  # Delisting date if applicable
    last_updated_utc: Optional[str] = None  # Last update from MASSIVE
    
    # Legacy exchange field
    exchange: Optional[str] = None  # Legacy exchange field
    
    # ==================== Enrichment Tracking ====================
    enrichment_status: Optional[str] = None  # "base", "foundation", "enriched", "failed"
    enriched_at: Optional[datetime] = None  # When enrichment was applied
    metadata_sources: List[str] = Field(default_factory=list)  # Sources used (e.g., ["MASSIVE", "AlphaVantage"])
    
    # Batch collection tracking (incremental collection strategy)
    batch_priority: Optional[float] = None  # Market cap used for priority ordering (desc)
    collection_attempts: int = 0  # Number of times collection was attempted
    last_collection_attempt: Optional[datetime] = None  # When last collection was attempted
    collection_error: Optional[str] = None  # Last error message if collection failed
    
    # ==================== Extended Data ====================
    extended_data: Dict[str, Any] = Field(default_factory=dict)  # Provider-specific extras
    
    # ==================== Metadata ====================
    source_provider: DataSource  # Primary data source
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "company_overviews"
        indexes = [
            "ticker",  # Unique - one overview per ticker
            "sector",
            "industry",
            "source_provider",
            "asset_type",  # Index for filtering by asset type
            "enrichment_status",  # Index for finding tickers needing enrichment
            "batch_priority",  # Index for priority-ordered batch processing
            "last_collection_attempt",  # Index for finding tickers needing retry
        ]
        # TTL: Keep company data for 90 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
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


# ==================== ETF Models ====================

class ETFHolding(Document):
    """
    Individual holding within an ETF.
    
    Embedded document for ETF holdings data.
    """
    # Security identification
    symbol: str  # Ticker symbol
    description: str  # Company name
    
    # Weight in fund
    weight: float  # Decimal (e.g., 0.0783 = 7.83%)
    weight_pct: Optional[float] = None  # Percentage for display (7.83)
    
    # Additional data (if available)
    shares: Optional[int] = None
    market_value: Optional[float] = None
    sector: Optional[str] = None
    asset_type: Optional[str] = None
    
    class Settings:
        # This is an embedded document, not a collection
        is_root = False


class ETFSectorAllocation(Document):
    """
    Sector allocation for an ETF.
    
    Embedded document for sector breakdown.
    """
    sector: str  # Sector name (e.g., "INFORMATION TECHNOLOGY")
    weight: float  # Decimal (e.g., 0.348 = 34.8%)
    weight_pct: Optional[float] = None  # Percentage for display (34.8)
    
    class Settings:
        # This is an embedded document, not a collection
        is_root = False


class ETFProfile(Document):
    """
    Complete ETF profile with holdings and sector allocations.
    
    TTL: 30 days (ETF holdings change quarterly)
    Source providers: Alpha Vantage (ETF_PROFILE)
    
    Used for:
    - ETF comparison and overlap analysis
    - Portfolio construction
    - Sector exposure analysis
    """
    # ETF identification
    ticker: str  # Unique identifier (e.g., "SPY", "QQQ")
    name: Optional[str] = None  # Full ETF name
    
    # Fund fundamentals
    net_assets: Optional[float] = None  # Total assets in USD
    net_expense_ratio: Optional[float] = None  # Expense ratio as decimal
    portfolio_turnover: Optional[float] = None  # Turnover as decimal
    dividend_yield: Optional[float] = None  # Dividend yield as decimal
    inception_date: Optional[str] = None  # YYYY-MM-DD
    leveraged: Optional[str] = None  # "YES" or "NO"
    
    # Holdings (complete list)
    holdings: List[Dict[str, Any]] = Field(default_factory=list)  # List of ETFHolding dicts
    total_holdings: int = 0  # Count of holdings
    
    # Sector allocations
    sector_allocations: List[Dict[str, Any]] = Field(default_factory=list)  # List of ETFSectorAllocation dicts
    
    # Top holdings summary (for quick access)
    top_10_holdings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    source_provider: DataSource = DataSource.ALPHA_VANTAGE
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None  # When holdings were last updated
    
    # Extended data (provider-specific)
    extended_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "etf_profiles"
        indexes = [
            "ticker",  # Unique - one profile per ETF
            "source_provider",
            "fetched_at",
            "last_updated",
        ]
        # TTL: Keep ETF data for 30 days (holdings change quarterly)
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 2592000  # 30 days
        }


class ETFComparison(Document):
    """
    Cached ETF comparison results.
    
    TTL: 7 days (recalculate weekly)
    
    Stores pre-calculated overlap metrics between two ETFs
    for faster retrieval and to reduce API calls.
    """
    # ETFs being compared
    ticker1: str
    ticker2: str
    comparison_key: str  # Sorted combination: "QQQ_SPY" (alphabetical)
    
    # Comparison date
    comparison_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Overlap metrics
    overlap_by_weight: float  # Total overlap percentage
    overlapping_holdings_count: int  # Number of common holdings
    ticker1_in_ticker2_pct: float  # % of ticker1 holdings also in ticker2
    ticker2_in_ticker1_pct: float  # % of ticker2 holdings also in ticker1
    
    # Sector drift (ticker1 - ticker2)
    sector_drift: Dict[str, float] = Field(default_factory=dict)
    
    # Overlapping holdings details
    overlapping_holdings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Overweight holdings (ticker1 has more exposure than ticker2)
    overweight_holdings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Underweight holdings (ticker1 has less exposure than ticker2)
    underweight_holdings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Fund statistics
    ticker1_stats: Dict[str, Any] = Field(default_factory=dict)
    ticker2_stats: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "etf_comparisons"
        indexes = [
            "comparison_key",  # Unique key for cached comparisons
            [("ticker1", 1), ("ticker2", 1)],
            "comparison_date",
            "fetched_at",
        ]
        # TTL: Keep comparisons for 7 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 604800  # 7 days
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


class RelatedCompany(Document):
    """
    Related companies/tickers for a given stock (PHASE 4).
    
    Captures peer companies, competitors, and correlated stocks from MASSIVE API.
    Used for comparative analysis, sector tracking, and portfolio diversification.
    
    TTL: 90 days (refresh quarterly)
    Source provider: MASSIVE (GET /v1/related-companies/{ticker})
    
    Example relationships:
    - AAPL → MSFT (competitor)
    - AAPL → GOOGL (tech sector peer)
    - TSLA → F (auto sector peer)
    """
    # Primary ticker
    ticker: str  # Stock symbol (e.g., "AAPL")
    
    # Related ticker
    related_ticker: str  # Related stock symbol (e.g., "MSFT")
    
    # Relationship details
    relationship_type: Optional[str] = None  # "competitor", "sector_peer", "correlated", etc.
    
    # Correlation metrics (if available from provider)
    correlation_score: Optional[float] = None  # -1.0 to 1.0 (price correlation)
    
    # Dates
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    source_provider: DataSource = DataSource.POLYGON  # MASSIVE uses Polygon data
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Extended relationship data (flexible schema for provider-specific fields)
    extended_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "related_companies"
        indexes = [
            "ticker",  # Find all related companies for a ticker
            "related_ticker",  # Reverse lookup
            [("ticker", 1), ("related_ticker", 1)],  # Unique relationship
            "relationship_type",  # Filter by relationship type
            [("ticker", 1), ("correlation_score", -1)],  # Most correlated first
            "last_updated",
            "fetched_at",
        ]
        # TTL: Keep relationships for 90 days
        timeseries_options = {
            "timeField": "fetched_at",
            "granularity": "hours",
            "expireAfterSeconds": 7776000  # 90 days
        }
