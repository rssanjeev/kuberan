# StockAnalysis Quote Page Structure

**Last Updated:** 2025-12-14

This document describes the *structural layout* of StockAnalysis **stock
pages** for **individual stocks**, with a primary focus on the main
overview page but also including the key supporting pages used by Kuberan:

- Overview: `https://stockanalysis.com/stocks/{TICKER}/`
- Financials (annual & quarterly income statement)
- Statistics
- Metrics (segment / geography / expenses)
- Revenue
- Market Cap
- Dividend
- Company/Profile
- Forecast / Analyst expectations (where available)

It is **tool-agnostic** and is intended as the reference for any future
scraper implementation (Playwright, Puppeteer, `mcp_fetch`, etc.). Ingest
pipelines turn these HTML layouts into concrete
`stockanalysis_snapshot_v1` JSON documents; see the **Snapshot Schema**
section below for the exact fields and types.

The aim is to answer, for every field we may want from these pages:

> "Where on the page do I look, what stable cues can I use to
>  extract it, and is the value freely visible or hidden behind a
>  paywall/upgrade?"

Sections 2–10 focus on the **overview page**. Later sections document the
other StockAnalysis stock pages and clearly call out which portions are
visible on the free tier versus gated behind StockAnalysis Pro ("Upgrade")
so that we can backfill them if/when we upgrade the subscription.

---

## 1. URL Pattern & Scope

- **Base URL (overview)**: `https://stockanalysis.com/stocks/{TICKER}/`
  - Examples: `…/stocks/nvda/`, `…/stocks/aapl/`, `…/stocks/snps/`.

- **Other important URLs for the same ticker** (all covered by this
  document in later sections):
  - Financials (Income Statement, annual): `…/stocks/{TICKER}/financials/`
  - Financials (Income Statement, quarterly):
    `…/stocks/{TICKER}/financials/?p=quarterly`
  - Statistics: `…/stocks/{TICKER}/statistics/`
  - Metrics (segments / geographies / expenses):
    `…/stocks/{TICKER}/metrics/`
  - Revenue: `…/stocks/{TICKER}/revenue/`
  - Market Cap: `…/stocks/{TICKER}/market-cap/`
  - Dividend: `…/stocks/{TICKER}/dividend/`
  - Company/Profile page: `…/stocks/{TICKER}/company/`
  - Forecast / Analyst page (naming can vary):
    `…/stocks/{TICKER}/forecast/` (overview nav label: **Forecasts**)

Sections 2–10 document the **overview page snapshot**.
Sections 11+ document the other URLs (Financials, Statistics, Metrics,
Revenue, Market Cap, Dividend, Company, Forecast) and how to represent
their data and paywalled state.

---

## 1.1 Snapshot Schema (`stockanalysis_snapshot_v1`)

The StockAnalysis ingest pipeline produces one **snapshot document per
ticker** with the following logical schema:

```jsonc
{
  "provider": "STOCKANALYSIS",
  "ticker": "NVDA",
  "as_of_date": "2025-12-14",

  "identity": {
    "company_name": "NVIDIA Corp",
    "exchange": "NASDAQ",
    "sector": "Technology",
    "industry": "Semiconductors",
    "country": "USA"
  },

  "overview_metrics": {
    "market_cap": 1225000000000,
    "pe_ttm": 75.4,
    "forward_pe": 45.2,
    "ps_ttm": 32.1,
    "pb": 45.0,
    "dividend_yield": 0.0003
    // additional numeric metrics from the key stats strip
  },

  "summary_cards": {
    "revenue_ttm": 55000000000,
    "net_income_ttm": 15000000000,
    "eps_ttm": 3.45
    // optional: other clearly labeled card metrics
  },

  "company_profile": {
    "description": "NVIDIA Corp engages in...",
    "founded": 1993,
    "employees": 26400,
    "website_url": "https://www.nvidia.com"
  },

  "financials": {
    "income_statement_annual": [],
    "income_statement_quarterly": []
    // filled where values are visible on the free tier
  },

  "paywall_flags": {
    "metrics": {
      "segments": "paywalled",
      "geographies": "paywalled"
    }
  }
}
```

Notes:
- Only **freely visible** values are populated; any metric that is
  fully hidden behind a StockAnalysis Pro paywall is either marked in
  `paywall_flags` or omitted.
- All numeric fields are stored in already-parsed numeric form; raw
  HTML strings stay out of the snapshot so standardization can work on
  clean numbers.


## 2. High-Level Layout (Overview Page)

Ignoring global nav and footer, the main content of `…/stocks/{TICKER}/`
roughly appears in this order (top to bottom):

1. **Page Header Block** (ticker, company name, exchange, primary classification)
2. **Price & Key Stats Strip** (current price, daily change, market cap, P/E, etc.)
3. **Primary Chart Panel** (price chart; we do *not* scrape chart pixels)
4. **Key Metrics / Summary Cards** (high-level fundamentals, sometimes in cards)
5. **Tabbed Sections** (Overview, Financials, Statistics, etc. – navigation only)
6. **Company Description / Info Panel** (short business description)
7. **Secondary Info Panels** (market cap insight, revenue insight, dividend note, etc.)

