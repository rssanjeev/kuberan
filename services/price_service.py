"""
Simple price service for getting current stock prices.
"""
import yfinance as yf
from typing import Optional


class PriceService:
    """Service for retrieving current stock prices."""

    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
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