# Planning Checklist - Before Implementation

**Status:** 🟡 Planning Phase  
**Created:** December 15, 2025  
**Purpose:** Track what needs to be documented/decided before implementing API endpoints

---

## ✅ COMPLETED - Ready to Use

### Ingestion Layer
- ✅ **Provider Snapshot Schemas** (`docs/Ingest/`)
  - YFinance ingest spec
  - MASSIVE ingest spec  
  - Finviz page structure
  - StockAnalysis page structure
- ✅ **Ingestion Philosophy:** Preserve raw data, no transformation
- ✅ **Storage:** Provider-specific snapshot collections

### Standardization Layer
- ✅ **Rules & Strategies** (`docs/Standardization/`)
  - Data standardization rules
  - Data priority matrix design
  - Standardized ticker view schema
- ✅ **Configuration:** `config/data_priority_matrix.yaml` (65 data points)
- ✅ **Implementation:** `backend/app/services/standardization_engine.py`
- ✅ **Testing:** Golden fixtures and end-to-end tests
- ✅ **Philosophy:** "No Synthetic Data" principle enforced

### Core Principle
- ✅ **No Synthetic Data:** NEVER calculate or derive financial values
- ✅ **Weight Semantics:** Weights = priority (1.0 = highest), NOT coefficients
- ✅ **Source Transparency:** Every data point includes source provider

---

## 🟡 NEEDS DOCUMENTATION - Before Implementation

### 1. News Article Aggregation Strategy
**Priority:** HIGH (mentioned by user as next use case)

**What to Document:**
- [ ] News ingest specs for each provider (format, fields, API details)
- [ ] `aggregate_union` strategy specification
- [ ] Deduplication algorithm:
  - URL normalization rules (remove tracking params, canonicalize)
  - Fuzzy matching for similar articles (Levenshtein distance threshold?)
  - Title + date matching for non-URL duplicates
- [ ] News article schema (standardized view)
- [ ] Source preservation pattern (multiple sources per article)
- [ ] Conflict resolution (different publish dates, sentiments, etc.)

**Questions to Answer:**
- Q1: How aggressive should URL normalization be?
- Q2: Should we merge metadata from all providers reporting same article?
- Q3: What if providers report different publish dates for same article?
- Q4: How to handle article updates/corrections?

**Document to Create:**
- `docs/Standardization/NEWS_AGGREGATION_STRATEGY.md`

**Estimated Effort:** 2-3 hours

---

### 2. API Endpoint Specifications
**Priority:** HIGH (blocks frontend integration)

**What to Document:**
- [ ] `/stocks/standardized/{ticker}` endpoint contract
  - Request parameters (required vs. optional)
  - Response schema (Pydantic models)
  - Error responses (404, 500, etc.)
  - Performance characteristics (expected latency)
- [ ] Query parameter options:
  - `?fields=field1,field2` - Partial response
  - `?include_inputs=true` - Show all provider values
  - `?format=flat` - Flatten structure
- [ ] Caching strategy:
  - TTL for standardized views
  - Cache invalidation triggers
  - ETag/Last-Modified headers
- [ ] Rate limiting considerations

**Questions to Answer:**
- Q1: Should we always return all 66 fields or allow field selection?
- Q2: How to handle missing data (null vs. omit field)?
- Q3: Should we include metadata about provider availability?
- Q4: What's the expected latency (target: <100ms)?

**Document to Create:**
- `docs/API_STANDARDIZATION_ENDPOINTS.md`

**Estimated Effort:** 1-2 hours

---

### 3. Background Standardization Jobs
**Priority:** MEDIUM (can implement on-demand first)

**What to Document:**
- [ ] Job specification:
  - Trigger: Scheduled (every N minutes) vs. Event-driven (on snapshot update)
  - Batch size: How many tickers per execution
  - Error handling: Retry logic, failure recovery
- [ ] Freshness requirements:
  - How old can provider snapshots be before we skip standardization?
  - How to detect stale snapshots?
