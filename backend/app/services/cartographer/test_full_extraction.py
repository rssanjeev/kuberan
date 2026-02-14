"""
Cartographer Full Extraction Test - FinViz

Last Updated: 2025-12-21
Purpose: Extract ALL fields from FinViz and generate complete dictionary

This script:
1. Visits a FinViz stock page
2. Extracts ALL label/value pairs from snapshot table (66+ fields)
3. Extracts header and classification data
4. Generates a complete dictionary with proper field definitions
5. Saves the results for validation

Usage:
    cd backend
    python3 -m app.services.cartographer.test_full_extraction NVDA
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import async_playwright, Page

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Complete FinViz label → field mapping (66+ fields)
FINVIZ_FIELD_MAP = {
    # === Identification ===
    "Index": {"field_name": "index_membership", "data_type": "string", "category": "identification"},
    
    # === Valuation ===
    "Market Cap": {"field_name": "market_cap", "data_type": "currency", "category": "valuation"},
    "P/E": {"field_name": "pe_ratio", "data_type": "float", "category": "valuation"},
    "Forward P/E": {"field_name": "forward_pe", "data_type": "float", "category": "valuation"},
    "PEG": {"field_name": "peg_ratio", "data_type": "float", "category": "valuation"},
    "P/S": {"field_name": "price_to_sales", "data_type": "float", "category": "valuation"},
    "P/B": {"field_name": "price_to_book", "data_type": "float", "category": "valuation"},
    "P/C": {"field_name": "price_to_cash", "data_type": "float", "category": "valuation"},
    "P/FCF": {"field_name": "price_to_fcf", "data_type": "float", "category": "valuation"},
    
    # === Earnings & Growth ===
    "EPS (ttm)": {"field_name": "eps_ttm", "data_type": "float", "category": "earnings"},
    "EPS next Y": {"field_name": "eps_next_year", "data_type": "float", "category": "earnings"},
    "EPS next Q": {"field_name": "eps_next_quarter", "data_type": "float", "category": "earnings"},
    "EPS this Y": {"field_name": "eps_growth_this_year", "data_type": "percentage", "category": "growth"},
    "EPS next 5Y": {"field_name": "eps_growth_next_5y", "data_type": "percentage", "category": "growth"},
    "EPS past 5Y": {"field_name": "eps_growth_past_5y", "data_type": "percentage", "category": "growth"},
    "Sales past 5Y": {"field_name": "sales_growth_past_5y", "data_type": "percentage", "category": "growth"},
    "Sales Q/Q": {"field_name": "sales_growth_qoq", "data_type": "percentage", "category": "growth"},
    "EPS Q/Q": {"field_name": "eps_growth_qoq", "data_type": "percentage", "category": "growth"},
    
    # === Profitability ===
    "Gross Margin": {"field_name": "gross_margin", "data_type": "percentage", "category": "profitability"},
    "Oper. Margin": {"field_name": "operating_margin", "data_type": "percentage", "category": "profitability"},
    "Profit Margin": {"field_name": "profit_margin", "data_type": "percentage", "category": "profitability"},
    "ROA": {"field_name": "roa", "data_type": "percentage", "category": "profitability"},
    "ROE": {"field_name": "roe", "data_type": "percentage", "category": "profitability"},
    "ROI": {"field_name": "roi", "data_type": "percentage", "category": "profitability"},
    
    # === Balance Sheet ===
    "Current Ratio": {"field_name": "current_ratio", "data_type": "float", "category": "balance_sheet"},
    "Quick Ratio": {"field_name": "quick_ratio", "data_type": "float", "category": "balance_sheet"},
    "LT Debt/Eq": {"field_name": "lt_debt_to_equity", "data_type": "float", "category": "balance_sheet"},
    "Debt/Eq": {"field_name": "debt_to_equity", "data_type": "float", "category": "balance_sheet"},
    "Book/sh": {"field_name": "book_value_per_share", "data_type": "float", "category": "balance_sheet"},
    "Cash/sh": {"field_name": "cash_per_share", "data_type": "float", "category": "balance_sheet"},
    
    # === Dividends ===
    "Dividend": {"field_name": "dividend_amount", "data_type": "float", "category": "dividend"},
    "Dividend %": {"field_name": "dividend_yield", "data_type": "percentage", "category": "dividend"},
    "Payout": {"field_name": "payout_ratio", "data_type": "percentage", "category": "dividend"},
    
    # === Shares & Ownership ===
    "Shs Outstand": {"field_name": "shares_outstanding", "data_type": "currency", "category": "shares"},
    "Shs Float": {"field_name": "shares_float", "data_type": "currency", "category": "shares"},
    "Insider Own": {"field_name": "insider_ownership", "data_type": "percentage", "category": "ownership"},
    "Insider Trans": {"field_name": "insider_transactions", "data_type": "percentage", "category": "ownership"},
    "Inst Own": {"field_name": "institutional_ownership", "data_type": "percentage", "category": "ownership"},
    "Inst Trans": {"field_name": "institutional_transactions", "data_type": "percentage", "category": "ownership"},
    
    # === Short Interest ===
    "Short Float": {"field_name": "short_float", "data_type": "percentage", "category": "short_interest"},
    "Short Ratio": {"field_name": "short_ratio", "data_type": "float", "category": "short_interest"},
    "Short Interest": {"field_name": "short_interest", "data_type": "currency", "category": "short_interest"},
    
    # === Analyst ===
    "Target Price": {"field_name": "target_price", "data_type": "float", "category": "analyst"},
    "Recom": {"field_name": "analyst_recommendation", "data_type": "float", "category": "analyst"},
    
    # === Performance ===
    "Perf Week": {"field_name": "perf_week", "data_type": "percentage", "category": "performance"},
    "Perf Month": {"field_name": "perf_month", "data_type": "percentage", "category": "performance"},
    "Perf Quarter": {"field_name": "perf_quarter", "data_type": "percentage", "category": "performance"},
    "Perf Half Y": {"field_name": "perf_half_year", "data_type": "percentage", "category": "performance"},
    "Perf Year": {"field_name": "perf_year", "data_type": "percentage", "category": "performance"},
    "Perf YTD": {"field_name": "perf_ytd", "data_type": "percentage", "category": "performance"},
    
    # === Technical ===
    "52W High": {"field_name": "high_52w", "data_type": "float", "category": "technical"},
    "52W Low": {"field_name": "low_52w", "data_type": "float", "category": "technical"},
    "52W Range": {"field_name": "range_52w", "data_type": "string", "category": "technical"},
    "SMA20": {"field_name": "sma_20", "data_type": "percentage", "category": "technical"},
    "SMA50": {"field_name": "sma_50", "data_type": "percentage", "category": "technical"},
    "SMA200": {"field_name": "sma_200", "data_type": "percentage", "category": "technical"},
    "RSI (14)": {"field_name": "rsi_14", "data_type": "float", "category": "technical"},
    "ATR": {"field_name": "atr", "data_type": "float", "category": "technical"},
    "Beta": {"field_name": "beta", "data_type": "float", "category": "technical"},
    "Volatility": {"field_name": "volatility", "data_type": "string", "category": "technical"},
    
    # === Volume ===
    "Volume": {"field_name": "volume", "data_type": "integer", "category": "volume"},
    "Avg Volume": {"field_name": "avg_volume", "data_type": "currency", "category": "volume"},
    "Rel Volume": {"field_name": "relative_volume", "data_type": "float", "category": "volume"},
    
    # === Price ===
    "Price": {"field_name": "price", "data_type": "float", "category": "price"},
    "Prev Close": {"field_name": "prev_close", "data_type": "float", "category": "price"},
    "Change": {"field_name": "change", "data_type": "percentage", "category": "price"},
    
    # === Company Info ===
    "Employees": {"field_name": "employees", "data_type": "integer", "category": "company_info"},
    "Optionable": {"field_name": "optionable", "data_type": "string", "category": "company_info"},
    "Shortable": {"field_name": "shortable", "data_type": "string", "category": "company_info"},
    "Earnings": {"field_name": "earnings_date", "data_type": "string", "category": "company_info"},
    "Income": {"field_name": "income", "data_type": "currency", "category": "company_info"},
    "Sales": {"field_name": "sales", "data_type": "currency", "category": "company_info"},
}


class FinVizFullExtractor:
    """Extract ALL fields from a FinViz stock page."""
    
    def __init__(self):
        self.field_map = FINVIZ_FIELD_MAP
    
    async def extract(self, ticker: str, headless: bool = True) -> Dict[str, Any]:
        """
        Extract all data from FinViz quote page.
        
        Args:
            ticker: Stock ticker (e.g., "NVDA")
            headless: Run in headless mode
            
        Returns:
            Complete extraction result
        """
        url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            # Add a realistic user agent to avoid detection
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                print(f"\n→ Navigating to {url}")
                # Use domcontentloaded instead of networkidle (networkidle times out)
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Give page time to render
                await asyncio.sleep(3)
                
                # Try multiple selectors for snapshot table
                selectors_to_try = [
                    "table.snapshot-table2",
                    ".snapshot-table2",
                    "table.js-snapshot-table",
                    ".screener_snapshot-table-wrapper table"
                ]
                
                table_found = False
                for selector in selectors_to_try:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        print(f"✓ Found table with selector: {selector}")
                        table_found = True
                        break
                    except Exception:
                        continue
                
                if not table_found:
                    # Debug: save screenshot and page content
                    screenshot_path = f"/tmp/finviz_debug_{ticker}.png"
                    await page.screenshot(path=screenshot_path)
                    print(f"✗ Table not found. Screenshot saved to {screenshot_path}")
                    
                    # Check page title
                    title = await page.title()
                    print(f"  Page title: {title}")
                    
                    # Check if we got an error page
                    content = await page.content()
                    if "robot" in content.lower() or "captcha" in content.lower():
                        print("  ⚠️  Detected anti-bot protection!")
                    if "not found" in content.lower():
                        print(f"  ⚠️  Ticker {ticker} may not exist!")
                    
                    return {"error": "Snapshot table not found", "ticker": ticker}
                
                print("✓ Page loaded successfully")
                
                # Extract all regions
                result = {
                    "ticker": ticker,
                    "url": url,
                    "extracted_at": datetime.now().isoformat(),
                    "regions": {}
                }
                
                # 1. Extract header
                result["regions"]["header"] = await self._extract_header(page)
                
                # 2. Extract classification
                result["regions"]["classification"] = await self._extract_classification(page)
                
                # 3. Extract snapshot table (all fields)
                snapshot = await self._extract_snapshot_table(page)
                result["regions"]["snapshot_table"] = snapshot
                
                # 4. Summary statistics
                result["stats"] = {
                    "total_fields": len(snapshot),
                    "mapped_fields": sum(1 for v in snapshot.values() if not v.get("_unmapped")),
                    "unmapped_fields": sum(1 for v in snapshot.values() if v.get("_unmapped")),
                    "null_values": sum(1 for v in snapshot.values() if v.get("value") is None)
                }
                
                return result
                
            finally:
                await browser.close()
    
    async def _extract_header(self, page: Page) -> Dict[str, Any]:
        """Extract ticker and company name."""
        result = {}
        
        # Ticker
        ticker_el = await page.query_selector(".quote-header_ticker-wrapper_ticker")
        if ticker_el:
            result["ticker"] = {"raw": await ticker_el.inner_text(), "value": await ticker_el.inner_text()}
        
        # Company name
        name_el = await page.query_selector(".quote-header_ticker-wrapper_company a")
        if name_el:
            result["company_name"] = {"raw": await name_el.inner_text(), "value": await name_el.inner_text()}
        
        return result
    
    async def _extract_classification(self, page: Page) -> Dict[str, Any]:
        """Extract sector, industry, country, exchange."""
        result = {}
        
        # Use href patterns to identify each field
        patterns = [
            ("sector", "sec_"),
            ("industry", "ind_"),
            ("country", "geo_"),
            ("exchange", "exch_")
        ]
        
        for field_name, href_pattern in patterns:
            el = await page.query_selector(f"a[href*='{href_pattern}']")
            if el:
                text = await el.inner_text()
                result[field_name] = {"raw": text, "value": text}
        
        return result
    
    async def _extract_snapshot_table(self, page: Page) -> Dict[str, Any]:
        """Extract ALL label/value pairs from snapshot table."""
        result = {}
        
        # Get all cells in the snapshot table
        # FinViz uses: <td class="snapshot-td2">Label</td><td class="snapshot-td2">Value</td>
        cells = await page.query_selector_all("table.snapshot-table2 td")
        
        # Process pairs
        label_value_pairs = []
        i = 0
        while i < len(cells):
            label_text = await cells[i].inner_text()
            label_text = label_text.strip()
            
            # Check if this is a label (has corresponding value)
            if i + 1 < len(cells):
                value_text = await cells[i + 1].inner_text()
                value_text = value_text.strip()
                
                if label_text and label_text in self.field_map:
                    # Known label - get next cell as value
                    label_value_pairs.append((label_text, value_text))
                    i += 2
                elif label_text and not self._looks_like_value(label_text):
                    # Possible unmapped label
                    label_value_pairs.append((label_text, value_text))
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        # Convert to result dictionary
        for label, raw_value in label_value_pairs:
            config = self.field_map.get(label, {})
            field_name = config.get("field_name", self._normalize_label(label))
            data_type = config.get("data_type", "string")
            category = config.get("category", "unknown")
            
            transformed = self._transform_value(raw_value, data_type)
            
            result[field_name] = {
                "label": label,
                "raw": raw_value,
                "value": transformed,
                "data_type": data_type,
                "category": category,
                "_unmapped": label not in self.field_map
            }
        
        return result
    
    def _looks_like_value(self, text: str) -> bool:
        """Check if text looks like a value rather than a label."""
        # Values typically have numbers, percentages, or currency
        return bool(re.search(r'[\d%$]', text)) or text in ["-", "N/A", "Yes", "No"]
    
    def _normalize_label(self, label: str) -> str:
        """Normalize a label to a valid field name."""
        label = re.sub(r'\([^)]*\)', '', label)
        label = re.sub(r'[^a-zA-Z0-9]+', '_', label)
        return label.lower().strip('_')
    
    def _transform_value(self, raw_value: str, data_type: str) -> Any:
        """Transform raw string to typed value."""
        if raw_value in ["-", "N/A", "", None]:
            return None
        
        try:
            if data_type == "float":
                return self._parse_float(raw_value)
            elif data_type == "integer":
                return self._parse_integer(raw_value)
            elif data_type == "percentage":
                return self._parse_percentage(raw_value)
            elif data_type == "currency":
                return self._parse_currency(raw_value)
            else:
                return raw_value
        except Exception:
            return raw_value
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse a float value."""
        cleaned = re.sub(r'[,$%]', '', value)
        return float(cleaned)
    
    def _parse_integer(self, value: str) -> Optional[int]:
        """Parse an integer value with K/M/B suffixes."""
        value = value.upper().replace(',', '')
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, 'T': 1_000_000_000_000}
        
        for suffix, mult in multipliers.items():
            if value.endswith(suffix):
                return int(float(value[:-1]) * mult)
        
        return int(float(value))
    
    def _parse_percentage(self, value: str) -> Optional[float]:
        """Parse a percentage value."""
        cleaned = value.replace('%', '').replace(',', '')
        return float(cleaned)
    
    def _parse_currency(self, value: str) -> Any:
        """Parse a currency value with suffixes."""
        value = value.upper().replace(',', '').replace('$', '')
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, 'T': 1_000_000_000_000}
        
        for suffix, mult in multipliers.items():
            if value.endswith(suffix):
                return float(value[:-1]) * mult
        
        return float(value)


