"""
Metadata Collector Job - Automated stock metadata collection and enrichment.

Two modes:
1. One-off discovery: Initial bulk collection (manual trigger)
2. Enrichment cycle: Ongoing Alpha Vantage enhancement (scheduled)

Hybrid approach: Class for state management + pure functions for core logic.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import time

from app.core.logging_config import get_logger
from app.core.ticker_discovery import ticker_discovery
from app.services.stock.metadata_enrichment_service import metadata_enrichment_service
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions (Easy to test, reusable)
# ============================================================================

async def collect_and_save_metadata(ticker: str) -> bool:
    """
    Collect base metadata for a single ticker and save to database.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Stage 1: Collect base metadata from YFinance
        metadata = await metadata_enrichment_service.collect_base_metadata(ticker)
        
        if not metadata:
            logger.warning(f"No metadata collected for {ticker}", extra={"ticker": ticker})
            return False
        
        # Save to database
        saved = await metadata_enrichment_service.save_metadata(metadata)
        
        if saved:
            logger.info(
                f"Saved metadata for {ticker}",
                extra={
                    "ticker": ticker,
                    "asset_type": saved.asset_type,
                    "enrichment_status": saved.enrichment_status
                }
            )
            return True
        
        return False
    
    except Exception as e:
        logger.error(
            f"Failed to collect metadata for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return False


async def enrich_and_save_metadata(ticker: str) -> bool:
    """
    Enrich existing metadata with Alpha Vantage and save.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get existing metadata
        existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
        
        # Stage 2: Enrich with Alpha Vantage
        enriched = await metadata_enrichment_service.enrich_with_alpha_vantage(
            ticker=ticker,
            existing_metadata=existing
        )
        
        if not enriched:
            logger.warning(f"No enrichment data for {ticker}", extra={"ticker": ticker})
            # Mark as failed enrichment
            if existing:
                existing.enrichment_status = "failed"
                existing.enriched_at = datetime.utcnow()
                await existing.save()
            return False
        
        # Save enriched metadata
        saved = await metadata_enrichment_service.save_metadata(enriched)
        
        if saved:
            logger.info(
                f"Enriched metadata for {ticker}",
                extra={
                    "ticker": ticker,
                    "enrichment_status": saved.enrichment_status,
                    "has_pe_ratio": saved.pe_ratio is not None
                }
            )
            return True
        
        return False
    
    except Exception as e:
        logger.error(
            f"Failed to enrich metadata for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return False


async def collect_batch(tickers: List[str], batch_size: int = 100, delay: float = 0.5) -> Dict[str, int]:
    """
    Collect base metadata for a batch of tickers.
    
    Args:
        tickers: List of ticker symbols
        batch_size: Number of tickers to process before delay
        delay: Delay in seconds between batches
        
    Returns:
        Statistics dictionary with success/failure counts
    """
    success_count = 0
    failure_count = 0
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        
        logger.info(
            f"Processing batch {i // batch_size + 1}",
            extra={
                "batch_start": i,
                "batch_size": len(batch),
                "total_tickers": len(tickers)
            }
        )
        
        # Process batch concurrently
        tasks = [collect_and_save_metadata(ticker) for ticker in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        for result in results:
            if isinstance(result, bool) and result:
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(
            f"Batch complete",
            extra={
                "batch_number": i // batch_size + 1,
                "success": success_count,
                "failure": failure_count
            }
        )
        
        # Delay between batches (respect API courtesy limits)
        if i + batch_size < len(tickers):
            await asyncio.sleep(delay)
    
    return {
        "success": success_count,
        "failure": failure_count,
        "total": len(tickers)
    }


# ============================================================================
# Job Class: State Management and Scheduling
# ============================================================================

class MetadataCollectorJob:
    """
    Background job for stock metadata collection and enrichment.
    
    Modes:
    1. One-off discovery: Initial universe discovery (manual trigger)
    2. Enrichment cycle: Alpha Vantage enhancement (daily scheduled)
    """
    
    def __init__(self):
        """Initialize metadata collector job."""
        self.is_running = False
        self.last_discovery_run: Optional[datetime] = None
        self.last_enrichment_run: Optional[datetime] = None
        self.discovery_count: int = 0
        self.enrichment_count: int = 0
        
        # Configuration
        self.ENRICHMENT_BATCH_SIZE = 5  # Process 5 tickers per cycle (free tier limit)
        self.DISCOVERY_BATCH_SIZE = 100  # YFinance has no limits
    
    async def run_one_off_discovery(
        self,
        limit: Optional[int] = None,
        test_mode: bool = False
    ) -> Dict:
        """
        One-time execution: Discover and collect base metadata for all tickers.
        
        Process:
        1. Fetch all tickers from Alpha Vantage LISTING_STATUS
        2. Collect base metadata from YFinance (batch processing)
        3. Queue high-priority tickers for enrichment
        
        Args:
            limit: Limit number of tickers (for testing)
            test_mode: If True, only process first 20 tickers
            
        Returns:
            Statistics dictionary with results
        """
        if self.is_running:
            logger.warning("Discovery job already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info("Starting one-off metadata discovery")
            
            # Step 1: Discover all tickers from Alpha Vantage
            logger.info("Fetching ticker list from Alpha Vantage")
            all_tickers = await ticker_discovery.discover_all_tickers(status="active")
            
            if not all_tickers:
                logger.error("No tickers discovered")
                return {
                    "status": "error",
                    "message": "Failed to discover tickers"
                }
            
            # Get statistics
            stats = ticker_discovery.get_ticker_statistics(all_tickers)
            logger.info(
                "Ticker discovery complete",
                extra={
                    "total_tickers": stats["total"],
                    "asset_types": stats["by_asset_type"],
                    "exchanges": stats["by_exchange"]
                }
            )
            
            # Step 2: Prepare ticker list
            ticker_symbols = [t["symbol"] for t in all_tickers]
            
            # Apply limit for testing
            if test_mode:
                ticker_symbols = ticker_symbols[:20]
                logger.info("Test mode: limiting to 20 tickers")
            elif limit:
                ticker_symbols = ticker_symbols[:limit]
                logger.info(f"Limiting to {limit} tickers")
            
            # Step 3: Collect base metadata from YFinance (bulk)
            logger.info(
                f"Starting bulk metadata collection",
                extra={"ticker_count": len(ticker_symbols)}
            )
            
            collection_stats = await collect_batch(
                tickers=ticker_symbols,
                batch_size=self.DISCOVERY_BATCH_SIZE,
                delay=0.5
            )
            
            # Step 4: Identify high-priority tickers for enrichment
            logger.info("Identifying high-priority tickers for enrichment")
            priority_count = await self._queue_priority_enrichment()
            
            # Update job state
            self.last_discovery_run = datetime.utcnow()
            self.discovery_count += collection_stats["success"]
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "discovered_tickers": stats["total"],
                "processed_tickers": len(ticker_symbols),
                "collection_stats": collection_stats,
                "priority_enrichment_queued": priority_count,
                "elapsed_seconds": round(elapsed_time, 2),
                "asset_type_breakdown": stats["by_asset_type"]
            }
            
            logger.info(
                "One-off discovery complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "One-off discovery failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": str(e)
            }
        
        finally:
            self.is_running = False
    
    async def run_enrichment_cycle(self) -> Dict:
        """
        Scheduled execution: Enrich metadata with Alpha Vantage.
        
        Process:
        1. Find tickers needing enrichment (enrichment_status == "base")
        2. Prioritize: ETFs > Large cap > Mid cap > Small cap
        3. Process batch (5 tickers for free tier, respects rate limits)
        4. Update enrichment_status to "enriched"
        
        Returns:
            Statistics dictionary with results
        """
        if self.is_running:
            logger.warning("Enrichment cycle already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info("Starting enrichment cycle")
            
            # Find tickers needing enrichment (prioritized)
            tickers_to_enrich = await self._get_enrichment_queue(limit=self.ENRICHMENT_BATCH_SIZE)
            
            if not tickers_to_enrich:
                logger.info("No tickers need enrichment")
                return {
                    "status": "success",
                    "message": "No tickers need enrichment",
                    "processed": 0
                }
            
            logger.info(
                f"Processing {len(tickers_to_enrich)} tickers for enrichment",
                extra={"count": len(tickers_to_enrich)}
            )
            
            # Enrich tickers (sequential to respect rate limits)
            success_count = 0
            failure_count = 0
            
            for ticker in tickers_to_enrich:
                success = await enrich_and_save_metadata(ticker)
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                # Delay between requests (respect Alpha Vantage rate limits)
                await asyncio.sleep(12)  # 5 requests per minute = 12 seconds between
            
            # Update job state
            self.last_enrichment_run = datetime.utcnow()
            self.enrichment_count += success_count
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "processed": len(tickers_to_enrich),
                "success": success_count,
                "failure": failure_count,
                "elapsed_seconds": round(elapsed_time, 2)
            }
            
            logger.info(
                "Enrichment cycle complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Enrichment cycle failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": str(e)
            }
        
        finally:
            self.is_running = False
    
    async def _queue_priority_enrichment(self) -> int:
        """
        Identify and mark high-priority tickers for enrichment.
        
        Priority:
        1. All ETFs
        2. Large cap stocks (market_cap > $10B)
        
        Returns:
            Number of tickers queued
        """
        try:
            # Find all ETFs with base metadata
            etfs = await CompanyOverview.find(
                CompanyOverview.asset_type == "ETF",
                CompanyOverview.enrichment_status == "base"
            ).to_list()
            
            # Find large cap stocks with base metadata
            large_caps = await CompanyOverview.find(
                CompanyOverview.asset_type == "Stock",
                CompanyOverview.enrichment_status == "base",
                CompanyOverview.market_cap > 10_000_000_000
            ).to_list()
            
            priority_count = len(etfs) + len(large_caps)
            
            logger.info(
                "Priority enrichment queue identified",
                extra={
                    "etfs": len(etfs),
                    "large_caps": len(large_caps),
                    "total": priority_count
                }
            )
            
            return priority_count
        
        except Exception as e:
            logger.error(
                "Failed to queue priority enrichment",
                extra={"error": str(e)},
                exc_info=True
            )
            return 0
    
    async def _get_enrichment_queue(self, limit: int = 5) -> List[str]:
        """
        Get prioritized list of tickers needing enrichment.
        
        Priority order:
        1. ETFs with base metadata
        2. Large cap stocks (market_cap > $10B)
        3. Mid cap stocks (market_cap $2B-$10B)
        4. Small cap stocks
        
        Args:
            limit: Maximum number of tickers to return
            
        Returns:
            List of ticker symbols
        """
        tickers = []
        
        try:
            # Priority 1: ETFs
            if len(tickers) < limit:
                etfs = await CompanyOverview.find(
                    CompanyOverview.asset_type == "ETF",
                    CompanyOverview.enrichment_status == "base"
                ).limit(limit - len(tickers)).to_list()
                tickers.extend([etf.ticker for etf in etfs])
            
            # Priority 2: Large cap stocks
            if len(tickers) < limit:
                large_caps = await CompanyOverview.find(
                    CompanyOverview.asset_type == "Stock",
                    CompanyOverview.enrichment_status == "base",
                    CompanyOverview.market_cap > 10_000_000_000
                ).limit(limit - len(tickers)).to_list()
                tickers.extend([stock.ticker for stock in large_caps])
            
            # Priority 3: Mid cap stocks
            if len(tickers) < limit:
                mid_caps = await CompanyOverview.find(
                    CompanyOverview.asset_type == "Stock",
                    CompanyOverview.enrichment_status == "base",
                    CompanyOverview.market_cap > 2_000_000_000,
                    CompanyOverview.market_cap <= 10_000_000_000
                ).limit(limit - len(tickers)).to_list()
                tickers.extend([stock.ticker for stock in mid_caps])
            
            # Priority 4: Any remaining with base status
            if len(tickers) < limit:
                remaining = await CompanyOverview.find(
                    CompanyOverview.enrichment_status == "base"
                ).limit(limit - len(tickers)).to_list()
                tickers.extend([doc.ticker for doc in remaining])
            
            logger.info(
                "Enrichment queue retrieved",
                extra={"ticker_count": len(tickers)}
            )
            
            return tickers
        
        except Exception as e:
            logger.error(
                "Failed to get enrichment queue",
                extra={"error": str(e)},
                exc_info=True
            )
            return []
    
    async def run_incremental_batch_collection(self) -> Dict:
        """
        Incremental batch collection: Process 30 tickers per run.
        
        Strategy:
        - 30 tickers per batch
        - 1 hour gap between batches (10 batches/day)
        - Process by decreasing market cap order
        - Failed tickers moved to next day
        
        Process:
        1. Discover all tickers (if not in database)
        2. Get next batch of 30 tickers (ordered by market cap desc)
        3. Collect base metadata from YFinance
        4. Track failures for retry
        
        Returns:
            Statistics dictionary with results
        """
        if self.is_running:
            logger.warning("Incremental batch collection already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info("Starting incremental batch collection")
            
            # Step 1: Get next batch of tickers to process
            tickers_to_process = await self._get_next_collection_batch(batch_size=30)
            
            if not tickers_to_process:
                logger.info("No tickers need collection")
                return {
                    "status": "success",
                    "message": "No tickers need collection",
                    "processed": 0
                }
            
            logger.info(
                f"Processing batch of {len(tickers_to_process)} tickers",
                extra={"ticker_count": len(tickers_to_process)}
            )
            
            # Step 2: Process tickers concurrently within batch
            success_count = 0
            failure_count = 0
            
            tasks = [self._collect_with_tracking(ticker) for ticker in tickers_to_process]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes
            for result in results:
                if isinstance(result, bool) and result:
                    success_count += 1
                else:
                    failure_count += 1
            
            # Update job state
            self.discovery_count += success_count
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status": "success",
                "processed": len(tickers_to_process),
                "success": success_count,
                "failure": failure_count,
                "elapsed_seconds": round(elapsed_time, 2)
            }
            
            logger.info(
                "Incremental batch collection complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Incremental batch collection failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": str(e)
            }
        
        finally:
            self.is_running = False
    
    async def _get_next_collection_batch(self, batch_size: int = 30) -> List[str]:
        """
        Get next batch of tickers for collection, ordered by market cap (desc).
        
        Priority:
        1. Tickers not yet in database (from Alpha Vantage discovery)
        2. Failed tickers needing retry (ordered by batch_priority/market_cap)
        
        Args:
            batch_size: Number of tickers to return
            
        Returns:
            List of ticker symbols ordered by priority
        """
        tickers = []
        
        try:
            # Step 1: Check if we need to discover tickers first
            existing_count = await CompanyOverview.count()
            
            if existing_count == 0:
                logger.info("No tickers in database, running initial discovery")
                # Discover all tickers from Alpha Vantage
                all_tickers = await ticker_discovery.discover_all_tickers(status="active")
                
                if not all_tickers:
                    logger.error("Failed to discover tickers")
                    return []
                
                # Sort by market cap (largest first) - estimate based on exchange priority
                # NYSE/NASDAQ tickers are typically larger
                priority_tickers = sorted(
                    all_tickers,
                    key=lambda t: (
                        t.get("exchange") in ["NYSE", "NASDAQ", "AMEX"],
                        t.get("symbol")
                    ),
                    reverse=True
                )
                
                # Return first batch
                return [t["symbol"] for t in priority_tickers[:batch_size]]
            
            # Step 2: Get existing tickers that need collection/retry
            # Find tickers with failed collection attempts (oldest first)
            # Max 3 retry attempts before giving up (< 3 means attempts 1 and 2 only)
            failed_tickers = await CompanyOverview.find(
                CompanyOverview.enrichment_status == "base",
                CompanyOverview.collection_attempts > 0,
                CompanyOverview.collection_attempts < 3  # Retry only attempts 1 and 2
            ).sort([
                ("batch_priority", -1),  # Higher market cap first
                ("last_collection_attempt", 1)  # Oldest attempts first
            ]).limit(batch_size).to_list()
            
            if failed_tickers:
                logger.info(
                    f"Found {len(failed_tickers)} failed tickers for retry",
                    extra={"count": len(failed_tickers)}
                )
                return [ticker.ticker for ticker in failed_tickers]
            
            # Step 3: Get new tickers from discovery that haven't been added yet
            logger.info("Checking for new tickers from Alpha Vantage")
            all_tickers = await ticker_discovery.discover_all_tickers(status="active")
            
            if not all_tickers:
                logger.warning("No new tickers discovered")
                return []
            
            # Get existing ticker symbols
            existing_tickers = await CompanyOverview.distinct("ticker")
            existing_set = set(existing_tickers)
            
            # Find tickers not in database
            new_tickers = [t for t in all_tickers if t["symbol"] not in existing_set]
            
            if not new_tickers:
                logger.info("All discovered tickers are already in database")
                return []
            
            logger.info(
                f"Found {len(new_tickers)} new tickers",
                extra={"count": len(new_tickers)}
            )
            
            # Sort by exchange priority (NYSE/NASDAQ first)
            priority_tickers = sorted(
                new_tickers,
                key=lambda t: (
                    t.get("exchange") in ["NYSE", "NASDAQ", "AMEX"],
                    t.get("symbol")
                ),
                reverse=True
            )
            
            return [t["symbol"] for t in priority_tickers[:batch_size]]
        
        except Exception as e:
            logger.error(
                "Failed to get next collection batch",
                extra={"error": str(e)},
                exc_info=True
            )
            return []
    
    async def _collect_with_tracking(self, ticker: str) -> bool:
        """
        Collect metadata with tracking for retry logic.
        
        Tracks:
        - collection_attempts: Incremented on each attempt
        - last_collection_attempt: Timestamp of attempt
        - batch_priority: Market cap for ordering
        - collection_error: Error message if failed
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Collect base metadata from YFinance
            metadata = await metadata_enrichment_service.collect_base_metadata(ticker)
            
            if not metadata:
                logger.warning(f"No metadata collected for {ticker}", extra={"ticker": ticker})
                # Update tracking for failed attempt
                await self._update_collection_tracking(
                    ticker=ticker,
                    success=False,
                    error="No metadata returned from YFinance"
                )
                return False
            
            # Set batch priority (market cap for ordering)
            if metadata.get("market_cap"):
                metadata["batch_priority"] = metadata["market_cap"]
            
            # Save to database
            saved = await metadata_enrichment_service.save_metadata(metadata)
            
            if saved:
                logger.info(
                    f"Saved metadata for {ticker}",
                    extra={
                        "ticker": ticker,
                        "asset_type": saved.asset_type,
                        "market_cap": saved.market_cap
                    }
                )
                # Update tracking for successful collection
                await self._update_collection_tracking(
                    ticker=ticker,
                    success=True,
                    market_cap=saved.market_cap
                )
                return True
            
            return False
        
        except Exception as e:
            logger.error(
                f"Failed to collect metadata for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            # Update tracking for failed attempt
            await self._update_collection_tracking(
                ticker=ticker,
                success=False,
                error=str(e)
            )
            return False
    
    async def _update_collection_tracking(
        self,
        ticker: str,
        success: bool,
        market_cap: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        Update collection tracking fields for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            success: Whether collection was successful
            market_cap: Market cap for priority ordering
            error: Error message if failed
        """
        try:
            # Get or create ticker document
            doc = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
            
            if not doc:
                # Create minimal document for tracking
                doc = CompanyOverview(
                    ticker=ticker,
                    source_provider="YFINANCE",
                    enrichment_status="base"
                )
            
            # Update tracking fields
            doc.collection_attempts = (doc.collection_attempts or 0) + 1
            doc.last_collection_attempt = datetime.utcnow()
            
            if success:
                # Reset attempts on success
                doc.collection_attempts = 0
                doc.collection_error = None
                if market_cap:
                    doc.batch_priority = market_cap
            else:
                doc.collection_error = error
            
            await doc.save()
        
        except Exception as e:
            logger.error(
                f"Failed to update collection tracking for {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
    
    def get_job_status(self) -> Dict:
        """Get current job status and statistics."""
        return {
            "is_running": self.is_running,
            "last_discovery_run": self.last_discovery_run.isoformat() if self.last_discovery_run else None,
            "last_enrichment_run": self.last_enrichment_run.isoformat() if self.last_enrichment_run else None,
            "discovery_count": self.discovery_count,
            "enrichment_count": self.enrichment_count
        }


# Singleton instance
metadata_collector_job = MetadataCollectorJob()
