"""
Investment strategy model and projection calculations.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from models.stock import StockData


@dataclass
class InvestmentStrategy:
    """Data class representing an investment strategy."""
    
    name: str
    initial_investment: int
    monthly_contribution: int
    
    @property
    def quarterly_investment(self) -> int:
        """Calculate quarterly investment amount."""
        return self.monthly_contribution * 3


class PortfolioProjector:
    """Class responsible for calculating investment projections."""
    
    def __init__(self, stock_data: StockData):
        """Initialize projector with stock data."""
        self.stock_data = stock_data
    
    def project_strategy(self, strategy: InvestmentStrategy, quarters: int) -> List[Dict[str, Any]]:
        """
        Project investment growth for a given strategy over time.
        
        Args:
            strategy: The investment strategy to project
            quarters: Number of quarters to project
            
        Returns:
            List of dictionaries containing quarterly projection data
        """
        rows = []
        total_invested = strategy.initial_investment
        shares = strategy.initial_investment / self.stock_data.price
        
        for quarter in range(1, quarters + 1):
            # Invest quarterly amount
            total_invested += strategy.quarterly_investment
            shares += strategy.quarterly_investment / self.stock_data.price
            
            # Calculate and reinvest dividend with growth
            div_this_quarter = (self.stock_data.quarterly_dividend * 
                               (1 + self.stock_data.quarterly_growth_rate) ** (quarter - 1))
            dividend_amount = shares * div_this_quarter
            shares += dividend_amount / self.stock_data.price
            
            # Calculate current balance
            balance = shares * self.stock_data.price
            
            rows.append({
                "Strategy": strategy.name,
                "Quarter": f"Q{quarter}",
                "Initial_Investment": f"${strategy.initial_investment:,.2f}",
                "Quarterly_Investment": f"${strategy.quarterly_investment:,.2f}",
                "Total Shares": f"{shares:,.2f}",
                "Total_Investment": f"${total_invested:,.2f}",
                "Projected_Balance": f"${balance:,.2f}"
            })
        
        return rows