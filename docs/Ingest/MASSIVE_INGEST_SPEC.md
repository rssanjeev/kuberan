# MASSIVE Ingest Spec

**Last Updated:** December 14, 2025  
**Provider:** MASSIVE  
**Base URL:** `https://api.massive.com/`  
**Reference Docs:**
- `docs/MASSIVE_PROVIDER_GUIDE.md`
- `docs/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md`

---

## 1. Purpose & Role

This document defines **what Kuberan will ingest from MASSIVE** and **how it maps** into provider-specific snapshot structures that can later be unified by the DATA_STANDARDIZATION layer.

MASSIVE is the **authoritative source** for:
- Ticker-level **metadata & identifiers** (CIK, FIGI, SIC, exchange, type).
- **Corporate actions**: stock splits and dividends.
- **News + sentiment** for tickers.

MASSIVE is **not** used for:
- Adjusted close prices (YFinance is canonical).
- HTML fundamentals (Finviz / StockAnalysis handle those views).
- Detailed financial statements (deprecated in free tier).

All ingestion described here is **JSON-only** via the official HTTP API.

---

## 2. Endpoints Used

Only a subset of the free-tier reference endpoints are used for ingestion:

1. **Ticker Metadata (per ticker)**  
   `GET /v3/reference/tickers/{ticker}`

2. **Splits (per ticker or time window)**  
   `GET /v3/reference/splits`

3. **Dividends (per ticker or time window)**  
   `GET /v3/reference/dividends`

4. **News (per ticker)**  
   `GET /v2/reference/news`

Global reference endpoints (`/tickers`, `/tickers/types`, `/exchanges`, `/conditions`) are used for bootstrapping and lookup, not stored as per-ticker snapshots.

Rate limits: **5 calls/min, 300/hour, 7,200/day** (see provider guide for details). Jobs must respect these limits.

---

## 3. Snapshot Types

MASSIVE ingestion produces the following provider snapshots:

1. `massive_metadata_snapshot_v1` – One document per ticker.  
2. `massive_splits_snapshot_v1` – One document per ticker, with an array of split events.  
3. `massive_dividends_snapshot_v1` – One document per ticker, with an array of dividend events.  
4. `massive_news_snapshot_v1` – Many documents (one per article-ticker association).

These names are **provider-local**; the DATA_STANDARDIZATION layer will read from them and produce unified `standard_*` views.

There is **no paywall flagging** here: MASSIVE free tier is feature-limited by plan, not by cell-level paywalls like Finviz/StockAnalysis.

---

## 4. `massive_metadata_snapshot_v1`

### 4.1 Source

- Endpoint: `GET /v3/reference/tickers/{ticker}`
- JSON path: top-level `results` object in MASSIVE response.

### 4.2 Schema

Per ticker, we store a **flattened metadata document** capturing identifiers, classification, and basic fundamentals.

```jsonc
{
  "provider": "MASSIVE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",

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

  "sic_code": "3571",
  "sic_description": "Electronic Computers",

  "list_date": "1980-12-12",
  "total_employees": 164000,

  "phone_number": "1-408-996-1010",
  "address": {
    "address1": "One Apple Park Way",
    "city": "Cupertino",
    "state": "CA",
    "postal_code": "95014"
  },

  "homepage_url": "https://www.apple.com",
  "description": "Apple Inc. designs, manufactures...",

  "branding": {
    "logo_url": "https://api.massive.com/v1/reference/company-branding/...",
    "icon_url": "https://api.massive.com/v1/reference/company-branding/..."
  }
}
```

### 4.3 Field Mapping (MASSIVE → snapshot)

- `ticker` ← `results.ticker`
- `name` ← `results.name`
- `market` ← `results.market`
- `locale` ← `results.locale`
- `primary_exchange` ← `results.primary_exchange`
- `type` ← `results.type`
- `active` ← `results.active`
- `currency_name` ← `results.currency_name`
- `cik` ← `results.cik`
- `composite_figi` ← `results.composite_figi`
- `share_class_figi` ← `results.share_class_figi`
- `sic_code` ← `results.sic_code`
- `sic_description` ← `results.sic_description`
- `list_date` ← `results.list_date`
- `total_employees` ← `results.total_employees`
- `phone_number` ← `results.phone_number`
- `address.*` ← `results.address.*`
- `homepage_url` ← `results.homepage_url`
- `description` ← `results.description`
- `branding.logo_url` ← `results.branding.logo_url`
- `branding.icon_url` ← `results.branding.icon_url`
- `as_of_date` – ISO date when the snapshot was fetched.

DATA_STANDARDIZATION will treat MASSIVE as **authoritative** for identifiers (CIK, FIGI, SIC, exchange, type).

---

## 5. `massive_splits_snapshot`

### 5.1 Source

- Endpoint: `GET /v3/reference/splits`
- Typical query: `?ticker={TICKER}&limit=1000&order=asc&sort=execution_date`
- JSON path: `results[]` array in response.

### 5.2 Schema

One document per ticker, containing an ordered list of split events.

