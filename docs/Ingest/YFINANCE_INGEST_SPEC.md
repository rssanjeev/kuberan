# YFinance Ingest Spec

**Last Updated:** December 14, 2025  
**Provider:** YFinance (Yahoo Finance)  
**Library:** `yfinance` (Python)  
**Reference Doc:** `docs/YFINANCE_API_GUIDE.md`

---

## 1. Purpose & Role

This document defines **what Kuberan will ingest from YFinance** and **how it maps** into provider-specific snapshot structures for later DATA_STANDARDIZATION.

YFinance is the **authoritative source** for:
- Adjusted OHLCV **price history** (daily/weekly/monthly) for stocks and ETFs.
- Short-to-medium term **intraday bars** (where needed and within limits).
- Dividend and split history (as a cross-check to MASSIVE).

YFinance is **secondary** for:
- Fundamental fields from `Ticker.info` (used selectively, MASSIVE and HTML providers are primary for most metadata).

YFinance is **not** used for:
- Regulatory identifiers (CIK, FIGI, CUSIP, etc.).
- HTML layout or on-page ratios (Finviz/StockAnalysis handle that).

All ingestion is via the `yfinance` Python library, not raw HTTP.

---

## 2. Objects & Methods Used

From `docs/YFINANCE_API_GUIDE.md` we use:

1. `Ticker.history()` – price and corporate actions time series.  
2. `Ticker.dividends` – dividend history series (if needed separately).  
3. `Ticker.splits` – split history series (if needed separately).  
4. `Ticker.info` – a **small canonical subset** of fields.

We do **not** ingest full financial statements from YFinance (income/balance/cash flow) for now; those are handled by other providers.

---

## 3. Snapshot Types

YFinance ingestion produces the following provider snapshots:

1. `yfinance_price_timeseries_snapshot_v1` – Primary OHLCV + adjusted close history.  
2. `yfinance_dividends_snapshot_v1` – Per-ticker dividend events (optional; MASSIVE is primary).  
3. `yfinance_splits_snapshot_v1` – Per-ticker split events (optional; MASSIVE is primary).  
4. `yfinance_fundamentals_snapshot_v1` – Thin fundamentals subset from `Ticker.info`.

These snapshot names are provider-specific; DATA_STANDARDIZATION will consume them to construct unified `standard_prices` and optional `standard_fundamentals` views.

YFinance has **no paywall** concept; we do not use `{raw, paywalled}` wrapping here.

---

## 4. `yfinance_price_timeseries_snapshot_v1`

### 4.1 Source

- Object: `yf.Ticker(ticker)`
- Method: `Ticker.history()`
- Typical calls:

```python
history = ticker.history(
    period="max",           # or bounded start/end
    interval="1d",          # canonical interval for standardization
    auto_adjust=True,        # adjusted for splits/dividends
    actions=True,            # include Dividends/Splits columns
    prepost=False
)
```

### 4.2 Schema

Each snapshot covers **one ticker, one interval** (usually `1d`) over a date range.

```jsonc
{
  "provider": "YFINANCE",
  "ticker": "AAPL",
  "interval": "1d",
  "start_date": "2010-01-01",
  "end_date": "2025-12-13",
  "as_of_date": "2025-12-14",

  "rows": [
    {
      "date": "2025-12-12",
      "open": 220.15,
      "high": 223.40,
      "low": 219.80,
      "close": 222.75,
      "adj_close": 222.75,
      "volume": 123456789,
      "dividends": 0.00,
      "stock_splits": 0.0
    }
    // more rows ordered by date asc
  ]
}
```

### 4.3 Field Mapping (DataFrame → snapshot)

Given `history` is a `pandas.DataFrame` indexed by date:

- `rows[].date` ← row index (converted to ISO date string `YYYY-MM-DD`).
- `rows[].open` ← column `"Open"`.
- `rows[].high` ← column `"High"`.
- `rows[].low` ← column `"Low"`.
- `rows[].close` ← column `"Close"`.
- `rows[].adj_close` ← column `"Close"` when `auto_adjust=True` (already adjusted).  
  - If `auto_adjust=False`, map from `"Adj Close"` instead and keep raw `"Close"`.
- `rows[].volume` ← column `"Volume"`.
- `rows[].dividends` ← column `"Dividends"` (0.0 if missing).
- `rows[].stock_splits` ← column `"Stock Splits"` (0.0 if missing).

Top-level:

- `ticker` – input symbol used to create the `Ticker` object.
- `interval` – same as the `interval` parameter passed to `history()`.
- `start_date` / `end_date` – min/max index dates present in the DataFrame (or explicit start/end if provided).
- `as_of_date` – ISO date when the snapshot was generated.

DATA_STANDARDIZATION will treat this as the **canonical price history** for charting and return calculations.

---

## 5. `yfinance_dividends_snapshot`

### 5.1 Source

- Object: `yf.Ticker(ticker)`
- Property: `Ticker.dividends`

### 5.2 Schema

```jsonc
{
  "provider": "YFINANCE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",
  "events": [
    {
      "date": "2021-11-11",
      "amount": 0.22
    }
  ]
}
```

