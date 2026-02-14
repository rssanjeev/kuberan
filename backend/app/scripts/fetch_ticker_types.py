"""
One-time script to fetch and cache ticker types from MASSIVE API.

Run this script once during initial setup to populate the ticker_types collection.
Ticker types rarely change, so this data can be cached permanently.

Usage:
    docker exec kuberan-backend-1 python3 -m app.scripts.fetch_ticker_types

Expected Output:
    - Fetches 15-20 ticker types from MASSIVE API
    - Stores in ticker_types MongoDB collection
    - Displays summary of stored types

Ticker Types Fetched:
    - CS: Common Stock
    - ETF: Exchange Traded Fund
    - ADRC: American Depository Receipt Common
    - PFD: Preferred Stock
    - WARRANT: Warrant
    - RIGHT: Rights
    - UNIT: Unit
    - FUND: Mutual Fund
    - INDEX: Index
    - ETN: Exchange Traded Note
    - And more...
"""

import asyncio
import sys
from datetime import datetime

# Database initialization
async def init_db():
    """Initialize database connection."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie
    from app.models import DOCUMENT_MODELS
    import os
    
    # Get MongoDB URL from environment
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    database_name = os.getenv("DATABASE_NAME", "kuberan")
    
    # Create Motor client
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    # Initialize Beanie with document models
    await init_beanie(database=database, document_models=DOCUMENT_MODELS)
    
    print(f"✅ Connected to MongoDB: {mongodb_url}/{database_name}")


async def main():
    """Main script execution."""
    print("=" * 80)
    print("MASSIVE Ticker Types Fetch Script")
    print("=" * 80)
    print()
    
    # Initialize database
    print("Initializing database connection...")
    await init_db()
    print()
    
    # Import services after database initialization
    from app.services.providers.implementations.massive_provider import MassiveProvider
    from app.services.ticker_type_service import ticker_type_service
    from app.core.logging_config import get_logger
    import os
    
    logger = get_logger(__name__)
    
    # Get API key from environment (MASSIVE_KEY is the environment variable)
    api_key = os.getenv("MASSIVE_KEY")
    if not api_key:
        print("❌ ERROR: MASSIVE_KEY environment variable not set")
        print("   Set in docker-compose.yml or .env file")
        sys.exit(1)
    
    print(f"✅ API key configured: {api_key[:10]}...")
    print()
    
    # Initialize MASSIVE provider
    print("Initializing MASSIVE provider...")
    provider = MassiveProvider(api_key=api_key)
    print("✅ Provider initialized")
    print()
    
    # Fetch and store ticker types
    print("Fetching ticker types from MASSIVE API...")
    print("  Endpoint: GET /v3/reference/tickers/types")
    print("  Filters: asset_class=stocks, locale=us")
    print()
    
    try:
        count = await ticker_type_service.fetch_and_store_types(
            provider=provider,
            asset_class="stocks",
            locale="us"
        )
        
        print(f"✅ Successfully stored {count} ticker types")
        print()
        
        # Display stored types
        print("Stored ticker types:")
        print("-" * 80)
        types = await ticker_type_service.get_types()
        
        for t in sorted(types, key=lambda x: x.code):
            print(f"  {t.code:10s} - {t.description:40s} [{t.asset_class}/{t.locale}]")
        
        print("-" * 80)
        print()
        
        # Summary
        print("Summary:")
        print(f"  Total types stored: {len(types)}")
        print(f"  Collection: ticker_types")
        print(f"  Fetched at: {datetime.utcnow().isoformat()}Z")
        print()
        
        print("=" * 80)
        print("✅ SUCCESS: Ticker types fetch complete")
        print("=" * 80)
        
    except Exception as e:
        logger.error(
            "Failed to fetch ticker types",
            extra={"error": str(e)},
            exc_info=True
        )
        print()
        print("=" * 80)
        print("❌ ERROR: Ticker types fetch failed")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("Check logs for details:")
        print("  docker logs kuberan-backend-1 --tail 50")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
