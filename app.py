"""
Main application class for investment projection tool.
"""
from typing import List, Optional
import inquirer

from models.config import Config
from models.investment import InvestmentStrategy, PortfolioProjector
from services.data_scraper import StockDataService
from services.price_service import PriceService
from services.report_service import ReportService


class InvestmentProjectionApp:
    """Main application class for investment projections."""

    def __init__(self, config_file: str = ".env"):
        """Initialize the application with configuration."""
        self.config = Config(config_file)
        self.stock_service = StockDataService()
        self.price_service = PriceService()
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

        # Get stock data and current price
        print(f"Fetching data for {ticker}...")
        stock_data = self.stock_service.get_stock_data(ticker)
        
        if not stock_data:
            raise ValueError(f"Unable to fetch dividend data for ticker {ticker}")
            
        # Get current price separately
        current_price = self.price_service.get_current_price(ticker)
        if not current_price:
            raise ValueError(f"Unable to fetch current price for ticker {ticker}")
            
        # Update stock data with current price
        stock_data.price = current_price
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


def display_welcome():
    """Display welcome message."""
    print("\n" + "="*50)
    print("  KUBERAN - Investment Analysis Tool")
    print("="*50)
    print("Use arrow keys to navigate, Enter to select\n")

def get_ticker_input() -> str:
    """Get ticker symbol from user input with suggestions."""
    questions = [
        inquirer.Text('ticker',
                      message="Enter stock ticker symbol",
                      validate=lambda _, x: len(x.strip()) > 0)
    ]
    answers = inquirer.prompt(questions)
    return answers['ticker'].strip().upper() if answers else ""

def get_menu_choice() -> str:
    """Get menu choice using arrow keys."""
    questions = [
        inquirer.List('action',
                      message="What would you like to do?",
                      choices=['Generate Investment Projections', 'Exit'],
                      carousel=True)
    ]
    answers = inquirer.prompt(questions)
    return answers['action'] if answers else 'Exit'

def get_continue_choice() -> bool:
    """Ask user if they want to continue with arrow key selection."""
    questions = [
        inquirer.List('continue',
                      message="Would you like to perform another analysis?",
                      choices=['Yes', 'No'],
                      default='Yes')
    ]
    answers = inquirer.prompt(questions)
    return answers['continue'] == 'Yes' if answers else False

def main():
    """Main entry point with arrow key navigation."""
    app = InvestmentProjectionApp()
    
    display_welcome()
    print("Welcome to Kuberan Investment Analysis Tool! 🚀")
    
    while True:
        choice = get_menu_choice()
        
        if choice == 'Generate Investment Projections':
            ticker = get_ticker_input()
            if not ticker:
                print("❌ No ticker entered. Returning to menu.")
                continue
                
            print(f"\n🔍 Generating projections for {ticker}...")
            try:
                report_path = app.run(ticker)
                print(f"✅ Success! Report generated: {report_path}")
            except (ValueError, ConnectionError) as e:
                print(f"❌ Error generating projections: {e}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
            
            # Ask if user wants to continue
            if not get_continue_choice():
                break
        
        elif choice == 'Exit':
            break
    
    print("\nThank you for using Kuberan! Goodbye! 👋")


if __name__ == "__main__":
    main()