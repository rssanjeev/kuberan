"""
Ticker Discovery Module - Fetch all available tickers from Alpha Vantage.

Uses Alpha Vantage LISTING_STATUS API to get comprehensive list of all
US stocks and ETFs (~8,000-10,000 tickers).

SECURITY: No sensitive data stored, only public ticker information.
"""

import csv
import io
import os
from typing import List, Dict, Optional
from datetime import datetime
import httpx

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TickerDiscovery:
    """
    Discover all available tickers using Alpha Vantage LISTING_STATUS API.
    
    API Documentation:
    https://www.alphavantage.co/documentation/#listing-status
    
    Returns CSV with fields:
    - symbol: Ticker symbol
    - name: Company name
    - exchange: NASDAQ, NYSE, etc.
    - assetType: Stock, ETF, etc.
    - ipoDate: IPO date
    - delistingDate: If delisted
    - status: Active or Delisted
    """
    
    def __init__(self):
        """Initialize ticker discovery service."""
        self.api_key = os.getenv("ALPHA_VANTAGE_KEY")
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_KEY not set, ticker discovery will fail")
        
        self.base_url = "https://www.alphavantage.co/query"
    
    async def discover_all_tickers(
        self,
        status: str = "active",
        include_delisted: bool = False
    ) -> List[Dict]:
        """
        Discover all available tickers from Alpha Vantage.
        
        Args:
            status: "active" (default) or "delisted"
            include_delisted: If True, fetch both active and delisted
            
        Returns:
            List of ticker dictionaries with fields:
            - symbol: str
            - name: str
            - exchange: str
            - asset_type: str (Stock, ETF, etc.)
            - ipo_date: str
            - status: str (Active/Delisted)
            
        Raises:
            Exception: If API call fails or API key missing
        """
        if not self.api_key:
            raise Exception("ALPHA_VANTAGE_KEY environment variable not set")
        
        logger.info("Starting ticker discovery", extra={"status": status})
        
        all_tickers = []
        
        # Fetch active tickers
        if status == "active" or include_delisted:
            active_tickers = await self._fetch_listing_status("active")
            all_tickers.extend(active_tickers)
            logger.info(
                "Fetched active tickers",
                extra={"count": len(active_tickers)}
            )
        
        # Fetch delisted tickers if requested
        if status == "delisted" or include_delisted:
            delisted_tickers = await self._fetch_listing_status("delisted")
            all_tickers.extend(delisted_tickers)
            logger.info(
                "Fetched delisted tickers",
                extra={"count": len(delisted_tickers)}
            )
        
        logger.info(
            "Ticker discovery complete",
            extra={
                "total_tickers": len(all_tickers),
                "include_delisted": include_delisted
            }
        )
        
        return all_tickers
    
    async def _fetch_listing_status(self, status: str) -> List[Dict]:
        """
        Fetch listing status from Alpha Vantage API.
        
        Args:
            status: "active" or "delisted"
            
        Returns:
            List of parsed ticker dictionaries
        """
        params = {
            "function": "LISTING_STATUS",
            "apikey": self.api_key,
            "state": status
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                # Parse CSV response
                csv_content = response.text
                return self._parse_csv_response(csv_content, status)
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Alpha Vantage API HTTP error",
                extra={"status_code": e.response.status_code, "status": status},
                exc_info=True
            )
            raise Exception(f"Alpha Vantage API error: {e.response.status_code}") from e
        
        except httpx.TimeoutException:
            logger.error(
                "Alpha Vantage API timeout",
                extra={"status": status},
                exc_info=True
            )
            raise Exception("Alpha Vantage API timeout") from None
        
        except Exception as e:
            logger.error(
                "Failed to fetch listing status",
                extra={"status": status, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _parse_csv_response(self, csv_content: str, status: str) -> List[Dict]:
        """
        Parse CSV response from Alpha Vantage.
        
        CSV format:
        symbol,name,exchange,assetType,ipoDate,delistingDate,status
        
        Args:
            csv_content: CSV string from API
            status: "active" or "delisted" (for filtering)
            
        Returns:
            List of parsed ticker dictionaries
        """
        tickers = []
        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            try:
                ticker_data = {
                    "symbol": row.get("symbol", "").strip().upper(),
                    "name": row.get("name", "").strip(),
                    "exchange": row.get("exchange", "").strip(),
                    "asset_type": row.get("assetType", "Stock").strip(),
                    "ipo_date": row.get("ipoDate", "").strip() or None,
                    "delisting_date": row.get("delistingDate", "").strip() or None,
                    "status": row.get("status", "Active").strip()
                }
                
                # Validate symbol exists
                if not ticker_data["symbol"]:
                    continue
                
                tickers.append(ticker_data)
            
            except Exception as e:
                logger.warning(
                    "Failed to parse ticker row",
                    extra={"row": str(row)[:100], "error": str(e)}
                )
                continue
        
        logger.info(
            "Parsed CSV response",
            extra={"tickers_parsed": len(tickers), "status": status}
        )
        
        return tickers
    
    def get_ticker_statistics(self, tickers: List[Dict]) -> Dict:
        """
        Get statistics about discovered tickers.
        
        Args:
            tickers: List of ticker dictionaries
            
        Returns:
            Statistics dictionary with counts by type, exchange, status
        """
        if not tickers:
            return {
                "total": 0,
                "by_asset_type": {},
                "by_exchange": {},
                "by_status": {}
            }
        
        # Count by asset type
        asset_types = {}
        for ticker in tickers:
            asset_type = ticker.get("asset_type", "Unknown")
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        # Count by exchange
        exchanges = {}
        for ticker in tickers:
            exchange = ticker.get("exchange", "Unknown")
            exchanges[exchange] = exchanges.get(exchange, 0) + 1
        
        # Count by status
        statuses = {}
        for ticker in tickers:
            status = ticker.get("status", "Unknown")
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total": len(tickers),
            "by_asset_type": asset_types,
            "by_exchange": exchanges,
            "by_status": statuses
        }
    
    def filter_tickers(
        self,
        tickers: List[Dict],
        asset_type: Optional[str] = None,
        exchange: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter tickers by criteria.
        
        Args:
            tickers: List of ticker dictionaries
            asset_type: Filter by asset type (e.g., "Stock", "ETF")
            exchange: Filter by exchange (e.g., "NASDAQ", "NYSE")
            status: Filter by status (e.g., "Active", "Delisted")
            
        Returns:
            Filtered list of tickers
        """
        filtered = tickers
        
        if asset_type:
            filtered = [t for t in filtered if t.get("asset_type") == asset_type]
        
        if exchange:
            filtered = [t for t in filtered if t.get("exchange") == exchange]
        
        if status:
            filtered = [t for t in filtered if t.get("status") == status]
        
        logger.info(
            "Filtered tickers",
            extra={
                "original_count": len(tickers),
                "filtered_count": len(filtered),
                "asset_type": asset_type,
                "exchange": exchange,
                "status": status
            }
        )
        
        return filtered


# Singleton instance
ticker_discovery = TickerDiscovery()