def generate_complete_dictionary(extraction_result: Dict) -> Dict:
    """
    Generate a complete site dictionary from extraction results.
    
    This creates a properly formatted dictionary with all 66+ fields
    that can be used by the Cartographer extractor.
    """
    snapshot_data = extraction_result.get("regions", {}).get("snapshot_table", {})
    
    # Build parsing rules from extracted data
    parsing_rules = []
    
    for field_name, field_data in snapshot_data.items():
        rule = {
            "field_name": field_name,
            "label_text": field_data.get("label"),
            "selector": {
                "primary": None,  # Use label-based matching
                "fallbacks": [],
                "selector_type": "label"
            },
            "data_type": field_data.get("data_type", "string"),
            "transformation": None,
            "required": False,
            "paywalled": False,
            "category": field_data.get("category", "unknown")
        }
        parsing_rules.append(rule)
    
    # Sort by category then field name
    parsing_rules.sort(key=lambda x: (x.get("category", "z"), x.get("field_name", "")))
    
    dictionary = {
        "site_name": "finviz",
        "base_url": "https://finviz.com",
        "generated_at": datetime.now().isoformat(),
        "field_count": len(parsing_rules),
        "templates": {
            "stock_page": {
                "signature": {
                    "name": "stock_page",
                    "url_pattern": r"^https://finviz\.com/quote\.ashx\?t=[A-Z]+",
                    "required_elements": ["table.snapshot-table2"],
                    "forbidden_elements": [".error-page", ".ticker-not-found"]
                },
                "regions": [
                    {
                        "region_id": "header",
                        "description": "Ticker and company name",
                        "container_selector": "table.fullview-title",
                        "extraction_mode": "selector",
                        "parsing_rules": [
                            {
                                "field_name": "ticker",
                                "label_text": None,
                                "selector": {
                                    "primary": ".quote-header_ticker-wrapper_ticker",
                                    "fallbacks": ["h1 a", "a.tab-link"],
                                    "selector_type": "css"
                                },
                                "data_type": "string",
                                "required": True
                            },
                            {
                                "field_name": "company_name",
                                "label_text": None,
                                "selector": {
                                    "primary": ".quote-header_ticker-wrapper_company a",
                                    "fallbacks": ["h2", ".fullview-title a"],
                                    "selector_type": "css"
                                },
                                "data_type": "string",
                                "required": True
                            }
                        ]
                    },
                    {
                        "region_id": "classification",
                        "description": "Sector, industry, country, exchange",
                        "container_selector": "table.fullview-links",
                        "extraction_mode": "selector",
                        "parsing_rules": [
                            {
                                "field_name": "sector",
                                "selector": {"primary": "a[href*='sec_']", "fallbacks": [], "selector_type": "css"},
                                "data_type": "string",
                                "required": False
                            },
                            {
                                "field_name": "industry",
                                "selector": {"primary": "a[href*='ind_']", "fallbacks": [], "selector_type": "css"},
                                "data_type": "string",
                                "required": False
                            },
                            {
                                "field_name": "country",
                                "selector": {"primary": "a[href*='geo_']", "fallbacks": [], "selector_type": "css"},
                                "data_type": "string",
                                "required": False
                            },
                            {
                                "field_name": "exchange",
                                "selector": {"primary": "a[href*='exch_']", "fallbacks": [], "selector_type": "css"},
                                "data_type": "string",
                                "required": False
                            }
                        ]
                    },
                    {
                        "region_id": "snapshot_table",
                        "description": "Main fundamentals table with 66+ metrics",
                        "container_selector": "table.snapshot-table2",
                        "extraction_mode": "label_based",
                        "label_based": {
                            "label_selector": "table.snapshot-table2 td",
                            "value_position": "next_sibling",
                            "include_unmapped": True,
                            "label_mapping": {
                                label: {
                                    "field_name": config["field_name"],
                                    "data_type": config["data_type"],
                                    "category": config["category"]
                                }
                                for label, config in FINVIZ_FIELD_MAP.items()
                            }
                        },
                        "parsing_rules": parsing_rules
                    }
                ],
                "interceptors": ["cookie_banner", "ad_overlay"]
            }
        },
        "interceptors": [
            {
                "name": "cookie_banner",
                "trigger_selector": ".cookie-banner, .gdpr-consent",
                "action": "click",
                "target_selector": ".accept-button, .consent-accept",
                "timeout_ms": 2000,
                "priority": 10
            },
            {
                "name": "ad_overlay",
                "trigger_selector": ".ad-overlay, .modal-backdrop",
                "action": "close",
                "target_selector": ".close-button, [aria-label='Close']",
                "timeout_ms": 1000,
                "priority": 20
            }
        ],
        "metadata": {
            "version": "2.0",
            "extraction_mode": "label_based",
            "categories": list(set(c.get("category") for c in FINVIZ_FIELD_MAP.values()))
        }
    }
    
    return dictionary


