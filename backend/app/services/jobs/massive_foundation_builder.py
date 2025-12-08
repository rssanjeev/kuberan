"""
MASSIVE Foundation Builder - Bulk stock metadata collection via Polygon.io.

Purpose: Collect foundational metadata for all tickers at scale using MASSIVE provider.

Strategy:
- Rate limit: 5 calls/min = 300 calls/hour = 7,200 calls/day
- Schedule: Every 1 minute
- Batch size: 10 tickers per job with 12-second delays
- Delays: 12 seconds between calls = 5 calls/minute (full rate utilization)

Architecture: Hybrid functional/OOP
- Pure functions for core logic (testable)
- Job class for state and scheduling
"""

from datetime import datetime
from typing import List, Optional
import time
import re
import asyncio

from app.core.logging_config import get_logger
from app.services.stock.metadata_enrichment_service import metadata_enrichment_service
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Ticker Validation
# ============================================================================

def is_valid_ticker_format(ticker: str) -> bool:
    """
    Validate ticker format to avoid API errors.
    
    Invalid formats:
    - Warrants: ticker-WS, ticker-WT (e.g., ZEV-WS, AEON-WS)
    - Preferred stocks: ticker-P-X (e.g., APO-P-A, WRB-P-H)
    - Dual-class stocks: ticker-A, ticker-B (e.g., AKO-A, WSO-B, AGM-A)
    - Test tickers: ATEST-X
    - ANY tickers with hyphens (not supported by Polygon.io API)
    
    Valid format: 1-5 uppercase letters, optional single dot only
    Examples: AAPL, MSFT, GOOGL, BRK.A (dot is acceptable)
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid format, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Reject ANY ticker with hyphen (Polygon.io doesn't support them)
    if '-' in ticker:
        return False
    
    # Valid: 1-5 characters, uppercase letters, optional single dot
    # Examples: AAPL, MSFT, BRK.A, BRK.B, GOOGL, META
    # Dot is allowed for dual-class stocks (BRK.A, BRK.B)
    if re.match(r'^[A-Z]{1,5}(\\.?[A-Z])?$', ticker):
        return True
    
    return False


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
                    "sources": saved.metadata_sources if hasattr(saved, 'metadata_sources') else [],
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


async def get_tickers_needing_foundation(limit: int = 10) -> List[str]:
    """
    Get tickers that need foundation metadata collection.
    
    Targets tickers with enrichment_status == "base" (basic data only).
    These need upgrading to "foundation" via MASSIVE (Polygon.io).
    
    Excludes tickers with enrichment_status == "failed" (not found, delisted, etc.)
    
    Args:
        limit: Maximum number of tickers to return (default 10 for per-minute jobs)
        
    Returns:
        List of ticker symbols
    """
    try:
        # Get tickers at "base" level (need foundation upgrade)
        # Exclude "failed" tickers (404, delisted, etc.)
        # Sort by market_cap descending to prioritize large-cap stocks (S&P 500)
        # Tickers without market_cap will be sorted last (nulls last behavior)
        pending_docs = await CompanyOverview.find(
            {"enrichment_status": "base"}
        ).sort([("market_cap", -1)]).limit(limit * 2).to_list()  # Fetch extra to account for filtering
        
        # Extract ticker symbols and filter invalid formats
        all_tickers = [doc.ticker for doc in pending_docs]
        valid_tickers = [t for t in all_tickers if is_valid_ticker_format(t)]
        invalid_tickers = [t for t in all_tickers if not is_valid_ticker_format(t)]
        
        # Mark invalid tickers as failed immediately (skip API calls)
        if invalid_tickers:
            for ticker in invalid_tickers:
                await CompanyOverview.find_one(
                    {"ticker": ticker}
                ).update({"$set": {"enrichment_status": "failed"}})
            
            logger.warning(
                "Skipped invalid ticker formats",
                extra={
                    "invalid_count": len(invalid_tickers),
                    "examples": invalid_tickers[:5],
                    "reason": "Warrants/preferred stocks with hyphens not supported by API"
                }
            )
        
        # Use only valid tickers, limit to requested batch size
        pending_tickers = valid_tickers[:limit]
        
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
    batch_size: int = 10
) -> dict:
    """
    Collect foundation metadata for a batch of tickers.
    
    Rate limiting:
    - 5 calls/min limit from Polygon.io
    - Process 10 tickers per execution with 12-second delays
    - 12 seconds × 10 tickers = 120 seconds = 5 calls/minute average
    
    Args:
        tickers: List of ticker symbols
        batch_size: Maximum tickers per batch (default 10 for optimized rate usage)
        
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
            
            # Rate limiting: 12-second delay between calls = 5 calls/minute
            # 10 tickers × 12 seconds = 120 seconds = 2 minutes total
            # This uses full rate capacity efficiently
            if idx < len(tickers[:batch_size]):
                await asyncio.sleep(12)
            
            # Progress logging every 5 tickers
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
            tickers = await get_tickers_needing_foundation(limit=10)
            
            if not tickers:
                logger.info("No tickers need foundation metadata - all up to date")
                return
            
            # Collect foundation metadata batch
            stats = await collect_foundation_batch(tickers, batch_size=10)
            
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
