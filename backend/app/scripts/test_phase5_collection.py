#!/usr/bin/env python3
"""
Test script for Phase 5: Financial Statements Collection

Manually triggers data collection for test tickers to verify the endpoint works.
⚠️ DEPRECATION WARNING: MASSIVE Financials API deprecated February 23, 2026
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import DOCUMENT_MODELS
from app.services.providers.implementations.massive_provider import massive_provider
from app.repositories.stock_repository import stock_repository
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def test_financial_statements():
    """Test financial statements collection for AAPL."""
    
    # Initialize MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db_name = os.getenv("DATABASE_NAME", "kuberan")
    db = client[db_name]
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)
    
    logger.info("⚠️ Testing Phase 5: Financial Statements Collection (DEPRECATED)")
    logger.warning("MASSIVE Financials API will be deprecated on February 23, 2026")
    
    test_ticker = "AAPL"
    
    try:
        logger.info(f"Fetching financial statements for {test_ticker}")
        
        # Fetch from MASSIVE API (backfill mode - multiple statements)
        statements = await massive_provider.fetch_financials(
            ticker=test_ticker,
            timeframe="quarterly",
            limit=4  # Get 4 quarters
        )
        
        if not statements:
            logger.error("No financial statements returned from API")
            return False
        
        logger.info(f"Found {len(statements)} financial statements")
        
        # Save to database
        saved_count = 0
        for statement_data in statements:
            # Add required fields
            statement_data["statement_type"] = "comprehensive"  # All 3 statement types
            statement_data["source_provider"] = "polygon"  # MASSIVE uses Polygon.io
            
            # Convert fiscal_period to fiscal_quarter if needed
            fiscal_period = statement_data.get("fiscal_period")
            if fiscal_period and fiscal_period.startswith("Q"):
                statement_data["fiscal_quarter"] = int(fiscal_period[1])
            
            await stock_repository.save_financial_statement(statement_data)
            saved_count += 1
        
        logger.info(f"Saved {saved_count} financial statements to database")
        
        # Verify retrieval
        retrieved = await stock_repository.get_financial_statements(
            ticker=test_ticker,
            limit=10
        )
        logger.info(f"Retrieved {len(retrieved)} financial statements from database")
        
        if len(retrieved) > 0:
            sample = retrieved[0]
            quarter_str = f"Q{sample.fiscal_quarter}" if sample.fiscal_quarter else "Annual"
            revenue_str = f"${sample.revenue:,.0f}" if sample.revenue else "N/A"
            logger.info(
                f"Sample statement: FY{sample.fiscal_year} {quarter_str} "
                f"(Revenue: {revenue_str})"
            )
            return True
        else:
            logger.error("No financial statements found in database after saving")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_financial_statements())
    sys.exit(0 if success else 1)
