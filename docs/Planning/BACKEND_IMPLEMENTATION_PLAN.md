# Backend Implementation Plan

**Last Updated:** December 16, 2025  
**Status:** ⏳ Temporary  
**Purpose:** Authoritative backend execution plan covering extraction → ingestion → standardization → storage schedules and tasks  
**Related Docs:**
- [KUBERAN_OVERVIEW.md](../KUBERAN_OVERVIEW.md)
- [DATA_PIPELINE_ARCHITECTURE.md](../DATA_PIPELINE_ARCHITECTURE.md)
- [Standardization/DATA_STANDARDIZATION_RULES.md](../Standardization/DATA_STANDARDIZATION_RULES.md)
- [Standardization/DATA_PRIORITY_MATRIX.md](../Standardization/DATA_PRIORITY_MATRIX.md)
- [API.md](../API.md)
- [MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md](../MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md)
- [WORKFLOWS.md](../../.github/docs/WORKFLOWS.md)

---

## 1. Scope & Intent
- Apply "option three" architecture end-to-end without rewriting healthy code; extend/reuse existing modules in `backend/app/core`, `services`, `repositories`, and `jobs`.
- Focus exclusively on backend data flow (providers → snapshots → matrix-driven standardization → analytics-ready storage) while deferring frontend/UI work.
- Treat this document as the single source of truth for schedules, job ownership, and sequencing before any new code is written.

## 2. Guiding Principles
- **Security First:** Follow [SECURITY.md](../../.github/docs/SECURITY.md) for any financial data (no PDFs stored, SHA256 hashes for dedupe, discrete transactions only).
- **No Synthetic Data:** Standardization must select existing provider values per `DATA_PRIORITY_MATRIX.md` (weights = priority, not coefficients).
- **300-Line Rule:** Split modules as needed; prefer composition over monolith changes.
- **Structured Logging:** Every job uses `get_logger(__name__)` with context per [LOGGING.md](../../.github/docs/LOGGING.md).
- **Async-First:** All provider calls and repository writes remain async; background jobs coordinate via APScheduler.
- **Documentation Parity:** Any change triggered by this plan updates the relevant doc + Postman collection simultaneously.

## 3. End-to-End Flow Summary
1. **Data Extraction:** Provider clients (YFinance, MASSIVE, Finviz, StockAnalysis, Alpha Vantage, etc.) fetch raw payloads at scheduled cadences.
2. **Data Ingestion:** Snapshots persist untouched into provider-specific collections (`*_snapshots`) with indexes defined in `backend/app/models/provider.py`.
3. **Standardization:** `StandardizationEngine` applies the matrix, producing canonical ticker views plus domain-specific aggregates.
4. **Storage & Analytics:** Results land in purpose-built collections (standardized views, Mongo timeseries w/ TTL, permanent corporate-action collections) ready for downstream analytics and API exposure.

## 4. Phase Roadmap
| Phase | Focus | Deliverables | Dependencies |
| --- | --- | --- | --- |
| Phase 0 | Alignment | Review this plan, update PLANNING_CHECKLIST | None |
| Phase 1 | Extraction | Confirm provider clients + job schedules | Existing provider code, rate limit docs |
| Phase 2 | Ingestion | Snapshot schema audits, index verifications, storage tuning | Phase 1 |
| Phase 3 | Standardization | Matrix validation, job wiring, `/stocks/standardized/{ticker}` design | Phase 2 |
| Phase 4 | Storage Optimization | TTL config, archive strategy, monitoring dashboards | Phase 3 |
| Phase 5 | Verification | End-to-end dry runs, metrics, documentation updates | Phases 1-4 |

## 5. Stage Plans & Schedules

### 5.1 Data Extraction
**Objective:** Fetch freshest data from all providers without breaching rate limits.

| Provider & Domain | Existing Module(s) | Extraction Job | Schedule (US/Eastern) | Notes |
| --- | --- | --- | --- | --- |
| YFinance (prices, fundamentals) | `services/providers/implementations/yfinance_provider.py` | `jobs/stock/yfinance_price_job.py` (existing) | **Every 60 seconds** during market hours (09:00-17:00) | Respect retry/backoff; gate by `market_calendar.py`. |
| MASSIVE (metadata foundation) | `services/providers/implementations/massive_provider.py` | `jobs/massive_foundation_builder.py` | **Every minute** (24/7) limited to 5 tickers/run | Enforces 5 calls/min; logs enrichment progress. |
| Finviz (sentiment, snapshot) | `core/finviz_fetcher` (needs refactor) | New `finviz_snapshot_job` | **Every 15 minutes** during market hours | Use MCP per [WEB_SCRAPING.md](../../.github/docs/WEB_SCRAPING.md). |
| StockAnalysis (financials) | `core/stockanalysis_fetcher` | `financials_extraction_job.py` (existing) | **Every 3 minutes** (already scheduled) | Continues batch-of-10 tickers plan. |
| Alpha Vantage (ETF) | `services/providers/implementations/alpha_vantage_provider.py` | `jobs/etf/alpha_vantage_refresh_job.py` | **Every 30 minutes** (24/7, cached 30 days) | Ensure API key secrets via env. |
| Precious Metals (Brave search) | `core/precious_metals_fetcher.py` | `jobs/precious_metals/metal_price_job.py` | **Every 30 minutes** (24/7) | Already MCP-based; keep concurrency low. |

