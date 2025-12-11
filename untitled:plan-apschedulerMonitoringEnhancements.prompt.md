# APScheduler Monitoring Enhancements - Implementation Plan

**Project:** Kuberan Stock Tracker
**Current System:** APScheduler (AsyncIOScheduler) + FastAPI + MongoDB
**Goal:** Add enterprise-grade monitoring without Airflow migration
**Total Effort:** 14-21 hours (6 phases)
**Status:** Ready for implementation after financials extraction completes

---

## Executive Summary

This plan implements comprehensive monitoring for Kuberan's APScheduler system with:
- **Execution history tracking** (MongoDB-backed, 90-day retention)
- **REST API endpoints** (query history, statistics, job summaries)
- **Web dashboard** (real-time monitoring with Chart.js visualizations)
- **Failure notifications** (Email via SMTP + Slack webhooks)
- **Dynamic job control** (pause/resume/trigger without restart)
- **Production polish** (error handling, validation, documentation)

**Why This Approach:**
- 14-21 hours vs 41-62 hours for Airflow migration (67% cost savings)
- No infrastructure changes (stays on Docker Compose)
- Preserves existing job architecture (self-terminating pattern)
- Incremental delivery (can stop after any phase)
- Tested at each step before continuing

---

## Phase 1: Execution History Foundation (3-4 hours)

### Objective
Create MongoDB-backed execution history with async repository pattern.

### Deliverables

#### 1.1 Create Database Models (45 minutes)
**File:** `backend/app/models/scheduler.py` (NEW)

**Models:**
```python
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field

class JobExecutionLog(Document):
    """Record of individual job execution"""
    job_id: str                              # Job identifier
    job_name: str                            # Human-readable name
    started_at: datetime                     # Execution start time
    completed_at: Optional[datetime] = None  # Execution end time (None if running)
    status: str                              # pending, running, success, failed
    duration_seconds: Optional[float] = None # Execution duration
    records_processed: Optional[int] = None  # Items processed (batch jobs)
    error_message: Optional[str] = None      # Failure reason
    error_traceback: Optional[str] = None    # Stack trace (truncated to 2000 chars)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Custom job data
    
    class Settings:
        name = "job_execution_logs"
        indexes = [
            [("job_id", 1), ("started_at", -1)],  # Query by job + time
            [("status", 1)],                      # Filter by status
            [("started_at", -1)]                  # Recent executions
        ]
        # TTL index: Auto-delete logs older than 90 days
        timeseries = {
            "timeField": "started_at",
            "metaField": "job_id",
            "granularity": "minutes"
        }
        expireAfterSeconds = 7776000  # 90 days

class JobConfig(Document):
    """Persistent job configuration"""
    job_id: str                              # Job identifier
    job_name: str                            # Human-readable name
    enabled: bool = True                     # Job active state
    schedule_cron: Optional[str] = None      # Cron expression
    last_modified_at: datetime               # Config update time
    created_at: datetime                     # Initial creation
    
    class Settings:
        name = "job_configs"
        indexes = [
            [("job_id", 1)],  # Unique constraint
            [("enabled", 1)]  # Filter active jobs
        ]
```

**Testing:**
```bash
# Add models to app/models/__init__.py DOCUMENT_MODELS list
# Restart backend to register models
docker-compose restart backend

# Verify collections created
docker exec -it kuberan-mongodb mongosh kuberan --eval "db.getCollectionNames()"
# Should show: job_execution_logs, job_configs
```

---

#### 1.2 Create Repository Layer (1 hour)
**File:** `backend/app/repositories/scheduler_repository.py` (NEW)