async def main():
    """Run full extraction test."""
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    
    print("\n" + "="*70)
    print("FINVIZ FULL EXTRACTION TEST")
    print("="*70)
    
    # Step 1: Extract data
    print(f"\n[Step 1] Extracting all fields for {ticker}")
    print("-" * 70)
    
    extractor = FinVizFullExtractor()
    result = await extractor.extract(ticker, headless=True)
    
    print(f"\n✓ Extraction complete!")
    print(f"  - Total fields: {result['stats']['total_fields']}")
    print(f"  - Mapped fields: {result['stats']['mapped_fields']}")
    print(f"  - Unmapped fields: {result['stats']['unmapped_fields']}")
    print(f"  - Null values: {result['stats']['null_values']}")
    
    # Step 2: Display extracted data by category
    print(f"\n[Step 2] Extracted Data by Category")
    print("-" * 70)
    
    snapshot = result["regions"]["snapshot_table"]
    categories = {}
    for field_name, data in snapshot.items():
        cat = data.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((field_name, data))
    
    for cat in sorted(categories.keys()):
        print(f"\n  [{cat.upper()}]")
        for field_name, data in sorted(categories[cat], key=lambda x: x[0]):
            value = data.get("value")
            raw = data.get("raw", "")
            if value is not None:
                if isinstance(value, float) and value > 1_000_000:
                    display = f"{value/1_000_000_000:.2f}B" if value >= 1_000_000_000 else f"{value/1_000_000:.2f}M"
                else:
                    display = str(value)
            else:
                display = "N/A"
            unmapped = " [UNMAPPED]" if data.get("_unmapped") else ""
            print(f"    {field_name}: {display} (raw: {raw}){unmapped}")
    
    # Step 3: Save extraction result
    print(f"\n[Step 3] Saving Results")
    print("-" * 70)
    
    output_dir = Path(__file__).parent / "configs"
    output_dir.mkdir(exist_ok=True)
    
    # Save raw extraction
    extraction_path = output_dir / f"finviz_extraction_{ticker.lower()}.json"
    with open(extraction_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"✓ Extraction saved: {extraction_path}")
    
    # Step 4: Generate complete dictionary
    print(f"\n[Step 4] Generating Complete Dictionary")
    print("-" * 70)
    
    dictionary = generate_complete_dictionary(result)
    
    dict_path = output_dir / "finviz_dictionary_complete.json"
    with open(dict_path, "w") as f:
        json.dump(dictionary, f, indent=2)
    print(f"✓ Dictionary saved: {dict_path}")
    print(f"  - Total field definitions: {dictionary['field_count']}")
    print(f"  - Categories: {', '.join(dictionary['metadata']['categories'])}")
    
    # Step 5: Summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"""
✓ Successfully extracted {result['stats']['total_fields']} fields from FinViz
✓ {result['stats']['mapped_fields']} fields mapped to standardized names
✓ {result['stats']['unmapped_fields']} new/unmapped fields discovered
✓ Complete dictionary generated with label-based extraction

Output Files:
  1. {extraction_path} - Raw extraction data
  2. {dict_path} - Complete site dictionary

Next Steps:
  1. Review extraction results for accuracy
  2. Add any missing field mappings to FINVIZ_FIELD_MAP
  3. Replace finviz_dictionary.json with finviz_dictionary_complete.json
  4. Test extraction with multiple tickers
""")


if __name__ == "__main__":
    asyncio.run(main())
