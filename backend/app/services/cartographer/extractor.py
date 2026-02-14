"""
Cartographer Extractor - Phase 3

Extracts data from web pages using validated site dictionaries.
Supports both selector-based and label-based extraction modes.

Usage:
    extractor = CartographerExtractor()
    data = await extractor.extract("finviz", "stock_page", {"ticker": "NVDA"})
"""

import json
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CartographerExtractor:
    """
    Extracts structured data from web pages using site dictionaries.
    
    Supports two extraction modes:
    1. selector-based: Individual CSS selectors for each field
    2. label_based: Extract label/value pairs from tables (for FinViz-style layouts)
    """
    
    def __init__(self, configs_dir: Optional[Path] = None):
        """Initialize extractor with configs directory."""
        self.configs_dir = configs_dir or Path(__file__).parent / "configs"
        self._dictionaries: Dict[str, Dict] = {}
        self._browser: Optional[Browser] = None
        
    async def _ensure_browser(self, headless: bool = True) -> Browser:
        """Ensure browser is running."""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=headless)
        return self._browser
    
    async def close(self):
        """Close browser if running."""
        if self._browser:
            await self._browser.close()
            self._browser = None
    
    def load_dictionary(self, site_name: str) -> Dict:
        """Load site dictionary from JSON file."""
        if site_name in self._dictionaries:
            return self._dictionaries[site_name]
        
        dict_path = self.configs_dir / f"{site_name}_dictionary.json"
        if not dict_path.exists():
            raise FileNotFoundError(f"Dictionary not found: {dict_path}")
        
        with open(dict_path) as f:
            self._dictionaries[site_name] = json.load(f)
        
        logger.info(f"Loaded dictionary for {site_name}")
        return self._dictionaries[site_name]
    
    async def extract(
        self,
        site_name: str,
        template_name: str,
        url: str,
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        Extract data from a web page using site dictionary.
        
        Args:
            site_name: Name of the site (e.g., "finviz")
            template_name: Template to use (e.g., "stock_page")
            url: Full URL to extract from
            headless: Run browser in headless mode
            
        Returns:
            Dictionary of extracted data organized by region
        """
        dictionary = self.load_dictionary(site_name)
        
        template = dictionary.get("templates", {}).get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found in {site_name} dictionary")
        
        browser = await self._ensure_browser(headless=headless)
        page = await browser.new_page()
        
        try:
            # Navigate to URL
            logger.info(f"Extracting from {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Handle interceptors (cookie banners, ads, etc.)
            await self._handle_interceptors(page, dictionary.get("interceptors", []))
            
            # Verify page signature
            signature = template.get("signature", {})
            for req_elem in signature.get("required_elements", []):
                if not await page.query_selector(req_elem):
                    raise ValueError(f"Required element not found: {req_elem}")
            
            for forb_elem in signature.get("forbidden_elements", []):
                if await page.query_selector(forb_elem):
                    raise ValueError(f"Forbidden element found (error page?): {forb_elem}")
            
            # Extract data from each region
            result = {
                "source": site_name,
                "template": template_name,
                "url": url,
                "extracted_at": datetime.now().isoformat(),
                "data": {}
            }
            
            for region in template.get("regions", []):
                region_data = await self._extract_region(page, region)
                result["data"][region["region_id"]] = region_data
            
            logger.info(
                f"Extraction complete",
                extra={"url": url, "regions": len(result["data"])}
            )
            return result
            
        finally:
            await page.close()
    
    async def _handle_interceptors(self, page: Page, interceptors: List[Dict]):
        """Handle page interceptors (cookie banners, modals, etc.)."""
        for interceptor in sorted(interceptors, key=lambda x: x.get("priority", 50)):
            try:
                trigger = await page.query_selector(interceptor.get("trigger_selector", ""))
                if trigger:
                    timeout = interceptor.get("timeout_ms", 2000)
                    action = interceptor.get("action", "click")
                    target = interceptor.get("target_selector", "")
                    
                    if action == "click" and target:
                        button = await page.query_selector(target)
                        if button:
                            await button.click()
                            await page.wait_for_timeout(500)
                            logger.debug(f"Handled interceptor: {interceptor['name']}")
                    elif action == "close" and target:
                        close_btn = await page.query_selector(target)
                        if close_btn:
                            await close_btn.click()
                            await page.wait_for_timeout(500)
            except Exception as e:
                logger.debug(f"Interceptor {interceptor.get('name')} failed: {e}")
    
    async def _extract_region(self, page: Page, region: Dict) -> Dict[str, Any]:
        """Extract data from a single region."""
        region_id = region.get("region_id", "unknown")
        container_selector = region.get("container_selector")
        extraction_mode = region.get("extraction_mode", "selector")
        
        # Verify container exists
        if container_selector:
            container = await page.query_selector(container_selector)
            if not container:
                logger.warning(f"Container not found for region {region_id}: {container_selector}")
                return {"_error": f"Container not found: {container_selector}"}
        
        if extraction_mode == "label_based":
            return await self._extract_label_based(page, region)
        else:
            return await self._extract_selector_based(page, region)
    
    async def _extract_selector_based(self, page: Page, region: Dict) -> Dict[str, Any]:
        """Extract fields using individual selectors."""
        result = {}
        
        for rule in region.get("parsing_rules", []):
            field_name = rule.get("field_name")
            selector_config = rule.get("selector", {})
            
            # Try primary selector, then fallbacks
            selectors = [selector_config.get("primary", "")]
            selectors.extend(selector_config.get("fallbacks", []))
            
            raw_value = None
            for selector in selectors:
                if not selector:
                    continue
                try:
                    element = await page.query_selector(selector)
                    if element:
                        raw_value = await element.inner_text()
                        raw_value = raw_value.strip() if raw_value else None
                        break
                except Exception as e:
                    logger.debug(f"Selector failed for {field_name}: {selector} - {e}")
            
            if raw_value:
                # Apply transformation
                transformed = self._transform_value(
                    raw_value,
                    rule.get("data_type", "string"),
                    rule.get("transformation")
                )
                result[field_name] = {
                    "raw": raw_value,
                    "value": transformed,
                    "paywalled": rule.get("paywalled", False)
                }
            elif rule.get("required", False):
                logger.warning(f"Required field not found: {field_name}")
                result[field_name] = {"raw": None, "value": None, "_error": "Not found"}
        
        return result
    
    async def _extract_label_based(self, page: Page, region: Dict) -> Dict[str, Any]:
        """
        Extract fields using label/value pair matching.
        
        This is the preferred method for tables like FinViz's snapshot table
        where data is organized as label → value pairs.
        """
        result = {}
        label_config = region.get("label_based", {})
        
        label_selector = label_config.get("label_selector", "td.snapshot-td2")
        value_position = label_config.get("value_position", "next_sibling")
        label_mapping = label_config.get("label_mapping", {})
        
        # Get all label cells
        label_cells = await page.query_selector_all(label_selector)
        
        # Build label → value map
        label_value_pairs = {}
        for label_cell in label_cells:
            label_text = await label_cell.inner_text()
            label_text = label_text.strip() if label_text else ""
            
            if not label_text:
                continue
            
            # Get value based on position
            value_text = None
            if value_position == "next_sibling":
                # Get the next <td> element
                value_cell = await label_cell.evaluate_handle(
                    "el => el.nextElementSibling"
                )
                if value_cell:
                    value_text = await value_cell.inner_text()
            elif value_position == "next_td":
                # Similar approach via JS
                value_cell = await label_cell.evaluate_handle(
                    "el => el.nextElementSibling"
                )
                if value_cell:
                    value_text = await value_cell.inner_text()
            
            if value_text:
                label_value_pairs[label_text.strip()] = value_text.strip()
        
        # Map labels to field names
        for label, field_config in label_mapping.items():
            if isinstance(field_config, str):
                field_name = field_config
                data_type = "string"
                transformation = None
            else:
                field_name = field_config.get("field_name", label)
                data_type = field_config.get("data_type", "string")
                transformation = field_config.get("transformation")
            
            raw_value = label_value_pairs.get(label)
            if raw_value:
                transformed = self._transform_value(raw_value, data_type, transformation)
                result[field_name] = {
                    "raw": raw_value,
                    "value": transformed
                }
        
        # Also include unmapped fields with normalized names
        include_unmapped = label_config.get("include_unmapped", True)
        if include_unmapped:
            for label, raw_value in label_value_pairs.items():
                normalized_name = self._normalize_label(label)
                if normalized_name not in result and field_name not in result.values():
                    result[normalized_name] = {
                        "raw": raw_value,
                        "value": raw_value,  # Keep as string if unmapped
                        "_unmapped": True
                    }
        
        return result
    
    def _normalize_label(self, label: str) -> str:
        """Normalize a label to a valid field name."""
        # Remove parentheses content
        label = re.sub(r'\([^)]*\)', '', label)
        # Replace special chars with underscore
        label = re.sub(r'[^a-zA-Z0-9]+', '_', label)
        # Convert to lowercase snake_case
        label = label.lower().strip('_')
        return label
    
    def _transform_value(
        self,
        raw_value: str,
        data_type: str,
        transformation: Optional[str] = None
    ) -> Any:
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
                return self._parse_currency(raw_value, transformation)
            elif data_type == "date":
                return raw_value  # Keep as string for now
            else:
                return raw_value
        except Exception as e:
            logger.debug(f"Transform failed for '{raw_value}': {e}")
            return raw_value
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse a float value."""
        # Remove commas and currency symbols
        cleaned = re.sub(r'[,$%]', '', value)
        return float(cleaned)
    
    def _parse_integer(self, value: str) -> Optional[int]:
        """Parse an integer value, handling K/M/B suffixes."""
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
    
    def _parse_currency(self, value: str, transformation: Optional[str] = None) -> Any:
        """Parse a currency value with optional transformation."""
        value = value.upper().replace(',', '').replace('$', '')
        
        # Handle suffixes like B, M, K, T
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, 'T': 1_000_000_000_000}
        
        for suffix, mult in multipliers.items():
            if value.endswith(suffix):
                return float(value[:-1]) * mult
        
        return float(value)


# Convenience function
async def extract_finviz_stock(ticker: str, headless: bool = True) -> Dict[str, Any]:
    """
    Extract stock data from FinViz.
    
    Args:
        ticker: Stock ticker symbol (e.g., "NVDA")
        headless: Run browser in headless mode
        
    Returns:
        Extracted data dictionary
    """
    extractor = CartographerExtractor()
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
        return await extractor.extract("finviz", "stock_page", url, headless=headless)
    finally:
        await extractor.close()


# CLI for testing
if __name__ == "__main__":
    import sys
    
    async def main():
        ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
        print(f"\nExtracting data for {ticker}...")
        
        data = await extract_finviz_stock(ticker, headless=True)
        
        print(f"\nExtracted at: {data['extracted_at']}")
        print(f"Source: {data['source']}")
        print(f"Template: {data['template']}")
        print(f"\nData by region:")
        
        for region_id, region_data in data['data'].items():
            print(f"\n  [{region_id}]")
            for field, value in region_data.items():
                if isinstance(value, dict):
                    print(f"    {field}: {value.get('value', value.get('raw', 'N/A'))}")
                else:
                    print(f"    {field}: {value}")
    
    asyncio.run(main())
