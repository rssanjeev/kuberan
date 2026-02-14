#!/usr/bin/env python3
"""
Phase 3 Backfill Script: Enhanced Ticker Overview

Updates existing 1,418 CompanyOverview records with complete 30+ MASSIVE fields.

CRITICAL REQUIREMENTS:
- Zero data loss: Preserve all existing fields
- Rollback capability: Save backups before update
- Validation: Verify new fields populated correctly
- Rate limiting: Respect 5 calls/min MASSIVE limit

Usage:
    # Dry run (no changes)
    python3 -m app.scripts.backfill_phase3_ticker_details --dry-run
    
    # Test on 10 tickers
    python3 -m app.scripts.backfill_phase3_ticker_details --test --limit 10
    
    # Full backfill with backup
    python3 -m app.scripts.backfill_phase3_ticker_details --backup
    
    # Resume from ticker (if interrupted)
    python3 -m app.scripts.backfill_phase3_ticker_details --resume MSFT

Created: December 5, 2025
Author: Kuberan MASSIVE Integration (Phase 3)
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.provider import CompanyOverview
from app.models import DOCUMENT_MODELS
from app.services.providers.implementations.massive_provider import MassiveProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Phase3BackfillScript:
    """Backfill script for Phase 3 enhanced ticker overview."""
    
    def __init__(
        self,
        dry_run: bool = False,
        test_mode: bool = False,
        backup: bool = False,
        limit: Optional[int] = None,
        resume_from: Optional[str] = None
    ):
        self.dry_run = dry_run
        self.test_mode = test_mode
        self.backup = backup
        self.limit = limit
        self.resume_from = resume_from
        
        self.massive_provider: Optional[MassiveProvider] = None
        self.stats = {
            "total_tickers": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "backed_up": 0,
            "new_fields_added": {},  # Field name -> count of records with new data
        }
        
    async def initialize(self):
        """Initialize database connection and provider."""
        logger.info("Initializing Phase 3 backfill script")
        
        # Connect to MongoDB (use environment variable or default to Docker service name)
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
        client = AsyncIOMotorClient(mongodb_url)
        db_name = os.getenv("DATABASE_NAME", "kuberan")
        db = client[db_name]
        
        # Initialize Beanie
        await init_beanie(database=db, document_models=DOCUMENT_MODELS)
        
        # Initialize MASSIVE provider with API key from environment
        api_key = os.getenv("MASSIVE_KEY")
        if not api_key:
            raise ValueError("MASSIVE_KEY environment variable not set")
        self.massive_provider = MassiveProvider(api_key=api_key)
        
        logger.info("Initialization complete")
    
    async def get_tickers_to_backfill(self) -> List[CompanyOverview]:
        """
        Get list of CompanyOverview records that need backfilling.
        
        Criteria:
        - enrichment_status = "foundation" (from Phase 1)
        - Missing any of the 30+ MASSIVE fields (cik, phone_number, logo_url, etc.)
        """
        query = CompanyOverview.find(
            CompanyOverview.enrichment_status == "foundation"
        )
        
        # Resume from specific ticker if provided
        if self.resume_from:
            query = query.find(CompanyOverview.ticker >= self.resume_from)
        
        # Apply limit
        if self.limit:
            query = query.limit(self.limit)
        
        # Sort by ticker for consistent ordering
        query = query.sort("ticker")
        
        tickers = await query.to_list()
        self.stats["total_tickers"] = len(tickers)
        
        logger.info(
            f"Found {len(tickers)} tickers to backfill",
            extra={
                "total": len(tickers),
                "resume_from": self.resume_from,
                "limit": self.limit
            }
        )
        
        return tickers
    
    async def backup_ticker(self, ticker_obj: CompanyOverview) -> bool:
        """
        Save backup of existing ticker data before update.
        
        Backup format: JSON file in backend/backups/phase3/TICKER_YYYYMMDD_HHMMSS.json
        """
        if not self.backup:
            return True
        
        try:
            backup_dir = Path(__file__).parent.parent.parent / "backups" / "phase3"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{ticker_obj.ticker}_{timestamp}.json"
            
            # Convert to dict and save
            backup_data = ticker_obj.dict()
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self.stats["backed_up"] += 1
            logger.debug(
                f"Backed up ticker data",
                extra={"ticker": ticker_obj.ticker, "file": str(backup_file)}
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to backup ticker",
                extra={"ticker": ticker_obj.ticker, "error": str(e)},
                exc_info=True
            )
            return False
    
    async def fetch_complete_details(self, ticker: str) -> Optional[Dict]:
        """Fetch complete 30+ field details from MASSIVE API."""
        try:
            details = await self.massive_provider.fetch_ticker_details(ticker)
            
            if not details:
                logger.warning(
                    f"No details returned for ticker",
                    extra={"ticker": ticker}
                )
                return None
            
            return details
            
        except Exception as e:
            logger.error(
                f"Failed to fetch ticker details",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return None
    
    async def update_ticker(
        self,
        ticker_obj: CompanyOverview,
        new_data: Dict
    ) -> bool:
        """
        Update ticker with new MASSIVE data.
        
        ZERO DATA LOSS: Only add new fields, never overwrite existing non-null values.
        """
        try:
            # Track which fields are being added
            new_fields = []
            
            # Get valid fields from CompanyOverview model
            valid_fields = set(CompanyOverview.model_fields.keys())
            
            # Update fields only if they're currently None or missing
            for field_name, new_value in new_data.items():
                if new_value is None:
                    continue
                
                # Skip fields that don't exist in the model
                if field_name not in valid_fields:
                    continue
                
                current_value = getattr(ticker_obj, field_name, None)
                
                # Only update if current value is None or empty
                if current_value is None or current_value == "":
                    setattr(ticker_obj, field_name, new_value)
                    new_fields.append(field_name)
                    
                    # Track stats
                    if field_name not in self.stats["new_fields_added"]:
                        self.stats["new_fields_added"][field_name] = 0
                    self.stats["new_fields_added"][field_name] += 1
            
            # Update enrichment metadata
            ticker_obj.enrichment_status = "enriched"
            ticker_obj.enriched_at = datetime.utcnow()
            if "MASSIVE" not in ticker_obj.metadata_sources:
                ticker_obj.metadata_sources.append("MASSIVE")
            
            # Save if not dry run
            if not self.dry_run:
                await ticker_obj.save()
            
            logger.info(
                f"Updated ticker with {len(new_fields)} new fields",
                extra={
                    "ticker": ticker_obj.ticker,
                    "new_fields": new_fields[:10],  # Show first 10
                    "total_new_fields": len(new_fields),
                    "dry_run": self.dry_run
                }
            )
            
            self.stats["updated"] += 1
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to update ticker",
                extra={"ticker": ticker_obj.ticker, "error": str(e)},
                exc_info=True
            )
            self.stats["failed"] += 1
            return False
    
    async def backfill_single_ticker(self, ticker_obj: CompanyOverview) -> bool:
        """Backfill single ticker with complete MASSIVE data."""
        ticker = ticker_obj.ticker
        
        logger.info(
            f"Processing ticker",
            extra={"ticker": ticker, "current_status": ticker_obj.enrichment_status}
        )
        
        # Step 1: Backup existing data
        if self.backup:
            backup_success = await self.backup_ticker(ticker_obj)
            if not backup_success:
                logger.error(f"Backup failed for {ticker}, skipping update")
                self.stats["skipped"] += 1
                return False
        
        # Step 2: Fetch complete details from MASSIVE
        new_data = await self.fetch_complete_details(ticker)
        if not new_data:
            logger.warning(f"No new data for {ticker}, skipping")
            self.stats["skipped"] += 1
            return False
        
        # Step 3: Update ticker record
        success = await self.update_ticker(ticker_obj, new_data)
        
        # Step 4: Rate limiting - wait 12 seconds between calls (5 calls/min)
        if not self.dry_run:
            await asyncio.sleep(12)
        
        return success
    
    async def run(self):
        """Execute backfill process."""
        logger.info(
            "Starting Phase 3 backfill",
            extra={
                "dry_run": self.dry_run,
                "test_mode": self.test_mode,
                "backup": self.backup,
                "limit": self.limit,
                "resume_from": self.resume_from
            }
        )
        
        # Get tickers to backfill
        tickers = await self.get_tickers_to_backfill()
        
        if not tickers:
            logger.info("No tickers found to backfill")
            return
        
        # Process each ticker
        for i, ticker_obj in enumerate(tickers, 1):
            logger.info(
                f"Processing {i}/{len(tickers)}",
                extra={"ticker": ticker_obj.ticker, "progress": f"{i}/{len(tickers)}"}
            )
            
            await self.backfill_single_ticker(ticker_obj)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print backfill summary statistics."""
        logger.info("=" * 80)
        logger.info("Phase 3 Backfill Summary")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE UPDATE'}")
        logger.info(f"Total tickers: {self.stats['total_tickers']}")
        logger.info(f"Updated: {self.stats['updated']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Backed up: {self.stats['backed_up']}")
        logger.info("")
        logger.info("New fields added (top 10):")
        
        # Sort by count descending
        sorted_fields = sorted(
            self.stats["new_fields_added"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for field_name, count in sorted_fields[:10]:
            logger.info(f"  {field_name}: {count} records")
        
        logger.info("=" * 80)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 3 Backfill: Enhanced Ticker Overview (30+ MASSIVE fields)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: Process only limited tickers (use with --limit)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create JSON backups before updating"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of tickers to process"
    )
    parser.add_argument(
        "--resume",
        type=str,
        metavar="TICKER",
        help="Resume from specific ticker symbol"
    )
    
    args = parser.parse_args()
    
    # Create and run script
    script = Phase3BackfillScript(
        dry_run=args.dry_run,
        test_mode=args.test,
        backup=args.backup,
        limit=args.limit,
        resume_from=args.resume
    )
    
    await script.initialize()
    await script.run()


if __name__ == "__main__":
    asyncio.run(main())
