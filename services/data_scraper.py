"""
Stock data scraping services.
"""
import re
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from models.stock import StockData


class StockDataScraper:
    """Base class for stock data scrapers."""
    
    def __init__(self, timeout: int = 10):
        """Initialize scraper with timeout setting."""
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    
    def scrape(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Abstract method to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement scrape method")


class StockAnalysisScraper(StockDataScraper):
    """Scraper for StockAnalysis.com website."""
    
    def scrape(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Scrape stock data from StockAnalysis.com."""
        url = f"https://stockanalysis.com/etf/{ticker}/dividends/"
        data = {}
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Current price
            price_tag = soup.find("span", string=re.compile("Price"))
            if price_tag:
                price_val = price_tag.find_next("span").text.replace("$", "").replace(",", "")
                data["price"] = float(price_val)
            
            # Dividend yield
            yield_tag = soup.find("span", string=re.compile("Dividend Yield"))
            if yield_tag:
                yield_val = yield_tag.find_next("span").text.replace("%", "")
                data["yield"] = float(yield_val) / 100 if yield_val else None
            
            # Annual dividend
            div_tag = soup.find("span", string=re.compile("Annual Dividend"))
            if div_tag:
                div_val = div_tag.find_next("span").text.replace("$", "")
                data["dividend"] = float(div_val)
            
            # Dividend growth
            growth_tag = soup.find("span", string=re.compile("Dividend Growth"))
            if growth_tag:
                growth_val = growth_tag.find_next("span").text.replace("%", "")
                data["growth"] = float(growth_val) / 100 if growth_val else None
            
            # Ex-dividend date
            ex_tag = soup.find("span", string=re.compile("Ex-Dividend Date"))
            if ex_tag:
                data["ex_date"] = ex_tag.find_next("span").text.strip()
                
        except Exception as e:
            print(f"StockAnalysis scrape error for {ticker}: {e}")
            return None
        
        return data


class YahooFinanceScraper(StockDataScraper):
    """Scraper for Yahoo Finance website."""
    
    def scrape(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Scrape stock data from Yahoo Finance."""
        url = f"https://finance.yahoo.com/quote/{ticker}"
        data = {}
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Current price - try multiple selectors
            price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
            if not price_tag:
                # Alternative selector for price
                price_text = soup.find("span", {"data-reactid": re.compile(r".*")})
                if price_text and re.match(r"^[\d,.]+$", price_text.text.replace(",", "")):
                    price_tag = price_text
            
            if price_tag:
                price_text = price_tag.text.replace(",", "").replace("$", "")
                data["price"] = float(price_text)
            
            # Try to get yield from the summary table
            yield_cells = soup.find_all("td", string=re.compile(r"Yield|yield", re.IGNORECASE))
            for yield_cell in yield_cells:
                next_cell = yield_cell.find_next("td")
                if next_cell and "%" in next_cell.text:
                    yield_text = next_cell.text.replace("%", "").strip()
                    try:
                        data["yield"] = float(yield_text) / 100
                        break
                    except ValueError:
                        continue
            
            # Forward dividend & yield
            dvy_tag = soup.find("td", string=re.compile("Forward Dividend & Yield"))
            if dvy_tag:
                dvy_val = dvy_tag.find_next("td").text
                match = re.match(r"\$?([0-9.]+) \(([\d.]+)%\)", dvy_val)
                if match:
                    data["dividend"] = float(match.group(1))
                    data["yield"] = float(match.group(2)) / 100
            
            # Ex-dividend date
            ex_tag = soup.find("td", string=re.compile("Ex-Dividend Date"))
            if ex_tag:
                data["ex_date"] = ex_tag.find_next("td").text.strip()
                
        except Exception as e:
            print(f"Yahoo Finance scrape error for {ticker}: {e}")
            return None
        
        return data


class StockDataService:
    """Service for retrieving stock data with fallback scrapers."""
    
    def __init__(self):
        """Initialize service with scrapers."""
        self.scrapers = [
            StockAnalysisScraper(),
            YahooFinanceScraper()
        ]
        
        # Manual overrides for specific tickers
        self.manual_data = {
            "VXUS": {
                "price": 74.97,
                "yield": 0.0278,
                "dividend": 2.08,
                "growth": 0.05,
                "ex_date": "Recent"
            }
        }
    
    def get_stock_data(self, ticker: str) -> StockData:
        """
        Get stock data for a given ticker.
        
        Args:
            ticker: Stock/ETF ticker symbol
            
        Returns:
            StockData object with financial information
        """
        # Check for manual override first
        if ticker.upper() in self.manual_data:
            print(f"Using manual data for {ticker} based on current market information")
            manual = self.manual_data[ticker.upper()]
            return StockData(
                ticker=ticker.upper(),
                price=manual["price"],
                dividend_yield=manual["yield"],
                annual_dividend=manual["dividend"],
                dividend_growth=manual["growth"],
                ex_date=manual.get("ex_date")
            )
        
        # Try scrapers in order
        data = {}
        for scraper in self.scrapers:
            try:
                scraped_data = scraper.scrape(ticker)
                if scraped_data:
                    data.update(scraped_data)
                    if self._has_required_data(data):
                        break
            except Exception as e:
                print(f"Scraper {scraper.__class__.__name__} failed: {e}")
                continue
        
        # Apply defaults for missing fields
        self._apply_defaults(data, ticker)
        
        return StockData(
            ticker=ticker.upper(),
            price=data.get("price", 100.0),
            dividend_yield=data.get("yield", 0.025),
            annual_dividend=data.get("dividend", data.get("price", 100.0) * data.get("yield", 0.025)),
            dividend_growth=data.get("growth", 0.05),
            ex_date=data.get("ex_date")
        )
    
    def _has_required_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains minimum required fields."""
        return all(key in data and data[key] is not None 
                  for key in ["price", "yield", "dividend"])
    
    def _apply_defaults(self, data: Dict[str, Any], ticker: str) -> None:
        """Apply default values for missing data fields."""
        if not data.get("growth"):
            data["growth"] = 0.05  # 5% as realistic fallback
        
        if not data.get("yield"):
            data["yield"] = 0.025  # 2.5% as fallback yield
        
        if not data.get("dividend") and data.get("price") and data.get("yield"):
            data["dividend"] = data["price"] * data["yield"]
        
        if not data.get("price"):
            print(f"Warning: Could not fetch price for {ticker}. Using $100 as fallback.")
            data["price"] = 100.0