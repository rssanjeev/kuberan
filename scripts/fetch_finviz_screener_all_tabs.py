#!/usr/bin/env python3
"""
FinViz Screener - Ticker-Centric Extractor (Cartographer/Miner)

Extracts data from all 6 tabs of the FinViz screener and organizes it
by TICKER (not by tab). Each ticker gets its own complete data record
following the same pattern as the quote page financials extraction.

Each tab provides different columns of data:
- Overview (v=111): Company, Sector, Industry, Country, Market Cap, P/E, Price, Volume
- Valuation (v=121): P/E, Fwd P/E, PEG, P/S, P/B, P/C, P/FCF, EPS growth metrics
- Financial (v=161): Dividend, ROA, ROE, ROIC, Margins, Debt ratios
- Ownership (v=131): Outstanding, Float, Insider/Inst ownership, Short metrics
- Performance (v=141): Week/Month/Quarter/Year/3Y/5Y/10Y performance, Volatility
- Technical (v=171): Beta, ATR, SMA20/50/200, 52W High/Low, RSI

Output Format (ticker-centric):
{
  "ticker": "AAPL",
  "screener_data": {
    "overview": {"Company": "Apple Inc.", "Sector": "Technology", ...},
    "valuation": {"P/E": "28.5", "Forward P/E": "25.2", ...},
    "financial": {"Dividend": "0.52%", "ROE": "147.2%", ...},
    "ownership": {"Insider Own": "0.07%", "Inst Own": "60.1%", ...},
    "performance": {"Perf Week": "-2.5%", "Perf Month": "5.3%", ...},
    "technical": {"Beta": "1.24", "RSI (14)": "52.3", ...}
  },
  "metadata": {
    "source": "finviz_screener",
    "index_filter": "S&P 500",
    "extracted_at": "2025-12-21T10:30:00"
  }
}

Usage:
    python scripts/fetch_finviz_screener_all_tabs.py [--pages N] [--output-dir DIR]
    
Arguments:
    --pages N         Number of pages to fetch (20 tickers per page), default 1
    --output-dir DIR  Output directory for ticker JSON files
    
Example:
    # Extract S&P 500 (25 pages = ~500 tickers)
    python scripts/fetch_finviz_screener_all_tabs.py --pages 25 --output-dir docs/Ingest/screener/
"""

import asyncio
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


# Tab configurations: (view_code, tab_name)
TABS = {
    "overview": {"v": 111, "name": "Overview"},
    "valuation": {"v": 121, "name": "Valuation"},
    "financial": {"v": 161, "name": "Financial"},
    "ownership": {"v": 131, "name": "Ownership"},
    "performance": {"v": 141, "name": "Performance"},
    "technical": {"v": 171, "name": "Technical"},
}

# Index filters for FinViz screener
# The 'f' parameter with 'idx_' prefix filters by index
INDEX_FILTERS = {
    "sp500": "f=idx_sp500",      # S&P 500 (~500 stocks)
    "djia": "f=idx_dji",          # Dow Jones Industrial Average (~30 stocks)
    "nasdaq100": "f=idx_ndx",     # NASDAQ 100 (~100 stocks)
    "all": "",                     # All US stocks (8000+ stocks)
}

# User agent to avoid blocking
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


async def extract_table_data(html: str) -> tuple[List[str], List[Dict[str, str]]]:
    """
    Extract headers and rows from FinViz screener table.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Tuple of (headers list, list of row dicts)
    """
    from bs4 import BeautifulSoup
    
    # Use lxml parser (faster and commonly available)
    soup = BeautifulSoup(html, 'lxml')
    
    # Find the screener table
    table = soup.find('table', class_='screener_table')
    if not table:
        print("  ⚠️ No screener_table found")
        return [], []
    
    # Extract headers from thead
    headers = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
    
    # Extract data rows from tbody
    rows_data = []
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr', class_='styled-row')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= len(headers):
                row_dict = {}
                for i, cell in enumerate(cells[:len(headers)]):
                    if i < len(headers):
                        row_dict[headers[i]] = cell.get_text(strip=True)
                rows_data.append(row_dict)
    
    return headers, rows_data


