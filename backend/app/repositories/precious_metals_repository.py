"""
Repository for precious metals price data access.
Handles CRUD operations for gold and silver prices.
"""
from typing import List, Optional
from datetime import datetime
from app.models import GoldPrice, SilverPrice
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PreciousMetalsRepository:
    """
    Data access layer for precious metals prices.
    NO business logic - pure data operations.
    """
    
    # ========== Gold Price Operations ==========
    
    async def save_gold_price(self, price_data: dict) -> GoldPrice:
        """
        Save gold price record to database.
        
        Args:
            price_data: Dictionary with gold price fields
            
        Returns:
            Saved GoldPrice document
        """
        gold_price = GoldPrice(**price_data)
        await gold_price.insert()
        logger.info(
            "Saved gold price to database",
            extra={
                "24k_per_gram": price_data['price_24k_per_gram'],
                "city": price_data['city']
            }
        )
        return gold_price
    
    async def get_latest_gold_price(self, city: str = "Chennai") -> Optional[GoldPrice]:
        """
        Get most recent gold price for a city.
        
        Args:
            city: City name (default Chennai)
            
        Returns:
            Latest GoldPrice document or None
        """
        return await GoldPrice.find(
            GoldPrice.city == city
        ).sort(-GoldPrice.timestamp_ist).first_or_none()
    
    async def get_gold_price_history(
        self,
        city: str = "Chennai",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[GoldPrice]:
        """
        Get historical gold prices with optional date filtering.
        
        Args:
            city: City name
            start_date: Optional start date filter (compared against IST)
            end_date: Optional end date filter (compared against IST)
            limit: Maximum records to return
            
        Returns:
            List of GoldPrice documents
        """
        query = GoldPrice.find(GoldPrice.city == city)
        
        if start_date:
            query = query.find(GoldPrice.timestamp_ist >= start_date)
        if end_date:
            query = query.find(GoldPrice.timestamp_ist <= end_date)
        
        return await query.sort(-GoldPrice.timestamp_ist).limit(limit).to_list()
    
    async def get_earliest_gold_price(self, city: str = "Chennai") -> Optional[GoldPrice]:
        """
        Get earliest gold price record for a city.
        
        Args:
            city: City name (default Chennai)
            
        Returns:
            Earliest GoldPrice document or None
        """
        return await GoldPrice.find(
            GoldPrice.city == city
        ).sort(GoldPrice.timestamp_ist).first_or_none()
    
    # ========== Silver Price Operations ==========
    
    async def save_silver_price(self, price_data: dict) -> SilverPrice:
        """
        Save silver price record to database.
        
        Args:
            price_data: Dictionary with silver price fields
            
        Returns:
            Saved SilverPrice document
        """
        silver_price = SilverPrice(**price_data)
        await silver_price.insert()
        logger.info(
            "Saved silver price to database",
            extra={
                "per_gram": price_data['price_per_gram'],
                "city": price_data['city']
            }
        )
        return silver_price
    
    async def get_latest_silver_price(self, city: str = "Chennai") -> Optional[SilverPrice]:
        """
        Get most recent silver price for a city.
        
        Args:
            city: City name (default Chennai)
            
        Returns:
            Latest SilverPrice document or None
        """
        return await SilverPrice.find(
            SilverPrice.city == city
        ).sort(-SilverPrice.timestamp_ist).first_or_none()
    
    async def get_silver_price_history(
        self,
        city: str = "Chennai",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SilverPrice]:
        """
        Get historical silver prices with optional date filtering.
        
        Args:
            city: City name
            start_date: Optional start date filter (compared against IST)
            end_date: Optional end date filter (compared against IST)
            limit: Maximum records to return
            
        Returns:
            List of SilverPrice documents
        """
        query = SilverPrice.find(SilverPrice.city == city)
        
        if start_date:
            query = query.find(SilverPrice.timestamp_ist >= start_date)
        if end_date:
            query = query.find(SilverPrice.timestamp_ist <= end_date)
        
        return await query.sort(-SilverPrice.timestamp_ist).limit(limit).to_list()
    
    async def get_earliest_silver_price(self, city: str = "Chennai") -> Optional[SilverPrice]:
        """
        Get earliest silver price record for a city.
        
        Args:
            city: City name (default Chennai)
            
        Returns:
            Earliest SilverPrice document or None
        """
        return await SilverPrice.find(
            SilverPrice.city == city
        ).sort(SilverPrice.timestamp_ist).first_or_none()


# Singleton instance
precious_metals_repository = PreciousMetalsRepository()
