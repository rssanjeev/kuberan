Version: v1

# Data Standardization Rules

## 1. Purpose

This document defines how Kuberan standardizes ingested data from multiple providers into a single, consistent view. It is **ticker-agnostic**: rules are defined **per data point**, and the same rules are applied to every ticker.

The goals are:
- Provide a clear contract for the **standardization procedure**.
- Define the structure of the **standardized ticker view**.
- Define a **DATA_PRIORITY_MATRIX** describing how each data point is resolved from multiple providers.
- Stay **configurable** so that provider reliability can be re-weighted without code changes.

Authoritative configuration:
- `config/data_priority_matrix.yaml` is the **machine-readable matrix**
  that standardization code must follow.
- `docs/DATA_PRIORITY_MATRIX.md` is a **human-readable design doc**;
  when it differs from the YAML, the YAML is considered source of
  truth and the Markdown should be updated.

## 2. Key Concepts

### 2.1 Data Point

A **data point** is a single semantic value for a given ticker.

Examples:
- `sic_code`
- `exchange`
- `name`
- `market_cap`
- `close_price` at a specific timestamp
- `news_article` for a ticker

Standardization is: **for each data point, for a given ticker, combine all provider observations into one standardized result**.

### 2.2 Ingest Snapshot

An **ingest snapshot** is a provider-specific document produced by an ingestion pipeline, e.g.:
- `finviz_*_snapshot`
- `stockanalysis_*_snapshot`
- `massive_*_snapshot`
- `yfinance_*_snapshot`

Each snapshot contains raw provider fields. The standardization step **does not scrape or call providers directly**; it only reads these snapshot documents.

### 2.3 Standardized Ticker View (`standardized_ticker_view_v1`)

The **standardized ticker view** is the **materialized result** of applying the rules in this document to all available snapshots for a single ticker.

Conceptually:

```json
{
  "ticker": "AAPL",
  "as_of": "2025-12-14T00:00:00Z",
  "data_points": {
    "sic_code": {
      "value": "3571",
      "source": "massive",
      "inputs": {
        "massive": "3571",
        "finviz": "3571"
      }
    },
    "exchange": {
      "value": "XNAS",
      "source": "massive"
    },
    "market_cap": {
      "value": 2700000000000,
      "source": "yfinance"
    },
    "sector": {
      "value": "Technology",
      "source": "stockanalysis"
    }
    // ... more data points
  }
}
```

Notes:
- The **rules are ticker-agnostic**; `standardized_ticker_view_v1` is just **one-per-ticker storage** for efficient querying.
- Each `data_points[<name>]` entry carries the chosen `value`, `source`, and optionally the raw `inputs` used.

### 2.4 Other Standardized Artifacts

Some data points are naturally **collections** rather than scalars. They may be stored in dedicated collections but still follow the same per–data point rules:

- **Prices** (`standard_price_timeseries_v1`):
  - Time series of OHLCV rows (per ticker, per interval).
- **Corporate Actions** (`standard_corporate_actions_v1`):
  - Arrays of splits and dividends per ticker.
- **News** (`standard_news_article_v1`):
  - One document per article+ticker.

This document focuses on **rules**; physical storage layout can evolve independently.

## 4. Execution & Service Contract

Standardization is executed by a service that reads provider snapshots
and writes standardized views.

- Core interface (conceptual):
  - `standardize_ticker(ticker: str) -> standardized_ticker_view_v1`
  - `standardize_tickers(tickers: List[str]) -> List[standardized_ticker_view_v1]`
- Inputs:
  - All available `finviz_*_snapshot_v1`, `stockanalysis_*_snapshot_v1`,
    `massive_*_snapshot_v1`, `yfinance_*_snapshot_v1` documents for the
    ticker.
  - `config/data_priority_matrix.yaml` loaded into memory.
- Outputs:
  - One `standardized_ticker_view_v1` document per ticker written to
    the `standardized_ticker_views` collection.

Suggested snapshot storage (can evolve independently of rules):
- `finviz_snapshots` for `finviz_*_snapshot_v1`
- `stockanalysis_snapshots` for `stockanalysis_*_snapshot_v1`
- `massive_snapshots` for `massive_*_snapshot_v1`
- `yfinance_snapshots` for `yfinance_*_snapshot_v1`

Each snapshot collection is keyed at minimum by `ticker`, with
optional `as_of`/`fetched_at` timestamps for freshness checks.

Execution modes:
- **On-demand**: called directly when an API consumer needs a
  standardized view and snapshots are reasonably fresh.