```jsonc
{
  "provider": "MASSIVE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",
  "events": [
    {
      "execution_date": "2020-08-31",
      "split_from": 1,
      "split_to": 4
    },
    {
      "execution_date": "2005-02-28",
      "split_from": 1,
      "split_to": 2
    }
  ]
}
```

### 5.3 Field Mapping

For each element in `results`:

- `events[].execution_date` ← `result.execution_date`
- `events[].split_from` ← `result.split_from`
- `events[].split_to` ← `result.split_to`

DATA_STANDARDIZATION will merge these events with any equivalent data from YFinance (if needed) but MASSIVE is the **primary** source for corporate action structure.

---

## 6. `massive_dividends_snapshot`

### 6.1 Source

- Endpoint: `GET /v3/reference/dividends`
- Typical query: `?ticker={TICKER}&limit=1000&order=asc&sort=ex_dividend_date`
- JSON path: `results[]` array in response.

### 6.2 Schema

One document per ticker, containing an ordered list of dividend events.

```jsonc
{
  "provider": "MASSIVE",
  "ticker": "AAPL",
  "as_of_date": "2025-12-14",
  "events": [
    {
      "ex_dividend_date": "2021-11-05",
      "record_date": "2021-11-08",
      "declaration_date": "2021-10-28",
      "pay_date": "2021-11-11",

      "cash_amount": 0.22,
      "currency": "USD",
      "frequency": 4,
      "dividend_type": "CD"
    }
  ]
}
```

### 6.3 Field Mapping

For each element in `results`:

- `events[].ex_dividend_date` ← `result.ex_dividend_date`
- `events[].record_date` ← `result.record_date`
- `events[].declaration_date` ← `result.declaration_date`
- `events[].pay_date` ← `result.pay_date`
- `events[].cash_amount` ← `result.cash_amount`
- `events[].currency` ← `result.currency`
- `events[].frequency` ← `result.frequency`
- `events[].dividend_type` ← `result.dividend_type`

DATA_STANDARDIZATION will use these events to compute trailing dividend yield, income history, and cross-check with YFinance where needed.

---

## 7. `massive_news_snapshot`

### 7.1 Source

- Endpoint: `GET /v2/reference/news`
- Typical query: `?ticker={TICKER}&limit=50&order=desc&sort=published_utc`
- JSON path: `results[]` array in response.

### 7.2 Schema

We store one document **per article-ticker pair**. Multi-ticker articles are duplicated across tickers.

```jsonc
{
  "provider": "MASSIVE",
  "ticker": "AAPL",
  "article_id": "8ec638777c...93eb",

  "published_utc": "2024-06-24T18:33:53Z",
  "title": "Markets are underestimating Fed cuts: UBS",
  "description": "UBS analysts warn that markets are underestimating...",
  "article_url": "https://uk.investing.com/news/...",
  "image_url": "https://i-invdn-com.investing.com/news/...jpg",

  "publisher": {
    "name": "Investing.com",
    "homepage_url": "https://www.investing.com/",
    "logo_url": "https://s3.massive.com/public/assets/news/logos/investing.png",
    "favicon_url": "https://s3.massive.com/public/assets/news/favicons/investing.ico"
  },

  "sentiment": "positive",
  "sentiment_reasoning": "UBS analysts are providing a bullish outlook..."
}
```

### 7.3 Field Mapping

- `article_id` ← `result.id`
- `published_utc` ← `result.published_utc`
- `title` ← `result.title`
- `description` ← `result.description`
- `article_url` ← `result.article_url`
- `image_url` ← `result.image_url`
- `publisher.*` ← `result.publisher.*`
- `sentiment` / `sentiment_reasoning` ← from `result.insights[]` entry matching `ticker` (if present). If no per-ticker insight exists, `sentiment` may be `null`.

DATA_STANDARDIZATION may aggregate these into per-ticker sentiment scores over rolling windows.

---

## 8. Scheduling & Caching Guidelines

High-level guidance (implementation lives in jobs/services code):

- **Metadata:**
  - Refresh `massive_metadata_snapshot` **every 30–90 days** per ticker (company info changes slowly).
- **Splits/Dividends:**
  - Refresh `massive_splits_snapshot` and `massive_dividends_snapshot` **daily** for tracked tickers.
- **News:**
  - Poll `massive_news_snapshot` **every 10–30 minutes** during market hours for tracked tickers, within rate limits.

All snapshots should include `provider` and `as_of_date` to make downstream reconciliation explicit.

---

## 9. Relationship to DATA_STANDARDIZATION

The DATA_STANDARDIZATION layer will:

- Treat MASSIVE as **canonical** for:
  - Regulatory identifiers (CIK, FIGI, SIC, exchange, type).
  - Corporate action event structure (splits, dividends).
  - News sentiment inputs.
- Merge MASSIVE snapshots with:
  - **YFinance** price and OHLCV data.
  - **Finviz** / **StockAnalysis** HTML-derived fundamentals and ratios.

This spec provides all field-level mappings needed so that the standardization code can:
- Read provider snapshots (`massive_*_snapshot`).
- Map fields into unified `standard_metadata`, `standard_corporate_actions`, and `standard_news` documents.
