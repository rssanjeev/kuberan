# Provider Data Comparison Matrix

**Last Updated:** December 22, 2025  
**Status:** 🟢 Active  
**Purpose:** Compare data fields across all providers for standardization pipeline  
**Related Docs:**
- [DATA_PIPELINE_ARCHITECTURE.md](../DATA_PIPELINE_ARCHITECTURE.md)
- [config/data_priority_matrix.yaml](../../config/data_priority_matrix.yaml)
- [Standardization/DATA_STANDARDIZATION_RULES.md](../Standardization/DATA_STANDARDIZATION_RULES.md)

---

## Overview

This document provides a comprehensive comparison of data fields available from each provider. Use this to:
1. Understand which provider has which fields
2. Determine priority rankings for the data_priority_matrix.yaml
3. Identify data gaps and coverage

## Provider Summary

| Provider | Type | Primary Use Case | Rate Limits | Cost |
|----------|------|------------------|-------------|------|
| **YFinance** | API (unofficial) | Real-time prices, fundamentals | Unlimited* | Free |
| **MASSIVE** | API | Metadata, reference data | 5/min, 300/hr | Free tier |
| **FinViz** | Web Scraping | Technicals, valuation, overview | N/A | Free/Elite |
| **StockAnalysis** | Web Scraping | Detailed financials | N/A | Free |
| **Alpha Vantage** | API | ETF data, economic indicators | 5/min | Free/Premium |

*YFinance has soft rate limits; excessive requests may be throttled.

---

## Identity & Classification

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **ticker** | ✅ | ✅ | ✅ | ✅ | Any |
| **company_name** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **sector** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **industry** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **country** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **exchange** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **index_membership** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **cik** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |
| **figi** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |
| **lei** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |
| **sic_code** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |
| **employees** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **ipo_date** | ❌ | ✅ | ✅ | ❌ | MASSIVE (1.0) |
| **website** | ✅ | ✅ | ❌ | ✅ | YFinance (1.0) |
| **description** | ✅ | ✅ | ❌ | ✅ | YFinance (1.0) |
| **logo_url** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |
| **icon_url** | ❌ | ✅ | ❌ | ❌ | MASSIVE (1.0) |

---

## Price & Volume

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **price** | ✅ RT | ❌ | ✅ 15min | ❌ | YFinance (1.0) |
| **open** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **high** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **low** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **close** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **previous_close** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **volume** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **avg_volume** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **relative_volume** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **change_percent** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **gap** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **52w_high** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **52w_low** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **pct_from_52w_high** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **pct_from_52w_low** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |

**Legend:** ✅ = Available, ❌ = Not available, RT = Real-time, 15min = 15-minute delayed

---

## Valuation Metrics

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **market_cap** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **enterprise_value** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **pe_ratio** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **forward_pe** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **peg_ratio** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **price_to_sales** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **price_to_book** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **price_to_cash** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **price_to_fcf** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **ev_to_revenue** | ✅ | ❌ | ❌ | ✅ | YFinance (1.0) |
| **ev_to_ebitda** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |

---

## Profitability & Margins

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **gross_margin** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **operating_margin** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **profit_margin** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **roa** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **roe** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **roic** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |

---

## Balance Sheet & Liquidity

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **current_ratio** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **quick_ratio** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **debt_to_equity** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **lt_debt_to_equity** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **total_debt** | ✅ | ❌ | ❌ | ✅ | YFinance (1.0) |
| **total_cash** | ✅ | ❌ | ❌ | ✅ | YFinance (1.0) |
| **book_value_per_share** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **cash_per_share** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |

---

## Earnings & Growth

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **eps_ttm** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **eps_forward** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **eps_growth_qoq** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **eps_growth_yoy** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **eps_growth_5y** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **revenue_ttm** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **revenue_growth_qoq** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **revenue_growth_yoy** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **revenue_growth_5y** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |

---

## Dividends

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **dividend_rate** | ✅ | ❌ | ❌ | ✅ | YFinance (1.0) |
| **dividend_yield** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **payout_ratio** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **ex_dividend_date** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **dividend_history** | ✅ Full | ✅ Full | ❌ | ❌ | YFinance (1.0) |

---

## Technicals

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **beta** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **sma_20** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **sma_50** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **sma_200** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **rsi_14** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **atr** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **volatility** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |

---

## Ownership

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **insider_ownership** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **institutional_ownership** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **shares_outstanding** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **shares_float** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **short_float** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **short_ratio** | ❌ | ❌ | ✅ | ✅ | FinViz (1.0) |
| **insider_transactions** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **institutional_transactions** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |

---

## Analyst Data

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **target_price** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **analyst_recommendation** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |
| **num_analysts** | ✅ | ❌ | ❌ | ✅ | YFinance (1.0) |
| **earnings_date** | ✅ | ❌ | ✅ | ✅ | YFinance (1.0) |

---

## Performance Windows

