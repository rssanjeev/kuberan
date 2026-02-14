# FinViz Ingest Specification

**Last Updated:** December 22, 2025  
**Status:** 🟢 Active  
**Version:** v1  
**Purpose:** Define the FinViz snapshot schema and field mappings to standardized data points

---

## Overview

This document specifies how FinViz data is ingested, stored as snapshots, and mapped to Kuberan's standardized data points. FinViz provides data through two sources:
- **Screener** - Bulk data for multiple tickers
- **Quote Page** - Detailed data for individual tickers (includes financial statements)

## Extraction Method

**CRITICAL**: See `scripts/fetch_finviz_all_statements.py` for the confirmed production-ready extraction method using Playwright browser automation.

- **Technology**: Playwright async API (headless Chromium)
- **Parser**: `backend/app/core/finviz_parser.py` (4 separate BeautifulSoup parsers)
- **Output**: 4 HTML files per ticker + parsed JSON with 923+ data points

---

## Snapshot Schema

### Collection Name
```
finviz_snapshots
```

### Document Structure

```json
{
  "provider": "finviz",
  "ticker": "AAPL",
  "snapshot_version": "v1",
  "as_of_date": "2025-12-22",
  "fetched_at": "2025-12-22T14:30:00Z",
  "source_type": "quote_page",
  
  "identity": {
    "company_name": "Apple Inc",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "country": "USA",
    "index": "S&P 500",
    "employees": 164000,
    "ipo_date": "Dec 12, 1980"
  },
  
  "price": {
    "price": 256.77,
    "change": "-1.23%",
    "change_from_open": "0.47%",
    "gap": "0.08%",
    "prev_close": 259.50,
    "volume": "48,321,000",
    "avg_volume": "45.10M",
    "rel_volume": 1.07,
    "trades": "102,345"
  },
  
  "valuation": {
    "market_cap": "4043.84B",
    "enterprise_value": "4150.00B",
    "pe_ratio": 36.69,
    "forward_pe": 29.96,
    "peg_ratio": 2.86,
    "price_to_sales": 9.72,
    "price_to_book": 54.83,
    "price_to_cash": 73.93,
    "price_to_fcf": 40.94,
    "ev_to_ebitda": 27.50,
    "ev_to_sales": 10.20
  },
  
  "financials": {
    "income": "93.74B",
    "sales": "391.04B",
    "book_value_per_share": 4.69,
    "cash_per_share": 3.47
  },
  
  "profitability": {
    "roa": "30.93%",
    "roe": "171.42%",
    "roic": "68.44%",
    "gross_margin": "46.91%",
    "operating_margin": "31.97%",
    "profit_margin": "26.92%"
  },
  
  "liquidity": {
    "current_ratio": 0.89,
    "quick_ratio": 0.86,
    "debt_to_equity": 1.52,
    "lt_debt_to_equity": 1.22
  },
  
  "earnings": {
    "eps_ttm": 8.02,
    "eps_this_year": "10.50%",
    "eps_next_year": "10.83%",
    "eps_next_quarter": 3.56,
    "eps_past_5y": "17.91%",
    "eps_next_5y": "10.49%",
    "eps_past_3y_5y": "8.52% 13.51%",
    "eps_yoy_ttm": "-45.12%",
    "eps_qoq": "-66.54%",
    "sales_past_5y": "8.37%",
    "sales_past_3y_5y": "5.12% 8.37%",
    "sales_yoy_ttm": "5.02%",
    "sales_qoq": "6.07%",
    "earnings_date": "Jan 30 AMC"
  },
  
  "dividend": {
    "dividend_yield": "0.44%",
    "dividend_ttm": "1.00",
    "dividend_est": "1.04",
    "dividend_ex_date": "Nov 08, 2024",
    "dividend_growth_3y_5y": "5.38% 6.18%",
    "payout_ratio": "12.47%"
  },
  
  "ownership": {
    "shares_outstanding": "15.12B",
    "shares_float": "15.10B",
    "insider_ownership": "0.07%",
    "insider_transactions": "-6.22%",
    "institutional_ownership": "62.41%",
    "institutional_transactions": "-0.14%",
    "short_float": "0.90%",
    "short_ratio": 1.00,
    "short_interest": "135.80M"
  },
  
  "performance": {
    "perf_week": "-2.40%",
    "perf_month": "-6.77%",
    "perf_quarter": "-5.34%",
    "perf_half": "1.53%",
    "perf_ytd": "17.94%",
    "perf_year": "15.68%",
    "perf_3y": "45.23%",
    "perf_5y": "120.56%",
    "perf_10y": "450.89%"
  },
  
  "technical": {
    "beta": 1.24,
    "atr": 5.89,
    "volatility_week": "1.99%",
    "volatility_month": "1.85%",
    "volatility": "2.94% 3.37%",
    "sma20": "-1.39%",
    "sma50": "1.54%",
    "sma200": "19.03%",
    "high_52w": "-5.18%",
    "low_52w": "61.73%",
    "rsi": 48.95
  },
  
  "analyst": {
    "target_price": 250.00,
    "recommendation": 1.46
  },
  
  "options": {
    "option_short": "Yes / Yes"
  },
  
  "financial_statements": {
    "income_statement": { ... },
    "balance_sheet": { ... },
    "cash_flow": { ... }
  }
}
```

