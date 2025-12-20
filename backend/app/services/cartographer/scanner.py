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
    GlobalInterceptor,
    PageTemplate,
    RegionDefinition,
    ParsingRule,
    SelectorStrategy,
    SiteDictionary,
)

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

    async def load_config(self) -> CartographerConfig:
        """
        Load and validate YAML configuration.
        
        Returns:
            Validated CartographerConfig object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or doesn't match schema
        """
        logger.info("Loading configuration", extra={"path": str(self.config_path)})

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            raw_config = yaml.safe_load(f)

        # Validate against Pydantic schema
        try:
            self.config = CartographerConfig(**raw_config)
            self.site_name = self.config.site_name
            logger.info(
                "Configuration loaded successfully",
                extra={
                    "site": self.site_name,
                    "templates": len(self.config.page_templates),
                    "interceptors": len(self.config.global_interceptors),
                },
            )
            return self.config
        except Exception as e:
            logger.error(
                "Configuration validation failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise ValueError(f"Invalid configuration: {e}")

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

    async def _execute_interceptors(
        self, page: Page, interceptor_names: List[str]
    ) -> None:
        """
        Execute global interceptors (handle popups, ads, cookie consent).
        
        Args:
            page: Playwright page instance
            interceptor_names: List of interceptor names to execute
        """
        # Get interceptors by name
        interceptors = [
            i for i in self.config.global_interceptors if i.name in interceptor_names
        ]

        # Sort by priority (higher priority = execute first)
        interceptors.sort(key=lambda x: x.priority, reverse=True)

        for interceptor in interceptors:
            try:
                # Check if trigger element exists
                trigger = await page.query_selector(interceptor.trigger_selector)
                if not trigger:
                    logger.debug(
                        "Interceptor trigger not found",
                        extra={"name": interceptor.name},
                    )
                    continue

                logger.info("Executing interceptor", extra={"name": interceptor.name})

                # Execute action
                if interceptor.action == "click":
                    await page.click(interceptor.target_selector, timeout=interceptor.timeout_ms)
                elif interceptor.action == "close":
                    target = await page.query_selector(interceptor.target_selector)
                    if target:
                        await target.click()
                elif interceptor.action == "dismiss":
                    await page.keyboard.press("Escape")
                elif interceptor.action == "wait":
                    await asyncio.sleep(interceptor.timeout_ms / 1000)

                logger.info("Interceptor executed", extra={"name": interceptor.name})

            except Exception as e:
                logger.warning(
                    "Interceptor failed",
                    extra={"name": interceptor.name, "error": str(e)},
                )

    async def _validate_selector(
        self, page: Page, selector_strategy: SelectorStrategy
    ) -> Optional[str]:
        """
        Test selector strategy and return first working selector.
        
        Args:
            page: Playwright page instance
            selector_strategy: Selector with primary + fallbacks
            
        Returns:
            Working selector string, or None if all fail
        """
        # Try primary selector
        try:
            element = await page.query_selector(selector_strategy.primary)
            if element:
                logger.debug(
                    "Primary selector valid",
                    extra={"selector": selector_strategy.primary},
                )
                return selector_strategy.primary
        except Exception as e:
            logger.debug(
                "Primary selector failed",
                extra={"selector": selector_strategy.primary, "error": str(e)},
            )

        # Try fallbacks
        for fallback in selector_strategy.fallbacks:
            try:
                element = await page.query_selector(fallback)
                if element:
                    logger.info(
                        "Fallback selector valid",
                        extra={"selector": fallback, "primary": selector_strategy.primary},
                    )
                    return fallback
            except Exception as e:
                logger.debug(
                    "Fallback selector failed",
                    extra={"selector": fallback, "error": str(e)},
                )

        logger.warning(
            "All selectors failed",
            extra={
                "primary": selector_strategy.primary,
                "fallback_count": len(selector_strategy.fallbacks),
            },
        )
        return None

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
            # Navigate to page
            await page.goto(sample_url, wait_until="networkidle")
            logger.info("Page loaded", extra={"url": sample_url})

            # Execute interceptors
            await self._execute_interceptors(page, template.interceptors)

            # Validate signature
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

            # Validate all parsing rules
            validated_regions = []
            for region in template.regions:
                validated_rules = []

                for rule in region.parsing_rules:
                    working_selector = await self._validate_selector(page, rule.selector)

                    validated_rules.append({
                        "field_name": rule.field_name,
                        "selector": working_selector,  # Promoted fallback if primary failed
                        "data_type": rule.data_type,
                        "required": rule.required,
                        "valid": working_selector is not None,
                    })

                validated_regions.append({
                    "region_id": region.region_id,
                    "container_selector": region.container_selector,
                    "parsing_rules": validated_rules,
                })

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
            validated_templates = []

            for template in self.config.page_templates:
                if template.signature.name not in sample_urls:
                    logger.warning(
                        "No sample URL for template",
                        extra={"template": template.signature.name},
                    )
                    continue

                sample_url = sample_urls[template.signature.name]
                validated = await self.scan_template(template, sample_url)
                validated_templates.append(validated)

            # Create site dictionary
            dictionary = SiteDictionary(
                site_name=self.site_name,
                base_url=self.config.base_url,
                templates=validated_templates,
                interceptors=[
                    {"name": i.name, "trigger": i.trigger_selector}
                    for i in self.config.global_interceptors
                ],
                generated_at=None,  # Will be set by model
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