- [ ] Monitoring metrics:
  - Success/failure rates
  - Processing time per ticker
  - Data quality metrics (fields resolved vs. missing)
- [ ] Job prioritization:
  - High-priority tickers (large cap, frequently traded)
  - Low-priority tickers (penny stocks, illiquid)

**Questions to Answer:**
- Q1: Should standardization happen immediately after ingest or scheduled?
- Q2: What if 1 out of 4 providers is unavailable?
- Q3: How to handle partial data (only some providers have snapshots)?
- Q4: Should we keep historical standardized views or just latest?

**Document to Create:**
- `docs/STANDARDIZATION_JOBS.md`

**Estimated Effort:** 1 hour

---

### 4. Frontend Integration Patterns
**Priority:** MEDIUM (after API endpoint is implemented)

**What to Document:**
- [ ] UI component specifications:
  - Source badge component (color-coded by provider)
  - Tooltip component (show provider details on hover)
  - Data table with source column
  - Missing data placeholders
- [ ] State management:
  - Caching strategy (in-memory, localStorage)
  - TTL for cached data
  - Refresh triggers
- [ ] User interactions:
  - Click source badge → Show all provider values
  - Hover data point → Show provider details
  - Toggle: Hide/show source information
- [ ] Error handling:
  - Loading states
  - Error messages
  - Retry logic

**Questions to Answer:**
- Q1: How should we visually distinguish providers (colors, icons)?
- Q2: Should source badges always be visible or hidden by default?
- Q3: How to handle mobile views (limited space)?
- Q4: Should we allow users to choose preferred provider?

**Document to Create:**
- `docs/FRONTEND_DATA_DISPLAY.md`

**Estimated Effort:** 1-2 hours

---

### 5. Price Timeseries Strategy
**Priority:** LOW (future feature, not blocking)

**What to Document:**
- [ ] `timeseries_primary_with_checks` strategy specification
- [ ] Outlier detection algorithm:
  - Threshold for flagging anomalies (e.g., >1% difference)
  - Statistical methods (z-score, IQR)
- [ ] Anomaly handling:
  - Flag but don't modify (preserve "no synthetic data")
  - Logging and alerting
- [ ] Timeseries storage schema
- [ ] API endpoints for historical prices

**Document to Create:**
- `docs/Standardization/TIMESERIES_STANDARDIZATION_STRATEGY.md`

**Estimated Effort:** 2 hours

---

### 6. Corporate Actions Aggregation
**Priority:** LOW (future feature, not blocking)

**What to Document:**
- [ ] Corporate actions aggregation strategy
- [ ] Split/dividend deduplication rules
- [ ] Conflict resolution (different providers report different ratios)
- [ ] Schema for standardized corporate actions
- [ ] API endpoints

**Document to Create:**
- `docs/Standardization/CORPORATE_ACTIONS_AGGREGATION.md`

**Estimated Effort:** 1-2 hours

---

### 7. Monitoring & Observability
**Priority:** LOW (can add incrementally)

**What to Document:**
- [ ] Key metrics to track:
  - Data quality (% fields resolved)
  - Provider availability (uptime per provider)
  - Standardization latency
  - Cache hit rates
- [ ] Alerting rules:
  - Stale data (no updates in N hours)
  - Missing providers (< 2 providers available)
  - Anomaly spikes (unusual outlier counts)
- [ ] Dashboard design (Grafana/Datadog)
- [ ] Runbooks for common issues

**Document to Create:**
- `docs/MONITORING_STANDARDIZATION.md`

**Estimated Effort:** 1 hour

---

## 📋 Priority Order for Documentation

### IMMEDIATE (Next 1-2 hours)
1. **API Endpoint Specifications** (HIGH - blocks implementation)
   - `/stocks/standardized/{ticker}` contract
   - Response schemas
   - Query parameters

