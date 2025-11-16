"""
Precious metals price service - Business logic for metals price operations.
Follows Single Responsibility Principle.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.precious_metals_fetcher import precious_metals_fetcher
from app.repositories.precious_metals_repository import precious_metals_repository
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MetalsPriceService:
    """
    Business logic for precious metals price operations.
    Orchestrates fetching and repository operations.
    """
    
    async def fetch_and_save_gold_prices(self) -> Dict:
        """
        Fetch current gold prices and save to database.
        
        Returns:
            Status dictionary with result and data
        """
        logger.info("Starting gold price fetch and save")
        
        # Fetch prices
        prices = await precious_metals_fetcher.fetch_gold_prices()
        
        if not prices:
            logger.error("Failed to fetch gold prices")
            return {
                "status": "error",
                "message": "Failed to fetch gold prices from source"
            }
        
        # Save to database
        try:
            saved = await precious_metals_repository.save_gold_price(prices)
            return {
                "status": "success",
                "message": "Gold prices fetched and saved successfully",
                "data": {
                    "price_24k_per_gram": saved.price_24k_per_gram,
                    "price_22k_per_gram": saved.price_22k_per_gram,
                    "timestamp_ist": saved.timestamp_ist.isoformat(),
                    "timestamp_est": saved.timestamp_est.isoformat(),
                    "city": saved.city
                }
            }
        except Exception as e:
            logger.error(
                "Failed to save gold prices",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": f"Failed to save gold prices: {str(e)}"
            }
    
    async def fetch_and_save_silver_prices(self) -> Dict:
        """
        Fetch current silver prices and save to database.
        
        Returns:
            Status dictionary with result and data
        """
        logger.info("Starting silver price fetch and save")
        
        # Fetch prices
        prices = await precious_metals_fetcher.fetch_silver_prices()
        
        if not prices:
            logger.error("Failed to fetch silver prices")
            return {
                "status": "error",
                "message": "Failed to fetch silver prices from source"
            }
        
        # Save to database
        try:
            saved = await precious_metals_repository.save_silver_price(prices)
            return {
                "status": "success",
                "message": "Silver prices fetched and saved successfully",
                "data": {
                    "price_per_gram": saved.price_per_gram,
                    "price_per_kg": saved.price_per_kg,
                    "timestamp_ist": saved.timestamp_ist.isoformat(),
                    "timestamp_est": saved.timestamp_est.isoformat(),
                    "city": saved.city
                }
            }
        except Exception as e:
            logger.error(
                "Failed to save silver prices",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": f"Failed to save silver prices: {str(e)}"
            }
    
    async def fetch_and_save_all_prices(self) -> Dict:
        """
        Fetch both gold and silver prices.
        
        Returns:
            Combined status for both operations
        """
        logger.info("Fetching all precious metals prices")
        
        gold_result = await self.fetch_and_save_gold_prices()
        silver_result = await self.fetch_and_save_silver_prices()
        
        return {
            "gold": gold_result,
            "silver": silver_result,
            "overall_status": "success" if (
                gold_result["status"] == "success" and 
                silver_result["status"] == "success"
            ) else "partial" if (
                gold_result["status"] == "success" or 
                silver_result["status"] == "success"
            ) else "error"
        }
    
    async def get_latest_prices(self, city: str = "Chennai") -> Dict:
        """
        Get latest gold and silver prices from database.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with latest prices
        """
        gold = await precious_metals_repository.get_latest_gold_price(city)
        silver = await precious_metals_repository.get_latest_silver_price(city)
        
        return {
            "city": city,
            "gold": {
                "price_24k_per_gram": gold.price_24k_per_gram if gold else None,
                "price_22k_per_gram": gold.price_22k_per_gram if gold else None,
                "timestamp_ist": gold.timestamp_ist.isoformat() if gold else None,
                "timestamp_est": gold.timestamp_est.isoformat() if gold else None
            } if gold else None,
            "silver": {
                "price_per_gram": silver.price_per_gram if silver else None,
                "price_per_kg": silver.price_per_kg if silver else None,
                "timestamp_ist": silver.timestamp_ist.isoformat() if silver else None,
                "timestamp_est": silver.timestamp_est.isoformat() if silver else None
            } if silver else None
        }
    
    async def get_price_history(
        self,
        metal: str,  # "gold" or "silver"
        city: str = "Chennai",
        days: int = 30
    ) -> List[Dict]:
        """
        Get historical prices for specified period.
        
        Args:
            metal: "gold" or "silver"
            city: City name
            days: Number of days of history
            
        Returns:
            List of price records
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        if metal.lower() == "gold":
            records = await precious_metals_repository.get_gold_price_history(
                city=city,
                start_date=start_date,
                end_date=end_date
            )
            return [
                {
                    "price_24k_per_gram": r.price_24k_per_gram,
                    "price_22k_per_gram": r.price_22k_per_gram,
                    "timestamp_ist": r.timestamp_ist.isoformat(),
                    "timestamp_est": r.timestamp_est.isoformat()
                }
                for r in records
            ]
        elif metal.lower() == "silver":
            records = await precious_metals_repository.get_silver_price_history(
                city=city,
                start_date=start_date,
                end_date=end_date
            )
            return [
                {
                    "price_per_gram": r.price_per_gram,
                    "price_per_kg": r.price_per_kg,
                    "timestamp_ist": r.timestamp_ist.isoformat(),
                    "timestamp_est": r.timestamp_est.isoformat()
                }
                for r in records
            ]
        else:
            logger.error(f"Invalid metal type: {metal}")
            return []


# Singleton instance
metals_price_service = MetalsPriceService()