**Implementation:**
```python
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.scheduler import JobExecutionLog, JobConfig
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class SchedulerRepository:
    """Database operations for scheduler monitoring"""
    
    # Execution History Methods
    async def create_execution_log(
        self,
        job_id: str,
        job_name: str,
        started_at: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JobExecutionLog:
        """Create new execution log entry"""
        log = JobExecutionLog(
            job_id=job_id,
            job_name=job_name,
            started_at=started_at,
            status="running",
            metadata=metadata or {}
        )
        await log.insert()
        logger.info(
            "Execution log created",
            extra={"job_id": job_id, "log_id": str(log.id)}
        )
        return log
    
    async def update_execution_log(
        self,
        log_id: str,
        completed_at: datetime,
        status: str,
        records_processed: Optional[int] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None
    ) -> JobExecutionLog:
        """Mark execution complete/failed"""
        log = await JobExecutionLog.get(log_id)
        if not log:
            raise ValueError(f"Execution log {log_id} not found")
        
        log.completed_at = completed_at
        log.status = status
        log.duration_seconds = (completed_at - log.started_at).total_seconds()
        log.records_processed = records_processed
        log.error_message = error_message
        log.error_traceback = error_traceback[:2000] if error_traceback else None
        
        await log.save()
        logger.info(
            "Execution log updated",
            extra={
                "job_id": log.job_id,
                "status": status,
                "duration": log.duration_seconds
            }
        )
        return log
    
    async def get_execution_history(
        self,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[JobExecutionLog]:
        """Query execution history with filters"""
        query = {}
        if job_id:
            query["job_id"] = job_id
        if status:
            query["status"] = status
        if since:
            query["started_at"] = {"$gte": since}
        
        logs = await JobExecutionLog.find(query).sort("-started_at").limit(limit).to_list()
        return logs
    
    async def get_job_statistics(self, job_id: str, days: int = 7) -> Dict[str, Any]:
        """Calculate job statistics for time period"""
        since = datetime.utcnow() - timedelta(days=days)
        logs = await self.get_execution_history(job_id=job_id, since=since, limit=1000)
        
        total = len(logs)
        if total == 0:
            return {
                "job_id": job_id,
                "period_days": days,
                "total_executions": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate_pct": 0.0,
                "avg_duration_seconds": 0.0,
                "total_records_processed": 0
            }
        
        successes = [log for log in logs if log.status == "success"]
        failures = [log for log in logs if log.status == "failed"]
        
        durations = [log.duration_seconds for log in logs if log.duration_seconds]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        total_records = sum(log.records_processed for log in logs if log.records_processed)
        
        return {
            "job_id": job_id,
            "period_days": days,
            "total_executions": total,
            "success_count": len(successes),
            "failure_count": len(failures),
            "success_rate_pct": (len(successes) / total) * 100,
            "avg_duration_seconds": round(avg_duration, 2),
            "total_records_processed": total_records,
            "most_recent_execution": logs[0].started_at.isoformat() if logs else None
        }
    
    # Job Config Methods
    async def get_or_create_job_config(
        self,
        job_id: str,
        job_name: str,
        schedule_cron: Optional[str] = None
    ) -> JobConfig:
        """Get existing config or create default"""
        config = await JobConfig.find_one(JobConfig.job_id == job_id)
        if config:
            return config
        
        config = JobConfig(
            job_id=job_id,
            job_name=job_name,
            enabled=True,
            schedule_cron=schedule_cron,
            created_at=datetime.utcnow(),
            last_modified_at=datetime.utcnow()
        )
        await config.insert()
        logger.info("Job config created", extra={"job_id": job_id})
        return config
    
    async def update_job_config(
        self,
        job_id: str,
        enabled: Optional[bool] = None,
        schedule_cron: Optional[str] = None
    ) -> JobConfig:
        """Update job configuration"""
        config = await JobConfig.find_one(JobConfig.job_id == job_id)
        if not config:
            raise ValueError(f"Job config {job_id} not found")
        
        if enabled is not None:
            config.enabled = enabled
        if schedule_cron is not None:
            config.schedule_cron = schedule_cron
        config.last_modified_at = datetime.utcnow()
        
        await config.save()
        logger.info("Job config updated", extra={"job_id": job_id})
        return config

# Singleton instance
scheduler_repository = SchedulerRepository()
```

**Testing:**
```bash
# Python interactive test
docker exec -it kuberan-backend-1 python3 -c "
from app.repositories.scheduler_repository import scheduler_repository
from datetime import datetime
import asyncio

async def test():
    log = await scheduler_repository.create_execution_log(
        job_id='test_job',
        job_name='Test Job',
        started_at=datetime.utcnow(),
        metadata={'batch_size': 10}
    )
    print(f'Created log: {log.id}')
    
    await scheduler_repository.update_execution_log(
        log_id=str(log.id),
        completed_at=datetime.utcnow(),
        status='success',
        records_processed=100
    )
    print('Updated log successfully')

asyncio.run(test())
"
```

