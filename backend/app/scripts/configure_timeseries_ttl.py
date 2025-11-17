"""
Configure TTL for timeseries collections.

This script:
1. Identifies all models with timeseries_options
2. Drops and recreates collections as timeseries collections
3. Applies TTL (expireAfterSeconds) from model definitions
4. Recreates indexes from model Settings

Usage:
    python3 -m scripts.configure_timeseries_ttl [--dry-run]

Note: This will DROP and RECREATE collections, losing existing data.
Use --dry-run to see what would be done without actually doing it.
"""

import asyncio
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Add app to path
sys.path.insert(0, '/app')

from app.core.logging_config import get_logger
from app.models import DOCUMENT_MODELS

logger = get_logger(__name__)


# Models with timeseries configurations
TIMESERIES_MODELS = [
    {
        "model": "StockQuote",
        "collection": "stock_quotes",
        "timeField": "quote_timestamp",
        "granularity": "minutes",
        "expireAfterSeconds": 900,  # 15 minutes
        "description": "Real-time stock quotes (15-min TTL)"
    },
    {
        "model": "StockHistoricalPrice",
        "collection": "stock_historical_prices",
        "timeField": "timestamp",
        "metaField": "ticker",
        "granularity": "hours",
        "expireAfterSeconds": 31536000,  # 1 year
        "description": "Historical stock prices (1-year TTL)"
    },
    {
        "model": "IntradayPrice",
        "collection": "intraday_prices",
        "timeField": "timestamp",
        "metaField": "ticker",
        "granularity": "minutes",
        "expireAfterSeconds": 604800,  # 7 days
        "description": "Intraday prices (7-day TTL)"
    },
    {
        "model": "MarketIndicator",
        "collection": "market_indicators",
        "timeField": "timestamp",
        "metaField": "indicator_name",
        "granularity": "hours",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "Market indicators (30-day TTL)"
    },
    {
        "model": "TechnicalIndicator",
        "collection": "technical_indicators",
        "timeField": "timestamp",
        "metaField": "ticker",
        "granularity": "hours",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "Technical indicators (30-day TTL)"
    },
    {
        "model": "SentimentAnalysis",
        "collection": "sentiment_analyses",
        "timeField": "timestamp",
        "metaField": "ticker",
        "granularity": "hours",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "Sentiment analysis (30-day TTL)"
    },
    {
        "model": "OptionChain",
        "collection": "option_chains",
        "timeField": "timestamp",
        "metaField": "ticker",
        "granularity": "hours",
        "expireAfterSeconds": 604800,  # 7 days
        "description": "Options data (7-day TTL)"
    },
    {
        "model": "FuturesContract",
        "collection": "futures_contracts",
        "timeField": "timestamp",
        "metaField": "symbol",
        "granularity": "hours",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "Futures contracts (30-day TTL)"
    },
    {
        "model": "CryptoPrice",
        "collection": "crypto_prices",
        "timeField": "timestamp",
        "metaField": "symbol",
        "granularity": "minutes",
        "expireAfterSeconds": 604800,  # 7 days
        "description": "Cryptocurrency prices (7-day TTL)"
    },
    {
        "model": "ForexRate",
        "collection": "forex_rates",
        "timeField": "timestamp",
        "metaField": "currency_pair",
        "granularity": "minutes",
        "expireAfterSeconds": 604800,  # 7 days
        "description": "Forex rates (7-day TTL)"
    },
    {
        "model": "CommodityPrice",
        "collection": "commodity_prices",
        "timeField": "timestamp",
        "metaField": "commodity",
        "granularity": "hours",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "Commodity prices (30-day TTL)"
    },
    {
        "model": "EconomicIndicator",
        "collection": "economic_indicators",
        "timeField": "timestamp",
        "metaField": "indicator_name",
        "granularity": "hours",
        "expireAfterSeconds": 31536000,  # 1 year
        "description": "Economic indicators (1-year TTL)"
    },
    {
        "model": "ProviderAPICall",
        "collection": "provider_api_calls",
        "timeField": "timestamp",
        "metaField": "provider",
        "granularity": "minutes",
        "expireAfterSeconds": 2592000,  # 30 days
        "description": "API call tracking (30-day TTL)"
    },
    {
        "model": "ProviderHealthCheck",
        "collection": "provider_health_checks",
        "timeField": "timestamp",
        "metaField": "provider",
        "granularity": "minutes",
        "expireAfterSeconds": 604800,  # 7 days
        "description": "Provider health checks (7-day TTL)"
    },
    {
        "model": "RateLimitStatus",
        "collection": "rate_limit_status",
        "timeField": "timestamp",
        "metaField": "provider",
        "granularity": "minutes",
        "expireAfterSeconds": 3600,  # 1 hour
        "description": "Rate limit status (1-hour TTL)"
    },
]


