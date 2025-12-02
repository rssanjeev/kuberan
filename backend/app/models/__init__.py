"""
Kuberan Data Models.

This package contains all Beanie ODM models organized by domain:

Domain Models:
- auth: User authentication and profile
- stock: Stock Tracker domain (StockMetadata, StockPrice, UserWatchlist, TickerConfig)
- financier: Financier domain (MerchantCategory, CreditCardTransaction, FinancialDocumentMetadata)
- precious_metals: Precious metals tracking (GoldPrice, SilverPrice)
- provider: Multi-provider data models (17 models for stocks, forex, crypto, news, etc.)
- monitoring: System monitoring and metrics (4 models for API tracking, health checks, rate limits)

Usage:
    from app.models import User, StockPrice, CreditCardTransaction
    from app.models.provider import DataSource, StockQuote, CompanyOverview
    from app.models.monitoring import ProviderAPICall, ProviderDailyStats
"""

# Auth models
from app.models.auth import User

# Stock Tracker models
from app.models.stock import (
    StockMetadata,
    StockPrice,
    UserWatchlist,
    TickerConfig,
    TickerType
)

# Financier models
from app.models.financier import (
    MerchantCategory,
    CreditCardTransaction,
    FinancialDocumentMetadata,
)

# Precious Metals models
from app.models.precious_metals import (
    GoldPrice,
    SilverPrice,
)

# Investor models
from app.models.investor import (
    FamousInvestorPortfolio,
)

# Multi-Provider models (enums and 20 data models)
from app.models.provider import (
    # Enums
    DataSource,
    IndicatorType,
    
    # Stock models
    StockQuote,
    StockHistoricalPrice,
    StockDividend,
    StockSplit,
    StockEarnings,
    
    # Technical Indicator model
    TechnicalIndicator,
    
    # Fundamental Data models
    CompanyOverview,
    FinancialStatement,
    
    # News & Analyst models
    NewsArticle,
    AnalystRating,
    PriceTarget,
    
    # Forex/Crypto/Commodity models
    ForexRate,
    CryptoPrice,
    CommodityPrice,
    
    # ETF models
    ETFHolding,
    ETFSectorAllocation,
    ETFProfile,
    ETFComparison,
    
    # Economic Indicator model
    EconomicIndicator,
)

# Monitoring & Metrics models
from app.models.monitoring import (
    CallStatus,
    ProviderAPICall,
    ProviderDailyStats,
    ProviderHealthCheck,
    RateLimitStatus,
)

# All Beanie Document models for initialization
__all__ = [
    # Auth
    "User",
    
    # Stock Tracker
    "StockMetadata",
    "StockPrice",
    "UserWatchlist",
    "TickerConfig",
    "TickerType",
    
    # Financier
    "MerchantCategory",
    "CreditCardTransaction",
    "FinancialDocumentMetadata",
    
    # Precious Metals
    "GoldPrice",
    "SilverPrice",
    
    # Provider Enums
    "DataSource",
    "IndicatorType",
    
    # Provider Stock Models
    "StockQuote",
    "StockHistoricalPrice",
    "StockDividend",
    "StockSplit",
    "StockEarnings",
    
    # Provider Technical Indicator
    "TechnicalIndicator",
    
    # Provider Fundamental Data
    "CompanyOverview",
    "FinancialStatement",
    
    # Provider News & Analyst
    "NewsArticle",
    "AnalystRating",
    "PriceTarget",
    
    # Provider Forex/Crypto/Commodity
    "ForexRate",
    "CryptoPrice",
    "CommodityPrice",
    
    # Provider ETF Models
    "ETFHolding",
    "ETFSectorAllocation",
    "ETFProfile",
    "ETFComparison",
    
    # Provider Economic
    "EconomicIndicator",
    
    # Monitoring Enums
    "CallStatus",
    
    # Monitoring Models
    "ProviderAPICall",
    "ProviderDailyStats",
    "ProviderHealthCheck",
    "RateLimitStatus",
]

# List of all Document models for Beanie initialization
DOCUMENT_MODELS = [
    # Auth
    User,
    
    # Stock Tracker
    StockMetadata,
    StockPrice,
    UserWatchlist,
    TickerConfig,
    TickerType,
    
    # Financier
    MerchantCategory,
    CreditCardTransaction,
    FinancialDocumentMetadata,
    
    # Precious Metals
    GoldPrice,
    SilverPrice,
    
    # Investor
    FamousInvestorPortfolio,
    
    # Provider Models
    StockQuote,
    StockHistoricalPrice,
    StockDividend,
    StockSplit,
    StockEarnings,
    TechnicalIndicator,
    CompanyOverview,
    FinancialStatement,
    NewsArticle,
    AnalystRating,
    PriceTarget,
    ForexRate,
    CryptoPrice,
    CommodityPrice,
    ETFProfile,
    ETFComparison,
    EconomicIndicator,
    
    # Monitoring Models
    ProviderAPICall,
    ProviderDailyStats,
    ProviderHealthCheck,
    RateLimitStatus,
]
