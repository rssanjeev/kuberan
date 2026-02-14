"""
MASSIVE Deactivation Detector Job - Delisted ticker detection.

Detects tickers that have been delisted (active=false) by querying MASSIVE API
and comparing against existing database records. Marks inactive tickers appropriately.

Process:
1. Query database for all tickers with enrichment_status != "failed"
2. For each ticker, query MASSIVE API to check active status
3. If active=false, update enrichment_status to "failed"
4. Log deactivation events for monitoring

Schedule: Weekly (runs after delta extraction)

SECURITY: No sensitive data stored, only public ticker information.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

from app.core.logging_config import get_logger
from app.services.providers.provider_registry import provider_registry
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions
# ============================================================================

async def check_ticker_active_status(provider, ticker: str) -> Optional[bool]:
    """
    Check if a ticker is still active via MASSIVE API.
    
    Args:
        provider: MASSIVE provider instance
        ticker: Ticker symbol to check
        
    Returns:
        True if active, False if inactive, None if check failed
    """
    try:
        import httpx
        
        await provider.rate_limiter.acquire(priority=0)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "apiKey": provider.api_key
            }
            response = await client.get(
                f"{provider.base_url}/v3/reference/tickers/{ticker}",
                params=params
            )
            
            provider.rate_limiter.update_from_response(response.headers)
            
            if response.status_code == 404:
                # Ticker not found = likely delisted
                logger.info(
                    f"Ticker {ticker} returned 404 (likely delisted)",
                    extra={"ticker": ticker}
                )
                return False
            
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded checking {ticker}")
                return None  # Will retry later
            
            response.raise_for_status()
            data = response.json()
            
            if not data or "results" not in data:
                logger.warning(f"No results for ticker {ticker}")
                return None
            
            results = data["results"]
            active_status = results.get("active", True)
            
            logger.debug(
                f"Ticker {ticker} active status: {active_status}",
                extra={"ticker": ticker, "active": active_status}
            )
            
            return active_status
    
    except Exception as e:
        logger.error(
            f"Failed to check active status for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return None


async def mark_ticker_inactive(ticker: str) -> bool:
    """
    Mark ticker as inactive in database.
    
    Updates enrichment_status to "failed" and adds deactivation metadata.
    
    Args:
        ticker: Ticker symbol to mark as inactive
        
    Returns:
        True if successfully marked, False otherwise
    """
    try:
        ticker_doc = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
        
        if not ticker_doc:
            logger.warning(f"Ticker {ticker} not found in database")
            return False
        
        # Update enrichment_status to "failed"
        ticker_doc.enrichment_status = "failed"
        
        # Add deactivation metadata
        if not ticker_doc.extended_data:
            ticker_doc.extended_data = {}
        
        ticker_doc.extended_data["deactivation_detected"] = datetime.utcnow().isoformat()
        ticker_doc.extended_data["deactivation_reason"] = "ticker_delisted_or_inactive"
        ticker_doc.extended_data["last_active_check"] = datetime.utcnow().isoformat()
        
        await ticker_doc.save()
        
        logger.info(
            f"Marked ticker {ticker} as inactive",
            extra={
                "ticker": ticker,
                "previous_status": ticker_doc.enrichment_status
            }
        )
        
        return True
    
    except Exception as e:
        logger.error(
            f"Failed to mark ticker {ticker} as inactive",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return False


async def check_and_mark_if_inactive(provider, ticker_doc: CompanyOverview) -> Dict:
    """
    Check ticker active status and mark as inactive if needed.
    
    Args:
        provider: MASSIVE provider instance
        ticker_doc: CompanyOverview document from database
        
    Returns:
        Result dictionary with status and action taken
    """
    ticker = ticker_doc.ticker
    
    # Check active status via API
    is_active = await check_ticker_active_status(provider, ticker)
    
    if is_active is None:
        # Check failed (rate limit, error, etc.)
        return {
            "ticker": ticker,
            "status": "check_failed",
            "action": "none"
        }
    
    if is_active:
        # Still active, no action needed
        return {
            "ticker": ticker,
            "status": "active",
            "action": "none"
        }
    
    # Ticker is inactive, mark it
    marked = await mark_ticker_inactive(ticker)
    
    if marked:
        return {
            "ticker": ticker,
            "status": "inactive",
            "action": "marked_as_failed"
        }
    else:
        return {
            "ticker": ticker,
            "status": "inactive",
            "action": "mark_failed"
        }


# ============================================================================
# Job Class: Deactivation Detection Orchestration
# ============================================================================

class MassiveDeactivationDetectorJob:
    """
    Weekly job to detect delisted/inactive tickers.
    
    Strategy:
    - Check random sample of tickers each week (500 tickers)
    - Full scan over ~24 weeks (12,140 tickers / 500 per week)
    - Prioritize tickers not checked recently
    - Mark inactive tickers with enrichment_status="failed"
    
    Timeline:
    - Runs weekly (every Monday at 3 AM EST, after delta extraction)
    - 500 tickers per run
    - 500 API calls at 5/min = 100 minutes (~1.7 hours)
    - Rate limit friendly: 12 seconds between calls
    
    Benefits:
    - Prevents wasting API calls on delisted tickers
    - Keeps database clean
    - Gradual full coverage (6 months for all tickers)
    """
    
    def __init__(self):
        """Initialize deactivation detector job."""
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.total_deactivated: int = 0
        self.total_checked: int = 0
    
    async def run(
        self,
        batch_size: int = 500,
        test_mode: bool = False
    ) -> Dict:
        """
        Execute deactivation detection for a batch of tickers.
        
        Args:
            batch_size: Number of tickers to check (default 500)
            test_mode: If True, check only 10 tickers for testing
            
        Returns:
            Statistics dictionary with detection results
        """
        if self.is_running:
            logger.warning("Deactivation detection job already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            if test_mode:
                batch_size = 10
            
            logger.info(
                "Starting deactivation detection",
                extra={"batch_size": batch_size, "test_mode": test_mode}
            )
            
            # Get MASSIVE provider
            provider = provider_registry.get_provider_by_name("MassiveProvider")
            
            if not provider:
                logger.error("MASSIVE provider not available")
                return {
                    "status": "error",
                    "message": "MASSIVE provider not available"
                }
            
            # Query tickers to check
            # Priority: tickers without recent active check, exclude already failed
            tickers_to_check = await CompanyOverview.find(
                {
                    "enrichment_status": {"$ne": "failed"},
                    "$or": [
                        {"extended_data.last_active_check": {"$exists": False}},
                        {"extended_data.last_active_check": {"$lt": (datetime.utcnow() - timedelta(days=30)).isoformat()}}
                    ]
                }
            ).limit(batch_size).to_list()
            
            if not tickers_to_check:
                logger.info("No tickers need deactivation check")
                return {
                    "status": "success",
                    "tickers_checked": 0,
                    "message": "No tickers require checking"
                }
            
            logger.info(
                f"Checking {len(tickers_to_check)} tickers for deactivation",
                extra={"ticker_count": len(tickers_to_check)}
            )
            
            # Check tickers with rate limiting
            # Can't do concurrent due to rate limits, must be sequential
            results = []
            for i, ticker_doc in enumerate(tickers_to_check, 1):
                result = await check_and_mark_if_inactive(provider, ticker_doc)
                results.append(result)
                
                if i % 50 == 0:
                    logger.info(
                        f"Progress: {i}/{len(tickers_to_check)} tickers checked",
                        extra={"checked": i, "total": len(tickers_to_check)}
                    )
                
                # Rate limit: 5 calls/min = 12 seconds between calls
                if i < len(tickers_to_check):  # Don't wait after last ticker
                    await asyncio.sleep(12)
            
            # Count results
            active_count = sum(1 for r in results if r["status"] == "active")
            inactive_count = sum(1 for r in results if r["status"] == "inactive")
            check_failed_count = sum(1 for r in results if r["status"] == "check_failed")
            marked_count = sum(1 for r in results if r["action"] == "marked_as_failed")
            
            # Update job state
            self.last_run = datetime.utcnow()
            self.total_checked += len(results)
            self.total_deactivated += marked_count
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "tickers_checked": len(results),
                "active_tickers": active_count,
                "inactive_tickers": inactive_count,
                "marked_as_failed": marked_count,
                "check_failures": check_failed_count,
                "elapsed_seconds": round(elapsed_time, 2),
                "elapsed_minutes": round(elapsed_time / 60, 2),
                "total_checked_all_time": self.total_checked,
                "total_deactivated_all_time": self.total_deactivated
            }
            
            logger.info(
                "Deactivation detection complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Deactivation detection failed",
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
            "total_tickers_checked": self.total_checked,
            "total_tickers_deactivated": self.total_deactivated
        }


# Singleton instance
massive_deactivation_detector = MassiveDeactivationDetectorJob()
