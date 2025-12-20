# Cartographer & Miner Implementation Plan

**Version:** 1.0  
**Created:** December 20, 2025  
**Status:** 🟡 Ready for Implementation  
**Architecture:** Config-Driven Self-Healing Web Scraper

---

## Executive Summary

This document provides a complete implementation plan for the **Cartographer & Miner** architecture - a config-driven, self-healing web scraping system for Kuberan. The system replaces hardcoded parsers with dynamic, YAML-configured rules that can adapt to website changes without code modifications.

### Core Principles

**Primary:** "Update the configuration files, not the code."

**Development Compliance:**
- ✅ **File Size Limit**: All files <300 lines (models ~280, configs ~250 each)
- ✅ **Structured Logging**: All logs use `extra` parameter with context
- ✅ **Type Hints**: All function parameters and returns typed
- ✅ **Async/Await**: Uses async Playwright for I/O operations
- ✅ **No Synthetic Data**: Parser extracts existing values only
- ✅ **Security Compliant**: No sensitive data stored
- ✅ **Standalone Playwright**: Confirmed method for FinViz (per user quote)
- ✅ **One Config Per Site**: Modular, maintainable, version-controllable

**Architecture:** Each website gets its own configuration file and dictionary file for maximum modularity and maintainability.

---

## Architecture Overview

### The Two-Phase System

```
Phase 1: CARTOGRAPHY (Mapping)
┌─────────────────────────────────────────────────┐
│  The Cartographer                               │
│  • Reads template_definitions/{site}.yaml       │
│  • Scans website pages                          │
│  • Generates site_dictionaries/{site}.json      │
│  • Maps all extractable data points             │
│  • ONE DICTIONARY PER WEBSITE                   │
└─────────────────────────────────────────────────┘
                    ↓
         finviz_dictionary.json
         stockanalysis_dictionary.json
         alphavantage_dictionary.json
                    ↓
Phase 2: MINING (Extraction)
┌─────────────────────────────────────────────────┐
│  The Miner                                      │
│  • Loads site_dictionary.json                   │
│  • Executes scraping with Smart Parser          │
│  • Saves to MongoDB                             │
│  • Self-heals using fallback selectors          │
└─────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (Directory Structure & Models)

**Objective:** Create the configuration schema and data models.

**Files to Create:**
1. `backend/config/cartographer/template_definitions.yaml`
2. `backend/app/models/cartographer.py`

**Directory Structure:**
```
backend/
├── config/
│   └── cartographer/
│       ├── template_definitions/
│       │   ├── finviz.yaml                # FinViz config
│       │   ├── stockanalysis.yaml         # StockAnalysis config
│       │   └── alphavantage.yaml          # Alpha Vantage config
│       └── site_dictionaries/
│           ├── finviz_dictionary.json     # Generated (auto)
│           ├── stockanalysis_dictionary.json  # Generated (auto)
│           └── alphavantage_dictionary.json   # Generated (auto)
└── app/
    ├── models/
    │   └── cartographer.py                # Pydantic models
    └── services/
        └── cartographer/
            ├── __init__.py
            ├── scanner.py                 # The Cartographer
            ├── executor.py                # The Miner
            └── smart_parser.py            # Type casting logic