| Field | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|-------|----------|---------|--------|---------------|----------|
| **perf_week** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **perf_month** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **perf_quarter** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **perf_half_year** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **perf_year** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |
| **perf_ytd** | ❌ | ❌ | ✅ | ❌ | FinViz (1.0) |

---

## Financial Statements (Detailed)

| Statement Type | YFinance | MASSIVE | FinViz | StockAnalysis | Priority |
|----------------|----------|---------|--------|---------------|----------|
| **Income Statement (Annual)** | ✅ 4yr | ❌ | ✅ 8yr | ✅ 10yr+ | StockAnalysis (1.0) |
| **Income Statement (Quarterly)** | ✅ 4qtr | ❌ | ✅ 8qtr | ✅ 20qtr+ | StockAnalysis (1.0) |
| **Balance Sheet (Annual)** | ✅ 4yr | ❌ | ✅ 8yr | ✅ 10yr+ | StockAnalysis (1.0) |
| **Balance Sheet (Quarterly)** | ✅ 4qtr | ❌ | ✅ 8qtr | ✅ 20qtr+ | StockAnalysis (1.0) |
| **Cash Flow (Annual)** | ✅ 4yr | ❌ | ✅ 8yr | ✅ 10yr+ | StockAnalysis (1.0) |
| **Cash Flow (Quarterly)** | ✅ 4qtr | ❌ | ✅ 8qtr | ✅ 20qtr+ | StockAnalysis (1.0) |

---

## ETF-Specific Fields

| Field | YFinance | Alpha Vantage | FinViz | StockAnalysis | Priority |
|-------|----------|---------------|--------|---------------|----------|
| **expense_ratio** | ✅ | ✅ | ✅ | ✅ | YFinance (1.0) |
| **aum** | ✅ | ✅ | ✅ | ❌ | YFinance (1.0) |
| **nav** | ✅ | ✅ | ✅ | ❌ | YFinance (1.0) |
| **holdings_count** | ✅ | ✅ | ✅ | ❌ | Alpha Vantage (1.0) |
| **top_holdings** | ✅ | ✅ | ❌ | ❌ | Alpha Vantage (1.0) |
| **sector_weights** | ✅ | ✅ | ❌ | ❌ | Alpha Vantage (1.0) |
| **fund_category** | ❌ | ✅ | ✅ | ❌ | Alpha Vantage (1.0) |
| **fund_family** | ✅ | ✅ | ✅ | ❌ | YFinance (1.0) |
| **dividend_ttm** | ✅ | ❌ | ✅ | ❌ | YFinance (1.0) |
| **fund_flows** | ❌ | ❌ | ✅* | ❌ | FinViz Elite only |

---

## Unique Provider Strengths

### YFinance
- **Best for**: Real-time prices, fundamental data, dividend history
- **Unique fields**: Trailing/forward financial metrics, earnings estimates
- **Limitation**: Unofficial API, may break without notice

### MASSIVE (Polygon.io)
- **Best for**: Reference data, identifiers (CIK, FIGI, LEI)
- **Unique fields**: Logo/icon URLs, branding, SIC codes
- **Limitation**: Free tier has rate limits, no price data

### FinViz
- **Best for**: Technical indicators, valuation overview, performance windows
- **Unique fields**: RSI, SMA, relative volume, % from highs/lows, peers, held-by ETFs
- **Limitation**: Requires scraping, some fields Elite-only

### StockAnalysis
- **Best for**: Detailed financial statements, long history
- **Unique fields**: 10+ years of quarterly statements
- **Limitation**: Requires scraping

### Alpha Vantage
- **Best for**: ETF data, economic indicators
- **Unique fields**: ETF holdings with weights, sector allocations
- **Limitation**: 5 calls/minute on free tier

---

## Provider Priority Guidelines

When setting priorities in `data_priority_matrix.yaml`:

1. **Prefer API over scraping** - More reliable, less fragile
2. **Prefer real-time over delayed** - YFinance > FinViz for prices
3. **Prefer official sources** - MASSIVE for identifiers (FIGI, CIK)
4. **Prefer depth for statements** - StockAnalysis for 10+ year history
5. **Use provider strengths** - FinViz for technicals, YFinance for fundamentals

---

## Coverage Summary

| Provider | Fields Covered | Unique Fields | Primary Use |
|----------|---------------|---------------|-------------|
| **YFinance** | ~85 | 15+ | Fundamentals, prices |
| **MASSIVE** | ~40 | 10+ | Reference/metadata |
| **FinViz** | ~90 | 25+ | Technicals, overview |
| **StockAnalysis** | ~60 | 5+ | Financial statements |
| **Alpha Vantage** | ~50 | 10+ | ETF data |

---

## Next Steps

1. ✅ Complete provider ingest specs
2. ⏳ Update data_priority_matrix.yaml with all fields
3. ⏳ Implement standardization engine for multi-source merging
4. ⏳ Add field-level validation rules
5. ⏳ Create monitoring for data freshness

---

**Document Owner:** Engineering Team  
**Review Frequency:** Monthly  
**Next Review:** January 22, 2026
