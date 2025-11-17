# API Metrics Tracking System

## Overview

Kuberan tracks **all API calls** to external providers (Alpha Vantage, Finnhub, yfinance) in MongoDB for monitoring, cost optimization, and performance analysis.

**Last Updated:** November 16, 2025

---

## Why Track API Calls?

### 1. **Cost Monitoring**
- Track API usage against free tier limits
- Estimate costs for premium tiers
- Optimize provider selection to minimize costs
- Alert when approaching rate limits

### 2. **Performance Monitoring**
- Measure response times per provider
- Identify slow providers
- Detect performance degradation
- Optimize data fetching strategies

### 3. **Reliability Tracking**
- Monitor success/failure rates per provider
- Detect provider outages
- Automatic provider switching on failures
- Historical reliability analysis

### 4. **Usage Analytics**
- Which data types are most requested?
- Which tickers are most popular?
- Peak usage times
- Provider distribution

---

## Architecture

### Data Models (MongoDB Collections)

#### 1. **ProviderAPICall** (Timeseries, 30-day TTL)

Tracks every individual API call with full details.

**Schema:**
```python
{
    "provider": "alpha_vantage",           # Provider name
    "data_type": "quote",                   # Type of data requested
    "timestamp": "2025-11-16T10:30:00Z",   # When call was made
    "status": "success",                    # success|failure|timeout|rate_limited
    "response_time_ms": 145,                # Response time in milliseconds
    "ticker": "AAPL",                       # Ticker symbol (if applicable)
    "endpoint": "/query?function=QUOTE",    # API endpoint
    "error_message": null,                  # Error if failed
    "http_status_code": 200,                # HTTP status code
    "metadata": {}                          # Additional context
}
```

**Features:**
- **Timeseries collection** for optimal query performance
- **30-day TTL** - automatic deletion of old records
- **Indexed** by provider, timestamp, status, ticker

**Use Cases:**
- Real-time monitoring dashboards
- Recent API call history
- Debugging failed calls
- Performance analysis

---

#### 2. **ProviderDailyStats** (Permanent Storage)

Daily aggregated statistics per provider.

**Schema:**
```python
{
    "provider": "yfinance",
    "date": "2025-11-16T00:00:00Z",        # Date (midnight UTC)
    "total_calls": 1247,                    # Total API calls
    "successful_calls": 1198,               # Successful calls
    "failed_calls": 42,                     # Failed calls
    "rate_limited_calls": 5,                # Rate limited
    "timeout_calls": 2,                     # Timeouts
    "avg_response_time_ms": 156.3,          # Average response time
    "min_response_time_ms": 45,             # Fastest response
    "max_response_time_ms": 3200,           # Slowest response
    "calls_by_data_type": {                 # Breakdown by data type
        "quote": 800,
        "historical": 300,
        "news": 100,
        "dividends": 47
    },
    "estimated_cost": 0.00,                 # Cost estimate
    "success_rate": 0.961,                  # 96.1% success rate
    "uptime_percentage": 98.5               # Uptime %
}
```

**Features:**
- **Permanent storage** for historical analysis
- **Aggregated** from ProviderAPICall records
- **Daily background job** computes statistics
- **Unique index** on (provider, date)

**Use Cases:**
- Historical trend analysis
- Month-over-month comparisons
- Provider reliability reports
- Cost projections

---

#### 3. **ProviderHealthCheck** (Timeseries, 7-day TTL)

Provider health check results.

**Schema:**
```python
{
    "provider": "finnhub",
    "timestamp": "2025-11-16T10:35:00Z",
    "is_healthy": true,                     # Operational status
    "status_code": 200,                     # HTTP status
    "response_time_ms": 89,                 # Health check response time
    "consecutive_failures": 0,              # Failure streak
    "reliability_score": 0.98,              # Current reliability (0.0-1.0)
    "error_message": null                   # Error if unhealthy
}
```

**Features:**
- **7-day retention** for health history
- **Periodic checks** (every 5 minutes)
- **Reliability scoring** algorithm

**Use Cases:**
- Provider status dashboard
- Alert on provider downtime
- Automatic provider switching
- SLA monitoring

---

#### 4. **RateLimitStatus** (Timeseries, 1-hour TTL)

Current rate limit status per provider.

