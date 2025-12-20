"""
Cartographer Selector Validator - Validates CSS Selectors

Last Updated: 2025-12-20
Status: Active
Purpose: Test and validate CSS selectors on web pages to find working selectors

Extracted from scanner.py to comply with 300-line limit.
"""

from typing import Optional

from playwright.async_api import Page

from app.core.logging_config import get_logger
from app.models.cartographer import SelectorStrategy

logger = get_logger(__name__)


class SelectorValidator:
    """
    Validates CSS selectors on web pages.
    
    Tests primary selector and fallbacks to find first working selector.
    Used during scanning phase to discover which selectors work on live pages.
    """

    async def validate_selector(
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
        # Try primary selector first
        if await self._test_selector(page, selector_strategy.primary):
            logger.debug(
                "Primary selector valid",
                extra={"selector": selector_strategy.primary},
            )
            return selector_strategy.primary

        # Try fallback selectors
        for fallback in selector_strategy.fallbacks:
            if await self._test_selector(page, fallback):
                logger.info(
                    "Fallback selector valid",
                    extra={
                        "selector": fallback,
                        "primary": selector_strategy.primary,
                    },
                )
                return fallback

        # All selectors failed
        logger.warning(
            "All selectors failed",
            extra={
                "primary": selector_strategy.primary,
                "fallback_count": len(selector_strategy.fallbacks),
            },
        )
        return None

    async def _test_selector(self, page: Page, selector: str) -> bool:
        """
        Test if single selector works on page.
        
        Args:
            page: Playwright page instance
            selector: CSS selector to test
            
        Returns:
            True if selector found element, False otherwise
        """
        try:
            element = await page.query_selector(selector)
            return element is not None
        except Exception as e:
            logger.debug(
                "Selector test failed",
                extra={"selector": selector, "error": str(e)},
            )
            return False