For the overview page snapshot, our primary targets are:

- Header identity block (ticker, name, exchange, sector/industry)
- Price & key stats strip (price, change, market cap, P/E, dividend, etc.)
- Any clearly labeled **summary metrics** presented in a key-stats table
- Company description text block

We deliberately **do not** parse chart images or intra-day price series from
this page; time-series price data comes from MASSIVE/YFinance.


## 3. Header Identity Block

### Visual Description

At the top of the page you typically see:

- Ticker in bold (e.g., `NVDA`)
- Full company name (e.g., `NVIDIA Corporation`)
- Exchange and listing type information (e.g., `NASDAQ: NVDA`)
- Sometimes a brief classification (e.g., `Semiconductors`, `Technology`)

This block sits above the main price readout.

### Structural Pattern

While HTML may evolve, the consistent cues are:

- A prominent text element with the ticker symbol.
- Adjacent text with the company name.
- A smaller subheading or chip with `EXCHANGE: TICKER` formatting.

### Extraction Strategy

1. Find the first header section whose text contains the ticker (case-insensitive).
2. Within that block, capture:
   - `display_ticker`: visible ticker text (e.g., `NVDA`).
   - `company_name`: immediately adjacent text.
   - `exchange` and `listing`: from `EXCHANGE: TICKER` pattern if present.
3. Treat this as **identity verification** and store under `header` in the snapshot.


## 4. Price & Key Stats Strip

### Visual Description

Directly under the header, StockAnalysis shows a consolidated strip with:

- **Current share price** (large font, e.g., `$482.79`).
- **Daily change** in absolute and percentage terms (colored red/green).
- A short list of key stats, often inline or in a small grid, e.g.:
  - Market Cap (e.g., `$89.78B`)
  - P/E (e.g., `66.5`)
  - EPS (e.g., `$7.26`)
  - Dividend Yield (e.g., `0.54%` or `—`)
  - 52-week range, or similar.

These values echo information elsewhere on the site (e.g., the
`/market-cap/` or `/revenue/` pages).

### Structural Pattern

- A container just below the header that contains one large price element
  followed by several small label-value pairs.
- Labels are written out as clear English phrases (e.g., `Market Cap`,
  `Dividend Yield`, `P/E Ratio`).

### Extraction Strategy

1. From the header container, descend into the first child that contains:
   - A numeric with currency symbol and 2 decimal places (price), and
   - A nearby `%`-bearing string (daily percent change).
2. Record:
   - `last_price.raw` – full price string.
   - `price_change.raw` – text containing daily change.
3. For each label-value pair in the same strip (e.g., `Market Cap  $89.78B`):
   - Match on the visible **label text**.
   - Take the adjacent element as the `raw` value.

> These are **supplemental overview stats**. The canonical source for
> market cap, revenue, etc., is still MASSIVE/YFinance, but we store
> StockAnalysis values for cross-checking and richer UX.


## 5. Summary Metrics / Key Statistics (Overview Page)

### Visual Description

Below the price strip, the overview page often presents a consolidated
"key statistics" section – typically in one of two formats:

1. A **table** of label → value pairs (e.g., `Revenue (ttm)`, `EPS (ttm)`,
   `Profit Margin`, etc.).
2. A set of **cards** each with a title and a value (e.g., `Revenue (ttm)`
   as a card title, with `$7.05B` as the body).

The exact layout can change, but the **labels are stable English phrases**.

### Structural Pattern

- Labels are human-readable text nodes (e.g., `Market Cap`, `Revenue (ttm)`).
- Values are adjacent text in the same row/card.
- In some cases, StockAnalysis annotates units in a header (e.g.,
  `Financials in millions USD. Fiscal year is November - October.`) –
  that applies more to the dedicated Financials/Revenue pages, but the
  overview may echo some of those numbers.

### Extraction Strategy

1. Locate the container immediately below the price strip that:
   - Uses repeated label/value pairs (table rows or cards).
2. For each label:
   - Normalize the label to a key (see Section 8).
   - Store the adjacent value string as `raw`.
3. Treat all fields as **optional**; absence of a label simply means
   that field is omitted from this snapshot.


## 6. Company Description / Info Panel

### Visual Description

Further down the page, typically after the stats and chart, there is a
text block titled something like:

- `Company Profile`
- `About {Company Name}`

This block contains 1–3 paragraphs describing the business. For example,
for Synopsys or NVIDIA, this includes business segments and markets.

### Structural Pattern

- A heading (e.g., `Company Profile`) followed by a `<p>` or series of
  paragraphs.
- Text is pure narrative with no embedded numbers that we treat as
  structured metrics.

### Extraction Strategy

1. Search for a heading with text like `Company Profile` or `About`.
2. Take the following one or two paragraph elements and join them into a
   single `company_description.raw` string.
3. Do **not** attempt to NLP-parse this into structured fields at this
   stage; treat as free-form text.


