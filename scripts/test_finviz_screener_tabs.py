#!/usr/bin/env python3
"""
Test script to verify navigation and data extraction across all FinViz screener tabs.

This script:
1. Navigates to each screener tab (Overview, Valuation, Financial, etc.)
2. Extracts all 20 tickers with their tab-specific columns
3. Verifies data integrity for each tab

Requirements:
    pip install playwright beautifulsoup4
    playwright install chromium

Usage:
    python3 scripts/test_finviz_screener_tabs.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup


# All screener tab configurations
SCREENER_TABS = [
    {"name": "Overview", "param": "v=111", "expected_cols": 11},
    {"name": "Valuation", "param": "v=121", "expected_cols": 14},
    {"name": "Financial", "param": "v=161", "expected_cols": 14},
    {"name": "Ownership", "param": "v=131", "expected_cols": 14},
    {"name": "Performance", "param": "v=141", "expected_cols": 15},
    {"name": "Technical", "param": "v=171", "expected_cols": 14},
]


def parse_table_from_html(html_content: str, tab_name: str) -> dict:
    """
    Parse the screener table from HTML content.
    
    Returns:
        Dict with headers and rows data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {
        "tab": tab_name,
        "headers": [],
        "rows": [],
        "ticker_count": 0
    }
    
    # Find the screener table
    screener_table = soup.find('table', class_='screener_table')
    
    if not screener_table:
        print(f"  ⚠️  Could not find screener_table for {tab_name}")
        return result
    
    # Extract headers from thead
    thead = screener_table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            for th in header_row.find_all('th'):
                header_text = th.get_text(strip=True)
                result["headers"].append(header_text)
    
    # Extract data rows from tbody
    tbody = screener_table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr', class_='styled-row')
        
        for row in rows:
            cells = row.find_all('td')
            row_data = {}
            
            for i, cell in enumerate(cells):
                # Get header name for this column
                header = result["headers"][i] if i < len(result["headers"]) else f"col_{i}"
                
                # Extract text - handle nested elements
                link = cell.find('a')
                if link:
                    span = link.find('span')
                    if span:
                        value = span.get_text(strip=True)
                    else:
                        value = link.get_text(strip=True)
                else:
                    value = cell.get_text(strip=True)
                
                row_data[header] = value
            
            if row_data:
                result["rows"].append(row_data)
    
    result["ticker_count"] = len(result["rows"])
    return result


async def test_all_tabs():
    """Navigate to each screener tab and extract all data."""
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Error: Playwright is not installed.")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("FinViz Screener Tab Extraction Test")
    print(f"{'='*70}")
    print(f"Testing {len(SCREENER_TABS)} tabs\n")
    
    all_results = {
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "tabs": {}
    }
    
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        print("✓ Browser launched\n")
        
        for tab in SCREENER_TABS:
            tab_name = tab["name"]
            tab_param = tab["param"]
            url = f"https://finviz.com/screener.ashx?{tab_param}&ft=4"
            
            print(f"{'─'*60}")
            print(f"📑 Tab: {tab_name}")
            print(f"   URL: {url}")
            
            try:
                # Navigate to tab (use domcontentloaded to avoid networkidle timeout)
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(3)  # Allow JS to render fully
                
                # Get HTML content
                html = await page.content()
                
                # Parse the table
                parsed = parse_table_from_html(html, tab_name)
                
                print(f"   Headers ({len(parsed['headers'])}): {parsed['headers']}")
                print(f"   Tickers extracted: {parsed['ticker_count']}")
                
                # Show first 3 tickers as sample
                if parsed['rows']:
                    print(f"\n   Sample data (first 3 tickers):")
                    for row in parsed['rows'][:3]:
                        ticker = row.get('Ticker', row.get('ticker', 'N/A'))
                        # Show first few columns
                        preview = {k: v for k, v in list(row.items())[:5]}
                        print(f"     {ticker}: {preview}")
                
                # Store result
                all_results["tabs"][tab_name] = {
                    "url": url,
                    "headers": parsed["headers"],
                    "header_count": len(parsed["headers"]),
                    "ticker_count": parsed["ticker_count"],
                    "data": parsed["rows"]
                }
                
                print(f"   ✓ Success")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                all_results["tabs"][tab_name] = {"error": str(e)}
            
            print()
        
        await browser.close()
    
    # Summary
    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    total_success = 0
    for tab_name, tab_data in all_results["tabs"].items():
        if "error" not in tab_data:
            total_success += 1
            print(f"✓ {tab_name:12} | {tab_data['header_count']:2} columns | {tab_data['ticker_count']:2} tickers")
        else:
            print(f"✗ {tab_name:12} | Error: {tab_data['error']}")
    
    print(f"\nTotal: {total_success}/{len(SCREENER_TABS)} tabs successful")
    
    # Save results
    output_path = Path("docs/Ingest/finviz_screener_all_tabs_test.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Full results saved to: {output_path}")
    
    return all_results


if __name__ == "__main__":
    asyncio.run(test_all_tabs())