---

## Field Mapping to Standardized Data Points

This section maps FinViz raw fields to the standardized data point names used in `config/data_priority_matrix.yaml`.

### Identity Fields

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `identity.company_name` | `company_name` | Full legal company name |
| `identity.sector` | `sector` | Business sector classification |
| `identity.industry` | `industry` | Specific industry within sector |
| `identity.country` | `country` | Country code (needs normalization) |
| `identity.index` | `index_membership` | Major index memberships |
| `identity.employees` | `employees` | Full-time employee count |
| `identity.ipo_date` | `primary_listing_date` | IPO date (needs date parsing) |

### Size & Shares Fields

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `valuation.market_cap` | `market_cap` | Needs suffix parsing (B, M, T) |
| `valuation.enterprise_value` | `enterprise_value` | Needs suffix parsing |
| `ownership.shares_outstanding` | `shares_outstanding` | Needs suffix parsing |
| `ownership.shares_float` | `free_float_shares` | Needs suffix parsing |
| `price.avg_volume` | `avg_volume_3m` | Needs suffix parsing |

### Valuation Multiples

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `valuation.pe_ratio` | `pe_ttm` | Already numeric |
| `valuation.forward_pe` | `pe_forward` | Already numeric |
| `valuation.peg_ratio` | `peg_ratio` | Already numeric |
| `valuation.price_to_sales` | `ps_ttm` | Already numeric |
| `valuation.price_to_book` | `pb_ratio` | Already numeric |
| `valuation.price_to_cash` | `price_to_cash` | Already numeric |
| `valuation.price_to_fcf` | `pfcf_ttm` | Already numeric |
| `valuation.ev_to_ebitda` | `enterprise_value_ebitda` | Already numeric |
| `valuation.ev_to_sales` | `enterprise_value_sales` | Already numeric |

### Profitability & Margins

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `profitability.gross_margin` | `gross_margin_ttm` | Strip % suffix |
| `profitability.operating_margin` | `operating_margin_ttm` | Strip % suffix |
| `profitability.profit_margin` | `profit_margin_ttm` | Strip % suffix |
| `profitability.roa` | `return_on_assets_ttm` | Strip % suffix |
| `profitability.roe` | `return_on_equity_ttm` | Strip % suffix |
| `profitability.roic` | `return_on_invested_capital_ttm` | Strip % suffix |

### Earnings & Growth

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `earnings.eps_ttm` | `eps_ttm` | Already numeric |
| `earnings.eps_next_year` | `EPS_forward` | Strip % suffix, estimate |
| `earnings.eps_past_5y` | `eps_growth_5y` | Strip % suffix |
| `earnings.eps_next_5y` | `eps_growth_next_5y` | Strip % suffix |
| `earnings.sales_past_5y` | `revenue_5y_cagr` | Strip % suffix |

### Dividend Fields

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `dividend.dividend_yield` | `Dividend_yield_ttm` | Strip % suffix |
| `dividend.payout_ratio` | `Dividend_payout_ratio_ttm` | Strip % suffix |
| `dividend.dividend_ex_date` | `ex_dividend_date` | Parse date format |

### Risk & Volatility

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `technical.beta` | `beta_5y_monthly` | Already numeric (FinViz uses ~1Y daily) |
| `technical.high_52w` | `price_52w_high` | Needs price extraction if % shown |
| `technical.low_52w` | `price_52w_low` | Needs price extraction if % shown |
| `technical.volatility_week` | `volatility_1w` | Strip % suffix |
| `technical.volatility_month` | `volatility_1m` | Strip % suffix |

### Technical Indicators

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `technical.sma20` | `sma_20d_distance` | Strip % suffix (distance from MA) |
| `technical.sma50` | `sma_50d_distance` | Strip % suffix |
| `technical.sma200` | `sma_200d_distance` | Strip % suffix |
| `technical.rsi` | `rsi_14` | Already numeric |
| `technical.atr` | `atr_14` | Already numeric |

### Ownership & Short Interest

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `ownership.insider_ownership` | `insider_ownership_pct` | Strip % suffix |
| `ownership.institutional_ownership` | `institutional_ownership_pct` | Strip % suffix |
| `ownership.short_float` | `short_interest_pct` | Strip % suffix |
| `ownership.short_ratio` | `short_ratio` | Already numeric (days to cover) |