## 7. Secondary Insight Panels (Market Cap, Revenue, Dividend)

### Visual Description

StockAnalysis frequently shows **insight panels** either on the overview
page or on dedicated URLs (e.g., `/market-cap/`, `/revenue/`, `/dividend/`).
Examples of such text:

- Market cap insight (from `/market-cap/`):
  > `Synopsys has a market cap or net worth of $89.78 billion as of December 11, 2025. Its market cap has increased by 3.43% in one year.`

- Revenue insight (from `/revenue/`):
  > `In the fiscal year ending October 31, 2025, Synopsys had annual revenue of $7.05B with 15.12% growth. Synopsys had revenue of $2.25B in the quarter ending October 31, 2025, with 37.83% growth.`

- Dividend insight (from `/dividend/`):
  > `There is no dividend history available for Synopsys. This usually means that the stock has never paid a dividend.`

On the **overview** page you may see condensed versions of these insights
or short notes like `No dividend history`.

### Structural Pattern

- Often rendered as a highlighted text box below the main stats or in a
  right-hand column.
- Contains full sentences detailing growth rates, timeframes, or absence
  of dividends.

### Extraction Strategy (Overview Page Scope)

1. If the overview page includes any clearly labeled **insight box**
  referencing `market cap`, `revenue`, or `dividend` in sentence form:
   - Capture the entire text block as `insights[].raw` elements, tagged
     with a simple type (`market_cap`, `revenue`, `dividend`) based on
     keyword detection.
2. Deeper, structured extraction of these insights (e.g., parsing growth
  rates, dates) is handled by the dedicated `/market-cap/`, `/revenue/`,
  `/dividend/` sections later in **this** document, not in the overview
  scraper itself.


## 8. Normalized Field Map (Overview Page)

This section defines how StockAnalysis overview labels map to normalized
keys in Kuberan. We follow the same pattern used for Finviz: for each
field we store at least:

- `raw`: the literal string from StockAnalysis.
- Optionally `parsed`: a normalized numeric or date.
- Optionally `unit`: e.g., `USD`, `%`, `B` (billions), `M` (millions).

### 8.1 Representative Label → Key Mapping (Overview)

This is not exhaustive, but covers the main labels you can expect on the
overview page. All rows are **optional** in actual data.

| StockAnalysis Label      | Normalized Key         | Example Raw Value | Notes                         |
|--------------------------|------------------------|-------------------|-------------------------------|
| `Price` (header strip)   | `last_price`           | `$482.79`         | Main share price              |
| `Day Change`             | `price_change`         | `-5.91 (-1.21%)`  | May include both abs and %    |
| `Market Cap`             | `market_cap`           | `$89.78B`         | Mirrors `/market-cap/` page   |
| `P/E Ratio`              | `pe_ratio`             | `66.5`            | Trailing P/E                  |
| `EPS (ttm)`              | `eps_ttm`              | `$7.26`           | Trailing twelve-month EPS     |
| `Dividend Yield`         | `dividend_yield`       | `0.54%` or `—`    | May be missing or `—`        |
| `Dividend`               | `dividend_rate`        | `$1.05`           | Annualized dividend, if shown |
| `52-Week Range`          | `range_52w`            | `$350.00 - $500.00` | Full text range string      |
| `Volume`                 | `volume`               | `2.15M`           | Current day volume            |
| `Avg. Volume`            | `avg_volume`           | `1.80M`           | Average daily volume          |
| `Beta`                   | `beta`                 | `1.12`            | Volatility vs market          |
| `Revenue (ttm)`          | `revenue_ttm`          | `$7.05B`          | Mirrors `/revenue/`           |
| `Net Income (ttm)`       | `net_income_ttm`       | `$1.50B`          | Summary net income            |
| `Profit Margin`          | `profit_margin`        | `21.3%`           | Net profit margin             |
| `Operating Margin`       | `operating_margin`     | `25.0%`           | Operating margin              |
| `Return on Equity`       | `roe`                  | `18.7%`           | ROE                           |
| `Return on Assets`       | `roa`                  | `9.5%`            | ROA                           |
| `Shares Outstanding`     | `shares_outstanding`   | `188.4M`          | Could be approximated         |
| `Employees`              | `employees`            | `35,000`          | Headcount                     |
| `Sector`                 | `sector`               | `Technology`      | From classification chips     |
| `Industry`               | `industry`             | `Semiconductors`  | From classification chips     |
| `Country`                | `country`              | `USA`             | From classification chips     |

You should treat these as **best-effort**: some will not appear on every
overview page, and some may move to the dedicated Statistics or Metrics
pages over time.


## 9. Normalized Snapshot Schema (Overview)

We reuse the same conceptual schema as the Finviz snapshot, specialized
here for StockAnalysis as the `source`.

### 9.1 Schema Shape

