"""
Financials Collector Job

PHASE 5: Quarterly collection of financial statements for tracked tickers.

⚠️ URGENT: Endpoint deprecated - will be removed February 23, 2026 (79 days remaining)

This job fetches financial statements (income statement, balance sheet, cash flow)
from MASSIVE API and stores them in the FinancialStatement collection. Critical for
archiving financial data before endpoint deprecation.

Schedule: Quarterly (after earnings seasons: Feb, May, Aug, Nov)
Initial Target: S&P 500 2-year historical backfill (12,000 calls)
Rate Budget: 7,200 calls/day max (backfill requires ~1.7 days for S&P 500)

Migration Plan: After Feb 23, 2026, migrate to Alpha Vantage or SEC EDGAR API

SECURITY: Financial data is public company information. No sensitive data stored.

Created: December 5, 2025 (Phase 5 implementation)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.logging_config import get_logger
from app.models.provider import FinancialStatement, DataSource
from app.services.providers.implementations.massive_provider import massive_provider

logger = get_logger(__name__)


class FinancialsCollectorJob:
    """
    Background job to collect financial statements for tracked tickers.
    
    Implementation Pattern: Hybrid functional/OOP
    - Pure function: collect_financials_for_ticker (testable core logic)
    - Job class: Manages scheduling, state, and statistics (lifecycle)
    
    Features:
    - S&P 500 priority (largest companies first)
    - 2-year historical backfill (8 quarters or 2 annual reports)
    - Rate limiting (12 seconds between calls = 5 calls/min)
    - Upsert logic (update existing statements)
    - Statistics tracking (processed, statements saved, errors)
    
    Deprecation Strategy:
    - Complete S&P 500 backfill before Feb 23, 2026
    - Archive complete dataset to JSON/CSV
    - Migrate to Alpha Vantage Fundamentals API after deprecation
    """
    
    def __init__(self):
        """Initialize job with state tracking."""
        self.last_run: Optional[datetime] = None
        self.total_tickers_processed: int = 0
        self.total_statements_saved: int = 0
        self.is_running: bool = False
        self.backfill_mode: bool = False  # Toggle for historical backfill
    
    async def run(self, backfill: bool = False, limit: Optional[int] = None):
        """
        Main job execution: Fetch financial statements for tickers.
        
        Args:
            backfill: If True, fetch 2-year history. If False, fetch latest only.
            limit: Limit number of tickers to process (for testing or controlled backfill)
        
        Process:
        1. Get high-priority tickers (S&P 500, high market cap)
        2. For each ticker, fetch financial statements from MASSIVE
        3. Save FinancialStatement records (upsert on ticker+fiscal_date_ending)
        4. Track statistics and handle errors
        5. Update job state
        """
        if self.is_running:
            logger.warning("Financials collector already running, skipping")
            return
        
        self.is_running = True
        self.backfill_mode = backfill
        start_time = datetime.now()
        
        logger.info(
            f"Starting financials collection job (backfill={backfill})",
            extra={"backfill": backfill, "limit": limit}
        )
        
        try:
            # Get high-priority tickers (S&P 500, high market cap)
            target_count = limit if limit else (500 if backfill else 100)
            tickers = await self._get_priority_tickers(limit=target_count)
            
            if not tickers:
                logger.warning("No tickers found for financials collection")
                return
            
            logger.info(
                f"Loaded {len(tickers)} tickers for financials collection",
                extra={"ticker_count": len(tickers), "backfill": backfill}
            )
            
            # Statistics
            processed = 0
            statements_saved = 0
            errors = 0
            skipped = 0
            
            # Process each ticker with rate limiting
            for ticker_obj in tickers:
                ticker = ticker_obj.ticker
                
                try:
                    # Fetch both annual and quarterly statements
                    if backfill:
                        # Historical backfill: 2 years of quarterly + annual
                        annual_data = await massive_provider.fetch_financials(
                            ticker=ticker,
                            timeframe="annual",
                            limit=2
                        )
                        
                        # Rate limiting between calls
                        await asyncio.sleep(12)
                        
                        quarterly_data = await massive_provider.fetch_financials(
                            ticker=ticker,
                            timeframe="quarterly",
                            limit=8
                        )
                        
                        # Combine results
                        financial_data = []
                        if annual_data:
                            financial_data.extend(annual_data)
                        if quarterly_data:
                            financial_data.extend(quarterly_data)
                    else:
                        # Latest only: Just fetch most recent annual
                        financial_data = await massive_provider.fetch_financials(
                            ticker=ticker,
                            timeframe="annual",
                            limit=1
                        )
                    
                    if financial_data:
                        # Save each financial statement
                        saved_count = await self._save_financial_statements(
                            ticker=ticker,
                            financial_data=financial_data
                        )
                        
                        processed += 1
                        statements_saved += saved_count
                        
                        logger.info(
                            f"Saved {saved_count} financial statements for {ticker}",
                            extra={
                                "ticker": ticker,
                                "statements": saved_count,
                                "backfill": backfill
                            }
                        )
                    else:
                        # No financial data found (404 response)
                        skipped += 1
                        logger.debug(
                            f"No financial data found for {ticker}",
                            extra={"ticker": ticker}
                        )
                    
                    # Rate limiting: 12 seconds between tickers = 5 calls/min
                    await asyncio.sleep(12)
                
                except Exception as e:
                    errors += 1
                    logger.error(
                        f"Failed to collect financials for {ticker}",
                        extra={"ticker": ticker, "error": str(e)},
                        exc_info=True
                    )
                    # Continue with next ticker
            
            # Update job state
            self.last_run = datetime.now()
            self.total_tickers_processed += processed
            self.total_statements_saved += statements_saved
            
            # Log summary
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Financials collection completed in {duration:.1f}s",
                extra={
                    "processed": processed,
                    "statements_saved": statements_saved,
                    "skipped": skipped,
                    "errors": errors,
                    "duration_seconds": duration,
                    "backfill": backfill
                }
            )
        
        except Exception as e:
            logger.error(
                "Financials collection job failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
        
        finally:
            self.is_running = False
    
    async def _get_priority_tickers(self, limit: int = 500) -> List:
        """
        Get high-priority tickers for financial statement collection.
        
        Priority order:
        1. S&P 500 companies (largest market cap)
        2. User watchlist tickers
        3. High market cap stocks
        4. Recently IPO'd companies
        
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
    
    async def _save_financial_statements(
        self,
        ticker: str,
        financial_data: List[Dict]
    ) -> int:
        """
        Save financial statements to database.
        
        Uses upsert logic: Update if statement exists, insert if new.
        
        Args:
            ticker: Stock ticker symbol
            financial_data: List of financial statement dictionaries from MASSIVE
            
        Returns:
            Number of statements saved
        """
        saved_count = 0
        
        for statement in financial_data:
            try:
                fiscal_date_ending = statement.get("fiscal_date_ending")
                fiscal_period = statement.get("fiscal_period")
                
                if not fiscal_date_ending:
                    logger.warning(
                        f"Skipping statement without fiscal_date_ending",
                        extra={"ticker": ticker}
                    )
                    continue
                
                # Check if statement already exists
                existing = await FinancialStatement.find_one(
                    FinancialStatement.ticker == ticker,
                    FinancialStatement.fiscal_date_ending == fiscal_date_ending,
                    FinancialStatement.fiscal_period == fiscal_period
                )
                
                # Determine statement type (annual vs quarterly)
                timeframe = statement.get("timeframe", "annual")
                
                # Extract common metrics for easy querying
                income = statement.get("income_statement", {})
                balance = statement.get("balance_sheet", {})
                cash_flow = statement.get("cash_flow_statement", {})
                
                common_metrics = {
                    "revenue": income.get("revenues"),
                    "net_income": income.get("net_income"),
                    "total_assets": balance.get("total_assets"),
                    "total_liabilities": balance.get("total_liabilities"),
                    "shareholders_equity": balance.get("total_equity"),
                    "operating_cash_flow": cash_flow.get("operating_cash_flow")
                }
                
                if existing:
                    # Update existing statement
                    existing.fiscal_year = statement.get("fiscal_year")
                    existing.filing_date = statement.get("filing_date")
                    existing.data = statement  # Store complete statement
                    existing.common_metrics = common_metrics
                    existing.last_updated = datetime.now()
                    
                    await existing.save()
                    saved_count += 1
                else:
                    # Create new statement
                    financial_stmt = FinancialStatement(
                        ticker=ticker,
                        fiscal_period=fiscal_period,
                        fiscal_year=statement.get("fiscal_year"),
                        fiscal_date_ending=fiscal_date_ending,
                        filing_date=statement.get("filing_date"),
                        statement_type=timeframe,  # annual or quarterly
                        data=statement,  # Store complete statement
                        common_metrics=common_metrics,
                        source_provider=DataSource.POLYGON,  # MASSIVE uses Polygon
                        fetched_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    
                    await financial_stmt.insert()
                    saved_count += 1
            
            except Exception as e:
                logger.error(
                    f"Failed to save financial statement for {ticker}",
                    extra={
                        "ticker": ticker,
                        "fiscal_date": statement.get("fiscal_date_ending"),
                        "error": str(e)
                    },
                    exc_info=True
                )
                # Continue with next statement
        
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
            "total_statements_saved": self.total_statements_saved,
            "average_statements_per_ticker": (
                self.total_statements_saved / self.total_tickers_processed
                if self.total_tickers_processed > 0
                else 0
            ),
            "backfill_mode": self.backfill_mode,
            "deprecation_deadline": "2026-02-23",
            "days_until_deprecation": (
                datetime(2026, 2, 23) - datetime.now()
            ).days
        }