**Schema:**
```python
{
    "provider": "alpha_vantage",
    "timestamp": "2025-11-16T10:40:00Z",
    "limit_per_minute": 5,                  # Max calls/minute
    "limit_per_day": 25,                    # Max calls/day
    "limit_per_month": null,                # Max calls/month
    "calls_this_minute": 3,                 # Current minute usage
    "calls_today": 18,                      # Today's usage
    "calls_this_month": 456,                # Month's usage
    "remaining_minute": 2,                  # Remaining this minute
    "remaining_today": 7,                   # Remaining today
    "remaining_month": null,
    "minute_resets_at": "2025-11-16T10:41:00Z",
    "day_resets_at": "2025-11-17T00:00:00Z",
    "month_resets_at": "2025-12-01T00:00:00Z",
    "pricing_tier": "free"                  # free|premium
}
```

**Features:**
- **1-hour TTL** (only recent status needed)
- **Real-time tracking** of rate limits
- **Reset time calculations**

**Use Cases:**
- Rate limit warnings
- Automatic provider switching near limits
- Cost optimization (preserve expensive providers)
- Pricing tier management

---

## Usage

### 1. **Automatic Tracking (Recommended)**

Use the `@api_metrics.track_api_call` decorator:

```python
from app.core.api_metrics import api_metrics

class YFinanceProvider(BaseProvider):
    
    @api_metrics.track_api_call(
        provider="yfinance",
        data_type="quote"
    )
    async def fetch_real_time_quote(self, ticker: str) -> Dict:
        """Automatically tracked - no manual logging needed."""
        stock = yf.Ticker(ticker)
        return stock.info
```

**Benefits:**
- Automatic success/failure tracking
- Response time measurement
- Error capture with stack traces
- Zero boilerplate code

---

### 2. **Manual Tracking**

For custom scenarios:

```python
from app.core.api_metrics import api_metrics
from app.models.monitoring import CallStatus

async def custom_api_call():
    start_time = time.time()
    
    try:
        result = await external_api_call()
        status = CallStatus.SUCCESS
    except RateLimitError:
        status = CallStatus.RATE_LIMITED
        raise
    except Exception as e:
        status = CallStatus.FAILURE
        raise
    finally:
        response_time = int((time.time() - start_time) * 1000)
        
        await api_metrics.record_call(
            provider="custom_provider",
            data_type="custom_data",
            status=status,
            response_time_ms=response_time,
            ticker="AAPL",
            error_message=str(e) if status != CallStatus.SUCCESS else None
        )
```

---

### 3. **Daily Aggregation (Background Job)**

Run as a daily cron job to compute statistics:

```python
from app.core.api_metrics import api_metrics

# Aggregate yesterday's data for all providers
async def daily_aggregation_job():
    providers = ["alpha_vantage", "finnhub", "yfinance"]
    
    for provider in providers:
        stats = await api_metrics.aggregate_daily_stats(provider)
        
        if stats:
            logger.info(
                f"Daily stats: {provider}",
                extra={
                    "total_calls": stats.total_calls,
                    "success_rate": stats.success_rate
                }
            )
```

---

## Queries & Analytics

### Get Today's API Calls by Provider

```python
from datetime import datetime, timedelta
from app.models.monitoring import ProviderAPICall

# Get all calls today for Alpha Vantage
today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
calls = await ProviderAPICall.find(
    ProviderAPICall.provider == "alpha_vantage",
    ProviderAPICall.timestamp >= today_start
).to_list()

print(f"Alpha Vantage calls today: {len(calls)}")
```

### Get Provider Success Rate (Last 7 Days)

```python
from app.models.monitoring import ProviderDailyStats

# Get last 7 days of stats
week_ago = datetime.utcnow() - timedelta(days=7)
stats = await ProviderDailyStats.find(
    ProviderDailyStats.provider == "yfinance",
    ProviderDailyStats.date >= week_ago
).to_list()

# Calculate average success rate
avg_success_rate = sum(s.success_rate for s in stats) / len(stats)
print(f"yfinance 7-day success rate: {avg_success_rate:.2%}")
```

### Get API Calls by Data Type (Today)

```python
# Aggregate by data type
pipeline = [
    {"$match": {
        "provider": "finnhub",
        "timestamp": {"$gte": today_start}
    }},
    {"$group": {
        "_id": "$data_type",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]

result = await ProviderAPICall.aggregate(pipeline).to_list()

# Output:
# [
#   {"_id": "quote", "count": 450},
#   {"_id": "news", "count": 120},
#   {"_id": "earnings", "count": 30}
# ]
```

### Get Slowest API Calls (Last Hour)

```python
hour_ago = datetime.utcnow() - timedelta(hours=1)

slow_calls = await ProviderAPICall.find(
    ProviderAPICall.timestamp >= hour_ago,
    ProviderAPICall.response_time_ms > 2000  # Over 2 seconds
).sort([("response_time_ms", -1)]).limit(10).to_list()

for call in slow_calls:
    print(f"{call.provider} - {call.data_type}: {call.response_time_ms}ms")
```

