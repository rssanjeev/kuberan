# Standardization API Endpoints

**Last Updated:** December 16, 2025  
**Status:** 🟡 Draft - Specification in progress  
**Purpose:** Define REST API contracts for accessing standardized ticker data  
**Related Docs:**
- [DATA_PIPELINE_ARCHITECTURE.md](../DATA_PIPELINE_ARCHITECTURE.md) - Pipeline stage 3 (API Exposure)
- [DATA_STANDARDIZATION_RULES.md](../DATA_STANDARDIZATION_RULES.md) - Standardization rules
- [Standardization/standardized_ticker_view.md](../Standardization/standardized_ticker_view.md) - Output schema

---

## Overview

The Standardization API provides access to consolidated ticker data from multiple providers, applying standardization rules and priority matrices to deliver single authoritative values or aggregated collections.

### Key Features

- **Multi-Provider Consolidation**: Combines data from YFinance, MASSIVE, Finviz, StockAnalysis
- **Strategy-Based Standardization**: Applies `single_value` or `aggregate_union` per data point
- **Priority Matrix**: Uses provider priority rankings for conflict resolution
- **Source Transparency**: Returns provider attribution for all data points
- **Freshness Tracking**: Includes timestamps for data staleness detection

### Base URL

```
http://localhost:8000/standardized
```

---

## Endpoints

### 1. Get Standardized Ticker Data

**Endpoint:** `GET /standardized/{ticker}`

**Description:** Returns standardized ticker data by applying priority matrix and standardization strategies to raw provider snapshots.

