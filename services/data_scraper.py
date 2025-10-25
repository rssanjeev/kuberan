"""
Stock data scraping services.
"""
from typing import Optional, Dict, Any
import yfinance as yf
from models.stock import StockData







class YahooFinanceScraper:
    """Yahoo Finance data provider using yfinance library."""

    def scrape(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get stock data from Yahoo Finance using yfinance library."""
        data = {}

        try:
            # Create yfinance ticker object
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get dividend yield
            if 'dividendYield' in info and info['dividendYield']:
                data["yield"] = float(info['dividendYield'])
            elif 'trailingAnnualDividendYield' in info and info['trailingAnnualDividendYield']:
                data["yield"] = float(info['trailingAnnualDividendYield'])
            
            # Get dividend per share (annual)
            if 'dividendRate' in info and info['dividendRate']:
                data["dividend"] = float(info['dividendRate'])
            elif 'trailingAnnualDividendRate' in info and info['trailingAnnualDividendRate']:
                data["dividend"] = float(info['trailingAnnualDividendRate'])
            
            # Get ex-dividend date
            if 'exDividendDate' in info and info['exDividendDate']:
                data["ex_dividend_date"] = str(info['exDividendDate'])
            
            # Get additional useful data
            if 'longName' in info and info['longName']:
                data["name"] = info['longName']
            elif 'shortName' in info and info['shortName']:
                data["name"] = info['shortName']

        except Exception as e:
            print(f"Error getting {ticker} data from yfinance: {e}")
            return None

        return data


class StockDataService:
    """Service for retrieving stock data with fallback scrapers."""

    def __init__(self):
        """Initialize service with Yahoo Finance provider."""
        self.yahoo_scraper = YahooFinanceScraper()



    def get_stock_data(self, ticker: str) -> Optional[StockData]:
        """
        Get stock data for a given ticker.

        Args:
            ticker: Stock/ETF ticker symbol

        Returns:
            StockData object with financial information
        """
        # Get data from Yahoo Finance
        yahoo_data = self.yahoo_scraper.scrape(ticker)
        
        if not yahoo_data:
            print(f"Warning: No data available for {ticker}")
            return None
        
        return StockData(
            ticker=ticker,
            price=0.0,  # Price will be set elsewhere
            dividend_yield=yahoo_data.get("yield", 0.0),
            annual_dividend=yahoo_data.get("dividend", 0.0),
            dividend_growth=0.05,  # Default 5% growth
            ex_date=yahoo_data.get("ex_dividend_date")
        )
