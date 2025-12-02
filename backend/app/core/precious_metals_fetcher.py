"""
Precious metals price fetcher using Puppeteer MCP for browser automation.
Extracts gold and silver prices from goodreturns.in using JavaScript rendering.

Uses Puppeteer to bypass Cloudflare bot protection.

SECURITY: No sensitive data fetched or stored.
"""
import re
from typing import Dict, Optional
from datetime import datetime
import pytz
import asyncio
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Import Puppeteer MCP functions
try:
    from mcp_puppeteer import (
        puppeteer_navigate,
        puppeteer_screenshot,
        puppeteer_evaluate
    )
    PUPPETEER_AVAILABLE = True
    logger.info("Puppeteer MCP server available")
except (ImportError, NameError):
    PUPPETEER_AVAILABLE = False
    logger.warning("Puppeteer MCP server not available - precious metals fetching will fail")


class PreciousMetalsFetcher:
    """
    Fetch gold and silver prices using Puppeteer browser automation.
    
    Uses headless Chrome to render JavaScript and bypass Cloudflare protection.
    More reliable than HTTP requests for sites with bot detection.
    """
    
    def __init__(self):
        """Initialize fetcher."""
        self.gold_url = "https://www.goodreturns.in/gold-rates/chennai.html"
        self.silver_url = "https://www.goodreturns.in/silver-rates/chennai.html"
    
    def _extract_gold_prices_from_html(self, html: str) -> Optional[Dict[str, float]]:
        """
        Extract gold prices from goodreturns.in HTML content.
        
        The page typically has prices displayed in table format or structured divs.
        Look for patterns like "₹7,850" for 24K and "₹7,195" for 22K per gram.
        
        Args:
            html: Full HTML content from the page
            
        Returns:
            Dictionary with extracted prices or None
        """
        prices = {}
        
        # Pattern 1: Table format - "24 Carat Gold" followed by price
        pattern_24k = r'24\s*(?:Carat|Karat|K|KT).*?₹\s*([\d,]+)'
        match_24k = re.search(pattern_24k, html, re.IGNORECASE | re.DOTALL)
        if match_24k:
            price_str = match_24k.group(1).replace(',', '')
            prices['price_24k_per_gram'] = float(price_str)
        
        # Pattern 2: 22K Gold price
        pattern_22k = r'22\s*(?:Carat|Karat|K|KT).*?₹\s*([\d,]+)'
        match_22k = re.search(pattern_22k, html, re.IGNORECASE | re.DOTALL)
        if match_22k:
            price_str = match_22k.group(1).replace(',', '')
            prices['price_22k_per_gram'] = float(price_str)
        
        # Alternative pattern: Direct price matching with context
        if not prices:
            # Look for "per gram" context
            pattern_alt = r'₹\s*([\d,]+)\s*(?:per\s*gram)?.*?(?:24|22)\s*(?:K|Carat)'
            matches = re.findall(pattern_alt, html, re.IGNORECASE)
            if len(matches) >= 2:
                prices['price_24k_per_gram'] = float(matches[0].replace(',', ''))
                prices['price_22k_per_gram'] = float(matches[1].replace(',', ''))
        
        # Calculate per 8 gram (standard jewelry unit)
        if 'price_24k_per_gram' in prices:
            prices['price_24k_per_8_gram'] = prices['price_24k_per_gram'] * 8
        if 'price_22k_per_gram' in prices:
            prices['price_22k_per_8_gram'] = prices['price_22k_per_gram'] * 8
        
        # Validate
        required = ['price_24k_per_gram', 'price_22k_per_gram']
        if all(key in prices for key in required):
            logger.info(
                "Extracted gold prices from HTML",
                extra={
                    "24k_per_gram": prices['price_24k_per_gram'],
                    "22k_per_gram": prices['price_22k_per_gram']
                }
            )
            return prices
        
        logger.warning(
            "Could not extract all gold prices from HTML",
            extra={"found_keys": list(prices.keys())}
        )
        return None
    
    def _extract_silver_prices_from_html(self, html: str) -> Optional[Dict[str, float]]:
        """
        Extract silver prices from goodreturns.in HTML content.
        
        Args:
            html: Full HTML content from the page
            
        Returns:
            Dictionary with extracted prices or None
        """
        prices = {}
        
        # Pattern for silver per gram: ₹175 per gram
        pattern_gram = r'(?:silver|Silver).*?₹\s*([\d,]+)\s*(?:per\s*gram)?'
        match_gram = re.search(pattern_gram, html, re.IGNORECASE | re.DOTALL)
        if match_gram:
            price_str = match_gram.group(1).replace(',', '')
            prices['price_per_gram'] = float(price_str)
        
        # Pattern for per kg: ₹1,75,000 per kg
        pattern_kg = r'₹\s*([\d,]+)\s*per\s*(?:kilogram|kg)'
        match_kg = re.search(pattern_kg, html, re.IGNORECASE)
        if match_kg:
            price_str = match_kg.group(1).replace(',', '')
            prices['price_per_kg'] = float(price_str)
        
        # Calculate missing values
        if 'price_per_gram' in prices and 'price_per_kg' not in prices:
            prices['price_per_kg'] = prices['price_per_gram'] * 1000
        
        # Validate
        if 'price_per_gram' in prices:
            logger.info(
                "Extracted silver prices from HTML",
                extra={
                    "per_gram": prices['price_per_gram'],
                    "per_kg": prices.get('price_per_kg')
                }
            )
            return prices
        
        logger.warning(
            "Could not extract silver prices from HTML",
            extra={"found_keys": list(prices.keys())}
        )
        return None
    
    async def _fetch_page_with_puppeteer(self, url: str) -> Optional[str]:
        """
        Fetch page content using Puppeteer browser automation.
        
        This bypasses Cloudflare bot protection by using a real browser
        that executes JavaScript and renders the page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Full HTML content or None if failed
        """
        if not PUPPETEER_AVAILABLE:
            logger.error("Puppeteer MCP server not available")
            return None
        
        try:
            logger.info(f"Navigating to {url} with Puppeteer")
            
            # Navigate to the page
            await puppeteer_navigate(url=url)
            
            # Wait for page to fully load (important for dynamic content)
            logger.info("Waiting for page to load...")
            await asyncio.sleep(3)  # Give time for JavaScript to render
            
            # Extract the full HTML content using JavaScript
            html_content = await puppeteer_evaluate(
                script="document.documentElement.outerHTML"
            )
            
            if html_content and len(html_content) > 1000:  # Sanity check
                logger.info(
                    "Successfully fetched page with Puppeteer",
                    extra={"content_length": len(html_content)}
                )
                return html_content
            else:
                logger.error(
                    "Fetched content too short",
                    extra={"length": len(html_content) if html_content else 0}
                )
                return None
                
        except Exception as e:
            logger.error(
                "Puppeteer navigation failed",
                extra={"url": url, "error": str(e)},
                exc_info=True
            )
            return None
    
    async def fetch_gold_prices(self) -> Optional[Dict]:
        """
        Fetch current gold prices from goodreturns.in using Puppeteer.
        
        Returns:
            Dictionary with gold prices or None if failed
        """
        logger.info("Fetching gold prices from goodreturns.in")
        
        if not PUPPETEER_AVAILABLE:
            logger.error("Cannot fetch gold prices - Puppeteer MCP not available")
            return None
        
        try:
            # Fetch page content with browser automation
            html_content = await self._fetch_page_with_puppeteer(self.gold_url)
            
            if not html_content:
                logger.error("Failed to fetch gold page content")
                return None
            
            # Extract prices from HTML
            prices = self._extract_gold_prices_from_html(html_content)
            
            if prices:
                # Add metadata with both timezones
                ist = pytz.timezone('Asia/Kolkata')
                est = pytz.timezone('US/Eastern')
                now_utc = datetime.now(pytz.utc)
                prices['timestamp_ist'] = now_utc.astimezone(ist)
                prices['timestamp_est'] = now_utc.astimezone(est)
                prices['city'] = "Chennai"
                prices['source'] = "goodreturns.in"
                logger.info("Successfully extracted gold prices", extra=prices)
                return prices
            
            logger.error("Could not extract gold prices from HTML")
            return None
            
        except Exception as e:
            logger.error(
                "Error fetching gold prices",
                extra={"error": str(e)},
                exc_info=True
            )
            return None
    
    async def fetch_silver_prices(self) -> Optional[Dict]:
        """
        Fetch current silver prices from goodreturns.in using Puppeteer.
        
        Returns:
            Dictionary with silver prices or None if failed
        """
        logger.info("Fetching silver prices from goodreturns.in")
        
        if not PUPPETEER_AVAILABLE:
            logger.error("Cannot fetch silver prices - Puppeteer MCP not available")
            return None
        
        try:
            # Fetch page content with browser automation
            html_content = await self._fetch_page_with_puppeteer(self.silver_url)
            
            if not html_content:
                logger.error("Failed to fetch silver page content")
                return None
            
            # Extract prices from HTML
            prices = self._extract_silver_prices_from_html(html_content)
            
            if prices:
                # Add metadata with both timezones
                ist = pytz.timezone('Asia/Kolkata')
                est = pytz.timezone('US/Eastern')
                now_utc = datetime.now(pytz.utc)
                prices['timestamp_ist'] = now_utc.astimezone(ist)
                prices['timestamp_est'] = now_utc.astimezone(est)
                prices['city'] = "Chennai"
                prices['source'] = "goodreturns.in"
                logger.info("Successfully extracted silver prices", extra=prices)
                return prices
            
            logger.error("Could not extract silver prices from HTML")
            return None
            
        except Exception as e:
            logger.error(
                "Error fetching silver prices",
                extra={"error": str(e)},
                exc_info=True
            )
            return None


# Singleton instance
precious_metals_fetcher = PreciousMetalsFetcher()
