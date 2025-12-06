#!/usr/bin/env python3
"""
S&P 500 Financial Statements Archival Script

⚠️ URGENT: MASSIVE API financials endpoint deprecated February 23, 2026
79 days remaining to complete archival

Purpose:
    Archive 12 financial statements per ticker for S&P 500 companies:
    - 4 annual statements (10-K filings, 4 years of history)
    - 8 quarterly statements (10-Q filings, 2 years of history)

Target:
    500 tickers × 12 statements = 6,000 total statements

Runtime:
    ~20 hours (500 tickers × 2.4 minutes average per ticker)

Timeline:
    Start: December 6, 2025
    Complete: December 7, 2025

Usage:
    python3 -m app.scripts.backfill_sp500_financials
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
EXPORT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "financial_statements_archive" / "sp500"
CHECKPOINT_FILE = Path(__file__).parent / "sp500_checkpoint.json"
FAILED_TICKERS_FILE = Path(__file__).parent / "sp500_failed_tickers.json"
TARGET_TICKERS = 500
ANNUAL_LIMIT = 4
QUARTERLY_LIMIT = 8
RATE_LIMIT_DELAY = 12  # seconds between tickers


class SP500ArchivalJob:
    """Archive financial statements for S&P 500 companies."""
    
    def __init__(self):
        self.processed = 0
        self.statements_saved = 0
        self.failed_tickers = []
        self.start_time = None
        self.last_checkpoint_ticker = None
    
    async def run(self):
        """Execute S&P 500 archival job."""
        self.start_time = datetime.now()
        
        logger.info(
            "🚀 Starting S&P 500 financials archival",
            extra={
                "target_tickers": TARGET_TICKERS,
                "statements_per_ticker": ANNUAL_LIMIT + QUARTERLY_LIMIT,
                "total_target": TARGET_TICKERS * (ANNUAL_LIMIT + QUARTERLY_LIMIT),
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
            
            # Get S&P 500 tickers (top 500 by market cap)
            tickers = await self._get_sp500_tickers()
            
            if not tickers:
                logger.error("No tickers found for S&P 500 archival")
                return
            
            # Filter to start from checkpoint if resuming
            if start_ticker:
                logger.info(
                    f"📍 Resuming from checkpoint: {start_ticker}",
                    extra={"checkpoint_ticker": start_ticker}
                )
                tickers = [t for t in tickers if t.ticker >= start_ticker]
            
            logger.info(
                f"📊 Loaded {len(tickers)} tickers for archival",
                extra={"ticker_count": len(tickers)}
            )
            
            # Process each ticker
            for ticker_obj in tickers:
                await self._process_ticker(ticker_obj)
                
                # Rate limiting
                await asyncio.sleep(RATE_LIMIT_DELAY)
                
                # Save checkpoint every 10 tickers
                if self.processed % 10 == 0:
                    await self._save_checkpoint(ticker_obj.ticker)
            
            # Final summary
            await self._print_summary()
            
        except Exception as e:
            logger.error(
                "S&P 500 archival job failed",
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
    
    async def _get_sp500_tickers(self) -> List[CompanyOverview]:
        """
        Get top 500 tickers by market cap (S&P 500 proxy).
        
        Returns:
            List of CompanyOverview objects
        """
        tickers = await CompanyOverview.find(
            CompanyOverview.active == True,
            CompanyOverview.enrichment_status != None,
            CompanyOverview.market_cap != None
        ).sort([
            ("market_cap", -1)  # Descending market cap
        ]).limit(TARGET_TICKERS).to_list()
        
        return tickers
    
    async def _process_ticker(self, ticker_obj: CompanyOverview):
        """
        Process single ticker: fetch and save 12 statements.
        
        Args:
            ticker_obj: CompanyOverview object
        """
        ticker = ticker_obj.ticker
        
        try:
            logger.info(
                f"Processing {ticker} ({self.processed + 1}/{TARGET_TICKERS})",
                extra={
                    "ticker": ticker,
                    "progress": f"{self.processed + 1}/{TARGET_TICKERS}",
                    "market_cap": ticker_obj.market_cap
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
            
            # Export to JSON
            await self._export_ticker_data(ticker, statements_for_ticker)
            
            logger.info(
                f"✅ Saved {saved_count} statements for {ticker}",
                extra={
                    "ticker": ticker,
                    "statements_saved": saved_count,
                    "total_saved": self.statements_saved
                }
            )
            
            self.processed += 1
            
            # Progress update every 50 tickers
            if self.processed % 50 == 0:
                await self._print_progress()
        
        except Exception as e:
            logger.error(
                f"❌ Failed to process {ticker}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            self.failed_tickers.append({
                "ticker": ticker,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.processed += 1
    
    async def _export_ticker_data(self, ticker: str, statements: List[Dict]):
        """
        Export ticker statements to JSON.
        
        Args:
            ticker: Ticker symbol
            statements: List of financial statements
        """
        try:
            export_file = EXPORT_DIR / f"{ticker}_{datetime.now().strftime('%Y%m%d')}.json"
            
            export_data = {
                "ticker": ticker,
                "fetch_date": datetime.now().isoformat(),
                "statement_count": len(statements),
                "statements": statements
            }
            
            with open(export_file, "w") as f:
                json.dump(export_data, f, indent=2)
            
            logger.debug(
                f"Exported {ticker} data to {export_file}",
                extra={"ticker": ticker, "file": str(export_file)}
            )
        
        except Exception as e:
            logger.error(
                f"Failed to export {ticker} data",
                extra={"ticker": ticker, "error": str(e)},
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
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "timestamp": datetime.now().isoformat()
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
            last_ticker = checkpoint.get("last_ticker")
            
            logger.info(
                f"Loaded checkpoint: {last_ticker}",
                extra={
                    "last_ticker": last_ticker,
                    "processed": self.processed,
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
        """Print progress update."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        tickers_remaining = TARGET_TICKERS - self.processed
        avg_time_per_ticker = elapsed / self.processed if self.processed > 0 else 0
        estimated_remaining = tickers_remaining * avg_time_per_ticker
        
        logger.info(
            f"📈 Progress Update",
            extra={
                "processed": self.processed,
                "total": TARGET_TICKERS,
                "percentage": round((self.processed / TARGET_TICKERS) * 100, 1),
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "elapsed_hours": round(elapsed / 3600, 2),
                "estimated_remaining_hours": round(estimated_remaining / 3600, 2)
            }
        )
    
    async def _print_summary(self):
        """Print final summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info(
            "✅ S&P 500 archival complete!",
            extra={
                "tickers_processed": self.processed,
                "statements_saved": self.statements_saved,
                "failed_count": len(self.failed_tickers),
                "duration_hours": round(elapsed / 3600, 2),
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
    job = SP500ArchivalJob()
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())
