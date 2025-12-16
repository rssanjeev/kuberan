# Data Pipeline Architecture

**Version:** v1.0  
**Last Updated:** December 15, 2025  
**Status:** 🟢 Active

---

## Overview

This document provides a **high-level architecture** of Kuberan's data pipeline, covering how data flows from external providers through ingestion, standardization, storage, and finally to API endpoints consumed by the frontend.

### Core Philosophy

**No Synthetic Data Principle:**
- NEVER calculate or derive new financial values
- ONLY select existing values from providers based on priority
- Each data point MUST preserve its source provider for transparency
- Weights represent priority rankings (1.0 = highest), NOT calculation coefficients

---

## Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DATA PIPELINE OVERVIEW                        │
└─────────────────────────────────────────────────────────────────────┘

Stage 1: INGEST                    Stage 2: STANDARDIZE
┌──────────────────┐               ┌──────────────────┐
│   Provider APIs  │               │  Standardization │
│                  │               │     Engine       │
│  • YFinance      │──────────────▶│                  │
│  • Finviz        │  Snapshots    │  • Matrix-driven │
│  • StockAnalysis │               │  • Single value  │
│  • MASSIVE       │               │  • Aggregate     │
└──────────────────┘               └──────────────────┘
         │                                  │
         │ Store raw                        │ Store standardized
         ▼                                  ▼
┌──────────────────┐               ┌──────────────────┐
│ Provider         │               │ Standardized     │
│ Snapshot         │               │ Ticker Views     │
│ Collections      │               │ Collection       │
└──────────────────┘               └──────────────────┘
                                            │
                                            │ Query
                                            ▼
                    Stage 3: API           
                    ┌──────────────────┐
                    │  REST Endpoints  │
                    │                  │
                    │  • /standardized │
                    │  • /complete     │
                    │  • /price        │
                    └──────────────────┘
                             │
                             │ Consume
                             ▼
                    Stage 4: FRONTEND
                    ┌──────────────────┐
                    │   Flutter Web    │
                    │                  │
                    │  • Displays data │
                    │  • Shows source  │
                    └──────────────────┘