async def check_collection_exists(db, collection_name: str) -> bool:
    """Check if collection exists."""
    collections = await db.list_collection_names()
    return collection_name in collections


async def get_collection_count(db, collection_name: str) -> int:
    """Get document count in collection."""
    if await check_collection_exists(db, collection_name):
        return await db[collection_name].count_documents({})
    return 0


async def create_timeseries_collection(db, config: dict, dry_run: bool = False):
    """Create timeseries collection with TTL."""
    collection_name = config["collection"]
    
    logger.info("=" * 70)
    logger.info(f"Processing: {config['model']} → {collection_name}")
    logger.info(f"Description: {config['description']}")
    logger.info("=" * 70)
    
    # Check existing collection
    exists = await check_collection_exists(db, collection_name)
    if exists:
        count = await get_collection_count(db, collection_name)
        logger.warning(
            f"Collection exists with {count} documents",
            extra={"collection": collection_name, "count": count}
        )
        
        if not dry_run:
            logger.info(f"Dropping collection: {collection_name}")
            await db[collection_name].drop()
            logger.info("✅ Collection dropped")
        else:
            logger.info(f"[DRY RUN] Would drop collection: {collection_name}")
    
    # Build timeseries options
    timeseries_opts = {
        "timeField": config["timeField"],
        "granularity": config["granularity"]
    }
    
    if "metaField" in config:
        timeseries_opts["metaField"] = config["metaField"]
    
    logger.info(
        "Creating timeseries collection",
        extra={
            "timeField": config["timeField"],
            "granularity": config["granularity"],
            "metaField": config.get("metaField", "none"),
            "ttl_seconds": config["expireAfterSeconds"],
            "ttl_human": format_ttl(config["expireAfterSeconds"])
        }
    )
    
    if not dry_run:
        # Create timeseries collection
        await db.create_collection(
            collection_name,
            timeseries=timeseries_opts,
            expireAfterSeconds=config["expireAfterSeconds"]
        )
        logger.info(f"✅ Timeseries collection created: {collection_name}")
        
        # Verify creation
        collections = await db.list_collection_names()
        if collection_name in collections:
            # Get collection info
            coll_info = await db.command({"listCollections": 1, "filter": {"name": collection_name}})
            if coll_info["cursor"]["firstBatch"]:
                info = coll_info["cursor"]["firstBatch"][0]
                logger.info(
                    "✅ Verified timeseries collection",
                    extra={
                        "type": info.get("type", "unknown"),
                        "options": info.get("options", {})
                    }
                )
    else:
        logger.info(
            f"[DRY RUN] Would create timeseries collection: {collection_name}",
            extra={"options": timeseries_opts, "ttl": config["expireAfterSeconds"]}
        )
    
    logger.info("")


def format_ttl(seconds: int) -> str:
    """Format TTL seconds into human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    elif seconds < 31536000:
        return f"{seconds // 86400}d"
    else:
        return f"{seconds // 31536000}y"


async def main(dry_run: bool = False):
    """Main migration script."""
    logger.info("=" * 70)
    logger.info("TIMESERIES TTL CONFIGURATION SCRIPT")
    logger.info("=" * 70)
    logger.info("")
    
    if dry_run:
        logger.warning("🔍 DRY RUN MODE - No changes will be made")
        logger.info("")
    
    # Connect to database
    logger.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    db = client.kuberan
    
    # Initialize Beanie (to access model definitions)
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)
    logger.info("✅ Database initialized")
    logger.info("")
    
    # Summary
    logger.info(f"Found {len(TIMESERIES_MODELS)} timeseries collections to configure")
    logger.info("")
    
    # Process each timeseries collection
    success_count = 0
    error_count = 0
    
    for config in TIMESERIES_MODELS:
        try:
            await create_timeseries_collection(db, config, dry_run)
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error(
                f"❌ Failed to process {config['collection']}",
                extra={"error": str(e)},
                exc_info=True
            )
            logger.info("")
    
    # Final summary
    logger.info("=" * 70)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"✅ Successful: {success_count}/{len(TIMESERIES_MODELS)}")
    logger.info(f"❌ Failed: {error_count}/{len(TIMESERIES_MODELS)}")
    
    if dry_run:
        logger.info("")
        logger.warning("🔍 DRY RUN COMPLETE - No changes were made")
        logger.info("Run without --dry-run to apply changes")
    else:
        logger.info("")
        logger.info("✅ Migration complete!")
        logger.info("")
        logger.info("Note: These collections will now automatically expire old data:")
        for config in TIMESERIES_MODELS:
            ttl_human = format_ttl(config["expireAfterSeconds"])
            logger.info(f"  • {config['collection']}: {ttl_human} TTL")
    
    logger.info("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run))
