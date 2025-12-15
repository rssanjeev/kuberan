Version: v1

# Standardized Ticker View

## 1. Purpose

This document describes the **standardized ticker view** in Kuberan, a per-ticker materialization of data standardized across all providers.

It complements `DATA_STANDARDIZATION_RULES.md` by focusing on:
- The shape of the standardized view.
- How it is expected to be stored and queried.
- How it relates to individual data points and the `DATA_PRIORITY_MATRIX`.

## 2. Concept Overview

The standardized ticker view is a **single document per ticker** that captures the resolved values for many data points after standardization.

Key properties:
- **Ticker-agnostic rules**: Logic is defined per data point; each ticker uses the same rules.
- **Multi-provider inputs**: Values come from Finviz, StockAnalysis, MASSIVE, and YFinance ingest snapshots.
- **Provenance-aware**: Each data point stores the chosen source and, optionally, raw inputs.

The canonical name used in docs and code for this materialization is `standardized_ticker_view_v1`.

## 3. Document Structure

At a high level, a standardized ticker view document looks like this:

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
      "source": "yfinance",
      "inputs": {
        "yfinance": 2700000000000,
        "finviz": 2680000000000,
        "stockanalysis": 2695000000000
      }
    },
    "sector": {
      "value": "Technology",
      "source": "stockanalysis"
    }
    // ... more data points
  }
}
```

### 3.1 Top-Level Fields

- `ticker` (string):
  - The canonical ticker symbol for this document.
  - Resolved using the `ticker` data point rules in `DATA_PRIORITY_MATRIX`.

- `as_of` (ISO8601 timestamp):
  - The logical timestamp when this standardized view was computed.
  - May align with a batch run time (e.g., nightly job) or on-demand computation.

- `data_points` (object):
  - A map from **data point name** (e.g., `sic_code`, `market_cap`) to a standardized record.

### 3.2 Data Point Entry Shape

Each entry in `data_points` follows this pattern:

```json
"<data_point_name>": {
  "value": <standardized_value>,
  "source": "<provider_name>",
  "inputs": {
    "massive": <raw_value_from_massive_if_any>,
    "yfinance": <raw_value_from_yfinance_if_any>,
    "finviz": <raw_value_from_finviz_if_any>,
    "stockanalysis": <raw_value_from_stockanalysis_if_any>
  }
}
```

- `value`:
  - The resolved standardized value, as determined by the strategy in `DATA_PRIORITY_MATRIX`.

- `source`:
  - The provider whose value ultimately "won" for this data point.
  - One of: `massive`, `yfinance`, `finviz`, `stockanalysis`, or `null` if unresolved.

- `inputs` (optional):
  - Raw values per provider that participated in the resolution, useful for debugging and quality analysis.
  - May be omitted for storage efficiency in v1, or persisted only for selected data points.

## 4. Relationship to DATA_STANDARDIZATION_RULES and Matrix

The standardized ticker view is **not** where rules live; it is the **product** of applying rules.

- `DATA_STANDARDIZATION_RULES.md`:
  - Describes strategies and conceptual behavior.
  - Defines what data points exist and how they should be resolved conceptually.

- `config/data_priority_matrix.yaml`:
  - Machine-readable configuration of strategies, candidates, and weights for each data point.

- `standardized_ticker_view_v1` (this doc):
  - Defines how the **resulting per-ticker document** should look and behave.

### 4.1 Execution Flow (Per Ticker)

1. **Load Provider Snapshots**
   - Read all ingest snapshots for the ticker from Finviz, StockAnalysis, MASSIVE, YFinance.

2. **Resolve Each Data Point**
   - For every data point defined in the matrix:
     - Gather candidate values from provider snapshots.
     - Apply the configured strategy (e.g., `single_value`, `numeric_consensus`).
     - Produce a `{ value, source, inputs }` record.

3. **Assemble standardized_ticker_view_v1**
   - Populate `ticker` and `as_of`.
   - Populate `data_points` with all resolved entries.

4. **Persist**
   - Store the document in a dedicated collection (e.g., `standardized_ticker_views`).
   - Optionally index by `ticker` for fast lookup.

## 5. Storage & Indexing Recommendations

- Collection name (suggested): `standardized_ticker_views`.
- Primary index:
  - `{ ticker: 1 }` for fast per-ticker lookup.
- Optional compound index:
  - `{ ticker: 1, as_of: -1 }` if multiple historical versions per ticker are stored.

## 6. Versioning

- This document describes **standardized_ticker_view_v1**.
- Future versions (e.g., `v2`) may:
  - Add new top-level fields.
  - Extend the structure of `data_points` entries.
  - Introduce richer provenance or quality flags.
- Backwards-incompatible changes should:
  - Update the version line at the top of this file.
  - Be paired with migration notes for the underlying collection.

## 7. Related Documents

- `docs/DATA_STANDARDIZATION_RULES.md` — conceptual rules and strategies.
- `config/data_priority_matrix.yaml` — machine-readable matrix driving resolution.
- Provider ingest specs in `docs/Ingest/` — describe how raw snapshots are shaped.
