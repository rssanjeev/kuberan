"""
Historical Data Backfill Job - Gradual 5-year cache population.

Fetches 5 years of historical OHLCV data for active tickers to populate
the database cache. Enables fast queries for technical analysis, backtesting,
and charting without repeated Yahoo Finance API calls.

Process:
1. Query 10 tickers with enrichment_status="foundation" and no/incomplete history
2. For each ticker:
   - Fetch 5-year daily data from Yahoo Finance
   - Save to stock_historical_prices collection
   - Add 12-second delay (rate limiting)
3. Track progress and handle errors gracefully

Schedule: Daily at 6:00 PM EST
Rate Limiting: 12 seconds between API calls (5 calls/min)
Throughput: 10 tickers/day × 5 years = ~12,600 records/day
Coverage Timeline: ~1,200 tickers over 120 days (4 months)

SECURITY: No sensitive data stored, only public market data.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import time

from app.core.logging_config import get_logger
from app.models.provider import CompanyOverview
from app.services.stock.fetcher import StockFetcher
from app.repositories.provider_repository import provider_repository

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions
# ============================================================================

async def get_tickers_for_backfill(limit: int = 10) -> List[CompanyOverview]:
    """
    Query tickers that need historical data backfill.
    
    Prioritizes tickers with:
    - enrichment_status="foundation" (basic metadata collected)
    - active=True (currently trading)
    - No extended_data.backfill_complete flag
    
    Args:
        limit: Maximum number of tickers to return
        
    Returns:
        List of CompanyOverview objects ready for backfill
    """
    try:
        # Query tickers needing backfill
        # Filter for tickers with:
        # 1. enrichment_status = "foundation" (basic metadata collected)
        # 2. active = True (currently trading)
        # 3. extended_data.backfill_complete != True (not already backfilled)
        tickers = await CompanyOverview.find(
            {
                "enrichment_status": "foundation",
                "active": True,
                "extended_data.backfill_complete": {"$ne": True}
            }
        ).limit(limit).to_list()
        
        logger.info(
            f"Found {len(tickers)} tickers for historical backfill",
            extra={"ticker_count": len(tickers), "limit": limit}
        )
        
        return tickers
    
    except Exception as e:
        logger.error(
            "Failed to query tickers for backfill",
            extra={"error": str(e)},
            exc_info=True
        )
        return []


async def fetch_and_save_historical_data(
    fetcher: StockFetcher,
    ticker: str,
    period: str = "5y"
) -> Dict:
    """
    Fetch 5-year historical data and save to database.
    
    Args:
        fetcher: StockFetcher instance
        ticker: Stock ticker symbol
        period: Time period (default: 5y)
        
    Returns:
        Result dictionary with status and record count
    """
    try:
        logger.info(
            f"Fetching historical data for {ticker}",
            extra={"ticker": ticker, "period": period}
        )
        
        # Fetch from Yahoo Finance
        history = await fetcher.get_stock_history(ticker, period=period)
        
        if not history or not history.get("data"):
            logger.warning(
                f"No historical data available for {ticker}",
                extra={"ticker": ticker}
            )
            return {
                "ticker": ticker,
                "status": "no_data",
                "records_saved": 0
            }
        
        # Save to database with caching
        saved_count = await provider_repository.save_historical_prices_bulk(
            ticker=ticker,
            historical_data=history["data"],
            source="yfinance",
            interval="1d"
        )
        
        logger.info(
            f"Saved {saved_count} historical records for {ticker}",
            extra={
                "ticker": ticker,
                "records_saved": saved_count,
                "total_fetched": len(history["data"])
            }
        )
        
        return {
            "ticker": ticker,
            "status": "success",
            "records_fetched": len(history["data"]),
            "records_saved": saved_count
        }
    
    except Exception as e:
        logger.error(
            f"Failed to fetch/save historical data for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return {
            "ticker": ticker,
            "status": "error",
            "error": str(e),
            "records_saved": 0
        }


async def mark_backfill_complete(ticker: str) -> bool:
    """
    Mark ticker as backfill complete in database.
    
    Updates extended_data.backfill_complete flag to prevent re-processing.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if updated successfully, False otherwise
    """
    try:
        ticker_obj = await CompanyOverview.find_one(
            CompanyOverview.ticker == ticker
        )
        
        if not ticker_obj:
            logger.warning(
                f"Ticker {ticker} not found for backfill completion update",
                extra={"ticker": ticker}
            )
            return False
        
        # Update extended_data with backfill completion
        if not ticker_obj.extended_data:
            ticker_obj.extended_data = {}
        
        ticker_obj.extended_data["backfill_complete"] = True
        ticker_obj.extended_data["backfill_timestamp"] = datetime.utcnow().isoformat()
        
        await ticker_obj.save()
        
        logger.debug(
            f"Marked {ticker} backfill as complete",
            extra={"ticker": ticker}
        )
        
        return True
    
    except Exception as e:
        logger.error(
            f"Failed to mark backfill complete for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return False


# ============================================================================
# Job Class: Historical Data Backfill Orchestration
# ============================================================================

class HistoricalDataBackfillJob:
    """
    Daily job to gradually backfill 5-year historical data for active tickers.
    
    Timeline:
    - Runs daily at 6:00 PM EST
    - Processes 10 tickers per run
    - Fetches 5 years of daily data (~1,260 records per ticker)
    - ~12,600 records/day added to database
    - ~120 days (4 months) to complete all ~1,200 tickers
    
    Rate Limiting:
    - 12-second delay between API calls
    - 5 calls/min to Yahoo Finance (conservative)
    - Total execution time: ~2 minutes per run
    
    First Run:
    - Starts with any tickers having enrichment_status="foundation"
    - Prioritizes tickers without backfill_complete flag
    """
    
    def __init__(self):
        """Initialize historical data backfill job."""
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.total_tickers_processed: int = 0
        self.total_records_saved: int = 0
        self.fetcher = StockFetcher()
    
    async def run(self, batch_size: int = 10) -> Dict:
        """
        Execute historical data backfill for a batch of tickers.
        
        Args:
            batch_size: Number of tickers to process per run (default: 10)
            
        Returns:
            Statistics dictionary with backfill results
        """
        if self.is_running:
            logger.warning("Historical backfill job already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info(
                "Starting historical data backfill",
                extra={"batch_size": batch_size}
            )
            
            # Get tickers needing backfill
            tickers = await get_tickers_for_backfill(limit=batch_size)
            
            if not tickers:
                logger.info("No tickers need historical backfill at this time")
                self.last_run = datetime.utcnow()
                return {
                    "status": "success",
                    "message": "No tickers need backfill",
                    "tickers_processed": 0,
                    "records_saved": 0
                }
            
            # Process each ticker with rate limiting
            results = []
            records_saved_this_run = 0
            
            for idx, ticker_obj in enumerate(tickers):
                ticker = ticker_obj.ticker
                
                logger.info(
                    f"Processing ticker {idx + 1}/{len(tickers)}: {ticker}",
                    extra={
                        "ticker": ticker,
                        "progress": f"{idx + 1}/{len(tickers)}"
                    }
                )
                
                # Fetch and save historical data
                result = await fetch_and_save_historical_data(
                    self.fetcher,
                    ticker,
                    period="5y"
                )
                
                results.append(result)
                records_saved_this_run += result.get("records_saved", 0)
                
                # Mark as complete if successful
                if result["status"] == "success":
                    await mark_backfill_complete(ticker)
                
                # Rate limiting: 12-second delay between API calls
                # (Except for last ticker - no need to wait)
                if idx < len(tickers) - 1:
                    logger.debug(
                        f"Rate limiting: waiting 12 seconds before next ticker",
                        extra={"next_ticker": tickers[idx + 1].ticker}
                    )
                    await asyncio.sleep(12)
            
            # Update job statistics
            self.last_run = datetime.utcnow()
            self.total_tickers_processed += len(tickers)
            self.total_records_saved += records_saved_this_run
            
            elapsed_time = time.time() - start_time
            
            # Compile results
            successful = sum(1 for r in results if r["status"] == "success")
            failed = sum(1 for r in results if r["status"] == "error")
            no_data = sum(1 for r in results if r["status"] == "no_data")
            
            result = {
                "status": "success",
                "tickers_processed": len(tickers),
                "successful": successful,
                "failed": failed,
                "no_data": no_data,
                "records_saved": records_saved_this_run,
                "elapsed_seconds": round(elapsed_time, 2),
                "total_tickers_all_time": self.total_tickers_processed,
                "total_records_all_time": self.total_records_saved,
                "details": results
            }
            
            logger.info(
                "Historical backfill complete",
                extra={
                    "tickers_processed": len(tickers),
                    "records_saved": records_saved_this_run,
                    "elapsed_seconds": round(elapsed_time, 2)
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "Historical backfill job failed",
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
            "total_tickers_processed": self.total_tickers_processed,
            "total_records_saved": self.total_records_saved
        }


# Singleton instance
historical_data_backfill = HistoricalDataBackfillJob()