---

#### 1.3 Create Execution Tracker (1 hour)
**File:** `backend/app/services/scheduler/execution_tracker.py` (NEW)

**Implementation:**
```python
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import traceback
from app.repositories.scheduler_repository import scheduler_repository
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ExecutionTracker:
    """Async context manager for automatic execution logging"""
    
    @staticmethod
    @asynccontextmanager
    async def track(
        job_id: str,
        job_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Usage:
            async with ExecutionTracker.track("job_id", "Job Name") as tracker:
                # Job execution code
                tracker.set_records_processed(100)
        """
        started_at = datetime.utcnow()
        
        # Create execution log
        log = await scheduler_repository.create_execution_log(
            job_id=job_id,
            job_name=job_name,
            started_at=started_at,
            metadata=metadata
        )
        
        tracker = _TrackerContext(log_id=str(log.id))
        
        try:
            yield tracker
            
            # Success: Update log
            await scheduler_repository.update_execution_log(
                log_id=str(log.id),
                completed_at=datetime.utcnow(),
                status="success",
                records_processed=tracker.records_processed
            )
            
            logger.info(
                "Job execution successful",
                extra={
                    "job_id": job_id,
                    "duration": (datetime.utcnow() - started_at).total_seconds(),
                    "records_processed": tracker.records_processed
                }
            )
            
        except Exception as e:
            # Failure: Capture error details
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            await scheduler_repository.update_execution_log(
                log_id=str(log.id),
                completed_at=datetime.utcnow(),
                status="failed",
                records_processed=tracker.records_processed,
                error_message=error_message,
                error_traceback=error_traceback
            )
            
            logger.error(
                "Job execution failed",
                extra={
                    "job_id": job_id,
                    "error": error_message
                },
                exc_info=True
            )
            
            raise

class _TrackerContext:
    """Context object passed to tracked job"""
    def __init__(self, log_id: str):
        self.log_id = log_id
        self.records_processed: Optional[int] = None
    
    def set_records_processed(self, count: int):
        """Update records processed count"""
        self.records_processed = count
```

**Testing:**
```python
# Test with dummy job
async def test_job():
    async with ExecutionTracker.track("test_job", "Test Job") as tracker:
        await asyncio.sleep(1)  # Simulate work
        tracker.set_records_processed(50)
        # Will log success

async def test_failing_job():
    async with ExecutionTracker.track("test_job", "Test Job") as tracker:
        await asyncio.sleep(0.5)
        raise ValueError("Test error")  # Will log failure

# Run tests
asyncio.run(test_job())
asyncio.run(test_failing_job())  # Should capture exception
```

---

#### 1.4 Integrate with Financials Job (1 hour)
**File:** `backend/app/services/jobs/financials_extraction_job.py` (MODIFY)

**Changes:**
```python
from app.services.scheduler.execution_tracker import ExecutionTracker

class FinancialsExtractionJob:
    # ... existing __init__ ...
    
    async def run(self):
        """Main execution with tracking"""
        async with ExecutionTracker.track(
            job_id="financials_extraction",
            job_name="S&P 500 Financials Extraction",
            metadata={
                "batch_size": self.batch_size,
                "target_tickers": 500
            }
        ) as tracker:
            # Check if job should continue
            should_continue = await self.should_run()
            if not should_continue:
                logger.info("Extraction complete, job terminating")
                return
            
            # Get next batch
            tickers = await self.get_next_batch()
            if not tickers:
                logger.warning("No tickers to process")
                return
            
            # Process batch
            success_count = 0
            for ticker in tickers:
                try:
                    await self.extract_ticker_financials(ticker)
                    success_count += 1
                except Exception as e:
                    logger.error(
                        "Ticker extraction failed",
                        extra={"ticker": ticker, "error": str(e)}
                    )
            
            # Update tracker
            tracker.set_records_processed(success_count)
            
            logger.info(
                "Batch complete",
                extra={
                    "extracted": success_count,
                    "failed": len(tickers) - success_count
                }
            )
```

