#!/usr/bin/env python3
"""
Test script for Finviz parser.

Usage:
    python3 test_finviz_parser.py NVDA
    python3 test_finviz_parser.py AAPL
    python3 test_finviz_parser.py SNPS
"""

import sys
import json
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.finviz_parser import parse_finviz_files
from core.logging_config import get_logger

logger = get_logger(__name__)


def test_parser(ticker: str):
    """
    Test Finviz parser for given ticker.
    
    Supports both architectures:
    - NEW (Option 1): 3 self-contained files (each with snapshot + statement)
    - OLD: 4 separate files (1 fullpage + 3 statement-only files)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL', 'SNPS')
    """
    ticker = ticker.upper()
    logger.info(f"Testing parser for {ticker}")
    
    # Construct file paths
    base_path = Path(__file__).parent.parent.parent.parent / 'docs' / 'Ingest'
    
    # Try NEW architecture first (3 self-contained files)
    income_path = base_path / f'finviz_income_statement_{ticker.lower()}.html'
    balance_path = base_path / f'finviz_balance_sheet_{ticker.lower()}.html'
    cashflow_path = base_path / f'finviz_cash_flow_{ticker.lower()}.html'
    
    # Check for OLD architecture (separate fullpage file)
    fullpage_path = base_path / f'finviz_fullpage_{ticker.lower()}.html'
    
    # Detect architecture based on file presence
    # PRIORITY: Check OLD architecture first (separate fullpage file)
    if fullpage_path.exists() and income_path.exists():
        # OLD architecture: Separate fullpage + statement files
        logger.info(f"Using OLD architecture (4 separate files)")
        print(f"✓ Detected OLD architecture (4 separate files)")
        
        fullpage_html_path = fullpage_path
        
    elif income_path.exists() and balance_path.exists() and cashflow_path.exists():
        # NEW architecture (Option 1): 3 self-contained files
        # In this case, fullpage_path == income_path (both contain snapshot)
        logger.info(f"Using NEW architecture (3 self-contained files)")
        print(f"✓ Detected NEW architecture (3 self-contained files)")
        
        fullpage_html_path = income_path  # Use income file as fullpage (contains snapshot)
        
        # Balance sheet and cash flow are optional (for backwards compatibility)
        if not balance_path.exists():
            logger.warning(f"Balance sheet HTML not found: {balance_path}")
            print(f"⚠️  Balance sheet file not found (will use income statement)")
            balance_path = None
        
        if not cashflow_path.exists():
            logger.warning(f"Cash flow HTML not found: {cashflow_path}")
            print(f"⚠️  Cash flow file not found (will use income statement)")
            cashflow_path = None
    else:
        # Files not found
        logger.error(f"Required HTML files not found for {ticker}")
        print(f"❌ Files not found for {ticker}")
        print(f"   Please extract HTML first using:")
        print(f"   python3 scripts/fetch_finviz_all_statements.py {ticker}")
        print(f"\n   Expected files (NEW architecture):")
        print(f"   - {income_path}")
        print(f"   - {balance_path}")
        print(f"   - {cashflow_path}")
        print(f"\n   Or (OLD architecture):")
        print(f"   - {fullpage_path}")
        print(f"   - {income_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"TESTING FINVIZ PARSER FOR {ticker}")
    print(f"{'='*60}\n")
    
    try:
        # Parse files (supports both architectures)
        result = parse_finviz_files(
            str(fullpage_html_path),
            str(income_path),
            str(balance_path) if balance_path else None,
            str(cashflow_path) if cashflow_path else None,
            ticker
        )
        
        # Display results
        print("✅ PARSING SUCCESSFUL\n")
        
        # Snapshot metrics
        print(f"📊 SNAPSHOT TABLE: {len(result['snapshot'])} metrics")
        print("-" * 60)
        
        # Show first 10 snapshot metrics
        snapshot_sample = list(result['snapshot'].items())[:10]
        for metric, value in snapshot_sample:
            print(f"  {metric:30} {value}")
        
        if len(result['snapshot']) > 10:
            print(f"  ... ({len(result['snapshot']) - 10} more metrics)")
        
        print()
        
        # Income Statement
        income_periods = list(result['income_statement'].keys())
        print(f"📈 INCOME STATEMENT: {len(income_periods)} periods")
        print("-" * 60)
        
        if income_periods:
            first_period = income_periods[0]
            metrics_count = len(result['income_statement'][first_period])
            print(f"  Periods: {', '.join(income_periods)}")
            print(f"  Metrics per period: {metrics_count}")
            
            # Show sample metrics from first period
            if metrics_count > 0:
                print(f"\n  Sample metrics ({first_period}):")
                sample_metrics = list(result['income_statement'][first_period].items())[:5]
                for metric, value in sample_metrics:
                    print(f"    {metric:30} {value}")
                
                if metrics_count > 5:
                    print(f"    ... ({metrics_count - 5} more metrics)")
        else:
            print("  ⚠️ No periods found (check HTML structure)")
        
        print()
        
        # Balance Sheet
        balance_periods = list(result['balance_sheet'].keys())
        print(f"💰 BALANCE SHEET: {len(balance_periods)} periods")
        print("-" * 60)
        
        if balance_periods:
            first_period = balance_periods[0]
            metrics_count = len(result['balance_sheet'][first_period])
            print(f"  Periods: {', '.join(balance_periods)}")
            print(f"  Metrics per period: {metrics_count}")
            
            # Show sample metrics from first period
            if metrics_count > 0:
                print(f"\n  Sample metrics ({first_period}):")
                sample_metrics = list(result['balance_sheet'][first_period].items())[:5]
                for metric, value in sample_metrics:
                    print(f"    {metric:30} {value}")
                
                if metrics_count > 5:
                    print(f"    ... ({metrics_count - 5} more metrics)")
        else:
            print("  ⚠️ No periods found (check HTML structure)")
        
        print()
        
        # Cash Flow
        cashflow_periods = list(result['cash_flow'].keys())
        print(f"💵 CASH FLOW: {len(cashflow_periods)} periods")
        print("-" * 60)
        
        if cashflow_periods:
            first_period = cashflow_periods[0]
            metrics_count = len(result['cash_flow'][first_period])
            print(f"  Periods: {', '.join(cashflow_periods)}")
            print(f"  Metrics per period: {metrics_count}")
            
            # Show sample metrics from first period
            if metrics_count > 0:
                print(f"\n  Sample metrics ({first_period}):")
                sample_metrics = list(result['cash_flow'][first_period].items())[:5]
                for metric, value in sample_metrics:
                    print(f"    {metric:30} {value}")
                
                if metrics_count > 5:
                    print(f"    ... ({metrics_count - 5} more metrics)")
        else:
            print("  ⚠️ No periods found (check HTML structure)")
        
        print()
        
        # Metadata
        metadata = result['metadata']
        print("🔍 METADATA")
        print("-" * 60)
        print(f"  Periods available: {metadata['periods_available']}")
        print(f"  Paywall detected: {'Yes ⚠️' if metadata['paywall_detected'] else 'No'}")
        print(f"  Parsed at: {metadata['parsed_at']}")
        
        print()
        
        # Save to JSON file
        output_path = base_path / f'{ticker.lower()}_financials.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 JSON saved to: {output_path}")
        print()
        
        # Summary
        print(f"{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Snapshot metrics: {len(result['snapshot'])}")
        print(f"✅ Income statement periods: {len(income_periods)}")
        print(f"{'⚠️' if not balance_periods else '✅'} Balance sheet periods: {len(balance_periods)}")
        print(f"{'⚠️' if not cashflow_periods else '✅'} Cash flow periods: {len(cashflow_periods)}")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Parse failed for {ticker}", exc_info=True)
        print(f"\n❌ PARSING FAILED")
        print(f"   Error: {str(e)}")
        print(f"   See logs for details")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_finviz_parser.py TICKER")
        print("\nExamples:")
        print("  python3 test_finviz_parser.py NVDA")
        print("  python3 test_finviz_parser.py AAPL")
        print("  python3 test_finviz_parser.py SNPS")
        sys.exit(1)
    
    ticker = sys.argv[1]
    success = test_parser(ticker)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
