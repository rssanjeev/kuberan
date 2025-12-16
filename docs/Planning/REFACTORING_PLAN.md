# Kuberan Codebase Refactoring Plan

**Created:** December 13, 2025  
**Status:** 🚧 In Progress  
**Goal:** Enforce 300-line limit across all Python files

---

## Executive Summary

**Current State:**
- 44 files exceed 300-line limit (out of ~150 Python files)
- Largest violator: `routers/etf.py` (4,506 lines, 15x over limit)
- Total excess lines: ~27,000 lines in oversized files

**Target State:**
- All Python files under 300 lines (excluding blanks/comments/imports)
- Modular architecture with clear separation of concerns
- Improved maintainability and AI/Copilot efficiency

**Strategy:**
- **Phase 1 (Completed):** Stocks router refactored (837 → 906 lines across 4 modules) ✅
- **Phase 2 (Completed):** Precious metals removal (-1,214 lines) ✅
- **Phase 3 (This Document):** Systematic refactoring of remaining violations
- **Incremental Approach:** Tackle largest files first, test after each change

---

## Files Exceeding 300-Line Limit (44 files)

### Critical Priority (1,000+ lines, must split)

| File | Lines | Ratio | Priority | Proposed Structure |
|------|-------|-------|----------|-------------------|
| `routers/etf.py` | 4,506 | 15.0x | 🔴 **P0** | Split into 8-10 modules by endpoint group |
| `services/etf/etf_analytics_service.py` | 1,430 | 4.8x | 🔴 **P0** | Split into 5 focused analytics modules |
| `services/providers/implementations/massive_provider.py` | 1,308 | 4.4x | 🔴 **P0** | Split by API category (reference, market, news) |
| `services/analytics_service.py` | 1,166 | 3.9x | 🔴 **P0** | Split into 4 modules (spending, trends, outliers, viz) |
| `models/provider.py` | 1,027 | 3.4x | 🟡 **P1** | Split by model type (stock, forex, etf, monitoring) |

### High Priority (750-999 lines)

| File | Lines | Ratio | Priority | Proposed Structure |
|------|-------|-------|----------|-------------------|
| `services/providers/implementations/alpha_vantage_provider.py` | 950 | 3.2x | 🟡 **P1** | Split by data type (fundamentals, technicals, news) |
| `routers/system.py` | 940 | 3.1x | 🟡 **P1** | Split into 4 modules (metadata, providers, jobs, health) |
| `services/etf/etf_backtesting_service.py` | 907 | 3.0x | 🟡 **P1** | Split into 3 modules (monte_carlo, scenarios, analysis) |
| `services/etf/etf_dividend_service.py` | 906 | 3.0x | 🟡 **P1** | Split into 3 modules (history, projections, calendar) |
| `services/etf/etf_portfolio_service.py` | 854 | 2.8x | 🟡 **P1** | Split into 3 modules (creation, analysis, rebalancing) |
| `services/jobs/metadata_collector.py` | 845 | 2.8x | 🟡 **P1** | Split into 3 modules (collection, validation, storage) |
| `services/etf/etf_tax_service.py` | 809 | 2.7x | 🟡 **P1** | Split into 3 modules (loss_harvest, gains, alternatives) |
| `services/etf/etf_data_service.py` | 760 | 2.5x | 🟡 **P1** | Split into 3 modules (cache, fetch, validation) |

### Medium Priority (500-749 lines)

| File | Lines | Ratio | Priority | Proposed Structure |
|------|-------|-------|----------|-------------------|
| `services/etf/etf_risk_service.py` | 707 | 2.4x | 🟢 **P2** | Split into 3 modules |
| `repositories/financial_repository.py` | 685 | 2.3x | 🟢 **P2** | Split by domain (transactions, merchants, documents) |
| `routers/financier.py` | 638 | 2.1x | 🟢 **P2** | Split into 3 modules (upload, transactions, analytics) |
| `services/stock/metadata_enrichment_service.py` | 633 | 2.1x | 🟢 **P2** | Split into 3 modules |
| `services/etf/etf_theme_service.py` | 592 | 2.0x | 🟢 **P2** | Split into 2 modules |
| `services/etf/etf_performance_service.py` | 586 | 2.0x | 🟢 **P2** | Split into 2 modules |
| `repositories/provider_repository.py` | 561 | 1.9x | 🟢 **P2** | Split by data type (prices, fundamentals, news) |
| `services/providers/implementations/yfinance_provider.py` | 560 | 1.9x | 🟢 **P2** | Split into 2 modules (prices, fundamentals) |
| `services/providers/provider_manager.py` | 558 | 1.9x | 🟢 **P2** | Split into 2 modules (manager, fallback) |
| `services/etf/etf_investor_service.py` | 556 | 1.9x | 🟢 **P2** | Split into 2 modules |
| `core/chase_parser.py` | 548 | 1.8x | 🟢 **P2** | Split into 2 modules (parser, validator) |
| `services/providers/implementations/finnhub_provider.py` | 521 | 1.7x | 🟢 **P2** | Split into 2 modules |
| `services/etf/etf_screening_service.py` | 521 | 1.7x | 🟢 **P2** | Split into 2 modules |
| `scripts/extract_financials_sp500.py` | 500 | 1.7x | 🟢 **P2** | OK as script (one-time use) |