- **Batch job**: periodic job (e.g., nightly) that recomputes
  standardized views for all relevant tickers.

Idempotence and overwrite semantics:
- Standardizing the same ticker from the same set of snapshots should
  be **idempotent** (re-running yields an identical
  `standardized_ticker_view_v1`).
- The latest successful standardization run **overwrites** the prior
  document for that ticker in `standardized_ticker_views`.
- Implementations may choose to also keep historical versions (e.g.,
  via `as_of` or an additional `version` field), but v1 only requires
  the latest per ticker.

Error and missing-data semantics:
- If a data point cannot be resolved (no provider has a value), the
  corresponding key **may be omitted** from `data_points` or stored
  with `value: null` and `source: null`.
- If providers disagree beyond configured tolerance (for
  `numeric_consensus`), the implementation may:
  - mark the point as unresolved (omit it), and/or
  - emit logging/metrics for investigation.

This contract is complemented by the shape described in
`standardized_ticker_view.md`.

## 6. Testing & Validation Plan

To ensure the implementation matches these rules, tests should be
organized around deterministic fixtures and strategy-level behavior.

### 6.1 Golden Fixtures (End-to-End)

Create small **golden bundles** per ticker containing:
- One or more provider snapshots (`*_snapshot_v1` documents) serialized
  as JSON.
- A slice of `config/data_priority_matrix.yaml` relevant to those data
  points.
- An expected `standardized_ticker_view_v1` document.

End-to-end tests then:
- Load the snapshots and matrix fragment.
- Run `standardize_ticker(ticker)`.
- Assert deep equality with the expected standardized view.

Golden bundles should cover:
- Happy path: all providers agree or are within tolerance.
- Partial data: only some providers have a value.
- Conflicts: providers disagree beyond tolerance (for
  `numeric_consensus`).
- Missing data: no provider supplies a value for a point.

### 6.2 Strategy-Level Unit Tests

For each strategy (e.g., `single_value`, `numeric_consensus`,
`timeseries_primary_with_checks`):
- Pass in synthetic provider values and matrix parameters.
- Assert that the resolved `{ value, source }` matches expectations.
- Include edge cases:
  - Ties in weight.
  - Values exactly on the tolerance boundary.
  - Outliers that should be ignored.

### 6.3 Invariants & Property Checks

Add higher-level tests that assert invariants, such as:
- If only one provider supplies a value and it is valid, the
  standardized value must match that provider.
- For `numeric_consensus`, the resolved value must lie within the
  configured tolerance envelope of all accepted inputs.
- For `aggregate_union` collections, there should be **no duplicates**
  after normalization.

Where feasible, property-based tests can generate random inputs within
constraints to further validate these invariants.

## 3. Standardization Strategies

Each data point is associated with a **strategy** describing how to resolve multiple inputs.

Supported strategies in v1:

1. **`single_value`**
   - Use one value selected according to provider weights and conflict rules.
   - Typical for stable identifiers: `sic_code`, `exchange`, `name`.

2. **`numeric_consensus`**
   - For numeric values where small discrepancies are expected (e.g., `market_cap`).
   - Use weighted average or choose the value closest to the weighted median within allowed tolerance.

3. **`latest_by_timestamp`**
   - For values that change over time and where providers emit different timestamps.
   - Example: `latest_close_price` if multiple intraday feeds are used.

4. **`timeseries_primary_with_checks`**
   - For price time series (`OHLCV`).
   - One provider is the **primary generator** of the series; others are used only for anomaly detection / sanity checks, not for merging row-by-row in v1.

5. **`aggregate_union`**
   - For collections where we want all valid items from all providers.
   - Example: `news_article` data point (all articles, deduplicated).

6. **`passthrough`**
   - Use data from a single provider with no conflict resolution.
   - Useful for v1 when only one provider currently supplies a given data point.

## 4. DATA_PRIORITY_MATRIX

The **DATA_PRIORITY_MATRIX** is a **machine-readable configuration** for all data points.

- One entry **per data point**.
- Each entry defines:
  - `strategy`: one of the strategies above.
  - `candidates`: list of provider sources with weights and optional flags.
  - Optional `tolerance`, `min_agreement`, or other strategy-specific parameters.

Example (YAML-like):

