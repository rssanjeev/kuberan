# API Metrics Query Guide

How to query Kuberan's API call tracking data via REST API or MongoDB directly.

**Last Updated:** November 16, 2025

---

## Option 1: REST API Endpoints (Recommended)

After restarting the backend, you can query metrics via HTTP endpoints.

### 📊 **Get Summary for All Providers (Today)**

```bash
curl http://localhost:8000/monitoring/providers/summary | python3 -m json.tool
```

**Response:**
```json
{
  "providers": [
    {
      "provider": "yfinance",
      "total_calls_today": 145,
      "successful_calls": 142,
      "failed_calls": 3,
      "rate_limited_calls": 0,
      "timeout_calls": 0,
      "success_rate": 0.9793,
      "avg_response_time_ms": 156.32
    },
    {
      "provider": "alpha_vantage",
      "total_calls_today": 23,
      "successful_calls": 20,
      "failed_calls": 2,
      "rate_limited_calls": 1,
      "timeout_calls": 0,
      "success_rate": 0.8696,
      "avg_response_time_ms": 234.15
    },
    {
      "provider": "finnhub",
      "total_calls_today": 8,
      "successful_calls": 8,
      "failed_calls": 0,
      "rate_limited_calls": 0,
      "timeout_calls": 0,
      "success_rate": 1.0,
      "avg_response_time_ms": 189.45
    }
  ],
  "as_of": "2025-11-16T10:45:23.123Z"
}
```

---

### 📈 **Get Daily Statistics (Last 7 Days)**

```bash
# yfinance stats
curl http://localhost:8000/monitoring/providers/yfinance/stats?days=7 | python3 -m json.tool

# Alpha Vantage stats (last 30 days)
curl http://localhost:8000/monitoring/providers/alpha_vantage/stats?days=30 | python3 -m json.tool
```

**Response:**
```json
{
  "provider": "yfinance",
  "period_days": 7,
  "stats_count": 7,
  "daily_stats": [
    {
      "date": "2025-11-16T00:00:00Z",
      "total_calls": 145,
      "successful_calls": 142,
      "failed_calls": 3,
      "rate_limited_calls": 0,
      "timeout_calls": 0,
      "success_rate": 0.9793,
      "avg_response_time_ms": 156.32,
      "min_response_time_ms": 45,
      "max_response_time_ms": 890,
      "calls_by_data_type": {
        "quote": 80,
        "historical": 40,
        "news": 20,
        "dividends": 5
      },
      "estimated_cost": 0.0,
      "uptime_percentage": 97.93
    }
    // ... 6 more days
  ]
}
```

---

### 🔍 **Get Recent API Calls**

```bash
# Last 50 calls for yfinance
curl http://localhost:8000/monitoring/providers/yfinance/recent-calls?limit=50 | python3 -m json.tool

# Only failed calls
curl "http://localhost:8000/monitoring/providers/alpha_vantage/recent-calls?status=failure&limit=20" | python3 -m json.tool

# Only quote calls
curl "http://localhost:8000/monitoring/providers/yfinance/recent-calls?data_type=quote&limit=100" | python3 -m json.tool

# Failed calls for specific data type
curl "http://localhost:8000/monitoring/providers/finnhub/recent-calls?status=failure&data_type=news" | python3 -m json.tool
```

**Response:**
```json
{
  "provider": "yfinance",
  "count": 50,
  "filters": {
    "status": null,
    "data_type": null
  },
  "calls": [
    {
      "timestamp": "2025-11-16T10:44:15.123Z",
      "data_type": "quote",
      "status": "success",
      "response_time_ms": 145,
      "ticker": "AAPL",
      "endpoint": null,
      "error_message": null,
      "http_status_code": 200
    },
    {
      "timestamp": "2025-11-16T10:43:28.456Z",
      "data_type": "historical",
      "status": "success",
      "response_time_ms": 234,
      "ticker": "TSLA",
      "endpoint": null,
      "error_message": null,
      "http_status_code": 200
    }
    // ... 48 more calls
  ]
}
```

---

### ⚡ **Get Performance Metrics**

```bash
# Last 24 hours
curl http://localhost:8000/monitoring/providers/yfinance/performance?hours=24 | python3 -m json.tool

# Last week
curl http://localhost:8000/monitoring/providers/alpha_vantage/performance?hours=168 | python3 -m json.tool
```