```

#### Step 1.1: Create Pydantic Models

**File:** `backend/app/models/cartographer.py`

```python
"""
Cartographer Data Models

Defines the schema for config-driven web scraping architecture.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Supported data types for Smart Parser."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    BOOLEAN = "boolean"
    LIST = "list"


class SelectorType(str, Enum):
    """CSS selector types."""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"


class InterceptorAction(str, Enum):
    """Actions to take when interceptor triggers."""
    CLICK = "click"
    CLOSE = "close"
    WAIT = "wait"
    DISMISS = "dismiss"


class PageSignature(BaseModel):
    """Unique identifier for a page type."""
    name: str = Field(..., description="Human-readable page type name")
    url_pattern: str = Field(..., description="Regex pattern to match URL")
    required_elements: List[str] = Field(
        default_factory=list,
        description="CSS selectors that MUST exist"
    )
    forbidden_elements: List[str] = Field(
        default_factory=list,
        description="CSS selectors that MUST NOT exist"
    )


class GlobalInterceptor(BaseModel):
    """Rules for handling pop-ups and interruptions."""
    name: str = Field(..., description="Interceptor identifier")
    trigger_selector: str = Field(..., description="CSS selector for detection")
    action: InterceptorAction = Field(..., description="Action to take")
    target_selector: Optional[str] = Field(
        None,
        description="Target for action (e.g., close button)"
    )
    timeout_ms: int = Field(default=2000, description="Wait timeout")
    priority: int = Field(default=100, description="Execution priority (lower=first)")


class SelectorStrategy(BaseModel):
    """Fallback selector chain."""
    primary: str = Field(..., description="Primary CSS selector")
    fallbacks: List[str] = Field(
        default_factory=list,
        description="Fallback selectors in order"
    )
    selector_type: SelectorType = Field(default=SelectorType.CSS)


class ParsingRule(BaseModel):
    """Defines how to extract and cast a data point."""
    field_name: str = Field(..., description="Normalized field name")
    label_text: Optional[str] = Field(
        None,
        description="Label to search for (e.g., 'P/E')"
    )
    selector: SelectorStrategy = Field(..., description="Selector strategy")
    data_type: DataType = Field(..., description="Target data type")
    transformation: Optional[str] = Field(
        None,
        description="Optional transformation function"
    )
    required: bool = Field(default=False, description="Is field required?")
    paywalled: bool = Field(default=False, description="Is behind paywall?")


class RegionDefinition(BaseModel):
    """A logical region on the page (e.g., 'snapshot_table')."""
    region_id: str = Field(..., description="Unique region identifier")
    description: str = Field(..., description="Human-readable description")
    container_selector: str = Field(..., description="CSS selector for container")
    parsing_rules: List[ParsingRule] = Field(
        default_factory=list,
        description="Rules for fields in this region"
    )


class PageTemplate(BaseModel):
    """Complete template for a page type."""
    signature: PageSignature
    regions: List[RegionDefinition]
    interceptors: List[str] = Field(
        default_factory=list,
        description="Global interceptor IDs to apply"
    )


class SiteDictionary(BaseModel):
    """Generated mapping of extractable data."""
    site_name: str = Field(..., description="Website name")
    generated_at: datetime = Field(default_factory=datetime.now)
    templates: Dict[str, PageTemplate] = Field(
        default_factory=dict,
        description="Page type → template mapping"
    )
    interceptors: List[GlobalInterceptor] = Field(
        default_factory=list,
        description="Global interceptor definitions"
    )
    metadata: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class ScrapingResult(BaseModel):
    """Result from a single scraping operation."""
    ticker: str
    page_type: str
    extracted_data: Dict[str, Union[str, int, float, bool, None]]
    interceptors_triggered: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    selectors_used: Dict[str, str] = Field(
        default_factory=dict,
        description="Field → selector mapping (for debugging)"
    )


class CartographerConfig(BaseModel):
    """Root configuration object."""
    site_name: str
    base_url: str
    global_interceptors: List[GlobalInterceptor]
    page_templates: List[PageTemplate]
    settings: Dict[str, Union[str, int, bool]] = Field(
        default_factory=dict,
        description="Global settings (timeouts, retries, etc.)"
    )
```

#### Step 1.2: Create Configuration Files

**Strategy: One configuration file per website**

**Why?**
- **Modularity**: Each site evolves independently
- **Easier debugging**: Issues isolated per site
- **Version control**: Track changes per site separately
- **Maintainability**: Smaller files (<300 lines each)
- **Deployment**: Update one site without affecting others

**File:** `backend/config/cartographer/template_definitions/finviz.yaml`

```yaml
# Cartographer Configuration for FinViz
# Last Updated: 2025-12-20
# File Size: ~250 lines (within 300-line limit)

site_name: "finviz"
base_url: "https://finviz.com"

# Global Settings
settings:
  default_timeout: 10000  # milliseconds
  max_retries: 3
  headless: true
  browser_type: "chromium"
  wait_for_network_idle: true

# Global Interceptors (Pop-ups, Ads, Modals)
global_interceptors:
  - name: "cookie_consent"
    trigger_selector: "div.cookie-notice"
    action: "click"
    target_selector: "button.accept-cookies"
    timeout_ms: 2000
    priority: 10

  - name: "premium_popup"
    trigger_selector: "div.premium-overlay"
    action: "click"
    target_selector: "button.close-premium"
    timeout_ms: 2000
    priority: 20

  - name: "ad_overlay"
    trigger_selector: "div.ad-interstitial"
    action: "dismiss"
    target_selector: "span.close-ad"
    timeout_ms: 1500
    priority: 30

# Page Templates
page_templates:
  # Template 1: Stock/ETF Quote Page
  - signature:
      name: "quote_page"
      url_pattern: "^https://finviz\\.com/quote\\.ashx\\?t=.*"
      required_elements:
        - "table.snapshot-table2"
        - "div.quote-header"
      forbidden_elements:
        - "div.error-page"
        - "div.ticker-not-found"

    interceptors:
      - "cookie_consent"
      - "premium_popup"

    regions:
      # Region 1: Header (Ticker + Company Name)
      - region_id: "header"
        description: "Quote header with ticker and company name"
        container_selector: "div.quote-header"
        parsing_rules:
          - field_name: "ticker"
            selector:
              primary: "div.quote-header h1"
              fallbacks:
                - "table.fullview-title td b"
                - "span.ticker-symbol"
            data_type: "string"
            required: true

          - field_name: "company_name"
            selector:
              primary: "div.quote-header h2"
              fallbacks:
                - "table.fullview-title td.fullview-title"
            data_type: "string"
            required: true

      # Region 2: Classification Chips
      - region_id: "classification"
        description: "Sector, Industry, Country, Exchange chips"
        container_selector: "div.quote-links"
        parsing_rules:
          - field_name: "sector"
            label_text: null  # First link in sequence
            selector:
              primary: "div.quote-links a:nth-of-type(1)"
            data_type: "string"

          - field_name: "industry"
            selector:
              primary: "div.quote-links a:nth-of-type(2)"
            data_type: "string"

          - field_name: "country"
            selector:
              primary: "div.quote-links a:nth-of-type(3)"
            data_type: "string"

          - field_name: "exchange"
            selector:
              primary: "div.quote-links a:nth-of-type(4)"
            data_type: "string"

      # Region 3: Snapshot Table (Main Fundamentals)
      - region_id: "snapshot_table"
        description: "Fundamental metrics grid"
        container_selector: "table.snapshot-table2"
        parsing_rules:
          # Valuation Metrics
          - field_name: "market_cap"
            label_text: "Market Cap"
            selector:
              primary: "td:contains('Market Cap') + td"
              fallbacks:
                - "//td[text()='Market Cap']/following-sibling::td[1]"
              selector_type: "css"
            data_type: "currency"
            transformation: "parse_market_cap"

          - field_name: "pe_ratio"
            label_text: "P/E"
            selector:
              primary: "td:contains('P/E') + td"
            data_type: "float"

          - field_name: "forward_pe"
            label_text: "Forward P/E"
            selector:
              primary: "td:contains('Forward P/E') + td"
            data_type: "float"

          - field_name: "peg_ratio"
            label_text: "PEG"
            selector:
              primary: "td:contains('PEG') + td"
            data_type: "float"

          - field_name: "price_to_sales"
            label_text: "P/S"
            selector:
              primary: "td:contains('P/S') + td"
            data_type: "float"

          - field_name: "price_to_book"
            label_text: "P/B"
            selector:
              primary: "td:contains('P/B') + td"
            data_type: "float"

          # Profitability Metrics
          - field_name: "roe"
            label_text: "ROE"
            selector:
              primary: "td:contains('ROE') + td"
            data_type: "percentage"

          - field_name: "roa"
            label_text: "ROA"
            selector:
              primary: "td:contains('ROA') + td"
            data_type: "percentage"

          - field_name: "profit_margin"
            label_text: "Profit Margin"
            selector:
              primary: "td:contains('Profit Margin') + td"
            data_type: "percentage"

          # Dividend Metrics
          - field_name: "dividend_yield"
            label_text: "Dividend %"
            selector:
              primary: "td:contains('Dividend %') + td"
            data_type: "percentage"

          - field_name: "payout_ratio"
            label_text: "Payout"
            selector:
              primary: "td:contains('Payout') + td"
            data_type: "percentage"

          # ETF-Specific Fields
          - field_name: "aum"
            label_text: "AUM"
            selector:
              primary: "td:contains('AUM') + td"
            data_type: "currency"
            transformation: "parse_market_cap"

          - field_name: "expense_ratio"
            label_text: "Expense"
            selector:
              primary: "td:contains('Expense') + td"
            data_type: "percentage"

          - field_name: "total_holdings"
            label_text: "Total Holdings"
            selector:
              primary: "td:contains('Total Holdings') + td"
            data_type: "integer"

          # Paywalled Fields (Elite Only)
          - field_name: "flows_3y"
            label_text: "Flows% 3Y"
            selector:
              primary: "td:contains('Flows% 3Y') + td"
            data_type: "percentage"
            paywalled: true

          - field_name: "flows_5y"
            label_text: "Flows% 5Y"
            selector:
              primary: "td:contains('Flows% 5Y') + td"
            data_type: "percentage"
            paywalled: true

      # Region 4: Peers & ETF Holdings
      - region_id: "related_tickers"
        description: "Peers and 'Held by' ETFs"
        container_selector: "div.peers-links"
        parsing_rules:
          - field_name: "peers"
            label_text: "Peers"
            selector:
              primary: "a[href*='quote.ashx']"
            data_type: "list"

          - field_name: "held_by_etfs"
            label_text: "Held by"
            selector:
              primary: "a[href*='quote.ashx']"
            data_type: "list"

  # Template 2: Screener Results Page
  - signature:
      name: "screener_page"
      url_pattern: "^https://finviz\\.com/screener\\.ashx.*"
      required_elements:
        - "table.screener-table"
        - "div.screener-controls"
      forbidden_elements: []

    interceptors:
      - "cookie_consent"
      - "ad_overlay"

    regions:
      - region_id: "results_table"
        description: "Screener results grid"
        container_selector: "table.screener-table"
        parsing_rules:
          - field_name: "tickers"
            selector:
              primary: "tr td.ticker-cell a"
            data_type: "list"

          - field_name: "market_caps"
            selector:
              primary: "tr td.market-cap-cell"
            data_type: "list"
```

---

### Phase 2: The Cartographer (Scanner)

**Objective:** Implement the scanner that generates `site_dictionary.json`.

**File:** `backend/app/services/cartographer/scanner.py`

```python
"""
The Cartographer