### Low Priority (300-499 lines)

| File | Lines | Ratio | Priority | Notes |
|------|-------|-------|----------|-------|
| `services/etf/etf_tco_service.py` | 473 | 1.6x | 🔵 **P3** | Minor refactor needed |
| `services/jobs/massive_ticker_discovery.py` | 450 | 1.5x | 🔵 **P3** | Job script, defer |
| `services/providers/base_provider.py` | 435 | 1.5x | 🔵 **P3** | Base class, keep cohesive |
| `services/etf/etf_profile_service.py` | 429 | 1.4x | 🔵 **P3** | Minor refactor |
| `routers/monitoring.py` | 422 | 1.4x | 🔵 **P3** | Split into 2 modules |
| `scripts/backfill_phase3_ticker_details.py` | 405 | 1.4x | 🔵 **P3** | OK as script |
| `services/providers/load_balancer.py` | 401 | 1.3x | 🔵 **P3** | Minor refactor |
| `services/etf/etf_comparison_service.py` | 399 | 1.3x | 🔵 **P3** | Minor refactor |
| `services/jobs/massive_delta_extractor.py` | 385 | 1.3x | 🔵 **P3** | Job script, defer |
| `services/providers/provider_config.py` | 384 | 1.3x | 🔵 **P3** | Config file, keep cohesive |
| `core/api_metrics.py` | 382 | 1.3x | 🔵 **P3** | Minor refactor |
| `services/jobs/related_tickers_collector.py` | 381 | 1.3x | 🔵 **P3** | Job script, defer |
| `services/manual_entries_service.py` | 380 | 1.3x | 🔵 **P3** | Minor refactor |
| `core/checking_account_parser.py` | 380 | 1.3x | 🔵 **P3** | Minor refactor |
| `services/jobs/historical_data_backfill.py` | 377 | 1.3x | 🔵 **P3** | Job script, defer |
| `services/jobs/massive_deactivation_detector.py` | 373 | 1.2x | 🔵 **P3** | Job script, defer |
| `repositories/etf_repository.py` | 372 | 1.2x | 🔵 **P3** | Minor refactor |
| `services/jobs/massive_foundation_builder.py` | 368 | 1.2x | 🔵 **P3** | Job script, defer |
| `services/providers/provider_registry.py` | 354 | 1.2x | 🔵 **P3** | Minor refactor |
| `services/providers/adaptive_rate_limiter.py` | 347 | 1.2x | 🔵 **P3** | Minor refactor |
| `scripts/configure_timeseries_ttl.py` | 345 | 1.2x | 🔵 **P3** | OK as script |
| `services/scheduler/registry.py` | 306 | 1.0x | 🔵 **P3** | Borderline, monitor |

---

## Refactoring Strategy

### Principles

1. **Incremental Approach:** Refactor one file at a time, test after each change
2. **Logical Grouping:** Split by functionality, not arbitrary line counts
3. **Preserve Imports:** Maintain existing import paths where possible (use `__init__.py`)
4. **Test Coverage:** Verify endpoints/functionality after each refactor
5. **Documentation:** Update inline comments, docstrings remain with functions

### Patterns

#### Pattern 1: Router Splitting (e.g., etf.py → etf/)
```
routers/etf.py (4,506 lines)
↓
routers/etf/
├── __init__.py (main router aggregator)
├── etf_profile.py (profile, holdings, sectors)
├── etf_discovery.py (search, similar, comparables)
├── etf_comparison.py (compare, exposure)
├── etf_portfolio.py (create, analyze, rebalance)
├── etf_performance.py (performance, risk, correlation)
├── etf_tax.py (TCO, tax loss harvest, gains)
├── etf_analytics.py (backtesting, monte carlo, stress test)
├── etf_dividends.py (dividends, projections, calendar)
├── etf_trends.py (sector rotation, themes, investors)
└── etf_screening.py (screening endpoints)
```

