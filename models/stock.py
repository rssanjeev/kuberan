"""
Stock data model and related functionality.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class StockData:
    """Data class representing stock/ETF financial information."""
    
    ticker: str
    price: float
    dividend_yield: float
    annual_dividend: float
    dividend_growth: float
    ex_date: Optional[str] = None
    
    @property
    def quarterly_dividend(self) -> float:
        """Calculate quarterly dividend amount."""
        return self.annual_dividend / 4
    
    @property
    def quarterly_growth_rate(self) -> float:
        """Calculate quarterly compounded growth rate."""
        return (1 + self.dividend_growth) ** (1/4) - 1
    
    def __str__(self) -> str:
        """String representation of stock data."""
        return (f"StockData(ticker={self.ticker}, price=${self.price:.2f}, "
                f"yield={self.dividend_yield:.2%}, dividend=${self.annual_dividend:.2f})")