#### Request

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker symbol (e.g., "AAPL", "MSFT") |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_sources` | boolean | No | `false` | Include provider source attribution for each field |
| `include_timestamps` | boolean | No | `false` | Include snapshot timestamps for freshness tracking |
| `strategy_override` | string | No | - | Override default strategy for specific data points (expert mode) |
| `max_age_hours` | integer | No | `24` | Maximum age of snapshots to consider (hours) |

#### Response

**Success Response (200 OK):**

```json
{
  "ticker": "AAPL",
  "standardized_at": "2025-12-16T14:30:00Z",
  "data": {
    "company_name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": 2770000000000,
    "current_price": 185.50,
    "volume": 65432100,
    "pe_ratio": 28.5,
    "dividend_yield": 0.0053,
    "52_week_high": 199.62,
    "52_week_low": 124.17,
    "beta": 1.29,
    "news": [
      {
        "title": "Apple Announces New Product Line",
        "source": "Reuters",
        "published_at": "2025-12-16T10:00:00Z",
        "url": "https://reuters.com/article/123",
        "snippet": "Apple unveiled its latest innovation..."
      },
      {
        "title": "Apple Stock Hits Record High",
        "source": "Bloomberg",
        "published_at": "2025-12-16T09:30:00Z",
        "url": "https://bloomberg.com/news/456",
        "snippet": "Shares of Apple Inc. reached..."
      }
    ]
  },
  "metadata": {
    "providers_used": ["yfinance", "massive", "finviz"],
    "snapshot_count": 3,
    "freshness": "current"
  }
}
```

**With `include_sources=true`:**

```json
{
  "ticker": "AAPL",
  "standardized_at": "2025-12-16T14:30:00Z",
  "data": {
    "company_name": {
      "value": "Apple Inc.",
      "source": "yfinance",
      "strategy": "single_value",
      "priority_rank": 1
    },
    "sector": {
      "value": "Technology",
      "source": "massive",
      "strategy": "single_value",
      "priority_rank": 1
    },
    "current_price": {
      "value": 185.50,
      "source": "yfinance",
      "strategy": "single_value",
      "priority_rank": 1
    },
    "news": {
      "value": [
        {
          "title": "Apple Announces New Product Line",
          "source": "Reuters",
          "published_at": "2025-12-16T10:00:00Z",
          "url": "https://reuters.com/article/123",
          "snippet": "Apple unveiled its latest innovation...",
          "_metadata": {
            "provider": "finviz",
            "extracted_at": "2025-12-16T14:00:00Z"
          }
        },
        {
          "title": "Apple Stock Hits Record High",
          "source": "Bloomberg",
          "published_at": "2025-12-16T09:30:00Z",
          "url": "https://bloomberg.com/news/456",
          "snippet": "Shares of Apple Inc. reached...",
          "_metadata": {
            "provider": "stockanalysis",
            "extracted_at": "2025-12-16T13:45:00Z"
          }
        }
      ],
      "strategy": "aggregate_union",
      "providers": ["finviz", "stockanalysis"],
      "deduplication": {
        "method": "url_fingerprint",
        "duplicates_removed": 1
      }
    }
  },
  "metadata": {
    "providers_used": ["yfinance", "massive", "finviz", "stockanalysis"],
    "snapshot_count": 4,
    "freshness": "current"
  }
}
```

**With `include_timestamps=true`:**

```json
{
  "ticker": "AAPL",
  "standardized_at": "2025-12-16T14:30:00Z",
  "data": {
    "company_name": "Apple Inc.",
    "current_price": 185.50,
    "news": [
      {
        "title": "Apple Announces New Product Line",
        "source": "Reuters",
        "published_at": "2025-12-16T10:00:00Z",
        "url": "https://reuters.com/article/123"
      }
    ]
  },
  "metadata": {
    "providers_used": ["yfinance", "massive", "finviz"],
    "snapshot_count": 3,
    "freshness": "current",
    "snapshots": [
      {
        "provider": "yfinance",
        "snapshot_id": "abc123",
        "collected_at": "2025-12-16T14:25:00Z",
        "age_minutes": 5
      },
      {
        "provider": "massive",
        "snapshot_id": "def456",
        "collected_at": "2025-12-16T14:20:00Z",
        "age_minutes": 10
      },
      {
        "provider": "finviz",
        "snapshot_id": "ghi789",
        "collected_at": "2025-12-16T14:00:00Z",
        "age_minutes": 30
      }
    ]
  }
}
```

**Error Responses:**

**404 Not Found:**
```json
{
  "error": "ticker_not_found",
  "message": "No snapshots found for ticker 'INVALID'",
  "ticker": "INVALID"
}
```

**400 Bad Request:**
```json
{
  "error": "invalid_parameter",
  "message": "max_age_hours must be between 1 and 168",
  "parameter": "max_age_hours",
  "provided_value": 200
}
```

**500 Internal Server Error:**
```json
{
  "error": "standardization_failed",
  "message": "Error applying standardization rules",
  "ticker": "AAPL",
  "details": "Missing priority matrix configuration for data point 'sector'"
}
```

#### Business Logic

**Standardization Process:**

1. **Fetch Snapshots**: Query `provider_snapshots` collection for ticker within `max_age_hours`
2. **Load Priority Matrix**: Load provider priorities from `config/data_priority_matrix.yaml`
3. **Apply Strategies**: For each data point:
   - **single_value**: Select value from highest priority provider (if available)
   - **aggregate_union**: Merge arrays from all providers with deduplication
4. **Add Metadata**: Include source attribution if `include_sources=true`
5. **Return Response**: Format as standardized ticker view

**Caching Strategy:**

- **Cache Key**: `standardized:{ticker}:{include_sources}:{include_timestamps}:{max_age_hours}`
- **TTL**: 5 minutes (data freshness requirement)
- **Invalidation**: On new snapshot ingestion for ticker

**Performance Considerations:**

- Index on `(ticker, provider, collected_at)` for fast snapshot queries
- Pre-compute standardized views for top 500 tickers (background job)
- Cache standardized responses (5 minute TTL)

---

### 2. Get Standardization Metadata

**Endpoint:** `GET /standardized/{ticker}/meta`

**Description:** Returns metadata about standardization process without full data payload.

#### Request

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker symbol |

#### Response

**Success Response (200 OK):**

```json
{
  "ticker": "AAPL",
  "available_providers": ["yfinance", "massive", "finviz", "stockanalysis"],
  "snapshot_count": 4,
  "freshest_snapshot": {
    "provider": "yfinance",
    "collected_at": "2025-12-16T14:25:00Z",
    "age_minutes": 5
  },
  "oldest_snapshot": {
    "provider": "finviz",
    "collected_at": "2025-12-16T14:00:00Z",
    "age_minutes": 30
  },
  "data_completeness": {
    "total_fields": 45,
    "populated_fields": 42,
    "coverage_percentage": 93.3
  },
  "priority_matrix_version": "v1",
  "last_standardized": "2025-12-16T14:30:00Z"
}
```

---

### 3. Bulk Standardization

**Endpoint:** `POST /standardized/bulk`

**Description:** Get standardized data for multiple tickers in one request.

#### Request

**Request Body:**

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "include_sources": false,
  "include_timestamps": false,
  "max_age_hours": 24
}
```