# Singleton instance for job scheduler
financials_collector_job = FinancialsCollectorJob()


# Pure function for testable core logic
async def collect_financials_for_ticker(
    ticker: str,
    backfill: bool = False
) -> Optional[Dict]:
    """
    Fetch and save financial statements for a single ticker.
    
    Pure function - testable core business logic separated from job infrastructure.
    
    Args:
        ticker: Stock ticker symbol
        backfill: If True, fetch 2-year history. If False, fetch latest only.
        
    Returns:
        Summary dictionary with saved counts or None if failed
        
    Example:
        >>> result = await collect_financials_for_ticker("AAPL", backfill=True)
        >>> print(result['statements_saved'])
        10
    """
    try:
        # Fetch financial data
        if backfill:
            # Get 2 years: annual + quarterly
            annual_data = await massive_provider.fetch_financials(
                ticker=ticker,
                timeframe="annual",
                limit=2
            )
            
            await asyncio.sleep(12)  # Rate limiting
            
            quarterly_data = await massive_provider.fetch_financials(
                ticker=ticker,
                timeframe="quarterly",
                limit=8
            )
            
            financial_data = []
            if annual_data:
                financial_data.extend(annual_data)
            if quarterly_data:
                financial_data.extend(quarterly_data)
        else:
            # Just latest annual
            financial_data = await massive_provider.fetch_financials(
                ticker=ticker,
                timeframe="annual",
                limit=1
            )
        
        if not financial_data:
            logger.info(f"No financial data found for {ticker}")
            return None
        
        # Save to database
        saved_statements = []
        
        for statement in financial_data:
            fiscal_date_ending = statement.get("fiscal_date_ending")
            fiscal_period = statement.get("fiscal_period")
            
            if not fiscal_date_ending:
                continue
            
            # Check if exists
            existing = await FinancialStatement.find_one(
                FinancialStatement.ticker == ticker,
                FinancialStatement.fiscal_date_ending == fiscal_date_ending,
                FinancialStatement.fiscal_period == fiscal_period
            )
            
            # Extract common metrics
            income = statement.get("income_statement", {})
            balance = statement.get("balance_sheet", {})
            cash_flow = statement.get("cash_flow_statement", {})
            
            common_metrics = {
                "revenue": income.get("revenues"),
                "net_income": income.get("net_income"),
                "total_assets": balance.get("total_assets"),
                "total_liabilities": balance.get("total_liabilities"),
                "shareholders_equity": balance.get("total_equity"),
                "operating_cash_flow": cash_flow.get("operating_cash_flow")
            }
            
            if existing:
                # Update
                existing.data = statement
                existing.common_metrics = common_metrics
                existing.last_updated = datetime.now()
                await existing.save()
            else:
                # Insert
                financial_stmt = FinancialStatement(
                    ticker=ticker,
                    fiscal_period=fiscal_period,
                    fiscal_year=statement.get("fiscal_year"),
                    fiscal_date_ending=fiscal_date_ending,
                    filing_date=statement.get("filing_date"),
                    statement_type=statement.get("timeframe", "annual"),
                    data=statement,
                    common_metrics=common_metrics,
                    source_provider=DataSource.POLYGON,
                    fetched_at=datetime.now(),
                    last_updated=datetime.now()
                )
                await financial_stmt.insert()
            
            saved_statements.append(statement)
        
        logger.info(
            f"Saved {len(saved_statements)} statements for {ticker}",
            extra={"ticker": ticker, "count": len(saved_statements), "backfill": backfill}
        )
        
        return {
            "ticker": ticker,
            "statements_saved": len(saved_statements),
            "backfill": backfill
        }
    
    except Exception as e:
        logger.error(
            f"Failed to collect financials for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        return None