**Testing:**
```bash
# Trigger job manually to test tracking
docker exec -it kuberan-backend-1 python3 -c "
from app.services.jobs.financials_extraction_job import financials_extraction_job
import asyncio

asyncio.run(financials_extraction_job.run())
"

# Verify log created
docker exec -it kuberan-mongodb mongosh kuberan --eval "
db.job_execution_logs.find({job_id: 'financials_extraction'}).sort({started_at: -1}).limit(1).pretty()
"
```

---

### Phase 1 Completion Checklist
- [ ] Models created and registered (`JobExecutionLog`, `JobConfig`)
- [ ] Repository methods tested (create, update, query, statistics)
- [ ] Execution tracker tested (success and failure scenarios)
- [ ] Financials job integrated and running with tracking
- [ ] MongoDB collections visible (`job_execution_logs`, `job_configs`)
- [ ] Logs show execution tracking messages

**Estimated Time:** 3-4 hours
**Deliverables:** MongoDB-backed execution history with async tracker

---

## Phase 2: REST API Endpoints (2-3 hours)

### Objective
Expose execution history and job control via REST API.

### Deliverables

#### 2.1 Create Router File (2 hours)
**File:** `backend/app/routers/scheduler.py` (MODIFY - extend existing)

**Add New Endpoints:**
```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from app.repositories.scheduler_repository import scheduler_repository
from app.services.scheduler.scheduler import job_scheduler
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/system/scheduler", tags=["Scheduler"])

# ============================================================================
# EXECUTION HISTORY ENDPOINTS (NEW)
# ============================================================================

@router.get("/history")
async def get_execution_history(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    status: Optional[str] = Query(None, description="Filter by status (success/failed)"),
    days: Optional[int] = Query(7, description="Look back N days"),
    limit: int = Query(100, ge=1, le=500)
):
    """Get execution history with filters"""
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = await scheduler_repository.get_execution_history(
        job_id=job_id,
        status=status,
        since=since,
        limit=limit
    )
    
    return {
        "count": len(logs),
        "filters": {"job_id": job_id, "status": status, "days": days},
        "executions": [
            {
                "job_id": log.job_id,
                "job_name": log.job_name,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "status": log.status,
                "duration_seconds": log.duration_seconds,
                "records_processed": log.records_processed,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }

@router.get("/jobs/{job_id}/statistics")
async def get_job_statistics(
    job_id: str,
    days: int = Query(7, ge=1, le=90, description="Statistics period in days")
):
    """Get job performance statistics"""
    stats = await scheduler_repository.get_job_statistics(job_id, days)
    return stats

@router.get("/jobs/{job_id}/recent-failures")
async def get_recent_failures(
    job_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent failed executions with error details"""
    logs = await scheduler_repository.get_execution_history(
        job_id=job_id,
        status="failed",
        limit=limit
    )
    
    return {
        "job_id": job_id,
        "failure_count": len(logs),
        "failures": [
            {
                "started_at": log.started_at.isoformat(),
                "duration_seconds": log.duration_seconds,
                "error_message": log.error_message,
                "error_traceback": log.error_traceback
            }
            for log in logs
        ]
    }

@router.get("/jobs/summary")
async def get_jobs_summary():
    """Get summary of all registered jobs with statistics"""
    jobs = job_scheduler.get_jobs()
    
    summary = []
    for job in jobs:
        stats = await scheduler_repository.get_job_statistics(job["job_id"], days=7)
        
        summary.append({
            "job_id": job["job_id"],
            "job_name": job["job_name"],
            "next_run": job.get("next_run_time"),
            "statistics": stats
        })
    
    return {
        "total_jobs": len(jobs),
        "jobs": summary
    }
```

**Testing:**
```bash
curl http://localhost:8000/system/scheduler/history | python3 -m json.tool
curl http://localhost:8000/system/scheduler/jobs/financials_extraction/statistics | python3 -m json.tool
curl http://localhost:8000/system/scheduler/jobs/financials_extraction/recent-failures | python3 -m json.tool
curl http://localhost:8000/system/scheduler/jobs/summary | python3 -m json.tool
```

---

### Phase 2 Completion Checklist
- [ ] 4 new endpoints added to scheduler router
- [ ] Endpoints return correct data from MongoDB
- [ ] API.md documentation updated
- [ ] Postman collection updated and tested
- [ ] All curl tests pass

**Estimated Time:** 2-3 hours
**Deliverables:** REST API for querying execution history

---

