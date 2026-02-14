#!/usr/bin/env python3
"""
FinViz Unified Data Extractor

A single entry point for both FinViz data extraction pipelines:
1. Screener Pipeline: Bulk extraction (20 tickers per page, 6 tabs)
2. Quote Page Pipeline: Detailed extraction (1 ticker at a time, financial statements)

Data is saved directly to MongoDB using the FinvizSnapshot model.

Usage:
    # Screener only (bulk extraction)
    python3 scripts/finviz_extract.py --source screener --pages 1
    
    # Quote page only (specific tickers)
    python3 scripts/finviz_extract.py --source quote --tickers AAPL NVDA MSFT
    
    # Both pipelines (screener first, then quote for extracted tickers)
    python3 scripts/finviz_extract.py --source both --pages 1
    
    # Filter by index
    python3 scripts/finviz_extract.py --source screener --index sp500 --pages 25
    
    # Save to files only (skip MongoDB)
    python3 scripts/finviz_extract.py --source screener --pages 1 --no-db

Arguments:
    --source        Pipeline to run: screener, quote, or both (required)
    --index         Index filter: all, sp500, djia, nasdaq100 (default: all)
    --pages         Number of screener pages (20 tickers per page)
    --tickers       Specific tickers for quote extraction (space-separated)
    --no-confirm    Skip confirmation prompt when using --source both
"""

import argparse
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie


# =============================================================================
# CONFIGURATION
# =============================================================================

# Tab configurations for screener
SCREENER_TABS = {
    "overview": {"v": 111, "name": "Overview"},
    "valuation": {"v": 121, "name": "Valuation"},
    "financial": {"v": 161, "name": "Financial"},
    "ownership": {"v": 131, "name": "Ownership"},
    "performance": {"v": 141, "name": "Performance"},
    "technical": {"v": 171, "name": "Technical"},
}

# Index filters for FinViz screener
INDEX_FILTERS = {
    "all": "",                     # All US stocks (8000+ stocks) - DEFAULT
    "sp500": "f=idx_sp500",        # S&P 500 (~500 stocks)
    "djia": "f=idx_dji",           # Dow Jones Industrial Average (~30 stocks)
    "nasdaq100": "f=idx_ndx",      # NASDAQ 100 (~100 stocks)
}

INDEX_DISPLAY_NAMES = {
    "all": "All US Stocks",
    "sp500": "S&P 500",
    "djia": "Dow Jones Industrial Average",
    "nasdaq100": "NASDAQ 100",
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# MongoDB connection URI (default to Docker Compose service)
MONGODB_URI = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "kuberan")


# =============================================================================
# MONGODB INTEGRATION
# =============================================================================

async def init_mongodb():
    """Initialize MongoDB connection with Beanie ODM."""
    from app.models.cartographer import FinvizSnapshot
    
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    await init_beanie(
        database=db,
        document_models=[FinvizSnapshot]
    )
    
    return client


