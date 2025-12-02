"""
MASSIVE Delta Extractor Job - Weekly IPO detection.

Detects new tickers that have been added since the last run by querying 
MASSIVE API with list_date filter. Runs weekly to catch recent IPOs.

Process:
1. Get last successful run timestamp from job metadata
2. Query MASSIVE API: list_date.gte={last_run_date}
3. Save new ticker placeholders to database
4. Update job metadata with current timestamp

SECURITY: No sensitive data stored, only public ticker information.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

from app.core.logging_config import get_logger
from app.services.providers.provider_registry import provider_registry
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions
# ============================================================================

async def fetch_new_tickers_since_date(provider, since_date: str) -> List[Dict]:
    """
    Fetch all tickers listed since a specific date.
    
    Uses MASSIVE API filter: list_date.gte={since_date}
    
    Args:
        provider: MASSIVE provider instance
        since_date: ISO date string (YYYY-MM-DD)
        
    Returns:
        List of ticker dictionaries with basic metadata
    """
    try:
        import httpx
        
        all_tickers = []
        next_url = None
        page_count = 0
        
        await provider.rate_limiter.acquire(priority=0)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                page_count += 1
                
                if next_url:
                    # Pagination URL - add API key
                    separator = "&" if "?" in next_url else "?"
                    url_with_key = f"{next_url}{separator}apiKey={provider.api_key}"
                    response = await client.get(url_with_key)
                else:
                    # First request with date filter
                    params = {
                        "apiKey": provider.api_key,
                        "active": "true",
                        "limit": 1000,
                        "market": "stocks",
                        "list_date.gte": since_date  # KEY: Delta extraction filter
                    }
                    response = await client.get(
                        f"{provider.base_url}/v3/reference/tickers",
                        params=params
                    )
                
                provider.rate_limiter.update_from_response(response.headers)
                
                if response.status_code == 429:
                    logger.warning("Rate limit exceeded, retrying after delay")
                    await asyncio.sleep(60)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if not data or "results" not in data:
                    logger.warning("No results in delta extraction response")
                    break
                
                results = data.get("results", [])
                all_tickers.extend(results)
                
                logger.info(
                    f"Delta extraction page {page_count}: {len(results)} tickers",
                    extra={
                        "page": page_count,
                        "tickers_this_page": len(results),
                        "total_so_far": len(all_tickers)
                    }
                )
                
                # Check for next page
                next_url = data.get("next_url")
                if not next_url:
                    break
                
                # Rate limit delay: 5 calls/min = 12 seconds between calls
                await asyncio.sleep(12)
        
        logger.info(
            f"Delta extraction complete: {len(all_tickers)} new tickers found",
            extra={"since_date": since_date, "total_tickers": len(all_tickers)}
        )
        
        return all_tickers
    
    except Exception as e:
        logger.error(
            "Failed to fetch new tickers in delta extraction",
            extra={"since_date": since_date, "error": str(e)},
            exc_info=True
        )
        return []


async def save_new_ticker(ticker_data: Dict) -> bool:
    """
    Save newly discovered ticker to database.
    
    Similar to bulk discovery but checks for existence first and logs
    differently to distinguish delta updates from bulk discovery.
    
    Args:
        ticker_data: Ticker info from MASSIVE API
        
    Returns:
        True if saved (new ticker), False if already exists or failed
    """
    try:
        ticker = ticker_data.get("ticker", "").strip().upper()
        
        if not ticker:
            logger.warning("Empty ticker symbol in delta extraction, skipping")
            return False
        
        # Check if ticker already exists
        existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
        
        if existing:
            logger.debug(
                f"Ticker {ticker} already in database (discovered elsewhere)",
                extra={"ticker": ticker}
            )
            return False  # Not new, return False to count properly
        
        # Create placeholder for new IPO
        placeholder = CompanyOverview(
            ticker=ticker,
            name=ticker_data.get("name", ""),
            exchange=ticker_data.get("primary_exchange", ""),
            asset_type=_classify_asset_type(ticker_data.get("type", "")),
            currency=ticker_data.get("currency_name", "USD").upper(),
            country="US",
            source_provider="polygon",
            enrichment_status=None,  # Will be enriched by foundation builder
            extended_data={
                "discovered_via": "massive_delta_extraction",
                "list_date": ticker_data.get("list_date", ""),
                "polygon_type": ticker_data.get("type", ""),
                "market": ticker_data.get("market", ""),
                "locale": ticker_data.get("locale", ""),
                "active": ticker_data.get("active", True),
                "cik": ticker_data.get("cik", ""),
                "composite_figi": ticker_data.get("composite_figi", ""),
                "discovery_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await placeholder.insert()
        
        logger.info(
            f"New IPO detected and saved: {ticker}",
            extra={
                "ticker": ticker,
                "company_name": ticker_data.get("name", ""),
                "list_date": ticker_data.get("list_date", ""),
                "asset_type": placeholder.asset_type
            }
        )
        
        return True
    
    except Exception as e:
        logger.error(
            f"Failed to save new ticker in delta extraction",
            extra={"ticker": ticker_data.get("ticker"), "error": str(e)},
            exc_info=True
        )
        return False


def _classify_asset_type(polygon_type: str) -> str:
    """
    Classify Polygon.io ticker type to Kuberan asset type.
    
    Args:
        polygon_type: Type from MASSIVE/Polygon (e.g., "CS", "ETF", "ADRC")
        
    Returns:
        Kuberan asset type (Stock, ETF, or Other)
    """
    polygon_type = polygon_type.upper()
    
    if polygon_type == "ETF":
        return "ETF"
    elif polygon_type in ["CS", "COMMON STOCK", "EQUITY"]:
        return "Stock"
    elif polygon_type in ["ADRC", "GDR", "ADR"]:
        return "Stock"  # ADRs are stocks
    else:
        return "Other"


# ============================================================================
# Job Class: Delta Extraction Orchestration
# ============================================================================

class MassiveDeltaExtractorJob:
    """
    Weekly job to detect new IPOs using MASSIVE API list_date filter.
    
    Timeline:
    - Runs weekly (every Monday at 2 AM EST)
    - Queries tickers with list_date >= last_run_date
    - Typically 5-20 new IPOs per week
    - 1-2 API calls (most weeks fit in 1 page)
    - ~12-24 seconds execution time
    
    First Run:
    - If never run before, uses current_date - 30 days as starting point
    - This catches any recent IPOs missed during bulk discovery
    """
    
    def __init__(self):
        """Initialize delta extractor job."""
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.last_run_date_str: Optional[str] = None  # ISO date for API filter
        self.total_new_tickers: int = 0
    
    async def run(self, lookback_days: Optional[int] = None) -> Dict:
        """
        Execute delta extraction to detect new IPOs.
        
        Args:
            lookback_days: Override lookback period (default: 7 days for weekly run)
            
        Returns:
            Statistics dictionary with extraction results
        """
        if self.is_running:
            logger.warning("Delta extraction job already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            # Determine date range
            if lookback_days:
                since_date = (datetime.utcnow() - timedelta(days=lookback_days)).date()
            elif self.last_run_date_str:
                # Use last successful run date
                since_date = datetime.fromisoformat(self.last_run_date_str).date()
            else:
                # First run: go back 30 days to catch recent IPOs
                since_date = (datetime.utcnow() - timedelta(days=30)).date()
                logger.info(
                    "First delta extraction run, looking back 30 days",
                    extra={"since_date": since_date.isoformat()}
                )
            
            since_date_str = since_date.isoformat()
            
            logger.info(
                "Starting delta extraction for new IPOs",
                extra={"since_date": since_date_str}
            )
            
            # Get MASSIVE provider
            provider = provider_registry.get_provider_by_name("MassiveProvider")
            
            if not provider:
                logger.error("MASSIVE provider not available")
                return {
                    "status": "error",
                    "message": "MASSIVE provider not available"
                }
            
            # Fetch new tickers since date
            new_tickers = await fetch_new_tickers_since_date(provider, since_date_str)
            
            if not new_tickers:
                logger.info(
                    "No new tickers found in delta extraction",
                    extra={"since_date": since_date_str}
                )
                
                # Update last run even if no results
                self.last_run = datetime.utcnow()
                self.last_run_date_str = datetime.utcnow().date().isoformat()
                
                return {
                    "status": "success",
                    "new_tickers_found": 0,
                    "tickers_saved": 0,
                    "since_date": since_date_str,
                    "message": "No new IPOs detected"
                }
            
            # Save new tickers concurrently
            logger.info(
                f"Saving {len(new_tickers)} potential new tickers",
                extra={"ticker_count": len(new_tickers)}
            )
            
            tasks = [save_new_ticker(ticker) for ticker in new_tickers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count actual new tickers (True = new, False = already existed)
            new_count = sum(1 for r in results if r is True)
            already_existed = sum(1 for r in results if r is False)
            
            # Update job state
            self.last_run = datetime.utcnow()
            self.last_run_date_str = datetime.utcnow().date().isoformat()
            self.total_new_tickers += new_count
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "new_tickers_found": len(new_tickers),
                "tickers_saved": new_count,
                "already_existed": already_existed,
                "since_date": since_date_str,
                "next_run_date": self.last_run_date_str,
                "elapsed_seconds": round(elapsed_time, 2),
                "total_new_tickers_all_time": self.total_new_tickers
            }
            
            logger.info(
                "Delta extraction complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Delta extraction failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": str(e)
            }
        
        finally:
            self.is_running = False
    
    def get_job_status(self) -> Dict:
        """Get current job status and statistics."""
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_run_date": self.last_run_date_str,
            "total_new_tickers_discovered": self.total_new_tickers
        }


# Singleton instance
massive_delta_extractor = MassiveDeltaExtractorJob()
