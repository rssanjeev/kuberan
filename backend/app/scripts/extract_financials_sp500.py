"""
S&P 500 Financial Statements Extraction Script

Mission: Archive 2 years of financial data for S&P 500 companies before MASSIVE API deprecation (Feb 23, 2026)

Strategy:
- Extract top 500 companies by market capitalization
- ONE API call per ticker (returns TTM + quarterly + annual in single response)
- Parse 10 statements per ticker (covering 2 years by default)
- Store all 4 financial statement types: income, balance sheet, cash flow, comprehensive income
- 12-second delays between calls (5 calls/min rate limit)
- Resume capability (skip already processed tickers)
- JSON backup for each ticker

Execution Time: ~100 minutes (500 tickers × 12 seconds)

Usage:
    cd /Users/sanjeev/Developer/kuberan
    docker exec -it kuberan-backend-1 python3 -m app.scripts.extract_financials_sp500
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Kuberan imports
import sys
sys.path.insert(0, '/app')

from app.core.logging_config import get_logger
from app.models.provider import FinancialStatement, CompanyOverview
from app.services.providers.implementations.massive_provider import MassiveProvider

logger = get_logger(__name__)


class SP500FinancialsExtractor:
    """Extract financial statements for S&P 500 companies."""
    
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("MASSIVE_KEY")
        if not api_key:
            raise ValueError("MASSIVE_KEY environment variable not set")
        
        self.massive_provider = MassiveProvider(api_key=api_key)
        self.backup_dir = Path("/app/data/financials_backup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_tickers": 0,
            "successful": 0,
            "failed": 0,
            "rate_limit_exhausted": 0,  # NEW: Track rate limit failures
            "skipped": 0,
            "total_statements": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def init_database(self):
        """Initialize MongoDB connection and Beanie."""
        logger.info("Initializing database connection")
        
        client = AsyncIOMotorClient("mongodb://mongodb:27017")
        db = client["kuberan"]
        
        await init_beanie(
            database=db,
            document_models=[CompanyOverview, FinancialStatement]
        )
        
        logger.info("Database initialized successfully")
    
    async def get_sp500_tickers(self) -> List[str]:
        """
        Get S&P 500 tickers ordered by market cap (descending).
        
        Returns:
            List of ticker symbols
        """
        logger.info("Fetching S&P 500 tickers from MongoDB")
        
        # Query top 500 by market cap (assuming this field exists in CompanyOverview)
        companies = await CompanyOverview.find(
            CompanyOverview.enrichment_status == "foundation",
            CompanyOverview.market_cap != None
        ).sort([("market_cap", -1)]).limit(500).to_list()
        
        tickers = [company.ticker for company in companies]
        
        logger.info(
            "Retrieved S&P 500 tickers",
            extra={"count": len(tickers)}
        )
        
        return tickers
    
    async def check_ticker_processed(self, ticker: str) -> bool:
        """
        Check if ticker already has financial statements in MongoDB.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if processed, False otherwise
        """
        # Check if we have any financial statements for this ticker
        existing = await FinancialStatement.find_one(
            FinancialStatement.ticker == ticker
        )
        
        return existing is not None
    
    async def extract_ticker_financials(self, ticker: str, retry_count: int = 0, max_retries: int = 3) -> Optional[Dict]:
        """
        Extract financial statements for a single ticker with retry logic.
        
        Args:
            ticker: Stock ticker symbol
            retry_count: Current retry attempt (0-based)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with extracted data or None if failed after all retries
        """
        logger.info(f"Extracting financials for {ticker}" + (f" (retry {retry_count}/{max_retries})" if retry_count > 0 else ""))
        
        try:
            # Fetch ALL available financial statements (quarterly + annual + TTM)
            # Single API call returns all timeframes (more efficient than 2 separate calls)
            # Limit set to 50 to get ~5+ years of data (typically 10 statements per year)
            
            statements = await self.massive_provider.fetch_financials(
                ticker=ticker,
                timeframe=None,  # Don't filter - get both quarterly and annual
                limit=50  # Increased from 12 to get more historical data
            )
            
            if not statements:
                logger.warning(
                    "No financial data returned for ticker",
                    extra={"ticker": ticker}
                )
                return None
            
            statement_count = len(statements)
            logger.debug(
                f"  - Fetched {statement_count} financial statements (mix of quarterly + annual)"
            )
            
            logger.info(
                "Received financial statements",
                extra={
                    "ticker": ticker,
                    "statement_count": statement_count
                }
            )
            
            # Save JSON backup
            self._save_json_backup(ticker, statements)
            
            # Transform and save to MongoDB
            saved_count = await self._save_statements_to_mongodb(ticker, statements)
            
            logger.info(
                "Successfully processed ticker",
                extra={
                    "ticker": ticker,
                    "statements_received": statement_count,
                    "statements_saved": saved_count
                }
            )
            
            return {
                "ticker": ticker,
                "statement_count": statement_count,
                "saved_count": saved_count,
                "status": "success"
            }
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a rate limit error
            if "rate limit" in error_str or "429" in error_str:
                if retry_count < max_retries:
                    # Exponential backoff: 30s, 60s, 120s
                    wait_time = 30 * (2 ** retry_count)
                    logger.warning(
                        f"⚠️ Rate limit hit for {ticker}, retrying in {wait_time}s (attempt {retry_count + 1}/{max_retries})",
                        extra={"ticker": ticker, "wait_time": wait_time, "retry": retry_count + 1}
                    )
                    await asyncio.sleep(wait_time)
                    return await self.extract_ticker_financials(ticker, retry_count + 1, max_retries)
                else:
                    logger.error(
                        f"❌ Rate limit retry exhausted for {ticker} after {max_retries} attempts",
                        extra={"ticker": ticker, "error": str(e)}
                    )
                    return {"ticker": ticker, "status": "rate_limit_exhausted", "error": str(e)}
            
            # Non-rate-limit error - log and fail
            logger.error(
                "Failed to extract financials for ticker",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return None
    
    def _save_json_backup(self, ticker: str, statements: List[Dict]):
        """Save raw API response to JSON file."""
        backup_file = self.backup_dir / f"{ticker}_financials.json"
        
        try:
            with open(backup_file, 'w') as f:
                json.dump(
                    {
                        "ticker": ticker,
                        "extracted_at": datetime.utcnow().isoformat(),
                        "statements": statements
                    },
                    f,
                    indent=2
                )
            
            logger.debug(
                "Saved JSON backup",
                extra={"ticker": ticker, "file": str(backup_file)}
            )
            
        except Exception as e:
            logger.error(
                "Failed to save JSON backup",
                extra={"ticker": ticker, "error": str(e)}
            )
    
    async def _save_statements_to_mongodb(
        self,
        ticker: str,
        statements: List[Dict]
    ) -> int:
        """
        Transform and save financial statements to MongoDB.
        
        Splits each statement into separate documents for:
        - income statement
        - balance sheet
        - cash flow statement
        
        Args:
            ticker: Stock ticker
            statements: List of statement dicts from API
            
        Returns:
            Number of documents saved
        """
        saved_count = 0
        
        for stmt_data in statements:
            # Extract common metadata
            fiscal_year = int(stmt_data.get("fiscal_year", 0))
            fiscal_date_ending = stmt_data.get("fiscal_date_ending")
            
            # Create separate documents for each statement type
            # Statement types are at TOP LEVEL (income_statement, balance_sheet, cash_flow_statement)
            statement_types = []
            
            # Income Statement (at top level, not under financials)
            if "income_statement" in stmt_data and stmt_data["income_statement"]:
                income_data = stmt_data["income_statement"]
                statement_types.append({
                    "type": "income",
                    "data": income_data,
                    "revenue": income_data.get("revenues"),
                    "net_income": income_data.get("net_income")
                })
            
            # Balance Sheet (at top level)
            if "balance_sheet" in stmt_data and stmt_data["balance_sheet"]:
                balance_data = stmt_data["balance_sheet"]
                statement_types.append({
                    "type": "balance_sheet",
                    "data": balance_data,
                    "total_assets": balance_data.get("total_assets"),
                    "total_liabilities": balance_data.get("total_liabilities"),
                    "shareholders_equity": balance_data.get("stockholders_equity")
                })
            
            # Cash Flow Statement (at top level)
            if "cash_flow_statement" in stmt_data and stmt_data["cash_flow_statement"]:
                cash_flow_data = stmt_data["cash_flow_statement"]
                statement_types.append({
                    "type": "cash_flow",
                    "data": cash_flow_data,
                    "operating_cash_flow": cash_flow_data.get("operating_cash_flow")
                })
            
            # Comprehensive Income Statement (at top level)
            if "comprehensive_income" in stmt_data and stmt_data["comprehensive_income"]:
                comp_income_data = stmt_data["comprehensive_income"]
                statement_types.append({
                    "type": "comprehensive_income",
                    "data": comp_income_data,
                    "comprehensive_income_loss": comp_income_data.get("comprehensive_income_loss"),
                    "other_comprehensive_income_loss": comp_income_data.get("other_comprehensive_income_loss")
                })
            
            # Save each statement type as separate document
            for stmt_type_info in statement_types:
                try:
                    # Extract fiscal period (Q1, Q2, Q3, Q4, FY, TTM)
                    fiscal_period = stmt_data.get("fiscal_period", "FY")
                    timeframe = stmt_data.get("timeframe", "annual")
                    
                    financial_stmt = FinancialStatement(
                        ticker=ticker,
                        statement_type=stmt_type_info["type"],
                        fiscal_year=fiscal_year,
                        fiscal_period=fiscal_period,
                        fiscal_date_ending=fiscal_date_ending,
                        timeframe=timeframe,
                        data=stmt_type_info["data"],
                        revenue=stmt_type_info.get("revenue"),
                        net_income=stmt_type_info.get("net_income"),
                        total_assets=stmt_type_info.get("total_assets"),
                        total_liabilities=stmt_type_info.get("total_liabilities"),
                        shareholders_equity=stmt_type_info.get("shareholders_equity"),
                        operating_cash_flow=stmt_type_info.get("operating_cash_flow"),
                        source_provider="massive"
                    )
                    
                    # Check if exists (match on ticker + type + year + period)
                    existing = await FinancialStatement.find_one(
                        FinancialStatement.ticker == ticker,
                        FinancialStatement.statement_type == stmt_type_info["type"],
                        FinancialStatement.fiscal_year == fiscal_year,
                        FinancialStatement.fiscal_period == fiscal_period
                    )
                    
                    if existing:
                        existing.data = financial_stmt.data
                        existing.revenue = financial_stmt.revenue
                        existing.net_income = financial_stmt.net_income
                        existing.total_assets = financial_stmt.total_assets
                        existing.total_liabilities = financial_stmt.total_liabilities
                        existing.shareholders_equity = financial_stmt.shareholders_equity
                        existing.operating_cash_flow = financial_stmt.operating_cash_flow
                        await existing.save()
                        logger.debug(f"  - Updated: {ticker} {stmt_type_info['type']} FY{fiscal_year}")
                    else:
                        await financial_stmt.insert()
                        logger.debug(f"  - Inserted: {ticker} {stmt_type_info['type']} FY{fiscal_year}")
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(
                        f"Failed to save {stmt_type_info['type']} for {ticker} FY{fiscal_year}",
                        extra={"ticker": ticker, "year": fiscal_year, "error": str(e)},
                        exc_info=True
                    )
        
        return saved_count
    
    async def extract_all(self):
        """Main extraction loop for all S&P 500 tickers."""
        logger.info("🚀 Starting S&P 500 financial statements extraction")
        
        self.stats["start_time"] = datetime.utcnow()
        
        # Initialize database
        await self.init_database()
        
        # Get S&P 500 tickers
        tickers = await self.get_sp500_tickers()
        self.stats["total_tickers"] = len(tickers)
        
        logger.info(
            "S&P 500 extraction started",
            extra={
                "total_tickers": len(tickers),
                "estimated_time_minutes": len(tickers) * 0.2,  # 12 seconds per ticker
                "backup_directory": str(self.backup_dir)
            }
        )
        
        # Process each ticker
        for idx, ticker in enumerate(tickers, start=1):
            # Check if already processed (resume capability)
            if await self.check_ticker_processed(ticker):
                logger.info(
                    f"Ticker already processed, skipping",
                    extra={"ticker": ticker, "progress": f"{idx}/{len(tickers)}"}
                )
                self.stats["skipped"] += 1
                continue
            
            # Extract financials for this ticker (with retry logic)
            result = await self.extract_ticker_financials(ticker)
            
            if result:
                if result.get("status") == "success":
                    self.stats["successful"] += 1
                    self.stats["total_statements"] += result.get("statement_count", 0)
                elif result.get("status") == "rate_limit_exhausted":
                    self.stats["rate_limit_exhausted"] += 1
                    logger.warning(
                        f"⚠️ {ticker} exhausted rate limit retries - will need manual retry",
                        extra={"ticker": ticker}
                    )
                else:
                    self.stats["failed"] += 1
            else:
                self.stats["failed"] += 1
            
            # Progress logging (every 50 tickers)
            if idx % 50 == 0:
                elapsed = (datetime.utcnow() - self.stats["start_time"]).total_seconds()
                avg_time_per_ticker = elapsed / idx
                remaining = len(tickers) - idx
                estimated_remaining = (remaining * avg_time_per_ticker) / 60  # minutes
                
                logger.info(
                    "🔄 Progress update",
                    extra={
                        "progress": f"{idx}/{len(tickers)}",
                        "successful": self.stats["successful"],
                        "failed": self.stats["failed"],
                        "skipped": self.stats["skipped"],
                        "elapsed_minutes": round(elapsed / 60, 1),
                        "estimated_remaining_minutes": round(estimated_remaining, 1)
                    }
                )
            
            # Rate limit: 12-second delay (5 calls/min)
            if idx < len(tickers):  # Don't wait after last ticker
                logger.debug(f"Waiting 12 seconds (rate limit)...")
                await asyncio.sleep(12)
        
        # Final statistics
        self.stats["end_time"] = datetime.utcnow()
        self._print_summary()
    
    def _print_summary(self):
        """Print extraction summary statistics."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info("=" * 80)
        logger.info("✅ S&P 500 FINANCIAL STATEMENTS EXTRACTION COMPLETE")
        logger.info("=" * 80)
        logger.info(
            "Final Statistics",
            extra={
                "total_tickers": self.stats["total_tickers"],
                "successful": self.stats["successful"],
                "rate_limit_exhausted": self.stats["rate_limit_exhausted"],
                "failed": self.stats["failed"],
                "skipped": self.stats["skipped"],
                "total_statements_extracted": self.stats["total_statements"],
                "duration_minutes": round(duration / 60, 1),
                "avg_seconds_per_ticker": round(duration / self.stats["total_tickers"], 1),
                "backup_directory": str(self.backup_dir)
            }
        )
        logger.info("=" * 80)
        
        # Save summary to file
        summary_file = self.backup_dir / f"extraction_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(
                {
                    "extraction_date": datetime.utcnow().isoformat(),
                    "statistics": self.stats,
                    "duration_seconds": duration
                },
                f,
                indent=2,
                default=str  # Handle datetime serialization
            )
        
        logger.info(f"Summary saved to: {summary_file}")


async def main():
    """Main entry point."""
    extractor = SP500FinancialsExtractor()
    await extractor.extract_all()


if __name__ == "__main__":
    asyncio.run(main())