async def fetch_tab_page(
    page,
    tab_key: str,
    tab_config: dict,
    page_num: int = 1,
    index_filter: str = "sp500"
) -> tuple[List[str], List[Dict[str, str]]]:
    """
    Fetch a single page of a specific tab.
    
    Args:
        page: Playwright page object
        tab_key: Tab identifier (e.g., "overview")
        tab_config: Tab configuration dict with 'v' (view code)
        page_num: Page number (1-indexed, 20 rows per page)
        index_filter: Index to filter by ("sp500", "djia", "nasdaq100", "all")
        
    Returns:
        Tuple of (headers, rows_data)
    """
    # Calculate row offset (r parameter)
    # Page 1 = r=1, Page 2 = r=21, Page 3 = r=41, etc.
    row_offset = (page_num - 1) * 20 + 1
    
    # Build URL with optional index filter
    filter_param = INDEX_FILTERS.get(index_filter, INDEX_FILTERS["sp500"])
    filter_part = f"&{filter_param}" if filter_param else ""
    url = f"https://finviz.com/screener.ashx?v={tab_config['v']}{filter_part}&r={row_offset}"
    
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)  # Wait for dynamic content
        
        html = await page.content()
        headers, rows = await extract_table_data(html)
        
        return headers, rows
        
    except Exception as e:
        print(f"  ⚠️ Error fetching {tab_config['name']} page {page_num}: {e}")
        return [], []