```jsonc
{
  "source": "stockanalysis",
  "ticker": "NVDA",
  "entity_type": "stock",        // always "stock" for now
  "as_of": "2025-12-14T00:00:00Z", // ISO timestamp when we scraped
  "header": {
    "display_ticker": "NVDA",
    "company_name": "NVIDIA Corporation",
    "exchange": "NASDAQ",
    "listing": "NASDAQ: NVDA"
  },
  "classification": {
    "sector": { "raw": "Technology" },
    "industry": { "raw": "Semiconductors" },
    "country": { "raw": "USA" }
  },
  "fields": {
    "last_price":        { "raw": "$482.79" },
    "price_change":      { "raw": "-5.91 (-1.21%)" },
    "market_cap":        { "raw": "$89.78B" },
    "pe_ratio":          { "raw": "66.5" },
    "eps_ttm":           { "raw": "$7.26" },
    "dividend_yield":    { "raw": "0.54%" },
    "dividend_rate":     { "raw": "$1.05" },
    "range_52w":         { "raw": "$350.00 - $500.00" },
    "volume":            { "raw": "2.15M" },
    "avg_volume":        { "raw": "1.80M" },
    "beta":              { "raw": "1.12" },
    "revenue_ttm":       { "raw": "$7.05B" },
    "net_income_ttm":    { "raw": "$1.50B" },
    "profit_margin":     { "raw": "21.3%" },
    "operating_margin":  { "raw": "25.0%" },
    "roe":               { "raw": "18.7%" },
    "roa":               { "raw": "9.5%" },
    "shares_outstanding":{ "raw": "188.4M" },
    "employees":         { "raw": "35,000" }
  },
  "description": {
    "company_profile": {
      "raw": "NVIDIA Corporation provides graphics processing units (GPUs) and related software and hardware solutions for gaming, data center, and automotive markets..."
    }
  },
  "insights": [
    {
      "type": "market_cap",
      "raw": "NVIDIA has a market cap or net worth of $89.78 billion as of December 11, 2025. Its market cap has increased by 3.43% in one year."
    },
    {
      "type": "revenue",
      "raw": "In the fiscal year ending October 31, 2025, NVIDIA had annual revenue of $7.05B with 15.12% growth. NVIDIA had revenue of $2.25B in the quarter ending October 31, 2025, with 37.83% growth."
    }
  ]
}
```

### 9.2 Notes on Parsing

- **Optionality**: Any key in `fields` may be absent for a given ticker.
- **Raw-first**: Always store `raw`; `parsed` can be added later as
  post-processing (e.g. convert `$89.78B` → numeric value in USD).
- **Units**: If you parse values, record units (`USD`, `%`, `B`, `M`) so
  downstream analytics can treat them correctly.
- **Deduplication**: Many of these values are also present on
  `/statistics/`, `/revenue/`, etc. Overview extraction should *not*
  overwrite more authoritative data; it simply provides an additional
  StockAnalysis perspective for cross-checking.


## 10. Implementation Guidelines (Overview Scraper)

- Treat StockAnalysis as a **supplemental provider** for overview data.
  MASSIVE/YFinance remain the primary sources for prices, market cap,
  and financials.
- Use **label text** as the primary selector for key stats. Avoid relying
  solely on CSS class names or element positions.
- Keep the overview scraper **separate** from dedicated Financials,
  Revenue, Metrics, and other page-specific scrapers. Each set of URLs
  has its own subsection and schema **within this document**.
- When both MASSIVE and StockAnalysis provide the same field (e.g.,
  `market_cap`), store StockAnalysis under the `stockanalysis` source
  namespace and do not try to reconcile in the extractor; reconciliation
  happens in a higher-level standardization layer.
- Log any missing or unexpected labels to help keep this document up to
  date as StockAnalysis evolves its UI.


## 11. Paywalled / Hidden Content (All StockAnalysis Pages)

StockAnalysis exposes different amounts of data depending on whether the
user is anonymous/free or subscribed to StockAnalysis Pro. For Kuberan,
we must:

- **Respect** current access level (no attempts to bypass paywalls).
- **Record** when a given cell/field is hidden or replaced with
  "Upgrade" / similar text.
- **Document** where additional, paywalled data exists so we can
  programmatically backfill older history after we upgrade.

### 11.1 General Free vs Pro Behaviors

Common free-tier behaviors observed on StockAnalysis:

- Some tables (especially deep history) include a catch‑all column like
  `2016 – 2020` where every cell is rendered as `Upgrade`. Clicking it
  leads to a signup/upgrade flow.
- For long time series (many quarters or many years), only the most
  recent subset of columns is visible by default; older columns either
  collapse behind `+ N more` or require Pro. In scraped HTML, these
  hidden columns may be entirely absent or rendered as `Upgrade`.
- Narrative insights (e.g., "NVIDIA had revenue of $187.14B ttm...")
  are generally visible on the free tier and **should be scraped**.

When a value is hidden or replaced by an upgrade prompt:

- Store a cell-level flag, e.g.: `{ "raw": "Upgrade", "paywalled": true }`.
- Do **not** attempt to infer or reconstruct the numeric value.
- At the page level, record a simple summary flag such as
  `"has_paywalled_history": true` to help downstream backfill logic.

