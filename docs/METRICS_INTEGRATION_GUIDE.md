# API Metrics Integration Guide

Quick guide to integrating API call tracking into Kuberan providers.

**Last Updated:** November 16, 2025

---

## Step 1: Run TTL Migration

Create the 3 new MongoDB timeseries collections:

```bash
# Navigate to backend directory
cd /Users/sanjeev/Developer/kuberan

# Run TTL configuration script
docker exec -w /app kuberan-backend-1 \
  python3 -m app.scripts.configure_timeseries_ttl

# Expected output:
# ✓ Created 'provider_api_calls' (30-day TTL)
# ✓ Created 'provider_health_checks' (7-day TTL)
# ✓ Created 'rate_limit_status' (1-hour TTL)
```

**Verify collections:**
```bash
docker exec -it kuberan-mongodb mongosh kuberan

# In MongoDB shell:
db.getCollectionNames()
# Should see: provider_api_calls, provider_health_checks, rate_limit_status

# Check timeseries status:
db.getCollectionInfos({name: "provider_api_calls"})
```

---

## Step 2: Add Tracking to Provider Methods

### Pattern 1: Decorator (Recommended)

**Before:**
```python
class YFinanceProvider(BaseProvider):
    
    async def fetch_real_time_quote(self, ticker: str) -> Dict:
        """Fetch real-time quote from yfinance."""
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Transform to quote model
        quote = StockQuote(...)
        saved = await provider_repository.save_quote(quote)
        
        return self._to_dict(saved)
```

**After:**
```python
from app.core.api_metrics import api_metrics

class YFinanceProvider(BaseProvider):
    
    @api_metrics.track_api_call(
        provider="yfinance",
        data_type="quote"
    )
    async def fetch_real_time_quote(self, ticker: str) -> Dict:
        """Fetch real-time quote from yfinance."""
        # EXACT SAME CODE - no changes needed!
        stock = yf.Ticker(ticker)
        info = stock.info
        
        quote = StockQuote(...)
        saved = await provider_repository.save_quote(quote)
        
        return self._to_dict(saved)
```

**What happens automatically:**
- ✅ Start time recorded
- ✅ End time recorded
- ✅ Response time calculated
- ✅ Success/failure detected
- ✅ Errors captured with messages
- ✅ Saved to MongoDB (ProviderAPICall)
- ✅ Rate limit status updated (if applicable)

---

### Pattern 2: Decorator with Dynamic Ticker

For methods where ticker is a parameter:

```python
@api_metrics.track_api_call(
    provider="alpha_vantage",
    data_type="historical"
)
async def fetch_historical_prices(
    self, 
    ticker: str, 
    start_date: datetime, 
    end_date: datetime
) -> Dict:
    """Ticker automatically extracted from context."""
    # The decorator will capture 'ticker' from function arguments
    pass
```

---

### Pattern 3: Multiple Decorators

Stack decorators for retry logic + metrics:

```python
@retry(max_attempts=3, backoff=2.0)  # Retry decorator
@api_metrics.track_api_call(
    provider="finnhub",
    data_type="news"
)
async def fetch_company_news(self, ticker: str) -> Dict:
    """Metrics track all attempts, including retries."""
    pass
```

---

## Step 3: Test Tracking

### Make Some API Calls

```bash
# Via curl or Postman
curl http://localhost:8000/stocks/quote/AAPL
curl http://localhost:8000/stocks/historical/TSLA?days=30
curl http://localhost:8000/stocks/news/MSFT?limit=10
```

### Verify MongoDB Storage

```bash
docker exec -it kuberan-mongodb mongosh kuberan
```

**Query recent calls:**
```javascript
db.provider_api_calls.find().sort({timestamp: -1}).limit(5)

// Expected output:
// {
//   _id: ObjectId("..."),
//   provider: "yfinance",
//   data_type: "quote",
//   timestamp: ISODate("2025-11-16T10:45:23.123Z"),
//   status: "success",
//   response_time_ms: 145,
//   ticker: "AAPL",
//   endpoint: null,
//   error_message: null,
//   http_status_code: 200
// }
```

**Check count by provider:**
```javascript
db.provider_api_calls.aggregate([
  {$group: {_id: "$provider", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

**Check success rate:**
```javascript
db.provider_api_calls.aggregate([
  {$group: {
    _id: "$provider",
    total: {$sum: 1},
    successful: {
      $sum: {$cond: [{$eq: ["$status", "success"]}, 1, 0]}
    }
  }},
  {$project: {
    total: 1,
    successful: 1,
    success_rate: {$divide: ["$successful", "$total"]}
  }}
])
```

---

## Step 4: Create Daily Aggregation Job

Add to `backend/app/services/jobs/metrics_aggregation_job.py`:

```python
"""
Daily metrics aggregation job.

Runs at midnight to compute ProviderDailyStats from raw ProviderAPICall logs.
"""

