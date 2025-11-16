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
    """
    # Import jobs here to avoid circular imports
    from app.services.jobs.price_collector import price_collector_job
    from app.services.jobs.metals_price_collector import metals_price_collector_job
    
    # Price collection: Every 60 seconds, 9 AM - 5 PM EST, Mon-Fri
    job_scheduler.add_job(
        func=price_collector_job.run,
        trigger=CronTrigger(
            day_of_week='mon-fri',  # Monday to Friday
            hour='9-16',            # 9 AM to 4:59 PM
            minute='*',             # Every minute
            second='0',             # At the start of each minute
            timezone='US/Eastern'
        ),
        job_id='price_collector',
        name='Stock Price Collection'
    )
    
    # Market close poll: Once at 5:00 PM EST
    job_scheduler.add_job(
        func=price_collector_job.run,
        trigger=CronTrigger(
            day_of_week='mon-fri',
            hour='17',
            minute='0',
            second='0',
            timezone='US/Eastern'
        ),
        job_id='market_close_poll',
        name='Market Close Price Poll'
    )
    
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
    
    logger.info(
        f"Registered {len(job_scheduler.jobs)} scheduled jobs",
        extra={"job_count": len(job_scheduler.jobs)}
    )


def unregister_all_jobs():
    """Unregister all jobs (useful for testing)."""
    job_ids = list(job_scheduler.jobs.keys())
    for job_id in job_ids:
        job_scheduler.remove_job(job_id)
