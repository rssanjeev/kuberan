"""
Centralized job scheduler using APScheduler.
Manages all scheduled background tasks in one place.
"""
from typing import Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.base import BaseTrigger
import pytz
from datetime import datetime
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class JobScheduler:
    """
    Centralized scheduler for all background jobs.
    Provides a single APScheduler instance and job management.
    """
    
    def __init__(self):
        """Initialize scheduler with US/Eastern timezone."""
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('US/Eastern'))
        self.jobs: Dict[str, str] = {}  # job_id -> job_name mapping
        self._is_running = False
    
    def start(self):
        """Start the scheduler."""
        if self._is_running:
            logger.warning("Job scheduler is already running")
            return
        
        self.scheduler.start()
        self._is_running = True
        
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        logger.info(
            f"Job scheduler started at {current_time.strftime('%Y-%m-%d %H:%M:%S EST')}",
            extra={"job_count": len(self.jobs)}
        )
        
        for job_id, job_name in self.jobs.items():
            logger.debug(f"Registered job: {job_name}", extra={"job_id": job_id})
    
    def stop(self):
        """Stop the scheduler and all jobs."""
        if not self._is_running:
            return
        
        self.scheduler.shutdown()
        self._is_running = False
        logger.info("Job scheduler stopped")
    
    def add_job(
        self,
        func,
        trigger: BaseTrigger,
        job_id: str,
        name: str,
        **kwargs
    ):
        """
        Add a job to the scheduler.
        
        Args:
            func: Async function to execute
            trigger: APScheduler trigger (CronTrigger, IntervalTrigger, etc.)
            job_id: Unique identifier for the job
            name: Human-readable job name
            **kwargs: Additional arguments passed to scheduler.add_job()
        """
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True,
            **kwargs
        )
        self.jobs[job_id] = name
    
    def remove_job(self, job_id: str):
        """Remove a job from the scheduler."""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
    
    def pause_job(self, job_id: str):
        """Pause a job without removing it."""
        self.scheduler.pause_job(job_id)
    
    def resume_job(self, job_id: str):
        """Resume a paused job."""
        self.scheduler.resume_job(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status information for a specific job.
        
        Returns:
            Dictionary with job info or None if not found
        """
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        }
    
    def get_all_jobs(self) -> list:
        """Get status for all registered jobs."""
        return [
            self.get_job_status(job_id) 
            for job_id in self.jobs.keys()
        ]
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running


# Singleton instance
job_scheduler = JobScheduler()