#### Pattern 2: Service Splitting (e.g., analytics_service.py → analytics/)
```
services/analytics_service.py (1,166 lines)
↓
services/analytics/
├── __init__.py (exports all functions)
├── spending_analysis.py (category breakdown, totals)
├── trend_analysis.py (linear regression, predictions)
├── outlier_detection.py (z-score, anomaly detection)
└── visualization.py (chart generation, base64 encoding)
```

#### Pattern 3: Provider Splitting (e.g., massive_provider.py → massive/)
```
services/providers/implementations/massive_provider.py (1,308 lines)
↓
services/providers/implementations/massive/
├── __init__.py (MassiveProvider class)
├── reference_api.py (tickers, types, exchanges)
├── market_data.py (quotes, prices, splits, dividends)
└── news_api.py (news articles, sentiment)
```

#### Pattern 4: Model Splitting (e.g., provider.py → provider/)
```
models/provider.py (1,027 lines)
↓
models/provider/
├── __init__.py (exports all models)
├── enums.py (DataSource, IndicatorType, etc.)
├── stock_models.py (StockQuote, StockHistoricalPrice, etc.)
├── forex_crypto_models.py (ForexRate, CryptoPrice, etc.)
├── etf_models.py (ETFProfile, ETFHolding, etc.)
└── monitoring_models.py (already in monitoring.py)
```

---

## Implementation Phases

### ✅ Phase 1: Stocks Router (COMPLETE)
- **File:** `routers/stocks.py` (837 lines)
- **Result:** 4 modules (max 242 lines each)
- **Status:** ✅ Completed Dec 13, 2025

### ✅ Phase 2: Precious Metals Removal (COMPLETE)
- **Files:** 6 files removed
- **Impact:** -1,214 lines
- **Status:** ✅ Completed Dec 13, 2025

### 🚧 Phase 3: ETF Router (NEXT)
- **File:** `routers/etf.py` (4,506 lines, 15x over limit)
- **Target:** 10 modules (~450 lines each)
- **Effort:** 4-6 hours
- **Priority:** 🔴 **P0** - Largest violator

**Proposed ETF Router Structure:**
```python
# routers/etf/__init__.py
from fastapi import APIRouter
router = APIRouter(prefix="/etf", tags=["ETF"])

from .etf_profile import router as profile_router
from .etf_discovery import router as discovery_router
# ... 8 more sub-routers

router.include_router(profile_router)
router.include_router(discovery_router)
# ... include all sub-routers
```

**10 Sub-Modules:**
1. `etf_profile.py` (~450 lines): Profile, holdings, sectors, geographic
2. `etf_discovery.py` (~450 lines): Search, similar, comparables, exposure
3. `etf_comparison.py` (~400 lines): Compare, holdings overlap, portfolio compare
4. `etf_portfolio.py` (~450 lines): Create, analyze, rebalance, risk assessment
5. `etf_performance.py` (~450 lines): Performance, correlation matrix, benchmarks
6. `etf_tax.py` (~450 lines): TCO, tax loss harvest, capital gains, alternatives
7. `etf_analytics.py` (~500 lines): Backtesting, monte carlo, stress test, scenario
8. `etf_dividends.py` (~450 lines): Dividends, projections, calendar, growth
9. `etf_trends.py` (~450 lines): Sector rotation, themes, investor activity
10. `etf_screening.py` (~400 lines): Advanced screening, filters

**Testing Checklist:**
- [ ] All 67 ETF endpoints functional
- [ ] Services properly imported
- [ ] No circular dependencies
- [ ] Backend starts without errors
- [ ] Alpha Vantage API calls work

### 🔜 Phase 4: Analytics Service
- **File:** `services/analytics_service.py` (1,166 lines)
- **Target:** 4 modules (~290 lines each)
- **Effort:** 2-3 hours
- **Priority:** 🔴 **P0**

**Modules:**
1. `spending_analysis.py`: Category breakdowns, monthly totals
2. `trend_analysis.py`: Linear regression, predictions
3. `outlier_detection.py`: Z-score analysis, anomaly detection
4. `visualization.py`: Chart generation, base64 encoding

### 🔜 Phase 5: MASSIVE Provider
- **File:** `services/providers/implementations/massive_provider.py` (1,308 lines)
- **Target:** 3 modules (~430 lines each)
- **Effort:** 2-3 hours
- **Priority:** 🔴 **P0**