def screener_data_to_snapshot(ticker_data: Dict[str, Any]) -> "FinvizSnapshot":
    """
    Convert screener pipeline data to FinvizSnapshot model.
    
    Maps data from 6 tabs (overview, valuation, financial, ownership, 
    performance, technical) to structured snapshot fields.
    """
    from app.models.cartographer import (
        FinvizSnapshot,
        FinvizIdentity,
        FinvizPrice,
        FinvizValuation,
        FinvizFinancials,
        FinvizProfitability,
        FinvizLiquidity,
        FinvizDividend,
        FinvizGrowth,
        FinvizOwnership,
        FinvizTechnical,
        FinvizPerformance,
        FinvizSourceInfo,
    )
    
    ticker = ticker_data.get("ticker", "")
    screener = ticker_data.get("screener_data", {})
    metadata = ticker_data.get("metadata", {})
    
    # Helper to get value from any tab
    def get_field(field_name: str, tabs: List[str] = None) -> Optional[str]:
        tabs = tabs or list(screener.keys())
        for tab in tabs:
            if tab in screener and field_name in screener[tab]:
                val = screener[tab][field_name]
                if val and val != "-":
                    return val
        return None
    
    def parse_float(val: str) -> Optional[float]:
        if not val or val == "-":
            return None
        try:
            # Remove commas and percentage signs
            clean = val.replace(",", "").replace("%", "").replace("$", "")
            return float(clean)
        except:
            return None
    
    # Build structured sections
    identity = FinvizIdentity(
        ticker=ticker,
        company_name=get_field("Company"),
        sector=get_field("Sector"),
        industry=get_field("Industry"),
        country=get_field("Country"),
        exchange=None,  # Not in screener data
    )
    
    price = FinvizPrice(
        price=parse_float(get_field("Price")),
        change_pct=get_field("Change"),
        volume=parse_int(get_field("Volume")),
        avg_volume=get_field("Avg Volume"),
        rel_volume=parse_float(get_field("Rel Volume")),
        prev_close=None,  # Not in screener (quote_page only)
    )
    
    valuation = FinvizValuation(
        market_cap=get_field("Market Cap"),
        pe=parse_float(get_field("P/E")),
        forward_pe=parse_float(get_field("Fwd P/E")),  # Screener uses abbreviated header
        peg=parse_float(get_field("PEG")),
        ps=parse_float(get_field("P/S")),
        pb=parse_float(get_field("P/B")),
        pc=parse_float(get_field("P/C")),
        p_fcf=parse_float(get_field("P/FCF")),  # Screener uses abbreviated header
        enterprise_value=None,  # Not in screener
    )
    
    financials = FinvizFinancials(
        eps_ttm=None,  # Not in screener (quote_page only)
        eps_next_y=None,  # EPS value not in screener (growth % is)
        eps_next_q=None,  # Not in screener (quote_page only)
        eps_this_y=get_field("EPS This Y"),  # This is growth %, capitalized in screener
        eps_growth_next_y=get_field("EPS Next Y"),  # Growth %, capitalized in screener
        eps_growth_next_5y=get_field("EPS Next 5Y"),  # Capitalized in screener
        eps_growth_past_5y=get_field("EPS Past 5Y"),  # Capitalized in screener
        sales_past_5y=get_field("Sales Past 5Y"),  # Capitalized in screener
        sales_qq=None,  # Not in screener (quote_page only)
        eps_qq=None,  # Not in screener (quote_page only)
    )
    
    profitability = FinvizProfitability(
        gross_margin=get_field("Gross M"),  # Screener uses abbreviated header
        oper_margin=get_field("Oper M"),  # Screener uses abbreviated header
        profit_margin=get_field("Profit M"),  # Screener uses abbreviated header
        roa=get_field("ROA"),
        roe=get_field("ROE"),
        roi=get_field("ROIC"),  # Screener uses ROIC, not ROI
    )
    
    liquidity = FinvizLiquidity(
        current_ratio=parse_float(get_field("Curr R")),  # Screener uses abbreviated header
        quick_ratio=parse_float(get_field("Quick R")),  # Screener uses abbreviated header
        debt_eq=parse_float(get_field("Debt/Eq")),
        lt_debt_eq=parse_float(get_field("LTDebt/Eq")),  # No space in screener
    )
    
    dividend = FinvizDividend(
        dividend_yield=get_field("Dividend"),  # Screener uses "Dividend", not "Dividend %"
        dividend=None,  # This is the TTM value, quote_page only
        payout_ratio=None,  # "Payout" is quote_page only
    )
    
    growth = FinvizGrowth(
        eps_this_y=get_field("EPS This Y"),  # Capitalized in screener
        eps_next_y=get_field("EPS Next Y"),  # Capitalized in screener
        eps_next_5y=get_field("EPS Next 5Y"),  # Capitalized in screener
        eps_past_5y=get_field("EPS Past 5Y"),  # Capitalized in screener
        sales_past_5y=get_field("Sales Past 5Y"),  # Capitalized in screener
        sales_qq=None,  # Not in screener (quote_page only)
        eps_qq=None,  # Not in screener (quote_page only)
    )
    
    ownership = FinvizOwnership(
        insider_ownership=get_field("Insider Own"),
        insider_transactions=get_field("Insider Trans"),
        institutional_ownership=get_field("Inst Own"),
        institutional_transactions=get_field("Inst Trans"),
        shares_outstanding=get_field("Outstanding"),  # Screener uses "Outstanding"
        shares_float=get_field("Float"),  # Screener uses "Float"
        short_float=get_field("Short Float"),
        short_ratio=parse_float(get_field("Short Ratio")),
    )
    
    technical = FinvizTechnical(
        beta=parse_float(get_field("Beta")),
        atr=parse_float(get_field("ATR")),
        volatility_week=get_field("Volatility W"),  # Screener uses "Volatility W"
        rsi_14=parse_float(get_field("RSI")),  # Screener uses "RSI", not "RSI (14)"
        sma_20=get_field("SMA20"),
        sma_50=get_field("SMA50"),
        sma_200=get_field("SMA200"),
        high_52w=parse_float(get_field("52W High")),
        low_52w=parse_float(get_field("52W Low")),
        from_high_52w=get_field("52W Range"),
        recom=None,  # Not in screener (quote_page only)
        target_price=None,  # Not in screener (quote_page only)
    )
    
    performance = FinvizPerformance(
        perf_week=get_field("Perf Week"),
        perf_month=get_field("Perf Month"),
        perf_quarter=get_field("Perf Quart"),  # Screener uses abbreviated header
        perf_half_year=get_field("Perf Half"),  # Screener uses abbreviated header
        perf_year=get_field("Perf Year"),
        perf_ytd=get_field("Perf YTD"),
    )
    
    # Count non-None fields in screener
    screener_fields_count = sum(
        1 for tab in screener.values() 
        for v in (tab.values() if isinstance(tab, dict) else [])
        if v and v != "-"
    )
    
    source = FinvizSourceInfo(
        screener_collected_at=datetime.now(),
        screener_tab=metadata.get("index_filter", "all"),
        screener_fields_count=screener_fields_count,
        is_complete=False,  # Quote page not yet collected
    )
    
    return FinvizSnapshot(
        ticker=ticker,
        entity_type="stock",  # Default; can be updated later
        identity=identity,
        price=price,
        valuation=valuation,
        financials=financials,
        profitability=profitability,
        liquidity=liquidity,
        dividend=dividend,
        growth=growth,
        ownership=ownership,
        technical=technical,
        performance=performance,
        source=source,
        extra_fields={},  # Raw screener data could be stored here if needed
        page_url=f"https://finviz.com/quote.ashx?t={ticker}",
    )


