# Financial Statements Archival Plan

**Last Updated:** December 5, 2025  
**Deadline:** February 23, 2026 (79 days remaining)  
**Status:** Scripts Ready - Execution Pending

---

## Overview

⚠️ **URGENT**: MASSIVE API financials endpoint will be deprecated on February 23, 2026.

This plan archives 12 financial statements per ticker (4 annual + 8 quarterly) for:
1. **S&P 500 Priority**: 500 largest companies (~20 hours)
2. **Full Dataset**: All 12,140 tickers (~60 days)

---

## Archival Parameters (Finalized)

### Statements Per Ticker: 12 Total
- **4 Annual Statements**: 10-K filings (4 years of history)
- **8 Quarterly Statements**: 10-Q filings (2 years of history)
- **Coverage**: 4+ years of comprehensive financial data
- **Rationale**: Industry-standard depth for analysis

### Sort Strategy
- **Primary**: Market cap DESCENDING (largest companies first)
- **Secondary**: Ticker alphabetically (for nulls/equal market caps)
- **MongoDB Query**:
  ```python
  CompanyOverview.find().sort([
      ("market_cap", -1),  # Largest first: AAPL → MSFT → NVDA
      ("ticker", 1)         # Alphabetical for nulls
  ])
  ```

### Rate Limiting
- **MASSIVE API Limits**: 5 calls/min, 300/hour, 7,200/day
- **Script Configuration**: 12 seconds between tickers
- **Effective Rate**: ~10 tickers/minute with buffer

---

## Phase 1: S&P 500 Priority Archival

### Target
- **Tickers**: 500 (top 500 by market cap)
- **Statements**: 6,000 total (500 × 12)
- **Runtime**: ~20 hours
- **Timeline**:
  - **Start**: December 6, 2025 (tomorrow)
  - **Complete**: December 7, 2025

### Script
- **File**: `backend/app/scripts/backfill_sp500_financials.py`
- **Status**: ✅ Created and ready to execute

### Execution
```bash
# Start S&P 500 archival
docker exec -it kuberan-backend python3 -m app.scripts.backfill_sp500_financials

# Monitor progress (real-time)
docker logs -f kuberan-backend | grep "Progress"

# View checkpoint
cat backend/app/scripts/sp500_checkpoint.json

# Check failed tickers
cat backend/app/scripts/sp500_failed_tickers.json
```

### Features
- **Progress Tracking**: Log every 50 tickers
- **Checkpoint System**: Resume capability every 10 tickers
- **JSON Export**: One file per ticker in `data/financial_statements_archive/sp500/`
- **Error Handling**: Continue on failure, log to separate file
- **MongoDB Storage**: 5-year TTL on documents

---

## Phase 2: Full Dataset Archival (Market Cap Priority)

### Target
- **Tickers**: 12,140 (all active tickers)
- **Statements**: 145,680 total (12,140 × 12)
- **Runtime**: ~60 days
- **Timeline**:
  - **Start**: January 1, 2026
  - **Complete**: February 15, 2026 (8-day buffer before deletion)

### Script
- **File**: `backend/app/scripts/backfill_all_financials.py`
- **Status**: ✅ Created and ready to execute

### Sort Order (Market Cap Descending)
```
AAPL ($2.8T) → MSFT ($2.7T) → NVDA ($2.5T) → ... → smallest
```

**Why?** Risk mitigation - archive most important companies first.

### Execution
```bash
# Start full dataset archival
docker exec -it kuberan-backend python3 -m app.scripts.backfill_all_financials

# Monitor progress (runs in background for 60 days)
docker logs -f kuberan-backend | grep "Progress"

# View checkpoint (updated every 10 tickers)
cat backend/app/scripts/full_dataset_checkpoint.json

# Check progress percentage
cat backend/app/scripts/full_dataset_checkpoint.json | grep progress_percentage
```

### Features
- **Progress Tracking**: Log every 100 tickers with milestone markers
- **Checkpoint System**: Resume capability every 10 tickers
- **Batch JSON Export**: One file per 100 tickers in `data/financial_statements_archive/full_dataset/`
- **Error Handling**: Continue on failure, comprehensive error log
- **MongoDB Storage**: 5-year TTL on documents

### Progress Milestones
| Days | Tickers | Coverage | Milestone |
|------|---------|----------|-----------|
| 7 | ~500 | Top 80% market cap | ✅ Mega-cap complete |
| 14 | ~1,500 | S&P 1500 equivalent | ✅ Large-cap complete |
| 30 | ~5,000 | Mid-cap coverage | ✅ Mid-cap complete |
| 60 | 12,140 | 100% complete | ✅ All tickers archived |

---

## Data Storage

### MongoDB
- **Collection**: `financial_statements`
- **TTL**: 5 years (expires February 23, 2031)
- **Indexes**: ticker, fiscal_year, fiscal_quarter
- **Total Size**: ~12-18 GB estimated

### JSON Backups
- **S&P 500**: `data/financial_statements_archive/sp500/`
  - Format: `{ticker}_{YYYYMMDD}.json`
  - Count: 500 files
  