> Finviz behaves similarly with its **Elite** tier (for example, older
> intraday candles and some advanced screens). Paywalled Finviz fields
> are documented in `FINVIZ_QUOTE_PAGE_STRUCTURE.md`. For StockAnalysis,
> the following sections call out the main paywalled areas we care about.


## 12. Financials Pages (Income Statement – Annual & Quarterly)

### 12.1 URLs

- Annual income statement:
  - `https://stockanalysis.com/stocks/{TICKER}/financials/`
- Quarterly income statement (same table structure, more columns):
  - `https://stockanalysis.com/stocks/{TICKER}/financials/?p=quarterly`

For NVDA as of 2025‑10‑26, the page title is **"NVIDIA Income Statement"**
with the note:

- `Financials in millions USD. Fiscal year is February - January.`

### 12.2 Layout

Both annual and quarterly pages share the same basic layout:

- A heading (`{Company} Income Statement`).
- An explanatory line about units and fiscal year.
- A **wide table** where:
  - **Rows** = metrics (e.g. `Revenue`, `Revenue Growth (YoY)`,
    `Cost of Revenue`, `Gross Profit`, `Selling, General & Admin`,
    `Research & Development`, `Operating Income`, `Net Income`,
    `EPS (Diluted)`, `Free Cash Flow`, `Margins`, `EBITDA`, etc.).
  - **Columns** = periods.

Annual example (NVDA):

- Header row: `Fiscal Year | TTM | FY 2025 | FY 2024 | FY 2023 | FY 2022 |
  FY 2021 | 2016 - 2020`.
- Second header row (period endings): `Oct '25 Oct 26, 2025`,
  `Jan '25 Jan 26, 2025`, etc.
- Subsequent rows provide values per fiscal year and a last column where
  each cell is `Upgrade` for the historical bundle `2016–2020`.

Quarterly example (NVDA):

- Header row: `Fiscal Quarter | Q3 2026 | Q2 2026 | Q1 2026 | Q4 2025 |
  ... | +20 Quarters` (exact labels can vary but pattern is the same).
- Row vocabulary is nearly identical to the annual table, but with
  quarter‑specific values.

### 12.3 Paywalled / Hidden Data

- The **`2016 – 2020`** column on the annual income statement is
  entirely paywalled; each cell is rendered as `Upgrade` and links to a
  Pro signup page.
- In quarterly view, **older quarters** may be hidden behind
  pagination/"+N more quarters" or similar. On free tier, HTML for those
  columns either does not exist or is only accessible after an upgrade.

Scraper behavior:

- For any cell whose visible text is `Upgrade`:
  - Store `{ "raw": "Upgrade", "paywalled": true }`.
  - Do not set a parsed numeric value.
- For visible numeric cells:
  - Store `{ "raw": "187,142", "unit_hint": "millions_usd" }`.
  - Parsing to an absolute USD amount can be done later by multiplying
    by 1e6.
- At the table level, set:
  - `financials_annual.has_paywalled_history = true` when any row
    contains a paywalled column (e.g. `2016–2020`).
  - Similarly for `financials_quarterly.has_paywalled_history` if
    older quarters are missing or show `Upgrade`.

This lets us:

- Ingest all **visible** rows/columns today, and
- Detect where we can backfill from Pro later without changing the
  scraping contract.

### 12.4 Representative Label → Key Mapping (Financials)

For the income statement tables, use the row label as the basis for the
normalized key. Representative mappings:

| Row Label                         | Normalized Key                 |
|----------------------------------|---------------------------------|
| `Revenue`                        | `revenue`                      |
| `Revenue Growth (YoY)`           | `revenue_growth_yoy`           |
| `Cost of Revenue`                | `cost_of_revenue`              |
| `Gross Profit`                   | `gross_profit`                 |
| `Selling, General & Admin`       | `selling_general_admin`        |
| `Research & Development`         | `research_and_development`     |
| `Operating Expenses`             | `operating_expenses`           |
| `Operating Income`               | `operating_income`             |
| `Interest Expense`               | `interest_expense`             |
| `Interest & Investment Income`   | `interest_and_investment_income` |
| `Other Non Operating Income (Expenses)` | `other_non_operating_income_expenses` |
| `EBT Excluding Unusual Items`    | `ebt_excl_unusual`             |
| `Merger & Restructuring Charges` | `merger_and_restructuring_charges` |
| `Gain (Loss) on Sale of Investments` | `gain_loss_on_investments`  |
| `Pretax Income`                  | `pretax_income`                |
| `Income Tax Expense`             | `income_tax_expense`           |
| `Net Income`                     | `net_income`                   |
| `Net Income to Common`           | `net_income_to_common`         |
| `Net Income Growth`              | `net_income_growth`            |
| `Shares Outstanding (Basic)`     | `shares_out_basic`             |
| `Shares Outstanding (Diluted)`   | `shares_out_diluted`           |
| `Shares Change (YoY)`            | `shares_change_yoy`            |
| `EPS (Basic)`                    | `eps_basic`                    |
| `EPS (Diluted)`                  | `eps_diluted`                  |
| `EPS Growth`                     | `eps_growth`                   |
| `Free Cash Flow`                 | `free_cash_flow`               |
| `Free Cash Flow Per Share`       | `free_cash_flow_per_share`     |
| `Dividend Per Share`             | `dividend_per_share`           |
| `Dividend Growth`                | `dividend_growth`              |
| `Gross Margin`                   | `gross_margin`                 |
| `Operating Margin`               | `operating_margin`             |
| `Profit Margin`                  | `profit_margin`                |
| `Free Cash Flow Margin`          | `free_cash_flow_margin`        |
| `EBITDA`                         | `ebitda`                       |
| `EBITDA Margin`                  | `ebitda_margin`                |
| `D&A For EBITDA`                 | `depreciation_and_amortization_for_ebitda` |
| `EBIT`                           | `ebit`                         |
| `EBIT Margin`                    | `ebit_margin`                  |
| `Effective Tax Rate`             | `effective_tax_rate`           |

