"""
Precious Metals domain models.

Models:
- GoldPrice: Gold price data for Chennai
- SilverPrice: Silver price data for Chennai
"""

from beanie import Document
from datetime import datetime


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