async def fetch_all_tabs_for_pages(
    pages: int = 1,
    output_dir: Optional[str] = None,
    index_filter: str = "sp500"
) -> Dict[str, Any]:
    """
    Fetch all tabs for specified number of pages and organize by ticker.
    
    Args:
        pages: Number of pages to fetch (20 tickers per page)
        output_dir: Optional output directory for individual ticker files
        index_filter: Index to filter by ("sp500", "djia", "nasdaq100", "all")
        
    Returns:
        Ticker-centric data structure
    """
    from playwright.async_api import async_playwright
    
    # Get human-readable filter name
    filter_names = {
        "sp500": "S&P 500",
        "djia": "Dow Jones Industrial Average",
        "nasdaq100": "NASDAQ 100",
        "all": "All US Stocks"
    }
    
    # Temporary storage: organize by tab first, then pivot to ticker-centric
    raw_data_by_tab = {}
    extraction_timestamp = datetime.now().isoformat()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=USER_AGENT
        )
        page = await context.new_page()
        
        filter_name = filter_names.get(index_filter, index_filter)
        print(f"\n🔍 FinViz Screener - {filter_name}")
        print(f"   Extracting {pages} page(s) × 6 tabs")
        print(f"   Expected tickers: up to {pages * 20}")
        print("=" * 60)
        
        # Fetch each tab
        for tab_key, tab_config in TABS.items():
            print(f"\n📑 Tab: {tab_config['name']} (v={tab_config['v']})")
            
            tab_rows = []
            
            # Fetch all pages for this tab
            for page_num in range(1, pages + 1):
                print(f"   Page {page_num}/{pages}...", end=" ")
                
                headers, rows = await fetch_tab_page(page, tab_key, tab_config, page_num, index_filter)
                
                if rows:
                    tab_rows.extend(rows)
                    print(f"✓ {len(rows)} tickers")
                else:
                    print("⚠️ No data")
                
                # Brief delay between pages
                if page_num < pages:
                    await asyncio.sleep(1)
            
            raw_data_by_tab[tab_key] = tab_rows
            print(f"   Total for {tab_config['name']}: {len(tab_rows)} tickers")
            
            # Brief delay between tabs
            await asyncio.sleep(1)
        
        await browser.close()
    
    # ===== PIVOT: Convert tab-centric to ticker-centric =====
    print("\n" + "=" * 60)
    print("🔄 Pivoting data to ticker-centric format...")
    
    tickers_data = {}
    
    # Process each tab and organize by ticker
    for tab_key, rows in raw_data_by_tab.items():
        for row in rows:
            ticker = row.get("Ticker", "UNKNOWN")
            if ticker == "UNKNOWN":
                continue
                
            # Initialize ticker record if not exists
            if ticker not in tickers_data:
                tickers_data[ticker] = {
                    "ticker": ticker,
                    "screener_data": {
                        "overview": {},
                        "valuation": {},
                        "financial": {},
                        "ownership": {},
                        "performance": {},
                        "technical": {}
                    },
                    "metadata": {
                        "source": "finviz_screener",
                        "index_filter": filter_names.get(index_filter, index_filter),
                        "extracted_at": extraction_timestamp
                    }
                }
            
            # Add this tab's data to the ticker (exclude "Ticker" and "No." columns)
            tab_data = {k: v for k, v in row.items() if k not in ["Ticker", "No."]}
            tickers_data[ticker]["screener_data"][tab_key] = tab_data
    
    # Convert to list
    tickers_list = list(tickers_data.values())
    total_tickers = len(tickers_list)
    
    print(f"   ✓ Organized {total_tickers} tickers")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"   Index Filter: {filter_names.get(index_filter, index_filter)}")
    print(f"   Pages Fetched: {pages}")
    print(f"   Total Tickers: {total_tickers}")
    print(f"   Data per Ticker: 6 tabs (overview, valuation, financial, ownership, performance, technical)")
    
    # Save output
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual ticker files
        print(f"\n💾 Saving individual ticker files to: {output_dir}")
        for ticker_data in tickers_list:
            ticker = ticker_data["ticker"]
            ticker_file = output_path / f"{ticker.lower()}_screener.json"
            ticker_file.write_text(json.dumps(ticker_data, indent=2, default=str))
        
        # Also save a combined index file
        index_file = output_path / f"_index_{index_filter}.json"
        index_data = {
            "metadata": {
                "source": "finviz_screener",
                "index_filter": filter_names.get(index_filter, index_filter),
                "pages_fetched": pages,
                "total_tickers": total_tickers,
                "extracted_at": extraction_timestamp,
                "tabs": list(TABS.keys())
            },
            "tickers": [t["ticker"] for t in tickers_list]
        }
        index_file.write_text(json.dumps(index_data, indent=2, default=str))
        
        print(f"   ✓ Saved {total_tickers} ticker files")
        print(f"   ✓ Saved index file: {index_file}")
    
    return {
        "metadata": {
            "source": "finviz_screener",
            "index_filter": filter_names.get(index_filter, index_filter),
            "pages_fetched": pages,
            "total_tickers": total_tickers,
            "extracted_at": extraction_timestamp
        },
        "tickers": tickers_list
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract FinViz screener data - organized by TICKER (not by tab)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Format (ticker-centric):
  Each ticker gets its own JSON file with all 6 tabs of data:
  {
    "ticker": "AAPL",
    "screener_data": {
      "overview": {"Company": "Apple Inc.", "Sector": "Technology", ...},
      "valuation": {"P/E": "28.5", ...},
      "financial": {"Dividend": "0.52%", ...},
      "ownership": {"Insider Own": "0.07%", ...},
      "performance": {"Perf Week": "-2.5%", ...},
      "technical": {"Beta": "1.24", ...}
    },
    "metadata": {...}
  }

Examples:
  # Extract first 25 pages (~500 tickers) of S&P 500
  python scripts/fetch_finviz_screener_all_tabs.py --index sp500 --pages 25
  
  # Extract Dow Jones Industrial Average (only ~2 pages needed)
  python scripts/fetch_finviz_screener_all_tabs.py --index djia --pages 2
  
  # Extract NASDAQ 100 (~5 pages needed)
  python scripts/fetch_finviz_screener_all_tabs.py --index nasdaq100 --pages 5
"""
    )
    parser.add_argument(
        "--index",
        type=str,
        choices=["sp500", "djia", "nasdaq100", "all"],
        default="sp500",
        help="Index to filter by (default: sp500)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch (20 tickers per page, default: 1)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for ticker files (default: docs/Ingest/screener/{index}/)"
    )
    
    args = parser.parse_args()
    
    # Determine output directory
    output_dir = args.output_dir or f"docs/Ingest/screener/{args.index}"
    
    # Run extraction
    asyncio.run(fetch_all_tabs_for_pages(
        pages=args.pages,
        output_dir=output_dir,
        index_filter=args.index
    ))


if __name__ == "__main__":
    main()
