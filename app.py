"""
Main application class for investment projection tool.
"""
import asyncio

from features.projections.investmentprojections import InvestmentProjectionApp
from utility.ui_utils import display_welcome, get_ticker_input, get_menu_choice, get_continue_choice

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