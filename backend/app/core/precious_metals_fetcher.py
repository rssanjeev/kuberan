"""
Precious metals price fetcher using Brave Search MCP.
Extracts gold and silver prices from search results.

SECURITY: No sensitive data fetched or stored.
"""
import re
from typing import Dict, Optional, List
from datetime import datetime
import pytz
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PreciousMetalsFetcher:
    """
    Fetch gold and silver prices using Brave Search API.
    
    Advantages over web scraping:
    - No HTML parsing needed
    - No 403 errors
    - More reliable
    - Faster
    """
    
    def __init__(self):
        """Initialize fetcher."""
        pass
    
    def _extract_gold_prices(self, description: str) -> Optional[Dict[str, float]]:
        """
        Extract gold prices from search result description.
        
        Expected format from goodreturns.in:
        "₹12,600 per gram for 24 karat gold, ₹11,550 per gram for 22 karat gold"
        
        Args:
            description: Search result description text
            
        Returns:
            Dictionary with extracted prices or None
        """
        prices = {}
        
        # Pattern for 24K per gram: ₹12,600 per gram for 24 karat
        pattern_24k = r'₹?([\d,]+)\s*per\s*gram\s*for\s*24\s*(?:karat|carat|K)'
        match_24k = re.search(pattern_24k, description, re.IGNORECASE)
        if match_24k:
            price_str = match_24k.group(1).replace(',', '')
            prices['price_24k_per_gram'] = float(price_str)
        
        # Pattern for 22K per gram: ₹11,550 per gram for 22 karat
        pattern_22k = r'₹?([\d,]+)\s*per\s*gram\s*for\s*22\s*(?:karat|carat|K)'
        match_22k = re.search(pattern_22k, description, re.IGNORECASE)
        if match_22k:
            price_str = match_22k.group(1).replace(',', '')
            prices['price_22k_per_gram'] = float(price_str)
        
        # Calculate per 8 gram (standard jewelry unit in India)
        if 'price_24k_per_gram' in prices:
            prices['price_24k_per_8_gram'] = prices['price_24k_per_gram'] * 8
        if 'price_22k_per_gram' in prices:
            prices['price_22k_per_8_gram'] = prices['price_22k_per_gram'] * 8
        
        # Validate we got all required prices
        required = ['price_24k_per_gram', 'price_22k_per_gram']
        if all(key in prices for key in required):
            logger.info(
                "Extracted gold prices from search",
                extra={
                    "24k_per_gram": prices['price_24k_per_gram'],
                    "22k_per_gram": prices['price_22k_per_gram']
                }
            )
            return prices
        
        logger.warning(
            "Could not extract all gold prices",
            extra={"found_keys": list(prices.keys())}
        )
        return None
    
    def _extract_silver_prices(self, description: str) -> Optional[Dict[str, float]]:
        """
        Extract silver prices from search result description.
        
        Expected format from goodreturns.in:
        "₹175 per gram and ₹1,75,000 per kilogram"
        
        Args:
            description: Search result description text
            
        Returns:
            Dictionary with extracted prices or None
        """
        prices = {}
        
        # Pattern for per gram: ₹175 per gram
        pattern_gram = r'₹?([\d,]+)\s*per\s*gram'
        match_gram = re.search(pattern_gram, description, re.IGNORECASE)
        if match_gram:
            price_str = match_gram.group(1).replace(',', '')
            prices['price_per_gram'] = float(price_str)
        
        # Pattern for per kg: ₹1,75,000 per kilogram or ₹175000 per kg
        pattern_kg = r'₹?([\d,]+)\s*per\s*(?:kilogram|kg)'
        match_kg = re.search(pattern_kg, description, re.IGNORECASE)
        if match_kg:
            price_str = match_kg.group(1).replace(',', '')
            prices['price_per_kg'] = float(price_str)
        
        # Validate
        if 'price_per_gram' in prices and 'price_per_kg' in prices:
            logger.info(
                "Extracted silver prices from search",
                extra={
                    "per_gram": prices['price_per_gram'],
                    "per_kg": prices['price_per_kg']
                }
            )
            return prices
        
        # If we only have per gram, calculate per kg
        if 'price_per_gram' in prices and 'price_per_kg' not in prices:
            prices['price_per_kg'] = prices['price_per_gram'] * 1000
            logger.info(
                "Calculated silver per kg from per gram",
                extra={"per_kg": prices['price_per_kg']}
            )
            return prices
        
        logger.warning(
            "Could not extract silver prices",
            extra={"found_keys": list(prices.keys())}
        )
        return None
    
    def _parse_brave_results(self, results_text: str) -> List[Dict]:
        """
        Parse Brave Search results from MCP tool output.
        
        Args:
            results_text: Raw results from brave_web_search
            
        Returns:
            List of result dictionaries
        """
        # Results are returned as formatted text with URL, title, description
        results = []
        
        # Split by result boundaries (typically each result on separate lines)
        # The MCP tool returns results in a specific format - parse accordingly
        lines = results_text.split('\n')
        
        current_result = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_result:
                    results.append(current_result)
                    current_result = {}
                continue
            
            # Parse URL, title, description from formatted output
            if line.startswith('url:'):
                current_result['url'] = line.split('url:', 1)[1].strip()
            elif line.startswith('title:'):
                current_result['title'] = line.split('title:', 1)[1].strip()
            elif line.startswith('description:'):
                current_result['description'] = line.split('description:', 1)[1].strip()
        
        # Add last result if exists
        if current_result:
            results.append(current_result)
        
        return results
    
    async def fetch_gold_prices(self) -> Optional[Dict]:
        """
        Fetch current gold prices using Brave Search.
        
        Returns:
            Dictionary with gold prices or None if failed
        """
        logger.info("Fetching gold prices via Brave Search")
        
        try:
            # Call Brave Search MCP tool
            try:
                results_raw = await self._call_brave_search(
                    "gold rates chennai today"
                )
            except Exception as e:
                logger.error(
                    "Failed to call Brave Search API",
                    extra={"error": str(e)},
                    exc_info=True
                )
                return None
            
            if not results_raw:
                logger.error("No search results for gold prices")
                return None
            
            # Parse results
            results = self._parse_brave_results(results_raw)
            
            # Try to extract from first few results
            for result in results:
                description = result.get('description', '')
                url = result.get('url', '')
                
                # Check if this is from goodreturns.in
                if 'goodreturns.in' not in url.lower():
                    continue
                
                # Try to extract prices
                prices = self._extract_gold_prices(description)
                if prices:
                    # Add metadata with both timezones
                    ist = pytz.timezone('Asia/Kolkata')
                    est = pytz.timezone('US/Eastern')
                    now_utc = datetime.now(pytz.utc)
                    prices['timestamp_ist'] = now_utc.astimezone(ist)
                    prices['timestamp_est'] = now_utc.astimezone(est)
                    prices['city'] = "Chennai"
                    prices['source'] = "goodreturns.in"
                    return prices
            
            logger.error("Could not extract gold prices from any result")
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
        Fetch current silver prices using Brave Search.
        
        Returns:
            Dictionary with silver prices or None if failed
        """
        logger.info("Fetching silver prices via Brave Search")
        
        try:
            # Use the MCP Brave Search tool
            try:
                results_raw = await self._call_brave_search(
                    "silver rates chennai today per gram per kg"
                )
            except Exception as e:
                logger.error(
                    "Failed to call Brave Search API",
                    extra={"error": str(e)},
                    exc_info=True
                )
                return None
            
            if not results_raw:
                logger.error("No search results for silver prices")
                return None
            
            # Parse results
            results = self._parse_brave_results(results_raw)
            
            # Try to extract from first few results
            for result in results:
                description = result.get('description', '')
                url = result.get('url', '')
                
                # Check if this is from goodreturns.in
                if 'goodreturns.in' not in url.lower():
                    continue
                
                # Try to extract prices
                prices = self._extract_silver_prices(description)
                if prices:
                    # Add metadata with both timezones
                    ist = pytz.timezone('Asia/Kolkata')
                    est = pytz.timezone('US/Eastern')
                    now_utc = datetime.now(pytz.utc)
                    prices['timestamp_ist'] = now_utc.astimezone(ist)
                    prices['timestamp_est'] = now_utc.astimezone(est)
                    prices['city'] = "Chennai"
                    prices['source'] = "goodreturns.in"
                    return prices
            
            logger.error("Could not extract silver prices from any result")
            return None
            
        except Exception as e:
            logger.error(
                "Error fetching silver prices",
                extra={"error": str(e)},
                exc_info=True
            )
            return None
    
    async def _call_brave_search(self, query: str) -> str:
        """
        Call Brave Search MCP server to get web results.
        
        Uses the configured Brave Search MCP server.
        Fails if MCP server is not available.
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results as string with url, title, description
            
        Raises:
            Exception: If Brave Search MCP server is not available
        """
        logger.info(
            "Calling Brave Search MCP server",
            extra={"query": query}
        )
        
        try:
            # Call the Brave Search MCP tool (configured in MCP settings)
            results = await mcp_brave_search_brave_web_search(
                query=query,
                count=3
            )
            
            # Format MCP results
            formatted_results = []
            if isinstance(results, dict) and 'results' in results:
                for result in results.get('results', []):
                    formatted_results.append(
                        f"url: {result.get('url', '')}\n"
                        f"title: {result.get('title', '')}\n"
                        f"description: {result.get('description', '')}\n"
                    )
            
            formatted_text = "\n".join(formatted_results)
            logger.info(
                "Brave Search MCP call successful",
                extra={"result_count": len(formatted_results)}
            )
            return formatted_text
            
        except NameError as e:
            logger.error(
                "Brave Search MCP server not available",
                extra={"error": str(e)},
                exc_info=True
            )
            raise Exception(
                f"Brave Search MCP server not configured or not available: {str(e)}"
            )
        except Exception as e:
            logger.error(
                "Failed to call Brave Search API",
                extra={"error": str(e)},
                exc_info=True
            )
            raise


# Singleton instance
precious_metals_fetcher = PreciousMetalsFetcher()