**Response:**
```json
{
  "provider": "yfinance",
  "period_hours": 24,
  "total_calls": 145,
  "status_breakdown": {
    "successful": 142,
    "failed": 3,
    "rate_limited": 0,
    "timeout": 0
  },
  "success_rate": 0.9793,
  "response_times": {
    "avg_ms": 156.32,
    "min_ms": 45,
    "max_ms": 890,
    "p50_ms": 142.5,
    "p95_ms": 456.8
  },
  "data_type_breakdown": {
    "quote": 80,
    "historical": 40,
    "news": 20,
    "dividends": 5
  },
  "recent_errors": [
    {
      "timestamp": "2025-11-16T08:30:12.456Z",
      "data_type": "historical",
      "error_message": "Connection timeout",
      "http_status_code": null
    }
  ]
}
```

---

### 🌐 **Get All Recent Calls (Across Providers)**

```bash
# Last 100 calls from all providers (last 24 hours)
curl "http://localhost:8000/monitoring/calls/all?limit=100&hours=24" | python3 -m json.tool

# Last 50 calls from all providers (last 6 hours)
curl "http://localhost:8000/monitoring/calls/all?limit=50&hours=6" | python3 -m json.tool
```

**Response:**
```json
{
  "count": 100,
  "period_hours": 24,
  "calls": [
    {
      "timestamp": "2025-11-16T10:44:15.123Z",
      "provider": "yfinance",
      "data_type": "quote",
      "status": "success",
      "response_time_ms": 145,
      "ticker": "AAPL",
      "error_message": null
    },
    {
      "timestamp": "2025-11-16T10:43:45.789Z",
      "provider": "alpha_vantage",
      "data_type": "news",
      "status": "rate_limited",
      "response_time_ms": null,
      "ticker": "TSLA",
      "error_message": "Rate limit exceeded"
    }
    // ... 98 more calls
  ]
}
```

---

### 📊 **Get Aggregated Statistics**

```bash
# Last 7 days aggregate
curl http://localhost:8000/monitoring/stats/aggregate?days=7 | python3 -m json.tool

# Last 30 days aggregate
curl http://localhost:8000/monitoring/stats/aggregate?days=30 | python3 -m json.tool
```

**Response:**
```json
{
  "period_days": 7,
  "providers": [
    {
      "provider": "yfinance",
      "total_calls": 1015,
      "successful_calls": 994,
      "failed_calls": 21,
      "rate_limited_calls": 0,
      "timeout_calls": 0,
      "success_rate": 0.9793,
      "avg_response_time_ms": 156.32
    },
    {
      "provider": "alpha_vantage",
      "total_calls": 161,
      "successful_calls": 140,
      "failed_calls": 14,
      "rate_limited_calls": 7,
      "timeout_calls": 0,
      "success_rate": 0.8696,
      "avg_response_time_ms": 234.15
    },
    {
      "provider": "finnhub",
      "total_calls": 56,
      "successful_calls": 56,
      "failed_calls": 0,
      "rate_limited_calls": 0,
      "timeout_calls": 0,
      "success_rate": 1.0,
      "avg_response_time_ms": 189.45
    }
  ],
  "grand_total": 1232
}
```

---

## Option 2: Query MongoDB Directly

If you prefer direct database access:

```bash
# Access MongoDB shell
docker exec -it kuberan-mongodb mongosh kuberan
```

### 🔍 **Common MongoDB Queries**

#### 1. Count Total Calls Today

```javascript
const today = new Date();
today.setHours(0,0,0,0);

db.provider_api_calls.countDocuments({
  timestamp: {$gte: today}
})
```

#### 2. Get Calls by Provider (Last 24 Hours)

```javascript
const yesterday = new Date(Date.now() - 24*60*60*1000);

db.provider_api_calls.find({
  provider: "yfinance",
  timestamp: {$gte: yesterday}
}).sort({timestamp: -1}).limit(20)
```

#### 3. Success Rate by Provider

```javascript
db.provider_api_calls.aggregate([
  {$group: {
    _id: "$provider",
    total: {$sum: 1},
    successful: {
      $sum: {$cond: [{$eq: ["$status", "success"]}, 1, 0]}
    },
    failed: {
      $sum: {$cond: [{$eq: ["$status", "failure"]}, 1, 0]}
    }
  }},
  {$project: {
    provider: "$_id",
    total: 1,
    successful: 1,
    failed: 1,
    success_rate: {
      $divide: ["$successful", "$total"]
    }
  }},
  {$sort: {total: -1}}
])
```

#### 4. Average Response Time by Provider