async def save_snapshots_to_mongodb(
    snapshots: List["FinvizSnapshot"],
    upsert: bool = True
) -> Dict[str, int]:
    """
    Save FinvizSnapshot documents to MongoDB.
    
    If upsert=True, updates existing documents for the same ticker.
    Returns stats on saved/updated documents.
    """
    from app.models.cartographer import FinvizSnapshot
    
    stats = {"inserted": 0, "updated": 0, "errors": 0}
    
    for snapshot in snapshots:
        try:
            if upsert:
                # Find existing document for this ticker
                existing = await FinvizSnapshot.find_one(
                    FinvizSnapshot.ticker == snapshot.ticker
                )
                
                if existing:
                    # Update existing document, preserving quote_page data if present
                    existing.identity = snapshot.identity
                    existing.price = snapshot.price
                    existing.valuation = snapshot.valuation
                    existing.financials = snapshot.financials
                    existing.profitability = snapshot.profitability
                    existing.liquidity = snapshot.liquidity
                    existing.dividend = snapshot.dividend
                    existing.growth = snapshot.growth
                    existing.ownership = snapshot.ownership
                    existing.technical = snapshot.technical
                    existing.performance = snapshot.performance
                    existing.source.screener_collected_at = snapshot.source.screener_collected_at
                    existing.source.screener_tab = snapshot.source.screener_tab
                    existing.source.screener_fields_count = snapshot.source.screener_fields_count
                    existing.as_of = datetime.now()
                    
                    await existing.save()
                    stats["updated"] += 1
                else:
                    await snapshot.insert()
                    stats["inserted"] += 1
            else:
                await snapshot.insert()
                stats["inserted"] += 1
                
        except Exception as e:
            print(f"      ❌ Error saving {snapshot.ticker}: {e}")
            stats["errors"] += 1
    
    return stats


# =============================================================================
# SCREENER PIPELINE
# =============================================================================

