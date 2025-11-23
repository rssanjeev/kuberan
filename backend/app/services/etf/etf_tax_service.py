"""
ETF Tax Optimization Service

Tax-efficient investing strategies:
- Tax-loss harvesting opportunities
- Capital gains estimation and tracking
- Tax-efficient fund alternatives
- Wash sale rule compliance

Phase: 9 of 15
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository
from app.repositories.provider_repository import provider_repository
from app.services.etf.etf_profile_service import etf_profile_service
from app.services.etf.etf_performance_service import etf_performance_service
from app.services.etf.etf_comparison_service import etf_comparison_service
from app.services.etf.etf_screening_service import etf_screening_service

logger = get_logger(__name__)


class ETFTaxService:
    """
    Service for ETF tax optimization and planning.
    
    Provides:
    - Tax-loss harvesting opportunities
    - Capital gains/loss estimation
    - Tax-efficient alternative recommendations
    - Wash sale rule compliance checking
    """
    
    # IRS wash sale rule: 30 days before and after sale
    WASH_SALE_DAYS = 30
    
    # Tax rates (2025 federal long-term capital gains)
    TAX_RATES = {
        'short_term': 0.37,  # Ordinary income (top bracket)
        'long_term': 0.20,   # Long-term cap gains (top bracket)
        'qualified_dividends': 0.20
    }
    
    def __init__(self):
        """Initialize tax service."""
        pass
    
    async def find_tax_loss_harvest_pairs(
        self,
        holdings: str,
        loss_threshold: float = 500.0,
        correlation_min: float = 0.90
    ) -> Dict[str, Any]:
        """
        Identify tax-loss harvesting opportunities in portfolio.
        
        Tax-loss harvesting: Sell losing positions to realize losses for tax
        deduction, then buy similar (but not identical) ETFs to maintain exposure.
        
        Must comply with IRS wash sale rule: Cannot buy substantially identical
        security 30 days before or after sale.
        
        Args:
            holdings: Comma-separated holdings with purchase info
                     Format: "TICKER:SHARES:COST_BASIS" (e.g., "VOO:100:40000")
            loss_threshold: Minimum loss to consider harvesting (default: $500)
            correlation_min: Minimum correlation for replacement ETFs (default: 0.90)
            
        Returns:
            Harvesting opportunities with replacement suggestions
            
        Example:
            >>> pairs = await find_tax_loss_harvest_pairs("VOO:100:42000,VTI:50:12000")
            >>> print(pairs['opportunities'][0])
            {
                "current_etf": "VOO",
                "shares": 100,
                "cost_basis": 42000,
                "current_value": 40000,
                "unrealized_loss": -2000,
                "tax_savings": 740,  # At 37% short-term rate
                "replacements": [
                    {
                        "ticker": "IVV",
                        "name": "iShares Core S&P 500",
                        "correlation": 0.995,
                        "expense_ratio": 0.0003,
                        "reason": "Tracks same index with different structure"
                    }
                ]
            }
        """
        # Parse holdings
        parsed_holdings = self._parse_holdings_with_basis(holdings)
        
        if loss_threshold < 0:
            raise ValueError("Loss threshold must be positive")
        
        if correlation_min < 0 or correlation_min > 1:
            raise ValueError("Correlation must be between 0 and 1")
        
        logger.info(
            "Finding tax-loss harvest opportunities",
            extra={
                "holding_count": len(parsed_holdings),
                "loss_threshold": loss_threshold,
                "correlation_min": correlation_min
            }
        )
        
        try:
            opportunities = []
            total_harvestable_loss = 0
            total_tax_savings = 0
            
            for ticker, holding_info in parsed_holdings.items():
                # Get current price from provider_repository
                latest_quote = await provider_repository.get_latest_quote(ticker)
                
                if not latest_quote or not latest_quote.price:
                    logger.warning(
                        "Could not get current price",
                        extra={"ticker": ticker}
                    )
                    continue
                
                current_price = latest_quote.price
                
                # Calculate unrealized gain/loss
                shares = holding_info['shares']
                cost_basis = holding_info['cost_basis']
                current_value = shares * current_price
                unrealized_gain_loss = current_value - cost_basis
                
                # Only process losses above threshold
                if unrealized_gain_loss >= -loss_threshold:
                    continue
                
                # Determine holding period (assume short-term if not specified)
                holding_period_days = holding_info.get('holding_period_days', 180)
                is_long_term = holding_period_days > 365
                
                # Calculate tax savings
                tax_rate = self.TAX_RATES['long_term'] if is_long_term else self.TAX_RATES['short_term']
                tax_savings = abs(unrealized_gain_loss) * tax_rate
                
                # Find replacement ETFs (similar but not identical)
                replacements = await self._find_replacement_etfs(
                    ticker,
                    correlation_min
                )
                
                # Get profile for ETF name
                profile = await etf_profile_service.get_etf_profile(ticker)
                
                opportunity = {
                    "current_etf": ticker,
                    "etf_name": profile.get('name'),
                    "shares": shares,
                    "cost_basis": round(cost_basis, 2),
                    "cost_basis_per_share": round(cost_basis / shares, 2),
                    "current_price": round(current_price, 2),
                    "current_value": round(current_value, 2),
                    "unrealized_loss": round(unrealized_gain_loss, 2),
                    "loss_percentage": round((unrealized_gain_loss / cost_basis) * 100, 2),
                    "holding_period": "Long-term (>1 year)" if is_long_term else "Short-term (<1 year)",
                    "applicable_tax_rate": tax_rate,
                    "estimated_tax_savings": round(tax_savings, 2),
                    "replacements": replacements[:5],  # Top 5 replacements
                    "wash_sale_warning": "Ensure 30-day wait before/after to avoid wash sale"
                }
                
                opportunities.append(opportunity)
                total_harvestable_loss += abs(unrealized_gain_loss)
                total_tax_savings += tax_savings
            
            # Sort by tax savings (highest first)
            opportunities.sort(key=lambda x: x['estimated_tax_savings'], reverse=True)
            
            logger.info(
                "Tax-loss harvest opportunities identified",
                extra={
                    "opportunity_count": len(opportunities),
                    "total_tax_savings": total_tax_savings
                }
            )
            
            return {
                "opportunities": opportunities,
                "summary": {
                    "total_opportunities": len(opportunities),
                    "total_harvestable_loss": round(total_harvestable_loss, 2),
                    "estimated_total_tax_savings": round(total_tax_savings, 2),
                    "loss_threshold": loss_threshold,
                    "correlation_threshold": correlation_min
                },
                "tax_considerations": {
                    "wash_sale_rule": f"Cannot buy substantially identical security {self.WASH_SALE_DAYS} days before/after sale",
                    "short_term_rate": self.TAX_RATES['short_term'],
                    "long_term_rate": self.TAX_RATES['long_term'],
                    "annual_loss_limit": 3000,  # $3,000 annual deduction limit
                    "note": "Losses exceeding $3,000 can be carried forward to future years"
                },
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to find tax-loss harvest opportunities",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def estimate_capital_gains(
        self,
        holdings: str,
        sell_percentage: float = 100.0
    ) -> Dict[str, Any]:
        """
        Estimate capital gains/losses if positions were sold today.
        
        Helps plan tax liability and optimize selling strategy.
        
        Args:
            holdings: Comma-separated holdings with purchase info
                     Format: "TICKER:SHARES:COST_BASIS:PURCHASE_DATE"
                     (e.g., "VOO:100:40000:2020-01-15")
            sell_percentage: Percentage of position to sell (default: 100%)
            
        Returns:
            Detailed capital gains breakdown by holding
            
        Example:
            >>> gains = await estimate_capital_gains("VOO:100:40000:2020-01-15")
            >>> print(gains['total_tax_liability'])
            1200.50  # Total estimated tax owed
        """
        if sell_percentage <= 0 or sell_percentage > 100:
            raise ValueError("Sell percentage must be between 0 and 100")
        
        parsed_holdings = self._parse_holdings_with_basis(holdings)
        
        logger.info(
            "Estimating capital gains",
            extra={
                "holding_count": len(parsed_holdings),
                "sell_percentage": sell_percentage
            }
        )
        
        try:
            holdings_analysis = []
            total_cost_basis = 0
            total_proceeds = 0
            short_term_gains = 0
            long_term_gains = 0
            
            for ticker, holding_info in parsed_holdings.items():
                # Get current price from provider_repository
                latest_quote = await provider_repository.get_latest_quote(ticker)
                
                if not latest_quote or not latest_quote.price:
                    logger.warning(
                        "Could not get current price for capital gains",
                        extra={"ticker": ticker}
                    )
                    continue
                
                current_price = latest_quote.price
                
                # Calculate gains
                shares = holding_info['shares']
                shares_to_sell = shares * (sell_percentage / 100)
                cost_basis = holding_info['cost_basis']
                cost_basis_for_sale = cost_basis * (sell_percentage / 100)
                
                proceeds = shares_to_sell * current_price
                capital_gain = proceeds - cost_basis_for_sale
                
                # Determine holding period
                holding_period_days = holding_info.get('holding_period_days', 180)
                is_long_term = holding_period_days > 365
                
                # Calculate tax
                tax_rate = self.TAX_RATES['long_term'] if is_long_term else self.TAX_RATES['short_term']
                tax_liability = max(0, capital_gain * tax_rate)  # No tax on losses
                
                # Get profile for ETF name
                profile = await etf_profile_service.get_etf_profile(ticker)
                
                holding_analysis = {
                    "ticker": ticker,
                    "etf_name": profile.get('name'),
                    "shares": shares,
                    "shares_to_sell": round(shares_to_sell, 4),
                    "cost_basis": round(cost_basis, 2),
                    "cost_basis_per_share": round(cost_basis / shares, 2),
                    "cost_basis_for_sale": round(cost_basis_for_sale, 2),
                    "current_price": round(current_price, 2),
                    "proceeds": round(proceeds, 2),
                    "capital_gain_loss": round(capital_gain, 2),
                    "gain_loss_percentage": round((capital_gain / cost_basis_for_sale) * 100, 2),
                    "holding_period": "Long-term (>1 year)" if is_long_term else "Short-term (<1 year)",
                    "holding_period_days": holding_period_days,
                    "applicable_tax_rate": tax_rate,
                    "estimated_tax": round(tax_liability, 2)
                }
                
                holdings_analysis.append(holding_analysis)
                total_cost_basis += cost_basis_for_sale
                total_proceeds += proceeds
                
                if capital_gain > 0:
                    if is_long_term:
                        long_term_gains += capital_gain
                    else:
                        short_term_gains += capital_gain
            
            # Calculate totals
            total_capital_gain = total_proceeds - total_cost_basis
            total_tax_liability = (
                short_term_gains * self.TAX_RATES['short_term'] +
                long_term_gains * self.TAX_RATES['long_term']
            )
            
            # Sort by tax liability (highest first)
            holdings_analysis.sort(key=lambda x: x['estimated_tax'], reverse=True)
            
            logger.info(
                "Capital gains estimated",
                extra={
                    "total_capital_gain": total_capital_gain,
                    "total_tax_liability": total_tax_liability
                }
            )
            
            return {
                "holdings": holdings_analysis,
                "summary": {
                    "total_cost_basis": round(total_cost_basis, 2),
                    "total_proceeds": round(total_proceeds, 2),
                    "total_capital_gain_loss": round(total_capital_gain, 2),
                    "short_term_gains": round(short_term_gains, 2),
                    "long_term_gains": round(long_term_gains, 2),
                    "estimated_total_tax": round(total_tax_liability, 2),
                    "net_after_tax": round(total_proceeds - total_tax_liability, 2),
                    "effective_tax_rate": round((total_tax_liability / total_capital_gain * 100), 2) if total_capital_gain > 0 else 0
                },
                "tax_optimization_tips": self._get_tax_optimization_tips(
                    short_term_gains,
                    long_term_gains,
                    holdings_analysis
                ),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to estimate capital gains",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_tax_efficient_alternatives(
        self,
        ticker: str,
        target_expense_ratio: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Find more tax-efficient alternatives to a given ETF.
        
        Tax efficiency factors:
        - Lower turnover (fewer taxable events)
        - Lower expense ratio (less drag on returns)
        - Qualified dividend treatment
        - Index tracking (vs active management)
        
        Args:
            ticker: Current ETF ticker
            target_expense_ratio: Maximum acceptable expense ratio (optional)
            
        Returns:
            Tax-efficient alternatives with analysis
            
        Example:
            >>> alts = await get_tax_efficient_alternatives("ARKK")
            >>> print(alts['alternatives'][0])
            {
                "ticker": "VTI",
                "name": "Vanguard Total Stock Market",
                "expense_ratio": 0.0003,
                "estimated_turnover": 4,  # 4% annual turnover
                "tax_efficiency_score": 95,
                "reason": "Lower turnover and expense ratio"
            }
        """
        ticker = ticker.upper().strip()
        
        logger.info(
            "Finding tax-efficient alternatives",
            extra={"ticker": ticker}
        )
        
        try:
            # Get current ETF profile
            current_profile = await etf_profile_service.get_etf_profile(ticker)
            current_expense_ratio = current_profile.get('fundamentals', {}).get('net_expense_ratio', 0)
            
            # Get similar ETFs using screening service
            similar_result = await etf_screening_service.find_similar_etfs(
                reference_ticker=ticker,
                limit=20
            )
            
            similar_etfs = similar_result.get('similar_etfs', [])
            
            if not similar_etfs:
                return {
                    "ticker": ticker,
                    "current_expense_ratio": current_expense_ratio,
                    "alternatives": [],
                    "note": "No similar ETFs found for comparison",
                    "calculation_timestamp": datetime.utcnow().isoformat()
                }
            
            # Analyze alternatives for tax efficiency
            alternatives = []
            for etf_dict in similar_etfs:
                etf_ticker = etf_dict.get('ticker')
                if etf_ticker == ticker:
                    continue
                
                expense_ratio = etf_dict.get('expense_ratio', 0)
                net_assets = etf_dict.get('net_assets', 0)
                etf_name = etf_dict.get('name', etf_ticker)
                category = etf_dict.get('category', '')
                
                # Skip if above target expense ratio
                if target_expense_ratio and expense_ratio > target_expense_ratio:
                    continue
                
                # Calculate tax efficiency score (0-100)
                tax_efficiency_score = self._calculate_tax_efficiency_score(
                    expense_ratio,
                    net_assets
                )
                
                # Only include if more tax-efficient than current
                current_score = self._calculate_tax_efficiency_score(
                    current_expense_ratio,
                    current_profile.get('fundamentals', {}).get('net_assets', 0)
                )
                
                if tax_efficiency_score <= current_score:
                    continue
                
                alternative = {
                    "ticker": etf_ticker,
                    "name": etf_name,
                    "expense_ratio": expense_ratio,
                    "expense_ratio_pct": round(expense_ratio * 100, 4),
                    "net_assets": net_assets,
                    "estimated_turnover": self._estimate_turnover_from_type(category),
                    "tax_efficiency_score": round(tax_efficiency_score, 2),
                    "annual_savings_per_10k": round(
                        (current_expense_ratio - expense_ratio) * 10000, 2
                    ),
                    "reason": self._get_tax_efficiency_reason(
                        current_expense_ratio,
                        expense_ratio,
                        category
                    )
                }
                
                alternatives.append(alternative)
            
            # Sort by tax efficiency score
            alternatives.sort(key=lambda x: x['tax_efficiency_score'], reverse=True)
            
            logger.info(
                "Tax-efficient alternatives found",
                extra={
                    "ticker": ticker,
                    "alternative_count": len(alternatives)
                }
            )
            
            return {
                "ticker": ticker,
                "etf_name": current_profile.get('name'),
                "current_expense_ratio": current_expense_ratio,
                "current_expense_ratio_pct": round(current_expense_ratio * 100, 4),
                "alternatives": alternatives[:10],  # Top 10
                "tax_efficiency_factors": {
                    "expense_ratio": "Lower fees = less drag on after-tax returns",
                    "turnover": "Lower turnover = fewer taxable events",
                    "fund_size": "Larger funds = better economies of scale",
                    "structure": "Index funds typically more tax-efficient than active"
                },
                "recommendation": self._get_tax_efficiency_recommendation(alternatives),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to find tax-efficient alternatives",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    # ==================== Private Helper Methods ====================
    
    def _parse_holdings_with_basis(self, holdings: str) -> Dict[str, Dict]:
        """
        Parse holdings string with cost basis information.
        
        Format: "TICKER:SHARES:COST_BASIS:PURCHASE_DATE"
        Example: "VOO:100:40000:2020-01-15"
        """
        parsed = {}
        
        for holding in holdings.split(','):
            parts = holding.strip().split(':')
            
            if len(parts) < 3:
                raise ValueError(
                    f"Invalid holding format: {holding}. "
                    f"Expected 'TICKER:SHARES:COST_BASIS[:PURCHASE_DATE]'"
                )
            
            ticker = parts[0].strip().upper()
            
            try:
                shares = float(parts[1].strip())
                cost_basis = float(parts[2].strip())
            except ValueError:
                raise ValueError(f"Invalid numeric values for {ticker}")
            
            if shares <= 0 or cost_basis <= 0:
                raise ValueError(f"Shares and cost basis must be positive for {ticker}")
            
            # Parse purchase date if provided
            purchase_date = None
            holding_period_days = 180  # Default to short-term
            
            if len(parts) >= 4:
                try:
                    purchase_date = datetime.strptime(parts[3].strip(), '%Y-%m-%d')
                    holding_period_days = (datetime.utcnow() - purchase_date).days
                except ValueError:
                    logger.warning(
                        "Invalid date format, using default holding period",
                        extra={"ticker": ticker, "date": parts[3]}
                    )
            
            parsed[ticker] = {
                'shares': shares,
                'cost_basis': cost_basis,
                'purchase_date': purchase_date,
                'holding_period_days': holding_period_days
            }
        
        return parsed
    
    async def _find_replacement_etfs(
        self,
        ticker: str,
        correlation_min: float
    ) -> List[Dict]:
        """
        Find suitable replacement ETFs for tax-loss harvesting.
        
        Replacements must be similar (high correlation) but not identical
        to avoid wash sale rule violations.
        """
        try:
            # Get similar ETFs using screening service
            similar_result = await etf_screening_service.find_similar_etfs(
                reference_ticker=ticker,
                limit=10
            )
            
            similar = similar_result.get('similar_etfs', [])
            
            if not similar:
                return []
            
            replacements = []
            for etf_dict in similar:
                etf_ticker = etf_dict.get('ticker')
                # Skip the same ticker
                if etf_ticker == ticker:
                    continue
                
                # Estimate correlation based on similarity
                # Real implementation would use historical price correlation
                # For now, use same category/sector as proxy
                estimated_correlation = 0.85  # Conservative estimate
                
                if estimated_correlation < correlation_min:
                    continue
                
                replacement = {
                    "ticker": etf_ticker,
                    "name": etf_dict.get('name', etf_ticker),
                    "correlation": estimated_correlation,
                    "expense_ratio": etf_dict.get('expense_ratio', 0),
                    "expense_ratio_pct": round(etf_dict.get('expense_ratio', 0) * 100, 4),
                    "net_assets": etf_dict.get('net_assets', 0),
                    "reason": self._get_replacement_reason(ticker, etf_ticker, etf_dict.get('category', ''))
                }
                
                replacements.append(replacement)
            
            # Sort by correlation (highest first)
            replacements.sort(key=lambda x: x['correlation'], reverse=True)
            
            return replacements
            
        except Exception as e:
            logger.warning(
                "Failed to find replacements",
                extra={"ticker": ticker, "error": str(e)}
            )
            return []
    
    def _calculate_tax_efficiency_score(
        self,
        expense_ratio: float,
        net_assets: float
    ) -> float:
        """
        Calculate tax efficiency score (0-100).
        
        Higher score = more tax efficient
        """
        # Expense ratio component (40% weight)
        if expense_ratio <= 0.0005:  # 0.05%
            expense_score = 100
        elif expense_ratio <= 0.002:  # 0.2%
            expense_score = 90
        elif expense_ratio <= 0.005:  # 0.5%
            expense_score = 75
        elif expense_ratio <= 0.01:  # 1%
            expense_score = 50
        else:
            expense_score = 25
        
        # Fund size component (30% weight) - larger = more efficient
        if net_assets >= 100_000_000_000:  # $100B+
            size_score = 100
        elif net_assets >= 10_000_000_000:  # $10B+
            size_score = 85
        elif net_assets >= 1_000_000_000:  # $1B+
            size_score = 70
        elif net_assets >= 100_000_000:  # $100M+
            size_score = 50
        else:
            size_score = 30
        
        # Turnover component (30% weight) - assumed based on expense ratio
        # Lower expense ratio often correlates with lower turnover
        if expense_ratio <= 0.001:
            turnover_score = 100
        elif expense_ratio <= 0.005:
            turnover_score = 80
        else:
            turnover_score = 60
        
        # Weighted score
        total_score = (
            expense_score * 0.4 +
            size_score * 0.3 +
            turnover_score * 0.3
        )
        
        return total_score
    
    def _estimate_turnover_from_type(self, category: str) -> str:
        """Estimate annual turnover based on ETF category."""
        category_lower = category.lower()
        
        if 'index' in category_lower or 'passive' in category_lower:
            return "Low (5-15%)"
        elif 'active' in category_lower:
            return "High (50-100%)"
        elif 'smart beta' in category_lower or 'factor' in category_lower:
            return "Moderate (20-40%)"
        else:
            return "Medium (15-30%)"
    
    def _get_tax_efficiency_reason(
        self,
        current_er: float,
        alternative_er: float,
        category: Optional[str]
    ) -> str:
        """Generate reason for tax efficiency improvement."""
        er_savings = current_er - alternative_er
        er_savings_bps = er_savings * 10000  # Basis points
        
        reasons = []
        
        if er_savings_bps >= 50:
            reasons.append(f"Saves {er_savings_bps:.0f} bps in fees")
        
        if category and 'index' in category.lower():
            reasons.append("Index fund with low turnover")
        
        if not reasons:
            reasons.append("Similar exposure with better structure")
        
        return " • ".join(reasons)
    
    def _get_replacement_reason(
        self,
        original: str,
        replacement: str,
        category: Optional[str]
    ) -> str:
        """Generate reason for replacement ETF suggestion."""
        # Common replacement pairs
        pairs = {
            'VOO': 'IVV',  # S&P 500 alternatives
            'VTI': 'ITOT',  # Total market alternatives
            'VEA': 'IEFA',  # International alternatives
        }
        
        if original in pairs and replacement == pairs[original]:
            return "Tracks same index with different structure (avoids wash sale)"
        elif category and 'S&P 500' in category:
            return "Alternative S&P 500 tracker"
        elif category and 'total' in category.lower():
            return "Alternative total market fund"
        else:
            return "Similar exposure, different implementation"
    
    def _get_tax_optimization_tips(
        self,
        short_term_gains: float,
        long_term_gains: float,
        holdings: List[Dict]
    ) -> List[str]:
        """Generate personalized tax optimization tips."""
        tips = []
        
        # Short-term vs long-term
        if short_term_gains > 0 and long_term_gains > 0:
            if short_term_gains > long_term_gains:
                tips.append(
                    "Consider waiting to sell short-term positions until they qualify "
                    "for long-term treatment (>1 year) to reduce tax rate from 37% to 20%"
                )
        elif short_term_gains > 0:
            tips.append(
                "All gains are short-term (taxed at 37%). Consider holding positions "
                "longer for preferential long-term capital gains treatment"
            )
        
        # Loss harvesting
        losses = [h for h in holdings if h['capital_gain_loss'] < 0]
        if losses:
            tips.append(
                f"You have {len(losses)} position(s) with losses. Consider tax-loss "
                f"harvesting to offset gains and reduce tax liability"
            )
        
        # Selling strategy
        if len(holdings) > 3:
            tips.append(
                "Consider spreading sales across multiple years to avoid higher tax brackets"
            )
        
        return tips or ["No specific optimization opportunities identified"]
    
    def _get_tax_efficiency_recommendation(
        self,
        alternatives: List[Dict]
    ) -> str:
        """Generate overall tax efficiency recommendation."""
        if not alternatives:
            return "Current fund is already tax-efficient, no changes recommended"
        
        top_alt = alternatives[0]
        savings = top_alt['annual_savings_per_10k']
        
        if savings >= 50:
            return (
                f"Strong recommendation: Switch to {top_alt['ticker']} for "
                f"${savings:.2f} annual savings per $10,000 invested"
            )
        elif savings >= 20:
            return (
                f"Consider switching to {top_alt['ticker']} for "
                f"${savings:.2f} annual savings per $10,000 invested"
            )
        else:
            return "Current fund is reasonably tax-efficient"


# Singleton instance
etf_tax_service = ETFTaxService()
