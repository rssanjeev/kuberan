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
    from app.services.jobs.massive_foundation_builder import massive_foundation_builder_job
    
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
    
    # ============================================================================
    # PHASE 3.5 JOBS: Historical Data Backfill (ENABLED Dec 4, 2025)
    # ============================================================================
    # Daily job to gradually populate 5-year historical price cache
    # Purpose: Enable fast queries for technical analysis, backtesting, charting
    # Schedule: Daily at 6:00 PM EST
    # Throughput: 10 tickers/day × ~1,260 records = ~12,600 records/day
    # Coverage: ~1,200 tickers over 120 days (4 months)
    # Rate Limiting: 12-second delays between API calls (5 calls/min)
    # ============================================================================
    from app.services.jobs.historical_data_backfill import historical_data_backfill
    
    # ============================================================================
    # PHASE 4 JOBS: Related Tickers Collection (ENABLED Dec 5, 2025)
    # ============================================================================
    # Weekly job to collect related companies for S&P 500 tickers
    # Purpose: Populate peer/competitor relationships for comparison features
    # Schedule: Weekly Monday 4:00 AM EST
    # Throughput: 300 tickers/week, ~5-10 relationships per ticker
    # Rate Limiting: 12-second delays between API calls (5 calls/min)
    # ============================================================================
    from app.services.jobs.related_tickers_collector import related_tickers_collector_job
    
    # ============================================================================
    # PHASE 5 JOBS: Financials Collection (ENABLED Dec 5, 2025)
    # ============================================================================
    # Quarterly job to collect financial statements before API deprecation
    # Purpose: Archive income statements, balance sheets, cash flow statements
    # Schedule: Quarterly (February, May, August, November) at 5:00 AM EST
    # ⚠️ URGENT: API deprecated Feb 23, 2026 - 79 days remaining
    # Backfill Strategy:
    #   - S&P 500: 500 tickers × 10 statements = 5,000 calls (~17 hours)
    #   - Full dataset: 12,140 tickers × 10 statements = 121,400 calls (~50 days)
    # Rate Limiting: 12-second delays between API calls (5 calls/min)
    # ============================================================================
    from app.services.jobs.financials_collector import financials_collector_job
    
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
    # HISTORICAL DATA BACKFILL: Gradual 5-year cache population
    # ============================================================================
    # Daily at 6:00 PM EST - processes 10 tickers per run
    # Fetches 5 years of daily OHLCV data from Yahoo Finance
    # Throughput: 10 tickers × ~1,260 records = ~12,600 records/day
    # Coverage timeline: ~1,200 tickers over 120 days (4 months)
    # Rate limiting: 12-second delays between API calls (5 calls/min)
    job_scheduler.add_job(
        func=historical_data_backfill.run,
        trigger=CronTrigger(
            hour='18',              # 6 PM
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='historical_data_backfill',
        name='Historical Data Backfill (Daily 5-Year Cache Population)'
    )
    
    # ============================================================================
    # RELATED TICKERS COLLECTION: Weekly peer/competitor relationship building
    # ============================================================================
    # Weekly Monday 4:00 AM EST - processes 300 tickers per run
    # Fetches related companies from MASSIVE API for S&P 500 tickers
    # Throughput: 300 tickers × ~5-10 relationships = 1,500-3,000 relationships/week
    # Rate limiting: 12-second delays between API calls (5 calls/min)
    job_scheduler.add_job(
        func=related_tickers_collector_job.run,
        trigger=CronTrigger(
            day_of_week='mon',      # Monday only
            hour='4',               # 4 AM
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='related_tickers_collection',
        name='Related Tickers Collection (Weekly S&P 500)'
    )
    
    # ============================================================================
    # FINANCIALS COLLECTION: Quarterly financial statements archival
    # ============================================================================
    # Quarterly (February, May, August, November) at 5:00 AM EST
    # Processes latest annual financial statements for S&P 500
    # ⚠️ URGENT: API deprecated Feb 23, 2026 - backfill ASAP
    # Normal mode: Latest annual only (500-1,000 statements per quarter)
    # Backfill mode: 2 annual + 8 quarterly per ticker (run manually)
    # Rate limiting: 12-second delays between API calls (5 calls/min)
    job_scheduler.add_job(
        func=financials_collector_job.run,
        trigger=CronTrigger(
            month='2,5,8,11',       # February, May, August, November
            day='15',               # Mid-month (after most earnings)
            hour='5',               # 5 AM
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='financials_collection',
        name='Financials Collection (Quarterly Statements Archival)'
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
    # MASSIVE Foundation Builder: ENABLED (Dec 5, 2025)
    # ============================================================================
    # Purpose: Collect foundational metadata (CIK, FIGI, logos, etc.) for all tickers
    # Rate: 5 calls/min (Polygon.io free tier limit)
    # Schedule: Every minute, processing 5 tickers per run
    # Throughput: 300 tickers/hour = 7,200 tickers/day
    # Progress: 4,463/12,147 enriched (36.7%)
    # Remaining: 7,464 tickers (~24.9 hours to completion)
    # Benefits: Frequent updates, better rate limit adherence, market cap prioritization
    
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
