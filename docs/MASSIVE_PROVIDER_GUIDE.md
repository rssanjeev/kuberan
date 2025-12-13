# MASSIVE API Provider Guide

**Last Updated:** December 13, 2025  
**API Provider:** Polygon.io (branded as MASSIVE)  
**Base URL:** `https://api.polygon.io`  
**Documentation:** https://polygon.io/docs  
**Reference Guide:** See `docs/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md` for complete endpoint documentation  
**Primary Use:** Real-time quotes, identifiers, regulatory data, news with sentiment  
**Free Tier Rate Limits:** 5 calls/min, 300 calls/hour, 7,200 calls/day

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Free Tier Reference Endpoints](#free-tier-reference-endpoints)
4. [Rate Limits](#rate-limits)
5. [Data Identifiers](#data-identifiers)
6. [Response Formats](#response-formats)
7. [Caching Strategy](#caching-strategy)
8. [Best Practices](#best-practices)
9. [Code Examples](#code-examples)

---

> **📖 Complete Endpoint Documentation**: See [`MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md`](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md) for detailed documentation of all 11 free tier reference endpoints with query parameters, response schemas, and usage examples.

---

## Overview

### What is MASSIVE?

**MASSIVE and Polygon.io are the same service.** Polygon.io is the actual API provider, while "MASSIVE" is their branding/marketing name. Throughout Kuberan's codebase, we refer to it as "MASSIVE" for consistency, but:

- **Actual API base URL:** `https://api.polygon.io`
- **API infrastructure:** Polygon.io's exchange-level data platform
- **Documentation:** https://polygon.io/docs
- **Why the confusion?** Polygon.io uses "MASSIVE" in their marketing, but their API URLs still use `polygon.io`

For Kuberan, this means:
- Code uses `api.polygon.io` for actual HTTP requests
- Documentation refers to "MASSIVE" or "MASSIVE (Polygon.io)"
- Both names reference the same service

### Capabilities

Polygon.io provides exchange-level financial data with regulatory identifiers (CIK, FIGI, CUSIP) and real-time market data.

### Strengths

✅ **Exchange-Level Data:** Direct from exchanges (Tier 1 reliability)  
✅ **Regulatory IDs:** CIK, FIGI, CUSIP, ISIN, LEI (canonical sources)  
✅ **Real-Time Quotes:** Minimal latency (<100ms for Developer tier)  
✅ **Comprehensive Metadata:** 85+ fields per ticker  
✅ **News with Sentiment:** Publisher-attributed articles with sentiment scores  
✅ **Corporate Actions:** Splits, dividends, earnings dates  
✅ **Historical Aggregates:** OHLCV bars at multiple intervals  
✅ **Ticker Types:** Distinguishes CS (common stock), ADRC (ADR), ETF, etc.  

### Limitations

❌ **Requires API Key:** Must register at polygon.io and authenticate  
❌ **Rate Limits (Free Tier):** 5 calls/min, 300 calls/hour, 7,200 calls/day  
❌ **Limited Free Tier:** Only reference endpoints (no real-time prices on free tier)  
❌ **Cost:** Paid plans start at $29/month for real-time data  
❌ **Financial Statements:** Deprecated endpoint (use Alpha Vantage as fallback)  
❌ **No Adjusted Prices:** Use YFinance for split/dividend-adjusted close  

### When to Use MASSIVE

**Primary Use Cases:**
- Real-time stock quotes (current price, bid/ask, volume)
- Regulatory identifiers (CIK, FIGI, CUSIP, ISIN)
- Ticker type classification (CS, ADRC, ETF, etc.)
- Primary exchange identification (XNYS, XNAS, etc.)
- Company metadata (employees, SIC code, phone, address)
- News articles with sentiment analysis
- Corporate actions (splits, dividends, earnings)
- Branding assets (logos, icons)

**Not Recommended For:**
- Adjusted close prices (use YFinance)
- Financial statements on free tier (use YFinance or Alpha Vantage)
- Intraday bars on free tier (limited to 5 calls/min)
- High-volume backtesting (use cached data)

---

## Authentication

### API Key Setup

1. **Register:** https://polygon.io/dashboard/signup
2. **Get API Key:** Dashboard → API Keys → Copy key
3. **Set Environment Variable:**

```bash
# Add to .env or docker-compose.yml
POLYGON_API_KEY=your_api_key_here
```

### Authentication Methods

**Method 1: Query Parameter (Recommended)**

```python
import httpx

api_key = os.getenv("POLYGON_API_KEY")
url = f"https://api.polygon.io/v3/reference/tickers?apiKey={api_key}"
response = httpx.get(url)
```

**Method 2: Authorization Header**

```python
headers = {"Authorization": f"Bearer {api_key}"}
response = httpx.get(
    "https://api.polygon.io/v3/reference/tickers",
    headers=headers
)
```

### Verify Authentication

```python
# Test API key
response = httpx.get(
    f"https://api.polygon.io/v3/reference/tickers/AAPL?apiKey={api_key}"
)

if response.status_code == 200:
    print("✓ API key valid")
elif response.status_code == 401:
    print("✗ Invalid API key")
elif response.status_code == 403:
    print("✗ API key lacks permissions")
```

---

## Free Tier Reference Endpoints

> **Note**: This section provides a quick reference for the 11 free tier endpoints available to Kuberan. For **complete documentation** with all query parameters, response schemas, pagination details, and usage examples, see [`MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md`](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md).

### Available Endpoints (Free Tier)

| Endpoint | Purpose | Documentation |
|----------|---------|---------------|
| `GET /v3/reference/tickers` | All tickers list with filtering | [Guide §1](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#1-all-tickers) |
| `GET /v3/reference/tickers/{ticker}` | **Ticker overview** (most important) | [Guide §2](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#2-ticker-overview) |
| `GET /v3/reference/tickers/types` | Ticker type classifications | [Guide §3](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#3-ticker-types) |
| `GET /v3/reference/exchanges` | Exchange directory with MIC codes | [Guide §4](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#4-exchanges) |
| `GET /v3/reference/conditions` | Trade/quote condition codes | [Guide §5](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#5-condition-codes) |
| `GET /v3/reference/splits` | Stock split history | [Guide §6](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#6-stock-splits) |
| `GET /v3/reference/dividends` | Dividend history | [Guide §7](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#7-dividends) |
| `GET /vX/reference/financials` | **Financials (deprecated)** | [Guide §8](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#8-financials-deprecated) |
| `GET /v2/reference/news` | Financial news with sentiment | [Guide §9](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#9-news) |
| `GET /v3/reference/options/contracts` | All option contracts | [Guide §10](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#10-all-option-contracts) |
| `GET /v3/reference/options/contracts/{ticker}` | Specific option contract | [Guide §11](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md#11-option-contract-overview) |

### Paid Tier Endpoints (Not Available)

The following require a paid subscription ($29+/month):
- ❌ Real-time quotes (`/v2/snapshot/locale/us/markets/stocks/tickers`)
- ❌ Historical aggregates (`/v2/aggs/ticker/{ticker}/range`)
- ❌ Intraday trades (`/v3/trades/{ticker}`)
- ❌ Technical indicators (SMA, EMA, RSI, MACD)
- ❌ WebSocket streaming
- ❌ Market status

### 1. Reference API (Metadata)

Ticker metadata, identifiers, and classification.

#### All Tickers

**Endpoint:** `GET /v3/reference/tickers`

**Purpose:** List all available tickers with filtering

**Parameters:**
- `ticker` (string): Filter by ticker symbol
- `type` (string): Filter by type (CS, ADRC, ETF, etc.)
- `market` (string): Filter by market (stocks, otc, crypto, fx)
- `exchange` (string): Filter by exchange (XNAS, XNYS, etc.)
- `active` (bool): Active tickers only (default true)
- `order` (string): Sort order (asc/desc)
- `limit` (int): Results per page (max 1000)
- `sort` (string): Sort field (ticker, name, market, etc.)

**Response:**
```json
{
  "status": "OK",
  "count": 12140,
  "results": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "market": "stocks",
      "locale": "us",
      "primary_exchange": "XNAS",
      "type": "CS",
      "active": true,
      "currency_name": "usd",
      "cik": "0000320193",
      "composite_figi": "BBG000B9XRY4",
      "share_class_figi": "BBG001S5N8V8"
    }
  ],
  "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=..."
}
```

#### Ticker Overview (Most Important)

**Endpoint:** `GET /v3/reference/tickers/{ticker}`

**Purpose:** Complete ticker metadata (85+ fields)

**Response:**
```json
{
  "status": "OK",
  "results": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "market": "stocks",
    "locale": "us",
    "primary_exchange": "XNAS",
    "type": "CS",
    "active": true,
    "currency_name": "usd",
    "cik": "0000320193",
    "composite_figi": "BBG000B9XRY4",
    "share_class_figi": "BBG001S5N8V8",
    "phone_number": "1-408-996-1010",
    "address": {
      "address1": "One Apple Park Way",
      "city": "Cupertino",
      "state": "CA",
      "postal_code": "95014"
    },
    "description": "Apple Inc. designs, manufactures...",
    "sic_code": "3571",
    "sic_description": "Electronic Computers",
    "ticker_root": "AAPL",
    "homepage_url": "https://www.apple.com",
    "total_employees": 164000,
    "list_date": "1980-12-12",
    "branding": {
      "logo_url": "https://api.polygon.io/v1/reference/company-branding/...",
      "icon_url": "https://api.polygon.io/v1/reference/company-branding/..."
    },
    "share_class_shares_outstanding": 15204100000,
    "weighted_shares_outstanding": 15204100000,
    "market_cap": 2770000000000
  }
}
```

**Cache TTL:** 30 days (metadata rarely changes)

#### Ticker Types

**Endpoint:** `GET /v3/reference/tickers/types`

**Purpose:** Get all available ticker types

**Response:**
```json
{
  "status": "OK",
  "results": [
    {"code": "CS", "description": "Common Stock"},
    {"code": "ADRC", "description": "American Depositary Receipt Common"},
    {"code": "ETF", "description": "Exchange Traded Fund"},
    {"code": "REIT", "description": "Real Estate Investment Trust"},
    {"code": "RIGHT", "description": "Right"},
    {"code": "WARRANT", "description": "Warrant"},
    {"code": "UNIT", "description": "Unit"}
  ]
}
```

#### Exchanges

**Endpoint:** `GET /v3/reference/exchanges`

**Purpose:** List all exchanges with MIC codes

**Response:**
```json
{
  "status": "OK",
  "results": [
    {
      "id": 1,
      "type": "exchange",
      "market": "stocks",
      "mic": "XNYS",
      "name": "New York Stock Exchange",
      "tape": "A"
    },
    {
      "id": 2,
      "type": "exchange",
      "market": "stocks",
      "mic": "XNAS",
      "name": "NASDAQ",
      "tape": "Q"
    }
  ]
}
```

### 2. Market Data API

Real-time quotes, historical OHLCV, and intraday data.

#### Previous Close

**Endpoint:** `GET /v2/aggs/ticker/{ticker}/prev`

**Purpose:** Previous day's OHLCV

**Response:**
```json
{
  "ticker": "AAPL",
  "status": "OK",
  "results": [{
    "T": "AAPL",
    "v": 52164000,
    "vw": 194.1234,
    "o": 195.00,
    "c": 194.50,
    "h": 196.00,
    "l": 193.50,
    "t": 1702346400000,
    "n": 500000
  }]
}
```

**Fields:**
- `T` - Ticker symbol
- `v` - Volume
- `vw` - Volume-weighted average price
- `o` - Open
- `c` - Close
- `h` - High
- `l` - Low
- `t` - Timestamp (Unix milliseconds)
- `n` - Number of transactions

#### Aggregates (Historical Bars)

**Endpoint:** `GET /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}`

**Purpose:** OHLCV bars for custom date ranges

**Parameters:**
- `multiplier` (int): Size of timespan (e.g., 1, 5, 15)
- `timespan` (string): minute, hour, day, week, month, quarter, year
- `from` (string): Start date (YYYY-MM-DD)
- `to` (string): End date (YYYY-MM-DD)
- `adjusted` (bool): Adjust for splits (default true)
- `sort` (string): asc or desc
- `limit` (int): Max results (default 5000)

**Example:**
```
GET /v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-12-31
```

**Response:** Same format as Previous Close, but with multiple results

#### Splits

**Endpoint:** `GET /v3/reference/splits`

**Purpose:** Stock split history

**Parameters:**
- `ticker` (string): Filter by ticker
- `execution_date.gte` (string): Splits on or after date
- `execution_date.lte` (string): Splits on or before date

**Response:**
```json
{
  "status": "OK",
  "results": [{
    "ticker": "AAPL",
    "execution_date": "2020-08-31",
    "split_from": 1,
    "split_to": 4
  }]
}
```

#### Dividends

**Endpoint:** `GET /v3/reference/dividends`

**Purpose:** Dividend history

**Parameters:**
- `ticker` (string): Filter by ticker
- `ex_dividend_date.gte` (string): Ex-div on or after date
- `ex_dividend_date.lte` (string): Ex-div on or before date

**Response:**
```json
{
  "status": "OK",
  "results": [{
    "ticker": "AAPL",
    "ex_dividend_date": "2024-11-08",
    "payment_date": "2024-11-14",
    "record_date": "2024-11-11",
    "declaration_date": "2024-10-31",
    "cash_amount": 0.25,
    "currency": "USD",
    "dividend_type": "CD",
    "frequency": 4
  }]
}
```

### 3. News API

Financial news with publisher attribution and sentiment.

#### Ticker News

**Endpoint:** `GET /v2/reference/news`

**Purpose:** News articles with sentiment scores

**Parameters:**
- `ticker` (string): Filter by ticker
- `published_utc.gte` (string): Articles on or after date
- `published_utc.lte` (string): Articles on or before date
- `order` (string): asc or desc (by published date)
- `limit` (int): Max results (default 10, max 1000)

**Response:**
```json
{
  "status": "OK",
  "count": 500,
  "results": [{
    "id": "abc123",
    "publisher": {
      "name": "Bloomberg",
      "homepage_url": "https://www.bloomberg.com",
      "logo_url": "https://logo-url.com/bloomberg.png",
      "favicon_url": "https://favicon-url.com/bloomberg.ico"
    },
    "title": "Apple Announces New iPhone",
    "author": "John Doe",
    "published_utc": "2024-12-13T10:30:00Z",
    "article_url": "https://bloomberg.com/article-url",
    "tickers": ["AAPL", "AAPL.US"],
    "image_url": "https://image-url.com/iphone.jpg",
    "description": "Apple unveiled its latest iPhone...",
    "keywords": ["Apple", "iPhone", "Technology"],
    "insights": [{
      "ticker": "AAPL",
      "sentiment": "positive",
      "sentiment_reasoning": "Article discusses new product launch..."
    }]
  }],
  "next_url": "https://api.polygon.io/v2/reference/news?cursor=..."
}
```

**Sentiment Values:**
- `positive` - Bullish news
- `neutral` - Neutral news
- `negative` - Bearish news

**Cache TTL:** 1 hour (news updates frequently)

---

## Rate Limits

### Tier Comparison

| Tier | Calls/Minute | Calls/Hour | Calls/Day | Cost |
|------|--------------|------------|-----------|------|
| **Free** | 5 | 300 | 7,200 | $0 |
| **Starter** | 100 | 6,000 | 144,000 | $29/mo |
| **Developer** | 1,000 | 60,000 | 1,440,000 | $99/mo |
| **Advanced** | 10,000 | 600,000 | 14,400,000 | $399/mo |

### Current Tier

**Kuberan:** Developer tier (1,000 calls/min, 60,000/hour)

### Rate Limit Handling

**Status Code:** 429 (Too Many Requests)

**Response:**
```json
{
  "status": "ERROR",
  "message": "Rate limit exceeded",
  "request_id": "abc123"
}
```

**Retry-After Header:**
```
Retry-After: 60
```

**Implementation:**
```python
import httpx
import time

async def fetch_with_backoff(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        response = await httpx.get(url)
        
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        response.raise_for_status()
    
    raise Exception("Max retries exceeded")
```

---

## Data Identifiers

### Regulatory IDs

MASSIVE provides canonical sources for regulatory identifiers.

#### CIK (Central Index Key)

**Purpose:** SEC filing identifier  
**Format:** 10 digits with leading zeros (e.g., "0000320193")  
**Use:** Link to SEC EDGAR filings  
**Example:** https://www.sec.gov/cgi-bin/browse-edgar?CIK=0000320193

#### FIGI (Financial Instrument Global Identifier)

**Purpose:** Bloomberg-managed unique identifier  
**Format:** 12 alphanumeric characters (e.g., "BBG000B9XRY4")  
**Types:**
- **Composite FIGI:** Represents all share classes
- **Share Class FIGI:** Specific share class

**Example:**
- AAPL Composite: `BBG000B9XRY4`
- AAPL Share Class: `BBG001S5N8V8`

#### CUSIP (Committee on Uniform Securities Identification Procedures)

**Purpose:** North American security identifier  
**Format:** 9 characters (6 issuer + 2 issue + 1 check digit)  
**Example:** `037833100` (AAPL)

#### ISIN (International Securities Identification Number)

**Purpose:** Global security identifier  
**Format:** 12 characters (2 country + 9 NSIN + 1 check digit)  
**Example:** `US0378331005` (AAPL)

#### LEI (Legal Entity Identifier)

**Purpose:** Legal entity identification (regulatory)  
**Format:** 20 alphanumeric characters  
**Example:** `HWUPKR0MPOU8FGXBT394` (Apple Inc.)

### Why MASSIVE for Identifiers?

**Canonical Source:**
- MASSIVE gets IDs directly from regulatory bodies
- Most accurate and up-to-date
- Used for official filings and reports

**Cross-Reference:**
- Link tickers across different data providers
- Match securities across markets
- Validate ticker symbol accuracy

---

## Response Formats

### Pagination

MASSIVE uses **cursor-based pagination**.

**Pattern:**
```json
{
  "status": "OK",
  "results": [...],
  "count": 1000,
  "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=YXNkZg"
}
```

**Implementation:**
```python
async def fetch_all_pages(base_url: str):
    results = []
    next_url = base_url
    
    while next_url:
        response = await httpx.get(next_url)
        data = response.json()
        
        results.extend(data.get('results', []))
        next_url = data.get('next_url')
    
    return results
```

### Timestamp Formats

**Unix Milliseconds:**
```json
{
  "t": 1702346400000
}
```

**Convert to Python datetime:**
```python
from datetime import datetime

timestamp_ms = 1702346400000
dt = datetime.fromtimestamp(timestamp_ms / 1000)
# 2023-12-12 00:00:00
```

**ISO 8601:**
```json
{
  "published_utc": "2024-12-13T10:30:00Z"
}
```

**Parse ISO:**
```python
from datetime import datetime

dt = datetime.fromisoformat("2024-12-13T10:30:00Z".replace('Z', '+00:00'))
```

### Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| **OK** | Success | Use data |
| **DELAYED** | Data delayed | Check timestamp |
| **ERROR** | Request failed | Check error message |
| **NOT_FOUND** | Resource not found | Try different params |

**Response:**
```json
{
  "status": "OK",
  "results": {...}
}
```

---

## Caching Strategy

### By Data Type

```python
CACHE_TTL = {
    # Reference data (rarely changes)
    "ticker_metadata": 2592000,   # 30 days
    "exchanges": 2592000,          # 30 days
    "ticker_types": 2592000,       # 30 days
    
    # Market data (updates frequently)
    "real_time_quote": 900,        # 15 minutes
    "previous_close": 86400,       # 1 day
    "aggregates": 86400,           # 1 day
    
    # Corporate actions (immutable once occurred)
    "splits": None,                # Never expire
    "dividends": None,             # Never expire
    
    # News (updates frequently)
    "news": 3600                   # 1 hour
}
```

### Aggressive Caching for Reference Data

**Pattern:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class MassiveCache:
    def __init__(self):
        self.metadata_cache = {}
        self.metadata_ttl = timedelta(days=30)
    
    async def get_ticker_metadata(self, ticker: str):
        # Check cache
        if ticker in self.metadata_cache:
            data, timestamp = self.metadata_cache[ticker]
            if datetime.now() - timestamp < self.metadata_ttl:
                return data
        
        # Fetch from MASSIVE
        data = await self._fetch_from_massive(ticker)
        self.metadata_cache[ticker] = (data, datetime.now())
        return data
```

---

## Best Practices

### 1. Use next_url for Pagination

**Always follow next_url:**
```python
async def fetch_all_tickers():
    url = "https://api.polygon.io/v3/reference/tickers?limit=1000"
    all_results = []
    
    while url:
        response = await httpx.get(url)
        data = response.json()
        
        all_results.extend(data['results'])
        url = data.get('next_url')  # None if last page
    
    return all_results
```

### 2. Cache Reference Data Aggressively

**Metadata rarely changes:**
- Ticker overviews: 30 days
- Exchange list: 30 days
- Ticker types: 30 days
- CIK/FIGI mappings: Never expire (immutable)

### 3. Respect Rate Limits

**Implement backoff:**
```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls = deque()
        self.max_calls = calls_per_minute
        self.window = timedelta(minutes=1)
    
    async def acquire(self):
        now = datetime.now()
        
        # Remove calls outside window
        while self.calls and now - self.calls[0] > self.window:
            self.calls.popleft()
        
        # Wait if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = (self.calls[0] + self.window - now).total_seconds()
            await asyncio.sleep(sleep_time)
            return await self.acquire()
        
        self.calls.append(now)
```

### 4. Validate CIK/FIGI Mappings

**Always trust MASSIVE:**
```python
# ✅ Good: Use MASSIVE IDs as source of truth
massive_cik = await massive_provider.get_cik("AAPL")
# Store: 0000320193

# ❌ Bad: Override MASSIVE with other providers
# If YFinance says different CIK, MASSIVE wins
```

### 5. Store Identifiers Permanently

**Never expire:**
- CIK, FIGI, CUSIP, ISIN, LEI
- These are immutable regulatory IDs
- Cache indefinitely once retrieved

---

## Code Examples

### Example 1: Ticker Overview Retrieval

```python
import httpx
import os

async def get_ticker_metadata(ticker: str):
    api_key = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"apiKey": api_key})
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"API error: {data.get('error')}")
        
        results = data['results']
        
        return {
            "ticker": results['ticker'],
            "name": results['name'],
            "cik": results.get('cik'),
            "composite_figi": results.get('composite_figi'),
            "share_class_figi": results.get('share_class_figi'),
            "cusip": results.get('cusip'),
            "sic_code": results.get('sic_code'),
            "sic_description": results.get('sic_description'),
            "total_employees": results.get('total_employees'),
            "market_cap": results.get('market_cap'),
            "homepage_url": results.get('homepage_url'),
            "description": results.get('description'),
            "phone_number": results.get('phone_number'),
            "address": results.get('address'),
            "branding": results.get('branding')
        }

# Usage
metadata = await get_ticker_metadata("AAPL")
print(f"CIK: {metadata['cik']}")
print(f"FIGI: {metadata['composite_figi']}")
```

### Example 2: Historical Aggregates Query

```python
async def get_daily_bars(ticker: str, start_date: str, end_date: str):
    api_key = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={
            "apiKey": api_key,
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000
        })
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"API error: {data}")
        
        bars = []
        for result in data['results']:
            bars.append({
                "date": datetime.fromtimestamp(result['t'] / 1000).date(),
                "open": result['o'],
                "high": result['h'],
                "low": result['l'],
                "close": result['c'],
                "volume": result['v'],
                "vwap": result['vw'],
                "transactions": result['n']
            })
        
        return bars

# Usage
bars = await get_daily_bars("AAPL", "2024-01-01", "2024-12-31")
print(f"Fetched {len(bars)} daily bars")
```

### Example 3: News with Sentiment Extraction

```python
async def get_ticker_news(ticker: str, limit: int = 10):
    api_key = os.getenv("POLYGON_API_KEY")
    url = "https://api.polygon.io/v2/reference/news"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={
            "apiKey": api_key,
            "ticker": ticker,
            "order": "desc",
            "limit": limit
        })
        response.raise_for_status()
        
        data = response.json()
        
        articles = []
        for result in data['results']:
            # Extract sentiment for this ticker
            sentiment = None
            sentiment_reasoning = None
            
            for insight in result.get('insights', []):
                if insight['ticker'] == ticker:
                    sentiment = insight.get('sentiment')
                    sentiment_reasoning = insight.get('sentiment_reasoning')
                    break
            
            articles.append({
                "title": result['title'],
                "publisher": result['publisher']['name'],
                "published_date": result['published_utc'],
                "article_url": result['article_url'],
                "image_url": result.get('image_url'),
                "description": result.get('description'),
                "sentiment": sentiment,
                "sentiment_reasoning": sentiment_reasoning
            })
        
        return articles

# Usage
news = await get_ticker_news("AAPL", limit=5)
for article in news:
    print(f"{article['title']} - Sentiment: {article['sentiment']}")
```

### Example 4: Pagination Handling

```python
async def fetch_all_active_tickers():
    api_key = os.getenv("POLYGON_API_KEY")
    base_url = "https://api.polygon.io/v3/reference/tickers"
    
    all_tickers = []
    next_url = f"{base_url}?active=true&limit=1000&apiKey={api_key}"
    
    async with httpx.AsyncClient() as client:
        while next_url:
            response = await client.get(next_url)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                break
            
            all_tickers.extend(data['results'])
            next_url = data.get('next_url')
            
            # Add API key to next_url if missing
            if next_url and 'apiKey' not in next_url:
                separator = '&' if '?' in next_url else '?'
                next_url = f"{next_url}{separator}apiKey={api_key}"
            
            print(f"Fetched {len(all_tickers)} tickers so far...")
    
    return all_tickers

# Usage
tickers = await fetch_all_active_tickers()
print(f"Total active tickers: {len(tickers)}")
```

### Example 5: Error Handling with Retries

```python
import asyncio
from httpx import HTTPStatusError, TimeoutException

async def fetch_with_retry(url: str, max_retries: int = 3):
    """Fetch from MASSIVE with exponential backoff."""
    backoff = 1
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limited, waiting {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status_code == 404:
                    print(f"Resource not found: {url}")
                    return None
                
                response.raise_for_status()
                
        except TimeoutException:
            print(f"Timeout on attempt {attempt + 1}, retrying...")
            await asyncio.sleep(backoff)
            backoff *= 2
            
        except HTTPStatusError as e:
            if attempt < max_retries - 1:
                print(f"HTTP error {e.response.status_code}, retrying...")
                await asyncio.sleep(backoff)
                backoff *= 2
            else:
                raise
    
    raise Exception(f"Max retries exceeded for {url}")

# Usage
api_key = os.getenv("POLYGON_API_KEY")
url = f"https://api.polygon.io/v3/reference/tickers/AAPL?apiKey={api_key}"
data = await fetch_with_retry(url)
```

---

## Summary

**MASSIVE (Polygon.io) Overview:**
- **API Base URL**: `https://api.polygon.io`
- **Free Tier Access**: 11 reference endpoints (metadata, splits, dividends, news)
- **Rate Limits**: 5 calls/min, 300 calls/hour, 7,200 calls/day
- **Primary Use**: Ticker metadata enrichment with regulatory identifiers (CIK, FIGI)
- **Paid Tier Required**: Real-time quotes, historical prices, technical indicators

**MASSIVE Strengths:**
- ✅ Exchange-level data (Tier 1 reliability)
- ✅ Regulatory identifiers (CIK, FIGI, CUSIP, LEI) - canonical sources
- ✅ Comprehensive metadata (85+ fields per ticker)
- ✅ Corporate actions (splits, dividends with detailed dates)
- ✅ Financial news with sentiment analysis
- ✅ Ticker type classification (CS, ETF, ADRC, etc.)

**When to Use MASSIVE:**
- **Primary**: Ticker metadata enrichment (replaces AlphaVantage for discovery)
- **Secondary**: Dividends, splits, news with sentiment
- **Reference**: Exchanges, ticker types (cache permanently)

**When NOT to Use MASSIVE:**
- ❌ Real-time/historical prices (use YFinance on free tier)
- ❌ Adjusted close prices (use YFinance)
- ❌ Financial statements (deprecated endpoint, use AlphaVantage fallback)
- ❌ High-volume requests (limited to 5 calls/min on free tier)

**Complete Documentation:**  
See [`MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md`](./MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md) for detailed endpoint documentation with all query parameters, response schemas, and integration examples.

---

**Last Updated:** December 13, 2025
- ✅ Regulatory identifiers (CIK, FIGI, CUSIP, ISIN, LEI)
- ✅ Real-time quotes with minimal latency
- ✅ News with sentiment analysis
- ✅ Corporate actions (splits, dividends)

**MASSIVE Weaknesses:**
- ❌ Requires API key and authentication
- ❌ Rate limits (1000/min on Developer tier)
- ❌ No adjusted prices (use YFinance)
- ❌ Financial statements require Premium tier

**Primary Use in Kuberan:**
- Real-time stock quotes (price, bid/ask, volume)
- Regulatory identifiers (CIK, FIGI, CUSIP, ISIN)
- Ticker type classification (CS, ADRC, ETF)
- Primary exchange identification (XNYS, XNAS)
- Company metadata (employees, SIC, contact info)
- News articles with sentiment
- Corporate actions tracking

**Not Recommended For:**
- Adjusted close prices (use YFinance)
- Financial statements on current tier (use YFinance)
- High-volume backtesting without caching

---

**Next Steps:**
- See [YFINANCE_API_GUIDE.md](YFINANCE_API_GUIDE.md) for adjusted prices and ratios
- See [DATA_PRIORITY_MATRIX.md](DATA_PRIORITY_MATRIX.md) for field-level priorities
- See [CONFLICT_RESOLUTION_STRATEGY.md](CONFLICT_RESOLUTION_STRATEGY.md) for handling conflicts