```

---

## Stage 1: Data Ingestion

### 1.1 Purpose

Fetch raw data from external providers and store **as-is** in provider-specific snapshot collections.

### 1.2 Ingestion Philosophy

**Key Principles:**
1. **Preservation**: Store raw provider data without transformation
2. **Versioning**: Each snapshot includes `snapshot_version` (e.g., `v1`)
3. **Timestamping**: Track `fetched_at` and provider's `as_of_date`
4. **Idempotency**: Re-fetching same data produces identical snapshot
5. **Error Handling**: Failed fetches logged but don't block other providers

### 1.3 Provider Snapshot Structure

Each provider has its own snapshot schema documented in `docs/Ingest/`:

**Common Fields (all providers):**
```json
{
  "provider": "yfinance",         // Provider identifier
  "ticker": "AAPL",               // Stock ticker
  "snapshot_version": "v1",       // Schema version
  "as_of_date": "2025-12-15",     // Provider's data date
  "fetched_at": "2025-12-15T10:30:00Z",  // When we fetched it
  
  // Provider-specific structured data follows...
  "identity": { ... },
  "fundamentals": { ... },
  "prices": { ... }
}
```

**Provider-Specific Documentation:**
- `docs/Ingest/YFINANCE_INGEST_SPEC.md` - YFinance snapshot schema
- `docs/Ingest/MASSIVE_INGEST_SPEC.md` - MASSIVE snapshot schema
- `docs/Ingest/FINVIZ_QUOTE_PAGE_STRUCTURE.md` - Finviz snapshot schema
- `docs/Ingest/STOCKANALYSIS_QUOTE_PAGE_STRUCTURE.md` - StockAnalysis snapshot schema

### 1.4 Snapshot Collections

**MongoDB Collections:**
```
yfinance_snapshots         - YFinance API data
finviz_snapshots          - Finviz web scraping data
stockanalysis_snapshots   - StockAnalysis web scraping data
massive_snapshots         - MASSIVE API data (Polygon.io compatible)
```

**Indexes:**
- Primary: `(ticker, as_of_date)` - Latest snapshot per ticker
- Secondary: `fetched_at` - Cleanup old snapshots
- TTL: Consider 30-90 day retention for non-critical historical data

### 1.5 Ingestion Triggers

**Execution Modes:**

1. **Scheduled Jobs** (Primary):
   - Background jobs run every N minutes/hours
   - Batch fetch for all active tickers
   - Example: `YFinanceFetchJob` runs every 5 minutes during market hours

2. **On-Demand** (Secondary):
   - API endpoint triggers fresh fetch
   - Useful for real-time price updates
   - Respects rate limits and caching

3. **Backfill** (Maintenance):
   - One-time scripts to populate historical data
   - Runs outside normal schedule
   - Example: Initial population of 12K tickers

**Rate Limiting:**
- Each provider has different limits (5 calls/min for MASSIVE, unlimited for YFinance)
- Adaptive rate limiter in `app/services/providers/adaptive_rate_limiter.py`
- Respects `Retry-After` headers

---

## Stage 2: Data Standardization

### 2.1 Purpose

Apply **matrix-driven rules** to select the best value for each data point from multiple provider snapshots.

### 2.2 Standardization Philosophy

**Key Principles:**
1. **Selection, Not Calculation**: Choose existing provider values, never calculate new ones
2. **Priority-Based**: Weights (1.0 = highest) determine selection order
3. **Transparency**: Every selected value includes its source provider
4. **Consistency**: Same rules applied to all tickers
5. **Configurability**: Rules defined in YAML, not hardcoded

### 2.3 Configuration Files

**Authoritative Source:**
- `config/data_priority_matrix.yaml` - Machine-readable configuration (65+ data points)

**Documentation:**
- `docs/Standardization/DATA_PRIORITY_MATRIX.md` - Human-readable design doc
- `docs/Standardization/DATA_STANDARDIZATION_RULES.md` - Rules and strategies
- `docs/Standardization/standardized_ticker_view.md` - Output schema

### 2.4 Standardization Strategies

**Currently Implemented:**

1. **`single_value`** (Primary Strategy - 65 data points):
   - Iterate candidates by descending weight
   - Return first non-null value
   - Example: `market_cap` prefers YFinance (1.0) over MASSIVE (0.95)

2. **`numeric_consensus`** (DEPRECATED):
   - Previously calculated weighted averages
   - **REMOVED** - Violates "no synthetic data" principle
   - All entries migrated to `single_value`

**Future Strategies (Documented but not implemented):**

3. **`aggregate_union`** (For News Articles):
   - Collect items from ALL providers
   - Remove duplicates based on normalization key
   - Preserve source for each item
   - Use case: News articles, corporate actions

4. **`timeseries_primary_with_checks`** (For Price Data):
   - Use primary provider for timeseries
   - Cross-check against other providers for outlier detection
   - Flag anomalies but don't modify values

### 2.5 Standardization Engine

**Location:** `backend/app/services/standardization_engine.py`

**Key Methods:**
```python
class StandardizationEngine:
    def standardize_ticker(self, ticker: str, snapshots: Dict) -> Dict:
        """Main entry point - produces standardized view."""
        
    def _apply_single_value(self, candidates: List, strategy_config: Dict) -> Dict:
        """Select highest-priority non-null value."""
        
    def _apply_numeric_consensus(self, ...):
        """DEPRECATED - Raises ValueError."""
