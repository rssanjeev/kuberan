# Kuberan API Documentation

**Base URL:** `http://localhost:8000`

**Last Updated:** November 30, 2025

---

## Table of Contents

### Core Domains
1. [Stock Information Endpoints](#stock-information-endpoints) *(5 endpoints)*
2. [Market Status Endpoints](#market-status-endpoints)
3. [Financier - Financial Analytics Endpoints](#financier---financial-analytics-endpoints)
4. [ETF Analysis Endpoints](#etf-analysis-endpoints) *(67 endpoints)*

### System Management
7. [System Management Endpoints](#system-management-endpoints)
8. [Monitoring Endpoints](#monitoring-endpoints)
9. [Metadata Enrichment Endpoints](#metadata-enrichment-endpoints)
10. [Precious Metals Endpoints](#precious-metals-endpoints)

### Authentication
11. [Authentication Endpoints](#authentication-endpoints)

---

## Overview

Kuberan provides a comprehensive REST API for:
- **Stock Tracker**: Real-time price monitoring and metadata enrichment (12,140 tickers)
- **Financier**: Credit card statement processing and transaction analytics
- **ETF Analysis**: Comprehensive ETF research and portfolio management (67 endpoints)
- **System Management**: Provider status, job scheduling, and monitoring
- **Metadata Enrichment**: Multi-provider ticker metadata collection (MASSIVE/Polygon.io)

---

## Stock Information Endpoints

> **Note:** For ticker management and discovery, use `/system/metadata/*` endpoints.
> Stock endpoints are query-focused only (price, history, market info).

### List All Tickers with Metadata
Get a paginated, filtered list of all tickers with full metadata (from CompanyOverview).

**Endpoint:** `GET /stocks/tickers`

**Query Parameters:**
- `enrichment_status` (optional): Filter by enrichment status (`base`, `foundation`, `enriched`, `failed`)
- `asset_type` (optional): Filter by asset type (`Stock`, `ETF`)
- `search` (optional): Substring match on ticker or name
- `sort_by` (optional): `market_cap`, `ticker`, `name` (default: `market_cap`)
- `sort_order` (optional): `asc`, `desc` (default: `desc`)
- `limit` (optional): Max results (default: 100, max: 1000)
- `skip` (optional): Pagination offset (default: 0)

**Example:**
`GET /stocks/tickers?enrichment_status=foundation&asset_type=Stock&search=apple&sort_by=market_cap&sort_order=desc&limit=50&skip=0`

**Response:**
```json
{
  "total": 12140,
  "returned": 50,
  "skip": 0,
  "limit": 50,
  "tickers": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "market_cap": 2500000000000,
      "enrichment_status": "foundation",
      "asset_type": "Stock",
      "exchange": "NASDAQ",
      "country": "USA",
      "fetched_at": "2025-11-30T10:00:00Z"
    }
    // ...more tickers
  ]
}
```

**Errors:**
- `400 Bad Request` - Invalid query parameters
- `500 Internal Server Error` - Server error

### Get Ticker Types
Get official ticker type classifications from MASSIVE API.

**Endpoint:** `GET /stocks/tickers/types`

**Query Parameters:**
- `asset_class` (optional): Filter by asset class (`stocks`, `options`, `crypto`, `fx`, `indices`)
- `locale` (optional): Filter by locale (`us`, `global`)

**Example:** `GET /stocks/tickers/types?asset_class=stocks`

**Response:**
```json
{
  "count": 24,
  "results": [
    {
      "code": "CS",
      "description": "Common Stock",
      "asset_class": "stocks",
      "locale": "us"
    },
    {
      "code": "ETF",
      "description": "Exchange Traded Fund",
      "asset_class": "stocks",
      "locale": "us"
    },
    {
      "code": "ADRC",
      "description": "American Depository Receipt Common",
      "asset_class": "stocks",
      "locale": "us"
    },
    {
      "code": "PFD",
      "description": "Preferred Stock",
      "asset_class": "stocks",
      "locale": "us"
    },
    {
      "code": "WARRANT",
      "description": "Warrant",
      "asset_class": "stocks",
      "locale": "us"
    }
  ]
}
```

**Common Ticker Types:**
- **CS** - Common Stock
- **ETF** - Exchange Traded Fund
- **ADRC** - American Depository Receipt Common
- **ADRP** - American Depository Receipt Preferred
- **ADRR** - American Depository Receipt Rights
- **ADRW** - American Depository Receipt Warrants
- **PFD** - Preferred Stock
- **WARRANT** - Warrant
- **RIGHT** - Rights
- **UNIT** - Unit
- **FUND** - Fund
- **ETN** - Exchange Traded Note
- **BOND** - Corporate Bond

**Use Cases:**
- Filter tickers by security type
- Validate ticker classifications
- Educational reference for security types
- System integration and data classification

**Example Requests:**
```bash
# Get all ticker types
curl http://localhost:8000/stocks/tickers/types

# Filter by asset class
curl "http://localhost:8000/stocks/tickers/types?asset_class=stocks"

# Filter by locale
curl "http://localhost:8000/stocks/tickers/types?locale=us"
```

**Errors:**
- `500 Internal Server Error` - Failed to fetch ticker types

**Notes:**
- Data cached permanently (types rarely change)
- Free tier compatible
- 24 types available for stocks/us
- Run `fetch_ticker_types.py` script once to populate database

### Get Stock Information
Get current stock information for a specific ticker.

**Endpoint:** `GET /stocks/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol (e.g., AAPL)

**Example:** `GET /stocks/NVDA`

**Response:**
```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "current_price": 194.63,
  "change": 2.15,
  "change_percent": 1.12,
  "market_cap": 4782000000000,
  "sector": "Technology",
  "industry": "Semiconductors"
}
```

**Errors:**
- `404 Not Found` - Stock data not found for ticker

---

### Get Stock History
Get historical OHLCV price data for a specific ticker. Supports two query modes:
1. **Period-based** (Yahoo Finance): Fetch fresh data and optionally cache
2. **Date-range** (Database cache): Query previously cached data (fast)

**Endpoint:** `GET /stocks/history/{ticker}`

**Parameters:**
- `ticker` (path, required) - Stock ticker symbol

**Period-based Query Parameters:**
- `period` (query, optional) - Time period (default: `1mo`)
  - Valid values: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`
- `interval` (query, optional) - Data interval (default: `1d`)
  - Valid values: `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`, `1mo`
  - Note: Intraday intervals (1m-1h) limited to last 60 days
- `cache` (query, optional) - Cache fetched data in database (default: `true`)

**Date-range Query Parameters (Cache Mode):**
- `start_date` (query) - Start date in `YYYY-MM-DD` format
- `end_date` (query) - End date in `YYYY-MM-DD` format
- `interval` (query, optional) - Data interval (default: `1d`)

**Example - Period-based (Fetch and Cache):**  
`GET /stocks/history/AAPL?period=1y&interval=1d&cache=true`

**Response (Period-based):**
```json
{
  "ticker": "AAPL",
  "period": "1y",
  "interval": "1d",
  "source": "yfinance",
  "count": 250,
  "cached_count": 250,
  "data": [
    {
      "Date": "2024-12-04T00:00:00-05:00",
      "Open": 177.26,
      "High": 179.0,
      "Low": 175.99,
      "Close": 178.85,
      "Volume": 20135600,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    }
    // ...249 more records
  ]
}
```

**Example - Date-range (Cache Query):**  
`GET /stocks/history/AAPL?start_date=2024-01-01&end_date=2024-12-31&interval=1d`

**Response (Date-range):**
```json
{
  "ticker": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "source": "cache",
  "count": 250,
  "data": [
    {
      "Date": "2024-01-02",
      "Open": 177.26,
      "High": 179.0,
      "Low": 175.99,
      "Close": 178.85,
      "Volume": 20135600,
      "Adj Close": null
    }
    // ...249 more records
  ]
}
```

**Fields Returned:**
- `Date` - Trading date with timezone (period-based) or YYYY-MM-DD (cache)
- `Open` - Opening price
- `High` - Highest price
- `Low` - Lowest price
- `Close` - Closing price
- `Volume` - Trading volume
- `Adj Close` - Adjusted close (null in cache mode)
- `Dividends` - Dividend amount (0.0 if none)
- `Stock Splits` - Split ratio (0.0 if none)

**Caching Strategy:**
- **Automatic**: Data is cached by default when using period-based queries
- **Storage**: MongoDB `stock_historical_prices` collection with 5-year TTL
- **Duplicates**: Automatically prevented (re-fetching same data won't duplicate)
- **Growth**: Organic - data cached only when requested or via background job
- **Benefits**: Fast subsequent queries, reduced API calls, historical analysis

**Background Job - Automated Backfill:**
A daily background job gradually populates the historical price cache for all active tickers:
- **Schedule**: Every day at 6:00 PM EST
- **Batch Size**: 10 tickers per run
- **Data Range**: 5 years of daily OHLCV data (~1,260 records per ticker)
- **Throughput**: ~12,600 records per day
- **Coverage Timeline**: All active foundation-enriched tickers backfilled over ~4 months
- **Rate Limiting**: 12-second delays between API calls (respects Yahoo Finance limits)
- **Tracking**: Tickers marked with `backfill_complete` flag to prevent re-processing
- **Purpose**: Ensures fast queries for technical analysis, charting, and backtesting without repeated Yahoo Finance calls

**Use Cases:**
1. **Initial fetch with caching**: `?period=5y` (cache 5 years of data)
2. **Fast cached queries**: `?start_date=2024-01-01&end_date=2024-12-31`
3. **Technical indicator data**: `?period=2y` (enough for 200-day SMA calculations)
4. **Backtesting**: Fetch max available history with `?period=max`

**Errors:**
- `404 Not Found` - No historical data available (period-based) or no cached data (date-range)
- `400 Bad Request` - Invalid period, interval, or date format

---

### Get Stock Price
Get just the current price for a specific ticker (lightweight endpoint).

**Endpoint:** `GET /stocks/price/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol

**Example:** `GET /stocks/price/AAPL`

**Response:**
```json
{
  "ticker": "AAPL",
  "current_price": 178.45,
  "timestamp": "2025-11-11T19:15:00"
}
```

**Errors:**
- `404 Not Found` - Price not found for ticker

---

## Market Status Endpoints

### Get Market Status
Check if the NYSE market is open today.

**Endpoint:** `GET /stocks/market/status`

**Response:**
```json
{
  "date": "2025-11-11",
  "is_market_open": true,
  "message": "Market is open for trading"
}
```

**Note:** Uses NYSE calendar to determine market status, accounting for holidays and weekends.

---

## Provider Configuration Endpoints

### Get Provider Routing Configuration
Get transparency into the multi-provider data routing strategy showing which data type comes from which provider (YFinance, Alpha Vantage, Finnhub).

**Endpoint:** `GET /stocks/config/routing`

**Response:**
```json
{
  "routing_strategy": {
    "quote": {
      "primary": "yfinance",
      "fallback": ["alpha_vantage", "finnhub"],
      "reason": "YFinance free tier with good coverage, unlimited API calls",
      "data_points": [
        "price", "open", "high", "low", "volume", 
        "change", "change_percent", "timestamp"
      ]
    },
    "historical_prices": {
      "primary": "yfinance",
      "fallback": ["alpha_vantage"],
      "reason": "YFinance provides comprehensive OHLCV data for free",
      "data_points": [
        "date", "open", "high", "low", "close", "volume"
      ]
    },
    "company_overview": {
      "primary": "alpha_vantage",
      "fallback": ["finnhub"],
      "reason": "AlphaVantage provides comprehensive company fundamentals",
      "data_points": [
        "sector", "industry", "description", "market_cap", 
        "pe_ratio", "dividend_yield", "52_week_high", "52_week_low"
      ]
    },
    "fundamentals": {
      "primary": "alpha_vantage",
      "fallback": [],
      "reason": "Only AlphaVantage provides detailed financial statements via API",
      "data_points": [
        "income_statement", "balance_sheet", "cash_flow", 
        "earnings", "revenue", "profit_margin"
      ]
    },
    "technical_indicators": {
      "primary": "alpha_vantage",
      "fallback": [],
      "reason": "AlphaVantage offers 50+ technical indicators via dedicated endpoints",
      "data_points": [
        "SMA", "EMA", "RSI", "MACD", "BBANDS", "ADX", "STOCH"
      ]
    },
    "dividends": {
      "primary": "yfinance",
      "fallback": ["alpha_vantage"],
      "reason": "YFinance provides historical dividend data for free",
      "data_points": [
        "ex_dividend_date", "payment_date", "amount", "frequency"
      ]
    },
    "splits": {
      "primary": "yfinance",
      "fallback": ["alpha_vantage"],
      "reason": "YFinance has reliable split history",
      "data_points": [
        "date", "split_ratio", "before", "after"
      ]
    },
    "earnings": {
      "primary": "yfinance",
      "fallback": ["alpha_vantage"],
      "reason": "YFinance provides earnings calendar and historical data",
      "data_points": [
        "earnings_date", "eps_estimate", "eps_actual", "revenue", "surprise"
      ]
    },
    "news": {
      "primary": "finnhub",
      "fallback": ["alpha_vantage"],
      "reason": "Finnhub provides real-time financial news with sentiment",
      "data_points": [
        "headline", "summary", "source", "url", "published_date", "sentiment"
      ]
    },
    "analyst_ratings": {
      "primary": "finnhub",
      "fallback": [],
      "reason": "Only Finnhub provides analyst ratings and recommendations via API",
      "data_points": [
        "rating", "target_price", "analyst_firm", "date", "recommendation"
      ]
    },
    "price_targets": {
      "primary": "finnhub",
      "fallback": [],
      "reason": "Finnhub aggregates analyst price targets",
      "data_points": [
        "target_high", "target_low", "target_mean", "target_median", "number_of_analysts"
      ]
    },
    "etf_holdings": {
      "primary": "alpha_vantage",
      "fallback": [],
      "reason": "Only AlphaVantage provides ETF holdings via ETF_PROFILE endpoint",
      "data_points": [
        "holdings", "top_10_holdings", "sector_weights", "asset_allocation"
      ]
    }
  },
  "active_providers": ["yfinance", "alpha_vantage", "finnhub"],
  "provider_details": {
    "yfinance": {
      "tier": "free",
      "rate_limit": "unlimited",
      "cost": "$0",
      "priority": 1
    },
    "alpha_vantage": {
      "tier": "free",
      "rate_limit": "5 calls/min, 500 calls/day",
      "cost": "$0 (free tier)",
      "priority": 2
    },
    "finnhub": {
      "tier": "free",
      "rate_limit": "60 calls/min",
      "cost": "$0 (free tier)",
      "priority": 3
    }
  },
  "can_switch_providers": true,
  "last_updated": "2025-11-17T00:00:00Z"
}
```

**Use Cases:**
- Understand data source for each metric
- See fallback strategies if primary provider fails
- Know which providers require API keys
- Understand provider priority and rate limits

**Notes:**
- YFinance is used as primary for prices (free, unlimited calls)
- Alpha Vantage provides fundamentals and technical indicators (requires API key)
- Finnhub provides news and analyst data (requires API key)
- System automatically fails over to backup providers if primary fails

---

## System Management Endpoints

### Get Scheduler Information
Get comprehensive information about all scheduled background jobs.

**Endpoint:** `GET /system/scheduler/info`

**Description:**  
Returns the status of the job scheduler and details about all registered jobs including their schedules, next run times, and trigger configurations.

**Response:**
```json
{
  "scheduler_status": "running",
  "total_jobs": 3,
  "jobs": [
    {
      "id": "price_collector",
      "name": "Stock Price Collection",
      "next_run": "2025-11-17T09:00:00-05:00",
      "trigger": "cron[day_of_week='mon-fri', hour='9-16', minute='*', second='0']"
    },
    {
      "id": "market_close_poll",
      "name": "Market Close Price Poll",
      "next_run": "2025-11-17T17:00:00-05:00",
      "trigger": "cron[day_of_week='mon-fri', hour='17', minute='0', second='0']"
    },
    {
      "id": "metals_price_collector",
      "name": "Precious Metals Price Collection",
      "next_run": "2025-11-18T10:00:00+05:30",
      "trigger": "cron[hour='10', minute='0', second='0']"
    }
  ]
}
```

**Fields:**
- `scheduler_status`: Current status of the scheduler (`running` or `stopped`)
- `total_jobs`: Number of registered jobs
- `jobs`: Array of job details
  - `id`: Unique job identifier
  - `name`: Human-readable job name
  - `next_run`: ISO 8601 timestamp of next scheduled execution
  - `trigger`: Cron expression defining the schedule

**Use Cases:**
- Monitor which jobs are scheduled
- View upcoming job execution times
- Verify scheduler is running
- Debug scheduling issues

**Example:**
```bash
curl http://localhost:8000/system/scheduler/info
```

---

### Get Individual Job Information
Get detailed information for a specific scheduled job.

**Endpoint:** `GET /system/scheduler/jobs/{job_id}`

**Path Parameters:**
- `job_id` (string, required): Job identifier (e.g., `price_collector`, `market_close_poll`, `metals_price_collector`)

**Response:**
```json
{
  "id": "price_collector",
  "name": "Stock Price Collection",
  "next_run": "2025-11-17T09:00:00-05:00",
  "trigger": "cron[day_of_week='mon-fri', hour='9-16', minute='*', second='0']"
}
```

**Error Responses:**
- `404 Not Found`: Job with specified ID doesn't exist

**Example:**
```bash
curl http://localhost:8000/system/scheduler/jobs/price_collector
```

---

## Metadata Management Endpoints

### Trigger Incremental Batch Collection
Manually trigger incremental batch collection of stock metadata.

**Endpoint:** `POST /system/metadata/collection/batch`

**Description:**  
Processes 30 tickers per batch in priority order (by market cap, descending). Failed tickers are automatically moved to the next run. Runs automatically 24 times/day (every hour, 00:00-23:00 EST) for a total of 720 tickers/day.

**Response:**
```json
{
  "status": "success",
  "processed": 30,
  "success": 28,
  "failure": 2,
  "elapsed_seconds": 45.2
}
```

**Fields:**
- `status`: Operation status (`success` or `error`)
- `processed`: Total number of tickers attempted
- `success`: Number of successful collections
- `failure`: Number of failed collections
- `elapsed_seconds`: Time taken to process batch

**Use Cases:**
- Manually trigger collection outside scheduled hours
- Test batch collection functionality
- Recover from failed scheduled runs

**Example:**
```bash
curl -X POST http://localhost:8000/system/metadata/collection/batch
```

---

### Trigger Full Discovery
Manually trigger one-off metadata discovery for all tickers.

**Endpoint:** `POST /system/metadata/discovery/trigger`

**Query Parameters:**
- `limit` (integer, optional): Limit number of tickers to process
- `test_mode` (boolean, optional): If `true`, only process first 20 tickers for testing

**Description:**  
Discovers all available tickers from Alpha Vantage LISTING_STATUS API and collects base metadata from YFinance in bulk. Queues high-priority tickers (ETFs and large caps) for Alpha Vantage enrichment.

**Response:**
```json
{
  "status": "success",
  "discovered_tickers": 12443,
  "processed_tickers": 12443,
  "collection_stats": {
    "success": 769,
    "failure": 11674,
    "total": 12443
  },
  "priority_enrichment_queued": 236,
  "elapsed_seconds": 215.24,
  "asset_type_breakdown": {
    "Stock": 7813,
    "ETF": 4630
  }
}
```

**Fields:**
- `discovered_tickers`: Total tickers found from Alpha Vantage
- `processed_tickers`: Number of tickers attempted for collection
- `collection_stats`: Breakdown of success/failure counts
- `priority_enrichment_queued`: ETFs and large caps queued for enrichment
- `elapsed_seconds`: Total execution time
- `asset_type_breakdown`: Distribution by asset type

**Example:**
```bash
# Test mode (20 tickers)
curl -X POST "http://localhost:8000/system/metadata/discovery/trigger?test_mode=true"

# Full discovery
curl -X POST http://localhost:8000/system/metadata/discovery/trigger

# Limited to 1000 tickers
curl -X POST "http://localhost:8000/system/metadata/discovery/trigger?limit=1000"
```

---

### Enrich Single Ticker
Manually trigger Alpha Vantage enrichment for a specific ticker.

**Endpoint:** `POST /system/metadata/enrich/{ticker}`

**Path Parameters:**
- `ticker` (string, required): Stock ticker symbol (e.g., `AAPL`, `MSFT`, `VOO`)

**Description:**  
Enriches existing ticker metadata with premium data from Alpha Vantage including P/E ratio, PEG ratio, dividend yield, revenue, profit margins, and more.

**Response:**
```json
{
  "status": "success",
  "ticker": "AAPL",
  "enrichment_status": "enriched",
  "message": "Metadata enriched successfully"
}
```

**Error Responses:**
- `404 Not Found`: Ticker not found in database (must collect base metadata first)
- `500 Internal Server Error`: Enrichment failed

**Use Cases:**
- Immediate enrichment for high-priority tickers
- Manual enrichment outside scheduled cycle
- Refresh stale data for specific ticker

**Example:**
```bash
curl -X POST http://localhost:8000/system/metadata/enrich/AAPL
```

---

### Get Metadata Collection Statistics
Get comprehensive statistics about metadata collection progress.

**Endpoint:** `GET /system/metadata/stats`

**Description:**  
Returns detailed statistics about ticker collection, enrichment status, asset type distribution, priority queue, and job execution status.

**Response:**
```json
{
  "total_tickers": 797,
  "by_enrichment_status": {
    "base": 797,
    "enriched": 0,
    "failed": 0
  },
  "by_asset_type": {
    "Stock": 625,
    "ETF": 172,
    "Other": 0
  },
  "enrichment_queue": {
    "etfs_pending": 172,
    "large_caps_pending": 70,
    "total_pending": 797
  },
  "job_status": {
    "is_running": false,
    "last_discovery_run": "2025-11-22T21:42:06.766407",
    "last_enrichment_run": null,
    "discovery_count": 797,
    "enrichment_count": 0
  }
}
```

**Fields:**
- `total_tickers`: Total tickers in database
- `by_enrichment_status`: Breakdown by enrichment level
  - `base`: YFinance metadata only
  - `enriched`: Alpha Vantage enrichment applied
  - `failed`: Enrichment failed
- `by_asset_type`: Distribution by asset type (Stock, ETF, Other)
- `enrichment_queue`: High-priority tickers pending enrichment
  - `etfs_pending`: ETFs awaiting enrichment
  - `large_caps_pending`: Large cap stocks (>$10B) awaiting enrichment
  - `total_pending`: Total tickers needing enrichment
- `job_status`: Current job execution state
  - `is_running`: Whether collection job is currently running
  - `last_discovery_run`: Last full discovery timestamp
  - `last_enrichment_run`: Last enrichment cycle timestamp
  - `discovery_count`: Total tickers collected (base metadata)
  - `enrichment_count`: Total tickers enriched (Alpha Vantage)

**Use Cases:**
- Monitor collection progress
- Track enrichment queue size
- Verify job execution
- Assess data coverage

**Example:**
```bash
curl http://localhost:8000/system/metadata/stats
```

---

### Get Failed Tickers
Get list of tickers that have exhausted retry attempts.

**Endpoint:** `GET /system/metadata/failed`

**Query Parameters:**
- `limit` (integer, optional, default: 100): Maximum number of failed tickers to return
- `skip` (integer, optional, default: 0): Number of failed tickers to skip for pagination

**Description:**  
Returns list of tickers with `collection_attempts >= 3` that have exhausted retry attempts and will not be retried automatically. Shows whether metadata was eventually collected and any error messages.

**Response:**
```json
{
  "total_failed": 28,
  "returned": 5,
  "skip": 0,
  "limit": 5,
  "failed_tickers": [
    {
      "ticker": "ZM",
      "collection_attempts": 4,
      "last_collection_attempt": "2025-11-23T13:32:46.104000",
      "collection_error": null,
      "has_metadata": true,
      "market_cap": 23789318144.0,
      "enrichment_status": "base"
    }
  ]
}
```

**Fields:**
- `total_failed`: Total number of tickers that exhausted retries
- `returned`: Number of tickers in current response
- `skip`: Pagination offset used
- `limit`: Maximum results per page
- `failed_tickers`: Array of failed ticker objects
  - `ticker`: Stock ticker symbol
  - `collection_attempts`: Number of collection attempts (3+)
  - `last_collection_attempt`: Timestamp of last attempt
  - `collection_error`: Error message if collection failed (null if eventually succeeded)
  - `has_metadata`: Whether metadata was eventually collected
  - `market_cap`: Market capitalization
  - `enrichment_status`: Current enrichment level

**Use Cases:**
- Identify tickers that need manual investigation
- Find tickers that failed but eventually succeeded
- Monitor retry exhaustion rate
- Debug collection issues

**Example:**
```bash
# Get first 50 failed tickers
curl "http://localhost:8000/system/metadata/failed?limit=50"

# Get next page
curl "http://localhost:8000/system/metadata/failed?limit=50&skip=50"
```

---

## Metadata Collection Strategy

### Two-Stage Enrichment
1. **Stage 1 - Base Collection (YFinance)**
   - Fast bulk collection
   - Basic metadata: name, sector, market cap, exchange
   - No API key required
   - Scheduled: 24 times/day (every hour), 30 tickers/batch = 720/day

2. **Stage 2 - Premium Enrichment (Alpha Vantage)**
   - Selective enrichment for high-priority tickers
   - Premium data: P/E ratio, PEG ratio, dividend yield, financials
   - API key required (free tier: 25 calls/day)
   - Scheduled: Daily at 2:00 AM EST, 5 tickers/cycle

### Priority Queue
Enrichment prioritized by:
1. **ETFs** - Always enriched (Alpha Vantage superior for ETF data)
2. **Large Cap Stocks** - Market cap > $10B
3. **Mid Cap Stocks** - Market cap $2B-$10B
4. **Small Cap Stocks** - Market cap < $2B (on-demand only)

### Batch Collection Features
- **Market cap ordering**: Large caps processed first
- **Failure tracking**: Failed tickers automatically retried next day
- **Retry logic**: Tracks collection attempts and errors
- **Incremental progress**: ~16 days to complete full universe (12,443 tickers)

---

## Background Jobs

The system runs two scheduled jobs:

1. **Stock Price Collection**
   - **Schedule:** Every 60 seconds, 9 AM - 5 PM EST (Monday-Friday)
   - **Job ID:** `price_collector`
   - **Description:** Automatically polls current prices for all enabled tickers during market hours

2. **Market Close Price Poll**
   - **Schedule:** Once at 5:00 PM EST (Monday-Friday)
   - **Job ID:** `market_close_poll`
   - **Description:** Captures closing prices at market close

---

## Error Responses

All endpoints follow standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

---

## Data Models

### Stock Information
```typescript
{
  ticker: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  market_cap?: number;
  sector?: string;
  industry?: string;
}
```

### Price Record
```typescript
{
  ticker: string;
  current_price: number;
  previous_close?: number;
  open?: number;
  day_high?: number;
  day_low?: number;
  volume?: number;
  timestamp: string; // ISO 8601 format
}
```

### Ticker Configuration
```typescript
{
  ticker: string;
  enabled: boolean;
  added_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
}
```

---

## Notes

- All ticker symbols are case-insensitive (automatically converted to uppercase)
- Timestamps are in ISO 8601 format
- Market hours are based on NYSE calendar (US/Eastern timezone)
- Price collection only occurs during market hours (9 AM - 5 PM EST, Monday-Friday, excluding holidays)
- Historical price data from `/stocks/price/collected/{ticker}` returns data from the last 365 days

---

## Financier - Financial Analytics Endpoints

### Comprehensive Financial Analysis
Get deep financial analysis with insights including cash flow, trends, anomalies, and health metrics.

**Endpoint:** `GET /financier/analytics/comprehensive`

**Query Parameters:**
- `year` (optional) - Filter by year (e.g., 2025)
- `month` (optional) - Filter by month (1-12)
- `category` (optional) - Filter by category (e.g., "Groceries")

**Example:** `GET /financier/analytics/comprehensive?year=2025`

**Response:**
```json
{
  "filters": {"year": 2025, "month": null, "category": null},
  "transaction_count": 178,
  "cash_flow": {
    "total_income": 5000.00,
    "total_expenses": 3842.50,
    "net_cash_flow": 1157.50
  },
  "monthly_cash_flow": [
    {
      "month": "May 2025",
      "income": 1500.00,
      "expenses": 1280.50,
      "net_cash_flow": 219.50
    }
  ],
  "category_breakdown": [
    {
      "category": "Restaurants & Dining",
      "amount": 985.25,
      "percentage": 25.6,
      "transaction_count": 43,
      "average_transaction": 22.91
    }
  ],
  "outliers": {
    "count": 3,
    "transactions": [
      {
        "transaction_date": "07/15",
        "merchant": "APPLE.COM/BILL",
        "amount": 999.00,
        "category": "Electronics",
        "z_score": 4.25,
        "deviation_from_average": 950.00
      }
    ]
  },
  "spending_spikes": [
    {
      "month": "Jul 2025",
      "spending": 1850.00,
      "average": 1200.00,
      "spike_ratio": 1.54,
      "excess_spending": 650.00
    }
  ],
  "trend_analysis": {
    "trend_direction": "increasing",
    "average_monthly_change": 45.30,
    "correlation_coefficient": 0.842,
    "statistical_significance": "significant",
    "next_month_prediction": 1345.80,
    "confidence": 0.709
  },
  "recurring_payments": [
    {
      "merchant": "NETFLIX.COM",
      "average_amount": 15.99,
      "amount_variation": 0.00,
      "occurrences": 5,
      "frequency": "monthly",
      "is_stable": true
    }
  ],
  "financial_health": {
    "savings_rate": 23.2,
    "expense_to_income_ratio": 76.8,
    "fixed_spending": 850.00,
    "discretionary_spending": 2992.50,
    "fixed_percentage": 22.1,
    "discretionary_percentage": 77.9,
    "category_concentration": 0.342,
    "diversification_score": 65.8
  }
}
```

**Features:**
- **Cash Flow Analysis**: Income, expenses, and net cash flow over time
- **Spending Breakdown**: Category-wise spending with percentages
- **Outlier Detection**: Unusual transactions using Z-score method (threshold: 3.0)
- **Spending Spikes**: Months with spending 1.5x above rolling average
- **Trend Analysis**: Linear regression showing spending direction and predictions
- **Recurring Payments**: Auto-detected subscription services and fixed expenses
- **Financial Health**: Savings rate, expense ratios, spending diversification

---

### Financial Visualizations
Generate visualization charts as base64-encoded images for frontend display.

**IMPORTANT**: This endpoint generates images for **frontend consumption only**. Images are returned as base64-encoded strings in JSON format, intended for display in React components. Do NOT use this endpoint for file downloads, PDF exports, or email attachments.

**Endpoint:** `GET /financier/analytics/visualizations`

**Query Parameters:**
- `year` (optional) - Filter by year
- `month` (optional) - Filter by month (1-12)
- `format` (optional) - Output format: `png` or `svg` (default: `png`)

**Example:** `GET /financier/analytics/visualizations?year=2025&format=png`

**Response:**
```json
{
  "income_vs_expenses": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "category_pie_chart": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "spending_trend": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "outlier_detection": "iVBORw0KGgoAAAANSUhEUgAAA..."
}
```

**Visualizations Generated:**
1. **income_vs_expenses**: Monthly income vs expenses bar chart
2. **category_pie_chart**: Spending distribution by category (pie chart)
3. **spending_trend**: Time series line chart with trend line
4. **outlier_detection**: Scatter plot highlighting unusual transactions

**Frontend Usage (React):**
```html
<img src="data:image/png;base64,{income_vs_expenses}" alt="Income vs Expenses" />
```

**Note**: Images are generated server-side and returned as base64 strings. They are NOT saved to disk or database. The frontend is responsible for displaying these images.

**Errors:**
- `400 Bad Request` - Invalid format (must be 'png' or 'svg')
- `500 Internal Server Error` - Error generating visualizations

---

### Analytics Data Models

#### Cash Flow Summary
```typescript
{
  total_income: number;      // Sum of all credits (payments received)
  total_expenses: number;    // Sum of all charges
  net_cash_flow: number;     // Income - Expenses
}
```

#### Monthly Cash Flow
```typescript
{
  month: string;             // "Jan 2025"
  income: number;
  expenses: number;
  net_cash_flow: number;
}
```

#### Category Breakdown
```typescript
{
  category: string;          // "Groceries"
  amount: number;
  percentage: number;        // % of total spending
  transaction_count: number;
  average_transaction: number;
}
```

#### Outlier Transaction
```typescript
{
  transaction_date: string;  // "MM/DD"
  merchant: string;
  amount: number;
  category: string;
  z_score: number;           // Statistical z-score (>3.0 = outlier)
  deviation_from_average: number;
}
```

#### Spending Spike
```typescript
{
  month: string;
  spending: number;
  average: number;           // 3-month rolling average
  spike_ratio: number;       // Current / Average
  excess_spending: number;   // Amount above average
}
```

#### Trend Analysis
```typescript
{
  trend_direction: "increasing" | "decreasing" | "stable";
  average_monthly_change: number;
  correlation_coefficient: number;  // -1 to 1
  statistical_significance: "significant" | "not_significant";
  next_month_prediction: number;
  confidence: number;               // R-squared (0-1)
}
```

#### Recurring Payment
```typescript
{
  merchant: string;
  average_amount: number;
  amount_variation: number;  // Standard deviation
  occurrences: number;
  frequency: "monthly" | "recurring";
  is_stable: boolean;        // Variation < $1.00
}
```

#### Financial Health Indicators
```typescript
{
  savings_rate: number | null;           // % of income saved (if income data available)
  expense_to_income_ratio: number | null; // % of income spent
  fixed_spending: number;                 // Essential expenses
  discretionary_spending: number;         // Non-essential expenses
  fixed_percentage: number;               // % of total spending
  discretionary_percentage: number;       // % of total spending
  category_concentration: number;         // Gini coefficient (0=diverse, 1=concentrated)
  diversification_score: number;          // 0-100 (higher = more diversified spending)
}
```

---

## Analytics Notes

- **Outlier Detection**: Uses Z-score method with threshold 3.0 (99.7% confidence interval)
- **Spending Spikes**: Detected when monthly spending exceeds 1.5x the 3-month rolling average
- **Trend Analysis**: Uses linear regression with statistical significance testing (p < 0.05)
- **Recurring Payments**: Requires minimum 3 occurrences to detect pattern
- **Financial Health**: Savings rate calculated only when income data is available
- **Fixed Categories**: Utilities, Insurance, Healthcare, Gas & Fuel, Transportation, Bills, Medical
- **Visualizations**: Generated server-side, returned as base64-encoded PNG or SVG images
- **Performance**: Analytics process up to 100,000 transactions per query
