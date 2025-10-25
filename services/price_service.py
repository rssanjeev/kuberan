"""
Simple price service for getting current stock prices.
"""
import asyncio
import yfinance as yf
from typing import Optional


class PriceService:
    """Service for retrieving current stock prices."""

    async def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            # Run yfinance call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            stock = yf.Ticker(ticker)
            info = await loop.run_in_executor(None, lambda: stock.info)
            
            # Try different price fields
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                return float(info['regularMarketPrice'])
            elif 'currentPrice' in info and info['currentPrice']:
                return float(info['currentPrice'])
            elif 'previousClose' in info and info['previousClose']:
                return float(info['previousClose'])
                
        except Exception as e:
            print(f"Error getting price for {ticker}: {e}")
            
        return None