"""
ETF Famous Investor Portfolio Service.

Provides portfolio data for famous investors (Buffett, Dalio, etc.)
and maps stock portfolios to ETF equivalents.

SECURITY: No sensitive data handling required - public portfolio data only.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.logging_config import get_logger
from app.models.investor import FamousInvestorPortfolio

logger = get_logger(__name__)


class ETFInvestorService:
    """
    Service for famous investor portfolio analysis.
    
    Features:
    - Search and discover famous investor portfolios
    - On-demand loading from curated data
    - Map stock portfolios to ETF equivalents
    - Portfolio mirroring with ETFs
    """
    
    # Sample investor data (will be stored in MongoDB on first load)
    SAMPLE_INVESTORS = {
        "warren_buffett": {
            "investor_id": "warren_buffett",
            "investor_name": "Warren Buffett",
            "entity_name": "Berkshire Hathaway Inc.",
            "entity_cik": "0001067983",
            "investment_style": "Value Investing",
            "description": "Long-term value investor focused on quality businesses with strong moats",
            "filing_date": datetime(2025, 9, 30),
            "filing_type": "13F-HR Q3 2025",
            "data_source": "Sample Data",
            "total_portfolio_value": 558000000000,
            "num_holdings": 45,
            "holdings": [
                {"ticker": "AAPL", "company": "Apple Inc.", "shares": 915560382, "value_usd": 174000000000, "weight_pct": 31.2, "sector": "Technology", "industry": "Consumer Electronics"},
                {"ticker": "BAC", "company": "Bank of America Corp", "shares": 1032852006, "value_usd": 35000000000, "weight_pct": 6.3, "sector": "Financials", "industry": "Banks"},
                {"ticker": "AXP", "company": "American Express Co", "shares": 151610700, "value_usd": 28500000000, "weight_pct": 5.1, "sector": "Financials", "industry": "Credit Services"},
                {"ticker": "KO", "company": "Coca-Cola Co", "shares": 400000000, "value_usd": 25200000000, "weight_pct": 4.5, "sector": "Consumer Staples", "industry": "Beverages"},
                {"ticker": "CVX", "company": "Chevron Corp", "shares": 123117925, "value_usd": 19500000000, "weight_pct": 3.5, "sector": "Energy", "industry": "Oil & Gas"},
                {"ticker": "OXY", "company": "Occidental Petroleum", "shares": 248053865, "value_usd": 15800000000, "weight_pct": 2.8, "sector": "Energy", "industry": "Oil & Gas"},
                {"ticker": "KHC", "company": "Kraft Heinz Co", "shares": 325634818, "value_usd": 11700000000, "weight_pct": 2.1, "sector": "Consumer Staples", "industry": "Packaged Foods"},
                {"ticker": "MCO", "company": "Moody's Corp", "shares": 24669778, "value_usd": 10500000000, "weight_pct": 1.9, "sector": "Financials", "industry": "Financial Services"},
                {"ticker": "V", "company": "Visa Inc", "shares": 8297460, "value_usd": 2300000000, "weight_pct": 0.4, "sector": "Financials", "industry": "Payment Processing"},
                {"ticker": "MA", "company": "Mastercard Inc", "shares": 3986648, "value_usd": 1900000000, "weight_pct": 0.3, "sector": "Financials", "industry": "Payment Processing"},
            ],
            "top_holdings": ["AAPL", "BAC", "AXP", "KO", "CVX", "OXY", "KHC", "MCO", "V", "MA"],
            "sector_allocation": {
                "Technology": 31.2,
                "Financials": 13.7,
                "Consumer Staples": 6.6,
                "Energy": 6.3,
                "Other": 42.2
            },
            "last_updated": datetime.now()
        },
        "ray_dalio": {
            "investor_id": "ray_dalio",
            "investor_name": "Ray Dalio",
            "entity_name": "Bridgewater Associates",
            "entity_cik": "0001350694",
            "investment_style": "Macro / All Weather",
            "description": "Macro investor known for All Weather portfolio strategy balancing stocks, bonds, commodities, and gold",
            "filing_date": datetime(2025, 9, 30),
            "filing_type": "13F-HR Q3 2025",
            "data_source": "Sample Data",
            "total_portfolio_value": 145000000000,
            "num_holdings": 250,
            "holdings": [
                {"ticker": "SPY", "company": "SPDR S&P 500 ETF", "shares": 45000000, "value_usd": 25000000000, "weight_pct": 17.2, "sector": "Equity Broad", "industry": "ETF"},
                {"ticker": "TLT", "company": "iShares 20+ Year Treasury Bond ETF", "shares": 110000000, "value_usd": 10500000000, "weight_pct": 7.2, "sector": "Fixed Income", "industry": "ETF"},
                {"ticker": "GLD", "company": "SPDR Gold Trust", "shares": 65000000, "value_usd": 12800000000, "weight_pct": 8.8, "sector": "Commodities", "industry": "ETF"},
                {"ticker": "EEM", "company": "iShares MSCI Emerging Markets ETF", "shares": 180000000, "value_usd": 8200000000, "weight_pct": 5.7, "sector": "International Equity", "industry": "ETF"},
                {"ticker": "VXUS", "company": "Vanguard Total International Stock", "shares": 95000000, "value_usd": 6800000000, "weight_pct": 4.7, "sector": "International Equity", "industry": "ETF"},
                {"ticker": "VWO", "company": "Vanguard FTSE Emerging Markets", "shares": 120000000, "value_usd": 5900000000, "weight_pct": 4.1, "sector": "International Equity", "industry": "ETF"},
                {"ticker": "IEF", "company": "iShares 7-10 Year Treasury Bond", "shares": 48000000, "value_usd": 5200000000, "weight_pct": 3.6, "sector": "Fixed Income", "industry": "ETF"},
                {"ticker": "PG", "company": "Procter & Gamble Co", "shares": 18500000, "value_usd": 3100000000, "weight_pct": 2.1, "sector": "Consumer Staples", "industry": "Household Products"},
                {"ticker": "JNJ", "company": "Johnson & Johnson", "shares": 16200000, "value_usd": 2800000000, "weight_pct": 1.9, "sector": "Healthcare", "industry": "Pharmaceuticals"},
                {"ticker": "KO", "company": "Coca-Cola Co", "shares": 38000000, "value_usd": 2400000000, "weight_pct": 1.7, "sector": "Consumer Staples", "industry": "Beverages"},
            ],
            "top_holdings": ["SPY", "GLD", "TLT", "EEM", "VXUS", "VWO", "IEF", "PG", "JNJ", "KO"],
            "sector_allocation": {
                "Equity Broad": 17.2,
                "Commodities": 8.8,
                "Fixed Income": 10.8,
                "International Equity": 14.5,
                "Consumer Staples": 3.8,
                "Healthcare": 1.9,
                "Other": 43.0
            },
            "last_updated": datetime.now()
        },
        "cathie_wood": {
            "investor_id": "cathie_wood",
            "investor_name": "Cathie Wood",
            "entity_name": "ARK Investment Management",
            "entity_cik": "0001579982",
            "investment_style": "Disruptive Innovation / Growth",
            "description": "Growth investor focused on disruptive innovation across genomics, fintech, AI, and technology",
            "filing_date": datetime(2025, 11, 15),
            "filing_type": "Daily Portfolio (ARKK)",
            "data_source": "Sample Data",
            "total_portfolio_value": 8500000000,
            "num_holdings": 35,
            "holdings": [
                {"ticker": "TSLA", "company": "Tesla Inc", "shares": 3500000, "value_usd": 1100000000, "weight_pct": 12.9, "sector": "Consumer Discretionary", "industry": "Automobiles"},
                {"ticker": "COIN", "company": "Coinbase Global Inc", "shares": 4200000, "value_usd": 950000000, "weight_pct": 11.2, "sector": "Financials", "industry": "Crypto Exchange"},
                {"ticker": "ROKU", "company": "Roku Inc", "shares": 10500000, "value_usd": 780000000, "weight_pct": 9.2, "sector": "Communication Services", "industry": "Streaming"},
                {"ticker": "CRSP", "company": "CRISPR Therapeutics", "shares": 8900000, "value_usd": 520000000, "weight_pct": 6.1, "sector": "Healthcare", "industry": "Biotech"},
                {"ticker": "SHOP", "company": "Shopify Inc", "shares": 6200000, "value_usd": 490000000, "weight_pct": 5.8, "sector": "Technology", "industry": "E-commerce"},
                {"ticker": "PATH", "company": "UiPath Inc", "shares": 25000000, "value_usd": 425000000, "weight_pct": 5.0, "sector": "Technology", "industry": "RPA Software"},
                {"ticker": "SQ", "company": "Block Inc", "shares": 5800000, "value_usd": 410000000, "weight_pct": 4.8, "sector": "Financials", "industry": "Fintech"},
                {"ticker": "NVTA", "company": "Invitae Corp", "shares": 42000000, "value_usd": 340000000, "weight_pct": 4.0, "sector": "Healthcare", "industry": "Genomics"},
                {"ticker": "TWLO", "company": "Twilio Inc", "shares": 4500000, "value_usd": 310000000, "weight_pct": 3.6, "sector": "Technology", "industry": "Cloud Communications"},
                {"ticker": "ZM", "company": "Zoom Video Communications", "shares": 4200000, "value_usd": 295000000, "weight_pct": 3.5, "sector": "Technology", "industry": "Video Conferencing"},
            ],
            "top_holdings": ["TSLA", "COIN", "ROKU", "CRSP", "SHOP", "PATH", "SQ", "NVTA", "TWLO", "ZM"],
            "sector_allocation": {
                "Technology": 22.6,
                "Consumer Discretionary": 12.9,
                "Financials": 16.0,
                "Healthcare": 10.1,
                "Communication Services": 9.2,
                "Other": 29.2
            },
            "last_updated": datetime.now()
        },
        "bill_ackman": {
            "investor_id": "bill_ackman",
            "investor_name": "Bill Ackman",
            "entity_name": "Pershing Square Capital Management",
            "entity_cik": "0001336528",
            "investment_style": "Activist / Concentrated Value",
            "description": "Activist investor with concentrated portfolio of high-conviction positions",
            "filing_date": datetime(2025, 9, 30),
            "filing_type": "13F-HR Q3 2025",
            "data_source": "Sample Data",
            "total_portfolio_value": 12500000000,
            "num_holdings": 8,
            "holdings": [
                {"ticker": "HLT", "company": "Hilton Worldwide Holdings", "shares": 16500000, "value_usd": 3800000000, "weight_pct": 30.4, "sector": "Consumer Discretionary", "industry": "Hotels & Resorts"},
                {"ticker": "CMG", "company": "Chipotle Mexican Grill", "shares": 1450000, "value_usd": 2900000000, "weight_pct": 23.2, "sector": "Consumer Discretionary", "industry": "Restaurants"},
                {"ticker": "LOW", "company": "Lowe's Companies", "shares": 9200000, "value_usd": 2200000000, "weight_pct": 17.6, "sector": "Consumer Discretionary", "industry": "Home Improvement"},
                {"ticker": "QSR", "company": "Restaurant Brands International", "shares": 20500000, "value_usd": 1600000000, "weight_pct": 12.8, "sector": "Consumer Discretionary", "industry": "Restaurants"},
                {"ticker": "HHC", "company": "Howard Hughes Holdings", "shares": 14800000, "value_usd": 1200000000, "weight_pct": 9.6, "sector": "Real Estate", "industry": "Real Estate Development"},
                {"ticker": "DHR", "company": "Danaher Corp", "shares": 3100000, "value_usd": 800000000, "weight_pct": 6.4, "sector": "Healthcare", "industry": "Life Sciences"},
            ],
            "top_holdings": ["HLT", "CMG", "LOW", "QSR", "HHC", "DHR"],
            "sector_allocation": {
                "Consumer Discretionary": 83.2,
                "Real Estate": 9.6,
                "Healthcare": 6.4,
                "Other": 0.8
            },
            "last_updated": datetime.now()
        },
        "carl_icahn": {
            "investor_id": "carl_icahn",
            "investor_name": "Carl Icahn",
            "entity_name": "Icahn Enterprises LP",
            "entity_cik": "0000921669",
            "investment_style": "Activist / Value",
            "description": "Activist investor taking large positions to influence corporate strategy",
            "filing_date": datetime(2025, 9, 30),
            "filing_type": "13F-HR Q3 2025",
            "data_source": "Sample Data",
            "total_portfolio_value": 18200000000,
            "num_holdings": 22,
            "holdings": [
                {"ticker": "CVR", "company": "CVR Energy Inc", "shares": 71500000, "value_usd": 2800000000, "weight_pct": 15.4, "sector": "Energy", "industry": "Oil Refining"},
                {"ticker": "IEP", "company": "Icahn Enterprises LP", "shares": 145000000, "value_usd": 2500000000, "weight_pct": 13.7, "sector": "Diversified", "industry": "Conglomerate"},
                {"ticker": "OXY", "company": "Occidental Petroleum", "shares": 32800000, "value_usd": 2100000000, "weight_pct": 11.5, "sector": "Energy", "industry": "Oil & Gas"},
                {"ticker": "SWX", "company": "Southwest Gas Holdings", "shares": 14200000, "value_usd": 1050000000, "weight_pct": 5.8, "sector": "Utilities", "industry": "Gas Utilities"},
                {"ticker": "HPE", "company": "Hewlett Packard Enterprise", "shares": 52500000, "value_usd": 980000000, "weight_pct": 5.4, "sector": "Technology", "industry": "IT Services"},
                {"ticker": "XRX", "company": "Xerox Holdings Corp", "shares": 48000000, "value_usd": 720000000, "weight_pct": 4.0, "sector": "Technology", "industry": "Business Equipment"},
            ],
            "top_holdings": ["CVR", "IEP", "OXY", "SWX", "HPE", "XRX"],
            "sector_allocation": {
                "Energy": 26.9,
                "Diversified": 13.7,
                "Utilities": 5.8,
                "Technology": 9.4,
                "Other": 44.2
            },
            "last_updated": datetime.now()
        },
    }
    
    # Sector to ETF mapping for portfolio mirroring
    SECTOR_TO_ETF_MAP = {
        "Technology": "XLK",  # Technology Select Sector SPDR
        "Healthcare": "XLV",  # Health Care Select Sector SPDR
        "Financials": "XLF",  # Financial Select Sector SPDR
        "Consumer Discretionary": "XLY",  # Consumer Discretionary Select Sector SPDR
        "Consumer Staples": "XLP",  # Consumer Staples Select Sector SPDR
        "Energy": "XLE",  # Energy Select Sector SPDR
        "Utilities": "XLU",  # Utilities Select Sector SPDR
        "Real Estate": "XLRE",  # Real Estate Select Sector SPDR
        "Industrials": "XLI",  # Industrial Select Sector SPDR
        "Materials": "XLB",  # Materials Select Sector SPDR
        "Communication Services": "XLC",  # Communication Services Select Sector SPDR
        "Equity Broad": "VOO",  # Vanguard S&P 500 (for broad equity)
        "Fixed Income": "AGG",  # iShares Core U.S. Aggregate Bond
        "Commodities": "GLD",  # SPDR Gold Trust
        "International Equity": "VXUS",  # Vanguard Total International Stock
        "Diversified": "VOO",  # Default to S&P 500
        "Other": "VOO",  # Default to S&P 500
    }
    
    async def get_available_investors(self) -> Dict[str, Any]:
        """
        Get list of available famous investors.
        
        Returns:
            List of investors with basic info
        """
        logger.info("Fetching available investors")
        
        try:
            # Query database for all investors
            investors = await FamousInvestorPortfolio.find_all().to_list()
            
            if not investors:
                # No investors in DB, load initial set
                logger.info("No investors in database, loading initial set")
                await self.load_initial_investors()
                investors = await FamousInvestorPortfolio.find_all().to_list()
            
            # Format response
            investor_list = [
                {
                    "investor_id": inv.investor_id,
                    "investor_name": inv.investor_name,
                    "entity_name": inv.entity_name,
                    "investment_style": inv.investment_style,
                    "total_portfolio_value": inv.total_portfolio_value,
                    "num_holdings": inv.num_holdings,
                    "filing_date": inv.filing_date.isoformat(),
                    "last_updated": inv.last_updated.isoformat()
                }
                for inv in investors
            ]
            
            result = {
                "count": len(investor_list),
                "investors": investor_list,
                "available_styles": list(set(inv["investment_style"] for inv in investor_list))
            }
            
            logger.info(
                "Available investors fetched",
                extra={"count": len(investor_list)}
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to fetch available investors",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def search_investor(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Search for investor portfolio by name (on-demand loading).
        
        Args:
            query: Investor name or entity name (e.g., "Warren Buffett")
            
        Returns:
            Complete investor portfolio with holdings
        """
        logger.info(
            "Searching for investor",
            extra={"query": query}
        )
        
        try:
            # Normalize query to investor_id
            investor_id = self._normalize_query(query)
            
            # Check database first
            portfolio = await FamousInvestorPortfolio.find_one(
                FamousInvestorPortfolio.investor_id == investor_id
            )
            
            if portfolio:
                logger.info(
                    "Investor found in cache",
                    extra={"investor_id": investor_id}
                )
                return self._format_portfolio(portfolio)
            
            # Not in DB - check if we have sample data
            logger.info(
                "Investor not in cache, loading from sample data",
                extra={"investor_id": investor_id}
            )
            
            if investor_id in self.SAMPLE_INVESTORS:
                # Load from sample data
                portfolio = await self._load_investor(investor_id)
                return self._format_portfolio(portfolio)
            
            # Not found
            raise ValueError(
                f"Investor not found: {query}. "
                f"Available investors: {', '.join(self.SAMPLE_INVESTORS.keys())}"
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Failed to search investor",
                extra={"query": query, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def mirror_with_etfs(
        self,
        investor_id: str,
        portfolio_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Mirror investor's stock portfolio with ETFs.
        
        Maps individual stocks to sector ETFs for easier replication.
        
        Args:
            investor_id: Investor identifier
            portfolio_value: Target portfolio value in USD (optional)
            
        Returns:
            ETF allocation to mirror the investor's portfolio
        """
        logger.info(
            "Mirroring portfolio with ETFs",
            extra={"investor_id": investor_id}
        )
        
        try:
            # Get investor portfolio
            portfolio = await FamousInvestorPortfolio.find_one(
                FamousInvestorPortfolio.investor_id == investor_id
            )
            
            if not portfolio:
                raise ValueError(f"Investor not found: {investor_id}")
            
            # Map sector allocations to ETFs
            etf_allocation = {}
            
            for sector, weight_pct in portfolio.sector_allocation.items():
                etf_ticker = self.SECTOR_TO_ETF_MAP.get(sector, "VOO")
                
                if etf_ticker in etf_allocation:
                    etf_allocation[etf_ticker] += weight_pct
                else:
                    etf_allocation[etf_ticker] = weight_pct
            
            # Normalize to 100%
            total_weight = sum(etf_allocation.values())
            if total_weight > 0:
                etf_allocation = {
                    ticker: round((weight / total_weight) * 100, 2)
                    for ticker, weight in etf_allocation.items()
                }
            
            # Calculate dollar amounts if portfolio value provided
            etf_positions = []
            for ticker, weight_pct in sorted(
                etf_allocation.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                position = {
                    "ticker": ticker,
                    "weight_pct": weight_pct,
                    "weight_decimal": round(weight_pct / 100, 4)
                }
                
                if portfolio_value:
                    position["dollar_amount"] = round(portfolio_value * weight_pct / 100, 2)
                
                etf_positions.append(position)
            
            result = {
                "investor": {
                    "investor_id": portfolio.investor_id,
                    "investor_name": portfolio.investor_name,
                    "investment_style": portfolio.investment_style
                },
                "original_portfolio": {
                    "total_value": portfolio.total_portfolio_value,
                    "num_holdings": portfolio.num_holdings,
                    "top_holdings": portfolio.top_holdings[:5]
                },
                "etf_allocation": etf_positions,
                "portfolio_value": portfolio_value,
                "num_etfs": len(etf_positions),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Portfolio mirrored successfully",
                extra={
                    "investor_id": investor_id,
                    "num_etfs": len(etf_positions)
                }
            )
            
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Failed to mirror portfolio",
                extra={"investor_id": investor_id, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def load_initial_investors(self) -> int:
        """
        Load initial set of famous investors into database.
        
        Returns:
            Number of investors loaded
        """
        logger.info("Loading initial investors into database")
        
        try:
            loaded_count = 0
            
            for investor_id, data in self.SAMPLE_INVESTORS.items():
                # Check if already exists
                existing = await FamousInvestorPortfolio.find_one(
                    FamousInvestorPortfolio.investor_id == investor_id
                )
                
                if existing:
                    logger.info(
                        "Investor already exists, skipping",
                        extra={"investor_id": investor_id}
                    )
                    continue
                
                # Create portfolio document
                portfolio = FamousInvestorPortfolio(**data)
                await portfolio.insert()
                
                loaded_count += 1
                logger.info(
                    "Loaded investor",
                    extra={"investor_id": investor_id}
                )
            
            logger.info(
                "Initial investors loaded",
                extra={"count": loaded_count}
            )
            
            return loaded_count
            
        except Exception as e:
            logger.error(
                "Failed to load initial investors",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    # -------------------- Helper Methods --------------------
    
    def _normalize_query(self, query: str) -> str:
        """Normalize investor name query to investor_id."""
        query_lower = query.lower().strip()
        
        # Direct match
        if query_lower in self.SAMPLE_INVESTORS:
            return query_lower
        
        # Try matching by investor name
        for investor_id, data in self.SAMPLE_INVESTORS.items():
            if query_lower in data["investor_name"].lower():
                return investor_id
            if query_lower in data["entity_name"].lower():
                return investor_id
        
        # Try fuzzy match (e.g., "buffett" -> "warren_buffett")
        for investor_id in self.SAMPLE_INVESTORS.keys():
            if query_lower in investor_id:
                return investor_id
        
        # Return as-is (will fail later if not found)
        return query_lower.replace(" ", "_")
    
    async def _load_investor(self, investor_id: str) -> FamousInvestorPortfolio:
        """Load investor from sample data into database."""
        if investor_id not in self.SAMPLE_INVESTORS:
            raise ValueError(f"No sample data for investor: {investor_id}")
        
        data = self.SAMPLE_INVESTORS[investor_id]
        portfolio = FamousInvestorPortfolio(**data)
        await portfolio.insert()
        
        logger.info(
            "Loaded investor into database",
            extra={"investor_id": investor_id}
        )
        
        return portfolio
    
    def _format_portfolio(self, portfolio: FamousInvestorPortfolio) -> Dict[str, Any]:
        """Format portfolio document for API response."""
        return {
            "investor": {
                "investor_id": portfolio.investor_id,
                "investor_name": portfolio.investor_name,
                "entity_name": portfolio.entity_name,
                "entity_cik": portfolio.entity_cik,
                "investment_style": portfolio.investment_style,
                "description": portfolio.description
            },
            "portfolio": {
                "filing_date": portfolio.filing_date.isoformat(),
                "filing_type": portfolio.filing_type,
                "data_source": portfolio.data_source,
                "total_portfolio_value": portfolio.total_portfolio_value,
                "num_holdings": portfolio.num_holdings
            },
            "holdings": portfolio.holdings,
            "top_holdings": portfolio.top_holdings,
            "sector_allocation": portfolio.sector_allocation,
            "last_updated": portfolio.last_updated.isoformat()
        }


# Singleton instance
etf_investor_service = ETFInvestorService()
