"""
Famous Investor Portfolio Models.

Stores portfolio holdings for famous investors (Buffett, Dalio, etc.)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import Document
from pymongo import IndexModel


class InvestorHolding:
    """Individual holding within a portfolio."""
    ticker: str
    company: str
    shares: int
    value_usd: float
    weight_pct: float
    sector: str
    industry: Optional[str] = None


class FamousInvestorPortfolio(Document):
    """
    Famous investor portfolio holdings.
    
    Stores publicly available portfolio data from SEC 13F filings,
    annual reports, or other public sources.
    """
    
    investor_id: str  # Unique identifier (e.g., "warren_buffett")
    investor_name: str  # Display name (e.g., "Warren Buffett")
    entity_name: str  # Company/fund name (e.g., "Berkshire Hathaway Inc.")
    entity_cik: Optional[str] = None  # SEC CIK number for 13F lookups
    
    investment_style: str  # "Value", "Growth", "Macro", etc.
    description: Optional[str] = None  # Brief bio/strategy description
    
    filing_date: datetime  # Date of portfolio snapshot
    filing_type: str  # "13F-HR", "Annual Report", "Manual", etc.
    data_source: str  # "SEC EDGAR", "Manual", "Scraped", etc.
    
    total_portfolio_value: float  # Total AUM in USD
    num_holdings: int  # Total number of positions
    
    holdings: List[Dict[str, Any]]  # List of individual holdings
    # Each holding: {ticker, company, shares, value_usd, weight_pct, sector, industry}
    
    top_holdings: List[str]  # List of top 10 ticker symbols
    
    sector_allocation: Dict[str, float]  # Sector breakdown (sector -> weight_pct)
    
    last_updated: datetime
    
    class Settings:
        name = "famous_investor_portfolios"
        indexes = [
            IndexModel([("investor_id", 1), ("filing_date", -1)]),
            IndexModel([("investor_name", 1)]),
            IndexModel([("entity_name", 1)]),
            IndexModel([("filing_date", -1)]),
            IndexModel([("investor_id", 1)], unique=True)  # One portfolio per investor for now
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "investor_id": "warren_buffett",
                "investor_name": "Warren Buffett",
                "entity_name": "Berkshire Hathaway Inc.",
                "entity_cik": "0001067983",
                "investment_style": "Value Investing",
                "description": "Long-term value investor focused on quality businesses",
                "filing_date": "2025-09-30T00:00:00Z",
                "filing_type": "13F-HR",
                "data_source": "SEC EDGAR",
                "total_portfolio_value": 558000000000,
                "num_holdings": 45,
                "holdings": [
                    {
                        "ticker": "AAPL",
                        "company": "Apple Inc.",
                        "shares": 915560382,
                        "value_usd": 174000000000,
                        "weight_pct": 31.2,
                        "sector": "Technology",
                        "industry": "Consumer Electronics"
                    }
                ],
                "top_holdings": ["AAPL", "BAC", "AXP", "KO", "CVX"],
                "sector_allocation": {
                    "Technology": 31.2,
                    "Financials": 28.5,
                    "Consumer Staples": 15.3
                },
                "last_updated": "2025-11-23T00:00:00Z"
            }
        }
