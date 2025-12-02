"""
MASSIVE Bi-Annual Refresh Job - Failsafe ticker re-scan.

Re-runs full ticker discovery every 6 months to catch any tickers missed by
incremental delta extraction. Acts as a failsafe to ensure database completeness.

Process:
1. Checks last_run date (should be 6 months ago)
2. Calls existing massive_ticker_discovery job to re-scan all tickers
3. Delta extractor will catch any new tickers incrementally between refreshes
4. This ensures nothing falls through the cracks

Schedule: Bi-annual (January 1 and July 1, 4 AM EST)

Timeline:
- Full discovery: ~2.5 minutes for 12,000+ tickers
- Minimal API usage: 12-15 API calls total (1,000 tickers per call)

SECURITY: No sensitive data stored, only public ticker information.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

from app.core.logging_config import get_logger
from app.services.jobs.massive_ticker_discovery import massive_ticker_discovery

logger = get_logger(__name__)


# ============================================================================
# Job Class: Bi-Annual Refresh Orchestration
# ============================================================================

class MassiveBiannualRefreshJob:
    """
    Bi-annual failsafe job to re-scan all tickers.
    
    Strategy:
    - Runs twice per year (January 1 and July 1)
    - Calls existing bulk discovery job (massive_ticker_discovery)
    - Ensures database has complete ticker coverage
    - Catches any tickers missed by incremental delta extraction
    
    Benefits:
    - Failsafe against data gaps
    - Minimal API usage (~15 calls, 2.5 minutes)
    - Leverages existing proven infrastructure
    - Simple and reliable
    
    Why Bi-Annual:
    - Delta extractor handles weekly IPO detection
    - Full refresh provides safety net
    - 6-month interval balances coverage vs API usage
    - Historical data: typically 50-100 IPOs per 6 months
    """
    
    def __init__(self):
        """Initialize bi-annual refresh job."""
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.total_runs: int = 0
        self.last_tickers_discovered: int = 0
    
    async def should_run(self) -> bool:
        """
        Check if refresh should run (6 months since last run).
        
        Returns:
            True if 6 months have passed, False otherwise
        """
        if not self.last_run:
            # First run - always proceed
            return True
        
        elapsed = datetime.utcnow() - self.last_run
        six_months = timedelta(days=182)  # ~6 months
        
        if elapsed >= six_months:
            logger.info(
                "Bi-annual refresh interval reached",
                extra={
                    "last_run": self.last_run.isoformat(),
                    "elapsed_days": elapsed.days
                }
            )
            return True
        
        logger.info(
            "Bi-annual refresh not needed yet",
            extra={
                "last_run": self.last_run.isoformat(),
                "elapsed_days": elapsed.days,
                "days_until_next": (six_months - elapsed).days
            }
        )
        return False
    
    async def run(self, force: bool = False) -> Dict:
        """
        Execute bi-annual ticker refresh.
        
        Args:
            force: If True, skip 6-month check and run immediately
            
        Returns:
            Statistics dictionary with refresh results
        """
        if self.is_running:
            logger.warning("Bi-annual refresh job already running")
            return {"status": "error", "message": "Job already running"}
        
        # Check if refresh is needed
        if not force and not await self.should_run():
            return {
                "status": "skipped",
                "message": "Bi-annual interval not reached",
                "last_run": self.last_run.isoformat() if self.last_run else None
            }
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info(
                "Starting bi-annual ticker refresh",
                extra={"forced": force}
            )
            
            # Call existing bulk discovery job
            discovery_result = await massive_ticker_discovery.run()
            
            if discovery_result.get("status") != "success":
                logger.error(
                    "Bi-annual refresh failed - discovery job error",
                    extra={"discovery_result": discovery_result}
                )
                return {
                    "status": "error",
                    "message": "Bulk discovery failed",
                    "discovery_result": discovery_result
                }
            
            # Update job state
            self.last_run = datetime.utcnow()
            self.total_runs += 1
            self.last_tickers_discovered = discovery_result.get("total_tickers", 0)
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "tickers_discovered": discovery_result.get("total_tickers", 0),
                "new_tickers_added": discovery_result.get("new_tickers", 0),
                "already_existed": discovery_result.get("already_existed", 0),
                "batches_processed": discovery_result.get("batches_processed", 0),
                "elapsed_seconds": round(elapsed_time, 2),
                "elapsed_minutes": round(elapsed_time / 60, 2),
                "total_runs_all_time": self.total_runs,
                "last_run": self.last_run.isoformat(),
                "next_run_due": (self.last_run + timedelta(days=182)).isoformat()
            }
            
            logger.info(
                "Bi-annual refresh complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Bi-annual refresh failed",
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
        next_run = None
        if self.last_run:
            next_run = (self.last_run + timedelta(days=182)).isoformat()
        
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run_due": next_run,
            "total_runs": self.total_runs,
            "last_tickers_discovered": self.last_tickers_discovered
        }


# Singleton instance
massive_biannual_refresh = MassiveBiannualRefreshJob()
