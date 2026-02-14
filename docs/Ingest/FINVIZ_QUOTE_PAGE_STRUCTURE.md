# Finviz Quote Page Structure

**Last Updated:** 2025-12-17  
**Status:** 🟢 Active - Reference for FinViz HTML structure  
**Purpose:** Document the structural layout of FinViz quote pages for data extraction

---

## ⭐ Confirmed Extraction Method

**IMPORTANT**: This document describes the HTML structure. For the **confirmed production-ready extraction method**, see:

- **Implementation**: `scripts/fetch_finviz_all_statements.py` (Playwright browser automation)
- **Parser**: `backend/app/core/finviz_parser.py` (4 separate BeautifulSoup parsers)
- **Documentation**: [Copilot Instructions - FinViz Section](../../.github/copilot-instructions.md#finviz-data-extraction-confirmed-standard-method)
- **Guide**: [WEB_SCRAPING.md - FinViz Section](../../.github/docs/WEB_SCRAPING.md#current-implementation-finviz-financial-statements-)

**User Quote**: *"Here after, if I mention extracting data from FinViz - This is what I mean."*

### Quick Start

```bash
# 1. Install Playwright (one-time)
pip3 install playwright && playwright install chromium

# 2. Extract all 3 financial statement tabs
python3 scripts/fetch_finviz_all_statements.py NVDA

# 3. Parse and validate (generates JSON with 923+ data points)
cd backend && python3 -m app.scripts.test_finviz_parser NVDA
```

**Extraction Results**:
- ✅ Snapshot Table: 83 metrics
- ✅ Income Statement: 8 periods × 30 metrics = 240 data points
- ✅ Balance Sheet: 8 periods × 39 metrics = 312 data points
- ✅ Cash Flow: 8 periods × 36 metrics = 288 data points

---

## Overview

This document describes the *structural layout* of Finviz quote pages
(`https://finviz.com/quote.ashx?t={TICKER}&p=d`) for both **stocks** and
**ETFs**. It serves as a reference for understanding the HTML structure
and how our extraction pipeline works.

The goal is to answer, for every field you may want from Finviz:

> "Where on the page do I look, and what stable cues can I use to
>  extract it?"

Our production extraction pipeline (Playwright + BeautifulSoup) uses this structure
to generate a concrete `finviz_snapshot_v1` JSON document. See the **Snapshot Schema**
section below for the exact fields and types.

---

## 1. URL Pattern & Page Types

- Base URL: `https://finviz.com/quote.ashx?t={TICKER}&p=d`
  - `{TICKER}`: stock or ETF ticker (e.g., `NVDA`, `MSFT`, `KO`, `VZ`, `VOO`).
  - `p=d`: daily chart view. Other values exist (e.g., `w`, `m`) but the
    *content blocks described here are the same*.
- Stocks and ETFs share **the same page template** with mostly identical
  layout. ETF pages reuse the snapshot table but may swap some company-
  specific fields (e.g., employees) for fund-specific fields (e.g., yield,
  expense, AUM).


## 2. High-Level Layout

Ignoring the global navigation, ads, and banners, the main quote content is
organized in this order (from top to bottom):

1. **Quote Header Row**
2. **Last Price / Change Block**
3. **Classification Chips Row** (Sector / Industry / Country / Exchange)
4. **Main Chart Panel** (chart + timeframe controls)
5. **Peers / "Held by" ETFs Row**
6. **Snapshot / Fundamentals Table** (large grid of label → value pairs)
7. **Additional Tables** (not always needed):
   - News headlines
   - Insider transactions
   - Option chains / ownership (for some tickers)

The **primary extraction target** is the Snapshot / Fundamentals table, plus
three supplemental areas:

- Quote Header Row (ticker + company name)
- Classification Chips Row (sector / industry / country / exchange)
- Peers / "Held by" ETFs Row (related tickers)

---

## 1.1 Snapshot Schema (`finviz_snapshot_v1`)

The Finviz ingest pipeline produces one **snapshot document per ticker**
with the following logical schema:

```jsonc
{
  "provider": "FINVIZ",
  "ticker": "NVDA",
  "as_of_date": "2025-12-14",

  "identity": {
    "company_name": "NVIDIA Corp",
    "exchange": "NASDAQ",
    "country": "USA",
    "sector": "Technology",
    "industry": "Semiconductors"
  },

  "snapshot_table": {
    "market_cap": "1.23T",
    "pe": "75.4",
    "forward_pe": "45.2",
    "peg": "2.10",
    "eps_ttm": "3.45",
    "dividend_yield": "0.03%",
    "payout_ratio": "8.5%",
    "roe": "45.0%",
    "profit_margin": "28.0%",
    "operating_margin": "32.0%",
    "current_ratio": "3.2",
    "quick_ratio": "2.8",
    "debt_to_equity": "40.0%",
    "beta": "1.70",
    "eps_next_5y": "25.0%"
    // many more label → raw string entries
  },

  "price_block": {
    "last_price": 123.45,
    "change": -1.23,
    "change_percent": -0.99
  },

  "held_by_etfs": ["VOO", "QQQ"],

  "raw_html_metadata": {
    "page_url": "https://finviz.com/quote.ashx?t=NVDA&p=d"
  }
}
```

Notes:
- Values in `snapshot_table` are stored as **raw strings exactly as
  rendered by Finviz**; standardization is responsible for parsing and
  normalizing them into numeric data points.
- `identity` and `price_block` fields may be duplicated across
  providers; the DATA_PRIORITY_MATRIX defines how conflicts are
  resolved.


## 3. Quote Header Row

### Visual Description

At the very top of the main content area, Finviz shows:

- The **ticker symbol** in large font (e.g., `NVDA`)
- The **company/fund name** next to it (e.g., `NVIDIA Corp`, `Vanguard S&P 500 ETF`)
- In some cases a small **country flag** and/or **exchange name** nearby

These are presented as a single horizontal row, typically above the chart and
snapshot table.

### Structural Pattern (DOM-wise)

- A `table` or `div` block containing:
  - A bold or large-font element for the ticker symbol.
  - A text/link element immediately following for company/fund name.
- The ticker string matches the `{TICKER}` in the query parameter (e.g., `NVDA`).

### Extraction Strategy

1. **Find the main ticker text**:
   - Identify the first large-font text element that exactly matches the
     ticker you requested (e.g., `NVDA`, `MSFT`, `VZ`, `KO`, `VOO`).
   - Nearby (same row or immediate sibling), capture the company/fund name.
2. Treat this as the **ground truth identifier** for the page.

> This row is useful for validation (confirming you are on the correct
> ticker) and for storing the Finviz display name.


## 4. Last Price / Change Block

### Visual Description

Immediately below the header, Finviz displays the **current or last close
price** in a large font, together with:

- Dollar change (e.g., `-5.91`)
- Percent change (e.g., `-3.27%`)
- Date and time (e.g., `Dec 13, 2025 04:00 PM`)

All are grouped together in a compact block, often to the left or center,
above the chart.

### Structural Pattern

- Numeric text in large font, often followed by a colored change value
  (green for up, red for down) and a percentage in parentheses.
- A date/time string in proximity.

### Extraction Strategy (Optional)

If you decide to get the last price from this block (rather than from another
source):

1. From the header row, descend into the first block that contains a large
   numeric value plus `%`.
2. Parse:
   - `last_price`: first numeric token.
   - `change_dollar`: next numeric token (with sign).
   - `change_percent`: token containing `%`.
   - `timestamp`: the human-readable date/time string nearby.

Given Kuberan already has strong price data from MASSIVE/YFinance, this block
is **supplemental** and primarily useful for display-level validation.


## 5. Classification Chips Row (Sector / Industry / Country / Exchange)

### Visual Description

Directly below the price block, there is a row of **clickable chips** like:

- `Technology` | `Semiconductors` | `USA` | `NASDAQ`

Or for other tickers:

- `Consumer Defensive` | `Beverages - Non-Alcoholic` | `USA` | `NYSE`

For ETFs, categories may still show the **sector/industry** of the underlying
universe or a fund category.

### Structural Pattern

- Presented as inline links or buttons.
- Order is consistent: **Sector → Industry → Country → Exchange**.
- Each chip is a separate clickable element.

### Extraction Strategy

1. Locate the row immediately below the price block that:
   - Contains 3–4 short text elements.
   - These elements are all links.
2. Map them by position:
   - `sector`   ← first chip
   - `industry` ← second chip
   - `country`  ← third chip
   - `exchange` ← fourth chip (may include index/market label)

This row should be used as the Finviz-sourced classification for the ticker.


## 6. Peers / "Held by" ETFs Row

### Visual Description

Below the chart controls and above the snapshot table, Finviz shows a small
two-part row:

- `Peers: AMD AVGO INTC QCOM TSM ...`
- `Held by: VTI VOO SPY IVV QQQ ...`

Each peer or ETF is a clickable ticker link.

### Structural Pattern

- A block of text that includes literal labels:
  - `Peers` (followed by a colon and a list of ticker links)
  - `Held by` (followed by colon and ETF ticker links)
- The tickers are anchors with `href` pointing back to `quote.ashx?t=`.

### Extraction Strategy

1. Search the DOM for text node containing `Peers` and `Held by`.
2. From that container:
   - Collect all ticker links immediately following `Peers:` → **peer list**.
   - Collect all ticker links immediately following `Held by:` → **ETF holders list**.
3. Normalise tickers by trimming spaces and taking the visible text.

This row is the **primary Finviz-only value add** for Kuberan:
- Quick peer universe.
- Primary ETFs that hold the stock (e.g., `VOO`, `SPY`, `QQQ`).


## 7. Snapshot / Fundamentals Table

### Visual Description

The snapshot table is the **large grid of fundamental and technical metrics**
that dominates the page. It is laid out as **label/value pairs** in rows,
roughly like this (example labels):

- `Index` | `P/E` | `EPS (ttm)` | `Insider Own` | `Shs Outstand` | `Perf Week`
- `Market Cap` | `Forward P/E` | `EPS next Y` | `EPS next Q` | `PEG` | `P/S`
- `P/B` | `P/C` | `P/FCF` | `EPS this Y` | `EPS next Y` | ...
- `ROA` | `ROE` | `ROI` | `Curr Ratio` | `Quick Ratio` | `LT Debt/Eq`
- `Gross Margin` | `Oper. Margin` | `Profit Margin` | `Payout` | `Dividend %` | ...
- `Perf Month` | `Perf Quarter` | `Perf Half Y` | `Perf Year` | `Perf YTD` | ...
- `52W High` | `52W Low` | `% from High` | `% from Low` | `50D MA` | `200D MA`
- `Volume` | `Avg Volume` | `Beta` | `Target Price` | `RSI (14)` | `Rel Volume`

The exact set and ordering can vary slightly over time, but **labels are
consistent** and uniquely identify each metric.

### Structural Pattern

- A single `table` that contains **all these labels and values**.
- Each label and value is in its own cell; pattern is:
  - `<td>Label1</td><td>Value1</td><td>Label2</td><td>Value2</td>...` per row.
- Label cells and value cells often have different CSS classes, but the most
  robust approach is to match by **visible label text**.

### General Extraction Strategy

1. **Locate the snapshot table**:
   - Find the first large table below the Peers/"Held by" row whose cells
     contain known labels such as `Index`, `P/E`, `EPS (ttm)`, `Market Cap`.
2. **Iterate over all `td` cells in document order**:
   - Treat **even-indexed cells** as labels and the following cell as the
     corresponding value, **or** more robustly:
   - For each cell whose text matches a known label (e.g., `P/E`), take its
     **immediate next sibling cell** as the value.
3. **Normalise labels** (e.g., `EPS (ttm)` → `eps_ttm`, `P/E` → `pe_ratio`).
4. Store `label → (raw_value_text)` mappings.

> The label text is the most stable selector; avoid relying solely on CSS
> classes or positional indices.

### Field Map (Representative Subset)

Below is a non-exhaustive, but representative field map. For each label,
search for that exact (or very close) visible text in the snapshot table.

#### Identification & Size

- `Index` → e.g., `S&P 500`, `DJIA`, or `-`.
- `Market Cap` → e.g., `2.77T`, `45.2B`.
- `Shs Outstand` → Shares outstanding.
- `Shs Float` → Free float.
- `Insider Own` → Insider ownership %.
- `Inst Own` → Institutional ownership %.

#### Valuation

- `P/E` → Price/Earnings (ttm).
- `Forward P/E` → Forward P/E.
- `PEG` → PEG ratio.
- `P/S` → Price/Sales.
- `P/B` → Price/Book.
- `P/C` → Price/Cash.
- `P/FCF` → Price/Free Cash Flow.

#### Earnings & Growth

- `EPS (ttm)` → EPS trailing twelve months.
- `EPS next Y` → Next-year EPS estimate.
- `EPS next Q` → Next-quarter EPS estimate.
- `EPS this Y` → EPS growth this year.
- `EPS next Y` → EPS growth next year.
- `EPS past 5Y` → EPS growth over past 5 years.
- `Sales past 5Y` → Revenue growth over past 5 years.

#### Profitability & Efficiency

- `ROA` → Return on Assets.
- `ROE` → Return on Equity.
- `ROI` → Return on Investment.
- `Gross Margin` → Gross profit margin.
- `Oper. Margin` → Operating margin.
- `Profit Margin` → Net profit margin.

#### Balance Sheet & Leverage

- `Curr Ratio` → Current ratio.
- `Quick Ratio` → Quick ratio.
- `Debt/Eq` → Debt-to-equity.
- `LT Debt/Eq` → Long-term debt-to-equity.

#### Dividends (Stocks & ETFs)

- `Dividend %` → Dividend yield (stock or fund-level).
- `Payout` → Payout ratio.
- `Ex-Dividend` / `Ex-Dividend Date` → Ex-dividend date.

For ETFs, the dividend section is usually richer and may appear with labels
similar to:

- `Dividend TTM` → Trailing twelve-month distribution, typically formatted
  as `amount (yield%)`, e.g. `3.75 (1.11%)`.
- `Dividend Ex-Date` → Most recent ex-dividend date, e.g. `Sep 29, 2025`.
- `Dividend Gr. 3/5Y` → Dividend growth over 3 and 5 years, often rendered
  as `X.XX% / Y.YY%`.

Your scraper should split these composite values only if you explicitly need
them separated; otherwise, preserving the raw Finviz string is acceptable.

For ETFs you will also commonly see fund-level cash-flow and size labels such
as:

- `AUM` / `Assets` → Assets under management (`575.77B`, `71.69B`, `116.01B`,
  etc.).
- `Total Holdings` → Number of underlying securities (`3535`, `108`, `8684`).
- `NAV/sh` → Net asset value per share.

Treat all of these as **optional labels**; they will be present on most
ETFs, rarely on individual stocks.

#### Performance Windows

- `Perf Week` → 1-week performance %.
- `Perf Month` → 1-month performance %.
- `Perf Quarter` → 3-month performance %.
- `Perf Half Y` → 6-month performance %.
- `Perf Year` → 1-year performance %.
- `Perf YTD` → Year-to-date performance %.
- `Perf 5Y` → 5-year performance % (when present).

#### Range & Technicals

- `52W High` → 52-week high price.
- `52W Low` → 52-week low price.
- `% from High` → Distance from 52W high.
- `% from Low` → Distance from 52W low.
- `50D MA` → 50-day moving average.
- `200D MA` → 200-day moving average.
- `SMA20`, `SMA50`, `SMA200` (sometimes) → Simple moving averages.
- `RSI (14)` → RSI with period 14.
- `Beta` → Beta.

#### Volume & Liquidity

- `Volume` → Current day volume.
- `Avg Volume` → Average daily volume.
- `Rel Volume` → Relative volume.

#### Analyst & Sentiment

- `Target Price` → Analyst target price.
- `Recommendation` → Analyst recommendation score (if shown).
- `Short Float` → Short interest as % of float.
- `Short Ratio` → Days to cover (short interest / avg volume).


## 8. Stock vs ETF Differences

This section is intended to answer a very concrete question for the scraper:

> "Given the *same* template, which labels are stock-oriented, which are
>  ETF-oriented, and which are shared?"

### 8.1 Shared Core Fields

These labels appear on both stocks and ETFs and can be treated identically:

- Identification & size: `Index`, `Market Cap`, `Shs Outstand`.
- Valuation: `P/E`, `Forward P/E`, `PEG`, `P/S`, `P/B`, `P/C`, `P/FCF`.
- Performance windows: `Perf Week`, `Perf Month`, `Perf Quarter`,
  `Perf Half Y`, `Perf Year`, `Perf YTD`, `Perf 3Y`, `Perf 5Y`, `Perf 10Y`
  (when present).
- Range & technicals: `52W High`, `52W Low`, `% from High`, `% from Low`,
  `50D MA`, `200D MA`, `SMA20`, `SMA50`, `SMA200`, `RSI (14)`, `Beta`.
- Volume & liquidity: `Volume`, `Avg Volume`, `Rel Volume`.
- Basic dividends: `Dividend %`, `Payout`, `Ex-Dividend`.
- Trading meta: `Prev Close`, `Price`, `Change`, `IPO`.
- Short/derivatives: `Option/Short` (usually shown as `Yes / Yes`).

Your normalization layer should therefore have a single set of keys for
these fields regardless of whether the entity is a stock or an ETF.

### 8.2 Stock-Oriented Fields (Rare or Absent on ETFs)

Primarily meaningful for operating companies; often absent for ETFs:

- Ownership: `Insider Own`, `Insider Trans`, `Inst Own`, `Inst Trans`.
- Earnings & growth: `EPS (ttm)`, `EPS next Y`, `EPS next Q`, `EPS this Y`,
  `EPS next Y` (growth), `EPS past 5Y`, `Sales past 5Y`.
- Profitability: `ROA`, `ROE`, `ROI`, `Gross Margin`, `Oper. Margin`,
  `Profit Margin`.
- Balance sheet & leverage: `Curr Ratio`, `Quick Ratio`, `Debt/Eq`,
  `LT Debt/Eq`.
- Analyst & sentiment: `Target Price`, `Recommendation`, `Short Float`,
  `Short Ratio`.

If you see these labels on an ETF page, treat them as you would for a stock
but be aware that their interpretation may be at the fund level (and less
commonly populated).

### 8.3 ETF-Oriented Fields (Rare or Absent on Stocks)

For ETFs such as `VTI`, `SCHD`, `VXUS`, you will consistently see
fund-specific labels. These are the main ones you should expect:

- **Category & region**
  - `Category` or equivalent description line such as:
    - `US Equities - Broad Market & Size`
    - `US Equities - Dividend & Fundamental`
    - `Global or ExUS Equities - Broad / Regional`
  - Tags indicating `U.S.` vs `International`.
  - Normalized key suggestion: `fund_category`, `region_tag`.

- **Fund size & structure**
  - `AUM` / `Assets` → Assets under management.
  - `Total Holdings` → Number of underlying securities.
  - `NAV/sh` → Net asset value per share.
  - `Expense` → Expense ratio (e.g., `0.03%`, `0.06%`, `0.05%`).
  - `Growth/Value` → Style orientation (may be textual or coded).
  - `Inverse/Leveraged` → Indicates whether the ETF is inverse/leveraged.
  - `Structure Type` / `ETF Type` / `Fund Family` / `Sponsor`.

- **Fund flows and distribution metrics**
  - `Dividend TTM` → Trailing 12‑month distribution (`amount (yield%)`).
  - `Dividend Ex-Date` → Ex-dividend date.
  - `Dividend Gr. 3/5Y` → Dividend growth over 3 and 5 years.
  - `Flows% 1M`, `Flows% 3M`, `Flows% YTD`, `Flows% 1Y`, `Flows% 3Y`,
    `Flows% 5Y` → Net flow percentages over various horizons. Some of the
    longer horizons may be hidden behind Finviz Elite; in that case, you will
    see the label but an empty or `-` value.

- **Additional technical nuance**
  - `ATR (14)` → Average True Range.
  - `Volatility` → Often shown as two numbers (e.g., `0.99% 1.26%`).
  - `Trades` → Total number of trades for the session (when present).

For these ETF-only labels, you should define normalized keys such as
`aum`, `total_holdings`, `nav_per_share`, `expense_ratio`, `fund_flows_1m`,
`fund_flows_3m`, `fund_dividend_ttm`, `fund_dividend_growth_3y`, etc. The
exact naming is flexible; consistency is more important than the specific
string.

### 8.4 Practical Guidance

- Treat all fields as **optional label/value pairs**.
- Do not hard-code a fixed schema for a given label order; instead:
  - Always parse the snapshot table generically.
  - Maintain a mapping from label → normalized key (core + ETF-specific).
  - When a label is absent (e.g., `ROE` for some ETFs), the field is simply
    `None` / missing.
- Use an explicit `entity_type` flag (`"stock"` vs `"etf"`) in your
  downstream schema so that consumers can interpret ambiguous fields like
  `Dividend %` correctly.

### 8.5 Paywalled / Hidden Content (Finviz Elite)

Finviz offers additional data to **Elite** subscribers. On a free account
you will sometimes see **the label present but the value effectively
hidden**, typically rendered as:

- A bare dash (`-`)
- An obviously empty cell, while adjacent time-horizon fields are populated
- In some cases, text or iconography clearly indicating Elite-only access

This is most visible on ETF pages for **longer-horizon flow metrics**
(`Flows% 3Y`, `Flows% 5Y`) and occasionally other advanced fields.

For Kuberan, you should treat this as a **first-class paywall signal**, not
as generic missing data. The goal is to be able to:

1. Distinguish between "data truly missing" vs "data gated by Elite".
2. Backfill Elite-only fields later **without changing the schema** when an
   Elite subscription is available.

#### 8.5.1 Field Shape

Each entry under the `fields` object is an object with at least a `raw`
string, and may include a `paywalled` flag:

```jsonc
"fields": {
  "flows_3y": { "raw": "-", "paywalled": true },
  "flows_1y": { "raw": "10.25%" },
  "market_cap": { "raw": "575.77B" }
}
``

Semantics:

- `raw`  
  The **literal text** visible in the cell (`-`, `10.25%`, `3.75 (1.11%)`,
  etc.). Do **not** attempt to infer or impute hidden values.
- `paywalled` (optional, boolean)  
  - `true`  → The label is present but the visible value is clearly
    Elite-gated (placeholder / empty / "Elite"), and the missingness is
    due to access level, not genuine data absence.
  - `false` or omitted → Either the value is fully visible, or it is
    genuinely not reported by Finviz (e.g., small or illiquid instruments).

Scrapers **must not guess**; they should only set `paywalled: true` when the
behaviour matches known Elite gating patterns (e.g., shorter horizons like
`Flows% 1M` and `Flows% 1Y` are populated while `Flows% 3Y`/`Flows% 5Y` show
`-`).

#### 8.5.2 Snapshot-Level Paywall Flags

In addition to per-field flags, snapshots may include an optional
`paywall` object at the top level to summarise Elite-only behaviour for
downstream consumers:

```jsonc
"paywall": {
  "has_elite_only_flows": true
}
```

Suggested flags (all optional, default `false` / absent):

- `has_elite_only_flows`  
  At least one of the `flows_*` fields is marked `paywalled: true`.

You can extend this object in the future if Finviz introduces other clearly
Elite-only groups (e.g., advanced ownership breakdowns).


## 9. Additional Tables (Optional)

### 9.1 News Table

Typically appears **below** the snapshot table and includes columns like:

- Date/Time
- Source (e.g., `MarketWatch`, `Reuters`)
- Headline (clickable link)

If you ever need Finviz news, search for a table with rows containing
headlines and dates, but note that Kuberan already has better news/sentiment
sources via MASSIVE.

### 9.2 Insider Transactions Table

For many **stocks**, Finviz shows an insider trades table with columns like:

- `Insider`
- `Relationship`
- `Date`
- `Transaction`
- `Cost`
- `#Shares`
- `Value ($)`
- `#Shares Total`
- `SEC Form 4`

This table can become very long. Extract it only if you explicitly need
insider trade data, as it is not central to Kuberan’s current design.


## 10. Tool-Agnostic Extraction Recipes

Below are generic recipes that can be implemented in Playwright, Puppeteer,
`mcp_fetch` + HTML parsing, etc.

### 10.1 Locate Main Blocks

1. **Quote root**: from `document`, locate the main content container that sits
   between the top navigation and the footer.
2. **Header row**: find the large ticker text matching your target symbol;
   take adjacent text as company/fund name.
3. **Classification chips**: from the header/price area, find the row of
   link-like chips; map them positionally (sector, industry, country,
   exchange).
4. **Peers/"Held by" row**: search for a block containing text `Peers` and
   `Held by`; collect following ticker links.
5. **Snapshot table**: find the first table below the peers row where the
   cell texts include known labels like `Index`, `P/E`, `Market Cap`.

### 10.2 Parse Snapshot Table

For each `row` in the snapshot table:

1. Get all `td` cells in order.
2. For `i` from 0 to `cells.length - 1` step 2:
   - `label_text = cells[i].innerText.trim()`
   - `value_text = cells[i+1].innerText.trim()` (if exists)
   - If `label_text` is non-empty:
     - Normalise to a key (`pe_ratio`, `market_cap`, etc.).
     - Store `key → value_text`.
3. If you prefer, instead of stepping by 2, you may:
   - Maintain a dictionary of expected labels.
   - For each cell, if `cell.innerText` is in that dictionary, take its
     `nextElementSibling` as the value.

### 10.3 Example Normalization Pseudocode

```pseudo
normalize_label(label):
  l = label.lower().strip()
  if l == 'p/e': return 'pe_ratio'
  if l.startswith('eps (ttm'): return 'eps_ttm'
  if l.startswith('market cap'): return 'market_cap'
  if l == 'dividend %': return 'dividend_yield'
  if l == 'curr ratio': return 'current_ratio'
  if l == 'quick ratio': return 'quick_ratio'
  if l == 'debt/eq': return 'debt_to_equity'
  if l == 'lt debt/eq': return 'lt_debt_to_equity'
  if l == 'roa': return 'roa'
  if l == 'roe': return 'roe'
  if l == 'roi': return 'roi'
  if l.startswith('gross margin'): return 'gross_margin'
  if l.startswith('oper. margin'): return 'operating_margin'
  if l.startswith('profit margin'): return 'profit_margin'
  if l.startswith('perf week'): return 'perf_week'
  if l.startswith('perf month'): return 'perf_month'
  if l.startswith('perf quarter'): return 'perf_quarter'
  if l.startswith('perf half y'): return 'perf_half_year'
  if l.startswith('perf year'): return 'perf_year'
  if l.startswith('perf ytd'): return 'perf_ytd'
  if l.startswith('52w high'): return 'high_52w'
  if l.startswith('52w low'): return 'low_52w'
  if l.startswith('50d ma'): return 'ma_50d'
  if l.startswith('200d ma'): return 'ma_200d'
  if l.startswith('target price'): return 'target_price'
  if l.startswith('rsi'): return 'rsi_14'
  # ... extend as needed
  return snake_case(l)  # safe fallback
```


## 11. Suggested Normalized Snapshot Schema

To make implementation concrete, this section sketches a **recommended
in-memory schema** for a single Finviz quote snapshot, then provides:

1. A label → normalized-key mapping table with example values.
2. A sample JSON structure for a **stock**.
3. A sample JSON structure for an **ETF**.

You are not required to match this exactly, but any scraper should be able to
populate something equivalent.

### 11.1 Label → Key Mapping Table

The table below lists the most important labels you will see in the snapshot
table, the suggested normalized key, one example of a raw value, and
whether it typically applies to stocks, ETFs, or both.

> Notes:
> - Labels are shown as they usually appear on Finviz; minor variations
>   (spacing, capitalization) should be handled by the normalization layer.
> - "Applies To" is a guideline; some fields *can* appear outside their
>   usual domain but are rare.

| Label (as seen on Finviz)   | Normalized Key              | Example Raw Value          | Applies To |
|-----------------------------|-----------------------------|----------------------------|------------|
| `Index`                     | `index_name`                | `S&P 500`                  | both       |
| `Market Cap`                | `market_cap`                | `2.77T`                    | both       |
| `Shs Outstand`             | `shares_outstanding`        | `2.46B`                    | both       |
| `Shs Float`                 | `float_shares`              | `2.40B`                    | stock      |
| `P/E`                       | `pe_ratio`                  | `45.23`                    | both       |
| `Forward P/E`               | `forward_pe_ratio`          | `32.10`                    | both       |
| `PEG`                       | `peg_ratio`                 | `1.85`                     | both       |
| `P/S`                       | `price_to_sales`            | `12.34`                    | both       |
| `P/B`                       | `price_to_book`             | `18.90`                    | both       |
| `P/C`                       | `price_to_cash`             | `24.50`                    | both       |
| `P/FCF`                     | `price_to_free_cash_flow`   | `30.10`                    | both       |
| `Dividend %`                | `dividend_yield`            | `0.04%`                    | both       |
| `Payout`                    | `payout_ratio`              | `5.00%`                    | both       |
| `Ex-Dividend` / `Ex-Dividend Date` | `ex_dividend_date`   | `Dec 12, 2025`             | both       |
| `Dividend TTM`              | `dividend_ttm`              | `3.75 (1.11%)`             | etf        |
| `Dividend Ex-Date`          | `dividend_ex_date`          | `Sep 29, 2025`             | etf        |
| `Dividend Gr. 3/5Y`         | `dividend_growth_3y_5y`     | `7.83% / 4.81%`            | etf        |
| `AUM` / `Assets`            | `aum`                       | `575.77B`                  | etf        |
| `Total Holdings`            | `total_holdings`            | `3535`                     | etf        |
| `NAV/sh`                    | `nav_per_share`             | `335.40`                   | etf        |
| `Expense`                   | `expense_ratio`             | `0.03%`                    | etf        |
| `Growth/Value`              | `growth_value_style`        | `Blend`                    | etf        |
| `Inverse/Leveraged`         | `leverage_type`             | `No / No`                  | etf        |
| `Sponsor`                   | `fund_sponsor`              | `Vanguard`                 | etf        |
| `Fund Family`               | `fund_family`               | `Schwab ETFs`              | etf        |
| `Category` / category line  | `fund_category`             | `US Equities - Broad Market & Size` | etf |
| `Region` / region tag       | `region_tag`                | `U.S.` / `International`   | etf        |
| `Flows% 1M`                 | `flows_1m`                  | `0.80%`                    | etf        |
| `Flows% 3M`                 | `flows_3m`                  | `1.87%`                    | etf        |
| `Flows% YTD`                | `flows_ytd`                 | `6.61%`                    | etf        |
| `Flows% 1Y`                 | `flows_1y`                  | `10.25%`                   | etf        |
| `Flows% 3Y`                 | `flows_3y`                  | `18.40%`                   | etf        |
| `Flows% 5Y`                 | `flows_5y`                  | `27.90%`                   | etf        |
| `Perf Week`                 | `perf_week`                 | `-0.47%`                   | both       |
| `Perf Month`                | `perf_month`                | `1.80%`                    | both       |
| `Perf Quarter`              | `perf_quarter`              | `3.10%`                    | both       |
| `Perf Half Y`               | `perf_half_year`            | `14.45%`                   | both       |
| `Perf Year`                 | `perf_year`                 | `12.22%`                   | both       |
| `Perf YTD`                  | `perf_ytd`                  | `15.93%`                   | both       |
| `Perf 3Y`                   | `perf_3y`                   | `70.85%`                   | both       |
| `Perf 5Y`                   | `perf_5y`                   | `75.64%`                   | both       |
| `Perf 10Y`                  | `perf_10y`                  | `212.87%`                  | both       |
| `Return% 1Y`                | `return_1y`                 | `13.32%`                   | etf        |
| `Return% 3Y`                | `return_3y`                 | `21.17%`                   | etf        |
| `Return% 5Y`                | `return_5y`                 | `13.48%`                   | etf        |
| `Return% 10Y`               | `return_10y`                | `12.10%`                   | etf        |
| `EPS (ttm)`                 | `eps_ttm`                   | `6.01`                     | stock      |
| `EPS next Y`                | `eps_next_year`             | `8.20`                     | stock      |
| `EPS next Q`                | `eps_next_quarter`          | `1.95`                     | stock      |
| `EPS this Y`                | `eps_growth_this_year`      | `85.0%`                    | stock      |
| `EPS past 5Y`               | `eps_growth_past_5y`        | `40.0%`                    | stock      |
| `Sales past 5Y`             | `sales_growth_past_5y`      | `22.0%`                    | stock      |
| `ROA`                       | `roa`                       | `10.50%`                   | stock      |
| `ROE`                       | `roe`                       | `34.12%`                   | stock      |
| `ROI`                       | `roi`                       | `20.75%`                   | stock      |
| `Gross Margin`              | `gross_margin`              | `68.0%`                    | stock      |
| `Oper. Margin`              | `operating_margin`          | `45.0%`                    | stock      |
| `Profit Margin`             | `profit_margin`             | `30.0%`                    | stock      |
| `Curr Ratio`                | `current_ratio`             | `1.80`                     | stock      |
| `Quick Ratio`               | `quick_ratio`               | `1.50`                     | stock      |
| `Debt/Eq`                   | `debt_to_equity`            | `0.40`                     | stock      |
| `LT Debt/Eq`                | `lt_debt_to_equity`         | `0.25`                     | stock      |
| `Insider Own`               | `insider_ownership`         | `3.10%`                    | stock      |
| `Insider Trans`             | `insider_transaction_change`| `-0.50%`                   | stock      |
| `Inst Own`                  | `institutional_ownership`   | `70.0%`                    | stock      |
| `Inst Trans`                | `institutional_transaction_change` | `1.20%`          | stock      |
| `Short Float`               | `short_float`               | `1.50%`                    | stock      |
| `Short Ratio`               | `short_ratio`               | `1.20`                     | stock      |
| `Target Price`              | `target_price`              | `650.00`                   | stock      |
| `Recommendation`            | `recommendation_score`      | `1.80`                     | stock      |
| `52W High`                  | `high_52w`                  | `974.00`                   | both       |
| `52W Low`                   | `low_52w`                   | `390.00`                   | both       |
| `% from High`               | `percent_from_high_52w`     | `-10.50%`                  | both       |
| `% from Low`                | `percent_from_low_52w`      | `70.25%`                   | both       |
| `50D MA`                    | `ma_50d`                    | `450.00`                   | both       |
| `200D MA`                   | `ma_200d`                   | `400.00`                   | both       |
| `SMA20`                     | `sma_20d`                   | `1.06%`                    | both       |
| `SMA50`                     | `sma_50d`                   | `1.24%`                    | both       |
| `SMA200`                    | `sma_200d`                  | `10.04%`                   | both       |
| `RSI (14)`                  | `rsi_14`                    | `54.32`                    | both       |
| `ATR (14)`                  | `atr_14`                    | `3.75`                     | both       |
| `Volatility`                | `volatility`                | `0.99% 1.26%`              | both       |
| `Volume`                    | `volume`                    | `4,254,367`                | both       |
| `Avg Volume`                | `avg_volume`                | `4.06M`                    | both       |
| `Rel Volume`                | `relative_volume`           | `1.05`                     | both       |
| `Prev Close`                | `prev_close`                | `339.87`                   | both       |
| `Price`                     | `last_price`                | `335.99`                   | both       |
| `Change`                    | `session_change_percent`    | `-1.14%`                   | both       |
| `Trades`                    | `trades`                    | `102,345`                  | both       |
| `IPO`                       | `ipo_date`                  | `May 31, 2001`             | both       |
| `Option/Short`              | `option_short_flags`        | `Yes / Yes`                | both       |

Your implementation does not have to store all of these fields; it should,
however, be prepared to recognise these labels and map them consistently.

### 11.2 Sample JSON Structure – Stock

Below is a plausible snapshot for a stock like `NVDA`.

```jsonc
{
  "source": "finviz",
  "ticker": "NVDA",
  "entity_type": "stock",                  // "stock" or "etf"
  "as_of": "2025-12-13T16:00:00Z",         // optional timestamp
  "header": {
    "display_ticker": "NVDA",
    "name": "NVIDIA Corp"
  },
  "classification": {
    "sector": "Technology",
    "industry": "Semiconductors",
    "country": "USA",
    "exchange": "NASDAQ"
  },
  "related": {
    "peers": ["AMD", "AVGO", "INTC", "QCOM"],
    "held_by": ["VTI", "VOO", "SPY", "QQQ"]
  },
  "fields": {
    "market_cap": { "raw": "2.77T" },
    "pe_ratio": { "raw": "45.23" },
    "forward_pe_ratio": { "raw": "32.10" },
    "peg_ratio": { "raw": "1.85" },
    "eps_ttm": { "raw": "6.01" },
    "eps_next_year": { "raw": "8.20" },
    "eps_growth_this_year": { "raw": "85.0%" },
    "eps_growth_past_5y": { "raw": "40.0%" },
    "sales_growth_past_5y": { "raw": "22.0%" },
    "roa": { "raw": "10.50%" },
    "roe": { "raw": "34.12%" },
    "roi": { "raw": "20.75%" },
    "gross_margin": { "raw": "68.0%" },
    "operating_margin": { "raw": "45.0%" },
    "profit_margin": { "raw": "30.0%" },
    "current_ratio": { "raw": "1.80" },
    "quick_ratio": { "raw": "1.50" },
    "debt_to_equity": { "raw": "0.40" },
    "lt_debt_to_equity": { "raw": "0.25" },
    "insider_ownership": { "raw": "3.10%" },
    "institutional_ownership": { "raw": "70.0%" },
    "short_float": { "raw": "1.50%" },
    "short_ratio": { "raw": "1.20" },
    "target_price": { "raw": "650.00" },
    "recommendation_score": { "raw": "1.80" },
    "dividend_yield": { "raw": "0.04%" },
    "payout_ratio": { "raw": "5.00%" },
    "ex_dividend_date": { "raw": "Dec 12, 2025" },
    "perf_week": { "raw": "3.45%" },
    "perf_month": { "raw": "8.10%" },
    "perf_year": { "raw": "220.00%" },
    "perf_ytd": { "raw": "190.00%" },
    "high_52w": { "raw": "974.00" },
    "low_52w": { "raw": "390.00" },
    "percent_from_high_52w": { "raw": "-10.50%" },
    "percent_from_low_52w": { "raw": "70.25%" },
    "ma_50d": { "raw": "900.00" },
    "ma_200d": { "raw": "750.00" },
    "rsi_14": { "raw": "65.20" },
    "atr_14": { "raw": "25.30" },
    "beta": { "raw": "1.69" },
    "volume": { "raw": "48,321,000" },
    "avg_volume": { "raw": "45.10M" },
    "relative_volume": { "raw": "1.07" },
    "prev_close": { "raw": "920.00" },
    "last_price": { "raw": "930.50" },
    "session_change_percent": { "raw": "1.14%" },
    "ipo_date": { "raw": "Jan 22, 1999" },
    "option_short_flags": { "raw": "Yes / Yes" }
  }
}
```

### 11.3 Sample JSON Structure – ETF

Below is a plausible snapshot for an ETF like `VTI`.

```jsonc
{
  "source": "finviz",
  "ticker": "VTI",
  "entity_type": "etf",                   // "stock" or "etf"
  "as_of": "2025-12-13T16:00:00Z",        // optional timestamp
  "header": {
    "display_ticker": "VTI",
    "name": "Vanguard Total Stock Market ETF"
  },
  "classification": {
    "sector": "Financial",                // as shown in chips row
    "industry": "Asset Management",
    "country": "USA",
    "exchange": "NYSEARCA",
    "fund_category": "US Equities - Broad Market & Size",
    "region_tag": "U.S."
  },
  "related": {
    "peers": ["SCHB", "ITOT", "SPTM"],
    "held_by": []                           // usually empty for ETFs
  },
  "paywall": {
    "has_elite_only_flows": true
  },
  "fields": {
    "market_cap": { "raw": "575.77B" },
    "aum": { "raw": "575.77B" },
    "total_holdings": { "raw": "3535" },
    "nav_per_share": { "raw": "335.40" },
    "expense_ratio": { "raw": "0.03%" },
    "fund_sponsor": { "raw": "Vanguard" },
    "fund_family": { "raw": "Vanguard ETFs" },
    "growth_value_style": { "raw": "Blend" },
    "dividend_ttm": { "raw": "3.75 (1.11%)" },
    "dividend_ex_date": { "raw": "Sep 29, 2025" },
    "dividend_growth_3y_5y": { "raw": "7.83% / 4.81%" },
    "flows_1m": { "raw": "0.80%" },
    "flows_3m": { "raw": "1.87%" },
    "flows_ytd": { "raw": "6.61%" },
    "flows_1y": { "raw": "10.25%" },
    // Example of Elite-gated horizons on a free account:
    "flows_3y": { "raw": "-", "paywalled": true },
    "flows_5y": { "raw": "-", "paywalled": true },
    "perf_week": { "raw": "-0.47%" },
    "perf_month": { "raw": "0.04%" },
    "perf_quarter": { "raw": "3.10%" },
    "perf_half_year": { "raw": "14.45%" },
    "perf_year": { "raw": "12.22%" },
    "perf_ytd": { "raw": "15.93%" },
    "perf_3y": { "raw": "70.85%" },
    "perf_5y": { "raw": "75.64%" },
    "perf_10y": { "raw": "212.87%" },
    "return_1y": { "raw": "13.32%" },
    "return_3y": { "raw": "21.17%" },
    "return_5y": { "raw": "13.48%" },
    "high_52w": { "raw": "345.00" },
    "low_52w": { "raw": "280.00" },
    "percent_from_high_52w": { "raw": "-2.61%" },
    "percent_from_low_52w": { "raw": "19.99%" },
    "sma_20d": { "raw": "1.06%" },
    "sma_50d": { "raw": "1.24%" },
    "sma_200d": { "raw": "10.04%" },
    "rsi_14": { "raw": "54.32" },
    "atr_14": { "raw": "3.75" },
    "volatility": { "raw": "0.99% 1.26%" },
    "volume": { "raw": "4,254,367" },
    "avg_volume": { "raw": "4.06M" },
    "relative_volume": { "raw": "1.05" },
    "prev_close": { "raw": "339.87" },
    "last_price": { "raw": "335.99" },
    "session_change_percent": { "raw": "-1.14%" },
    "ipo_date": { "raw": "May 31, 2001" },
    "option_short_flags": { "raw": "Yes / Yes" }
  }
}
```

Key points for implementation:

- **Header** and **classification** should be populated from the header row
  and classification chips, not from the snapshot table.
- All fields in `fields` are **optional**; if a label is missing on the
  page, simply omit the key or set its value to `null`.
- You may choose to only keep `raw` strings initially and add a separate
  parsed layer later; do not let parsing failures block collection of raw
  values.
- For Kuberan, this entire object will likely live under a dedicated
  `finviz_snapshot` namespace so that it does not conflict with the
  authoritative provider data (MASSIVE/YFinance).


## 12. How to Use This Document in Kuberan

- Treat this as the **schema contract** between Kuberan and any Finviz
  scraper implementation.
- Any new tool (Playwright script, `mcp_fetch` HTML parser, etc.) should:
  1. Follow the block-finding logic in sections 3–7.
  2. Parse snapshot labels using section 7 + 10.2.
  3. Apply normalization as in 10.3 (or an equivalent mapping).
- Keep in mind Kuberan’s **provider priority** rules:
  - MASSIVE/YFinance remain authoritative for prices and most fundamentals.
  - Finviz-derived values should be treated as **supplemental** and may be
    stored separately (e.g., under a `finviz_snapshot` namespace) for UI and
    cross-checking purposes.

This structure has been validated against multiple Finviz quote pages across
stocks (e.g., `NVDA`, `MSFT`, `KO`, `VZ`) and ETFs (e.g., `VOO`, `VTI`,
`SCHD`, `VXUS`). Minor presentation differences (ads, banners) do not affect
the core blocks
documented above.