```

**Input Format:**
```python
snapshots = {
    "yfinance": {...},      # YFinance snapshot
    "finviz": {...},        # Finviz snapshot
    "stockanalysis": {...}, # StockAnalysis snapshot
    "massive": {...}        # MASSIVE snapshot
}
```

**Output Format:**
```python
{
    "ticker": "AAPL",
    "version": "v1",
    "as_of": "2025-12-15T10:30:00Z",
    "data_points": {
        "market_cap": {
            "value": 2700000000000,
            "source": "yfinance"
        },
        "sic_code": {
            "value": "3571",
            "source": "massive"
        },
        # ... 64 more data points
    }
}
```

### 2.6 Standardized Storage

**MongoDB Collection:**
```
standardized_ticker_views  - One document per ticker
```

**Indexes:**
- Primary: `ticker` (unique)
- Secondary: `as_of` - Track freshness
- Full-text: `data_points.*.value` - Search across all fields

**Update Strategy:**
- Latest standardization **overwrites** previous document
- Consider keeping historical versions with `version_history` array
- Trigger re-standardization when provider snapshots update

---

## Stage 3: API Exposure

### 3.1 Purpose

Expose standardized data to frontend via REST API endpoints.

### 3.2 Endpoint Design (Planned)

**New Endpoint: `/stocks/standardized/{ticker}`**

**Purpose:**
- Return standardized ticker view with source information for each data point
- Frontend displays transparency: "Market Cap: $2.7T (from YFinance)"

**Implementation Location:**
- `backend/app/routers/stocks/ticker_info.py`

**Request:**
```http
GET /stocks/standardized/AAPL
```

**Response:**
```json
{
    "ticker": "AAPL",
    "version": "v1",
    "as_of": "2025-12-15T10:30:00Z",
    "data_points": {
        "market_cap": {
            "value": 2700000000000,
            "source": "yfinance",
            "display_value": "$2.70T"
        },
        "sic_code": {
            "value": "3571",
            "source": "massive"
        },
        // ... all 66 data points with sources
    },
    "metadata": {
        "providers_queried": ["yfinance", "finviz", "stockanalysis", "massive"],
        "providers_available": ["yfinance", "massive"],
        "fields_resolved": 66,
        "fields_missing": 0
    }
}
```

**Query Parameters (Future):**
```
?fields=market_cap,sector,pe_ratio  # Return only specified fields
?include_inputs=true                 # Include all provider values, not just selected
?format=flat                         # Flatten structure for simpler frontend parsing
```

### 3.3 Existing Endpoints (Reference)

**Current endpoints in `ticker_info.py`:**
- `GET /stocks/price/{ticker}` - Lightweight price-only
- `GET /stocks/complete/{ticker}` - Comprehensive info (yfinance + MASSIVE merged)
- `GET /stocks/related-companies/{ticker}` - Related companies

**Note:** `/complete/{ticker}` manually merges data but doesn't use StandardizationEngine or expose sources.

---

## Stage 4: Frontend Consumption

### 4.1 Purpose

Display standardized data to users with full transparency about data sources.

### 4.2 Frontend Requirements

**Display Patterns:**

1. **Source Badge:**
   ```
   Market Cap: $2.70T [YFinance]
   Sector: Technology [StockAnalysis]
   ```

2. **Tooltip on Hover:**
   ```
   Market Cap: $2.70T
   ────────────────────
   Source: YFinance
   Updated: 2 minutes ago
   ```

3. **Multi-Source Indicator:**
   ```
   Revenue: $385B [MASSIVE] ⓘ
   
   On hover:
   "This value is from MASSIVE. StockAnalysis also reported $384B."
   ```

4. **Missing Data Handling:**
   ```
   PEG Ratio: N/A
   Tooltip: "Not available from any provider"
   ```

### 4.3 Frontend Architecture

**Technology:** Flutter (Web, iOS, Android)

**Service Layer:**
```dart
class StandardizedDataService {
  Future<StandardizedTickerView> getStandardizedData(String ticker);
  
  String getSourceBadge(String provider) {
    // Returns color-coded badge (YFinance=blue, MASSIVE=purple, etc.)
  }
  
  Widget buildSourceTooltip(DataPoint dataPoint);
}
```

**UI Components:**
```dart
// Stat card showing one data point with source
StatCard(
  label: "Market Cap",
  value: "$2.70T",
  source: "YFinance",
  onTap: () => showSourceDetails()
)

// Data table with source column
DataTable(
  columns: ["Field", "Value", "Source", "Updated"],
  rows: [
    ["Market Cap", "$2.70T", "YFinance", "2m ago"],
    ["Sector", "Technology", "StockAnalysis", "1h ago"],
  ]
)
```

---

## Data Flow Examples

### Example 1: Stock Quote Request

```
User Action: Clicks "View AAPL" in frontend

1. Frontend → API: GET /stocks/standardized/AAPL

2. API Layer (ticker_info.py):
   - Check if standardized view exists and is fresh
   - If stale or missing, trigger standardization
   
3. Standardization Layer (standardization_engine.py):
   - Fetch provider snapshots from MongoDB:
     * yfinance_snapshots.find_one({"ticker": "AAPL"})
     * finviz_snapshots.find_one({"ticker": "AAPL"})
     * stockanalysis_snapshots.find_one({"ticker": "AAPL"})
     * massive_snapshots.find_one({"ticker": "AAPL"})
   
   - Load data_priority_matrix.yaml
   - For each of 66 data points:
     * Get candidates from all providers
     * Apply single_value strategy (weight-based selection)
     * Store selected value + source
   
   - Save to standardized_ticker_views collection
   
4. API Layer:
   - Return standardized view with 66 data points
   
5. Frontend:
   - Parse response
   - Display stat cards with source badges
   - Show tooltips on hover
   - Enable drill-down to see all provider values
```

### Example 2: Background Standardization Job

```
Scheduled Job: Every 5 minutes during market hours