from datetime import datetime, timedelta
from app.core.logging_config import get_logger
from app.core.api_metrics import api_metrics

logger = get_logger(__name__)

class MetricsAggregationJob:
    """Daily job to aggregate API call metrics."""
    
    def __init__(self):
        self.last_run: datetime = None
    
    async def run(self):
        """Aggregate yesterday's data for all providers."""
        logger.info("Starting metrics aggregation job")
        
        # Calculate yesterday's date
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        
        providers = ["alpha_vantage", "finnhub", "yfinance"]
        
        for provider in providers:
            try:
                stats = await api_metrics.aggregate_daily_stats(
                    provider=provider,
                    date=datetime.combine(yesterday, datetime.min.time())
                )
                
                if stats:
                    logger.info(
                        f"Aggregated metrics for {provider}",
                        extra={
                            "provider": provider,
                            "date": yesterday.isoformat(),
                            "total_calls": stats.total_calls,
                            "success_rate": stats.success_rate
                        }
                    )
                else:
                    logger.info(
                        f"No calls for {provider} on {yesterday}",
                        extra={"provider": provider, "date": yesterday.isoformat()}
                    )
                    
            except Exception as e:
                logger.error(
                    f"Failed to aggregate metrics for {provider}",
                    extra={"provider": provider, "error": str(e)},
                    exc_info=True
                )
        
        self.last_run = datetime.utcnow()
        logger.info("Metrics aggregation job completed")

# Singleton
metrics_aggregation_job = MetricsAggregationJob()
```

**Register in scheduler** (`backend/app/services/scheduler/registry.py`):

```python
from apscheduler.triggers.cron import CronTrigger
from app.services.jobs.metrics_aggregation_job import metrics_aggregation_job

def register_all_jobs():
    # ... existing jobs ...
    
    # Metrics aggregation - runs daily at 1 AM
    job_scheduler.add_job(
        func=metrics_aggregation_job.run,
        trigger=CronTrigger(hour=1, minute=0),  # 1:00 AM daily
        job_id='daily_metrics_aggregation',
        name='Daily Metrics Aggregation',
        replace_existing=True
    )
```

---

## Step 5: Create Monitoring Endpoints

Add to `backend/app/routers/monitoring.py`:

```python
"""
Monitoring API endpoints for provider metrics.
"""

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional
from app.models.monitoring import ProviderAPICall, ProviderDailyStats, CallStatus
from app.core.logging_config import get_logger

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = get_logger(__name__)

@router.get("/providers/summary")
async def get_providers_summary():
    """Get summary statistics for all providers (today)."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    providers = ["alpha_vantage", "finnhub", "yfinance"]
    summaries = []
    
    for provider in providers:
        calls = await ProviderAPICall.find(
            ProviderAPICall.provider == provider,
            ProviderAPICall.timestamp >= today_start
        ).to_list()
        
        total = len(calls)
        successful = sum(1 for c in calls if c.status == CallStatus.SUCCESS)
        failed = sum(1 for c in calls if c.status == CallStatus.FAILURE)
        rate_limited = sum(1 for c in calls if c.status == CallStatus.RATE_LIMITED)
        
        avg_response = (
            sum(c.response_time_ms or 0 for c in calls) / total
            if total > 0 else 0
        )
        
        summaries.append({
            "provider": provider,
            "total_calls_today": total,
            "successful_calls": successful,
            "failed_calls": failed,
            "rate_limited_calls": rate_limited,
            "success_rate": successful / total if total > 0 else 0,
            "avg_response_time_ms": round(avg_response, 2)
        })
    
    return {
        "providers": summaries,
        "as_of": datetime.utcnow().isoformat()
    }

@router.get("/providers/{provider}/stats")
async def get_provider_stats(
    provider: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve")
):
    """Get daily statistics for a provider over N days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = await ProviderDailyStats.find(
        ProviderDailyStats.provider == provider,
        ProviderDailyStats.date >= start_date
    ).sort([("date", -1)]).to_list()
    
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"No statistics found for provider '{provider}'"
        )
    
    return {
        "provider": provider,
        "period_days": days,
        "stats_count": len(stats),
        "daily_stats": [
            {
                "date": s.date.isoformat(),
                "total_calls": s.total_calls,
                "successful_calls": s.successful_calls,
                "failed_calls": s.failed_calls,
                "success_rate": s.success_rate,
                "avg_response_time_ms": s.avg_response_time_ms,
                "calls_by_data_type": s.calls_by_data_type
            }
            for s in stats
        ]
    }

