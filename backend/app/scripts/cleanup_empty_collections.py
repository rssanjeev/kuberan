"""
MongoDB Collection Cleanup Script

Removes all empty collections from the kuberan database to optimize storage
and reduce clutter. Only deletes collections with 0 documents.

Created: December 10, 2025
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# MongoDB connection
MONGODB_URL = "mongodb://mongodb:27017"
DATABASE_NAME = "kuberan"

# Collections to delete (all have 0 documents)
EMPTY_COLLECTIONS_TO_DELETE = [
    # Timeseries collections (never used)
    "option_chains",
    "system.buckets.option_chains",
    "futures_contracts",
    "system.buckets.futures_contracts",
    "economic_indicators",
    "system.buckets.economic_indicators",
    "commodity_prices",
    "system.buckets.commodity_prices",
    "rate_limit_status",
    "system.buckets.rate_limit_status",
    "stock_quotes",
    "system.buckets.stock_quotes",
    "market_indicators",
    "system.buckets.market_indicators",
    "crypto_prices",
    "system.buckets.crypto_prices",
    "forex_rates",
    "system.buckets.forex_rates",
    "provider_health_checks",
    "system.buckets.provider_health_checks",
    "sentiment_analyses",
    "system.buckets.sentiment_analyses",
    "intraday_prices",
    "system.buckets.intraday_prices",
    "technical_indicators",
    "system.buckets.technical_indicators",
    
    # Regular collections (never used)
    "analyst_ratings",
    "news_articles",
    "user_watchlists",
    "stock_earnings",
    "price_targets",
    "provider_daily_stats",
    "stock_metadata",
    "stock_splits",
]

# Collections to review (have some data, might be test data)
REVIEW_COLLECTIONS = [
    "etf_comparisons",  # 2 docs - test data
    "famous_investor_portfolios",  # 5 docs - small dataset
]


async def cleanup_collections(delete_review_collections: bool = False):
    """
    Delete empty collections from MongoDB.
    
    Args:
        delete_review_collections: If True, also delete collections that need review
    """
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        logger.info("Starting collection cleanup")
        
        # Get all existing collections
        all_collections = await db.list_collection_names()
        logger.info(f"Found {len(all_collections)} total collections")
        
        deleted_count = 0
        skipped_count = 0
        
        # Delete empty collections
        collections_to_process = EMPTY_COLLECTIONS_TO_DELETE.copy()
        if delete_review_collections:
            collections_to_process.extend(REVIEW_COLLECTIONS)
            logger.info("Will also delete review collections")
        
        for collection_name in collections_to_process:
            if collection_name in all_collections:
                # Verify it's actually empty before deleting
                count = await db[collection_name].count_documents({})
                
                if count == 0 or delete_review_collections:
                    await db[collection_name].drop()
                    deleted_count += 1
                    logger.info(
                        f"Deleted collection: {collection_name}",
                        extra={"collection": collection_name, "document_count": count}
                    )
                else:
                    skipped_count += 1
                    logger.warning(
                        f"Skipped collection (not empty): {collection_name}",
                        extra={"collection": collection_name, "document_count": count}
                    )
            else:
                logger.debug(
                    f"Collection does not exist: {collection_name}",
                    extra={"collection": collection_name}
                )
        
        # Final summary
        remaining_collections = await db.list_collection_names()
        
        logger.info(
            "Collection cleanup completed",
            extra={
                "deleted": deleted_count,
                "skipped": skipped_count,
                "remaining": len(remaining_collections),
                "collections_remaining": remaining_collections
            }
        )
        
        # Show remaining collection counts
        print("\n" + "="*80)
        print("REMAINING COLLECTIONS")
        print("="*80)
        
        for collection_name in sorted(remaining_collections):
            if not collection_name.startswith("system."):
                count = await db[collection_name].count_documents({})
                print(f"{collection_name:40s} : {count:,}")
        
        print("="*80)
        print(f"\n✓ Deleted {deleted_count} collections")
        print(f"✓ {len(remaining_collections)} collections remaining")
        print(f"✓ Skipped {skipped_count} non-empty collections")
        
    except Exception as e:
        logger.error(
            "Collection cleanup failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise
    
    finally:
        client.close()


async def main():
    """Main execution."""
    import sys
    
    print("\n" + "="*80)
    print("MongoDB Collection Cleanup Script")
    print("="*80)
    print("\nThis will delete ALL empty collections from the database.")
    print("\nEmpty collections to delete:")
    for col in EMPTY_COLLECTIONS_TO_DELETE:
        print(f"  - {col}")
    
    print("\nCollections with data (will NOT delete unless forced):")
    for col in REVIEW_COLLECTIONS:
        print(f"  - {col}")
    
    print("\n" + "="*80)
    
    # Check for force flag
    delete_review = "--force" in sys.argv or "--delete-review" in sys.argv
    
    if delete_review:
        print("⚠️  WARNING: --force flag detected")
        print("⚠️  This will also delete collections with test data!")
        print("\nPress Ctrl+C to cancel, or wait 5 seconds to proceed...")
        await asyncio.sleep(5)
    else:
        print("Run with --force to also delete review collections")
        print("\nProceeding to delete empty collections only...")
        await asyncio.sleep(2)
    
    await cleanup_collections(delete_review_collections=delete_review)


if __name__ == "__main__":
    asyncio.run(main())