**Extraction Action Items**
1. Audit each provider client for current rate limit handling; capture open issues in `PLANNING_CHECKLIST.md`.
2. Document exact Cron expressions in `services/scheduler/registry.py` comments for traceability.
3. Ensure every job emits `{"provider": ..., "stage": "extraction"}` structured logs with success/error counters.
4. Backfill missing provider coverage (e.g., MASSIVE enrichment <100%) before enabling downstream automation.
5. Update `WORKFLOWS.md` if any job start/stop commands change.

### 5.2 Data Ingestion
**Objective:** Persist raw payloads exactly as received, keeping provenance and schema versions intact.

| Snapshot Collection | Source Stage | Persistence Mechanism | Schedule Linkage | Notes |
| --- | --- | --- | --- | --- |
| `yfinance_snapshots` | YFinance extraction job | Inline write via `provider_repository.save_snapshot` | Mirrors extraction cadence (every 60s) | Ensure `snapshot_version` and `fetched_at` populated. |
| `massive_snapshots` | MASSIVE builder job | Inline write | Every minute | Store enrichment status + 404 markers for failed tickers. |
| `finviz_snapshots` | Finviz snapshot job | Inline write through new repository helper | Every 15 minutes | Capture HTML parse metadata for audits. |
| `stockanalysis_snapshots` | Financials extraction job | Inline write | Every 3 minutes | Keep JSON backups path for 500-ticker pipeline. |
| `alpha_vantage_snapshots` | ETF refresh job | Inline write | Every 30 minutes | Honor 30-day cache to reduce churn. |
| `precious_metals_snapshots` | Metals price job | Inline write | Every 30 minutes | Tag with city/currency pair. |

**Ingestion Schedules & Controls**
- **Immediate Persistence:** Extraction jobs call ingestion helpers synchronously; cadence therefore equals extraction cadence (no extra cron).
- **Daily Snapshot Integrity Check:** Add lightweight APScheduler job (`snapshot_integrity_job`) running **daily at 02:00** EST to:
  - Verify latest snapshot age per provider.
  - Emit warning if staleness > 2× expected interval.
  - Optionally trigger manual re-fetch via existing services.
- **Weekly Schema Drift Audit:** Every **Sunday 06:00** EST run script (`scripts/compare_snapshot_schemas.py`) comparing live snapshots vs documented schemas (`docs/Ingest/*`); log differences for review.

**Ingestion Action Items**
1. Confirm all snapshot collections have `(ticker, as_of_date)` indexes (see `backend/app/models/provider.py`).
2. Implement `snapshot_integrity_job` using current scheduler registry conventions.
3. Define alert thresholds in `API_METRICS_TRACKING.md` for ingestion lag.
4. Ensure MCP-based scrapers redact sensitive info before persistence per [WEB_SCRAPING.md](../../.github/docs/WEB_SCRAPING.md).

### 5.3 Standardization
**Objective:** Transform snapshots into unified ticker views using the matrix described in `DATA_STANDARDIZATION_RULES.md` and `DATA_PRIORITY_MATRIX.md`.

| Component | Existing Asset | Planned Updates | Schedule |
| --- | --- | --- | --- |
| `StandardizationEngine` | `services/standardization_engine.py` | Confirm only `single_value` strategy enabled; prep hooks for `aggregate_union` / `timeseries_primary_with_checks`. | N/A (library) |
| Standardization Job | New `jobs/standardization/standardized_view_job.py` | Iterate active tickers, load latest snapshots, invoke engine, upsert into `standardized_ticker_views`. | **Every 5 minutes** during market hours; **every 30 minutes** off-hours for catch-up. |
| `/stocks/standardized/{ticker}` Endpoint | Router addition to `routers/stocks.py` | Thin handler reading from `standardized_ticker_views`, exposing metadata + source info. | On-demand API |
| Validation Tests | `tests/test_standardization_*.py` | Expand golden fixtures when new providers join. | Run via CI (per commit) |

**Standardization Workflow**
1. **Input Selection:** Job queries `ticker_config_repository` for enabled tickers; batches of 250 per run to stay under Mongo load.
2. **Snapshot Fetch:** Pull the most recent snapshot per provider; fail gracefully when provider stale, marking `providers_available` metadata.
3. **Matrix Application:** For each field defined in `config/data_priority_matrix.yaml`, apply `single_value`. Future strategies remain TODO until news/timeseries ready.
4. **Output Storage:** Upsert to `standardized_ticker_views` with `as_of`, `version`, and `data_points.{field}.source` recorded.
5. **Metrics:** Emit counts for `fields_resolved`, `fields_missing`, job duration, and snapshot latency.