1. Job (standardization_job.py):
   - Query active tickers from ticker_config
   - For each ticker in batch (50 at a time):
     * Check if provider snapshots are fresh (< 10 minutes old)
     * If stale, skip (wait for ingest jobs to run first)
     * Call standardization_engine.standardize_ticker(ticker, snapshots)
     * Upsert to standardized_ticker_views
   
2. Result:
   - All active tickers have fresh standardized views
   - API requests served from cached standardized views (fast)
   - No need to standardize on-demand
```

---

## Special Cases

### Case 1: News Article Aggregation

**Strategy:** `aggregate_union` (Future Implementation)

**Philosophy:**
- Unlike stock metrics where we choose ONE value, news articles are AGGREGATED
- Multiple providers can report the same news article
- Remove duplicates based on normalized URL or article ID
- Preserve source for each unique article

**Example Output:**
```json
{
    "ticker": "AAPL",
    "news_articles": [
        {
            "title": "Apple Announces New iPhone",
            "url": "https://reuters.com/...",
            "published_at": "2025-12-15T09:00:00Z",
            "source": "massive",
            "sentiment": "positive"
        },
        {
            "title": "Apple Announces New iPhone",
            "url": "https://reuters.com/...",  // Same article
            "published_at": "2025-12-15T09:00:00Z",
            "source": "yfinance",  // Different provider, same article
            "sentiment": null
        },
        {
            "title": "iPhone Sales Beat Expectations",
            "url": "https://bloomberg.com/...",
            "published_at": "2025-12-15T10:30:00Z",
            "source": "finnhub",
            "sentiment": "positive"
        }
    ]
}
```

**After Deduplication:**
```json
{
    "ticker": "AAPL",
    "news_articles": [
        {
            "title": "Apple Announces New iPhone",
            "url": "https://reuters.com/...",
            "published_at": "2025-12-15T09:00:00Z",
            "sources": ["massive", "yfinance"],  // Both reported it
            "sentiment": "positive"  // Take non-null sentiment
        },
        {
            "title": "iPhone Sales Beat Expectations",
            "url": "https://bloomberg.com/...",
            "published_at": "2025-12-15T10:30:00Z",
            "sources": ["finnhub"],
            "sentiment": "positive"
        }
    ]
}
```

**Deduplication Strategy:**
1. Normalize URLs (remove tracking params, trailing slashes)
2. Compare normalized URLs for exact match
3. Fallback: Compare title + published_date similarity (Levenshtein distance)
4. Merge metadata from all providers reporting same article

### Case 2: Price Timeseries

**Strategy:** `timeseries_primary_with_checks` (Future Implementation)

**Philosophy:**
- Use ONE provider as primary source for consistency
- Cross-check against other providers for outlier detection
- Flag anomalies but don't modify values (preserve "no synthetic data" rule)

**Example:**
```python
{
    "ticker": "AAPL",
    "prices": [
        {
            "timestamp": "2025-12-15T09:30:00Z",
            "open": 173.85,
            "high": 175.10,
            "low": 173.50,
            "close": 174.49,
            "volume": 50123456,
            "source": "yfinance",  // Primary source
            "cross_checks": {
                "massive": {
                    "close": 174.50,  // Slight difference
                    "delta_pct": 0.006  // 0.6% difference
                },
                "anomaly_detected": false
            }
        },
        {
            "timestamp": "2025-12-15T09:31:00Z",
            "open": 174.49,
            "high": 174.80,
            "low": 174.30,
            "close": 174.60,
            "volume": 1234567,
            "source": "yfinance",
            "cross_checks": {
                "massive": {
                    "close": 169.50,  // Large difference!
                    "delta_pct": 2.92  // 2.92% difference
                },
                "anomaly_detected": true,
                "anomaly_reason": "Close price differs by >1% from secondary source"
            }
        }
    ]
}
```

**Use Case:**
- Frontend can show warning icon for anomalous data points
- Users can drill down to see all provider values
- Helps identify provider API issues or data quality problems

### Case 3: Corporate Actions

**Strategy:** `aggregate_union` (Future Implementation)

**Philosophy:**
- Collect stock splits and dividends from all providers
- Merge and deduplicate by date + type
- Resolve conflicts (e.g., different split ratios reported)

**Example:**
```json
{
    "ticker": "AAPL",
    "corporate_actions": {
        "splits": [
            {
                "date": "2020-08-31",
                "ratio": "4:1",
                "sources": ["yfinance", "massive", "stockanalysis"],
                "consensus": true
            }
        ],
        "dividends": [
            {
                "ex_date": "2025-11-08",
                "pay_date": "2025-11-15",
                "amount": 0.24,
                "sources": ["yfinance", "massive"],
                "consensus": true
            },
            {
                "ex_date": "2025-08-09",
                "pay_date": "2025-08-16",
                "amount": 0.24,
                "sources": ["yfinance"],  // Only one provider
                "consensus": false,
                "note": "Verify with additional sources"
            }
        ]
    }
}
```

---

## Documentation Status

### ✅ Fully Documented

1. **Ingestion Layer:**
   - ✅ Provider snapshot schemas (`docs/Ingest/*.md`)
   - ✅ YFinance ingest spec
   - ✅ MASSIVE ingest spec
   - ✅ Finviz page structure
   - ✅ StockAnalysis page structure

2. **Standardization Layer:**
   - ✅ Data standardization rules (`docs/Standardization/DATA_STANDARDIZATION_RULES.md`)
   - ✅ Data priority matrix design (`docs/Standardization/DATA_PRIORITY_MATRIX.md`)
   - ✅ Standardized ticker view schema (`docs/Standardization/standardized_ticker_view.md`)
   - ✅ Matrix configuration (`config/data_priority_matrix.yaml`)

3. **Implementation:**
   - ✅ Standardization engine (`backend/app/services/standardization_engine.py`)
   - ✅ Test fixtures and golden bundles (`backend/app/tests/standardization_fixtures/`)
   - ✅ End-to-end tests (`backend/app/tests/test_standardization_aapl_v0.py`)

4. **Philosophy:**
   - ✅ "No Synthetic Data" principle documented in `.github/copilot-instructions.md`
   - ✅ Weight semantics clarified (priority, not coefficients)

### 🟡 Partially Documented

5. **API Layer:**
   - 🟡 Existing endpoints documented (`docs/API.md`)
   - ❌ `/standardized/{ticker}` endpoint (not yet implemented)
   - ❌ Response schemas for standardized views
   - ❌ Error handling patterns

6. **Background Jobs:**
   - 🟡 Job scheduler framework exists
   - ❌ Standardization job specification
   - ❌ Job execution frequency and triggers
   - ❌ Job monitoring and alerting

### ❌ Not Yet Documented

7. **News Article Aggregation:**
   - ❌ Ingest specs for news providers
   - ❌ Deduplication algorithm
   - ❌ `aggregate_union` strategy implementation plan
   - ❌ News article schema
   - ❌ API endpoints for news

8. **Price Timeseries:**
   - ❌ `timeseries_primary_with_checks` strategy implementation plan
   - ❌ Outlier detection algorithm
   - ❌ Anomaly flagging rules
   - ❌ Timeseries storage schema

9. **Corporate Actions:**
   - ❌ Corporate actions aggregation strategy
   - ❌ Split/dividend deduplication
   - ❌ Conflict resolution rules
   - ❌ API endpoints for corporate actions

10. **Frontend Integration:**
    - ❌ Frontend service layer design
    - ❌ UI component specifications
    - ❌ Source badge styling guidelines
    - ❌ Tooltip content and formatting

11. **Monitoring & Observability:**
    - ❌ Metrics to track (data quality, provider availability, etc.)
    - ❌ Alerting rules (stale data, missing providers, anomalies)
    - ❌ Dashboard design (Grafana/Datadog/Prometheus)

12. **Migration & Deployment:**
    - ❌ Migration plan for existing data
    - ❌ Rollout strategy (gradual vs. big bang)
    - ❌ Rollback procedures
    - ❌ Backward compatibility considerations

---

## Next Steps

### Immediate (Before Coding)

1. **Document News Aggregation Strategy:**
   - Create `docs/Standardization/NEWS_AGGREGATION_STRATEGY.md`
   - Define deduplication algorithm
   - Specify `aggregate_union` strategy parameters
   - Design news article schema

2. **Document API Layer:**
   - Create `docs/API_STANDARDIZATION_ENDPOINTS.md`
   - Specify `/standardized/{ticker}` endpoint contract
   - Define response schemas
   - Document error handling patterns

3. **Document Background Jobs:**
   - Create `docs/STANDARDIZATION_JOBS.md`
   - Specify job triggers and schedules
   - Define monitoring metrics
   - Document failure recovery

4. **Document Frontend Integration:**
   - Create `docs/FRONTEND_DATA_DISPLAY.md`
   - Specify UI component requirements
   - Define source badge styling
   - Document user interactions (tooltips, drill-downs)

### Short-Term (Next Sprint)

5. **Implement API Endpoint:**
   - Add `/standardized/{ticker}` to `ticker_info.py`
   - Wire up StandardizationEngine
   - Add response models
   - Write integration tests

6. **Implement Background Jobs:**
   - Create `standardization_job.py`
   - Register in scheduler
   - Add monitoring metrics
   - Test with batch of tickers

7. **Frontend Prototype:**
   - Create source badge component
   - Implement tooltip on hover
   - Test with real API data

### Medium-Term (Future Sprints)

8. **News Article Aggregation:**
   - Implement `aggregate_union` strategy
   - Add news provider ingest jobs
   - Create deduplication service
   - Build news API endpoints

9. **Price Timeseries:**
   - Implement `timeseries_primary_with_checks` strategy
   - Add outlier detection
   - Create anomaly flagging service
   - Build timeseries API endpoints

10. **Monitoring & Observability:**
    - Define key metrics
    - Set up dashboards
    - Configure alerts
    - Document runbooks

---

## Open Questions

### Technical Decisions Needed

1. **Standardization Freshness:**
   - Q: How often should we re-standardize ticker data?
   - Options:
     - A: Every time provider snapshot updates (real-time, expensive)
     - B: Scheduled job every N minutes (batch, efficient)
     - C: On-demand when API requested + cached (lazy, inconsistent)
   - **Recommendation:** Option B (scheduled job every 5 minutes) + cache

2. **Historical Standardized Views:**
   - Q: Should we keep historical versions of standardized views?
   - Options:
     - A: Overwrite (always latest, simple)
     - B: Keep last N versions (point-in-time queries, storage cost)
     - C: Event sourcing (full history, complex)
   - **Recommendation:** Option A for now, Option B if needed later

3. **Partial Provider Availability:**
   - Q: What if only 1 out of 4 providers has data?
   - Options:
     - A: Standardize with available data only
     - B: Wait for minimum N providers (e.g., 2 out of 4)
     - C: Flag as "incomplete" in metadata
   - **Recommendation:** Option A + Option C (standardize but flag as incomplete)

4. **News Article URL Normalization:**
   - Q: How aggressive should we be with URL normalization?
   - Options:
     - A: Strict (exact match after removing query params)
     - B: Moderate (fuzzy match on domain + path)
     - C: Aggressive (fuzzy match on title + date)
   - **Recommendation:** Start with Option A, add Option C for edge cases

### Architectural Decisions Needed

5. **API Response Format:**
   - Q: Should `/standardized/{ticker}` return all 66 fields always?
   - Options:
     - A: Always return all fields (consistent, larger payload)
     - B: Allow field selection via query param (flexible, more complex)
   - **Recommendation:** Option A initially, add Option B if payload size becomes issue

6. **Frontend State Management:**
   - Q: How should frontend cache standardized data?
   - Options:
     - A: No caching (always fetch, simple but slow)
     - B: Local storage (persistent, but can get stale)
     - C: In-memory cache with TTL (balance freshness and performance)
   - **Recommendation:** Option C (cache for 1 minute, then refetch)

---

## Glossary

- **Data Point:** Single semantic value for a ticker (e.g., market_cap, sector)
- **Provider Snapshot:** Raw data from one provider stored as-is
- **Standardized View:** Matrix-driven consolidated view with sources
- **Single Value Strategy:** Select highest-priority non-null value
- **Aggregate Union Strategy:** Collect and deduplicate from all providers
- **Weight:** Priority ranking (1.0 = highest priority)
- **Source:** Provider that supplied the selected value
- **Synthetic Data:** Calculated or derived values (NEVER create these!)

---

## References

### Internal Documentation
- `.github/copilot-instructions.md` - Project philosophy and principles
- `docs/Standardization/DATA_STANDARDIZATION_RULES.md` - Standardization rules
- `docs/Standardization/DATA_PRIORITY_MATRIX.md` - Matrix design
- `config/data_priority_matrix.yaml` - Authoritative configuration

### External Resources
- [YFinance Documentation](https://pypi.org/project/yfinance/)
- [MASSIVE API Reference](https://massive.io/docs)
- [Finviz Website](https://finviz.com)
- [StockAnalysis Website](https://stockanalysis.com)

---

**Document Owner:** Engineering Team  
**Last Reviewed:** December 15, 2025  
**Next Review:** After implementing API endpoint
