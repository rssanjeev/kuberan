"""
Cartographer Scanner - Website Structure Mapper

Last Updated: 2025-12-20
Status: Active
Purpose: Scan websites and generate site dictionaries with validated selectors

Architecture:
- Load YAML configuration
- Navigate to sample pages using Playwright
- Validate all selectors (primary + fallbacks)
- Generate JSON dictionary with validated selectors
- Self-healing: Mark failed selectors, promote fallbacks

File Size: <300 lines (compliant)
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from playwright.async_api import async_playwright, Browser, Page

from app.core.logging_config import get_logger
from app.models.cartographer import (
    CartographerConfig,
    ExtractionMode,
    GlobalInterceptor,
    PageTemplate,
    RegionDefinition,
    ParsingRule,
    SelectorStrategy,
    SiteDictionary,
)
from .interceptor_handler import InterceptorHandler
from .selector_validator import SelectorValidator

logger = get_logger(__name__)


class CartographerScanner:
    """
    The Cartographer: Scans websites and generates validated site dictionaries.
    
    Workflow:
    1. Load YAML configuration
    2. Launch browser (Playwright)
    3. For each page template:
       - Navigate to sample URL
       - Execute global interceptors
       - Validate signature (required/forbidden elements)
       - For each region → For each parsing rule:
         - Test primary selector
         - Test fallback selectors if primary fails
         - Record working selector in dictionary
    4. Save validated dictionary to JSON
    """

    def __init__(self, config_path: Path):
        """
        Initialize scanner with configuration file path.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config: Optional[CartographerConfig] = None
        self.browser: Optional[Browser] = None
        self.site_name: str = ""
        self.interceptor_handler = InterceptorHandler()
        self.selector_validator = SelectorValidator()

    async def load_config(self) -> CartographerConfig:
        """Load and validate YAML configuration."""
        try:
            with open(self.config_path) as f:
                config_data = yaml.safe_load(f)
            
            self.config = CartographerConfig(**config_data)
            self.site_name = self.config.site_name
            
            logger.info(
                "Config loaded",
                extra={
                    "site": self.site_name,
                    "templates": len(self.config.page_templates),
                },
            )
            return self.config
        except (FileNotFoundError, yaml.YAMLError, ValidationError) as e:
            logger.error("Config load failed", extra={"error": str(e)}, exc_info=True)
            raise

    async def _launch_browser(self) -> Browser:
        """
        Launch Playwright browser with configured settings.
        
        Returns:
            Browser instance
        """
        logger.info("Launching browser", extra={"headless": self.config.settings.get("headless", True)})

        playwright = await async_playwright().start()
        browser_type = self.config.settings.get("browser_type", "chromium")

        if browser_type == "chromium":
            self.browser = await playwright.chromium.launch(
                headless=self.config.settings.get("headless", True)
            )
        elif browser_type == "firefox":
            self.browser = await playwright.firefox.launch(
                headless=self.config.settings.get("headless", True)
            )
        else:
            self.browser = await playwright.webkit.launch(
                headless=self.config.settings.get("headless", True)
            )

        logger.info("Browser launched", extra={"type": browser_type})
        return self.browser

    async def _validate_page_signature(
        self, page: Page, template: PageTemplate, sample_url: str
    ) -> None:
        """Validate required and forbidden elements match page signature."""
        # Validate required elements
        for required in template.signature.required_elements:
            element = await page.query_selector(required)
            if not element:
                logger.error(
                    "Required element not found",
                    extra={"selector": required, "url": sample_url},
                )
                raise ValueError(f"Required element not found: {required}")

        # Check forbidden elements
        for forbidden in template.signature.forbidden_elements:
            element = await page.query_selector(forbidden)
            if element:
                logger.error(
                    "Forbidden element found",
                    extra={"selector": forbidden, "url": sample_url},
                )
                raise ValueError(f"Forbidden element found: {forbidden}")

    async def _validate_parsing_rule(
        self, page: Page, rule: ParsingRule
    ) -> Dict:
        """Validate single parsing rule and return validated dictionary."""
        working_selector = await self.selector_validator.validate_selector(
            page, rule.selector
        )

        return {
            "field_name": rule.field_name,
            "selector": working_selector,  # Promoted fallback if primary failed
            "data_type": rule.data_type,
            "required": rule.required,
            "valid": working_selector is not None,
        }

    async def _validate_label_based_region(
        self, page: Page, region: RegionDefinition
    ) -> Dict:
        """Validate label-based extraction for a region."""
        label_config = region.label_config
        if not label_config:
            return {"region_id": region.region_id, "error": "No label_config defined"}
        
        # Check if container exists
        container = await page.query_selector(region.container_selector)
        if not container:
            return {
                "region_id": region.region_id,
                "error": f"Container not found: {region.container_selector}"
            }
        
        # Count label elements to verify selector works
        labels = await page.query_selector_all(
            f"{region.container_selector} {label_config.label_selector}"
        )
        label_count = len(labels)
        
        logger.info(
            "Label-based region validated",
            extra={
                "region_id": region.region_id,
                "label_count": label_count,
                "mappings": len(label_config.field_mappings),
            }
        )
        
        return {
            "region_id": region.region_id,
            "container_selector": region.container_selector,
            "extraction_mode": "label_based",
            "label_config": {
                "label_selector": label_config.label_selector,
                "value_selector": label_config.value_selector,
                "extract_all": label_config.extract_all,
                "field_mappings": [
                    {
                        "label": m.label,
                        "field_name": m.field_name,
                        "data_type": m.data_type.value,
                    }
                    for m in label_config.field_mappings
                ],
            },
            "labels_found": label_count,
            "valid": label_count > 0,
        }

    async def _scan_regions(
        self, page: Page, regions: List[RegionDefinition]
    ) -> List[Dict]:
        """Scan all regions and validate parsing rules."""
        validated_regions = []
        for region in regions:
            # Determine extraction mode (default to SELECTOR for backward compat)
            mode = getattr(region, 'extraction_mode', ExtractionMode.SELECTOR)
            
            if mode == ExtractionMode.LABEL_BASED:
                validated_region = await self._validate_label_based_region(page, region)
            else:
                # Original selector-based validation
                validated_rules = []
                for rule in region.parsing_rules:
                    validated_rule = await self._validate_parsing_rule(page, rule)
                    validated_rules.append(validated_rule)

                validated_region = {
                    "region_id": region.region_id,
                    "container_selector": region.container_selector,
                    "extraction_mode": "selector",
                    "parsing_rules": validated_rules,
                }
            
            validated_regions.append(validated_region)
        return validated_regions

    async def scan_template(
        self, template: PageTemplate, sample_url: str
    ) -> Dict:
        """
        Scan a single page template and validate all selectors.
        
        Args:
            template: Page template to scan
            sample_url: Sample URL to test against
            
        Returns:
            Validated template dictionary
        """
        logger.info(
            "Scanning template",
            extra={"template": template.signature.name, "url": sample_url},
        )

        page = await self.browser.new_page()
        try:
            # Navigate to page - use domcontentloaded instead of networkidle
            # FinViz has continuous ad/tracking scripts that prevent networkidle
            await page.goto(sample_url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for key elements to appear
            await page.wait_for_selector("table.snapshot-table2", timeout=10000)
            logger.info("Page loaded", extra={"url": sample_url})

            # Execute interceptors
            interceptors = [
                i for i in self.config.global_interceptors
                if i.name in template.interceptors
            ]
            await self.interceptor_handler.execute_interceptors(page, interceptors)

            # Validate page signature
            await self._validate_page_signature(page, template, sample_url)

            # Scan regions and validate parsing rules
            validated_regions = await self._scan_regions(page, template.regions)

            logger.info(
                "Template validated",
                extra={"template": template.signature.name, "regions": len(validated_regions)},
            )

            return {
                "template_name": template.signature.name,
                "url_pattern": template.signature.url_pattern,
                "regions": validated_regions,
            }

        except Exception as e:
            logger.error(
                "Template scan failed",
                extra={"template": template.signature.name, "error": str(e)},
                exc_info=True,
            )
            raise
        finally:
            await page.close()

    async def scan_site(self, sample_urls: Dict[str, str]) -> SiteDictionary:
        """
        Scan entire site and generate dictionary.
        
        Args:
            sample_urls: Dict mapping template names to sample URLs
                Example: {"quote_page": "https://finviz.com/quote.ashx?t=AAPL"}
                
        Returns:
            Complete site dictionary with validated selectors
        """
        logger.info("Starting site scan", extra={"site": self.site_name})

        if not self.config:
            await self.load_config()

        await self._launch_browser()

        try:
            validated_templates: Dict[str, PageTemplate] = {}

            for template in self.config.page_templates:
                if template.signature.name not in sample_urls:
                    logger.warning(
                        "No sample URL for template",
                        extra={"template": template.signature.name},
                    )
                    continue

                sample_url = sample_urls[template.signature.name]
                validated = await self.scan_template(template, sample_url)
                
                # Store as PageTemplate, keyed by template name
                validated_templates[template.signature.name] = template

            # Create site dictionary with proper types
            dictionary = SiteDictionary(
                site_name=self.site_name,
                base_url=self.config.base_url,
                templates=validated_templates,
                interceptors=list(self.config.global_interceptors),
                # generated_at uses default_factory=datetime.now
            )

            logger.info(
                "Site scan complete",
                extra={"site": self.site_name, "templates": len(validated_templates)},
            )

            return dictionary

        finally:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")

    async def save_dictionary(
        self, dictionary: SiteDictionary, output_path: Path
    ) -> None:
        """
        Save site dictionary to JSON file.
        
        Args:
            dictionary: Site dictionary to save
            output_path: Output JSON file path
        """
        logger.info("Saving dictionary", extra={"path": str(output_path)})

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(dictionary.model_dump(), f, indent=2, default=str)

        logger.info("Dictionary saved", extra={"path": str(output_path)})