```javascript
db.provider_api_calls.aggregate([
  {$match: {
    response_time_ms: {$ne: null}
  }},
  {$group: {
    _id: "$provider",
    avg_response_ms: {$avg: "$response_time_ms"},
    min_response_ms: {$min: "$response_time_ms"},
    max_response_ms: {$max: "$response_time_ms"},
    call_count: {$sum: 1}
  }},
  {$sort: {avg_response_ms: 1}}
])
```

#### 5. Calls by Data Type

```javascript
db.provider_api_calls.aggregate([
  {$group: {
    _id: {
      provider: "$provider",
      data_type: "$data_type"
    },
    count: {$sum: 1}
  }},
  {$sort: {count: -1}}
])
```

#### 6. Recent Failed Calls with Errors

```javascript
db.provider_api_calls.find({
  status: "failure",
  error_message: {$ne: null}
}).sort({timestamp: -1}).limit(10)
```

#### 7. Rate Limited Calls

```javascript
db.provider_api_calls.find({
  status: "rate_limited"
}).sort({timestamp: -1}).limit(20)
```

#### 8. Slowest Calls (Last 24 Hours)

```javascript
const yesterday = new Date(Date.now() - 24*60*60*1000);

db.provider_api_calls.find({
  timestamp: {$gte: yesterday},
  response_time_ms: {$gt: 1000}  // Over 1 second
}).sort({response_time_ms: -1}).limit(20)
```

#### 9. Hourly Call Distribution

```javascript
db.provider_api_calls.aggregate([
  {$match: {
    timestamp: {$gte: new Date(Date.now() - 24*60*60*1000)}
  }},
  {$group: {
    _id: {
      hour: {$hour: "$timestamp"},
      provider: "$provider"
    },
    count: {$sum: 1}
  }},
  {$sort: {"_id.hour": 1}}
])
```

#### 10. Error Message Frequency

```javascript
db.provider_api_calls.aggregate([
  {$match: {
    error_message: {$ne: null}
  }},
  {$group: {
    _id: "$error_message",
    count: {$sum: 1},
    providers: {$addToSet: "$provider"}
  }},
  {$sort: {count: -1}}
])
```

---

## Restart Backend to Enable Endpoints

```bash
# Restart backend container
docker-compose restart backend

# Watch logs
docker logs -f kuberan-backend-1

# Verify monitoring endpoints are available
curl http://localhost:8000/docs
# Look for "/monitoring" endpoints in Swagger UI
```

---

## Interactive Swagger UI

After restarting, visit:

**http://localhost:8000/docs**

Look for the **"monitoring"** tag with these endpoints:

- `GET /monitoring/providers/summary` - Summary for all providers
- `GET /monitoring/providers/{provider}/stats` - Daily statistics
- `GET /monitoring/providers/{provider}/recent-calls` - Recent API calls
- `GET /monitoring/providers/{provider}/performance` - Performance metrics
- `GET /monitoring/calls/all` - All recent calls (cross-provider)
- `GET /monitoring/stats/aggregate` - Aggregated statistics

You can test all endpoints interactively in the Swagger UI!

---

## Quick Testing Script

Create a test script to verify tracking is working:

```bash
#!/bin/bash
# test_monitoring.sh

echo "=== Provider Summary ==="
curl -s http://localhost:8000/monitoring/providers/summary | python3 -m json.tool

echo -e "\n=== yfinance Recent Calls (Last 10) ==="
curl -s "http://localhost:8000/monitoring/providers/yfinance/recent-calls?limit=10" | python3 -m json.tool

echo -e "\n=== Alpha Vantage Performance (Last 24h) ==="
curl -s "http://localhost:8000/monitoring/providers/alpha_vantage/performance?hours=24" | python3 -m json.tool

echo -e "\n=== All Providers Aggregate (Last 7 Days) ==="
curl -s "http://localhost:8000/monitoring/stats/aggregate?days=7" | python3 -m json.tool
```

```bash
chmod +x test_monitoring.sh
./test_monitoring.sh
```

---

## Monitoring Dashboard Ideas

Once you have the data, you can build dashboards showing:

1. **Real-time Status Board**
   - Current success rate per provider
   - Calls per minute/hour
   - Average response times

2. **Cost Tracking**
   - Calls per day vs. free tier limits
   - Projected monthly costs
   - Provider usage distribution

3. **Performance Comparison**
   - Response time charts per provider
   - Success rate trends
   - Reliability scores

4. **Error Analysis**
   - Common error messages
   - Failure patterns
   - Provider downtime incidents

5. **Usage Analytics**
   - Popular tickers
   - Most requested data types
   - Peak usage hours

---

**Last Updated:** November 16, 2025