Scans websites using template_definitions.yaml and generates site_dictionary.json.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from app.models.cartographer import (
    CartographerConfig,
    SiteDictionary,
    PageTemplate,
    GlobalInterceptor,
    ScrapingResult
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Cartographer:
    """Scans websites and generates site dictionaries."""

    def __init__(self, config_path: str):
        """
        Initialize Cartographer.

        Args:
            config_path: Path to template_definitions.yaml
        """
        self.config_path = Path(config_path)
        self.config: Optional[CartographerConfig] = None
        self.dictionary: Optional[SiteDictionary] = None

    async def load_config(self) -> CartographerConfig:
        """Load and validate configuration."""
        logger.info("Loading configuration", extra={"path": str(self.config_path)})

        with open(self.config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        self.config = CartographerConfig(**config_dict)
        logger.info("Configuration loaded", extra={"site": self.config.site_name})
        return self.config

    async def scan_site(self, sample_urls: Dict[str, str]) -> SiteDictionary:
        """
        Scan site using sample URLs for each page type.

        Args:
            sample_urls: Dict of page_type -> sample URL

        Returns:
            Generated SiteDictionary
        """
        logger.info("Starting site scan", extra={"sample_urls": len(sample_urls)})

        if not self.config:
            await self.load_config()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config.settings.get("headless", True)
            )

            validated_templates = {}

            for page_type, url in sample_urls.items():
                logger.info("Scanning page type", extra={"type": page_type, "url": url})

                template = self._find_template_for_url(url)
                if not template:
                    logger.warning("No template found for URL", extra={"url": url})
                    continue

                validated = await self._validate_template(browser, url, template)
                if validated:
                    validated_templates[page_type] = validated

            await browser.close()

        self.dictionary = SiteDictionary(
            site_name=self.config.site_name,
            generated_at=datetime.now(),
            templates=validated_templates,
            interceptors=self.config.global_interceptors,
            metadata={
                "config_version": "1.0",
                "sample_urls_count": len(sample_urls),
                "validated_templates": len(validated_templates)
            }
        )

        logger.info(
            "Site scan complete",
            extra={
                "templates": len(validated_templates),
                "interceptors": len(self.config.global_interceptors)
            }
        )

        return self.dictionary

    def _find_template_for_url(self, url: str) -> Optional[PageTemplate]:
        """Find matching template for URL."""
        import re

        for template in self.config.page_templates:
            if re.match(template.signature.url_pattern, url):
                return template

        return None

    async def _validate_template(
        self,
        browser: Browser,
        url: str,
        template: PageTemplate
    ) -> Optional[PageTemplate]:
        """
        Validate template against live page.

        Checks if required elements exist and forbidden elements don't exist.
        """
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Check required elements
            for selector in template.signature.required_elements:
                element = await page.query_selector(selector)
                if not element:
                    logger.warning(
                        "Required element not found",
                        extra={"selector": selector, "url": url}
                    )
                    return None

            # Check forbidden elements
            for selector in template.signature.forbidden_elements:
                element = await page.query_selector(selector)
                if element:
                    logger.warning(
                        "Forbidden element found",
                        extra={"selector": selector, "url": url}
                    )
                    return None

            logger.info("Template validated", extra={"template": template.signature.name})
            return template

        except Exception as e:
            logger.error(
                "Template validation failed",
                extra={"template": template.signature.name, "error": str(e)},
                exc_info=True
            )
            return None

        finally:
            await page.close()

    async def save_dictionary(self, output_path: str) -> None:
        """Save site dictionary to JSON file."""
        if not self.dictionary:
            raise ValueError("No dictionary to save. Run scan_site() first.")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(
                self.dictionary.model_dump(mode='json'),
                f,
                indent=2,
                default=str
            )

        logger.info("Dictionary saved", extra={"path": str(output_file)})


# Usage Example
async def main():
    """Example: Scan FinViz and generate site-specific dictionary."""
    cartographer = Cartographer(
        config_path="backend/config/cartographer/template_definitions/finviz.yaml"
    )

    sample_urls = {
        "quote_page": "https://finviz.com/quote.ashx?t=NVDA&p=d",
        "quote_page_etf": "https://finviz.com/quote.ashx?t=VTI&p=d",
    }

    dictionary = await cartographer.scan_site(sample_urls)
    await cartographer.save_dictionary(
        "backend/config/cartographer/site_dictionaries/finviz_dictionary.json"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

### Phase 3: The Miner (Executor) + Smart Parser

**Objective:** Implement the scraper that uses the dictionary to extract data.

#### Step 3.1: Smart Parser

**File:** `backend/app/services/cartographer/smart_parser.py`

```python
"""
Smart Parser

Type casting and data transformation logic.
"""

import re
from typing import Any, Optional
from datetime import datetime
from app.models.cartographer import DataType
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SmartParser:
    """Intelligently casts raw HTML strings to typed values."""

    @staticmethod
    def parse(raw_value: str, data_type: DataType, transformation: Optional[str] = None) -> Any:
        """
        Parse raw string to target data type.

        Args:
            raw_value: Raw text from HTML
            data_type: Target data type
            transformation: Optional transformation function name

        Returns:
            Typed value or None if parsing fails
        """
        if not raw_value or raw_value.strip() in ["-", "N/A", ""]:
            return None

        raw_value = raw_value.strip()

        try:
            if data_type == DataType.STRING:
                return raw_value

            elif data_type == DataType.INTEGER:
                return SmartParser._parse_integer(raw_value)

            elif data_type == DataType.FLOAT:
                return SmartParser._parse_float(raw_value)

            elif data_type == DataType.PERCENTAGE:
                return SmartParser._parse_percentage(raw_value)

            elif data_type == DataType.CURRENCY:
                if transformation == "parse_market_cap":
                    return SmartParser._parse_market_cap(raw_value)
                return SmartParser._parse_currency(raw_value)

            elif data_type == DataType.DATE:
                return SmartParser._parse_date(raw_value)

            elif data_type == DataType.BOOLEAN:
                return SmartParser._parse_boolean(raw_value)

            elif data_type == DataType.LIST:
                return SmartParser._parse_list(raw_value)

            else:
                logger.warning("Unknown data type", extra={"type": data_type})
                return raw_value

        except Exception as e:
            logger.error(
                "Parsing failed",
                extra={"raw": raw_value, "type": data_type, "error": str(e)}
            )
            return None

    @staticmethod
    def _parse_integer(value: str) -> Optional[int]:
        """Parse integer (handles commas)."""
        cleaned = value.replace(",", "").replace(" ", "")
        match = re.search(r"[-+]?\d+", cleaned)
        return int(match.group()) if match else None

    @staticmethod
    def _parse_float(value: str) -> Optional[float]:
        """Parse float."""
        cleaned = value.replace(",", "").replace(" ", "")
        match = re.search(r"[-+]?\d+\.?\d*", cleaned)
        return float(match.group()) if match else None

    @staticmethod
    def _parse_percentage(value: str) -> Optional[float]:
        """Parse percentage (returns as decimal, e.g., 5.5% → 5.5)."""
        match = re.search(r"[-+]?\d+\.?\d*", value)
        return float(match.group()) if match else None

    @staticmethod
    def _parse_currency(value: str) -> Optional[float]:
        """Parse currency (basic, without abbreviations)."""
        cleaned = value.replace("$", "").replace(",", "").strip()
        match = re.search(r"[-+]?\d+\.?\d*", cleaned)
        return float(match.group()) if match else None

    @staticmethod
    def _parse_market_cap(value: str) -> Optional[float]:
        """
        Parse market cap with abbreviations.

        Examples:
            "2.77T" → 2770000000000.0
            "45.2B" → 45200000000.0
            "123.45M" → 123450000.0
        """
        multipliers = {
            'T': 1_000_000_000_000,
            'B': 1_000_000_000,
            'M': 1_000_000,
            'K': 1_000
        }

        value = value.replace("$", "").strip()
        match = re.match(r"([-+]?\d+\.?\d*)\s*([TBMK])?", value, re.IGNORECASE)

        if match:
            number = float(match.group(1))
            suffix = match.group(2)

            if suffix:
                return number * multipliers.get(suffix.upper(), 1)
            return number

        return None

    @staticmethod
    def _parse_date(value: str) -> Optional[str]:
        """Parse date (returns ISO format string)."""
        # Simple implementation - can be extended
        try:
            dt = datetime.strptime(value, "%b %d, %Y")
            return dt.isoformat()
        except:
            return value  # Return as-is if parsing fails

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """Parse boolean."""
        return value.lower() in ["yes", "true", "1", "y"]

    @staticmethod
    def _parse_list(value: str) -> list:
        """Parse list (comma or space separated)."""
        if "," in value:
            return [item.strip() for item in value.split(",")]
        return value.split()
```

#### Step 3.2: The Miner

**File:** `backend/app/services/cartographer/executor.py`

```python
"""
The Miner

Executes scraping using site_dictionary.json and Smart Parser.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import async_playwright, Page, Browser
from app.models.cartographer import (
    SiteDictionary,
    PageTemplate,
    RegionDefinition,
    ParsingRule,
    GlobalInterceptor,
    ScrapingResult,
    InterceptorAction
)
from app.services.cartographer.smart_parser import SmartParser
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Miner:
    """Executes scraping using site dictionary."""

    def __init__(self, dictionary_path: str):
        """
        Initialize Miner.

        Args:
            dictionary_path: Path to site_dictionary.json
        """
        self.dictionary_path = Path(dictionary_path)
        self.dictionary: Optional[SiteDictionary] = None
        self.parser = SmartParser()

    def load_dictionary(self) -> SiteDictionary:
        """Load site dictionary."""
        logger.info("Loading dictionary", extra={"path": str(self.dictionary_path)})

        with open(self.dictionary_path, 'r') as f:
            dict_data = json.load(f)

        self.dictionary = SiteDictionary(**dict_data)
        logger.info(
            "Dictionary loaded",
            extra={"templates": len(self.dictionary.templates)}
        )
        return self.dictionary

    async def scrape_url(self, url: str, page_type: str) -> ScrapingResult:
        """
        Scrape a single URL.

        Args:
            url: Target URL
            page_type: Page template to use (e.g., 'quote_page')

        Returns:
            ScrapingResult with extracted data
        """
        if not self.dictionary:
            self.load_dictionary()

        template = self.dictionary.templates.get(page_type)
        if not template:
            raise ValueError(f"Template '{page_type}' not found in dictionary")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")

                # Run global interceptors
                triggered = await self._run_interceptors(page, template)

                # Extract data from all regions
                extracted_data = {}
                selectors_used = {}
                errors = []

                for region in template.regions:
                    region_data = await self._extract_region(page, region)
                    extracted_data.update(region_data.get("data", {}))
                    selectors_used.update(region_data.get("selectors", {}))
                    errors.extend(region_data.get("errors", []))

                # Infer ticker from URL or extracted data
                ticker = extracted_data.get("ticker", self._extract_ticker_from_url(url))

                result = ScrapingResult(
                    ticker=ticker,
                    page_type=page_type,
                    extracted_data=extracted_data,
                    interceptors_triggered=triggered,
                    errors=errors,
                    selectors_used=selectors_used
                )

                logger.info(
                    "Scraping complete",
                    extra={
                        "ticker": ticker,
                        "fields": len(extracted_data),
                        "errors": len(errors)
                    }
                )

                return result

            finally:
                await page.close()
                await browser.close()

    async def _run_interceptors(
        self,
        page: Page,
        template: PageTemplate
    ) -> List[str]:
        """Run global interceptors (pop-up handling)."""
        triggered = []

        # Get relevant interceptors for this template
        interceptor_ids = template.interceptors
        interceptors = [
            i for i in self.dictionary.interceptors
            if i.name in interceptor_ids
        ]

        # Sort by priority
        interceptors.sort(key=lambda x: x.priority)

        for interceptor in interceptors:
            try:
                element = await page.query_selector(interceptor.trigger_selector)
                if element:
                    await self._execute_interceptor_action(page, interceptor)
                    triggered.append(interceptor.name)
                    logger.info("Interceptor triggered", extra={"name": interceptor.name})

            except Exception as e:
                logger.warning(
                    "Interceptor failed",
                    extra={"name": interceptor.name, "error": str(e)}
                )

        return triggered

    async def _execute_interceptor_action(
        self,
        page: Page,
        interceptor: GlobalInterceptor
    ) -> None:
        """Execute interceptor action."""
        if interceptor.action == InterceptorAction.CLICK:
            if interceptor.target_selector:
                await page.click(interceptor.target_selector, timeout=interceptor.timeout_ms)

        elif interceptor.action == InterceptorAction.CLOSE:
            if interceptor.target_selector:
                await page.click(interceptor.target_selector, timeout=interceptor.timeout_ms)

        elif interceptor.action == InterceptorAction.DISMISS:
            await page.keyboard.press("Escape")

        elif interceptor.action == InterceptorAction.WAIT:
            await page.wait_for_timeout(interceptor.timeout_ms)

    async def _extract_region(
        self,
        page: Page,
        region: RegionDefinition
    ) -> Dict:
        """Extract data from a single region."""
        data = {}
        selectors = {}
        errors = []

        for rule in region.parsing_rules:
            try:
                raw_value = await self._extract_field(page, rule)
                if raw_value is not None:
                    parsed = self.parser.parse(
                        raw_value,
                        rule.data_type,
                        rule.transformation
                    )
                    data[rule.field_name] = parsed
                    selectors[rule.field_name] = rule.selector.primary

                elif rule.required:
                    errors.append(f"Required field '{rule.field_name}' not found")

            except Exception as e:
                error_msg = f"Failed to extract '{rule.field_name}': {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        return {"data": data, "selectors": selectors, "errors": errors}

    async def _extract_field(self, page: Page, rule: ParsingRule) -> Optional[str]:
        """Extract single field using selector strategy."""
        # Try primary selector
        selectors = [rule.selector.primary] + rule.selector.fallbacks

        for selector in selectors:
            try:
                # Handle label-based extraction
                if rule.label_text:
                    # Find label, then get next sibling
                    label_selector = f"td:has-text('{rule.label_text}')"
                    label = await page.query_selector(label_selector)
                    if label:
                        value_element = await label.evaluate_handle("el => el.nextElementSibling")
                        if value_element:
                            text = await value_element.inner_text()
                            return text.strip()
                else:
                    # Direct selector
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        return text.strip()

            except Exception as e:
                logger.debug(
                    "Selector failed, trying fallback",
                    extra={"selector": selector, "error": str(e)}
                )
                continue

        return None

    def _extract_ticker_from_url(self, url: str) -> str:
        """Extract ticker from URL as fallback."""
        import re
        match = re.search(r"[?&]t=([A-Z]+)", url)
        return match.group(1) if match else "UNKNOWN"


# Usage Example
async def main():
    """Example: Scrape NVDA quote page."""
    miner = Miner("backend/config/cartographer/site_dictionary.json")

    result = await miner.scrape_url(
        url="https://finviz.com/quote.ashx?t=NVDA&p=d",
        page_type="quote_page"
    )

    print(f"Ticker: {result.ticker}")
    print(f"Fields extracted: {len(result.extracted_data)}")
    print(f"Sample data: {list(result.extracted_data.items())[:5]}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

### Phase 4: MongoDB Integration

**Objective:** Save scraped data to MongoDB.

**File:** `backend/app/models/cartographer.py` (Add to existing file)

```python
# Add to existing models file:

from beanie import Document


class FinvizSnapshot(Document):
    """MongoDB document for FinViz scraped data."""
    
    provider: str = "finviz"
    ticker: str
    page_type: str
    snapshot_version: str = "v1"
    as_of_date: str
    fetched_at: datetime = Field(default_factory=datetime.now)
    
    # Extracted data
    identity: Dict[str, Any] = Field(default_factory=dict)
    snapshot_table: Dict[str, Any] = Field(default_factory=dict)
    classification: Dict[str, Any] = Field(default_factory=dict)
    related_tickers: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Metadata
    interceptors_triggered: List[str] = Field(default_factory=list)
    selectors_used: Dict[str, str] = Field(default_factory=dict)
    extraction_errors: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "finviz_snapshots"
        indexes = [
            IndexModel([("ticker", 1), ("as_of_date", -1)]),
            IndexModel([("ticker", 1)]),
            IndexModel([("fetched_at", -1)])
        ]
```

**File:** `backend/app/repositories/cartographer_repository.py`

```python
"""
Cartographer Repository

Data access layer for scraped data.
"""

from typing import Optional
from datetime import datetime
from app.models.cartographer import FinvizSnapshot, ScrapingResult
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CartographerRepository:
    """Repository for Cartographer scraped data."""

    async def save_snapshot(self, result: ScrapingResult) -> FinvizSnapshot:
        """
        Save scraping result to MongoDB.

        Args:
            result: ScrapingResult from Miner

        Returns:
            Saved FinvizSnapshot document
        """
        # Organize data by sections
        identity = {
            "ticker": result.extracted_data.get("ticker"),
            "company_name": result.extracted_data.get("company_name")
        }

        classification = {
            "sector": result.extracted_data.get("sector"),
            "industry": result.extracted_data.get("industry"),
            "country": result.extracted_data.get("country"),
            "exchange": result.extracted_data.get("exchange")
        }

        related_tickers = {
            "peers": result.extracted_data.get("peers", []),
            "held_by_etfs": result.extracted_data.get("held_by_etfs", [])
        }

        # All other fields go to snapshot_table
        snapshot_table = {
            k: v for k, v in result.extracted_data.items()
            if k not in [
                "ticker", "company_name", "sector", "industry",
                "country", "exchange", "peers", "held_by_etfs"
            ]
        }

        snapshot = FinvizSnapshot(
            ticker=result.ticker,
            page_type=result.page_type,
            as_of_date=datetime.now().strftime("%Y-%m-%d"),
            identity=identity,
            snapshot_table=snapshot_table,
            classification=classification,
            related_tickers=related_tickers,
            interceptors_triggered=result.interceptors_triggered,
            selectors_used=result.selectors_used,
            extraction_errors=result.errors
        )

        await snapshot.insert()

        logger.info(
            "Snapshot saved to MongoDB",
            extra={
                "ticker": result.ticker,
                "fields": len(snapshot_table),
                "errors": len(result.errors)
            }
        )

        return snapshot

    async def get_latest_snapshot(self, ticker: str) -> Optional[FinvizSnapshot]:
        """Get most recent snapshot for ticker."""
        return await FinvizSnapshot.find_one(
            FinvizSnapshot.ticker == ticker,
            sort=[("fetched_at", -1)]
        )


# Singleton instance
cartographer_repository = CartographerRepository()
```

---

### Phase 5: CLI Tool

**Objective:** Command-line interface for Cartographer & Miner.

**File:** `backend/app/scripts/run_cartographer.py`

```python
"""
Cartographer CLI Tool

Command-line interface for scanning and scraping with Cartographer.
"""

import asyncio
import click
from pathlib import Path

from app.services.cartographer.scanner import Cartographer
from app.services.cartographer.executor import Miner
from app.repositories.cartographer_repository import cartographer_repository


@click.group()
def cli():
    """Cartographer CLI - Config-driven web scraping."""
    pass


@cli.command()
@click.option(
    '--config',
    default='backend/config/cartographer/template_definitions.yaml',
    help='Path to template_definitions.yaml'
)
@click.option(
    '--output',
    default='backend/config/cartographer/site_dictionary.json',
    help='Output path for site_dictionary.json'
)
def scan(config: str, output: str):
    """Scan site and generate site_dictionary.json."""
    click.echo("🗺️  Starting Cartographer scan...")

    async def _scan():
        cartographer = Cartographer(config_path=config)

        sample_urls = {
            "quote_page": "https://finviz.com/quote.ashx?t=NVDA&p=d",
            "quote_page_etf": "https://finviz.com/quote.ashx?t=VTI&p=d",
        }

        await cartographer.scan_site(sample_urls)
        await cartographer.save_dictionary(output)

        click.echo(f"✅ Dictionary saved to: {output}")

    asyncio.run(_scan())


@cli.command()
@click.option(
    '--ticker',
    required=True,
    help='Ticker symbol to scrape'
)
@click.option(
    '--dictionary',
    default='backend/config/cartographer/site_dictionary.json',
    help='Path to site_dictionary.json'
)
@click.option(
    '--save',
    is_flag=True,
    help='Save to MongoDB'
)
def mine(ticker: str, dictionary: str, save: bool):
    """Scrape data for a ticker."""
    click.echo(f"⛏️  Mining data for {ticker}...")

    async def _mine():
        miner = Miner(dictionary_path=dictionary)

        url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
        result = await miner.scrape_url(url, page_type="quote_page")

        click.echo(f"✅ Extracted {len(result.extracted_data)} fields")
        click.echo(f"⚠️  {len(result.errors)} errors")

        if save:
            snapshot = await cartographer_repository.save_snapshot(result)
            click.echo(f"💾 Saved to MongoDB: {snapshot.id}")

    asyncio.run(_mine())


@cli.command()
@click.option(
    '--tickers',
    required=True,
    help='Comma-separated ticker list'
)
@click.option(
    '--dictionary',
    default='backend/config/cartographer/site_dictionary.json',
    help='Path to site_dictionary.json'
)
def batch(tickers: str, dictionary: str):
    """Batch scrape multiple tickers."""
    ticker_list = [t.strip() for t in tickers.split(',')]
    click.echo(f"⛏️  Batch mining {len(ticker_list)} tickers...")

    async def _batch():
        miner = Miner(dictionary_path=dictionary)

        for ticker in ticker_list:
            try:
                url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
                result = await miner.scrape_url(url, page_type="quote_page")
                await cartographer_repository.save_snapshot(result)
                click.echo(f"✅ {ticker}: {len(result.extracted_data)} fields")
            except Exception as e:
                click.echo(f"❌ {ticker}: {str(e)}")

    asyncio.run(_batch())


if __name__ == '__main__':
    cli()
```

**Usage:**

```bash
# Step 1: Scan site and generate dictionary
python3 backend/app/scripts/run_cartographer.py scan

# Step 2: Scrape single ticker
python3 backend/app/scripts/run_cartographer.py mine --ticker NVDA --save

# Step 3: Batch scrape
python3 backend/app/scripts/run_cartographer.py batch --tickers "NVDA,MSFT,AAPL,TSLA"
```

---

## Testing Strategy

### Unit Tests

**File:** `backend/app/tests/test_smart_parser.py`

```python
import pytest
from app.services.cartographer.smart_parser import SmartParser
from app.models.cartographer import DataType


def test_parse_integer():
    assert SmartParser.parse("1,234", DataType.INTEGER) == 1234
    assert SmartParser.parse("42", DataType.INTEGER) == 42


def test_parse_float():
    assert SmartParser.parse("3.14", DataType.FLOAT) == 3.14
    assert SmartParser.parse("2,500.50", DataType.FLOAT) == 2500.50


def test_parse_percentage():
    assert SmartParser.parse("5.5%", DataType.PERCENTAGE) == 5.5
    assert SmartParser.parse("-1.2%", DataType.PERCENTAGE) == -1.2


def test_parse_market_cap():
    assert SmartParser.parse("2.77T", DataType.CURRENCY, "parse_market_cap") == 2.77e12
    assert SmartParser.parse("45.2B", DataType.CURRENCY, "parse_market_cap") == 45.2e9
    assert SmartParser.parse("123.45M", DataType.CURRENCY, "parse_market_cap") == 123.45e6


def test_parse_list():
    result = SmartParser.parse("AMD, AVGO, INTC", DataType.LIST)
    assert result == ["AMD", "AVGO", "INTC"]
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Create directory structure
- [ ] Implement all models (`cartographer.py`)
- [ ] Create base configuration (`template_definitions.yaml`)
- [ ] Implement Cartographer (scanner)
- [ ] Implement Miner (executor)
- [ ] Implement Smart Parser
- [ ] Add MongoDB integration
- [ ] Create CLI tool
- [ ] Write unit tests
- [ ] Write integration tests

### Initial Deployment

- [ ] Run Cartographer scan: Generate `site_dictionary.json`
- [ ] Test Miner with 5 sample tickers
- [ ] Verify MongoDB storage
- [ ] Validate data quality
- [ ] Check error handling

### Production Rollout

- [ ] Batch scrape 100 tickers
- [ ] Monitor error rates
- [ ] Update selectors if needed (config only!)
- [ ] Add background job integration
- [ ] Set up monitoring/alerting

---

## Maintenance Guidelines

### When Website Changes

**DO:**
1. Update `template_definitions.yaml` (add fallback selectors)
2. Re-run Cartographer scan
3. Test with sample tickers
4. Deploy updated config

**DON'T:**
1. ❌ Modify Python code
2. ❌ Hardcode new selectors
3. ❌ Skip validation

### Adding New Page Types

1. Add new `PageTemplate` to `template_definitions.yaml`
2. Define `PageSignature` (URL pattern + required elements)
3. Add `RegionDefinition` entries
4. Define `ParsingRule` for each field
5. Run Cartographer scan with sample URL
6. Test with Miner

### Handling Paywalled Fields

Mark fields as `paywalled: true` in config:

```yaml
- field_name: "flows_3y"
  label_text: "Flows% 3Y"
  selector:
    primary: "td:contains('Flows% 3Y') + td"
  data_type: "percentage"
  paywalled: true  # ← Elite only
```

Miner will extract but flag as paywalled in MongoDB.

---

## Success Metrics

### Phase 1 (Foundation)
- ✅ Models compile without errors
- ✅ Config validates against schema
- ✅ Directory structure created

### Phase 2 (Cartographer)
- ✅ Scanner generates valid `site_dictionary.json`
- ✅ All page signatures validate
- ✅ Required elements found

### Phase 3 (Miner + Parser)
- ✅ 95%+ field extraction rate
- ✅ Smart Parser handles all data types
- ✅ Fallback selectors work when primary fails

### Phase 4 (MongoDB)
- ✅ Snapshots save successfully
- ✅ No duplicate entries
- ✅ Query performance acceptable

### Phase 5 (Production)
- ✅ Batch scraping successful
- ✅ Error rate <5%
- ✅ Config changes deploy without downtime

---

## Troubleshooting

### Common Issues

**Issue:** Required element not found during scan
- **Solution:** Check if page loaded fully. Increase timeout in config.

**Issue:** Fallback selectors all failing
- **Solution:** Website structure changed. Add new selector to config.

**Issue:** Smart Parser returning None
- **Solution:** Check raw HTML value. May need new transformation function.

**Issue:** Pop-ups blocking scraping
- **Solution:** Add new `GlobalInterceptor` to config.

---

## Appendix: Configuration Examples

### Adding a New Field

```yaml
parsing_rules:
  - field_name: "new_metric"
    label_text: "New Metric"
    selector:
      primary: "td:contains('New Metric') + td"
      fallbacks:
        - "//td[text()='New Metric']/following-sibling::td[1]"
    data_type: "float"
    transformation: null
    required: false
```

### Adding a New Interceptor

```yaml
global_interceptors:
  - name: "survey_popup"
    trigger_selector: "div.survey-modal"
    action: "click"
    target_selector: "button.close-survey"
    timeout_ms: 2000
    priority: 40
```

---

## Conclusion

This implementation plan provides everything needed to build the Cartographer & Miner system. The config-driven approach ensures that website changes can be handled through YAML updates rather than code changes, dramatically reducing maintenance overhead.

**Next Steps:**
1. Create directory structure
2. Implement models
3. Create base config
4. Implement Cartographer
5. Implement Miner
6. Test end-to-end
7. Deploy to production

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Maintained By:** Kuberan Engineering Team