### SHORT-TERM (Next 1-2 days)
2. **News Aggregation Strategy** (HIGH - user mentioned as next feature)
   - Deduplication algorithm
   - `aggregate_union` strategy
   - News schema

3. **Background Jobs** (MEDIUM - improves performance)
   - Job specification
   - Monitoring metrics
   - Freshness requirements

### MEDIUM-TERM (Next 1-2 weeks)
4. **Frontend Integration** (MEDIUM - after API is working)
   - UI components
   - State management
   - User interactions

### LONG-TERM (Future sprints)
5. **Price Timeseries Strategy** (LOW - nice-to-have)
6. **Corporate Actions Aggregation** (LOW - nice-to-have)
7. **Monitoring & Observability** (LOW - incremental)

---

## 🎯 Recommendation for Next Steps

### Option A: Document API First (Recommended)
**Rationale:** Unblocks implementation, frontend can start integrating
1. Write `docs/API_STANDARDIZATION_ENDPOINTS.md` (1-2 hours)
2. Implement `/stocks/standardized/{ticker}` endpoint (2-3 hours)
3. Test with frontend (1 hour)
4. Then document news aggregation

**Timeline:** 4-6 hours to production-ready API

### Option B: Document Everything First
**Rationale:** Complete planning before any code
1. Write all 7 documentation items (8-12 hours)
2. Review with team
3. Then start implementation

**Timeline:** 8-12 hours documentation + implementation

### Option C: Incremental Documentation
**Rationale:** Document as we implement
1. Write API endpoint spec (1 hour)
2. Implement API endpoint (2 hours)
3. Write news aggregation strategy (2 hours)
4. Implement news aggregation (3-4 hours)
5. Continue incrementally

**Timeline:** Spreads work over multiple sprints

---

## ✅ User's Stated Requirements

From conversation:
> "This philosophy of ingest and standardization will be applied to other data that we will be ingesting in the future, like News. Where we will be consolidating the news article/link data from multiple sources create a set (remove duplicates) and create a similar source of truth."

**Key Points:**
1. ✅ Same ingest + standardization pattern
2. ✅ Apply to news articles next
3. ✅ Consolidate from multiple sources
4. ✅ Remove duplicates (create set)
5. ✅ Create single source of truth
6. ✅ **Difference:** News is aggregated (union), not selected (single_value)

**Implication:**
- News requires NEW strategy: `aggregate_union`
- News requires deduplication algorithm
- News requires different storage pattern (many articles per ticker)

---

## 💡 Key Insights

### What We Have
- ✅ Solid foundation: Ingest + Standardization documented and tested
- ✅ Clear philosophy: "No Synthetic Data" principle
- ✅ Working implementation: StandardizationEngine with single_value strategy
- ✅ Test coverage: Golden fixtures and end-to-end tests

### What We Need
- 📝 API endpoint specification (HIGH priority)
- 📝 News aggregation strategy (HIGH priority - user's next feature)
- 📝 Background job specification (MEDIUM priority - performance)
- 📝 Frontend integration patterns (MEDIUM priority - UX)

### What Can Wait
- ⏸️ Price timeseries strategy (LOW priority - future feature)
- ⏸️ Corporate actions aggregation (LOW priority - future feature)
- ⏸️ Monitoring & observability (LOW priority - incremental)

---

## 🚀 Recommended Next Action

**Immediate:** Document API endpoint specification

Create `docs/API_STANDARDIZATION_ENDPOINTS.md` with:
1. Endpoint contract: `GET /stocks/standardized/{ticker}`
2. Response schema (Pydantic models)
3. Query parameters
4. Error handling
5. Performance expectations

**After that:** Ask user to choose:
- **Path A:** Implement API endpoint first (get data flowing to frontend)
- **Path B:** Document news aggregation strategy first (plan next feature)
- **Path C:** Do both in parallel (split work)

---

**Document Owner:** Engineering Team  
**Next Review:** After completing immediate priority items