Unlisted rows should default to `snake_case(label)` as the key.

### 12.5 Snapshot Shape (Conceptual)

For both annual and quarterly financials, a conceptual shape:

```jsonc
"financials_annual": {
  "unit": "millions_usd",
  "fiscal_year_end_month": 1,        // January, for NVDA
  "rows": [
    {
      "label": "Revenue",
      "key": "revenue",
      "values": {
        "TTM":        { "raw": "187,142" },
        "FY 2025":    { "raw": "130,497" },
        "FY 2024":    { "raw": "60,922" },
        "FY 2023":    { "raw": "26,974" },
        "FY 2022":    { "raw": "26,914" },
        "FY 2021":    { "raw": "16,675" },
        "2016-2020":  { "raw": "Upgrade", "paywalled": true }
      }
    }
    // ... more rows
  ],
  "has_paywalled_history": true
}
```

Quarterly financials mirror this shape but use quarter labels like
`"Q3 2026"`, `"Q2 2026"`, etc.


## 13. Statistics Page

### 13.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/statistics/`

### 13.2 Layout

The Statistics page is a **stack of labeled sections**, each containing
2‑column label/value tables and sometimes a short narrative at the top.
Representative sections for NVDA:

- **Total Valuation**
  - `Market Cap`, `Enterprise Value`.
- **Important Dates**
  - `Earnings Date`, `Ex-Dividend Date`.
- **Share Statistics**
  - `Current Share Class`, `Shares Outstanding`, `Shares Change (YoY)`,
    `Shares Change (QoQ)`, `Owned by Insiders (%)`,
    `Owned by Institutions (%)`, `Float`.
- **Valuation Ratios**
  - `PE Ratio`, `Forward PE`, `PS Ratio`, `Forward PS`, `PB Ratio`,
    `P/TBV Ratio`, `P/FCF Ratio`, `P/OCF Ratio`, `PEG Ratio`.
- **Enterprise Valuation**
  - `EV / Earnings`, `EV / Sales`, `EV / EBITDA`, `EV / EBIT`,
    `EV / FCF`.
- **Financial Position**
  - `Current Ratio`, `Quick Ratio`, `Debt / Equity`, `Debt / EBITDA`,
    `Debt / FCF`, `Interest Coverage`.
- **Financial Efficiency**
  - `Return on Equity (ROE)`, `Return on Assets (ROA)`,
    `Return on Invested Capital (ROIC)`, `Return on Capital Employed
    (ROCE)`, `Revenue Per Employee`, `Profits Per Employee`,
    `Employee Count`, `Asset Turnover`, `Inventory Turnover`.
- **Taxes**
  - `Income Tax`, `Effective Tax Rate`.
- **Stock Price Statistics**
  - `Beta (5Y)`, `52-Week Price Change`, `50-Day Moving Average`,
    `200-Day Moving Average`, `RSI`, `Average Volume (20 Days)`.
- **Short Selling Information**
  - `Short Interest`, `Short Previous Month`,
    `Short % of Shares Out`, `Short % of Float`,
    `Short Ratio (days to cover)`.
- **Income Statement (TTM)**
  - `Revenue`, `Gross Profit`, `Operating Income`, `Pretax Income`,
    `Net Income`, `EBITDA`, `EBIT`, `EPS`.
- **Balance Sheet (snapshot)**
  - `Cash & Cash Equivalents`, `Total Debt`, `Net Cash`,
    `Net Cash Per Share`, `Equity`, `Book Value Per Share`,
    `Working Capital`.
- **Cash Flow**
  - `Operating Cash Flow`, `Capital Expenditures`, `Free Cash Flow`,
    `FCF Per Share`.
- **Margins**
  - `Gross Margin`, `Operating Margin`, `Pretax Margin`, `Profit Margin`,
    `EBITDA Margin`, `EBIT Margin`, `FCF Margin`.
- **Dividends & Yields**
  - `Dividend Per Share`, `Dividend Yield`, `Dividend Growth (YoY)`,
    `Years of Dividend Growth`, `Payout Ratio`, `Buyback Yield`,
    `Shareholder Yield`, `Earnings Yield`, `FCF Yield`.
