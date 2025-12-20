#!/usr/bin/env python3
"""
extractor_control - Unified FinViz Financial Data Extraction & Parsing

Features:
- Single browser session for multiple tickers (efficient)
- Optional snapshot extraction (statements only mode)
- Automated parsing after extraction
- Concise summary output (distinct data points + time periods)
- No verbose data printing

Usage:
    python3 scripts/extractor_control.py AAPL MSFT NVDA
    python3 scripts/extractor_control.py --no-snapshot AAPL MSFT
    python3 scripts/extractor_control.py --help
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ ERROR: Playwright not installed")
    print("   Install with: pip3 install playwright && playwright install chromium")
    sys.exit(1)

try:
    from app.core.finviz_parser import parse_finviz_files
except ImportError:
    print("❌ ERROR: Cannot import finviz_parser")
    print("   Make sure backend/app/core/finviz_parser.py exists")
    sys.exit(1)


class FinVizExtractorControl:
    """Unified extraction and parsing controller"""
    
    def __init__(self, include_snapshot: bool = True, verbose: bool = False):
        self.include_snapshot = include_snapshot
        self.verbose = verbose
        self.base_url = "https://finviz.com/quote.ashx"
        self.output_dir = Path(__file__).parent.parent / "docs" / "Ingest"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def extract_ticker(self, page, ticker: str) -> Dict[str, int]:
        """Extract all statements for a single ticker using existing page"""
        ticker_upper = ticker.upper()
        ticker_lower = ticker.lower()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Processing {ticker_upper}")
            print(f"{'='*70}")
        
        # Navigate to ticker page
        url = f"{self.base_url}?t={ticker_upper}&p=d"
        # Increase timeout to 60s and use 'domcontentloaded' instead of 'networkidle'
        # networkidle can be too strict for sites with many background requests
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        if self.verbose:
            print(f"✓ Loaded page: {url}")
        
        # Click "Scroll to Statements" link
        try:
            await page.click('a:has-text("Scroll to Statements")', timeout=5000)
            if self.verbose:
                print("✓ Clicked 'Scroll to Statements'")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Could not click scroll link: {e}")
        
        # Wait for statements table
        await page.wait_for_selector('table.quote_statements-table', timeout=10000)
        if self.verbose:
            print("✓ Statements table loaded")
        
        file_sizes = {}
        
        # Extract full page (includes snapshot)
        if self.include_snapshot:
            full_html = await page.content()
            fullpage_path = self.output_dir / f"finviz_fullpage_{ticker_lower}.html"
            fullpage_path.write_text(full_html, encoding='utf-8')
            file_sizes['fullpage'] = len(full_html)
            if self.verbose:
                print(f"✓ Saved fullpage: {fullpage_path.name} ({file_sizes['fullpage']:,} bytes)")
        
        # Extract each statement tab
        tabs = [
            ("Income Statement", f"finviz_income_statement_{ticker_lower}.html"),
            ("Balance Sheet", f"finviz_balance_sheet_{ticker_lower}.html"),
            ("Cash Flow", f"finviz_cash_flow_{ticker_lower}.html")
        ]
        
        for tab_name, filename in tabs:
            # Click tab
            await page.click(f'a:has-text("{tab_name}")')
            # Wait for content to render
            await asyncio.sleep(2)
            # Extract HTML
            html = await page.content()
            filepath = self.output_dir / filename
            filepath.write_text(html, encoding='utf-8')
            
            tab_key = tab_name.lower().replace(" ", "_")
            file_sizes[tab_key] = len(html)
            
            if self.verbose:
                print(f"✓ Saved {tab_name}: {filename} ({file_sizes[tab_key]:,} bytes)")
        
        return file_sizes
    
    def parse_ticker(self, ticker: str) -> Optional[Dict]:
        """Parse extracted HTML files into structured JSON"""
        ticker_lower = ticker.lower()
        
        # Build file paths
        fullpage_path = self.output_dir / f"finviz_fullpage_{ticker_lower}.html"
        income_path = self.output_dir / f"finviz_income_statement_{ticker_lower}.html"
        balance_path = self.output_dir / f"finviz_balance_sheet_{ticker_lower}.html"
        cashflow_path = self.output_dir / f"finviz_cash_flow_{ticker_lower}.html"
        
        # Check files exist
        if not income_path.exists():
            print(f"❌ ERROR: Income statement file not found for {ticker.upper()}")
            return None
        
        # Use fullpage if available, otherwise use income for snapshot
        if self.include_snapshot and fullpage_path.exists():
            fullpage_html_path = str(fullpage_path)
        else:
            fullpage_html_path = str(income_path)
        
        try:
            # Parse using finviz_parser
            result = parse_finviz_files(
                fullpage_path=fullpage_html_path,
                income_statement_path=str(income_path),
                balance_sheet_path=str(balance_path),
                cash_flow_path=str(cashflow_path),
                ticker=ticker.upper()
            )
            
            # Save to JSON
            json_path = self.output_dir / f"{ticker_lower}_financials.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            if self.verbose:
                print(f"✓ Parsed and saved: {json_path.name}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR parsing {ticker.upper()}: {e}")
            return None
    
    def summarize_extraction(self, ticker: str, parsed_data: Dict) -> Dict:
        """Generate concise summary of extracted data"""
        if not parsed_data:
            return {
                'ticker': ticker.upper(),
                'status': 'failed',
                'distinct_data_points': 0,
                'time_periods': {}
            }
        
        # Count distinct data points
        snapshot_keys = len(parsed_data.get('snapshot', {}))
        
        income = parsed_data.get('income_statement', {})
        balance = parsed_data.get('balance_sheet', {})
        cashflow = parsed_data.get('cash_flow', {})
        
        # Get distinct metrics from first period
        income_keys = 0
        balance_keys = 0
        cashflow_keys = 0
        
        if income:
            first_period = list(income.keys())[0]
            income_keys = len(income[first_period])
        
        if balance:
            first_period = list(balance.keys())[0]
            balance_keys = len(balance[first_period])
        
        if cashflow:
            first_period = list(cashflow.keys())[0]
            cashflow_keys = len(cashflow[first_period])
        
        total_distinct = snapshot_keys + income_keys + balance_keys + cashflow_keys
        
        # Count time periods
        income_periods = list(income.keys()) if income else []
        balance_periods = list(balance.keys()) if balance else []
        cashflow_periods = list(cashflow.keys()) if cashflow else []
        
        return {
            'ticker': ticker.upper(),
            'status': 'success',
            'distinct_data_points': {
                'snapshot': snapshot_keys,
                'income_statement': income_keys,
                'balance_sheet': balance_keys,
                'cash_flow': cashflow_keys,
                'total': total_distinct
            },
            'time_periods': {
                'income_statement': len(income_periods),
                'balance_sheet': len(balance_periods),
                'cash_flow': len(cashflow_periods)
            },
            'period_details': {
                'income_statement': income_periods,
                'balance_sheet': balance_periods,
                'cash_flow': cashflow_periods
            }
        }
    
    async def process_tickers(self, tickers: List[str]) -> List[Dict]:
        """Process multiple tickers using single browser session"""
        results = []
        
        print(f"{'='*70}")
        print(f"FinViz Extractor Control - Processing {len(tickers)} ticker(s)")
        print(f"{'='*70}")
        print(f"Mode: {'Full (Snapshot + Statements)' if self.include_snapshot else 'Statements Only'}")
        print(f"Tickers: {', '.join([t.upper() for t in tickers])}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            # Launch browser once
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set user agent to look like a real browser
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            print("🌐 Browser session started\n")
            
            for i, ticker in enumerate(tickers, 1):
                print(f"[{i}/{len(tickers)}] Extracting {ticker.upper()}...", end=' ')
                
                try:
                    # Extract HTML files
                    file_sizes = await self.extract_ticker(page, ticker)
                    print("✓ Extracted", end=' ')
                    
                    # Parse to JSON
                    parsed_data = self.parse_ticker(ticker)
                    if parsed_data:
                        print("✓ Parsed")
                        
                        # Generate summary
                        summary = self.summarize_extraction(ticker, parsed_data)
                        results.append(summary)
                    else:
                        print("✗ Parse failed")
                        results.append({
                            'ticker': ticker.upper(),
                            'status': 'parse_failed'
                        })
                        
                except Exception as e:
                    print(f"✗ Error: {e}")
                    results.append({
                        'ticker': ticker.upper(),
                        'status': 'extraction_failed',
                        'error': str(e)
                    })
            
            await browser.close()
            print("\n🌐 Browser session closed")
        
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print concise summary of all extractions"""
        print(f"\n{'='*70}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*70}\n")
        
        for result in results:
            ticker = result['ticker']
            status = result['status']
            
            if status == 'success':
                dp = result['distinct_data_points']
                tp = result['time_periods']
                
                print(f"✅ {ticker}")
                print(f"   Distinct Data Points: {dp['total']}")
                print(f"      • Snapshot: {dp['snapshot']}")
                print(f"      • Income Statement: {dp['income_statement']}")
                print(f"      • Balance Sheet: {dp['balance_sheet']}")
                print(f"      • Cash Flow: {dp['cash_flow']}")
                print(f"   Time Periods: {tp['income_statement']} (Income), {tp['balance_sheet']} (Balance), {tp['cash_flow']} (Cash Flow)")
                
                # Show fiscal years and quarters as lists
                pd = result['period_details']
                if pd['income_statement']:
                    periods = pd['income_statement']
                    
                    # Separate fiscal years (FY_YYYY) from quarters (YYYY_QN)
                    fiscal_years = [p for p in periods if p.startswith('FY_')]
                    quarters = [p for p in periods if '_Q' in p and not p.startswith('FY_')]
                    ttm = [p for p in periods if p == 'TTM']
                    
                    # Format fiscal years (remove FY_ prefix)
                    if fiscal_years:
                        years = ', '.join([p.replace('FY_', '') for p in sorted(fiscal_years, reverse=True)])
                        print(f"   Fiscal Years: {years}")
                    
                    # Format quarters (group by year)
                    if quarters:
                        # Group quarters by year
                        quarters_by_year = {}
                        for q in quarters:
                            year, quarter = q.split('_')
                            if year not in quarters_by_year:
                                quarters_by_year[year] = []
                            quarters_by_year[year].append(quarter)
                        
                        # Print grouped by year
                        for year in sorted(quarters_by_year.keys(), reverse=True):
                            qs = ', '.join(sorted(quarters_by_year[year]))
                            print(f"   Fiscal Quarters ({year}): {qs}")
                    
                    # Show TTM if present
                    if ttm:
                        print(f"   TTM: Yes")
                
                print()
            else:
                print(f"❌ {ticker} - {status}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
                print()
        
        # Overall stats
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"{'='*70}")
        print(f"Total: {successful}/{len(results)} successful")
        print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description='FinViz Financial Data Extractor & Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract full data (snapshot + statements) for multiple tickers
  python3 scripts/extractor_control.py AAPL MSFT NVDA
  
  # Extract statements only (no snapshot)
  python3 scripts/extractor_control.py --no-snapshot AAPL MSFT
  
  # Verbose mode
  python3 scripts/extractor_control.py -v AAPL
        """
    )
    
    parser.add_argument(
        'tickers',
        nargs='+',
        help='Ticker symbols to extract (e.g., AAPL MSFT NVDA)'
    )
    
    parser.add_argument(
        '--no-snapshot',
        action='store_true',
        help='Extract statements only, skip snapshot table'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create controller
    controller = FinVizExtractorControl(
        include_snapshot=not args.no_snapshot,
        verbose=args.verbose
    )
    
    # Process tickers
    results = asyncio.run(controller.process_tickers(args.tickers))
    
    # Print summary
    controller.print_summary(results)


if __name__ == "__main__":
    main()
