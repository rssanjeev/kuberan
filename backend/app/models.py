from beanie import Document
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    disabled: bool = False

    class Settings:
        name = "users"


class StockMetadata(Document):
    """Store infrequently changing stock metadata."""
    ticker: str
    name: str
    short_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    currency: str = "USD"
    exchange: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    updated_at: datetime
    
    class Settings:
        name = "stock_metadata"
        indexes = [
            "ticker",  # Unique index on ticker
        ]


class StockPrice(Document):
    """Store time-series price data."""
    ticker: str
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    open: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime
    
    class Settings:
        name = "stock_prices"
        indexes = [
            "ticker",
            "timestamp",
            [("ticker", 1), ("timestamp", -1)],  # Compound index for queries
        ]


class UserWatchlist(Document):
    """Store user's watchlist of tickers."""
    user_id: str  # Reference to User
    tickers: list[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        name = "user_watchlists"
        indexes = [
            "user_id",
        ]


class MerchantCategory(Document):
    """
    Store merchant-to-category mappings for transaction categorization.
    Used to automatically categorize transactions based on merchant patterns.
    """
    merchant_name: str  # Exact merchant name from transaction
    category: str  # Category name (e.g., "Coffee & Cafes", "Groceries")
    confidence: float = 1.0  # Confidence score (0.0-1.0) for auto-categorization
    source: str = "manual"  # "manual", "auto", "ml"
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        name = "merchant_categories"
        indexes = [
            "merchant_name",  # Unique index on merchant name
            "category",
        ]


class CreditCardTransaction(Document):
    """
    Store credit card transactions parsed from statements.
    Security: No account numbers or sensitive account info stored.
    Focus: Transaction-level data only for expense analysis.
    """
    # Transaction identification (no account info)
    transaction_date: str  # MM/DD format from statement
    statement_year: int  # Year of statement
    statement_month: int  # Month of statement (for grouping)
    
    # Merchant information
    merchant_name: str  # Merchant description
    merchant_location: Optional[str] = None  # Location/state if available
    
    # Transaction details
    amount: float  # Positive for charges, negative for credits/payments
    transaction_type: str  # "charge" or "credit"
    category: Optional[str] = None  # Auto-assigned category
    
    # Metadata (no sensitive data)
    bank: str  # "Chase", "Amex", etc.
    raw_description: str  # Original transaction line for reference
    
    # Processing info
    imported_at: datetime
    source_file_hash: Optional[str] = None  # SHA256 hash of PDF (for deduplication)
    
    class Settings:
        name = "credit_card_transactions"
        indexes = [
            "statement_year",
            "statement_month",
            "category",
            "merchant_name",
            "bank",
            [("statement_year", -1), ("statement_month", -1)],  # Recent first
            [("category", 1), ("statement_year", -1)],  # Category analysis
        ]


class FinancialDocumentMetadata(Document):
    """
    Store minimal metadata about processed financial documents.
    Security: PDF file itself is NEVER stored, only processing metadata.
    """
    file_hash: str  # SHA256 hash of PDF (for deduplication)
    document_type: str  # "credit_card_statement", "payslip", etc.
    bank: Optional[str] = None  # Bank name if credit card
    
    # Statement period (no account info)
    statement_year: int
    statement_month: int
    statement_period_start: Optional[str] = None  # MM/DD/YY format
    statement_period_end: Optional[str] = None  # MM/DD/YY format
    
    # Processing info
    processed_at: datetime
    transaction_count: int  # Number of transactions extracted
    total_charges: float
    total_credits: float
    
    class Settings:
        name = "financial_document_metadata"
        indexes = [
            "file_hash",  # Unique index for deduplication
            "document_type",
            "bank",
            [("statement_year", -1), ("statement_month", -1)],
        ]


class GoldPrice(Document):
    """Store gold price data for Chennai."""
    price_24k_per_gram: float  # 24 karat gold per gram
    price_24k_per_8_gram: float  # 24K per 8 grams
    price_22k_per_gram: float  # 22 karat gold per gram
    price_22k_per_8_gram: float  # 22K per 8 grams
    city: str = "Chennai"
    timestamp_ist: datetime  # IST timezone (Asia/Kolkata)
    timestamp_est: datetime  # EST timezone (US/Eastern)
    source: str = "goodreturns.in"
    
    class Settings:
        name = "gold_prices"
        indexes = [
            "timestamp_ist",
            "timestamp_est",
            "city",
            [("city", 1), ("timestamp_ist", -1)],  # Compound index for queries
        ]


class SilverPrice(Document):
    """Store silver price data for Chennai."""
    price_per_gram: float
    price_per_kg: float
    city: str = "Chennai"
    timestamp_ist: datetime  # IST timezone (Asia/Kolkata)
    timestamp_est: datetime  # EST timezone (US/Eastern)
    source: str = "goodreturns.in"
    
    class Settings:
        name = "silver_prices"
        indexes = [
            "timestamp_ist",
            "timestamp_est",
            "city",
            [("city", 1), ("timestamp_ist", -1)],  # Compound index for queries
        ]