```yaml
sic_code:
  strategy: single_value
  candidates:
    - provider: massive
      weight: 1.0
    - provider: stockanalysis
      weight: 0.7
    - provider: finviz
      weight: 0.6

exchange:
  strategy: single_value
  candidates:
    - provider: massive
      weight: 1.0
    - provider: yfinance
      weight: 0.8

market_cap:
  strategy: numeric_consensus
  tolerance_pct: 5.0         # max allowed deviation between providers
  candidates:
    - provider: yfinance
      weight: 0.9
    - provider: finviz
      weight: 0.8
    - provider: stockanalysis
      weight: 0.8

close_price:
  strategy: timeseries_primary_with_checks
  candidates:
    - provider: yfinance
      role: primary
    - provider: finviz
      role: sanity_check

news_article:
  strategy: aggregate_union
  candidates:
    - provider: massive
    - provider: finviz
    - provider: stockanalysis
```

### 4.1 Properties

- **Ticker-agnostic**: the matrix is global; the same data point rules apply to all tickers.
- **Configurable**: weights and strategies can change if a provider becomes more/less reliable.
- **Machine-readable**: implemented as YAML/JSON alongside this doc, used by the standardization code.

## 5. v1 Rules for Core Data Points

This section sketches initial entries for key data points. Exact parameter values can be refined as we gain empirical data quality insights.

### 5.1 Identity & Classification

- `sic_code`:
  - Strategy: `single_value`.
  - Candidates: MASSIVE (primary), StockAnalysis, Finviz.

- `exchange`:
  - Strategy: `single_value`.
  - Candidates: MASSIVE (primary), YFinance.

- `name`:
  - Strategy: `single_value`.
  - Candidates: MASSIVE (primary), YFinance, StockAnalysis, Finviz.

- `sector`, `industry`:
  - Strategy: `single_value`.
  - Candidates: StockAnalysis (primary), Finviz, YFinance.

### 5.2 Size & Valuation

- `market_cap`:
  - Strategy: `numeric_consensus`.
  - Candidates: YFinance (high weight), Finviz, StockAnalysis.

- `pe_ttm`, `ps_ttm`, `pb`:
  - Strategy: `numeric_consensus`.
  - Candidates: StockAnalysis (primary if available), Finviz; YFinance as fallback.

### 5.3 Prices (OHLCV)

- `close_price`, `open_price`, `high_price`, `low_price`, `volume` (per timestamp):
  - Strategy: `timeseries_primary_with_checks`.
  - Candidates: YFinance as primary generator of daily adjusted OHLCV; other providers used only for anomaly detection, not merging.

### 5.4 Corporate Actions

- `split_event` (per split):
  - Strategy: `single_value` at event level; list of events is a collection.
  - Candidates: MASSIVE (primary), YFinance as cross-check.

- `dividend_event` (per dividend):
  - Strategy: `single_value` at event level; list of events is a collection.
  - Candidates: MASSIVE (primary), YFinance as cross-check.

### 5.5 News & Sentiment

- `news_article`:
  - Strategy: `aggregate_union`.
  - Candidates: MASSIVE, Finviz, StockAnalysis.
  - Deduplicate by `(url, published_at, title)`.

- `news_sentiment`:
  - Strategy: could be `numeric_consensus` per article/ticker or `passthrough` from MASSIVE in v1.

## 6. Execution Model

For each ticker `T`:

1. **Load snapshots**
   - Fetch all relevant provider snapshots for `T` from MongoDB (Finviz, StockAnalysis, MASSIVE, YFinance).

2. **Compute standardized data points**
   - For each data point defined in the DATA_PRIORITY_MATRIX:
     - Gather all candidate values from snapshots.
     - Apply the configured `strategy` using weights, tolerance, and roles.
     - Produce a resolved `{ value, source, inputs }` record.

3. **Materialize standardized views**
   - Build `standardized_ticker_view_v1` document for `T`.
   - Optionally build or update specialized collections:
     - `standard_price_timeseries_v1` (prices)
     - `standard_corporate_actions_v1` (splits/dividends)
     - `standard_news_article_v1` (news)

4. **Record provenance**
   - Keep track of which providers contributed to each data point to support debugging and future re-weighting.

## 7. Versioning

- This document defines **standardization rules v1**.
- Changes that:
  - Add new data points, or
  - Adjust strategies/weights in non-breaking ways

  can be treated as **v1.x** updates.

- Breaking changes (e.g., renaming data points, changing core strategies) should:
  - Update the version line above.
  - Be accompanied by migration notes for standardized collections.

---

Implementation detail: the **machine-readable DATA_PRIORITY_MATRIX** will live alongside this document (e.g., `config/data_priority_matrix.yaml`) and must be kept in sync with the rules described here.