- **Analyst Forecast**
  - `Price Target`, `Price Target Difference`, `Analyst Consensus`,
    `Analyst Count`, `Revenue Growth Forecast (5Y)`,
    `EPS Growth Forecast (5Y)`.
- **Fair Value**
  - `Lynch Fair Value`, `Lynch Upside`, `Graham Number`,
    `Graham Upside` (values may be missing or paywalled).
- **Stock Splits**
  - `Last Split Date`, `Split Type`, `Split Ratio`.
- **Scores**
  - `Altman Z-Score`, `Piotroski F-Score`.

### 13.3 Extraction & Paywalls

- Each section can be modeled as:
  - `section_name` (e.g. `valuation_ratios`),
  - `rows`: list of `{ label, key, value }` objects.
- Use the same label→key strategy as elsewhere (snake_case).
- If any value cell contains `Upgrade` or similar text, treat it as
  `{ "raw": "Upgrade", "paywalled": true }` and set a
  `statistics.has_paywalled_fields = true` flag.
- In free tier, most NVDA statistics are **visible**; we still keep the
  `paywalled` support to future‑proof the implementation.


## 14. Metrics Page (Segments, Geography, Expenses)

### 14.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/metrics/`

### 14.2 Layout

The Metrics page contains several **wide time‑series tables**, typically
with quarter or year end dates as columns and detailed breakdowns as
rows. For NVDA these include at least:

- **Revenue by Segment**
  - Rows like: `Data Center Revenue`, `Data Center Revenue Growth`,
    `Gaming Revenue`, `Gaming Revenue Growth`,
    `Professional Visualization Revenue`,
    `Automotive and Robotics Revenue`,
    `OEM and Other Revenue`, etc.
- **Operating Income by Segment**
  - Rows for `Compute and Networking`, `Compute and Networking Growth`,
    `Graphics`, `Graphics Growth`, `Other`.
- **Revenue by Geography**
  - Rows for `United States`, `United States Growth`, `Taiwan`,
    `Taiwan Growth`, `Singapore`, `Singapore Growth`, `China`,
    `China Growth`, `Other`, `Other Growth`.
- **Operating Expense Breakdown**
  - Rows for `Research and Development`,
    `Research and Development Growth`,
    `Selling, General, and Administrative`,
    `Selling, General, and Administrative Growth`, `Other Expenses`.

Columns are labeled with period end dates (e.g. `Oct 26, 2025`) and/or
short labels like `Q3 2026`.

### 14.3 Paywalled / Hidden Data

- Only a **limited window** of recent periods is typically visible on
  free tier; older periods may be hidden or accessible only to Pro.
- If any cell is rendered as `Upgrade` or similar, store it with
  `paywalled: true` and set `metrics.has_paywalled_history = true`.

### 14.4 Representation

- Use a structure mirroring financials, but grouped by table:
  - `metrics.segment_revenue.rows[...]`, `metrics.segment_operating.rows[...]`,
    `metrics.geography_revenue.rows[...]`, `metrics.operating_expenses.rows[...]`.
- Each row uses `label` + normalized `key` and a mapping of
  `period_label → cell`.


## 15. Revenue Page

### 15.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/revenue/`

### 15.2 Layout

The Revenue page is more narrative and summary‑oriented:

- Top insight paragraph summarizing:
  - Latest quarter revenue + growth %, TTM revenue + YoY growth,
    most recent full‑year revenue + growth.
- Summary metrics/cards (for NVDA):
  - `Revenue (ttm)`, `Revenue Growth`, `P/S Ratio`,
    `Revenue / Employee`, `Employees`, `Market Cap`.
- **Revenue History** table by fiscal year end:
  - Columns like `Fiscal Year End`, `Revenue`, `Change`, `Growth`.
- Explanatory section `Revenue Definition` with a `Full Definition` link.
- A `Related Stocks` table comparing revenue for peers.
- News feed similar to the overview page.

### 15.3 Paywalled / Hidden Data

- For NVDA, recent revenue history and summary stats are visible on free
  tier.
- Deeper history may have rows marked as `Upgrade` or may be truncated;
  handle as in previous sections by marking such cells as `paywalled`.

### 15.4 Representation

- At minimum, store:
  - `revenue_page.summary_cards` – label→value pairs for top metrics.
  - `revenue_page.history` – list of `{ fiscal_year_end, revenue, change,
    growth, paywalled? }`.
  - `revenue_page.insight.raw` – the top narrative paragraph.


## 16. Market Cap Page

### 16.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/market-cap/`

### 16.2 Layout

The Market Cap page is analogous to Revenue:

- Top narrative insight:
  - e.g. `NVIDIA has a market cap or net worth of $4.25 trillion as of
    December 12, 2025. Its market cap has increased by 26.83% in one
    year.`
- Summary cards:
  - `Market Cap`, `Enterprise Value`, `1-Year Change`, `Ranking`,
    `Category`, `Stock Price`.