- **Full Dataset**: `data/financial_statements_archive/full_dataset/`
  - Format: `batch_{NNNN}_{YYYYMMDD_HHMMSS}.json`
  - Count: ~122 batch files (12,140 ÷ 100)
  - Each batch: 100 tickers with statements

---

## Monitoring & Resume

### Real-Time Monitoring
```bash
# Watch progress updates
docker logs -f kuberan-backend | grep "📈 Progress"

# Check current ticker being processed
docker logs kuberan-backend --tail 10 | grep "Processing"

# View statements saved count
docker logs kuberan-backend | grep "statements_saved"
```

### Resume After Interruption
Both scripts automatically resume from last checkpoint:

1. **Checkpoint files** saved every 10 tickers:
   - S&P 500: `backend/app/scripts/sp500_checkpoint.json`
   - Full dataset: `backend/app/scripts/full_dataset_checkpoint.json`

2. **On restart**, script:
   - Loads checkpoint file
   - Resumes from `last_ticker`
   - Continues with remaining tickers

3. **No data loss**: MongoDB saves are atomic per statement

### Failed Tickers
```bash
# View failed tickers (if any)
cat backend/app/scripts/sp500_failed_tickers.json
cat backend/app/scripts/full_dataset_failed_tickers.json

# Retry failed tickers (manual)
# 1. Extract ticker list from failed file
# 2. Modify script to target specific tickers
# 3. Re-run script
```

---

## Timeline Summary

| Date | Milestone | Status |
|------|-----------|--------|
| Dec 5, 2025 | Scripts created | ✅ Complete |
| Dec 6, 2025 | Start S&P 500 archival | ⏳ Pending |
| Dec 7, 2025 | S&P 500 complete (6,000 statements) | ⏳ Pending |
| Jan 1, 2026 | Start full dataset archival | ⏳ Pending |
| Feb 15, 2026 | Full dataset complete (145,680 statements) | ⏳ Pending |
| Feb 23, 2026 | ⚠️ MASSIVE API removes endpoint | - |

**Buffer**: 8 days between completion and deletion

---

## Risk Mitigation

### Why S&P 500 First?
- **Top 500 companies = 80% of market cap**
- **If full archival fails**, most important data is safe
- **Quick win**: Complete in 20 hours (1 day)

### Why Market Cap Descending?
- **Progressive risk reduction**: Archive largest companies first
- **Milestone tracking**: Clear checkpoints (Day 7 = top 80%)
- **Failure recovery**: Most valuable data archived early
- **Prioritization**: Mega → Large → Mid → Small caps

### Checkpoint System
- **Every 10 tickers**: Save progress to disk
- **Resume capability**: Restart from last checkpoint on failure
- **No duplicate work**: Skip already-processed tickers

---

## Post-Archival Actions

### Data Verification
```bash
# Check MongoDB document count
docker exec -it kuberan-mongodb mongosh kuberan --eval \
  "db.financial_statements.countDocuments({})"

# Expected: ~145,680 documents (12,140 tickers × 12 statements)

# Check JSON backup count
ls -1 data/financial_statements_archive/sp500/ | wc -l  # Expected: 500
ls -1 data/financial_statements_archive/full_dataset/ | wc -l  # Expected: ~122
```

### Migration to Alpha Vantage
After February 23, 2026, migrate to Alpha Vantage for ongoing financial statements:
- **Endpoint**: `/v3/financials` (Alpha Vantage)
- **Coverage**: New statements only (post-archival)
- **Integration**: Update `massive_provider.py` to use Alpha Vantage

---

## Success Criteria

- ✅ **S&P 500**: 500 tickers × 12 statements = 6,000 statements
- ✅ **Full Dataset**: 12,140 tickers × 12 statements = 145,680 statements
- ✅ **Large-Cap Priority**: AAPL, MSFT, NVDA archived in first week
- ✅ **JSON Backups**: All statements exported to `data/` directory
- ✅ **MongoDB TTL**: 5-year retention configured
- ✅ **Completion**: February 15, 2026 (before deletion deadline)

---

## Commands Quick Reference

```bash
# S&P 500 Archival (Dec 6)
docker exec -it kuberan-backend python3 -m app.scripts.backfill_sp500_financials

# Full Dataset Archival (Jan 1)
docker exec -it kuberan-backend python3 -m app.scripts.backfill_all_financials

# Monitor Progress
docker logs -f kuberan-backend | grep "Progress"

# Check Checkpoint
cat backend/app/scripts/sp500_checkpoint.json
cat backend/app/scripts/full_dataset_checkpoint.json

# Verify MongoDB Count
docker exec -it kuberan-mongodb mongosh kuberan --eval \
  "db.financial_statements.countDocuments({})"
```

---

**Next Actions:**
1. ✅ Scripts created (Complete)
2. ⏳ Execute S&P 500 archival (Dec 6, 2025)
3. ⏳ Execute full dataset archival (Jan 1, 2026)
4. ⏳ Verify data integrity (Feb 15, 2026)
5. ⏳ Migrate to Alpha Vantage (Feb 23+, 2026)
