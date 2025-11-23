"""
ETF Total Cost of Ownership (TCO) Service

Calculate true ownership costs for ETF comparison beyond just expense ratios.
Includes bid/ask spreads, trading commissions, and total cost over time.

Phase 6: Total Cost of Ownership Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.logging_config import get_logger
from app.services.providers.provider_manager import provider_manager
from app.services.etf.etf_profile_service import etf_profile_service

logger = get_logger(__name__)


class ETFTCOService:
    """
    Calculate Total Cost of Ownership (TCO) for ETFs.
    
    TCO Components:
    1. Expense Ratio: Annual management fee
    2. Bid/Ask Spread: Cost of buying and selling
    3. Trading Commission: Broker fees (usually $0 now)
    
    TCO Formula:
    TCO = (expense_ratio × holding_period) + (bid_ask_spread × 2) + (commission × 2)
    
    Why This Matters:
    - SPY: 0.09% expense ratio, wider spread (~0.01%)
    - VOO: 0.03% expense ratio, tighter spread (~0.01%)
    - Over 10 years, this difference compounds significantly
    """
    
    # Default values
    DEFAULT_COMMISSION = 0.0  # Most brokers now offer $0 commissions
    DEFAULT_SPREAD_ESTIMATE = 0.01  # 1 basis point (0.01%) - conservative estimate
    
    def __init__(self):
        self.logger = logger
    
    async def calculate_tco(
        self,
        ticker: str,
        holding_period_years: float = 1.0,
        commission: float = DEFAULT_COMMISSION,
        investment_amount: float = 10000.0,
        use_cached_spread: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate Total Cost of Ownership for a single ETF.
        
        Args:
            ticker: ETF ticker symbol
            holding_period_years: How long you'll hold (1, 3, 5, 10 years)
            commission: Trading commission per trade (default: $0)
            investment_amount: Investment size for dollar cost calculation
            use_cached_spread: Use cached spread data if available
        
        Returns:
            {
                "ticker": "SPY",
                "holding_period_years": 5,
                "components": {
                    "expense_ratio_pct": 0.09,
                    "expense_ratio_cost": 45.00,
                    "bid_ask_spread_pct": 0.01,
                    "bid_ask_spread_cost": 2.00,
                    "commission_per_trade": 0.00,
                    "commission_total": 0.00
                },
                "total_cost": 47.00,
                "total_cost_pct": 0.47,
                "investment_amount": 10000,
                "calculation_timestamp": "2025-11-23T..."
            }
        """
        try:
            self.logger.info(
                "Calculating TCO",
                extra={
                    "ticker": ticker,
                    "holding_period": holding_period_years,
                    "investment": investment_amount
                }
            )
            
            # Validate inputs
            ticker = ticker.upper().strip()
            if not ticker or len(ticker) > 5:
                raise ValueError(f"Invalid ticker: {ticker}")
            
            if holding_period_years <= 0 or holding_period_years > 50:
                raise ValueError(f"Invalid holding period: {holding_period_years}. Must be 0-50 years.")
            
            if investment_amount <= 0:
                raise ValueError(f"Invalid investment amount: {investment_amount}")
            
            # Get ETF profile from cache (uses database, no API call)
            profile = await etf_profile_service.get_etf_profile(ticker)
            
            if not profile or 'fundamentals' not in profile:
                raise ValueError(f"ETF profile not found for {ticker}. Please fetch it first.")
            
            # Extract expense ratio from cached profile
            fundamentals = profile['fundamentals']
            expense_ratio = fundamentals.get('net_expense_ratio', 0) * 100  # Convert to percentage
            
            if expense_ratio == 0:
                # Fallback to expense_ratio_pct if available
                expense_ratio = fundamentals.get('expense_ratio_pct', 0.10)  # Default 0.10%
            
            # Estimate spread from net assets (no API call needed)
            net_assets = fundamentals.get('net_assets', 0)
            spread_pct = self._estimate_spread_from_aum(ticker, net_assets)
            
            # Calculate costs
            # 1. Expense ratio cost (annual fee × holding period)
            expense_cost = investment_amount * (expense_ratio / 100) * holding_period_years
            
            # 2. Bid/Ask spread cost (pay spread on buy AND sell)
            spread_cost = investment_amount * (spread_pct / 100) * 2  # Buy + sell
            
            # 3. Commission cost (pay commission on buy AND sell)
            commission_total = commission * 2
            
            # Total cost
            total_cost = expense_cost + spread_cost + commission_total
            total_cost_pct = (total_cost / investment_amount) * 100
            
            result = {
                "ticker": ticker,
                "holding_period_years": holding_period_years,
                "components": {
                    "expense_ratio_pct": round(expense_ratio, 4),
                    "expense_ratio_cost": round(expense_cost, 2),
                    "bid_ask_spread_pct": round(spread_pct, 4),
                    "bid_ask_spread_cost": round(spread_cost, 2),
                    "commission_per_trade": round(commission, 2),
                    "commission_total": round(commission_total, 2)
                },
                "total_cost": round(total_cost, 2),
                "total_cost_pct": round(total_cost_pct, 4),
                "investment_amount": investment_amount,
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(
                "TCO calculated",
                extra={
                    "ticker": ticker,
                    "total_cost": total_cost,
                    "total_cost_pct": total_cost_pct
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "TCO calculation failed",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"TCO calculation failed for {ticker}: {str(e)}")
    
    async def compare_tco(
        self,
        ticker1: str,
        ticker2: str,
        holding_period_years: float = 5.0,
        commission: float = DEFAULT_COMMISSION,
        investment_amount: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Compare Total Cost of Ownership between two ETFs.
        
        Args:
            ticker1: First ETF ticker
            ticker2: Second ETF ticker
            holding_period_years: Holding period for comparison
            commission: Trading commission per trade
            investment_amount: Investment amount for cost calculation
        
        Returns:
            {
                "ticker1": "SPY",
                "ticker2": "VOO",
                "holding_period_years": 5,
                "investment_amount": 10000,
                "tco1": {
                    "total_cost": 47.00,
                    "total_cost_pct": 0.47,
                    "components": {...}
                },
                "tco2": {
                    "total_cost": 17.00,
                    "total_cost_pct": 0.17,
                    "components": {...}
                },
                "comparison": {
                    "cost_difference": 30.00,
                    "cost_difference_pct": 0.30,
                    "savings_with_cheaper": 30.00,
                    "cheaper_etf": "VOO",
                    "cost_ratio": 2.76,
                    "explanation": "VOO is 64% cheaper than SPY over 5 years"
                },
                "calculation_timestamp": "2025-11-23T..."
            }
        """
        try:
            self.logger.info(
                "Comparing TCO",
                extra={
                    "ticker1": ticker1,
                    "ticker2": ticker2,
                    "holding_period": holding_period_years
                }
            )
            
            # Validate tickers are different
            ticker1 = ticker1.upper().strip()
            ticker2 = ticker2.upper().strip()
            
            if ticker1 == ticker2:
                raise ValueError(f"Cannot compare ETF to itself: {ticker1}")
            
            # Calculate TCO for both ETFs
            tco1 = await self.calculate_tco(
                ticker=ticker1,
                holding_period_years=holding_period_years,
                commission=commission,
                investment_amount=investment_amount
            )
            
            tco2 = await self.calculate_tco(
                ticker=ticker2,
                holding_period_years=holding_period_years,
                commission=commission,
                investment_amount=investment_amount
            )
            
            # Compare costs
            cost_diff = abs(tco1['total_cost'] - tco2['total_cost'])
            cost_diff_pct = abs(tco1['total_cost_pct'] - tco2['total_cost_pct'])
            
            cheaper_etf = ticker1 if tco1['total_cost'] < tco2['total_cost'] else ticker2
            more_expensive = ticker2 if cheaper_etf == ticker1 else ticker1
            
            cheaper_cost = min(tco1['total_cost'], tco2['total_cost'])
            expensive_cost = max(tco1['total_cost'], tco2['total_cost'])
            
            cost_ratio = expensive_cost / cheaper_cost if cheaper_cost > 0 else 1.0
            savings_pct = ((expensive_cost - cheaper_cost) / expensive_cost) * 100 if expensive_cost > 0 else 0
            
            explanation = (
                f"{cheaper_etf} is {savings_pct:.0f}% cheaper than {more_expensive} "
                f"over {holding_period_years} years"
            )
            
            result = {
                "ticker1": ticker1,
                "ticker2": ticker2,
                "holding_period_years": holding_period_years,
                "investment_amount": investment_amount,
                "tco1": {
                    "total_cost": tco1['total_cost'],
                    "total_cost_pct": tco1['total_cost_pct'],
                    "components": tco1['components']
                },
                "tco2": {
                    "total_cost": tco2['total_cost'],
                    "total_cost_pct": tco2['total_cost_pct'],
                    "components": tco2['components']
                },
                "comparison": {
                    "cost_difference": round(cost_diff, 2),
                    "cost_difference_pct": round(cost_diff_pct, 4),
                    "savings_with_cheaper": round(cost_diff, 2),
                    "cheaper_etf": cheaper_etf,
                    "cost_ratio": round(cost_ratio, 2),
                    "savings_pct": round(savings_pct, 1),
                    "explanation": explanation
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(
                "TCO comparison complete",
                extra={
                    "ticker1": ticker1,
                    "ticker2": ticker2,
                    "cheaper": cheaper_etf,
                    "savings": cost_diff
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "TCO comparison failed",
                extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"TCO comparison failed: {str(e)}")
    
    async def calculate_multi_period_tco(
        self,
        ticker: str,
        periods: List[float] = [1, 3, 5, 10],
        commission: float = DEFAULT_COMMISSION,
        investment_amount: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Calculate TCO across multiple holding periods.
        
        Args:
            ticker: ETF ticker symbol
            periods: List of holding periods in years (e.g., [1, 3, 5, 10])
            commission: Trading commission per trade
            investment_amount: Investment amount
        
        Returns:
            {
                "ticker": "SPY",
                "investment_amount": 10000,
                "periods": {
                    "1": {"total_cost": 11.00, "total_cost_pct": 0.11},
                    "3": {"total_cost": 29.00, "total_cost_pct": 0.29},
                    "5": {"total_cost": 47.00, "total_cost_pct": 0.47},
                    "10": {"total_cost": 92.00, "total_cost_pct": 0.92}
                }
            }
        """
        try:
            self.logger.info(
                "Calculating multi-period TCO",
                extra={"ticker": ticker, "periods": periods}
            )
            
            results = {}
            
            for period in periods:
                tco = await self.calculate_tco(
                    ticker=ticker,
                    holding_period_years=period,
                    commission=commission,
                    investment_amount=investment_amount
                )
                
                results[str(int(period))] = {
                    "total_cost": tco['total_cost'],
                    "total_cost_pct": tco['total_cost_pct'],
                    "expense_ratio_cost": tco['components']['expense_ratio_cost'],
                    "spread_cost": tco['components']['bid_ask_spread_cost']
                }
            
            return {
                "ticker": ticker,
                "investment_amount": investment_amount,
                "periods": results,
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(
                "Multi-period TCO calculation failed",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Multi-period TCO calculation failed: {str(e)}")
    
    # ==================== Helper Methods ====================
    
    def _extract_expense_ratio(self, raw_profile: Dict) -> float:
        """
        Extract expense ratio from Alpha Vantage ETF profile.
        
        Returns as decimal (e.g., 0.0009 for 0.09%)
        """
        try:
            # Alpha Vantage returns net_expense_ratio as decimal (0.0009 = 0.09%)
            expense_ratio = raw_profile.get('net_expense_ratio', None)
            
            if expense_ratio is None:
                self.logger.warning(
                    "Expense ratio not found in profile, using default",
                    extra={"profile_keys": list(raw_profile.keys())}
                )
                return 0.0010  # Default 0.10% if not found
            
            # Convert to decimal if it's a string
            if isinstance(expense_ratio, str):
                expense_ratio = expense_ratio.strip().rstrip('%')
                expense_ratio = float(expense_ratio) / 100  # Convert percentage to decimal
            else:
                expense_ratio = float(expense_ratio)
            
            # Alpha Vantage returns as decimal (e.g., 0.0009 for 0.09%)
            # We need percentage for display (e.g., 0.09)
            expense_ratio_pct = expense_ratio * 100
            
            self.logger.debug(
                "Extracted expense ratio",
                extra={"expense_ratio_decimal": expense_ratio, "expense_ratio_pct": expense_ratio_pct}
            )
            
            return expense_ratio_pct  # Return as percentage for calculation
            
        except Exception as e:
            self.logger.warning(
                "Failed to extract expense ratio, using default",
                extra={"error": str(e)}
            )
            return 0.10  # Default 0.10% if not found
    
    def _estimate_spread_from_aum(
        self,
        ticker: str,
        net_assets: float
    ) -> float:
        """
        Estimate bid/ask spread from ETF net assets (AUM).
        
        Larger ETFs = more liquid = tighter spreads
        This avoids API calls and is accurate enough for TCO estimates.
        
        Args:
            ticker: ETF ticker (for special cases)
            net_assets: Net assets in dollars
        
        Returns:
            Estimated spread in percentage
        """
        # Hardcoded spreads for mega-popular ETFs (most accurate)
        popular_etfs = {
            'SPY': 0.01, 'VOO': 0.01, 'IVV': 0.01,  # S&P 500
            'QQQ': 0.01, 'VTI': 0.01, 'VT': 0.01,   # Total market
            'AGG': 0.02, 'BND': 0.02, 'VXUS': 0.02, # Bonds/International
            'VNQ': 0.03, 'GLD': 0.02, 'SLV': 0.03   # Real estate/Commodities
        }
        
        if ticker in popular_etfs:
            return popular_etfs[ticker]
        
        # Estimate from AUM
        if net_assets > 100_000_000_000:  # > $100B (mega ETFs)
            spread_pct = 0.01  # 1 basis point
        elif net_assets > 10_000_000_000:  # > $10B (large ETFs)
            spread_pct = 0.02  # 2 basis points
        elif net_assets > 1_000_000_000:   # > $1B (medium ETFs)
            spread_pct = 0.03  # 3 basis points
        elif net_assets > 100_000_000:     # > $100M (small ETFs)
            spread_pct = 0.05  # 5 basis points
        else:  # < $100M (micro ETFs)
            spread_pct = 0.10  # 10 basis points
        
        self.logger.debug(
            "Estimated spread from AUM",
            extra={"ticker": ticker, "net_assets_b": net_assets / 1_000_000_000, "spread_pct": spread_pct}
        )
        
        return spread_pct
    



# Singleton instance
etf_tco_service = ETFTCOService()
