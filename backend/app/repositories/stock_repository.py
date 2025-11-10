from typing import Optional, List
from datetime import datetime, timedelta
from app.models import StockMetadata, StockPrice, UserWatchlist

class StockRepository:
    """Repository for stock data persistence in MongoDB."""
    
    async def save_stock_metadata(self, metadata: dict) -> StockMetadata:
        """
        Save or update stock metadata in the database.
        
        Args:
            metadata: Dictionary with stock metadata
            
        Returns:
            Saved StockMetadata document
        """
        ticker = metadata["ticker"]
        
        # Check if metadata already exists
        existing = await StockMetadata.find_one(StockMetadata.ticker == ticker)
        
        if existing:
            # Update existing metadata
            for key, value in metadata.items():
                if key != "ticker" and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            await existing.save()
            return existing
        else:
            # Create new metadata
            stock_meta = StockMetadata(
                ticker=ticker,
                name=metadata.get("name", ticker),
                short_name=metadata.get("short_name"),
                sector=metadata.get("sector"),
                industry=metadata.get("industry"),
                market_cap=metadata.get("market_cap"),
                currency=metadata.get("currency", "USD"),
                exchange=metadata.get("exchange"),
                country=metadata.get("country"),
                website=metadata.get("website"),
                description=metadata.get("description"),
                updated_at=datetime.utcnow()
            )
            await stock_meta.insert()
            return stock_meta
    
    async def get_stock_metadata(self, ticker: str) -> Optional[StockMetadata]:
        """Get stock metadata from database."""
        return await StockMetadata.find_one(StockMetadata.ticker == ticker)
    
    async def is_metadata_stale(self, ticker: str, max_age_days: int = 7) -> bool:
        """
        Check if metadata needs refreshing.
        
        Args:
            ticker: Stock ticker
            max_age_days: Maximum age in days before refresh needed
            
        Returns:
            True if metadata is stale or doesn't exist
        """
        metadata = await self.get_stock_metadata(ticker)
        if not metadata:
            return True
        
        age = datetime.utcnow() - metadata.updated_at
        return age > timedelta(days=max_age_days)
    
    async def save_stock_price(self, price_data: dict) -> StockPrice:
        """
        Save stock price data to database.
        
        Args:
            price_data: Dictionary with price data
            
        Returns:
            Saved StockPrice document
        """
        stock_price = StockPrice(
            ticker=price_data["ticker"],
            current_price=price_data.get("current_price"),
            previous_close=price_data.get("previous_close"),
            open=price_data.get("open"),
            day_high=price_data.get("day_high"),
            day_low=price_data.get("day_low"),
            volume=price_data.get("volume"),
            timestamp=datetime.utcnow()
        )
        await stock_price.insert()
        return stock_price
    
    async def get_latest_price(self, ticker: str) -> Optional[StockPrice]:
        """Get the latest price data for a ticker."""
        return await StockPrice.find(
            StockPrice.ticker == ticker
        ).sort(-StockPrice.timestamp).first_or_none()
    
    async def get_price_history(
        self, 
        ticker: str, 
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StockPrice]:
        """
        Get historical price data for a ticker.
        
        Args:
            ticker: Stock ticker
            start_time: Start datetime (default: last 24 hours)
            limit: Maximum number of records
            
        Returns:
            List of StockPrice documents
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=1)
        
        return await StockPrice.find(
            StockPrice.ticker == ticker,
            StockPrice.timestamp >= start_time
        ).sort(-StockPrice.timestamp).limit(limit).to_list()
    
    async def get_user_watchlist(self, user_id: str) -> Optional[UserWatchlist]:
        """Get user's watchlist."""
        return await UserWatchlist.find_one(UserWatchlist.user_id == user_id)
    
    async def add_to_watchlist(self, user_id: str, ticker: str) -> UserWatchlist:
        """Add a ticker to user's watchlist."""
        watchlist = await self.get_user_watchlist(user_id)
        
        if watchlist:
            if ticker not in watchlist.tickers:
                watchlist.tickers.append(ticker)
                watchlist.updated_at = datetime.utcnow()
                await watchlist.save()
        else:
            watchlist = UserWatchlist(
                user_id=user_id,
                tickers=[ticker],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await watchlist.insert()
        
        return watchlist
    
    async def remove_from_watchlist(self, user_id: str, ticker: str) -> Optional[UserWatchlist]:
        """Remove a ticker from user's watchlist."""
        watchlist = await self.get_user_watchlist(user_id)
        
        if watchlist and ticker in watchlist.tickers:
            watchlist.tickers.remove(ticker)
            watchlist.updated_at = datetime.utcnow()
            await watchlist.save()
        
        return watchlist

# Singleton instance
stock_repository = StockRepository()
