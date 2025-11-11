"""Repository for managing ticker configuration in MongoDB."""
from typing import List, Optional
from datetime import datetime
from app.models import TickerConfig


class TickerConfigRepository:
    """Handle ticker configuration CRUD operations."""
    
    async def get_all_enabled_tickers(self) -> List[str]:
        """
        Get all enabled tickers from MongoDB.
        
        Returns:
            List of ticker symbols that are enabled
        """
        configs = await TickerConfig.find(TickerConfig.enabled == True).to_list()
        return [config.ticker for config in configs]
    
    async def get_all_tickers(self) -> List[TickerConfig]:
        """
        Get all ticker configurations (enabled and disabled).
        
        Returns:
            List of TickerConfig documents
        """
        return await TickerConfig.find_all().to_list()
    
    async def get_ticker(self, ticker: str) -> Optional[TickerConfig]:
        """
        Get a specific ticker configuration.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            TickerConfig or None if not found
        """
        return await TickerConfig.find_one(TickerConfig.ticker == ticker.upper())
    
    async def add_ticker(self, ticker: str, enabled: bool = True) -> TickerConfig:
        """
        Add a new ticker to configuration.
        
        Args:
            ticker: Stock ticker symbol
            enabled: Whether ticker is enabled for polling
            
        Returns:
            Created TickerConfig
            
        Raises:
            ValueError: If ticker already exists
        """
        ticker = ticker.upper()
        
        # Check if already exists
        existing = await self.get_ticker(ticker)
        if existing:
            raise ValueError(f"Ticker {ticker} already exists")
        
        # Create new
        config = TickerConfig(
            ticker=ticker,
            enabled=enabled,
            added_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await config.insert()
        return config
    
    async def remove_ticker(self, ticker: str) -> bool:
        """
        Remove a ticker from configuration.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if removed
            
        Raises:
            ValueError: If ticker does not exist
        """
        config = await self.get_ticker(ticker.upper())
        if not config:
            raise ValueError(f"Ticker {ticker.upper()} does not exist")
        
        await config.delete()
        return True
    
    async def enable_ticker(self, ticker: str) -> Optional[TickerConfig]:
        """
        Enable a ticker for polling.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Updated TickerConfig or None if not found
        """
        config = await self.get_ticker(ticker.upper())
        if config:
            config.enabled = True
            config.updated_at = datetime.utcnow()
            await config.save()
            return config
        return None
    
    async def disable_ticker(self, ticker: str) -> Optional[TickerConfig]:
        """
        Disable a ticker (keeps in DB but won't poll).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Updated TickerConfig or None if not found
        """
        config = await self.get_ticker(ticker.upper())
        if config:
            config.enabled = False
            config.updated_at = datetime.utcnow()
            await config.save()
            return config
        return None
    
    async def seed_from_yaml(self, tickers: List[str]) -> int:
        """
        Seed database with tickers from YAML if DB is empty.
        
        Args:
            tickers: List of ticker symbols from YAML
            
        Returns:
            Number of tickers added
        """
        # Check if DB already has tickers
        existing_count = await TickerConfig.count()
        if existing_count > 0:
            return 0  # Don't seed if already has data
        
        # Add all tickers from YAML
        count = 0
        for ticker in tickers:
            await self.add_ticker(ticker, enabled=True)
            count += 1
        
        return count


# Singleton instance
ticker_config_repository = TickerConfigRepository()
