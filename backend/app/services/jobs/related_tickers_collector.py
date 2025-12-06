"""
Related Tickers Collector Job

PHASE 4: Weekly collection of related companies/competitors for tracked tickers.

This job fetches related companies (peers, competitors, correlated stocks) from 
MASSIVE API and stores them in the RelatedCompany collection. Helps users discover
similar stocks for competitive analysis and portfolio diversification.

Schedule: Weekly (Monday 4:00 AM EST)
Target: 300 tickers per week (S&P 500 priority initially)
Rate Budget: 300 calls/week = 42.8 calls/day (within 7,200/day limit)

SECURITY: No sensitive data stored. Only ticker relationships and correlation scores.

Created: December 5, 2025 (Phase 4 implementation)
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from app.core.logging_config import get_logger
from app.models.provider import RelatedCompany
from app.repositories.stock_repository import stock_repository
from app.services.providers.implementations.massive_provider import massive_provider

logger = get_logger(__name__)


class RelatedTickersCollectorJob:
    """
    Background job to collect related companies for tracked tickers.
    
    Implementation Pattern: Hybrid functional/OOP
    - Pure function: collect_related_companies_for_ticker (testable core logic)
    - Job class: Manages scheduling, state, and statistics (lifecycle)
    
    Features:
    - S&P 500 priority (largest companies first)
    - Market cap sorting (focus on major stocks)
    - Rate limiting (12 seconds between calls = 5 calls/min)
    - Upsert logic (update existing relationships)
    - Statistics tracking (processed, relationships found, errors)
    """
    
    def __init__(self):
        """Initialize job with state tracking."""
        self.last_run: Optional[datetime] = None
        self.total_tickers_processed: int = 0
        self.total_relationships_found: int = 0
        self.is_running: bool = False
    
    async def run(self):
        """
        Main job execution: Fetch related companies for 300 tickers.
        
        Process:
        1. Get high-priority tickers (S&P 500, high market cap)
        2. For each ticker, fetch related companies from MASSIVE
        3. Save RelatedCompany records (upsert on ticker+related_ticker pair)
        4. Track statistics and handle errors
        5. Update job state
        """
        if self.is_running:
            logger.warning("Related tickers collector already running, skipping")
            return
        
        self.is_running = True
        start_time = datetime.now()
        
        logger.info("Starting related tickers collection job")
        
        try:
            # Get high-priority tickers (S&P 500, high market cap)
            tickers = await self._get_priority_tickers(limit=300)
            
            if not tickers:
                logger.warning("No tickers found for related companies collection")
                return
            
            logger.info(
                f"Loaded {len(tickers)} tickers for related companies collection",
                extra={"ticker_count": len(tickers)}
            )
            
            # Statistics
            processed = 0
            relationships_found = 0
            errors = 0
            skipped = 0
            
            # Process each ticker with rate limiting
            for ticker_obj in tickers:
                ticker = ticker_obj.ticker
                
                try:
                    # Fetch related companies from MASSIVE
                    related_data = await massive_provider.fetch_related_companies(ticker)
                    
                    if related_data:
                        # Save each relationship
                        saved_count = await self._save_related_companies(
                            ticker=ticker,
                            related_data=related_data
                        )
                        
                        processed += 1
                        relationships_found += saved_count
                        
                        logger.info(
                            f"Saved {saved_count} related companies for {ticker}",
                            extra={
                                "ticker": ticker,
                                "relationships": saved_count
                            }
                        )
                    else:
                        # No relationships found (404 response)
                        skipped += 1
                        logger.debug(
                            f"No related companies found for {ticker}",
                            extra={"ticker": ticker}
                        )
                    
                    # Rate limiting: 12 seconds between calls = 5 calls/min
                    await asyncio.sleep(12)
                
                except Exception as e:
                    errors += 1
                    logger.error(
                        f"Failed to collect related companies for {ticker}",
                        extra={"ticker": ticker, "error": str(e)},
                        exc_info=True
                    )
                    # Continue with next ticker
            
            # Update job state
            self.last_run = datetime.now()
            self.total_tickers_processed += processed
            self.total_relationships_found += relationships_found
            
            # Log summary
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Related tickers collection completed in {duration:.1f}s",
                extra={
                    "processed": processed,
                    "relationships_found": relationships_found,
                    "skipped": skipped,
                    "errors": errors,
                    "duration_seconds": duration
                }
            )
        
        except Exception as e:
            logger.error(
                "Related tickers collection job failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
        
        finally:
            self.is_running = False
    
    async def _get_priority_tickers(self, limit: int = 300) -> List:
        """
        Get high-priority tickers for relationship discovery.
        
        Priority order:
        1. S&P 500 companies (largest market cap)
        2. User watchlist tickers
        3. High market cap stocks
        4. ETFs (major market indices)
        
        Args:
            limit: Maximum number of tickers to return
            
        Returns:
            List of CompanyOverview objects
        """
        try:
            # Query CompanyOverview with enrichment_status != None (enriched tickers)
            # Sort by market_cap DESC (largest companies first)
            # Filter active=true (exclude delisted)
            from app.models.provider import CompanyOverview
            
            tickers = await CompanyOverview.find(
                CompanyOverview.active == True,
                CompanyOverview.enrichment_status != None,
                CompanyOverview.market_cap != None
            ).sort([("market_cap", -1)]).limit(limit).to_list()
            
            logger.info(
                f"Loaded {len(tickers)} priority tickers",
                extra={
                    "limit": limit,
                    "loaded": len(tickers)
                }
            )
            
            return tickers
        
        except Exception as e:
            logger.error(
                "Failed to load priority tickers",
                extra={"error": str(e)},
                exc_info=True
            )
            return []
    
    async def _save_related_companies(
        self,
        ticker: str,
        related_data: List[Dict]
    ) -> int:
        """
        Save related companies to database.
        
        Uses upsert logic: Update if relationship exists, insert if new.
        
        Args:
            ticker: Primary ticker symbol
            related_data: List of related company dictionaries from MASSIVE
            
        Returns:
            Number of relationships saved
        """
        saved_count = 0
        
        for company in related_data:
            try:
                related_ticker = company.get("ticker")
                if not related_ticker:
                    continue
                
                # Check if relationship already exists
                existing = await RelatedCompany.find_one(
                    RelatedCompany.ticker == ticker,
                    RelatedCompany.related_ticker == related_ticker
                )
                
                if existing:
                    # Update existing relationship
                    existing.relationship_type = company.get("relationship_type")
                    existing.correlation_score = company.get("similarity_score")
                    existing.last_updated = datetime.now()
                    existing.extended_data = company.get("extended_data", {})
                    
                    await existing.save()
                    saved_count += 1
                else:
                    # Create new relationship
                    relationship = RelatedCompany(
                        ticker=ticker,
                        related_ticker=related_ticker,
                        relationship_type=company.get("relationship_type"),
                        correlation_score=company.get("similarity_score", 0.0),
                        last_updated=datetime.now(),
                        fetched_at=datetime.now(),
                        extended_data=company.get("extended_data", {})
                    )
                    
                    await relationship.insert()
                    saved_count += 1
            
            except Exception as e:
                logger.error(
                    f"Failed to save relationship {ticker} -> {company.get('ticker')}",
                    extra={
                        "ticker": ticker,
                        "related_ticker": company.get("ticker"),
                        "error": str(e)
                    },
                    exc_info=True
                )
                # Continue with next relationship
        
        return saved_count
    
    def get_job_status(self) -> Dict:
        """
        Get current job status and statistics.
        
        Returns:
            Dictionary with job status information
        """
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_tickers_processed": self.total_tickers_processed,
            "total_relationships_found": self.total_relationships_found,
            "average_relationships_per_ticker": (
                self.total_relationships_found / self.total_tickers_processed
                if self.total_tickers_processed > 0
                else 0
            )
        }


# Singleton instance for job scheduler
related_tickers_collector_job = RelatedTickersCollectorJob()


# Pure function for testable core logic
async def collect_related_companies_for_ticker(ticker: str) -> Optional[List[Dict]]:
    """
    Fetch and save related companies for a single ticker.
    
    Pure function - testable core business logic separated from job infrastructure.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        List of related company dictionaries or None if failed
        
    Example:
        >>> related = await collect_related_companies_for_ticker("AAPL")
        >>> print(len(related))  # Number of relationships found
        8
    """
    try:
        # Fetch from MASSIVE API
        related_data = await massive_provider.fetch_related_companies(ticker)
        
        if not related_data:
            logger.info(f"No related companies found for {ticker}")
            return None
        
        # Save to database
        saved_relationships = []
        
        for company in related_data:
            related_ticker = company.get("ticker")
            if not related_ticker:
                continue
            
            # Check if already exists
            existing = await RelatedCompany.find_one(
                RelatedCompany.ticker == ticker,
                RelatedCompany.related_ticker == related_ticker
            )
            
            if existing:
                # Update
                existing.relationship_type = company.get("relationship_type")
                existing.correlation_score = company.get("similarity_score")
                existing.last_updated = datetime.now()
                existing.extended_data = company.get("extended_data", {})
                await existing.save()
            else:
                # Insert
                relationship = RelatedCompany(
                    ticker=ticker,
                    related_ticker=related_ticker,
                    relationship_type=company.get("relationship_type"),
                    correlation_score=company.get("similarity_score", 0.0),
                    last_updated=datetime.now(),
                    fetched_at=datetime.now(),
                    extended_data=company.get("extended_data", {})
                )
                await relationship.insert()
            
            saved_relationships.append(company)
        
        logger.info(
            f"Saved {len(saved_relationships)} relationships for {ticker}",
            extra={"ticker": ticker, "count": len(saved_relationships)}
        )
        
        return saved_relationships
    
    except Exception as e:
        logger.error(
            f"Failed to collect related companies for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return None
