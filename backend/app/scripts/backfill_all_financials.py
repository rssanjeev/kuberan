#!/usr/bin/env python3
"""
Full Dataset Financial Statements Archival Script (Market Cap Priority)

⚠️ URGENT: MASSIVE API financials endpoint deprecated February 23, 2026
79 days remaining to complete archival

Purpose:
    Archive 12 financial statements per ticker for ALL 12,140 tickers:
    - 4 annual statements (10-K filings, 4 years of history)
    - 8 quarterly statements (10-Q filings, 2 years of history)
    
    CRITICAL: Process in DESCENDING market cap order (large-cap first)

Target:
    12,140 tickers × 12 statements = 145,680 total statements

Runtime:
    ~60 days (12,140 tickers × 7 minutes average per ticker)

Timeline:
    Start: January 1, 2026
    Complete: February 15, 2026 (8-day buffer before deletion)

Sort Strategy:
    Market cap DESCENDING → AAPL ($2.8T) → MSFT → NVDA → smallest
    
    Checkpoints:
    - Day 7: Top 80% market cap coverage (~500 largest companies)
    - Day 14: S&P 1500 equivalent (~1,500 companies)
    - Day 30: ~5,000 companies (mid-cap coverage complete)
    - Day 60: All 12,140 companies complete

Usage:
    python3 -m app.scripts.backfill_all_financials
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models import DOCUMENT_MODELS
from app.models.provider import CompanyOverview
from app.services.providers.implementations.massive_provider import massive_provider
from app.repositories.stock_repository import stock_repository
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Configuration
EXPORT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "financial_statements_archive" / "full_dataset"
CHECKPOINT_FILE = Path(__file__).parent / "full_dataset_checkpoint.json"
FAILED_TICKERS_FILE = Path(__file__).parent / "full_dataset_failed_tickers.json"
BATCH_EXPORT_SIZE = 100  # Export to JSON every N tickers
ANNUAL_LIMIT = 4
QUARTERLY_LIMIT = 8
RATE_LIMIT_DELAY = 12  # seconds between tickers


class FullDatasetArchivalJob:
    """Archive financial statements for all 12,140 tickers (market cap priority)."""
    
    def __init__(self):
        self.processed = 0
        self.statements_saved = 0
        self.failed_tickers = []
        self.start_time = None
        self.last_checkpoint_ticker = None
        self.total_tickers = 0
        self.batch_statements = []  # For batched JSON export
    
    async def run(self):
        """Execute full dataset archival job."""
        self.start_time = datetime.now()
        
        logger.info(
            "🚀 Starting FULL DATASET financials archival (MARKET CAP PRIORITY)",
            extra={
                "statements_per_ticker": ANNUAL_LIMIT + QUARTERLY_LIMIT,
                "sort_order": "market_cap DESC → largest companies first",
                "start_time": self.start_time.isoformat()
            }
        )
        
        try:
            # Initialize MongoDB
            await self._init_mongodb()
            
            # Create export directory
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            
            # Load checkpoint if exists
            start_ticker = await self._load_checkpoint()
            
            # Get ALL tickers sorted by market cap DESC
            tickers = await self._get_all_tickers_by_market_cap()
            
            if not tickers:
                logger.error("No tickers found for full dataset archival")
                return
            
            self.total_tickers = len(tickers)
            
            # Filter to start from checkpoint if resuming
            if start_ticker:
                logger.info(
                    f"📍 Resuming from checkpoint: {start_ticker}",
                    extra={"checkpoint_ticker": start_ticker}
                )
                # Find index of checkpoint ticker
                start_index = next(
                    (i for i, t in enumerate(tickers) if t.ticker == start_ticker),
                    0
                )
                tickers = tickers[start_index:]
            
            logger.info(
                f"📊 Loaded {len(tickers)} tickers for archival (market cap sorted)",
                extra={
                    "total_tickers": self.total_tickers,
                    "remaining": len(tickers),
                    "first_ticker": tickers[0].ticker if tickers else None,
                    "last_ticker": tickers[-1].ticker if tickers else None
                }
            )
            
            # Process each ticker
            for ticker_obj in tickers:
                await self._process_ticker(ticker_obj)
                
                # Rate limiting
                await asyncio.sleep(RATE_LIMIT_DELAY)
                
                # Save checkpoint every 10 tickers
                if self.processed % 10 == 0:
                    await self._save_checkpoint(ticker_obj.ticker)
                
                # Export batch every BATCH_EXPORT_SIZE tickers
                if len(self.batch_statements) >= BATCH_EXPORT_SIZE:
                    await self._export_batch()
            
            # Export any remaining statements
            if self.batch_statements:
                await self._export_batch()
            
            # Final summary
            await self._print_summary()
            
        except Exception as e:
            logger.error(
                "Full dataset archival job failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def _init_mongodb(self):
        """Initialize MongoDB connection."""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DATABASE_NAME", "kuberan")
        
        client = AsyncIOMotorClient(mongodb_url)
        db = client[db_name]
        
        await init_beanie(
            database=db,
            document_models=DOCUMENT_MODELS
        )
        
        logger.info(
            "MongoDB initialized",
            extra={"mongodb_url": mongodb_url, "database": db_name}
        )
    
    async def _get_all_tickers_by_market_cap(self) -> List[CompanyOverview]:
        """
        Get ALL tickers sorted by market cap DESCENDING.
        
        Sort Order:
        - Primary: Market cap DESCENDING (largest first: AAPL → MSFT → NVDA)
        - Secondary: Ticker alphabetically (for nulls/equal market caps)
        
        Returns:
            List of CompanyOverview objects (~12,140 tickers)
        """
        tickers = await CompanyOverview.find(
            CompanyOverview.active == True,
            CompanyOverview.enrichment_status != None
        ).sort([
            ("market_cap", -1),  # Descending: largest first
            ("ticker", 1)         # Alphabetical for nulls
        ]).to_list()
        
        return tickers
    
    async def _process_ticker(self, ticker_obj: CompanyOverview):
        """
        Process single ticker: fetch and save 12 statements.
        
        Args:
            ticker_obj: CompanyOverview object
        """
        ticker = ticker_obj.ticker
        market_cap = ticker_obj.market_cap
        
        try:
            # Calculate progress percentage
            progress_pct = round((self.processed / self.total_tickers) * 100, 2) if self.total_tickers > 0 else 0
            
            logger.info(
                f"Processing {ticker} ({self.processed + 1}/{self.total_tickers} - {progress_pct}%)",
                extra={
                    "ticker": ticker,
                    "progress": f"{self.processed + 1}/{self.total_tickers}",
                    "percentage": progress_pct,
                    "market_cap": market_cap,
                    "market_cap_billions": round(market_cap / 1e9, 2) if market_cap else None
                }
            )
            
            statements_for_ticker = []
            
            # Fetch 4 annual statements
            annual_statements = await massive_provider.fetch_financials(
                ticker=ticker,
                timeframe="annual",
                limit=ANNUAL_LIMIT
            )
            
            if annual_statements:
                statements_for_ticker.extend(annual_statements)
                logger.info(
                    f"Fetched {len(annual_statements)} annual statements for {ticker}",
                    extra={"ticker": ticker, "count": len(annual_statements)}
                )
            
            # Rate limiting between API calls
            await asyncio.sleep(12)
            
            # Fetch 8 quarterly statements
            quarterly_statements = await massive_provider.fetch_financials(
                ticker=ticker,
                timeframe="quarterly",
                limit=QUARTERLY_LIMIT
            )
            
            if quarterly_statements:
                statements_for_ticker.extend(quarterly_statements)
                logger.info(
                    f"Fetched {len(quarterly_statements)} quarterly statements for {ticker}",
                    extra={"ticker": ticker, "count": len(quarterly_statements)}
                )
            
            # Save statements to MongoDB
            saved_count = 0
            for statement_data in statements_for_ticker:
                # Add metadata
                statement_data["statement_type"] = "comprehensive"
                statement_data["source_provider"] = "polygon"
                
                # Convert fiscal_period to fiscal_quarter
                fiscal_period = statement_data.get("fiscal_period")
                if fiscal_period and fiscal_period.startswith("Q"):
                    statement_data["fiscal_quarter"] = int(fiscal_period[1])
                
                # Save to database
                await stock_repository.save_financial_statement(statement_data)
                saved_count += 1
            
            self.statements_saved += saved_count
            
            # Add to batch for JSON export
            self.batch_statements.append({
                "ticker": ticker,
                "market_cap": market_cap,
                "fetch_date": datetime.now().isoformat(),
                "statement_count": len(statements_for_ticker),
                "statements": statements_for_ticker
            })
            
            logger.info(
                f"✅ Saved {saved_count} statements for {ticker}",
                extra={
                    "ticker": ticker,
                    "statements_saved": saved_count,
                    "total_saved": self.statements_saved
                }
            )
            
            self.processed += 1
            
            # Progress update every 100 tickers
            if self.processed % 100 == 0:
                await self._print_progress()
        
        except Exception as e:
            logger.error(
                f"❌ Failed to process {ticker}",
                extra={
                    "ticker": ticker,
                    "market_cap": market_cap,
                    "error": str(e)
                },
                exc_info=True
            )
            self.failed_tickers.append({
                "ticker": ticker,
                "market_cap": market_cap,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.processed += 1
    
    async def _export_batch(self):
        """
        Export batch of ticker statements to JSON.
        """
        try:
            batch_num = self.processed // BATCH_EXPORT_SIZE
            export_file = EXPORT_DIR / f"batch_{batch_num:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "batch_number": batch_num,
                "ticker_count": len(self.batch_statements),
                "export_date": datetime.now().isoformat(),
                "tickers": self.batch_statements
            }
            
            with open(export_file, "w") as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(
                f"📦 Exported batch {batch_num} to {export_file.name}",
                extra={
                    "batch_number": batch_num,
                    "ticker_count": len(self.batch_statements),
                    "file": str(export_file)
                }
            )
            
            # Clear batch
            self.batch_statements = []
        
        except Exception as e:
            logger.error(
                "Failed to export batch",
                extra={"error": str(e)},
                exc_info=True
            )
    
    async def _save_checkpoint(self, ticker: str):
        """
        Save progress checkpoint.
        
        Args:
            ticker: Last processed ticker
        """
        try:
            checkpoint = {
                "last_ticker": ticker,
                "processed_count": self.processed,
                "total_tickers": self.total_tickers,
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "timestamp": datetime.now().isoformat(),
                "progress_percentage": round((self.processed / self.total_tickers) * 100, 2) if self.total_tickers > 0 else 0
            }
            
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(checkpoint, f, indent=2)
            
            logger.debug(
                f"Checkpoint saved: {ticker}",
                extra={"ticker": ticker, "processed": self.processed}
            )
        
        except Exception as e:
            logger.error(
                "Failed to save checkpoint",
                extra={"error": str(e)},
                exc_info=True
            )
    
    async def _load_checkpoint(self) -> Optional[str]:
        """
        Load checkpoint if exists.
        
        Returns:
            Last processed ticker or None
        """
        if not CHECKPOINT_FILE.exists():
            return None
        
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                checkpoint = json.load(f)
            
            self.processed = checkpoint.get("processed_count", 0)
            self.statements_saved = checkpoint.get("statements_saved", 0)
            self.total_tickers = checkpoint.get("total_tickers", 0)
            last_ticker = checkpoint.get("last_ticker")
            
            logger.info(
                f"Loaded checkpoint: {last_ticker}",
                extra={
                    "last_ticker": last_ticker,
                    "processed": self.processed,
                    "total": self.total_tickers,
                    "progress_pct": checkpoint.get("progress_percentage", 0),
                    "statements_saved": self.statements_saved
                }
            )
            
            return last_ticker
        
        except Exception as e:
            logger.error(
                "Failed to load checkpoint",
                extra={"error": str(e)},
                exc_info=True
            )
            return None
    
    async def _print_progress(self):
        """Print progress update with market cap coverage."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        tickers_remaining = self.total_tickers - self.processed
        avg_time_per_ticker = elapsed / self.processed if self.processed > 0 else 0
        estimated_remaining = tickers_remaining * avg_time_per_ticker
        
        # Calculate market cap coverage milestones
        progress_pct = (self.processed / self.total_tickers) * 100 if self.total_tickers > 0 else 0
        
        milestone = ""
        if progress_pct >= 4.1:  # ~500 tickers
            milestone = "✅ Top 80% market cap"
        if progress_pct >= 12.4:  # ~1,500 tickers
            milestone = "✅ S&P 1500 equivalent"
        if progress_pct >= 41.2:  # ~5,000 tickers
            milestone = "✅ Mid-cap coverage complete"
        
        logger.info(
            f"📈 Progress Update {milestone}",
            extra={
                "processed": self.processed,
                "total": self.total_tickers,
                "percentage": round(progress_pct, 2),
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "elapsed_hours": round(elapsed / 3600, 2),
                "elapsed_days": round(elapsed / 86400, 2),
                "estimated_remaining_hours": round(estimated_remaining / 3600, 2),
                "estimated_remaining_days": round(estimated_remaining / 86400, 2)
            }
        )
    
    async def _print_summary(self):
        """Print final summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info(
            "✅ FULL DATASET archival complete!",
            extra={
                "tickers_processed": self.processed,
                "total_tickers": self.total_tickers,
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "duration_hours": round(elapsed / 3600, 2),
                "duration_days": round(elapsed / 86400, 2),
                "statements_per_ticker_avg": round(self.statements_saved / self.processed, 1) if self.processed > 0 else 0
            }
        )
        
        # Save failed tickers report
        if self.failed_tickers:
            with open(FAILED_TICKERS_FILE, "w") as f:
                json.dump(self.failed_tickers, f, indent=2)
            
            logger.warning(
                f"Failed tickers saved to {FAILED_TICKERS_FILE}",
                extra={"failed_count": len(self.failed_tickers)}
            )


async def main():
    """Main execution function."""
    job = FullDatasetArchivalJob()
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())
