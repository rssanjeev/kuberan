"""
Job registry - registers all scheduled jobs with the centralized scheduler.
"""
from apscheduler.triggers.cron import CronTrigger
from app.services.scheduler.scheduler import job_scheduler
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_all_jobs():
    """
    Register all scheduled jobs with the centralized scheduler.
    Called once during application startup.
    
    SYSTEM 2 ONLY: Comprehensive NYSE/NASDAQ collection
    - Metadata enrichment (Alpha Vantage)
    - Incremental batch collection (YFinance)
    - Precious metals collection
    
    DISABLED: System 1 (Watchlist price collection for 7 tickers)
    """
    # Import jobs here to avoid circular imports
    from app.services.jobs.metals_price_collector import metals_price_collector_job
    from app.services.jobs.metadata_collector import metadata_collector_job
    from app.services.jobs.massive_foundation_builder import massive_foundation_builder_job
    
    # ============================================================================
    # SYSTEM 1: DISABLED - Watchlist Price Collection (7 tickers)
    # ============================================================================
    # Disabled per user request - focusing only on comprehensive NYSE collection
    
    # # Price collection: Every 60 seconds, 9 AM - 5 PM EST, Mon-Fri
    # job_scheduler.add_job(
    #     func=price_collector_job.run,
    #     trigger=CronTrigger(
    #         day_of_week='mon-fri',
    #         hour='9-16',
    #         minute='*',
    #         second='0',
    #         timezone='US/Eastern'
    #     ),
    #     job_id='price_collector',
    #     name='Stock Price Collection'
    # )
    
    # # Market close poll: Once at 5:00 PM EST
    # job_scheduler.add_job(
    #     func=price_collector_job.run,
    #     trigger=CronTrigger(
    #         day_of_week='mon-fri',
    #         hour='17',
    #         minute='0',
    #         second='0',
    #         timezone='US/Eastern'
    #     ),
    #     job_id='market_close_poll',
    #     name='Market Close Price Poll'
    # )
    
    # ============================================================================
    # SYSTEM 2: ACTIVE - Comprehensive NYSE/NASDAQ Collection
    # ============================================================================
    
    # Precious metals collection: Once daily at 10:00 AM IST (all days)
    job_scheduler.add_job(
        func=metals_price_collector_job.run,
        trigger=CronTrigger(
            hour='10',              # 10 AM
            minute='0',             # At the start of the hour
            second='0',
            timezone='Asia/Kolkata'  # IST timezone
        ),
        job_id='metals_price_collector',
        name='Precious Metals Price Collection'
    )
    
    # Metadata enrichment: Daily at 2:00 AM EST (Alpha Vantage free tier: 25 calls/day)
    # Processes 5 tickers per run to stay within limits
    job_scheduler.add_job(
        func=metadata_collector_job.run_enrichment_cycle,
        trigger=CronTrigger(
            hour='2',               # 2 AM
            minute='0',             # At the start of the hour
            second='0',
            timezone='US/Eastern'   # EST timezone
        ),
        job_id='metadata_enrichment',
        name='Stock Metadata Enrichment (Alpha Vantage)'
    )
    
    # Incremental metadata collection: Every 15 minutes
    # 100 tickers per batch * 4 times/hour * 24 hours = 9,600 tickers/day
    # This ensures we feed the Foundation Builder (7,200/day) fast enough
    job_scheduler.add_job(
        func=metadata_collector_job.run_incremental_batch_collection,
        trigger=CronTrigger(
            minute='*/15',  # Every 15 minutes (0, 15, 30, 45)
            second='0',
            timezone='US/Eastern'
        ),
        job_id='incremental_collection_15min',
        name='Incremental Metadata Collection (Every 15 min)'
    )
    
    # ============================================================================
    # MASSIVE Foundation Builder: Continuous Per-Minute Collection via Polygon.io
    # ============================================================================
    # Purpose: Collect foundational metadata (CIK, FIGI, logos, etc.) for all tickers
    # Rate: 5 calls/min (Polygon.io free tier limit)
    # Schedule: Every minute, processing 5 tickers per run
    # Throughput: 300 tickers/hour = 7,200 tickers/day
    # Target: Complete 1,066 tickers in ~4 hours
    # Benefits: Frequent updates, better rate limit adherence, no artificial delays
    
    job_scheduler.add_job(
        func=massive_foundation_builder_job.run,
        trigger=CronTrigger(
            minute='*',  # Every minute
            second='0',
            timezone='US/Eastern'  # EST/EDT timezone
        ),
        job_id='massive_foundation_per_minute',
        name='MASSIVE Foundation Collection (Every Minute)'
    )
    
    logger.info(
        f"Registered {len(job_scheduler.jobs)} scheduled jobs",
        extra={"job_count": len(job_scheduler.jobs)}
    )


def unregister_all_jobs():
    """Unregister all jobs (useful for testing)."""
    job_ids = list(job_scheduler.jobs.keys())
    for job_id in job_ids:
        job_scheduler.remove_job(job_id)
