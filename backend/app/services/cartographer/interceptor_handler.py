"""
Cartographer Interceptor Handler - Handles Global Interceptors

Last Updated: 2025-12-20
Status: Active
Purpose: Execute global interceptors (cookie consent, popups, ads) on scraped pages

Extracted from scanner.py to comply with 300-line limit.
"""

import asyncio
from typing import List

from playwright.async_api import Page

from app.core.logging_config import get_logger
from app.models.cartographer import GlobalInterceptor

logger = get_logger(__name__)


class InterceptorHandler:
    """
    Handles execution of global interceptors on web pages.
    
    Interceptors handle common UI obstacles:
    - Cookie consent banners
    - Premium/paywall popups
    - Ad overlays
    - Newsletter signups
    """

    async def execute_interceptors(
        self, page: Page, interceptors: List[GlobalInterceptor]
    ) -> None:
        """
        Execute list of interceptors in priority order.
        
        Args:
            page: Playwright page instance
            interceptors: List of interceptors to execute
        """
        # Sort by priority (higher priority = execute first)
        sorted_interceptors = sorted(interceptors, key=lambda x: x.priority, reverse=True)

        for interceptor in sorted_interceptors:
            await self._handle_interceptor(page, interceptor)

    async def _handle_interceptor(self, page: Page, interceptor: GlobalInterceptor) -> bool:
        """
        Execute single interceptor.
        
        Args:
            page: Playwright page instance
            interceptor: Interceptor configuration
            
        Returns:
            True if interceptor executed successfully, False otherwise
        """
        try:
            # Check if trigger element exists
            trigger = await page.query_selector(interceptor.trigger_selector)
            if not trigger:
                logger.debug(
                    "Interceptor trigger not found",
                    extra={"name": interceptor.name},
                )
                return False

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
            return True

        except Exception as e:
            logger.warning(
                "Interceptor failed",
                extra={"name": interceptor.name, "error": str(e)},
            )
            return False