async def extract_screener_table_data(html: str) -> tuple[List[str], List[Dict[str, str]]]:
    """Extract headers and rows from FinViz screener table."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', class_='screener_table')
    
    if not table:
        print("  ⚠️ No screener_table found")
        return [], []
    
    # Extract headers
    headers = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    
    # Extract data rows
    rows_data = []
    tbody = table.find('tbody')
    if tbody:
        for row in tbody.find_all('tr'):
            cells = row.find_all('td')
            if cells and len(cells) == len(headers):
                row_dict = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
                rows_data.append(row_dict)
    
    return headers, rows_data


async def fetch_screener_tab_page(
    page,
    tab_key: str,
    tab_config: dict,
    page_num: int = 1,
    index_filter: str = "all"
) -> tuple[List[str], List[Dict[str, str]]]:
    """Fetch a single page of a specific screener tab."""
    row_offset = (page_num - 1) * 20 + 1
    
    filter_param = INDEX_FILTERS.get(index_filter, INDEX_FILTERS["all"])
    filter_part = f"&{filter_param}" if filter_param else ""
    url = f"https://finviz.com/screener.ashx?v={tab_config['v']}{filter_part}&r={row_offset}"
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        headers, rows = await extract_screener_table_data(html)
        
        return headers, rows
        
    except Exception as e:
        print(f"  ❌ Error fetching {tab_key} page {page_num}: {e}")
        return [], []


async def run_screener_pipeline(
    pages: int = 1,
    index_filter: str = "all"
) -> Dict[str, Any]:
    """
    Run the screener pipeline to extract data from all 6 tabs.
    
    Args:
        pages: Number of screener pages to fetch (20 tickers per page)
        index_filter: Index filter (all, sp500, djia, nasdaq100)
    
    Returns:
        Dict with tickers list and metadata
    """
    from playwright.async_api import async_playwright
    
    print("\n" + "=" * 70)
    print("🔍 FINVIZ SCREENER PIPELINE")
    print("=" * 70)
    print(f"   Index Filter: {INDEX_DISPLAY_NAMES.get(index_filter, index_filter)}")
    print(f"   Pages to Fetch: {pages} (up to {pages * 20} tickers)")
    print(f"   Tabs: {', '.join(SCREENER_TABS.keys())}")
    
    raw_data_by_tab = {}
    extraction_timestamp = datetime.now().isoformat()
    
    async with async_playwright() as p:
        print("\n🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=USER_AGENT
        )
        page = await context.new_page()
        print("   ✓ Browser ready")
        
        try:
            for tab_key, tab_config in SCREENER_TABS.items():
                print(f"\n📊 Extracting {tab_config['name']} tab...")
                
                all_rows = []
                for page_num in range(1, pages + 1):
                    print(f"   Page {page_num}/{pages}...", end=" ", flush=True)
                    headers, rows = await fetch_screener_tab_page(
                        page, tab_key, tab_config, page_num, index_filter
                    )
                    
                    if rows:
                        all_rows.extend(rows)
                        print(f"✓ {len(rows)} rows")
                    else:
                        print("⚠️ No data")
                        break
                
                raw_data_by_tab[tab_key] = all_rows
                print(f"   Total {tab_config['name']}: {len(all_rows)} rows")
                
        finally:
            await browser.close()
    
    # Pivot to ticker-centric format
    print("\n🔄 Pivoting to ticker-centric format...")
    tickers_data = {}
    
    for tab_key, rows in raw_data_by_tab.items():
        for row in rows:
            ticker = row.get("Ticker", "")
            if not ticker:
                continue
            
            if ticker not in tickers_data:
                tickers_data[ticker] = {
                    "ticker": ticker,
                    "screener_data": {},
                    "metadata": {
                        "source": "finviz_screener",
                        "index_filter": INDEX_DISPLAY_NAMES.get(index_filter, index_filter),
                        "extracted_at": extraction_timestamp
                    }
                }
            
            tickers_data[ticker]["screener_data"][tab_key] = row
    
    tickers_list = list(tickers_data.values())
    total_tickers = len(tickers_list)
    
    print(f"   ✓ Organized {total_tickers} tickers")
    
    # Save to MongoDB
    db_stats = {"inserted": 0, "updated": 0, "errors": 0}
    print(f"\n💾 Saving to MongoDB...")
    try:
        snapshots = [screener_data_to_snapshot(td) for td in tickers_list]
        db_stats = await save_snapshots_to_mongodb(snapshots)
        print(f"   ✓ MongoDB: {db_stats['inserted']} inserted, {db_stats['updated']} updated")
        if db_stats['errors'] > 0:
            print(f"   ⚠️ {db_stats['errors']} errors during save")
    except Exception as e:
        print(f"   ❌ MongoDB save failed: {e}")
        db_stats["errors"] = total_tickers
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SCREENER PIPELINE COMPLETE")
    print("=" * 70)
    print(f"   Index: {INDEX_DISPLAY_NAMES.get(index_filter, index_filter)}")
    print(f"   Pages Fetched: {pages}")
    print(f"   Tickers Extracted: {total_tickers}")
    print(f"   MongoDB: {db_stats['inserted']} new, {db_stats['updated']} updated")
    
    return {
        "metadata": {
            "source": "finviz_screener",
            "index_filter": index_filter,
            "pages_fetched": pages,
            "total_tickers": total_tickers,
            "extracted_at": extraction_timestamp,
            "db_stats": db_stats
        },
        "tickers": tickers_list
    }


# =============================================================================
# QUOTE PAGE PIPELINE
# =============================================================================

async def dismiss_interstitial_ads(page) -> bool:
    """
    Detect and dismiss interstitial ads that block interaction.
    
    Implements 3 strategies:
    1. Click close buttons via CSS selectors
    2. Remove ad iframes via JavaScript
    3. Wait 8 seconds for ad to auto-dismiss
    
    Returns True if no ads or ads were dismissed, False otherwise.
    """
    try:
        # Check for Google interstitial ad iframes
        ad_iframes = await page.query_selector_all('iframe[id*="google_ads_iframe"][id*="WebInterstitial"]')
        
        if ad_iframes:
            print(f"      🚫 Detected {len(ad_iframes)} interstitial ad(s)")
            
            # Strategy 1: Try to close via close button
            close_selectors = [
                'button[aria-label="Close"]',
                'button.close',
                'div.close-button',
                '[id*="close"]',
                '[class*="dismiss"]',
                '[aria-label*="Close"]',
                '[aria-label*="Dismiss"]'
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = await page.query_selector(selector)
                    if close_btn:
                        await close_btn.click()
                        print(f"      ✓ Clicked close button: {selector}")
                        await page.wait_for_timeout(1000)
                        return True
                except:
                    continue
            
            # Strategy 2: Try removing ad iframes via JavaScript
            removed = await page.evaluate("""
                () => {
                    const ads = document.querySelectorAll('iframe[id*="google_ads_iframe"][id*="WebInterstitial"]');
                    const parentContainers = document.querySelectorAll('ins[id*="gpt_unit"]');
                    
                    let count = 0;
                    ads.forEach(ad => {
                        ad.remove();
                        count++;
                    });
                    
                    parentContainers.forEach(container => {
                        if (container.innerHTML.includes('google_ads_iframe')) {
                            container.remove();
                            count++;
                        }
                    });
                    
                    return count;
                }
            """)
            
            if removed > 0:
                print(f"      ✓ Removed {removed} ad element(s)")
                await page.wait_for_timeout(1000)
                return True
            
            # Strategy 3: Wait for ad to auto-dismiss (some ads close after 5-10 seconds)
            print("      ⏳ Waiting 8 seconds for ad to auto-dismiss...")
            await page.wait_for_timeout(8000)
            
            # Check if ad is gone
            remaining_ads = await page.query_selector_all('iframe[id*="google_ads_iframe"][id*="WebInterstitial"]')
            if len(remaining_ads) < len(ad_iframes):
                print(f"      ✓ Ad auto-dismissed ({len(remaining_ads)} remaining)")
                return True
            
            print("      ⚠️ Ad still present, will try forceful clicks")
            return False
        else:
            return True
            
    except Exception as e:
        print(f"      ⚠️ Error handling ads: {e}")
        return False


async def run_quote_pipeline_for_ticker(
    ticker: str
) -> Optional[Dict[str, Any]]:
    """
    Run quote page extraction for a single ticker.
    
    Returns parsed financial data or None on failure.
    """
    from playwright.async_api import async_playwright
    
    # Import parser
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
    from app.core.finviz_parser import FinvizParser
    
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}&p=d"
    
    print(f"\n   📄 Fetching {ticker.upper()}...")
    
    html_content = {
        'full_page': '',
        'income_statement': '',
        'balance_sheet': '',
        'cash_flow': ''
    }
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=USER_AGENT
            )
            page = await context.new_page()
            
            try:
                # Load page
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Get full page HTML for snapshot parsing
                html_content['full_page'] = await page.content()
                
                # Try to scroll to statements section
                try:
                    scroll_link = page.locator('a:has-text("Scroll to Statements")')
                    if await scroll_link.count() > 0:
                        await scroll_link.first.click()
                        await page.wait_for_timeout(1500)
                except:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
                    await page.wait_for_timeout(1000)
                
                # Wait for statements table
                try:
                    await page.wait_for_selector('table.quote_statements-table', timeout=10000)
                except:
                    print(f"      ⚠️ No statements table found for {ticker}")
                
                await page.wait_for_timeout(2000)
                
                # Handle interstitial ads before clicking tabs
                await dismiss_interstitial_ads(page)
                
                # Extract each financial statement tab with retry logic
                tabs = [
                    ("Income Statement", "income_statement"),
                    ("Balance Sheet", "balance_sheet"),
                    ("Cash Flow", "cash_flow")
                ]
                
                for tab_name, tab_key in tabs:
                    max_retries = 2
                    for attempt in range(max_retries):
                        try:
                            tab_link = page.locator(f'a:has-text("{tab_name}")').first
                            if await tab_link.count() > 0:
                                await tab_link.click()
                                await page.wait_for_timeout(2000)
                                html_content[tab_key] = await page.content()
                                break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                # Check for ads on retry
                                await dismiss_interstitial_ads(page)
                                await page.wait_for_timeout(1000)
                            else:
                                print(f"      ⚠️ Could not extract {tab_name}: {e}")
                
            finally:
                await browser.close()
        
        # Parse HTML content
        parser = FinvizParser(
            fullpage_html=html_content['full_page'],
            income_statement_html=html_content['income_statement'],
            balance_sheet_html=html_content['balance_sheet'],
            cash_flow_html=html_content['cash_flow'],
            ticker=ticker
        )
        
        parsed_data = parser.parse_all()
        
        return parsed_data
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return None


async def run_quote_pipeline(
    tickers: List[str]
) -> Dict[str, Any]:
    """
    Run quote page extraction for multiple tickers.
    
    Args:
        tickers: List of ticker symbols to extract
    """
    print("\n" + "=" * 70)
    print("📊 FINVIZ QUOTE PAGE PIPELINE")
    print("=" * 70)
    print(f"   Tickers to Process: {len(tickers)}")
    
    results = []
    success_count = 0
    db_saved_count = 0
    
    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        result = await run_quote_pipeline_for_ticker(ticker)
        if result:
            results.append(result)
            success_count += 1
            
            # Save to MongoDB
            try:
                snapshot = convert_quote_to_snapshot(result)
                await save_snapshots_to_mongodb([snapshot], upsert=True)
                db_saved_count += 1
            except Exception as e:
                print(f"   ⚠️ MongoDB save failed for {ticker}: {e}")
        
        # Small delay between requests
        if i < len(tickers):
            await asyncio.sleep(2)
    
    print("\n" + "=" * 70)
    print("📊 QUOTE PAGE PIPELINE COMPLETE")
    print("=" * 70)
    print(f"   Total Processed: {len(tickers)}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {len(tickers) - success_count}")
    print(f"   Saved to MongoDB: {db_saved_count}")
    
    return {
        "metadata": {
            "source": "finviz_quote_page",
            "total_tickers": len(tickers),
            "successful": success_count,
            "db_saved": db_saved_count,
            "extracted_at": datetime.now().isoformat()
        },
        "results": results
    }


# =============================================================================
# UNIFIED PIPELINE
# =============================================================================

async def run_both_pipelines(
    pages: int = 1,
    index_filter: str = "all",
    no_confirm: bool = False
) -> Dict[str, Any]:
    """
    Run both pipelines: screener first, then quote page for extracted tickers.
    """
    # Step 1: Run screener pipeline
    screener_result = await run_screener_pipeline(
        pages=pages,
        index_filter=index_filter
    )
    
    # Get list of tickers from screener
    tickers = [t["ticker"] for t in screener_result.get("tickers", [])]
    
    if not tickers:
        print("\n⚠️ No tickers extracted from screener. Quote pipeline skipped.")
        return {"screener": screener_result, "quote": None}
    
    # Step 2: Ask for permission to continue
    print("\n" + "=" * 70)
    print("🔄 SCREENER COMPLETE - READY FOR QUOTE PAGE EXTRACTION")
    print("=" * 70)
    print(f"\n   Tickers extracted: {len(tickers)}")
    print(f"   Sample: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
    print(f"\n   The quote page pipeline will extract detailed financial data")
    print(f"   (income statement, balance sheet, cash flow) for each ticker.")
    print(f"   This will take approximately {len(tickers) * 5} seconds.")
    
    if not no_confirm:
        print("\n" + "-" * 70)
        response = input("   Continue with quote page extraction? [y/N]: ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("\n   ❌ Quote page extraction cancelled by user.")
            print("   ✓ Screener data has been saved.")
            return {"screener": screener_result, "quote": None, "cancelled": True}
    
    # Step 3: Run quote pipeline
    print("\n   ✓ Proceeding with quote page extraction...")
    quote_result = await run_quote_pipeline(
        tickers=tickers
    )
    
    return {
        "screener": screener_result,
        "quote": quote_result
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="FinViz Unified Data Extractor - Screener and Quote Page pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Screener only - extract first page (20 tickers) from all US stocks
  python3 scripts/finviz_extract.py --source screener --pages 1
  
  # Screener only - extract S&P 500 (25 pages)
  python3 scripts/finviz_extract.py --source screener --index sp500 --pages 25
  
  # Quote page only - specific tickers
  python3 scripts/finviz_extract.py --source quote --tickers AAPL NVDA MSFT
  
  # Both pipelines - screener first, then quote (with confirmation)
  python3 scripts/finviz_extract.py --source both --pages 1
  
  # Both pipelines - skip confirmation prompt
  python3 scripts/finviz_extract.py --source both --pages 1 --no-confirm

Output:
  Screener: docs/Ingest/screener/{index}/{TICKER}_screener.json
  Quote:    docs/Ingest/quote/{ticker}_financials.json
"""
    )
    
    parser.add_argument(
        "--source",
        type=str,
        choices=["screener", "quote", "both"],
        required=True,
        help="Pipeline to run: screener, quote, or both"
    )
    
    parser.add_argument(
        "--index",
        type=str,
        choices=["all", "sp500", "djia", "nasdaq100"],
        default="all",
        help="Index filter for screener (default: all)"
    )
    
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of screener pages to fetch (20 tickers per page, default: 1)"
    )
    
    parser.add_argument(
        "--tickers",
        type=str,
        nargs="+",
        help="Specific tickers for quote extraction (space-separated)"
    )
    
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompt when using --source both"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.source == "quote" and not args.tickers:
        print("❌ Error: --tickers is required when using --source quote")
        print("   Example: --source quote --tickers AAPL NVDA MSFT")
        sys.exit(1)
    
    if args.source == "screener" and args.tickers:
        print("⚠️ Warning: --tickers is ignored when using --source screener")
        print("   Use --index and --pages instead to control which tickers to extract")
    
    # Define async main to keep everything in one event loop
    async def async_main():
        """Run everything in a single event loop to avoid 'Event loop is closed' errors."""
        # Initialize MongoDB
        await init_mongodb()
        
        if args.source == "screener":
            await run_screener_pipeline(
                pages=args.pages,
                index_filter=args.index
            )
            
        elif args.source == "quote":
            await run_quote_pipeline(
                tickers=args.tickers
            )
            
        elif args.source == "both":
            await run_both_pipelines(
                pages=args.pages,
                index_filter=args.index,
                no_confirm=args.no_confirm
            )
    
    # Run everything in a single asyncio.run() call
    try:
        asyncio.run(async_main())
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Extraction cancelled by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
