"""
Investment Projections Module

This module contains the main application class for running investment projections
with various strategies and generating reports.
"""
import asyncio
from typing import Optional, List
import inquirer

from models.config import Config
from models.investment import InvestmentStrategy, PortfolioProjector
from services.data_scraper import StockDataService
from services.price_service import PriceService
from services.report_service import ReportService

# Import UI utility functions from shared module
from utility.ui_utils import display_projection_summary, get_export_or_custom_choice, get_custom_strategy_inputs


class InvestmentProjectionApp:
    """Main application class for investment projections."""

    def __init__(self, config_file: str = ".env"):
        """
        Initialize the application with configuration and services.
        
        Args:
            config_file: Path to the configuration file (default: ".env")
        """
        self.config = Config(config_file)
        self.stock_service = StockDataService()
        self.price_service = PriceService()
        self.report_service = ReportService()

    async def run(self, ticker: Optional[str] = None) -> Optional[str]:
        """
        Run the investment projection analysis for a given stock ticker.
        
        This method performs the following workflow:
        1. Fetches stock data and current price concurrently
        2. Creates portfolio projector with the stock data
        3. Generates projections for all configured strategies
        4. Displays projection summary to the user
        5. Handles user choice for export or custom strategy creation

        Args:
            ticker: Stock ticker symbol (uses config default if None)

        Returns:
            Path to the generated report file if exported, None otherwise
            
        Raises:
            ValueError: If unable to fetch stock data or current price
        """
        # Use provided ticker or default from config
        ticker = ticker or self.config.ticker

        # Get stock data and current price concurrently
        print(f"Fetching data for {ticker}...")
        
        # Run data fetching concurrently for better performance
        stock_data_task = asyncio.create_task(self.stock_service.get_stock_data(ticker))
        price_task = asyncio.create_task(self.price_service.get_current_price(ticker))
        
        stock_data, current_price = await asyncio.gather(stock_data_task, price_task)
        
        if not stock_data:
            raise ValueError(f"Unable to fetch dividend data for ticker {ticker}")
            
        if not current_price:
            raise ValueError(f"Unable to fetch current price for ticker {ticker}")
            
        # Update stock data with current price
        stock_data.price = current_price
        print(f"Fetched data for {ticker}: {stock_data}")

        # Create portfolio projector
        projector = PortfolioProjector(stock_data)

        # Generate projections for all strategies concurrently
        strategies = self._create_strategies()
        
        # Create tasks for concurrent projection generation
        projection_tasks = [
            projector.project_strategy(strategy, self.config.quarters)
            for strategy in strategies
        ]
        
        # Run all projections concurrently
        strategy_projections = await asyncio.gather(*projection_tasks)
        
        # Flatten the results
        all_projections = []
        for projections in strategy_projections:
            all_projections.extend(projections)

        # Display projection summary
        display_projection_summary(all_projections, ticker)
        
        # Ask user's choice: export, no export, or custom strategy
        choice = get_export_or_custom_choice()
        
        if choice == 'Yes':
            # Generate and save report
            report_service = ReportService()
            report_path = await report_service.generate_csv_report(all_projections, ticker)
            return report_path
        elif choice == 'Try Custom Strategy':
            # Get custom strategy inputs
            initial_investment, monthly_investment = get_custom_strategy_inputs()
            
            # Create custom strategy
            custom_strategy = InvestmentStrategy(
                name="Custom Strategy",
                initial_investment=int(initial_investment),
                monthly_contribution=int(monthly_investment)
            )
            
            # Generate projection for custom strategy
            print(f"\n� Generating custom projection for {ticker}...")
            custom_projector = PortfolioProjector(stock_data)
            custom_projections = await custom_projector.project_strategy(custom_strategy, self.config.quarters)
            
            # Display custom strategy summary
            print(f"\n📊 CUSTOM STRATEGY PROJECTION FOR {ticker}")
            print("=" * 90)
            display_projection_summary(custom_projections, ticker)
            
            # Ask if they want to export the custom strategy results
            export_questions = [
                inquirer.List('export_custom',
                             message="Would you like to export the custom strategy results to CSV?",
                             choices=['Yes', 'No'],
                             carousel=True)
            ]
            export_answers = inquirer.prompt(export_questions)
            
            if export_answers['export_custom'] == 'Yes':
                report_service = ReportService()
                report_path = await report_service.generate_csv_report(custom_projections, f"{ticker}_custom_strategy")
                return report_path
            else:
                return None
        else:
            return None

    def _create_strategies(self) -> List[InvestmentStrategy]:
        """
        Create InvestmentStrategy objects from configuration.
        
        Reads the strategy configurations from the config file and converts
        them into InvestmentStrategy objects for projection analysis.
        
        Returns:
            List of InvestmentStrategy objects configured for this analysis
        """
        strategies = []
        for strategy_config in self.config.strategies:
            strategy = InvestmentStrategy(
                name=strategy_config["name"],
                initial_investment=strategy_config["initial"],
                monthly_contribution=strategy_config["monthly"]
            )
            strategies.append(strategy)
        return strategies