"""
UI Utility Functions

This module contains shared UI utility functions for user interactions
and display formatting.
"""
from typing import List, Any
import inquirer


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