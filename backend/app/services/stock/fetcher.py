"""
Stock data fetcher - Yahoo Finance integration.
Provides functions to fetch stock prices, metadata, and historical data.
"""
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from app.repositories.stock_repository import stock_repository


class StockFetcher:
    """Service for fetching stock data from Yahoo Finance and managing persistence."""
    
    def __init__(self):
        self.repository = stock_repository
    
    async def get_stock_price(self, ticker: str) -> Optional[Dict]:
        """
        Get real-time price data for a single ticker (frequently changing data).
        This is optimized for frequent polling.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with price info or None if error
        """
        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            
            # Get fast info (lightweight API call)
            fast_info = await loop.run_in_executor(None, lambda: stock.fast_info)
            
            return {
                "ticker": ticker,
                "current_price": fast_info.get("lastPrice"),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None
    
    async def get_stock_metadata(self, ticker: str) -> Optional[Dict]:
        """
        Get metadata for a single ticker (infrequently changing data).
        This should be cached and refreshed less frequently.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with metadata or None if error
        """
        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            info = await loop.run_in_executor(None, lambda: stock.info)
            
            return {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "short_name": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange"),
                "country": info.get("country"),
                "website": info.get("website"),
                "description": info.get("longBusinessSummary"),
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching metadata for {ticker}: {e}")
            return None
    
    async def get_stock_info(self, ticker: str) -> Optional[Dict]:
        """
        Get complete stock information (both price and metadata).
        Use this for initial load; prefer get_stock_price() for updates.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with complete stock info or None if error
        """
        price_data = await self.get_stock_price(ticker)
        metadata = await self.get_stock_metadata(ticker)
        
        if not price_data or not metadata:
            return None
        
        return {**metadata, **price_data}
    
    async def get_stock_info_with_cache(self, ticker: str, save_to_db: bool = True) -> Optional[Dict]:
        """
        Get stock info with intelligent caching.
        - Always fetch fresh price data
        - Use cached metadata if available and not stale
        - Optionally save to database
        
        Args:
            ticker: Stock ticker symbol
            save_to_db: Whether to save data to MongoDB
            
        Returns:
            Dictionary with stock info
        """
        # Check if we need to refresh metadata
        needs_metadata_refresh = await self.repository.is_metadata_stale(ticker)
        
        # Fetch price (always fresh)
        price_data = await self.get_stock_price(ticker)
        if not price_data:
            return None
        
        # Get metadata (from cache or fetch)
        if needs_metadata_refresh:
            metadata = await self.get_stock_metadata(ticker)
            if metadata and save_to_db:
                await self.repository.save_stock_metadata(metadata)
        else:
            # Use cached metadata
            cached_metadata = await self.repository.get_stock_metadata(ticker)
            if cached_metadata:
                metadata = {
                    "ticker": cached_metadata.ticker,
                    "name": cached_metadata.name,
                    "short_name": cached_metadata.short_name,
                    "sector": cached_metadata.sector,
                    "industry": cached_metadata.industry,
                    "market_cap": cached_metadata.market_cap,
                    "currency": cached_metadata.currency,
                    "exchange": cached_metadata.exchange,
                    "country": cached_metadata.country,
                    "website": cached_metadata.website,
                    "description": cached_metadata.description,
                }
            else:
                # Metadata not in cache, fetch it
                metadata = await self.get_stock_metadata(ticker)
                if metadata and save_to_db:
                    await self.repository.save_stock_metadata(metadata)
        
        # Save price data
        if price_data and save_to_db:
            await self.repository.save_stock_price(price_data)
        
        if not metadata:
            return None
        
        return {**metadata, **price_data}
    
    async def get_multiple_stocks(self, tickers: List[str]) -> List[Dict]:
        """
        Get stock information for multiple tickers concurrently.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            List of stock info dictionaries
        """
        tasks = [self.get_stock_info(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
    
    async def get_stock_history(self, ticker: str, period: str = "1mo") -> Optional[Dict]:
        """
        Get historical stock data.
        
        Args:
            ticker: Stock ticker symbol
            period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            
        Returns:
            Dictionary with historical data
        """
        try:
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            history = await loop.run_in_executor(None, lambda: stock.history(period=period))
            
            return {
                "ticker": ticker,
                "period": period,
                "data": history.to_dict('records') if not history.empty else []
            }
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return None


# Singleton instance
stock_fetcher = StockFetcher()

# For backwards compatibility with old code
stock_service = stock_fetcher
