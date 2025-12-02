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
    
    ============================================================================
    ALL JOBS DISABLED (Dec 1, 2025)
    ============================================================================
    User requested all scheduled jobs to be stopped to prepare for:
    - MASSIVE API provider implementation
    - Migration from Polygon.io to MASSIVE for metadata enrichment
    - Clean slate before new background job architecture
    
    To re-enable jobs:
    1. Uncomment the imports section below
    2. Uncomment desired job registrations
    3. Restart backend container: docker-compose restart backend
    
    Previous jobs (now disabled):
    - metals_price_collector (daily at 10 AM IST)
    - metadata_enrichment (daily at 2 AM EST)
    - incremental_collection_15min (every 15 minutes)
    - massive_foundation_per_minute (every minute)
    ============================================================================
    """
    # # Import jobs here to avoid circular imports
    # from app.services.jobs.metals_price_collector import metals_price_collector_job
    # from app.services.jobs.metadata_collector import metadata_collector_job
    # from app.services.jobs.massive_foundation_builder import massive_foundation_builder_job
    
    # ============================================================================
    # PHASE 1 JOBS: MASSIVE All Tickers Discovery (ENABLED Dec 2, 2025)
    # ============================================================================
    # Three jobs for comprehensive ticker discovery and maintenance:
    # 1. Delta Extractor: Weekly IPO detection using list_date.gte filter
    # 2. Deactivation Detector: Weekly delisting tracking via active field
    # 3. Bi-Annual Refresh: Failsafe full re-scan every 6 months
    #
    # Testing completed Dec 2, 2025:
    # - Delta Extractor: ✅ 12,035 tickers processed, 0 duplicates saved
    # - Deactivation Detector: ✅ 10 tickers checked, 3 inactive detected
    # - Bi-Annual Refresh: ✅ 13 batches processed, full scan successful
    # ============================================================================
    from app.services.jobs.massive_delta_extractor import massive_delta_extractor
    from app.services.jobs.massive_deactivation_detector import massive_deactivation_detector
    from app.services.jobs.massive_biannual_refresh import massive_biannual_refresh
    
    # DELTA EXTRACTOR: Weekly IPO detection (every Monday 2:00 AM EST)
    # Queries MASSIVE API with list_date.gte filter to find new listings
    # First run: 30-day lookback, subsequent: incremental since last run
    # Throughput: 5-20 new IPOs per week, 1-2 API calls, ~12-24 seconds
    job_scheduler.add_job(
        func=massive_delta_extractor.run,
        trigger=CronTrigger(
            day_of_week='mon',      # Monday only
            hour='2',               # 2 AM
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='massive_delta_extraction',
        name='MASSIVE Delta Extraction (Weekly IPO Detection)'
    )
    
    # DEACTIVATION DETECTOR: Weekly delisting check (every Monday 3:00 AM EST)
    # Checks 500 tickers per run for active=false status
    # Full coverage: ~24 weeks for all 12,140 tickers
    # Throughput: 500 API calls at 5/min = ~100 minutes (1.7 hours)
    job_scheduler.add_job(
        func=massive_deactivation_detector.run,
        trigger=CronTrigger(
            day_of_week='mon',      # Monday only
            hour='3',               # 3 AM (after delta extraction)
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='massive_deactivation_detection',
        name='MASSIVE Deactivation Detection (Weekly Delisting Check)'
    )
    
    # BI-ANNUAL REFRESH: Failsafe full re-scan (January 1 & July 1, 4:00 AM EST)
    # Re-runs bulk ticker discovery to catch anything missed by delta extraction
    # Throughput: ~2.5 minutes for 12,000+ tickers, 12-15 API calls
    job_scheduler.add_job(
        func=massive_biannual_refresh.run,
        trigger=CronTrigger(
            month='1,7',            # January and July
            day='1',                # First day of month
            hour='4',               # 4 AM
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='massive_biannual_refresh',
        name='MASSIVE Bi-Annual Refresh (Failsafe Full Re-Scan)'
    )
    
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
    # SYSTEM 2: DISABLED - Comprehensive NYSE/NASDAQ Collection
    # ============================================================================
    
    # ============================================================================
    # PRECIOUS METALS COLLECTION: DISABLED
    # ============================================================================
    # Uses Puppeteer browser automation to bypass Cloudflare protection
    # Fetches gold and silver prices from goodreturns.in
    # Schedule: Once daily at 10:00 AM IST (all days)
    
    # job_scheduler.add_job(
    #     func=metals_price_collector_job.run,
    #     trigger=CronTrigger(
    #         hour='10',              # 10 AM
    #         minute='0',             # At the start of the hour
    #         second='0',
    #         timezone='Asia/Kolkata'  # IST timezone
    #     ),
    #     job_id='metals_price_collector',
    #     name='Precious Metals Price Collection'
    # )
    
    # # Metadata enrichment: Daily at 2:00 AM EST (Alpha Vantage free tier: 25 calls/day)
    # # Processes 5 tickers per run to stay within limits
    # job_scheduler.add_job(
    #     func=metadata_collector_job.run_enrichment_cycle,
    #     trigger=CronTrigger(
    #         hour='2',               # 2 AM
    #         minute='0',             # At the start of the hour
    #         second='0',
    #         timezone='US/Eastern'   # EST timezone
    #     ),
    #     job_id='metadata_enrichment',
    #     name='Stock Metadata Enrichment (Alpha Vantage)'
    # )
    
    # # Incremental metadata collection: Every 15 minutes
    # # 100 tickers per batch * 4 times/hour * 24 hours = 9,600 tickers/day
    # # This ensures we feed the Foundation Builder (7,200/day) fast enough
    # job_scheduler.add_job(
    #     func=metadata_collector_job.run_incremental_batch_collection,
    #     trigger=CronTrigger(
    #         minute='*/15',  # Every 15 minutes (0, 15, 30, 45)
    #         second='0',
    #         timezone='US/Eastern'
    #     ),
    #     job_id='incremental_collection_15min',
    #     name='Incremental Metadata Collection (Every 15 min)'
    # )
    
    # ============================================================================
    # MASSIVE Foundation Builder: DISABLED
    # ============================================================================
    # Purpose: Collect foundational metadata (CIK, FIGI, logos, etc.) for all tickers
    # Rate: 5 calls/min (Polygon.io free tier limit)
    # Schedule: Every minute, processing 5 tickers per run
    # Throughput: 300 tickers/hour = 7,200 tickers/day
    # Target: Complete 1,066 tickers in ~4 hours
    # Benefits: Frequent updates, better rate limit adherence, no artificial delays
    
    # job_scheduler.add_job(
    #     func=massive_foundation_builder_job.run,
    #     trigger=CronTrigger(
    #         minute='*',  # Every minute
    #         second='0',
    #         timezone='US/Eastern'  # EST/EDT timezone
    #     ),
    #     job_id='massive_foundation_per_minute',
    #     name='MASSIVE Foundation Collection (Every Minute)'
    # )
    
    logger.info(
        f"Registered {len(job_scheduler.jobs)} scheduled jobs",
        extra={"job_count": len(job_scheduler.jobs)}
    )


def unregister_all_jobs():
    """Unregister all jobs (useful for testing)."""
    job_ids = list(job_scheduler.jobs.keys())
    for job_id in job_ids:
        job_scheduler.remove_job(job_id)