## Phase 3: Web Dashboard (4-6 hours)

### Objective
Create HTML/JS dashboard for visual monitoring (no React build step).

### Deliverables

#### 3.1 Create Dashboard HTML (3 hours)
**File:** `backend/app/static/scheduler_dashboard.html` (NEW)

**Key Features:**
- Real-time stats (total jobs, success rate, executions)
- Performance chart (Chart.js bar chart)
- Jobs table with next run times
- Recent executions table with status badges
- Auto-refresh every 30 seconds
- Manual refresh button

#### 3.2 Serve Dashboard via FastAPI (30 minutes)
**File:** `backend/app/main.py` (MODIFY)

**Add Static Files Mount:**
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

# Create static directory
os.makedirs("app/static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Dashboard redirect
@app.get("/system/scheduler/dashboard")
async def scheduler_dashboard():
    return RedirectResponse(url="/static/scheduler_dashboard.html")
```

**Access:** http://localhost:8000/system/scheduler/dashboard

---

### Phase 3 Completion Checklist
- [ ] Dashboard HTML created with Chart.js
- [ ] Static files mounted in FastAPI
- [ ] Dashboard accessible in browser
- [ ] Summary stats display correctly
- [ ] Performance chart renders
- [ ] Auto-refresh works (30 seconds)
- [ ] Documentation updated

**Estimated Time:** 4-6 hours
**Deliverables:** Web dashboard for visual monitoring

---

## Phase 4: Failure Notifications (2-3 hours)

### Objective
Send alerts via Email (SMTP) and Slack webhooks when jobs fail.

### Deliverables

#### 4.1 Create Notification Service (1.5 hours)
**File:** `backend/app/services/scheduler/notification_service.py` (NEW)

**Features:**
- Email notifications via SMTP (Gmail, SendGrid, etc.)
- Slack notifications via webhooks
- Rate limiting (15-minute cooldown per job)
- HTML email templates
- Slack block kit formatting

#### 4.2 Integrate with Execution Tracker (30 minutes)
**File:** `backend/app/services/scheduler/execution_tracker.py` (MODIFY)

**Add notification call in exception handler:**
```python
from app.services.scheduler.notification_service import notification_service

# In exception block:
await notification_service.notify_job_failure(
    job_id=job_id,
    job_name=job_name,
    error_message=error_message,
    started_at=started_at,
    duration_seconds=(datetime.utcnow() - started_at).total_seconds()
)
```

#### 4.3 Configuration Guide (1 hour)
**File:** `docs/SCHEDULER_MONITORING.md` (NEW)

**Environment Variables:**
```bash
# Email
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TO=admin@example.com,dev@example.com

# Slack
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Rate Limiting
ALERT_COOLDOWN_MINUTES=15
```

---

### Phase 4 Completion Checklist
- [ ] Notification service created
- [ ] Email alerts working (SMTP)
- [ ] Slack alerts working (webhooks)
- [ ] Rate limiting prevents spam
- [ ] Configuration guide written
- [ ] Test notifications sent successfully

**Estimated Time:** 2-3 hours
**Deliverables:** Email + Slack failure notifications

---

## Phase 5: Dynamic Job Control (2-3 hours)

### Objective
Pause/resume/trigger jobs without backend restart.

### Deliverables

#### 5.1 Add Control Endpoints (1.5 hours)
**File:** `backend/app/routers/scheduler.py` (MODIFY)

**New Endpoints:**
```python
@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause scheduled job"""
    job_scheduler.pause_job(job_id)
    await scheduler_repository.update_job_config(job_id, enabled=False)
    return {"status": "paused", "job_id": job_id}

@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume paused job"""
    job_scheduler.resume_job(job_id)
    await scheduler_repository.update_job_config(job_id, enabled=True)
    return {"status": "resumed", "job_id": job_id}

@router.post("/jobs/{job_id}/trigger")
async def trigger_job(job_id: str):
    """Manually trigger job execution"""
    job_scheduler.trigger_job(job_id)
    return {"status": "triggered", "job_id": job_id}
```

#### 5.2 Update Dashboard (1 hour)
**File:** `backend/app/static/scheduler_dashboard.html` (MODIFY)

**Add Control Buttons:**
- Pause/Resume toggle buttons
- Trigger Now button
- Confirm dialogs for actions

---

### Phase 5 Completion Checklist
- [ ] Control endpoints implemented
- [ ] Jobs can be paused/resumed
- [ ] Manual trigger works
- [ ] Dashboard buttons functional
- [ ] Job state persists in MongoDB
- [ ] Documentation updated

**Estimated Time:** 2-3 hours
**Deliverables:** Dynamic job control without restart

---

## Phase 6: Polish & Documentation (1-2 hours)

### Objective
Production-ready error handling, validation, and documentation.

### Deliverables

#### 6.1 Error Handling (30 minutes)
- Add input validation to all endpoints
- Handle edge cases (job not found, invalid dates)
- Improve error messages
- Add request logging

#### 6.2 Documentation (1 hour)
**Update Files:**
- `docs/API.md` - All new endpoints documented
- `docs/WORKFLOWS.md` - Monitoring workflows added
- `docs/SCHEDULER_MONITORING.md` - Complete setup guide
- `README.md` - Link to monitoring dashboard

**Postman Collection:**
- Add all new endpoints
- Test and export collection

#### 6.3 Final Testing (30 minutes)
- Test all 6 phases end-to-end
- Verify data integrity
- Check performance (dashboard load time)
- Validate notifications

---

### Phase 6 Completion Checklist
- [ ] Input validation on all endpoints
- [ ] Error handling comprehensive
- [ ] API.md complete
- [ ] WORKFLOWS.md updated
- [ ] SCHEDULER_MONITORING.md written
- [ ] Postman collection updated
- [ ] End-to-end testing passed

**Estimated Time:** 1-2 hours
**Deliverables:** Production-ready monitoring system

---

## Implementation Timeline

**Total Effort:** 14-21 hours (6 phases)

**Recommended Schedule:**

**Day 1 (6-8 hours):**
- Phase 1: Execution History Foundation (3-4h)
- Phase 2: REST API Endpoints (2-3h)
- Testing and validation (1h)

**Day 2 (6-8 hours):**
- Phase 3: Web Dashboard (4-6h)
- Phase 4: Failure Notifications (2-3h)
- Testing and validation (1h)

**Day 3 (3-5 hours):**
- Phase 5: Dynamic Job Control (2-3h)
- Phase 6: Polish & Documentation (1-2h)
- Final end-to-end testing (1h)

---

## Success Criteria

**Phase 1 Complete:**
- MongoDB collections created
- Execution logs stored automatically
- Repository queries working

**Phase 2 Complete:**
- 4 API endpoints functional
- Postman collection updated
- Documentation current

**Phase 3 Complete:**
- Dashboard accessible in browser
- Real-time stats display
- Chart renders correctly

**Phase 4 Complete:**
- Email alerts received on failure
- Slack notifications working
- Rate limiting prevents spam

**Phase 5 Complete:**
- Jobs can be paused/resumed via API
- Manual trigger works
- State persists across restarts

**Phase 6 Complete:**
- All documentation updated
- Error handling robust
- End-to-end tests pass

---

## Rollback Plan

If any phase causes issues:

1. **Revert Code Changes:**
   ```bash
   git checkout -- backend/app/models/scheduler.py
   git checkout -- backend/app/repositories/scheduler_repository.py
   # etc.
   ```

2. **Restart Backend:**
   ```bash
   docker-compose restart backend
   ```

3. **Drop Test Collections:**
   ```bash
   docker exec -it kuberan-mongodb mongosh kuberan --eval "
   db.job_execution_logs.drop();
   db.job_configs.drop();
   "
   ```

4. **Verify System Healthy:**
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/system/scheduler/info
   ```

---

## Post-Implementation

**After All Phases Complete:**

1. **Monitor Production:**
   - Check dashboard daily for first week
   - Verify notifications working
   - Validate data retention (90-day TTL)

2. **Performance Tuning:**
   - If dashboard slow, add caching
   - If MongoDB queries slow, add indexes
   - If notifications spam, increase cooldown

3. **Future Enhancements (Optional):**
   - Job dependencies (Phase 7)
   - Advanced alerting rules (Phase 8)
   - Parameter overrides per execution (Phase 9)
   - Historical trend analysis (Phase 10)

---

**Plan Complete - Ready for Implementation**
**Last Updated:** December 11, 2025