**Modules:**
1. `reference_api.py`: All Tickers, Ticker Overview, Ticker Types, Exchanges
2. `market_data.py`: Quotes, historical prices, splits, dividends
3. `news_api.py`: News articles with sentiment analysis

### 🔜 Phase 6: ETF Analytics Service
- **File:** `services/etf/etf_analytics_service.py` (1,430 lines)
- **Target:** 5 modules (~285 lines each)
- **Effort:** 3-4 hours
- **Priority:** 🔴 **P0**

### 🔜 Phase 7: Provider Models
- **File:** `models/provider.py` (1,027 lines)
- **Target:** 4 modules (~255 lines each)
- **Effort:** 2 hours
- **Priority:** 🟡 **P1**

### 🔜 Phase 8: Remaining P0/P1 Files
- System router, AlphaVantage provider, remaining ETF services
- **Effort:** 8-10 hours
- **Priority:** 🟡 **P1**

### 🔜 Phase 9: P2 Files (500-749 lines)
- Financial repository, financier router, remaining providers
- **Effort:** 6-8 hours
- **Priority:** 🟢 **P2**

### 🔜 Phase 10: P3 Files (300-499 lines)
- Low-priority refactors, minor cleanups
- **Effort:** 4-6 hours
- **Priority:** 🔵 **P3**

---

## Timeline Estimate

| Phase | Files | Effort | Completion Target |
|-------|-------|--------|------------------|
| Phase 1 (✅ Complete) | 1 file | 2h | Dec 13, 2025 |
| Phase 2 (✅ Complete) | 6 files | 1h | Dec 13, 2025 |
| Phase 3 (Next) | 1 file | 6h | Dec 14, 2025 |
| Phase 4-7 | 4 files | 10h | Dec 15-16, 2025 |
| Phase 8 | 8 files | 10h | Dec 17-18, 2025 |
| Phase 9 | 13 files | 8h | Dec 19-20, 2025 |
| Phase 10 | 16 files | 6h | Dec 21-22, 2025 |
| **Total** | **44 files** | **43h** | **Dec 22, 2025** |

**Realistic Estimate:** 2-3 weeks working 2-3 hours/day

---

## Benefits of Refactoring

### 1. **Maintainability**
- ✅ Entire file visible in single screen (no scrolling)
- ✅ Clear file purpose (one responsibility per module)
- ✅ Easy to locate specific functionality

### 2. **AI/Copilot Efficiency**
- ✅ Faster context loading (smaller files)
- ✅ Better code suggestions (focused context)
- ✅ Reduced risk of accidental breaking changes

### 3. **Testing**
- ✅ Easier to write focused unit tests
- ✅ Better test coverage per module
- ✅ Faster test execution (test specific modules)

### 4. **Collaboration**
- ✅ Reduced merge conflicts (smaller files)
- ✅ Easier code reviews (reviewable in one session)
- ✅ Clear ownership per module

### 5. **Performance**
- ✅ Faster imports (only load what's needed)
- ✅ Better code splitting for future optimizations
- ✅ Easier to identify performance bottlenecks

---

## Rules & Guidelines

### DO ✅
- Keep modules under 300 lines (actual code, exclude blanks/comments/imports)
- Use descriptive file names indicating purpose
- Maintain existing import paths via `__init__.py`
- Test after each refactor
- Update documentation inline
- Commit incrementally

### DON'T ❌
- Create arbitrary splits (split by logical functionality)
- Break circular dependencies by copying code
- Remove docstrings or comments
- Skip testing
- Batch multiple refactors in one commit
- Delay refactoring (do it now while fresh in mind)

---

## Progress Tracking

### Completed (2/44 files, 4.5%)
- ✅ `routers/stocks.py` → `routers/stocks/` (4 modules)
- ✅ Precious metals removal (6 files deleted)

### In Progress (0/44 files)
- None

### Remaining (42/44 files, 95.5%)
- 🔴 **5 Critical files** (1,000+ lines each)
- 🟡 **8 High priority files** (750-999 lines)
- 🟢 **13 Medium priority files** (500-749 lines)
- 🔵 **16 Low priority files** (300-499 lines)

---

## Next Actions

1. **Immediate:** Refactor `routers/etf.py` (4,506 → 10 modules)
2. **This Week:** Complete Phases 3-4 (etf router + analytics service)
3. **Next Week:** Phases 5-7 (providers + models)
4. **Following Week:** Phases 8-10 (cleanup remaining files)

---

**Last Updated:** December 13, 2025  
**Responsible:** Sanjeev  
**Status:** 🚧 Phase 3 Starting (ETF Router Refactor)
