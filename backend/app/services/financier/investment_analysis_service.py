"""
Investment Analysis Service

Provides rolling investment analysis and tracking for investment transactions.
Analyzes contributions, trends, and investment patterns over time.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from app.core.logging_config import get_logger
from app.repositories.financial_repository import financial_repository

logger = get_logger(__name__)


class InvestmentAnalysisService:
    """Service for analyzing investment transactions and patterns."""
    
    async def get_rolling_investment_analysis(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        months_back: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate rolling investment analysis over specified period.
        
        Provides:
        - Total contributions over period
        - Monthly average contributions
        - Contribution trends (increasing/decreasing)
        - Target vs actual analysis
        - Consistency metrics
        
        Args:
            year: Current year for analysis
            month: Current month for analysis
            months_back: Number of months to analyze (default 12)
            
        Returns:
            Comprehensive investment analysis
        """
        logger.info(
            "Calculating rolling investment analysis",
            extra={
                "year": year,
                "month": month,
                "months_back": months_back
            }
        )
        
        try:
            # Get investment transactions
            transactions = await financial_repository.get_investment_transactions(
                year=year,
                month=month,
                months_back=months_back
            )
            
            if not transactions:
                return {
                    "period": {
                        "months": months_back,
                        "year": year,
                        "month": month
                    },
                    "total_contributions": 0,
                    "transaction_count": 0,
                    "message": "No investment transactions found for this period"
                }
            
            # Calculate metrics
            total_contributions = sum(abs(txn.amount) for txn in transactions)
            transaction_count = len(transactions)
            
            # Group by month
            monthly_contributions = defaultdict(float)
            monthly_counts = defaultdict(int)
            
            for txn in transactions:
                month_key = f"{txn.statement_year}-{txn.statement_month:02d}"
                monthly_contributions[month_key] += abs(txn.amount)
                monthly_counts[month_key] += 1
            
            # Sort by month
            sorted_months = sorted(monthly_contributions.keys())
            contribution_values = [monthly_contributions[m] for m in sorted_months]
            
            # Calculate statistics
            if contribution_values:
                avg_monthly = statistics.mean(contribution_values)
                median_monthly = statistics.median(contribution_values)
                
                if len(contribution_values) > 1:
                    stdev_monthly = statistics.stdev(contribution_values)
                    consistency_score = (1 - (stdev_monthly / avg_monthly)) * 100 if avg_monthly > 0 else 0
                else:
                    stdev_monthly = 0
                    consistency_score = 100
                
                # Determine trend
                if len(contribution_values) >= 3:
                    recent_avg = statistics.mean(contribution_values[-3:])
                    older_avg = statistics.mean(contribution_values[:3])
                    trend = "increasing" if recent_avg > older_avg else "decreasing"
                    trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                else:
                    trend = "stable"
                    trend_percentage = 0
            else:
                avg_monthly = median_monthly = stdev_monthly = 0
                consistency_score = 0
                trend = "unknown"
                trend_percentage = 0
            
            # Monthly breakdown
            monthly_breakdown = []
            for month_key in sorted_months:
                monthly_breakdown.append({
                    "month": month_key,
                    "amount": round(monthly_contributions[month_key], 2),
                    "transaction_count": monthly_counts[month_key]
                })
            
            # Get top investment destinations
            destination_totals = defaultdict(float)
            for txn in transactions:
                destination = self._identify_investment_destination(txn.merchant_name)
                destination_totals[destination] += abs(txn.amount)
            
            top_destinations = sorted(
                [{"destination": k, "amount": round(v, 2)} for k, v in destination_totals.items()],
                key=lambda x: x["amount"],
                reverse=True
            )[:5]
            
            # Calculate projections
            projected_annual = avg_monthly * 12
            
            return {
                "period": {
                    "months_analyzed": len(sorted_months),
                    "date_range": {
                        "start": sorted_months[0] if sorted_months else None,
                        "end": sorted_months[-1] if sorted_months else None
                    }
                },
                "summary": {
                    "total_contributions": round(total_contributions, 2),
                    "transaction_count": transaction_count,
                    "average_monthly": round(avg_monthly, 2),
                    "median_monthly": round(median_monthly, 2),
                    "projected_annual": round(projected_annual, 2)
                },
                "trends": {
                    "direction": trend,
                    "change_percentage": round(trend_percentage, 2),
                    "consistency_score": round(consistency_score, 1),
                    "standard_deviation": round(stdev_monthly, 2)
                },
                "monthly_breakdown": monthly_breakdown,
                "top_destinations": top_destinations,
                "insights": self._generate_investment_insights(
                    avg_monthly,
                    consistency_score,
                    trend,
                    trend_percentage
                )
            }
            
        except Exception as e:
            logger.error(
                "Error calculating rolling investment analysis",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    def _identify_investment_destination(self, merchant_name: str) -> str:
        """Identify investment destination from merchant name."""
        merchant_upper = merchant_name.upper()
        
        if 'SCHWAB' in merchant_upper:
            return "Charles Schwab"
        elif 'WEBULL' in merchant_upper:
            return "Webull"
        elif 'FIDELITY' in merchant_upper:
            return "Fidelity"
        elif 'VANGUARD' in merchant_upper:
            return "Vanguard"
        elif 'ROBINHOOD' in merchant_upper:
            return "Robinhood"
        else:
            return "Other Investment"
    
    def _generate_investment_insights(
        self,
        avg_monthly: float,
        consistency_score: float,
        trend: str,
        trend_percentage: float
    ) -> List[str]:
        """Generate insights based on investment patterns."""
        insights = []
        
        # Consistency insights
        if consistency_score >= 80:
            insights.append(f"✓ Excellent consistency! Your investments vary by less than {round(100 - consistency_score, 1)}%.")
        elif consistency_score >= 60:
            insights.append(f"⚠ Good consistency. Consider reducing variation (currently {round(100 - consistency_score, 1)}%).")
        else:
            insights.append(f"⚠ Investment amounts vary significantly ({round(100 - consistency_score, 1)}% variation). Consider setting up automatic transfers.")
        
        # Trend insights
        if trend == "increasing" and trend_percentage > 10:
            insights.append(f"📈 Great! Your investments are increasing by {abs(round(trend_percentage, 1))}%.")
        elif trend == "decreasing" and abs(trend_percentage) > 10:
            insights.append(f"📉 Notice: Your investments have decreased by {abs(round(trend_percentage, 1))}%. Review your budget.")
        
        # Amount insights
        if avg_monthly > 0:
            annual_projection = avg_monthly * 12
            insights.append(f"💰 At current rate, you'll invest ${round(annual_projection, 2):,.2f} annually.")
            
            # Retirement savings goal (15% of income is common recommendation)
            if avg_monthly >= 1000:
                insights.append("✓ You're on track with strong investment contributions!")
            elif avg_monthly >= 500:
                insights.append("⚠ Consider increasing contributions if possible to reach long-term goals.")
            else:
                insights.append("⚠ Try to increase investment amounts to build long-term wealth.")
        
        return insights


# Singleton instance
investment_analysis_service = InvestmentAnalysisService()