### Check Rate Limit Status

```python
from app.core.api_metrics import api_metrics

status = await api_metrics.get_rate_limit_status("alpha_vantage")

if status:
    print(f"Remaining today: {status.remaining_today} / {status.limit_per_day}")
    
    if status.remaining_today < 5:
        logger.warning("Alpha Vantage near daily limit!")
```

---

## API Endpoints (Monitoring Dashboard)

### Get Provider Statistics

```python
# backend/app/routers/monitoring.py

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from app.models.monitoring import ProviderDailyStats, ProviderAPICall

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/providers/{provider}/stats")
async def get_provider_stats(
    provider: str,
    days: int = Query(7, le=90)
):
    """Get daily statistics for provider over N days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = await ProviderDailyStats.find(
        ProviderDailyStats.provider == provider,
        ProviderDailyStats.date >= start_date
    ).sort([("date", -1)]).to_list()
    
    return {
        "provider": provider,
        "period_days": days,
        "daily_stats": [
            {
                "date": s.date.isoformat(),
                "total_calls": s.total_calls,
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
    limit: int = Query(100, le=1000)
):
    """Get most recent API calls for provider."""
    calls = await ProviderAPICall.find(
        ProviderAPICall.provider == provider
    ).sort([("timestamp", -1)]).limit(limit).to_list()
    
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
                "error_message": c.error_message
            }
            for c in calls
        ]
    }

@router.get("/providers/summary")
async def get_all_providers_summary():
    """Get summary for all providers today."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    
    providers = ["alpha_vantage", "finnhub", "yfinance"]
    summaries = []
    
    for provider in providers:
        calls = await ProviderAPICall.find(
            ProviderAPICall.provider == provider,
            ProviderAPICall.timestamp >= today_start
        ).to_list()
        
        total = len(calls)
        successful = sum(1 for c in calls if c.status == CallStatus.SUCCESS)
        
        summaries.append({
            "provider": provider,
            "total_calls_today": total,
            "successful_calls": successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_response_time_ms": sum(c.response_time_ms or 0 for c in calls) / total if total > 0 else 0
        })
    
    return {"providers": summaries, "as_of": datetime.utcnow().isoformat()}
```

---

## TTL Configuration

Collections are automatically cleaned up via MongoDB TTL:

| Collection | TTL | Reason |
|------------|-----|--------|
| **provider_api_calls** | 30 days | Recent history for debugging |
| **provider_health_checks** | 7 days | Short-term health monitoring |
| **rate_limit_status** | 1 hour | Only current status needed |
| **provider_daily_stats** | ∞ (permanent) | Historical analysis |

Run TTL migration script to configure:

```bash
docker exec -w /app kuberan-backend-1 \
  python3 -m app.scripts.configure_timeseries_ttl
```

---

## Benefits

### ✅ **Cost Optimization**
- Know exactly how many API calls you're making
- Stay within free tier limits
- Switch to cheaper providers when possible
- Estimate premium tier costs accurately

### ✅ **Performance Monitoring**
- Identify slow providers
- Optimize data fetching strategies
- Detect performance degradation early
- Compare provider response times

### ✅ **Reliability Tracking**
- Monitor provider uptime
- Automatic failover to backup providers
- Historical reliability analysis
- SLA compliance tracking

### ✅ **Usage Analytics**
- Understand data access patterns
- Optimize caching strategies
- Plan for scaling
- Identify popular tickers/data types

### ✅ **Debugging & Troubleshooting**
- Full audit trail of API calls
- Error messages and stack traces
- Response time analysis
- Reproduce and diagnose failures

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic API call tracking
- ✅ Daily statistics aggregation
- ✅ Rate limit monitoring
- ✅ Health checks

### Phase 2 (Planned)
- 🔄 Real-time dashboard UI
- 🔄 Cost estimation per provider
- 🔄 Alert notifications (email/SMS)
- 🔄 Provider performance comparison charts

### Phase 3 (Future)
- 📋 Machine learning for usage prediction
- 📋 Automatic provider tier recommendations
- 📋 Cost optimization suggestions
- 📋 Anomaly detection

---

## Summary

Kuberan's API metrics tracking system provides:

- **Complete visibility** into provider usage
- **Automatic tracking** with decorator pattern
- **MongoDB storage** with timeseries optimization
- **30-day detailed history** + permanent daily stats
- **Rate limit monitoring** to avoid overages
- **Performance analytics** for optimization
- **Cost tracking** for budgeting

**Track everything. Optimize confidently. Scale intelligently.**