### 5.3 Field Mapping

Given `dividends` is a `pandas.Series` indexed by date:

- `events[].date` ← index (ISO `YYYY-MM-DD`).
- `events[].amount` ← series value.

**Note:** MASSIVE is the **primary** dividend event source. This snapshot is mainly for cross-validation or backfilling edge cases.

---

## 6. `yfinance_splits_snapshot`

### 6.1 Source

- Object: `yf.Ticker(ticker)`
- Property: `Ticker.splits`

### 6.2 Schema

```jsonc
{
  "provider": "YFINANCE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",
  "events": [
    {
      "date": "2020-08-31",
      "ratio": 4.0
    }
  ]
}
```

### 6.3 Field Mapping

Given `splits` is a `pandas.Series` indexed by date:

- `events[].date` ← index (ISO `YYYY-MM-DD`).
- `events[].ratio` ← series value (e.g., `4.0` for a 4-for-1 split).

Again, MASSIVE is canonical for split structure (`split_from`, `split_to`), while YFinance’s ratio is a quick numeric check.

---

## 7. `yfinance_fundamentals_snapshot`

### 7.1 Source

- Object: `yf.Ticker(ticker)`
- Property: `Ticker.info` (dictionary with 120+ fields).

We store only a **thin, clearly-defined subset** that is either:
- Not available from MASSIVE free tier, or
- Useful as a convenience check.

### 7.2 Schema

```jsonc
{
  "provider": "YFINANCE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",

  "company_name": "Apple Inc.",
  "exchange": "NMS",
  "quote_type": "EQUITY",
  "currency": "USD",

  "sector": "Technology",
  "industry": "Consumer Electronics",

  "market_cap": 2770000000000,
  "pe_trailing": 29.5,
  "pe_forward": 27.1,
  "pb": 45.2,
  "beta": 1.28,

  "dividend_yield": 0.006,      // 0.6%
  "payout_ratio": 0.15,

  "fifty_two_week_high": 230.00,
  "fifty_two_week_low": 160.00,

  "regular_market_price": 222.75,
  "regular_market_day_high": 223.40,
  "regular_market_day_low": 219.80
}
```

### 7.3 Field Mapping (`Ticker.info` → snapshot)

From the `info` dict (if keys are present):

- `company_name` ← `info["longName"]`
- `exchange` ← `info["exchange"]`
- `quote_type` ← `info["quoteType"]`
- `currency` ← `info["currency"]`

- `sector` ← `info.get("sector")`
- `industry` ← `info.get("industry")`

- `market_cap` ← `info.get("marketCap")`
- `pe_trailing` ← `info.get("trailingPE")`
- `pe_forward` ← `info.get("forwardPE")`
- `pb` ← `info.get("priceToBook")`
- `beta` ← `info.get("beta")`

- `dividend_yield` ← `info.get("dividendYield")`
- `payout_ratio` ← `info.get("payoutRatio")`

- `fifty_two_week_high` ← `info.get("fiftyTwoWeekHigh")`
- `fifty_two_week_low` ← `info.get("fiftyTwoWeekLow")`

- `regular_market_price` ← `info.get("regularMarketPrice")`
- `regular_market_day_high` ← `info.get("regularMarketDayHigh")`
- `regular_market_day_low` ← `info.get("regularMarketDayLow")`

Any missing field **must** be omitted or set to `null` explicitly; ingestion logic should not fail if Yahoo omits data for a ticker.

DATA_STANDARDIZATION may:
- Prefer MASSIVE + HTML providers (Finviz/StockAnalysis) for long-term fundamentals.  
- Use `yfinance_fundamentals_snapshot` as a quick, low-friction source for basic ratios and current price context.

---

## 8. Scheduling & Caching Guidelines

- **Price history (`yfinance_price_timeseries_snapshot`):**
  - For active tickers, refresh **daily** after market close (EOD).  
  - Optionally backfill history once (`period="max"`), then maintain incrementally.

- **Dividends / Splits:**
  - Refresh **weekly** or **monthly**; primarily a cross-check to MASSIVE.

- **Fundamentals (`Ticker.info`):**
  - Refresh **every 7–30 days** per ticker – the call is relatively slow and data changes infrequently.

All snapshots must include `provider` and `as_of_date` for clear provenance and reconciliation.

---

## 9. Relationship to DATA_STANDARDIZATION

The DATA_STANDARDIZATION layer will:

- Treat YFinance as **canonical** for:
  - Adjusted OHLCV time series at daily interval (`1d`).
- Treat YFinance as **secondary** / auxiliary for:
  - Dividends, splits (cross-checking MASSIVE).
  - Lightweight fundamentals from `Ticker.info`.

Combined with:
- **MASSIVE** metadata & corporate actions.  
- **Finviz** and **StockAnalysis** HTML-derived fundamentals.

this spec provides all the field-level mappings needed to:
- Read provider snapshots (`yfinance_*_snapshot`).
- Map fields into unified `standard_prices` and `standard_fundamentals` documents.