**Body Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tickers` | array[string] | Yes | - | List of ticker symbols (max 50) |
| `include_sources` | boolean | No | `false` | Include provider source attribution |
| `include_timestamps` | boolean | No | `false` | Include snapshot timestamps |
| `max_age_hours` | integer | No | `24` | Maximum snapshot age (hours) |

#### Response

**Success Response (200 OK):**

```json
{
  "results": [
    {
      "ticker": "AAPL",
      "status": "success",
      "data": {
        "company_name": "Apple Inc.",
        "current_price": 185.50,
        ...
      }
    },
    {
      "ticker": "MSFT",
      "status": "success",
      "data": {
        "company_name": "Microsoft Corporation",
        "current_price": 372.15,
        ...
      }
    },
    {
      "ticker": "INVALID",
      "status": "error",
      "error": "ticker_not_found",
      "message": "No snapshots found for ticker 'INVALID'"
    }
  ],
  "summary": {
    "total_requested": 4,
    "successful": 3,
    "failed": 1
  }
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "too_many_tickers",
  "message": "Maximum 50 tickers allowed per request",
  "provided_count": 75
}
```

---

## Data Schema

### Standardized Ticker Response

See [Standardization/standardized_ticker_view.md](../Standardization/standardized_ticker_view.md) for complete field-level schema.

**Top-Level Structure:**

```typescript
{
  ticker: string;              // Ticker symbol
  standardized_at: timestamp;  // Standardization timestamp (ISO 8601)
  data: {
    // Single-value fields (strategy: single_value)
    company_name?: string;
    sector?: string;
    industry?: string;
    market_cap?: number;
    current_price?: number;
    // ... (see schema doc for complete list)
    
    // Aggregate fields (strategy: aggregate_union)
    news?: NewsArticle[];
    // ... (see schema doc for complete list)
  };
  metadata: {
    providers_used: string[];   // List of providers contributing data
    snapshot_count: number;     // Total snapshots used
    freshness: "current" | "stale" | "very_stale";  // Data freshness indicator
    snapshots?: SnapshotMetadata[];  // Optional: snapshot details
  };
}
```

### Source Attribution (when `include_sources=true`)

**Single-Value Fields:**

```typescript
{
  value: any;
  source: string;           // Provider name
  strategy: "single_value";
  priority_rank: number;    // Provider rank in priority matrix
}
```

**Aggregate Fields:**

```typescript
{
  value: any[];
  strategy: "aggregate_union";
  providers: string[];      // List of providers contributing items
  deduplication: {
    method: string;         // Deduplication algorithm used
    duplicates_removed: number;
  };
}
```

---

## Error Handling

### Error Response Format

All errors follow consistent format:

```typescript
{
  error: string;        // Machine-readable error code
  message: string;      // Human-readable error message
  ticker?: string;      // Ticker symbol (if applicable)
  parameter?: string;   // Parameter name (for validation errors)
  details?: any;        // Additional error details
}
```

### Error Codes

| Code | HTTP Status | Description | Resolution |
|------|-------------|-------------|------------|
| `ticker_not_found` | 404 | No snapshots found for ticker | Verify ticker symbol, check if ingestion succeeded |
| `invalid_parameter` | 400 | Invalid query parameter value | Check parameter constraints in spec |
| `too_many_tickers` | 400 | Bulk request exceeds max limit | Reduce ticker count to ≤50 |
| `standardization_failed` | 500 | Error in standardization engine | Check priority matrix config, retry request |
| `missing_priority_matrix` | 500 | Priority matrix not loaded | Verify `data_priority_matrix.yaml` exists |

---

## Rate Limiting

**Limits:**

- **Single ticker**: 100 requests/minute per IP
- **Bulk endpoint**: 10 requests/minute per IP

**Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702742400
```

**429 Response:**

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30
}
```

---

## Caching

**Client-Side Caching:**

Responses include standard HTTP caching headers:

```
Cache-Control: public, max-age=300
ETag: "abc123..."
Last-Modified: Mon, 16 Dec 2025 14:30:00 GMT
```

**Conditional Requests:**

Clients can use `If-None-Match` or `If-Modified-Since` headers to avoid unnecessary data transfer.

**304 Response:**

```
HTTP/1.1 304 Not Modified
ETag: "abc123..."
```

---

## Implementation Checklist

**Service Layer:**

- [ ] Create `StandardizationService` in `backend/app/services/standardization/`
- [ ] Implement `standardize_ticker(ticker, options)` method
- [ ] Implement `get_standardization_metadata(ticker)` method
- [ ] Implement `standardize_bulk(tickers, options)` method
- [ ] Load priority matrix from `config/data_priority_matrix.yaml`
- [ ] Apply `single_value` strategy (select by priority)
- [ ] Apply `aggregate_union` strategy (merge with deduplication)
- [ ] Add source attribution when `include_sources=true`
- [ ] Add timestamp metadata when `include_timestamps=true`

**Repository Layer:**

- [ ] Create `StandardizationRepository` in `backend/app/repositories/`
- [ ] Method: `get_snapshots_for_ticker(ticker, max_age_hours)`
- [ ] Method: `get_snapshots_for_tickers(tickers, max_age_hours)` (bulk)
- [ ] Method: `cache_standardized_view(ticker, data, ttl=300)`
- [ ] Method: `get_cached_standardized_view(ticker)`

**Router Layer:**

- [ ] Create `backend/app/routers/standardization.py`
- [ ] Endpoint: `GET /standardized/{ticker}`
- [ ] Endpoint: `GET /standardized/{ticker}/meta`
- [ ] Endpoint: `POST /standardized/bulk`
- [ ] Add query parameter validation
- [ ] Add rate limiting middleware
- [ ] Add response caching headers

**Testing:**

- [ ] Unit tests for `StandardizationService`
- [ ] Unit tests for priority matrix loading
- [ ] Unit tests for `single_value` strategy
- [ ] Unit tests for `aggregate_union` strategy
- [ ] Integration tests for endpoint responses
- [ ] Test with mock provider snapshots
- [ ] Test error handling (missing ticker, invalid params)
- [ ] Load test bulk endpoint (50 tickers)

**Documentation:**

- [ ] Update `docs/API.md` with endpoint links
- [ ] Update Postman collection with examples
- [ ] Add curl examples to README
- [ ] Document caching strategy in ARCHITECTURE.md

---

**Last Updated:** December 16, 2025  
**Status:** 🟡 Draft  
**Next Review:** After implementation complete