@router.get("/providers/{provider}/recent-calls")
async def get_recent_calls(
    provider: str,
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get recent API calls for a provider."""
    query = ProviderAPICall.provider == provider
    
    if status:
        try:
            status_enum = CallStatus(status)
            query = query & (ProviderAPICall.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be: success, failure, timeout, rate_limited"
            )
    
    calls = await ProviderAPICall.find(query) \
        .sort([("timestamp", -1)]) \
        .limit(limit) \
        .to_list()
    
    return {
        "provider": provider,
        "count": len(calls),
        "calls": [
            {
                "timestamp": c.timestamp.isoformat(),
                "data_type": c.data_type,
                "status": c.status.value,
                "response_time_ms": c.response_time_ms,
                "ticker": c.ticker,
                "endpoint": c.endpoint,
                "error_message": c.error_message,
                "http_status_code": c.http_status_code
            }
            for c in calls
        ]
    }
```

**Register router in `main.py`:**
```python
from app.routers import monitoring

app.include_router(monitoring.router)
```

---

## Step 6: Test Monitoring Endpoints

```bash
# Get summary for all providers
curl http://localhost:8000/monitoring/providers/summary | python3 -m json.tool

# Get 7-day stats for yfinance
curl http://localhost:8000/monitoring/providers/yfinance/stats?days=7 | python3 -m json.tool

# Get recent calls for Alpha Vantage
curl http://localhost:8000/monitoring/providers/alpha_vantage/recent-calls?limit=10 | python3 -m json.tool

# Get only failed calls
curl "http://localhost:8000/monitoring/providers/finnhub/recent-calls?status=failure" | python3 -m json.tool
```

---

## Verification Checklist

After integration, verify:

- [ ] TTL migration ran successfully (3 new collections created)
- [ ] Provider methods have `@api_metrics.track_api_call` decorator
- [ ] API calls are being logged to MongoDB (check provider_api_calls collection)
- [ ] Response times are being captured (non-null values)
- [ ] Errors are being recorded (check error_message field)
- [ ] Daily aggregation job is scheduled (check registry.py)
- [ ] Monitoring endpoints return data (test with curl)
- [ ] Success rates are accurate (compare to actual success/failure)
- [ ] Rate limit tracking works (if applicable)

---

## Troubleshooting

### No metrics being recorded

**Check:**
1. Decorator applied correctly to provider methods
2. Backend restarted after adding decorator
3. MongoDB connection working
4. Check logs for "Failed to record API call" errors

**Debug:**
```bash
# Check if decorator is working
docker logs kuberan-backend-1 | grep "Recording API call"

# Verify MongoDB connection
docker exec -it kuberan-mongodb mongosh kuberan --eval "db.provider_api_calls.countDocuments({})"
```

### Metrics recorded but decorator fails silently

The decorator is designed to be **fail-safe** - if metrics recording fails, the API call still succeeds.

**Check logs:**
```bash
docker logs kuberan-backend-1 | grep "Failed to record API call"
```

### Daily aggregation not running

**Check:**
1. Job registered in `registry.py`
2. Scheduler is running (check logs for "Scheduler started")
3. Job ID is unique

**Manual trigger:**
```python
# In Python shell
from app.services.jobs.metrics_aggregation_job import metrics_aggregation_job
await metrics_aggregation_job.run()
```

### Collections not created

**Re-run TTL script:**
```bash
docker exec -w /app kuberan-backend-1 \
  python3 -m app.scripts.configure_timeseries_ttl --dry-run=false
```

**Verify timeseries:**
```bash
docker exec -it kuberan-mongodb mongosh kuberan --eval "
  db.getCollectionInfos({name: 'provider_api_calls'}).forEach(info => {
    print('Collection:', info.name);
    print('Type:', info.type);
    print('Options:', JSON.stringify(info.options, null, 2));
  })
"
```

---

## Next Steps

1. ✅ Run TTL migration (Step 1)
2. ✅ Add decorators to all provider methods (Step 2)
3. ✅ Test and verify tracking (Step 3)
4. ✅ Create daily aggregation job (Step 4)
5. ✅ Add monitoring endpoints (Step 5)
6. ✅ Test monitoring API (Step 6)
7. 🔄 **Optional:** Build monitoring dashboard UI
8. 🔄 **Optional:** Add alerting (email/SMS on failures)
9. 🔄 **Optional:** Create cost estimation reports

---

**Last Updated:** November 16, 2025