- **Market Cap History** table:
  - `Date`, `Market Cap`, `% Change`, etc.
- Definition section (`Market Capitalization`) with formula and
  `Full Definition` link.
- Related stocks table showing other large caps.

### 16.3 Paywalled / Hidden Data

- As with revenue, recent history is visible; older history may be
  truncated or paywalled. Treat `Upgrade` cells as `paywalled` and set
  `market_cap_page.has_paywalled_history` accordingly.

### 16.4 Representation

- `market_cap_page.summary_cards` – label→value.
- `market_cap_page.history` – list of `{ date, market_cap, change_pct,
  paywalled? }`.
- `market_cap_page.insight.raw` – full narrative.


## 17. Dividend Page

### 17.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/dividend/`

### 17.2 Layout

The Dividend page focuses on distribution history and yield metrics:

- Top summary for NVDA:
  - `NVIDIA has an annual dividend of $0.04 per share, with a yield of
    0.02%. The dividend is paid every three months and the last
    ex-dividend date was Dec 4, 2025.`
- Summary cards:
  - `Dividend Yield`, `Annual Dividend`, `Ex-Dividend Date`,
    `Payout Frequency`, `Payout Ratio`, `Dividend Growth (1Y)`,
    `Growth Years`, `Buyback Yield`, `Shareholder Yield`.
- **Dividend History** table:
  - Columns: `Ex-Dividend Date`, `Cash Amount`, `Record Date`,
    `Pay Date`, possibly `Change` or `Notes`.
- A `Dividend Definition` section in some cases.

### 17.3 Paywalled / Hidden Data

- For NVDA, recent dividend history is visible on free tier.
- For other tickers, especially long‑lived dividend payers, older rows
  may be collapsed or marked `Upgrade`.
- Treat such rows as `paywalled` and set `dividend_page.has_paywalled_history`.

### 17.4 Representation

- `dividend_page.summary_cards` – label→value.
- `dividend_page.history` – list of dividend events:
  - `{ ex_date, cash_amount, record_date, pay_date, paywalled? }`.
- `dividend_page.insight.raw` – top paragraph.


## 18. Company / Profile Page

### 18.1 URL

- `https://stockanalysis.com/stocks/{TICKER}/company/`

### 18.2 Layout

The Company page aggregates long‑form descriptive and identity
information:

- **Long description** of the business and segments, often several
  paragraphs.
- `NVIDIA Corporation` summary table:
  - `Country`, `Founded`, `IPO Date`, `Industry`, `Sector`,
    `Employees`, `CEO`.
- **Contact details**:
  - Postal address, `Phone`, `Website`.
- **Stock details**:
  - `Ticker Symbol`, `Exchange`, `Stock Type`, `Fiscal Year`,
    `Reporting Currency`, `CIK Code`, `CUSIP Number`, `ISIN Number`,
    `Employer ID`, `SIC Code`.
- **Key Executives** table:
  - Names and titles for CEO, CFO, COO, etc.
- **Latest SEC Filings** table:
  - Recent filings with `Date`, `Type` (10‑Q, 10‑K, 8‑K, 13F, 144),
    `Title`.

### 18.3 Paywalled / Hidden Data

- For NVDA, all of the above appears to be visible on free tier.
- If certain filings or executive details are replaced with `Upgrade` or
  truncated in the future, mark them as `paywalled` at the row level and
  set `company_page.has_paywalled_fields`.

### 18.4 Representation

- `company_page.description.raw` – long description.
- `company_page.summary` – normalized company identity fields.
- `company_page.contact` – address/phone/website.
- `company_page.stock_details` – identification fields (CIK, CUSIP, ISIN,
  SIC, etc.).
- `company_page.executives` – list of `{ name, title }` objects.
- `company_page.sec_filings` – list of
  `{ date, type, title, paywalled? }`.


## 19. Forecast / Analyst Page (Planned)

### 19.1 URL

- The overview and statistics pages reference a **Forecasts** page and
  link to:
  - `https://stockanalysis.com/stocks/{TICKER}/forecast/`

During an earlier exploration, `…/stocks/nvda/forecasts/` returned
`404`, indicating the correct path is likely the singular `forecast/`.

### 19.2 Known / Overlapping Fields

Even without scraping the dedicated forecast page, we already see
forecast‑style data in:

- Overview `Analyst Summary` section:
  - `Analyst rating` (e.g. `Strong Buy`).
  - `12‑month price target` and upside %.
- Statistics `Analyst Forecast` section:
  - `Price Target`, `Price Target Difference`, `Analyst Consensus`,
    `Analyst Count`, `Revenue Growth Forecast (5Y)`,
    `EPS Growth Forecast (5Y)`.

When we later add explicit coverage for `…/forecast/`, we will:

- Reuse these same normalized keys.
- Treat any additional fields (e.g. distribution of targets, low/high
  estimates) as supplemental.
- Mark any rows or charts that are Pro‑only with `paywalled: true`.

Until then, forecast‑like fields should be extracted **only** from the
overview and statistics pages, following the structures already defined
above.
