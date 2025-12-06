#!/usr/bin/env python3
"""
Test script for Phase 4: Related Companies Collection

Manually triggers data collection for test tickers to verify the endpoint works.
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


async def test_related_companies():
    """Test related companies collection for AAPL."""
    
    # Initialize MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db_name = os.getenv("DATABASE_NAME", "kuberan")
    db = client[db_name]
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)
    
    logger.info("Testing Phase 4: Related Companies Collection")
    
    test_ticker = "AAPL"
    
    try:
        logger.info(f"Fetching related companies for {test_ticker}")
        
        # Fetch from MASSIVE API
        related = await massive_provider.fetch_related_companies(ticker=test_ticker)
        
        if not related:
            logger.error("No related companies returned from API")
            return False
        
        logger.info(f"Found {len(related)} related companies")
        
        # Transform and save to database
        saved_count = 0
        for company_data in related:
            # Transform to match RelatedCompany model
            transformed = {
                "ticker": test_ticker,  # The base ticker
                "related_ticker": company_data.get("ticker"),  # The related ticker
                "relationship_type": company_data.get("relationship_type", "related"),
                "correlation_score": company_data.get("similarity_score", 0.0),
                "sector_similarity": 1.0 if company_data.get("sector") else None,
                "metadata": {
                    "name": company_data.get("name"),
                    "market_cap": company_data.get("market_cap"),
                    "sector": company_data.get("sector"),
                    "industry": company_data.get("industry")
                }
            }
            await stock_repository.save_related_company(transformed)
            saved_count += 1
        
        logger.info(f"Saved {saved_count} related companies to database")
        
        # Verify retrieval
        retrieved = await stock_repository.get_related_companies(ticker=test_ticker)
        logger.info(f"Retrieved {len(retrieved)} related companies from database")
        
        if len(retrieved) > 0:
            logger.info(f"Sample related company: {retrieved[0].related_ticker} ({retrieved[0].relationship_type})")
            return True
        else:
            logger.error("No related companies found in database after saving")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_related_companies())
    sys.exit(0 if success else 1)