**Standardization Action Items**
1. Register the new job with dual cron entries (market hours vs off-hours) inside `services/scheduler/registry.py`.
2. Update `DATA_PIPELINE_ARCHITECTURE.md` and `API.md` after endpoint contract is finalized.
3. Add structured logging for missing provider data to help prioritize ingestion fixes.
4. Provide a dry-run flag for safe staging validation before production rollout.

### 5.4 Storage & Maintenance
**Objective:** Keep data query-ready while optimizing cost via TTL, indexing, and retention policies.

| Collection Type | Examples | Retention / TTL | Maintenance Schedule |
| --- | --- | --- | --- |
| Mongo Timeseries (auto-expiring) | `stock_quotes`, `intraday_prices`, `crypto_prices`, `forex_rates`, `option_chains`, `market_indicators`, `technical_indicators`, `sentiment_analyses`, `commodity_prices`, `economic_indicators` | Configured via `scripts/configure_timeseries_ttl.py` (15 min ↔ 1 year depending on dataset) | Verify TTL weekly (Sunday 05:00) using script output; rerun script if mismatch. |
| Permanent Collections | `stock_dividends`, `stock_splits`, `stock_earnings`, `company_overviews`, `standardized_ticker_views`, `financial_statements` | No TTL | Monthly compact/defragment job (First Sunday 03:00) using Mongo `compact` for high-churn collections. |
| Snapshot Collections | `*_snapshots` | Rolling window (30-90 days). Manual purge job required. | `snapshot_cleanup_job` every **Saturday 04:00** deletes docs older than provider retention (YFinance 30d, MASSIVE 90d, ETF 60d, etc.). |

**Storage Action Items**
1. Run `scripts/configure_timeseries_ttl.py --verify` weekly and archive the report under `docs/planning/reports/` (create directory if absent).
2. Implement `snapshot_cleanup_job` with provider-specific retention constants in `config/data_priority_matrix.yaml` or dedicated config file.
3. Document compact/purge procedures inside [WORKFLOWS.md](../../.github/docs/WORKFLOWS.md).
4. Add Grafana/Datadog dashboards (per [API_METRICS_TRACKING.md](../API_METRICS_TRACKING.md)) for collection size, TTL effectiveness, and job health.

## 6. Implementation Checklist (Derive Issues/PRs)
1. **Finalize Schedules**
	- [ ] Encode cron expressions in `services/scheduler/registry.py` for every job above.
	- [ ] Record schedule summary table in `PLANNING_CHECKLIST.md` and keep in sync.
2. **Provider & Ingestion Hardening**
	- [ ] Rate-limit audit per provider.
	- [ ] Schema drift report automation.
	- [ ] Snapshot integrity + cleanup jobs implemented.
3. **Standardization Enhancements**
	- [ ] Build `standardized_view_job` with dual cadence.
	- [ ] Extend tests (new golden fixtures for AAPL, MSFT, NVDA, SPY).
	- [ ] Expose `/stocks/standardized/{ticker}` endpoint + Postman entry.
4. **Storage Optimization**
	- [ ] TTL verification workflow documented + automated.
	- [ ] Snapshot purge cadence running and logged.
	- [ ] Monthly compaction process scripted.
5. **Monitoring & Documentation**
	- [ ] Update `API_METRICS_TRACKING.md` with new KPIs (snapshot staleness, fields missing, TTL drift).
	- [ ] Ensure all jobs emit metrics consumed by `core/api_metrics.py`.
	- [ ] Refresh Postman collection + README references.

## 7. Risk Register & Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Provider rate-limit bans | Data lag across entire pipeline | Centralized rate limiter + staggered schedules; monitor via extraction logs. |
| Snapshot schema drift | Standardization failures | Weekly audit job + alerting; versioned snapshot schemas in docs. |
| Standardization backlog | API serves stale views | Dual-cadence job with queue depth metrics; provide on-demand trigger endpoint. |
| TTL misconfiguration | Storage bloat or premature deletion | Weekly verify script; automated alerts if doc count drops unexpectedly. |
| Documentation drift | Engineers implement outdated behavior | Mandatory doc updates per change; treat this plan as gate before PR merge. |

## 8. Next Steps
1. Share this plan for review; apply feedback before any coding.
2. Once approved, update `PLANNING_CHECKLIST.md` with task owners/dates.
3. Begin Phase 1 (Extraction) hardening, then proceed sequentially unless dependencies allow parallelism.

---

**Review Cadence:** Revisit this document after each phase; archive to `docs/archive/` once implementation completes and the new workflow becomes "business as usual."  
**Owner:** Backend engineering team (stock + financier + ETF sub-teams).