### Price & Volume (Timeseries)

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `price.price` | `close_price` | Use for sanity check only |
| `price.volume` | `volume` | Use for sanity check only |
| `price.prev_close` | `prev_close` | Previous day close |

### Analyst Data

| FinViz Raw Field | Standardized Key | Notes |
|------------------|------------------|-------|
| `analyst.target_price` | `analyst_target_price` | Already numeric |
| `analyst.recommendation` | `analyst_rating` | 1-5 scale (1=Strong Buy) |

---

## Value Parsing Rules

### Suffix Parsing (Market Cap, Shares, etc.)

```python
def parse_finviz_value(raw_value: str) -> float:
    """Parse FinViz values with suffixes like B, M, K, T."""
    if not raw_value or raw_value == '-':
        return None
    
    raw_value = raw_value.strip().replace(',', '')
    
    multipliers = {
        'T': 1_000_000_000_000,
        'B': 1_000_000_000,
        'M': 1_000_000,
        'K': 1_000
    }
    
    for suffix, multiplier in multipliers.items():
        if raw_value.endswith(suffix):
            return float(raw_value[:-1]) * multiplier
    
    return float(raw_value)
```

### Percentage Parsing

```python
def parse_percentage(raw_value: str) -> float:
    """Parse percentage values, returning decimal (e.g., 5.25% -> 0.0525)."""
    if not raw_value or raw_value == '-':
        return None
    
    raw_value = raw_value.strip().replace('%', '')
    return float(raw_value) / 100.0
```

### Date Parsing

```python
from datetime import datetime

def parse_finviz_date(raw_date: str) -> str:
    """Parse FinViz date formats to ISO 8601."""
    if not raw_date or raw_date == '-':
        return None
    
    # Try different formats FinViz uses
    formats = [
        "%b %d, %Y",  # "Dec 12, 1980"
        "%b %d",       # "Jan 30" (current year)
        "%Y-%m-%d"     # Standard format
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(raw_date.split()[0:3], fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return raw_date  # Return as-is if unparseable
```

---

## Data Quality Flags

### Missing Data Indicators

FinViz uses these indicators for missing data:
- `-` (single dash)
- Empty string
- `N/A`

All should be treated as `null` in standardized output.

### Paywall Detection

Some FinViz data requires Elite subscription. Mark as paywalled:

```json
{
  "value": null,
  "paywalled": true,
  "source": "finviz"
}
```

### Staleness Detection

Compare `as_of_date` with current date. Data older than:
- **1 day**: Mark as potentially stale for price data
- **7 days**: Mark as stale for fundamentals
- **30 days**: Mark as very stale

---

## Provider Priority in Matrix

FinViz is configured as a secondary provider in most cases:

| Category | FinViz Priority Weight | Primary Provider |
|----------|----------------------|------------------|
| Market Cap | 0.9 | yfinance (1.0) |
| P/E Ratios | 0.9 | stockanalysis (1.0) |
| Margins | 0.9 | stockanalysis (1.0) |
| Ownership | 0.9 | stockanalysis (1.0) |
| Beta | 0.9 | stockanalysis (1.0) |
| 52W High/Low | 0.9 | yfinance (1.0) |
| News | union | massive (lead) |
| Price (timeseries) | sanity_check | yfinance (primary) |

---

## Indexes

### Recommended MongoDB Indexes

```javascript
// Primary lookup by ticker
db.finviz_snapshots.createIndex({ ticker: 1, as_of_date: -1 })

// Sector/Industry filtering
db.finviz_snapshots.createIndex({ "identity.sector": 1 })
db.finviz_snapshots.createIndex({ "identity.industry": 1 })

// Valuation screening
db.finviz_snapshots.createIndex({ "valuation.pe_ratio": 1 })
db.finviz_snapshots.createIndex({ "valuation.market_cap": 1 })
```

---

## Related Documentation

- [FINVIZ_SCHEMA.json](FINVIZ_SCHEMA.json) - Complete raw schema reference
- [FINVIZ_QUOTE_PAGE_STRUCTURE.md](FINVIZ_QUOTE_PAGE_STRUCTURE.md) - HTML structure for extraction
- [DATA_PRIORITY_MATRIX.md](../Standardization/DATA_PRIORITY_MATRIX.md) - Provider priority configuration
- [DATA_STANDARDIZATION_RULES.md](../Standardization/DATA_STANDARDIZATION_RULES.md) - Standardization strategies
- [WEB_SCRAPING.md](../../.github/docs/WEB_SCRAPING.md) - FinViz extraction method

---

## Changelog

### v1 (December 22, 2025)
- Initial specification
- Complete field mapping to standardized data points
- Value parsing rules for suffixes, percentages, dates
- Provider priority configuration
