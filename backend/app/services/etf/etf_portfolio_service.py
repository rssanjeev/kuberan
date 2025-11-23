"""
ETF Portfolio Builder and Analyzer Service

Create and analyze multi-ETF portfolios with allocation weights.
Calculate aggregate characteristics, diversification metrics, and optimization recommendations.

Phase 7: Portfolio Builder & Analyzer
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from app.core.logging_config import get_logger
from app.services.etf.etf_profile_service import etf_profile_service
from app.services.etf.etf_tco_service import etf_tco_service
from app.services.etf.etf_performance_service import etf_performance_service

logger = get_logger(__name__)


class ETFPortfolioService:
    """
    Build and analyze ETF portfolios.
    
    Features:
    1. Create portfolios with multiple ETFs and allocation weights
    2. Analyze aggregate characteristics (expense ratio, sector allocation)
    3. Calculate portfolio TCO and performance
    4. Assess diversification quality
    5. Generate rebalancing recommendations
    6. Compare portfolio alternatives
    
    Use Cases:
    - "Build a 60/40 stocks/bonds portfolio"
    - "Analyze my 3-fund portfolio diversification"
    - "Should I rebalance my portfolio?"
    - "Compare my portfolio vs a target allocation"
    """
    
    def __init__(self):
        self.logger = logger
    
    async def create_portfolio(
        self,
        name: str,
        holdings: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a portfolio with ETF holdings and allocation weights.
        
        Args:
            name: Portfolio name (e.g., "Aggressive Growth", "3-Fund Portfolio")
            holdings: List of holdings with ticker and weight
                [
                    {"ticker": "VTI", "weight": 60.0},
                    {"ticker": "VXUS", "weight": 30.0},
                    {"ticker": "BND", "weight": 10.0}
                ]
            description: Optional portfolio description
        
        Returns:
            {
                "portfolio_id": "uuid",
                "name": "3-Fund Portfolio",
                "description": "Total market portfolio",
                "holdings": [
                    {
                        "ticker": "VTI",
                        "weight": 60.0,
                        "name": "Vanguard Total Stock Market ETF"
                    }
                ],
                "total_weight": 100.0,
                "etf_count": 3,
                "created_at": "2025-11-23T..."
            }
        """
        try:
            self.logger.info(
                "Creating portfolio",
                extra={"portfolio_name": name, "etf_count": len(holdings)}
            )
            
            # Validate inputs
            if not name or not name.strip():
                raise ValueError("Portfolio name is required")
            
            if not holdings or len(holdings) == 0:
                raise ValueError("At least one holding is required")
            
            if len(holdings) > 50:
                raise ValueError("Maximum 50 ETFs per portfolio")
            
            # Validate and normalize holdings
            validated_holdings = []
            total_weight = 0.0
            seen_tickers = set()
            
            for holding in holdings:
                ticker = holding.get('ticker', '').upper().strip()
                weight = float(holding.get('weight', 0))
                
                if not ticker:
                    raise ValueError("Ticker is required for each holding")
                
                if ticker in seen_tickers:
                    raise ValueError(f"Duplicate ticker: {ticker}")
                
                if weight < 0 or weight > 100:
                    raise ValueError(f"Weight must be 0-100%: {ticker} has {weight}%")
                
                seen_tickers.add(ticker)
                total_weight += weight
                
                # Fetch ETF name for display
                try:
                    profile = await etf_profile_service.get_etf_profile(ticker)
                    etf_name = profile['name']
                except Exception as e:
                    self.logger.warning(
                        "Failed to fetch ETF name",
                        extra={"ticker": ticker, "error": str(e)}
                    )
                    etf_name = ticker
                
                validated_holdings.append({
                    "ticker": ticker,
                    "weight": round(weight, 2),
                    "name": etf_name
                })
            
            # Validate total weight
            if abs(total_weight - 100.0) > 0.01:
                raise ValueError(
                    f"Total weight must equal 100%. Current total: {total_weight}%"
                )
            
            # Generate portfolio ID (simple timestamp-based for now)
            portfolio_id = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            portfolio = {
                "portfolio_id": portfolio_id,
                "name": name.strip(),
                "description": description.strip() if description else None,
                "holdings": validated_holdings,
                "total_weight": round(total_weight, 2),
                "etf_count": len(validated_holdings),
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(
                "Portfolio created",
                extra={
                    "portfolio_id": portfolio_id,
                    "portfolio_name": name,
                    "etf_count": len(validated_holdings)
                }
            )
            
            return portfolio
            
        except Exception as e:
            self.logger.error(
                "Portfolio creation failed",
                extra={"portfolio_name": name, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Portfolio creation failed: {str(e)}")
    
    async def analyze_portfolio(
        self,
        holdings: List[Dict[str, Any]],
        investment_amount: float = 10000.0,
        holding_period_years: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze portfolio characteristics and metrics.
        
        Calculates:
        - Weighted expense ratio
        - Portfolio TCO
        - Sector allocation (diversification)
        - Geographic exposure
        - Asset class breakdown
        - Risk metrics (if available)
        
        Args:
            holdings: List of {"ticker": "VTI", "weight": 60.0}
            investment_amount: Portfolio value for cost calculations
            holding_period_years: Time horizon for TCO calculation
        
        Returns:
            {
                "aggregate_metrics": {
                    "weighted_expense_ratio": 0.05,
                    "portfolio_tco": 25.50,
                    "portfolio_tco_pct": 0.26
                },
                "diversification": {
                    "sector_allocation": {"Technology": 25.5, "Healthcare": 15.2},
                    "geographic_exposure": {"US": 70.0, "International": 30.0},
                    "asset_class": {"Equity": 90.0, "Fixed Income": 10.0}
                },
                "holdings_detail": [
                    {
                        "ticker": "VTI",
                        "weight": 60.0,
                        "expense_ratio": 0.03,
                        "contribution_to_portfolio_er": 0.018
                    }
                ],
                "quality_score": 85,
                "recommendations": [
                    "Portfolio is well-diversified across sectors",
                    "Consider adding international bonds for diversification"
                ]
            }
        """
        try:
            self.logger.info(
                "Analyzing portfolio",
                extra={
                    "etf_count": len(holdings),
                    "investment": investment_amount
                }
            )
            
            # Fetch profiles for all ETFs
            profiles = {}
            holdings_detail = []
            
            for holding in holdings:
                ticker = holding['ticker']
                weight = holding['weight']
                
                try:
                    profile = await etf_profile_service.get_etf_profile(ticker)
                    profiles[ticker] = profile
                    
                    expense_ratio = profile['fundamentals']['net_expense_ratio'] * 100  # Convert to %
                    contribution_to_er = (weight / 100) * expense_ratio
                    
                    holdings_detail.append({
                        "ticker": ticker,
                        "name": profile['name'],
                        "weight": weight,
                        "expense_ratio": round(expense_ratio, 4),
                        "contribution_to_portfolio_er": round(contribution_to_er, 4),
                        "net_assets": profile['fundamentals'].get('net_assets'),
                        "dividend_yield": profile['fundamentals'].get('dividend_yield_pct')
                    })
                    
                except Exception as e:
                    self.logger.warning(
                        "Failed to fetch ETF profile",
                        extra={"ticker": ticker, "error": str(e)}
                    )
                    # Continue with partial data
                    holdings_detail.append({
                        "ticker": ticker,
                        "weight": weight,
                        "error": f"Failed to fetch profile: {str(e)}"
                    })
            
            # Calculate weighted expense ratio
            weighted_er = sum(
                h['contribution_to_portfolio_er'] 
                for h in holdings_detail 
                if 'contribution_to_portfolio_er' in h
            )
            
            # Calculate portfolio TCO
            portfolio_tco_total = 0.0
            tco_breakdown = []
            
            for holding in holdings:
                ticker = holding['ticker']
                weight = holding['weight']
                etf_investment = investment_amount * (weight / 100)
                
                try:
                    tco = await etf_tco_service.calculate_tco(
                        ticker=ticker,
                        holding_period_years=holding_period_years,
                        investment_amount=etf_investment
                    )
                    
                    portfolio_tco_total += tco['total_cost']
                    
                    tco_breakdown.append({
                        "ticker": ticker,
                        "weight": weight,
                        "investment": etf_investment,
                        "tco_cost": tco['total_cost'],
                        "tco_pct": tco['total_cost_pct']
                    })
                    
                except Exception as e:
                    self.logger.warning(
                        "Failed to calculate TCO for ETF",
                        extra={"ticker": ticker, "error": str(e)}
                    )
            
            portfolio_tco_pct = (portfolio_tco_total / investment_amount) * 100
            
            # Aggregate sector allocation
            sector_allocation = defaultdict(float)
            geographic_exposure = defaultdict(float)
            asset_class = defaultdict(float)
            
            for holding in holdings:
                ticker = holding['ticker']
                weight = holding['weight']
                
                if ticker not in profiles:
                    continue
                
                profile = profiles[ticker]
                
                # Sector allocation
                if 'sectors' in profile:
                    for sector in profile['sectors']:
                        sector_name = sector.get('sector') or sector.get('name')
                        sector_weight = sector.get('weight', 0)
                        weighted_contribution = (weight / 100) * sector_weight
                        if sector_name:
                            sector_allocation[sector_name] += weighted_contribution
                
                # Geographic exposure (simplified - derive from ETF name/type or ticker)
                etf_name = (profile.get('name') or ticker or '').lower()
                if 'international' in etf_name or 'ex-us' in etf_name or 'world' in etf_name or \
                   ticker.lower() in ['vxus', 'ixus', 'veu', 'efa', 'iefa', 'vwo', 'eem', 'iemg']:
                    geographic_exposure['International'] += weight
                else:
                    geographic_exposure['US'] += weight
                
                # Asset class (simplified - derive from ETF name/type or ticker)
                if 'bond' in etf_name or 'fixed' in etf_name or 'treasury' in etf_name or \
                   ticker.lower() in ['bnd', 'agg', 'agz', 'biv', 'tlt', 'vgit', 'vglt']:
                    asset_class['Fixed Income'] += weight
                elif 'real estate' in etf_name or 'reit' in etf_name or ticker.lower() in ['vnq', 'vgslx', 'schh']:
                    asset_class['Real Estate'] += weight
                elif 'commodity' in etf_name or 'gold' in etf_name or ticker.lower() in ['gld', 'slv', 'dbc', 'dba']:
                    asset_class['Commodities'] += weight
                else:
                    asset_class['Equity'] += weight
            
            # Calculate diversification score (0-100)
            diversification_score = self._calculate_diversification_score(
                sector_allocation,
                len(holdings)
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                holdings_detail,
                sector_allocation,
                asset_class,
                weighted_er,
                diversification_score
            )
            
            result = {
                "aggregate_metrics": {
                    "weighted_expense_ratio": round(weighted_er, 4),
                    "portfolio_tco": round(portfolio_tco_total, 2),
                    "portfolio_tco_pct": round(portfolio_tco_pct, 4),
                    "holding_period_years": holding_period_years,
                    "investment_amount": investment_amount
                },
                "diversification": {
                    "sector_allocation": {
                        sector: round(weight, 2) 
                        for sector, weight in sorted(
                            sector_allocation.items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )
                    },
                    "geographic_exposure": {
                        region: round(weight, 2)
                        for region, weight in geographic_exposure.items()
                    },
                    "asset_class": {
                        asset: round(weight, 2)
                        for asset, weight in asset_class.items()
                    }
                },
                "holdings_detail": holdings_detail,
                "tco_breakdown": tco_breakdown,
                "quality_score": diversification_score,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(
                "Portfolio analysis complete",
                extra={
                    "etf_count": len(holdings),
                    "weighted_er": weighted_er,
                    "quality_score": diversification_score
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Portfolio analysis failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise Exception(f"Portfolio analysis failed: {str(e)}")
    
    async def calculate_rebalancing_needs(
        self,
        current_holdings: List[Dict[str, Any]],
        target_holdings: List[Dict[str, Any]],
        current_portfolio_value: float,
        rebalancing_threshold: float = 5.0
    ) -> Dict[str, Any]:
        """
        Calculate rebalancing recommendations.
        
        Compares current vs target allocations and suggests trades.
        
        Args:
            current_holdings: Current portfolio [{"ticker": "VTI", "weight": 65.0}]
            target_holdings: Target allocation [{"ticker": "VTI", "weight": 60.0}]
            current_portfolio_value: Current portfolio value
            rebalancing_threshold: Minimum drift % to trigger rebalance (default 5%)
        
        Returns:
            {
                "needs_rebalancing": true,
                "drift_analysis": [
                    {
                        "ticker": "VTI",
                        "current_weight": 65.0,
                        "target_weight": 60.0,
                        "drift": 5.0,
                        "drift_pct": 8.3,
                        "needs_action": true
                    }
                ],
                "rebalancing_trades": [
                    {
                        "ticker": "VTI",
                        "action": "SELL",
                        "amount": 500.00,
                        "shares_approx": 10
                    },
                    {
                        "ticker": "VXUS",
                        "action": "BUY",
                        "amount": 500.00,
                        "shares_approx": 15
                    }
                ],
                "estimated_cost": {
                    "commissions": 0.00,
                    "spread_cost": 10.00,
                    "total_cost": 10.00
                }
            }
        """
        try:
            self.logger.info(
                "Calculating rebalancing needs",
                extra={
                    "current_etfs": len(current_holdings),
                    "target_etfs": len(target_holdings),
                    "portfolio_value": current_portfolio_value
                }
            )
            
            # Normalize holdings into dictionaries
            current_map = {h['ticker']: h['weight'] for h in current_holdings}
            target_map = {h['ticker']: h['weight'] for h in target_holdings}
            
            # Get all unique tickers
            all_tickers = set(current_map.keys()) | set(target_map.keys())
            
            # Calculate drift for each position
            drift_analysis = []
            needs_rebalancing = False
            
            for ticker in sorted(all_tickers):
                current_weight = current_map.get(ticker, 0.0)
                target_weight = target_map.get(ticker, 0.0)
                drift = current_weight - target_weight
                drift_pct = (abs(drift) / target_weight * 100) if target_weight > 0 else 100
                
                needs_action = abs(drift) >= rebalancing_threshold
                if needs_action:
                    needs_rebalancing = True
                
                drift_analysis.append({
                    "ticker": ticker,
                    "current_weight": round(current_weight, 2),
                    "target_weight": round(target_weight, 2),
                    "drift": round(drift, 2),
                    "drift_pct": round(drift_pct, 1),
                    "needs_action": needs_action
                })
            
            # Calculate rebalancing trades
            rebalancing_trades = []
            total_spread_cost = 0.0
            
            if needs_rebalancing:
                for analysis in drift_analysis:
                    ticker = analysis['ticker']
                    drift = analysis['drift']
                    
                    if abs(drift) < rebalancing_threshold:
                        continue
                    
                    amount = abs(drift / 100 * current_portfolio_value)
                    action = "SELL" if drift > 0 else "BUY"
                    
                    # Get current price for share calculation
                    try:
                        profile = await etf_profile_service.get_etf_profile(ticker)
                        # Estimate shares (would need real-time price for accuracy)
                        shares_approx = int(amount / 100)  # Placeholder calculation
                        
                        # Estimate spread cost (0.01% for liquid ETFs)
                        spread_cost = amount * 0.0001
                        total_spread_cost += spread_cost
                        
                        rebalancing_trades.append({
                            "ticker": ticker,
                            "action": action,
                            "amount": round(amount, 2),
                            "shares_approx": shares_approx,
                            "estimated_spread_cost": round(spread_cost, 2)
                        })
                        
                    except Exception as e:
                        self.logger.warning(
                            "Failed to get price for rebalancing",
                            extra={"ticker": ticker, "error": str(e)}
                        )
            
            result = {
                "needs_rebalancing": needs_rebalancing,
                "rebalancing_threshold": rebalancing_threshold,
                "portfolio_value": current_portfolio_value,
                "drift_analysis": drift_analysis,
                "rebalancing_trades": rebalancing_trades,
                "estimated_cost": {
                    "commissions": 0.00,  # Most brokers offer $0 commissions
                    "spread_cost": round(total_spread_cost, 2),
                    "total_cost": round(total_spread_cost, 2)
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(
                "Rebalancing calculation complete",
                extra={
                    "needs_rebalancing": needs_rebalancing,
                    "trades": len(rebalancing_trades)
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Rebalancing calculation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise Exception(f"Rebalancing calculation failed: {str(e)}")
    
    async def compare_portfolios(
        self,
        portfolio1_holdings: List[Dict[str, Any]],
        portfolio2_holdings: List[Dict[str, Any]],
        portfolio1_name: str = "Portfolio 1",
        portfolio2_name: str = "Portfolio 2",
        investment_amount: float = 10000.0,
        holding_period_years: int = 5
    ) -> Dict[str, Any]:
        """
        Compare two portfolios side-by-side.
        
        Args:
            portfolio1_holdings: First portfolio holdings
            portfolio2_holdings: Second portfolio holdings
            portfolio1_name: Name for first portfolio
            portfolio2_name: Name for second portfolio
            investment_amount: Investment amount for comparison
            holding_period_years: Time horizon
        
        Returns:
            {
                "portfolio1": {...portfolio1 analysis...},
                "portfolio2": {...portfolio2 analysis...},
                "comparison": {
                    "expense_ratio_difference": -0.02,
                    "tco_difference": -15.00,
                    "diversification_difference": 5,
                    "winner": "Portfolio 2",
                    "explanation": "Portfolio 2 is cheaper and more diversified"
                }
            }
        """
        try:
            self.logger.info(
                "Comparing portfolios",
                extra={
                    "portfolio1_name": portfolio1_name,
                    "portfolio2_name": portfolio2_name
                }
            )
            
            # Analyze both portfolios
            analysis1 = await self.analyze_portfolio(
                holdings=portfolio1_holdings,
                investment_amount=investment_amount,
                holding_period_years=holding_period_years
            )
            
            analysis2 = await self.analyze_portfolio(
                holdings=portfolio2_holdings,
                investment_amount=investment_amount,
                holding_period_years=holding_period_years
            )
            
            # Compare key metrics
            er_diff = (
                analysis1['aggregate_metrics']['weighted_expense_ratio'] - 
                analysis2['aggregate_metrics']['weighted_expense_ratio']
            )
            
            tco_diff = (
                analysis1['aggregate_metrics']['portfolio_tco'] - 
                analysis2['aggregate_metrics']['portfolio_tco']
            )
            
            diversification_diff = (
                analysis1['quality_score'] - 
                analysis2['quality_score']
            )
            
            # Determine winner
            p1_score = 0
            p2_score = 0
            
            if analysis1['aggregate_metrics']['portfolio_tco'] < analysis2['aggregate_metrics']['portfolio_tco']:
                p1_score += 1
            else:
                p2_score += 1
            
            if analysis1['quality_score'] > analysis2['quality_score']:
                p1_score += 1
            else:
                p2_score += 1
            
            winner = portfolio1_name if p1_score > p2_score else portfolio2_name
            
            explanation = self._generate_comparison_explanation(
                portfolio1_name,
                portfolio2_name,
                er_diff,
                tco_diff,
                diversification_diff,
                winner
            )
            
            result = {
                "portfolio1": {
                    "name": portfolio1_name,
                    "analysis": analysis1
                },
                "portfolio2": {
                    "name": portfolio2_name,
                    "analysis": analysis2
                },
                "comparison": {
                    "expense_ratio_difference": round(er_diff, 4),
                    "tco_difference": round(tco_diff, 2),
                    "diversification_difference": round(diversification_diff, 0),
                    "winner": winner,
                    "explanation": explanation
                },
                "comparison_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(
                "Portfolio comparison complete",
                extra={
                    "winner": winner,
                    "tco_diff": tco_diff
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Portfolio comparison failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise Exception(f"Portfolio comparison failed: {str(e)}")
    
    # ==================== Helper Methods ====================
    
    def _calculate_diversification_score(
        self,
        sector_allocation: Dict[str, float],
        etf_count: int
    ) -> int:
        """
        Calculate portfolio diversification score (0-100).
        
        Factors:
        - Number of ETFs (more is better, up to a point)
        - Sector concentration (lower is better)
        - Sector count (more is better)
        """
        score = 0
        
        # ETF count score (max 30 points)
        if etf_count >= 5:
            score += 30
        elif etf_count >= 3:
            score += 20
        else:
            score += 10
        
        # Sector diversification (max 40 points)
        if sector_allocation:
            sector_count = len(sector_allocation)
            max_sector_weight = max(sector_allocation.values()) if sector_allocation else 0
            
            # More sectors is better (up to 20 points)
            if sector_count >= 8:
                score += 20
            elif sector_count >= 5:
                score += 15
            elif sector_count >= 3:
                score += 10
            else:
                score += 5
            
            # Lower concentration is better (up to 20 points)
            if max_sector_weight < 20:
                score += 20
            elif max_sector_weight < 30:
                score += 15
            elif max_sector_weight < 40:
                score += 10
            else:
                score += 5
        
        # Base quality score (30 points) - portfolio exists and is valid
        score += 30
        
        return min(score, 100)
    
    def _generate_recommendations(
        self,
        holdings_detail: List[Dict],
        sector_allocation: Dict[str, float],
        asset_class: Dict[str, float],
        weighted_er: float,
        diversification_score: int
    ) -> List[str]:
        """Generate portfolio recommendations based on analysis."""
        recommendations = []
        
        # Expense ratio recommendations
        if weighted_er > 0.20:
            recommendations.append(
                f"High expense ratio ({weighted_er:.2f}%). Consider lower-cost alternatives."
            )
        elif weighted_er < 0.10:
            recommendations.append(
                f"Excellent low-cost portfolio ({weighted_er:.2f}%)."
            )
        
        # Diversification recommendations
        if diversification_score >= 80:
            recommendations.append("Portfolio is well-diversified across sectors and assets.")
        elif diversification_score >= 60:
            recommendations.append("Portfolio has moderate diversification. Consider adding more sectors.")
        else:
            recommendations.append("Portfolio lacks diversification. Consider adding more ETFs or sectors.")
        
        # Sector concentration
        if sector_allocation:
            max_sector = max(sector_allocation.items(), key=lambda x: x[1])
            if max_sector[1] > 40:
                recommendations.append(
                    f"High concentration in {max_sector[0]} ({max_sector[1]:.1f}%). Consider diversifying."
                )
        
        # Asset class recommendations
        equity_pct = asset_class.get('Equity', 0)
        bond_pct = asset_class.get('Fixed Income', 0)
        
        if equity_pct > 90:
            recommendations.append(
                "Aggressive allocation (>90% equity). Consider adding bonds for stability."
            )
        elif equity_pct < 40:
            recommendations.append(
                "Conservative allocation (<40% equity). Consider adding equities for growth."
            )
        
        if not recommendations:
            recommendations.append("Portfolio is well-balanced and optimized.")
        
        return recommendations
    
    def _generate_comparison_explanation(
        self,
        name1: str,
        name2: str,
        er_diff: float,
        tco_diff: float,
        div_diff: float,
        winner: str
    ) -> str:
        """Generate human-readable comparison explanation."""
        parts = []
        
        if abs(tco_diff) > 5:
            cheaper = name1 if tco_diff > 0 else name2
            savings = abs(tco_diff)
            parts.append(f"{cheaper} is ${savings:.2f} cheaper")
        
        if abs(div_diff) > 10:
            more_diversified = name1 if div_diff > 0 else name2
            parts.append(f"{more_diversified} is more diversified")
        
        if abs(er_diff) > 0.05:
            lower_cost = name1 if er_diff > 0 else name2
            parts.append(f"{lower_cost} has lower fees")
        
        if parts:
            return f"{winner} wins: " + ", ".join(parts)
        else:
            return f"{winner} is marginally better overall"


# Singleton instance
etf_portfolio_service = ETFPortfolioService()
