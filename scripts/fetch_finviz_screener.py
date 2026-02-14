#!/usr/bin/env python3
"""
Fetch FinViz Screener page data using browser automation.

This script navigates to the FinViz screener, extracts:
1. Filter categories and options above the ticker list
2. Screener tabs and their column structures
3. Sample ticker data from each view

Requirements:
    pip install playwright beautifulsoup4
    playwright install chromium

Usage:
    python3 scripts/fetch_finviz_screener.py
    python3 scripts/fetch_finviz_screener.py --save-html
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup


async def fetch_finviz_screener(output_dir: str = "docs/Ingest", save_html: bool = False) -> dict:
    """
    Fetch and parse FinViz screener page data.
    
    Args:
        output_dir: Directory to save output
        save_html: If True, save raw HTML for debugging
        
    Returns:
        Dict with screener structure and sample data
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Error: Playwright is not installed.")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    # Screener URL with all filters visible
    url = "https://finviz.com/screener.ashx?v=111&ft=4"
    
    print(f"\n{'='*70}")
    print(f"Fetching FinViz Screener Data")
    print(f"{'='*70}")
    print(f"URL: {url}\n")
    
    # Prepare output directory
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Screener tabs to explore
    screener_tabs = [
        {"name": "Overview", "param": "v=111"},
        {"name": "Valuation", "param": "v=121"},
        {"name": "Financial", "param": "v=161"},
        {"name": "Ownership", "param": "v=131"},
        {"name": "Performance", "param": "v=141"},
        {"name": "Technical", "param": "v=171"},
    ]
    
    result = {
        "source": "finviz_screener",
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "base_url": "https://finviz.com/screener.ashx",
        "filters": {},
        "tabs": {},
        "total_tickers": None,
        "sample_data": {}
    }
    
    try:
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            print("✓ Browser launched")
            
            # Navigate to screener with all filters
            print(f"\n📄 Loading screener page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)  # Wait for JS to render
            print("✓ Page loaded")
            
            # Handle potential popups/ads
            await asyncio.sleep(2)
            try:
                # Close any modal dialogs
                close_buttons = await page.query_selector_all('[class*="close"], [class*="dismiss"], button:has-text("Close")')
                for btn in close_buttons[:3]:  # Try first 3 close buttons
                    try:
                        await btn.click(timeout=1000)
                        await asyncio.sleep(0.5)
                    except:
                        pass
            except:
                pass
            
            # Get full page HTML
            full_html = await page.content()
            soup = BeautifulSoup(full_html, 'html.parser')
            
            if save_html:
                html_path = output_dir_path / "finviz_screener_full.html"
                html_path.write_text(full_html)
                print(f"✓ Saved full HTML ({len(full_html):,} bytes)")
            
            # Extract total ticker count
            print("\n📊 Extracting screener data...")
            total_text = soup.find(string=lambda t: t and "Total" in t and "/" in str(t))
            if total_text:
                result["total_tickers"] = total_text.strip()
                print(f"   Total tickers: {result['total_tickers']}")
            
            # Extract filter categories
            print("\n🔍 Extracting filter categories...")
            filter_tables = soup.find_all('table', class_='filters-table')
            
            filters_found = []
            for table in filter_tables:
                # Find all filter dropdowns/selects
                selects = table.find_all('select')
                for select in selects:
                    filter_name = select.get('data-filter', '') or select.get('name', '')
                    options = [opt.get_text(strip=True) for opt in select.find_all('option')]
                    if filter_name and options:
                        filters_found.append({
                            "name": filter_name,
                            "option_count": len(options),
                            "sample_options": options[:5]
                        })
            
            # Also look for filter labels
            filter_labels = soup.find_all('td', class_='filters-cells')
            for label in filter_labels:
                label_text = label.get_text(strip=True)
                if label_text and len(label_text) < 50:
                    if label_text not in [f.get("name") for f in filters_found]:
                        filters_found.append({"name": label_text, "type": "label"})
            
            result["filters"]["count"] = len(filters_found)
            result["filters"]["categories"] = filters_found[:30]  # First 30
            print(f"   Found {len(filters_found)} filter categories")
            
            # Extract tab structure and column headers for each view
            print("\n📑 Extracting tab structures...")
            
            for tab in screener_tabs:
                tab_url = f"https://finviz.com/screener.ashx?{tab['param']}&ft=4"
                print(f"\n   [{tab['name']}] Navigating...")
                
                await page.goto(tab_url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(2)
                
                tab_html = await page.content()
                tab_soup = BeautifulSoup(tab_html, 'html.parser')
                
                if save_html:
                    tab_html_path = output_dir_path / f"finviz_screener_{tab['name'].lower()}.html"
                    tab_html_path.write_text(tab_html)
                
                # Extract column headers
                headers = []
                header_row = tab_soup.find('tr', class_='table-top')
                if header_row:
                    for th in header_row.find_all(['th', 'td']):
                        header_text = th.get_text(strip=True)
                        if header_text:
                            headers.append(header_text)
                
                # Extract sample data (first 5 rows)
                sample_rows = []
                data_table = tab_soup.find('table', id='screener-table') or tab_soup.find('table', class_='screener_table')
                if not data_table:
                    # Try finding by structure
                    tables = tab_soup.find_all('table')
                    for t in tables:
                        if t.find('tr', class_='table-top'):
                            data_table = t
                            break
                
                if data_table:
                    rows = data_table.find_all('tr', class_=['table-dark-row', 'table-light-row', 'screener-link-primary'])
                    for row in rows[:5]:
                        cells = row.find_all('td')
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if row_data and any(row_data):
                            sample_rows.append(row_data)
                
                result["tabs"][tab["name"]] = {
                    "url_param": tab["param"],
                    "columns": headers,
                    "column_count": len(headers),
                    "sample_rows": sample_rows,
                    "sample_row_count": len(sample_rows)
                }
                
                print(f"   ✓ {tab['name']}: {len(headers)} columns, {len(sample_rows)} sample rows")
            
            await browser.close()
            print("\n✓ Browser closed")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        result["error"] = str(e)
    
    # Save JSON output
    json_path = output_dir_path / "finviz_screener_structure.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Saved JSON: {json_path}")
    
    return result


def print_summary(data: dict):
    """Print a formatted summary of extracted data."""
    print(f"\n{'='*70}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n📊 Total Tickers: {data.get('total_tickers', 'Unknown')}")
    
    print(f"\n🔍 Filters: {data.get('filters', {}).get('count', 0)} categories")
    for f in data.get('filters', {}).get('categories', [])[:10]:
        print(f"   - {f.get('name')}")
    
    print(f"\n📑 Tabs Extracted:")
    for tab_name, tab_data in data.get('tabs', {}).items():
        cols = tab_data.get('column_count', 0)
        rows = tab_data.get('sample_row_count', 0)
        print(f"   - {tab_name}: {cols} columns")
        if tab_data.get('columns'):
            print(f"     Columns: {', '.join(tab_data['columns'][:6])}...")


if __name__ == "__main__":
    save_html = "--save-html" in sys.argv
    
    print("\n" + "="*70)
    print("FINVIZ SCREENER DATA EXTRACTION")
    print("="*70)
    
    data = asyncio.run(fetch_finviz_screener(save_html=save_html))
    print_summary(data)
    
    print(f"\n✅ Extraction complete!")
    print(f"   JSON saved to: docs/Ingest/finviz_screener_structure.json")
