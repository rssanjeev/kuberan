"""
MASSIVE Foundation Builder - Bulk stock metadata collection via Polygon.io.

Purpose: Collect foundational metadata for all tickers at scale using MASSIVE provider.

Strategy:
- Rate limit: 5 calls/min = 300 calls/hour = 7,200 calls/day
- Schedule: Every minute for continuous collection
- Batch size: 5 tickers per job (matches rate limit exactly)
- Target: Complete ~10,000 NYSE/NASDAQ tickers in ~33 hours

Architecture: Hybrid functional/OOP
- Pure functions for core logic (testable)
- Job class for state and scheduling
"""

from datetime import datetime
from typing import List, Optional
import time

from app.core.logging_config import get_logger
from app.services.stock.metadata_enrichment_service import metadata_enrichment_service
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions
# ============================================================================

async def collect_foundation_for_ticker(ticker: str) -> bool:
    """
    Collect foundation metadata for a single ticker via MASSIVE provider.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Collect foundation metadata via MASSIVE (Polygon.io)
        metadata = await metadata_enrichment_service.collect_foundation_metadata(ticker)
        
        if not metadata:
            logger.warning(
                "No foundation metadata collected",
                extra={"ticker": ticker, "provider": "MASSIVE"}
            )
            return False
        
        # Save to database
        saved = await metadata_enrichment_service.save_metadata(metadata)
        
        if saved:
            logger.info(
                "Saved foundation metadata via MASSIVE",
                extra={
                    "ticker": ticker,
                    "enrichment_status": saved.enrichment_status,
                    "source": saved.data_source,
                    "has_cik": bool(saved.cik),
                    "has_figi": bool(saved.composite_figi)
                }
            )
            return True
        
        return False
    
    except Exception as e:
        logger.error(
            "Failed to collect foundation metadata",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return False


async def get_tickers_needing_foundation(limit: int = 5) -> List[str]:
    """
    Get tickers that need foundation metadata collection.
    
    Targets tickers with enrichment_status == "base" (basic data only).
    These need upgrading to "foundation" via MASSIVE (Polygon.io).
    
    Excludes tickers with enrichment_status == "failed" (not found, delisted, etc.)
    
    Args:
        limit: Maximum number of tickers to return (default 5 for per-minute jobs)
        
    Returns:
        List of ticker symbols
    """
    try:
        # Get tickers at "base" level (need foundation upgrade)
        # Exclude "failed" tickers (404, delisted, etc.)
        # Fetch full documents to avoid Beanie projection issues
        pending_docs = await CompanyOverview.find(
            {"enrichment_status": "base"}
        ).limit(limit).to_list()
        
        # Extract ticker symbols from documents
        pending_tickers = [doc.ticker for doc in pending_docs]
        
        # Get counts for logging
        base_count = len(pending_tickers)
        foundation_count = await CompanyOverview.find(
            {"enrichment_status": "foundation"}
        ).count()
        failed_count = await CompanyOverview.find(
            {"enrichment_status": "failed"}
        ).count()
        total_count = await CompanyOverview.find().count()
        
        logger.info(
            "Foundation collection candidates identified",
            extra={
                "total_tickers": total_count,
                "needs_foundation": base_count,
                "already_foundation": foundation_count,
                "failed_tickers": failed_count,
                "batch_size": min(limit, base_count)
            }
        )
        
        return pending_tickers
    
    except Exception as e:
        logger.error(
            "Failed to get tickers needing foundation",
            extra={"error": str(e)},
            exc_info=True
        )
        return []


async def collect_foundation_batch(
    tickers: List[str],
    batch_size: int = 5
) -> dict:
    """
    Collect foundation metadata for a batch of tickers.
    
    Rate limiting:
    - 5 calls/min limit from Polygon.io
    - Process 5 tickers per minute (matches rate limit exactly)
    - Job runs every minute via scheduler, providing natural pacing
    
    Args:
        tickers: List of ticker symbols
        batch_size: Maximum tickers per batch (default 5 for per-minute execution)
        
    Returns:
        Statistics dictionary
    """
    stats = {
        "total": len(tickers),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "start_time": datetime.now()
    }
    
    logger.info(
        "Starting foundation metadata batch collection",
        extra={
            "batch_size": len(tickers),
            "provider": "MASSIVE",
            "estimated_duration_min": len(tickers) / 5  # 5 calls/min
        }
    )
    
    for idx, ticker in enumerate(tickers[:batch_size], 1):
        try:
            # Collect and save
            success = await collect_foundation_for_ticker(ticker)
            
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            # No artificial delays needed - per-minute scheduling provides natural rate limiting
            # Job processes 5 tickers immediately, exits, then APScheduler waits until next minute
            
            # Progress logging every 5 tickers (logs at end of each batch)
            if idx % 5 == 0:
                elapsed = (datetime.now() - stats["start_time"]).total_seconds() / 60
                logger.info(
                    "Foundation collection progress",
                    extra={
                        "completed": idx,
                        "total": len(tickers),
                        "success": stats["success"],
                        "failed": stats["failed"],
                        "elapsed_min": round(elapsed, 1)
                    }
                )
        
        except Exception as e:
            logger.error(
                "Batch collection error",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            stats["failed"] += 1
    
    stats["end_time"] = datetime.now()
    stats["duration_min"] = (stats["end_time"] - stats["start_time"]).total_seconds() / 60
    
    return stats


# ============================================================================
# Job Class: State Management + Scheduling
# ============================================================================

class MassiveFoundationBuilderJob:
    """
    Job class for MASSIVE foundation metadata collection.
    
    Manages:
    - Run statistics
    - Last execution time
    - Success/failure tracking
    """
    
    def __init__(self):
        """Initialize job with clean state."""
        self.last_run: Optional[datetime] = None
        self.run_count: int = 0
        self.total_success: int = 0
        self.total_failed: int = 0
    
    async def run(self) -> None:
        """
        Execute foundation metadata collection job.
        
        Process:
        1. Get tickers needing foundation metadata (limit 300)
        2. Collect via MASSIVE provider (5 calls/min)
        3. Save with enrichment_status='foundation'
        4. Update job statistics
        """
        start_time = datetime.now()
        
        logger.info(
            "MASSIVE foundation builder job started",
            extra={
                "run_count": self.run_count + 1,
                "last_run": self.last_run.isoformat() if self.last_run else None
            }
        )
        
        try:
            # Get tickers needing foundation metadata
            tickers = await get_tickers_needing_foundation(limit=300)
            
            if not tickers:
                logger.info("No tickers need foundation metadata - all up to date")
                return
            
            # Collect foundation metadata batch
            stats = await collect_foundation_batch(tickers, batch_size=300)
            
            # Update job statistics
            self.run_count += 1
            self.last_run = datetime.now()
            self.total_success += stats["success"]
            self.total_failed += stats["failed"]
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                "MASSIVE foundation builder job completed",
                extra={
                    "run_count": self.run_count,
                    "batch_success": stats["success"],
                    "batch_failed": stats["failed"],
                    "total_success": self.total_success,
                    "total_failed": self.total_failed,
                    "duration_sec": round(duration, 1),
                    "tickers_per_sec": round(stats["total"] / duration, 2) if duration > 0 else 0
                }
            )
        
        except Exception as e:
            logger.error(
                "MASSIVE foundation builder job failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise


# ============================================================================
# Singleton Instance
# ============================================================================

massive_foundation_builder_job = MassiveFoundationBuilderJob()
