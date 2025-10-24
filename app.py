"""
Main application class for investment projection tool.
"""
import sys
from typing import List, Optional

from models.config import Config
from models.investment import InvestmentStrategy, PortfolioProjector
from services.data_scraper import StockDataService
from services.report_service import ReportService


class InvestmentProjectionApp:
    """Main application class for investment projections."""
    
    def __init__(self, config_file: str = ".env"):
        """Initialize the application with configuration."""
        self.config = Config(config_file)
        self.stock_service = StockDataService()
        self.report_service = ReportService()
    
    def run(self, ticker: Optional[str] = None) -> str:
        """
        Run the investment projection analysis.
        
        Args:
            ticker: Stock ticker symbol (uses config default if None)
            
        Returns:
            Path to the generated report file
        """
        # Use provided ticker or default from config
        ticker = ticker or self.config.ticker
        
        # Get stock data
        print(f"Fetching data for {ticker}...")
        stock_data = self.stock_service.get_stock_data(ticker)
        print(f"Fetched data for {ticker}: {stock_data}")
        
        # Create portfolio projector
        projector = PortfolioProjector(stock_data)
        
        # Generate projections for all strategies
        all_projections = []
        strategies = self._create_strategies()
        
        for strategy in strategies:
            projections = projector.project_strategy(strategy, self.config.quarters)
            all_projections.extend(projections)
        
        # Generate report
        report_path = self.report_service.generate_csv_report(all_projections, ticker)
        print(f"Projection saved to {report_path}")
        
        return report_path
    
    def _create_strategies(self) -> List[InvestmentStrategy]:
        """Create InvestmentStrategy objects from configuration."""
        strategies = []
        for strategy_config in self.config.strategies:
            strategy = InvestmentStrategy(
                name=strategy_config["name"],
                initial_investment=strategy_config["initial"],
                monthly_contribution=strategy_config["monthly"]
            )
            strategies.append(strategy)
        return strategies


def main():
    """Main entry point for the application."""
    # Get ticker from command line argument or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run the application
    app = InvestmentProjectionApp()
    app.run(ticker)


if __name__ == "__main__":
    main()