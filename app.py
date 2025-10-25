"""
Main application class for investment projection tool.
"""
import asyncio
from typing import List, Optional, Dict, Any
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

    async def run(self, ticker: Optional[str] = None) -> Optional[str]:
        """
        Run the investment projection analysis.

        Args:
            ticker: Stock ticker symbol (uses config default if None)

        Returns:
            Path to the generated report file
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

def get_export_or_custom_choice() -> str:
    """Ask user if they want to export to CSV or try custom strategy."""
    questions = [
        inquirer.List('choice',
                     message="Would you like to export detailed results to CSV or try out a custom strategy?",
                     choices=['Yes', 'No', 'Try Custom Strategy'],
                     carousel=True)
    ]
    
    answers = inquirer.prompt(questions)
    return answers['choice']

def get_custom_strategy_inputs() -> tuple:
    """Get custom strategy inputs from user."""
    questions = [
        inquirer.Text('initial',
                     message="Enter initial investment amount (e.g., 10000)",
                     validate=lambda _, x: x.replace('.', '').replace(',', '').isdigit()),
        inquirer.Text('monthly',
                     message="Enter monthly investment amount (e.g., 500)",
                     validate=lambda _, x: x.replace('.', '').replace(',', '').isdigit())
    ]
    
    answers = inquirer.prompt(questions)
    return float(answers['initial']), float(answers['monthly'])


def display_projection_summary(all_projections: List[Any], ticker: str):
    """Display a summary table of projections by strategy."""
    print(f"\n📊 PROJECTION SUMMARY FOR {ticker}")
    print("=" * 90)
    
    # Group projections by strategy
    strategies = {}
    for proj in all_projections:
        strategy = proj['Strategy']
        quarter = int(proj['Quarter'].replace('Q', ''))
        
        if strategy not in strategies:
            strategies[strategy] = {
                'Initial_Investment': proj['Initial_Investment'],
                'Quarterly_Investment': proj['Quarterly_Investment'],
                'quarters': {}
            }
        
        strategies[strategy]['quarters'][quarter] = proj['Projected_Balance']
    
    # Calculate monthly investment from quarterly
    for strategy_data in strategies.values():
        quarterly_amt = float(strategy_data['Quarterly_Investment'].replace('$', '').replace(',', ''))
        strategy_data['Monthly_Investment'] = f"${quarterly_amt / 3:,.2f}"
    
    # Print header
    print(f"{'Strategy':<12} {'Initial':<10} {'Monthly':<10} {'Q1 Balance':<12} {'Q4 Balance':<12} {'Q8 Balance':<12} {'Q12 Balance':<12}")
    print(f"{'':12} {'':10} {'':10} {'(Year 1)':<12} {'(Year 1)':<12} {'(Year 2)':<12} {'(Year 3)':<12}")
    print("-" * 90)
    
    # Print each strategy row
    for strategy, data in strategies.items():
        q1_balance = data['quarters'].get(1, 'N/A')
        q4_balance = data['quarters'].get(4, 'N/A')
        q8_balance = data['quarters'].get(8, 'N/A')
        q12_balance = data['quarters'].get(12, 'N/A')
        
        print(f"{strategy:<12} {data['Initial_Investment']:<10} {data['Monthly_Investment']:<10} "
              f"{q1_balance:<12} {q4_balance:<12} {q8_balance:<12} {q12_balance:<12}")
    
    print("=" * 90)

async def main():
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
                report_path = await app.run(ticker)
                if report_path:
                    print(f"✅ Success! Report generated: {report_path}")
                else:
                    print("✅ Projection analysis completed!")
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
    asyncio.run(main())