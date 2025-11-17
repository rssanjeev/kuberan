"""
Stock Tracker domain models.

Models:
- StockMetadata: Infrequently changing stock information
- StockPrice: Time-series price data
- UserWatchlist: User's tracked tickers
- TickerConfig: Global ticker configuration for polling
"""

from beanie import Document
from typing import Optional
from datetime import datetime


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


class TickerConfig(Document):
    """Store global ticker configuration for price polling."""
    ticker: str
    enabled: bool = True
    added_at: datetime
    updated_at: datetime
    
    class Settings:
        name = "ticker_config"
        indexes = [
            "ticker",
            "enabled",
        ]
