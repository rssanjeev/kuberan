#!/usr/bin/env python3
"""
Fetch ALL 3 Finviz financial statement tabs using browser automation.

This script clicks through Income Statement, Balance Sheet, and Cash Flow tabs,
parses the HTML content directly at runtime, and saves only JSON results.

Requirements:
    pip install playwright beautifulsoup4
    playwright install chromium

Usage:
    python3 scripts/fetch_finviz_all_statements.py NVDA
    python3 scripts/fetch_finviz_all_statements.py AAPL
    python3 scripts/fetch_finviz_all_statements.py SNPS
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Import parser from backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.core.finviz_parser import FinvizParser


async def fetch_finviz_all_statements(ticker: str, output_dir: str = "docs/Ingest") -> dict:
    """
    Fetch and parse all Finviz financial data for ticker.
    
    This function:
    1. Loads the Finviz quote page
    2. Scrolls to the statements section
    3. Clicks each of the 3 tabs (Income Statement, Balance Sheet, Cash Flow)
    4. Extracts HTML content for each tab
    5. Parses HTML directly in memory using FinvizParser
    6. Saves only the JSON results (no HTML files)
    
    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL)
        output_dir: Directory to save JSON output
        
    Returns:
        Dict with parsed financial data:
        {
            'ticker': 'NVDA',
            'snapshot': {...},
            'income_statement': {...},
            'balance_sheet': {...},
            'cash_flow': {...},
            'metadata': {...},
            'json_file': 'path/to/ticker_financials.json'
        }
    
    Note:
        No HTML files are saved. All parsing happens in memory at runtime.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Error: Playwright is not installed.")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    # Construct URL
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}&p=d"
    
    print(f"\n{'='*70}")
    print(f"Fetching ALL Financial Statements for {ticker.upper()}")
    print(f"{'='*70}")
    print(f"URL: {url}\n")
    
    # Prepare output directory
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Storage for HTML content (in memory only, not saved to disk)
    html_content = {
        'full_page': '',
        'income_statement': '',
        'balance_sheet': '',
        'cash_flow': ''
    }
    
    try:
        async with async_playwright() as p:
            # Launch browser (headless=False for debugging, set to True for production)
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,  # Set to False to watch the browser work
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic user agent
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # ============================================================
                # STEP 1: Navigate to page and wait for load
                # ============================================================
                print("📄 Step 1: Loading Finviz page...")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                print("   ✓ Page loaded")
                
                # ============================================================
                # STEP 2: Scroll to statements section
                # ============================================================
                print("\n📜 Step 2: Scrolling to statements section...")
                
                # Try clicking "Scroll to Statements" link if it exists
                try:
                    statements_link = await page.query_selector('a[href="#statements"]')
                    if statements_link:
                        await statements_link.click()
                        print("   ✓ Clicked 'Scroll to Statements' link")
                        await page.wait_for_timeout(2000)
                    else:
                        # Alternative: scroll to statements div directly
                        await page.evaluate("window.location.hash = '#statements';")
                        await page.wait_for_timeout(2000)
                        print("   ✓ Scrolled to statements section")
                except Exception as e:
                    print(f"   ⚠️  Scroll method failed: {e}")
                    print("   Trying alternative scroll method...")
                    await page.evaluate("window.scrollTo(0, 3000);")
                    await page.wait_for_timeout(2000)
                
                # ============================================================
                # STEP 3: Wait for statements content to appear
                # ============================================================
                print("\n⏳ Step 3: Waiting for statements content to load...")
                
                try:
                    # Wait for the statements table to appear
                    await page.wait_for_selector('.quote_statements-table', timeout=10000)
                    print("   ✓ Statements table found")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not find statements table: {e}")
                    print("   Continuing anyway...")
                
                await page.wait_for_timeout(2000)
                
                # ============================================================
                # STEP 4: Save full page HTML FIRST (includes snapshot table)
                # ============================================================
                print("\n" + "="*70)
                print("Extracting Full Page with Snapshot Table")
                print("="*70)
                
                print("\n📄 Capturing full page HTML (in memory)...", end=" ", flush=True)
                
                # Get complete page HTML (includes snapshot table at top + statements section)
                full_page_html = await page.content()
                
                # Store in memory (not saved to disk)
                html_content['full_page'] = full_page_html
                
                full_size = len(full_page_html)
                print(f"✓ Captured ({full_size:,} bytes)")
                
                # ============================================================
                # STEP 4.5: Handle Interstitial Ads
                # ============================================================
                print("\n" + "="*70)
                print("Checking for Interstitial Ads")
                print("="*70)
                
                async def dismiss_interstitial_ads():
                    """Detect and dismiss interstitial ads that block interaction."""
                    try:
                        # Check for Google interstitial ad iframes
                        ad_iframes = await page.query_selector_all('iframe[id*="google_ads_iframe"][id*="WebInterstitial"]')
                        
                        if ad_iframes:
                            print(f"\n🚫 Detected {len(ad_iframes)} interstitial ad(s)")
                            
                            # Strategy 1: Try to close via close button
                            print("   🔍 Looking for close button...")
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
                                        print(f"   ✓ Clicked close button: {selector}")
                                        await page.wait_for_timeout(1000)
                                        return True
                                except:
                                    continue
                            
                            # Strategy 2: Try removing ad iframes via JavaScript
                            print("   🔧 Attempting to remove ad iframes via JavaScript...")
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
                                print(f"   ✓ Removed {removed} ad element(s)")
                                await page.wait_for_timeout(1000)
                                return True
                            
                            # Strategy 3: Wait for ad to auto-dismiss (some ads close after 5-10 seconds)
                            print("   ⏳ Waiting 8 seconds for ad to auto-dismiss...")
                            await page.wait_for_timeout(8000)
                            
                            # Check if ad is gone
                            remaining_ads = await page.query_selector_all('iframe[id*="google_ads_iframe"][id*="WebInterstitial"]')
                            if len(remaining_ads) < len(ad_iframes):
                                print(f"   ✓ Ad auto-dismissed ({len(remaining_ads)} remaining)")
                                return True
                            
                            print("   ⚠️  Ad still present, will try forceful clicks")
                            return False
                        else:
                            print("\n✓ No interstitial ads detected")
                            return True
                            
                    except Exception as e:
                        print(f"   ⚠️  Error handling ads: {e}")
                        return False
                
                # Run ad dismissal
                await dismiss_interstitial_ads()
                
                # ============================================================
                # STEP 5: Extract each statement tab (in memory)
                # ============================================================
                print("\n" + "="*70)
                print("Extracting Financial Statements from Tabs (In Memory)")
                print("="*70)
                
                # Define the 3 tabs we need to extract
                tabs = [
                    {
                        'name': 'Income Statement',
                        'selector': 'a.tab-link:has-text("Income Statement")',
                        'key': 'income_statement'
                    },
                    {
                        'name': 'Balance Sheet',
                        'selector': 'a.tab-link:has-text("Balance Sheet")',
                        'key': 'balance_sheet'
                    },
                    {
                        'name': 'Cash Flow',
                        'selector': 'a.tab-link:has-text("Cash Flow")',
                        'key': 'cash_flow'
                    }
                ]
                
                for i, tab in enumerate(tabs, 1):
                    print(f"\n📊 [{i}/3] Extracting {tab['name']}...")
                    
                    try:
                        # Retry logic with ad detection
                        max_retries = 2
                        success = False
                        
                        for attempt in range(max_retries):
                            try:
                                # Find tab element
                                tab_element = await page.query_selector(tab['selector'])
                                
                                if not tab_element:
                                    print(f"   ❌ Could not find tab: {tab['selector']}")
                                    break
                                
                                # Try to click the tab with reduced timeout (10s instead of 30s)
                                await tab_element.click(timeout=10000)
                                print(f"   ✓ Clicked '{tab['name']}' tab")
                                
                                # Wait for content to update
                                await page.wait_for_timeout(2000)
                                
                                # Extract the statements div HTML (after tab switch)
                                statements_html = await page.evaluate("""
                                    () => {
                                        const statementsDiv = document.getElementById('statements');
                                        return statementsDiv ? statementsDiv.innerHTML : '';
                                    }
                                """)
                                
                                if not statements_html or statements_html.strip() == "":
                                    print(f"   ⚠️  Warning: {tab['name']} content is empty!")
                                    break
                                
                                # Store in memory (not saved to disk)
                                html_content[tab['key']] = statements_html
                                
                                content_size = len(statements_html)
                                print(f"   ✓ Captured ({content_size:,} bytes)")
                                success = True
                                break
                                
                            except Exception as click_error:
                                # Check if ad is blocking
                                if "intercepts pointer events" in str(click_error) and attempt < max_retries - 1:
                                    print(f"   ⚠️  Click blocked (attempt {attempt + 1}/{max_retries}), checking for ads...")
                                    dismissed = await dismiss_interstitial_ads()
                                    if dismissed:
                                        print(f"   🔄 Retrying click after ad dismissal...")
                                        await page.wait_for_timeout(1000)
                                        continue
                                
                                # Last attempt or different error
                                if attempt == max_retries - 1:
                                    print(f"   ❌ Error clicking {tab['name']}: {click_error}")
                                break
                        
                        if not success:
                            print(f"   ⚠️  Skipping {tab['name']} after {max_retries} attempts")
                        
                    except Exception as e:
                        print(f"   ❌ Error extracting {tab['name']}: {e}")
                        continue
                
            finally:
                await browser.close()
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "="*70)
        # ============================================================
        # STEP 6: Parse HTML content directly in memory
        # ============================================================
        print("\n" + "="*70)
        print("Parsing HTML Content (In Memory)")
        print("="*70)
        
        print("\n🔍 Initializing FinvizParser...")
        parser = FinvizParser(
            fullpage_html=html_content['full_page'],
            income_statement_html=html_content['income_statement'],
            balance_sheet_html=html_content['balance_sheet'],
            cash_flow_html=html_content['cash_flow'],
            ticker=ticker
        )
        print("   ✓ Parser initialized")
        
        print("\n📊 Parsing all sections...")
        parsed_data = parser.parse_all()
        print("   ✓ Parsing complete")
        
        # ============================================================
        # STEP 7: Save parsed JSON (only output file)
        # ============================================================
        print("\n" + "="*70)
        print("Saving JSON Results")
        print("="*70)
        
        json_filename = f"{ticker.lower()}_financials.json"
        json_path = output_dir_path / json_filename
        
        print(f"\n💾 Writing JSON to {json_path.name}...", end=" ", flush=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        json_size = json_path.stat().st_size
        print(f"✓ Saved ({json_size:,} bytes)")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "="*70)
        print("✅ EXTRACTION & PARSING COMPLETE")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Timestamp: {timestamp}")
        
        print(f"\n📊 Data Summary:")
        print(f"  • Ticker: {parsed_data.get('ticker', 'N/A')}")
        print(f"  • Snapshot Metrics: {len(parsed_data.get('snapshot', {}))}")
        print(f"  • Income Statement Periods: {len(parsed_data.get('income_statement', {}))}")
        print(f"  • Balance Sheet Periods: {len(parsed_data.get('balance_sheet', {}))}")
        print(f"  • Cash Flow Periods: {len(parsed_data.get('cash_flow', {}))}")
        
        print(f"\n💾 Output:")
        print(f"  • JSON File: {json_filename} ({json_size:,} bytes)")
        print(f"  • Location: {json_path}")
        
        # Add JSON path to result
        parsed_data['json_file'] = str(json_path)
        
        return parsed_data
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fetch_finviz_all_statements.py TICKER [OUTPUT_DIR]")
        print("\nExamples:")
        print("  python3 scripts/fetch_finviz_all_statements.py NVDA")
        print("  python3 scripts/fetch_finviz_all_statements.py AAPL docs/Ingest")
        print("  python3 scripts/fetch_finviz_all_statements.py SNPS")
        sys.exit(1)
    
    ticker = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "docs/Ingest"
    
    # Run the async function and capture result
    result = asyncio.run(fetch_finviz_all_statements(ticker, output_dir))
    
    if result and 'json_file' in result:
        print(f"\n✅ Success! JSON saved to: {result['json_file']}")
    else:
        print("\n⚠️  Warning: Extraction completed but no JSON file path returned")


if __name__ == "__main__":
    main()
