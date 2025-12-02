# MASSIVE API Reference Endpoints - Complete Guide (Free Tier)

**Last Updated:** December 1, 2025

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Rate Limits](#authentication--rate-limits)
3. [Response Structure & Pagination](#response-structure--pagination)
4. [Stock Reference Endpoints](#stock-reference-endpoints)
   - [All Tickers](#1-all-tickers)
   - [Ticker Overview](#2-ticker-overview)
   - [Ticker Types](#3-ticker-types)
   - [Exchanges](#4-exchanges)
   - [Condition Codes](#5-condition-codes)
   - [Stock Splits](#6-stock-splits)
   - [Dividends](#7-dividends)
   - [Financials (Deprecated)](#8-financials-deprecated)
   - [News](#9-news)
5. [Options Reference Endpoints](#options-reference-endpoints)
   - [All Option Contracts](#10-all-option-contracts)
   - [Option Contract Overview](#11-option-contract-overview)
6. [Kuberan Integration Recommendations](#kuberan-integration-recommendations)

---

## Overview

This guide documents **all 11 reference endpoints** accessible on MASSIVE's **free tier** API plan. Reference endpoints provide foundational metadata about tickers, exchanges, corporate actions, and options contracts - essential building blocks for financial applications.

### What's Included on Free Tier

✅ **Reference Data Endpoints**: Access to all `/v3/reference/` endpoints  
✅ **Historical Corporate Actions**: Splits, dividends  
✅ **Company Fundamentals**: Ticker details, financials (deprecated)  
✅ **Market Structure**: Exchanges, condition codes, ticker types  
✅ **Options Contracts**: Contract listings and specifications  
✅ **Financial News**: News articles with sentiment analysis  

### What Requires Paid Tier

❌ **Real-time/Historical Prices**: Aggregates, snapshots, trades, quotes  
❌ **Technical Indicators**: SMA, EMA, RSI, MACD, etc.  
❌ **Market Status**: Real-time market hours  
❌ **Websocket Streaming**: Real-time data feeds  

---

## Authentication & Rate Limits

### API Key Authentication

All requests require an API key passed as a query parameter or header:

```bash
# Query parameter
https://api.massive.com/v3/reference/tickers?apiKey=YOUR_API_KEY

# Header (recommended)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.massive.com/v3/reference/tickers
```

### Rate Limits (Free Tier)

- **5 calls per minute**
- **300 calls per hour**
- **7,200 calls per day**

**Best Practices**:
- Cache responses aggressively (tickers, exchanges change infrequently)
- Use pagination efficiently (don't repeatedly fetch same data)
- Implement exponential backoff for rate limit errors
- Monitor `request_id` for debugging

---

## Response Structure & Pagination

### Standard Response Format

All endpoints return consistent JSON structure:

```json
{
  "count": 12140,               // Total results available
  "next_url": "https://...",    // Pagination URL (if more results)
  "request_id": "abc123...",    // Request identifier
  "results": [...],             // Array of data objects
  "status": "OK"                // Request status
}
```

### Pagination Pattern

When `next_url` is present, fetch next page:

```python
async def fetch_all_pages(base_url: str):
    all_results = []
    url = base_url
    
    while url:
        response = await fetch(url)
        all_results.extend(response['results'])
        url = response.get('next_url')  # None when no more pages
    
    return all_results
```

---

## Stock Reference Endpoints

### 1. All Tickers

**Endpoint:** `GET /v3/reference/tickers`

**Description:**  
Comprehensive list of all tickers across asset classes (stocks, ETFs, indices, etc.). Supports extensive filtering by ticker symbol, type, market, exchange, CUSIP, CIK, and more.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | No | Case-sensitive ticker symbol (e.g., AAPL) |
| `type` | string | No | Ticker type (CS, ETF, ADRC, etc.) |
| `market` | string | No | Market type (stocks, crypto, fx, otc) |
| `exchange` | string | No | Exchange MIC code (XNAS, XNYS, etc.) |
| `cusip` | string | No | CUSIP identifier |
| `cik` | string | No | CIK number |
| `date` | string | No | Query tickers as of date (YYYY-MM-DD) |
| `search` | string | No | Search by ticker or company name |
| `active` | boolean | No | Filter active/delisted (default: true) |
| `ticker.gte/gt/lte/lt` | string | No | Range filters for ticker symbol |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by (ticker, name, type, etc.) |

**Response Fields:**

```json
{
  "results": [
    {
      "active": true,
      "base_currency_name": "usd",
      "base_currency_symbol": "$",
      "cik": "0000320193",
      "composite_figi": "BBG000B9XRY4",
      "currency_name": "usd",
      "currency_symbol": "$",
      "delisted_utc": null,
      "last_updated_utc": "2025-11-30T00:00:00Z",
      "locale": "us",
      "market": "stocks",
      "name": "Apple Inc.",
      "primary_exchange": "XNAS",
      "share_class_figi": "BBG001S5N8V8",
      "ticker": "AAPL",
      "type": "CS"
    }
  ]
}
```

**Use Cases:**
- **Asset Discovery**: Find tickers matching criteria (e.g., all tech ETFs on NASDAQ)
- **Data Integration**: Sync Kuberan's ticker database with MASSIVE's complete list
- **Watchlist Building**: Search for tickers by company name or sector
- **Application Development**: Populate ticker dropdowns, autocomplete features

**Kuberan Integration:**
- ✅ Use for ticker metadata enrichment (replacing AlphaVantage discovery)
- ✅ Query by `type=CS` for common stocks, `type=ETF` for ETFs
- ✅ Filter `active=true` to exclude delisted tickers
- ✅ Cache results daily (tickers change infrequently)

**Example Request:**
```bash
# Get all active Apple-related tickers
curl "https://api.massive.com/v3/reference/tickers?search=Apple&active=true&limit=100"

# Get all NASDAQ ETFs
curl "https://api.massive.com/v3/reference/tickers?type=ETF&exchange=XNAS&limit=1000"
```

---

### 2. Ticker Overview

**Endpoint:** `GET /v3/reference/tickers/{ticker}`

**Description:**  
Comprehensive company profile for a specific ticker. Returns detailed information including company description, address, branding (logos/icons), financial metrics, identifiers (CIK, FIGI, SIC), and key dates.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Case-sensitive ticker symbol |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | No | Point-in-time lookup (YYYY-MM-DD) |

**Response Fields:**

```json
{
  "results": {
    "active": true,
    "address": {
      "address1": "One Apple Park Way",
      "city": "Cupertino",
      "postal_code": "95014",
      "state": "CA"
    },
    "branding": {
      "icon_url": "https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-01-10_icon.png",
      "logo_url": "https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-01-10_logo.svg"
    },
    "cik": "0000320193",
    "composite_figi": "BBG000B9XRY4",
    "currency_name": "usd",
    "delisted_utc": null,
    "description": "Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.",
    "homepage_url": "https://www.apple.com",
    "list_date": "1980-12-12",
    "locale": "us",
    "market": "stocks",
    "market_cap": 2770000000000,
    "name": "Apple Inc.",
    "phone_number": "+1 408 996-1010",
    "primary_exchange": "XNAS",
    "share_class_figi": "BBG001S5N8V8",
    "share_class_shares_outstanding": 15204100000,
    "sic_code": "3571",
    "sic_description": "ELECTRONIC COMPUTERS",
    "ticker": "AAPL",
    "ticker_root": "AAPL",
    "total_employees": 154000,
    "type": "CS",
    "weighted_shares_outstanding": 15204100000
  }
}
```

**Use Cases:**
- **Company Research**: Get detailed company information for investment analysis
- **Due Diligence**: Access SEC identifiers, SIC codes, employee counts
- **UI Enhancement**: Display company logos, descriptions in applications
- **Data Enrichment**: Populate ticker metadata in databases

**Kuberan Integration:**
- ✅ **PRIMARY USE**: Use for foundation metadata enrichment (replacing Polygon.io)
- ✅ Collect CIK, FIGI, SIC codes, branding URLs
- ✅ Store in `CompanyOverview` model (existing structure compatible)
- ✅ Schedule background job: Enrich 5-10 tickers per minute (respects rate limits)
- ✅ Cache results: 30-90 days (company info changes slowly)

**Example Request:**
```bash
# Get Apple Inc. overview
curl "https://api.massive.com/v3/reference/tickers/AAPL"

# Get historical overview (as of specific date)
curl "https://api.massive.com/v3/reference/tickers/AAPL?date=2020-01-01"
```

---

### 3. Ticker Types

**Endpoint:** `GET /v3/reference/tickers/types`

**Description:**  
Complete list of ticker type classifications used by MASSIVE. Each type includes a code (CS, ETF, ADRC), description, asset class, and locale. Essential for understanding ticker categorization.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_class` | string | No | Filter by asset class (stocks, options, crypto, fx, indices) |
| `locale` | string | No | Filter by locale (us, global) |

**Response Fields:**

```json
{
  "results": [
    {
      "asset_class": "stocks",
      "code": "CS",
      "description": "Common Stock",
      "locale": "us"
    },
    {
      "asset_class": "stocks",
      "code": "ETF",
      "description": "Exchange Traded Fund",
      "locale": "us"
    },
    {
      "asset_class": "stocks",
      "code": "ADRC",
      "description": "American Depository Receipt Common",
      "locale": "us"
    }
  ]
}
```

**Common Ticker Types:**
- **CS**: Common Stock
- **ETF**: Exchange Traded Fund
- **ADRC**: American Depository Receipt Common
- **PFD**: Preferred Stock
- **WARRANT**: Warrant
- **RIGHT**: Rights
- **UNIT**: Unit
- **FUND**: Mutual Fund
- **INDEX**: Index
- **ETN**: Exchange Traded Note

**Use Cases:**
- **Data Classification**: Categorize tickers in Kuberan database
- **Filtering**: Enable users to filter by security type
- **Educational Reference**: Display type descriptions in UI
- **System Integration**: Map MASSIVE types to internal taxonomy

**Kuberan Integration:**
- ✅ Fetch once and cache permanently (rarely changes)
- ✅ Use for dropdown filters in UI (e.g., "Show only ETFs")
- ✅ Store in configuration collection for reference
- ✅ Validate ticker types during metadata enrichment

**Example Request:**
```bash
# Get all ticker types
curl "https://api.massive.com/v3/reference/tickers/types"

# Get only stock types
curl "https://api.massive.com/v3/reference/tickers/types?asset_class=stocks"
```

---

### 4. Exchanges

**Endpoint:** `GET /v3/reference/exchanges`

**Description:**  
Directory of all exchanges supported by MASSIVE, including exchange names, acronyms, MIC codes (ISO 10383), operating MICs, participant IDs, asset classes, and URLs. Essential for understanding market structure.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_class` | string | No | Filter by asset class (stocks, options, crypto, fx, futures) |
| `locale` | string | No | Filter by locale (us, global) |

**Response Fields:**

```json
{
  "results": [
    {
      "acronym": "AMEX",
      "asset_class": "stocks",
      "id": 1,
      "locale": "us",
      "mic": "XASE",
      "name": "NYSE American (AMEX)",
      "operating_mic": "XNYS",
      "participant_id": "A",
      "type": "exchange",
      "url": "https://www.nyse.com/markets/nyse-american"
    },
    {
      "acronym": "NASDAQ",
      "asset_class": "stocks",
      "id": 2,
      "locale": "us",
      "mic": "XNAS",
      "name": "NASDAQ Stock Market",
      "operating_mic": "XNAS",
      "participant_id": "Q",
      "type": "exchange",
      "url": "https://www.nasdaq.com"
    }
  ]
}
```

**Key Fields Explained:**
- **MIC**: Market Identifier Code (ISO 10383 standard)
- **Operating MIC**: Parent entity MIC (e.g., NYSE owns ARCA)
- **Participant ID**: SIP (Securities Information Processor) identifier
- **Type**: exchange, TRF (Trade Reporting Facility), SIP

**Use Cases:**
- **Data Mapping**: Convert exchange codes to human-readable names
- **Market Coverage Analysis**: Identify which exchanges are supported
- **Regulatory Compliance**: Use MIC codes for regulatory reporting
- **Application Development**: Populate exchange filters, dropdowns

**Kuberan Integration:**
- ✅ Fetch once and cache permanently (rarely changes)
- ✅ Store in `exchanges` collection for reference
- ✅ Use for exchange name lookups (XNAS → "NASDAQ")
- ✅ Display exchange information in ticker details UI

**Example Request:**
```bash
# Get all exchanges
curl "https://api.massive.com/v3/reference/exchanges"

# Get only US stock exchanges
curl "https://api.massive.com/v3/reference/exchanges?asset_class=stocks&locale=us"
```

---

### 5. Condition Codes

**Endpoint:** `GET /v3/reference/conditions`

**Description:**  
Unified mapping of trade and quote condition codes across SIPs (CTA, UTP, OPRA). Each condition includes abbreviation, description, SIP mappings, and update rules (whether it affects OHLC, volume). Critical for correctly interpreting market data.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_class` | string | No | Filter by asset class (stocks, options, indices, fx, crypto) |
| `data_type` | string | No | Filter by data type (trade, quote, etc.) |
| `id` | integer | No | Filter by condition ID |
| `sip` | string | No | Filter by SIP (CTA, UTP, OPRA) |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "abbreviation": "B",
      "asset_class": "stocks",
      "data_types": ["trade"],
      "description": "Average Price Trade",
      "exchange": null,
      "id": 2,
      "legacy": false,
      "name": "Average Price Trade",
      "sip_mapping": {
        "CTA": "B",
        "UTP": "W"
      },
      "type": "sale_condition",
      "update_rules": {
        "consolidated": {
          "updates_high_low": false,
          "updates_open_close": false,
          "updates_volume": true
        },
        "market_center": {
          "updates_high_low": false,
          "updates_open_close": false,
          "updates_volume": true
        }
      }
    }
  ]
}
```

**Condition Types:**
- **sale_condition**: Trade execution conditions
- **quote_condition**: Quote status indicators
- **sip_generated_flag**: SIP-generated flags
- **financial_status_indicator**: Company financial status

**Use Cases:**
- **Data Interpretation**: Understand what trade/quote conditions mean
- **Unified Mapping**: Convert SIP-specific codes to standard definitions
- **Filtering & Analysis**: Exclude/include trades based on conditions
- **Algorithmic Trading**: Adjust strategies based on condition rules

**Kuberan Integration:**
- ✅ Fetch once and cache permanently (rarely changes)
- ⚠️ Not immediately needed (only relevant when processing trades/quotes)
- 🔮 Future use: When integrating real-time market data (paid tier)

**Example Request:**
```bash
# Get all condition codes
curl "https://api.massive.com/v3/reference/conditions?limit=1000"

# Get only trade conditions for stocks
curl "https://api.massive.com/v3/reference/conditions?asset_class=stocks&data_type=trade"
```

---

### 6. Stock Splits

**Endpoint:** `GET /v3/reference/splits`

**Description:**  
Historical record of stock split events, including execution dates, split ratios, and ticker symbols. Essential for adjusting historical price data and understanding share dilution/consolidation.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | No | Filter by ticker symbol |
| `execution_date` | string | No | Filter by execution date (YYYY-MM-DD) |
| `reverse_split` | boolean | No | Filter for reverse splits (split_from > split_to) |
| `ticker.gte/gt/lte/lt` | string | No | Range filters for ticker |
| `execution_date.gte/gt/lte/lt` | string | No | Range filters for date |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "execution_date": "2020-08-31",
      "id": "e3c5ab9c1a3d4e6f9b2c8d7f1e3a4b5c",
      "split_from": 1,
      "split_to": 4,
      "ticker": "AAPL"
    },
    {
      "execution_date": "2005-02-28",
      "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "split_from": 1,
      "split_to": 2,
      "ticker": "AAPL"
    }
  ]
}
```

**Split Ratio Interpretation:**
- **Forward Split**: `split_to > split_from` (e.g., 2-for-1: split_to=2, split_from=1)
- **Reverse Split**: `split_from > split_to` (e.g., 1-for-5: split_to=1, split_from=5)
- **Adjustment Factor**: `split_to / split_from`

**Use Cases:**
- **Historical Price Adjustment**: Adjust prices before split execution
- **Data Consistency**: Ensure price comparisons are split-adjusted
- **Financial Modeling**: Account for share count changes
- **Investment Analysis**: Understand company capital structure changes

**Kuberan Integration:**
- ✅ Fetch periodically (weekly) and store in database
- ✅ Use to adjust historical price data in `StockPrice` collection
- ✅ Display split events in stock history timeline
- ✅ Alert users when tracked stocks announce splits

**Example Request:**
```bash
# Get all Apple splits
curl "https://api.massive.com/v3/reference/splits?ticker=AAPL"

# Get splits in 2020
curl "https://api.massive.com/v3/reference/splits?execution_date.gte=2020-01-01&execution_date.lt=2021-01-01"

# Get only reverse splits
curl "https://api.massive.com/v3/reference/splits?reverse_split=true"
```

---

### 7. Dividends

**Endpoint:** `GET /v3/reference/dividends`

**Description:**  
Comprehensive dividend history including declaration, ex-dividend, record, and pay dates, along with cash amounts, frequency, and dividend types. Essential for income analysis and total return calculations.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | No | Filter by ticker symbol |
| `ex_dividend_date` | string | No | Filter by ex-dividend date (YYYY-MM-DD) |
| `record_date` | string | No | Filter by record date (YYYY-MM-DD) |
| `declaration_date` | string | No | Filter by declaration date (YYYY-MM-DD) |
| `pay_date` | string | No | Filter by pay date (YYYY-MM-DD) |
| `frequency` | integer | No | Filter by payment frequency (0=one-time, 1=annual, 2=bi-annual, 4=quarterly, 12=monthly) |
| `cash_amount` | number | No | Filter by dividend amount |
| `dividend_type` | string | No | Filter by type (CD=consistent, SC=special cash, LT=long-term cap gain, ST=short-term cap gain) |
| Range filters | various | No | `ticker.gte/gt/lte/lt`, `ex_dividend_date.gte/gt/lte/lt`, `record_date.gte/gt/lte/lt`, `declaration_date.gte/gt/lte/lt`, `pay_date.gte/gt/lte/lt`, `cash_amount.gte/gt/lte/lt` |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "cash_amount": 0.22,
      "currency": "USD",
      "declaration_date": "2021-10-28",
      "dividend_type": "CD",
      "ex_dividend_date": "2021-11-05",
      "frequency": 4,
      "id": "E8e3c4f794613e9205e2f178a36c53fcc57cdabb55e1988c87b33f9e52e221444",
      "pay_date": "2021-11-11",
      "record_date": "2021-11-08",
      "ticker": "AAPL"
    }
  ]
}
```

**Dividend Types:**
- **CD**: Consistent Dividend (regular scheduled payments)
- **SC**: Special Cash (one-time, infrequent payments)
- **LT**: Long-Term Capital Gain Distribution
- **ST**: Short-Term Capital Gain Distribution

**Frequency Codes:**
- **0**: One-time payment
- **1**: Annual (once per year)
- **2**: Bi-annual (twice per year)
- **4**: Quarterly (4 times per year)
- **12**: Monthly
- **24**: Bi-monthly
- **52**: Weekly

**Key Dates Explained:**
- **Declaration Date**: When board announces dividend
- **Ex-Dividend Date**: First trading day without dividend entitlement
- **Record Date**: Date shareholders must be on record to receive dividend
- **Pay Date**: When dividend is actually paid

**Use Cases:**
- **Income Analysis**: Calculate dividend yield and income projections
- **Total Return Calculations**: Account for dividend income in returns
- **Dividend Strategies**: Identify high-yield, consistent dividend payers
- **Tax Planning**: Distinguish between dividends and capital gains

**Kuberan Integration:**
- ✅ Fetch periodically (monthly) and store in database
- ✅ Display dividend history in stock detail pages
- ✅ Calculate dividend yield: `(annual_dividends / current_price) * 100`
- ✅ Alert users of upcoming ex-dividend dates for holdings
- ✅ Aggregate dividend income across portfolio

**Example Request:**
```bash
# Get Apple dividends
curl "https://api.massive.com/v3/reference/dividends?ticker=AAPL"

# Get quarterly dividends only
curl "https://api.massive.com/v3/reference/dividends?frequency=4&limit=100"

# Get dividends paid in 2021
curl "https://api.massive.com/v3/reference/dividends?pay_date.gte=2021-01-01&pay_date.lt=2022-01-01"
```

---

### 8. Financials (Deprecated)

**Endpoint:** `GET /vX/reference/financials`

**Description:**  
⚠️ **DEPRECATED** - Historical financial data derived from SEC filings (XBRL). Includes income statements, balance sheets, cash flow statements, and comprehensive income. While still accessible, MASSIVE recommends migrating to newer financial data endpoints (if available on paid tiers).

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | No | Filter by ticker symbol |
| `cik` | string | No | Filter by CIK number |
| `company_name` | string | No | Filter by company name |
| `sic` | string | No | Filter by SIC code |
| `filing_date` | string | No | Filter by filing date (YYYY-MM-DD) |
| `period_of_report_date` | string | No | Filter by report period (YYYY-MM-DD) |
| `timeframe` | string | No | Filter by timeframe (annual, quarterly, ttm) |
| `include_sources` | boolean | No | Include xpath and formula attributes (default: false) |
| `company_name.search` | string | No | Search by company name |
| Range filters | various | No | `filing_date.gte/gt/lte/lt`, `period_of_report_date.gte/gt/lte/lt` |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 100, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "acceptance_datetime": "20220504163045",
      "cik": "0001650729",
      "company_name": "SiteOne Landscape Supply, Inc.",
      "end_date": "20220403",
      "filing_date": "2022-05-04",
      "fiscal_period": "Q1",
      "fiscal_year": "2022",
      "sic": "5261",
      "start_date": "20220103",
      "ticker": ["SITE"],
      "timeframe": "quarterly",
      "financials": {
        "balance_sheet": {
          "assets": {"value": 2407400000, "unit": "USD", "label": "Assets"},
          "liabilities": {"value": 1308200000, "unit": "USD", "label": "Liabilities"},
          "equity": {"value": 1099200000, "unit": "USD", "label": "Equity"}
        },
        "income_statement": {
          "revenues": {"value": 805300000, "unit": "USD", "label": "Revenues"},
          "net_income_loss": {"value": 32300000, "unit": "USD", "label": "Net Income/Loss"},
          "basic_earnings_per_share": {"value": 0.72, "unit": "USD / shares"}
        },
        "cash_flow_statement": {
          "net_cash_flow_from_operating_activities": {"value": -118300000, "unit": "USD"},
          "net_cash_flow_from_investing_activities": {"value": -41000000, "unit": "USD"},
          "net_cash_flow_from_financing_activities": {"value": 150600000, "unit": "USD"}
        }
      },
      "source_filing_url": "https://api.massive.com/v1/reference/sec/filings/0001650729-22-000010"
    }
  ]
}
```

**Financial Statement Components:**
- **Balance Sheet**: Assets, liabilities, equity, current/noncurrent breakdowns
- **Income Statement**: Revenues, expenses, net income, EPS
- **Cash Flow Statement**: Operating, investing, financing activities
- **Comprehensive Income**: Other comprehensive income items

**Use Cases:**
- **Fundamental Analysis**: Evaluate company financial health
- **Trend Identification**: Track financial metrics over time
- **Cross-Company Comparisons**: Compare financials across peers
- **Research & Modeling**: Build financial models, DCF valuations

**Kuberan Integration:**
- ⚠️ **USE WITH CAUTION**: Deprecated endpoint, may be removed
- 🔮 Consider alternative: Wait for MASSIVE to release replacement
- ⚠️ If using: Cache results aggressively (quarterly updates only)
- 📊 Limitation: Max 100 results per request (vs 1000 for other endpoints)

**Example Request:**
```bash
# Get Apple's financials
curl "https://api.massive.com/vX/reference/financials?ticker=AAPL&limit=10"

# Get annual financials for 2022
curl "https://api.massive.com/vX/reference/financials?timeframe=annual&filing_date.gte=2022-01-01&filing_date.lt=2023-01-01"
```

---

### 9. News

**Endpoint:** `GET /v2/reference/news`

**Description:**  
Recent financial news articles with summaries, publisher details, associated tickers, and sentiment analysis. Articles include metadata like keywords, author, images, and insights with sentiment reasoning. Perfect for market sentiment analysis and staying informed on company developments.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | No | Filter by ticker symbol (case-sensitive) |
| `published_utc` | string | No | Filter by publication date (YYYY-MM-DD) |
| Range filters | various | No | `ticker.gte/gt/lte/lt`, `published_utc.gte/gt/lte/lt` |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "id": "8ec638777ca03b553ae516761c2a22ba2fdd2f37befae3ab6fdab74e9e5193eb",
      "publisher": {
        "name": "Investing.com",
        "homepage_url": "https://www.investing.com/",
        "logo_url": "https://s3.massive.com/public/assets/news/logos/investing.png",
        "favicon_url": "https://s3.massive.com/public/assets/news/favicons/investing.ico"
      },
      "title": "Markets are underestimating Fed cuts: UBS By Investing.com - Investing.com UK",
      "author": "Sam Boughedda",
      "published_utc": "2024-06-24T18:33:53Z",
      "article_url": "https://uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968",
      "amp_url": "https://m.uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968?ampMode=1",
      "image_url": "https://i-invdn-com.investing.com/news/LYNXNPEC4I0AL_L.jpg",
      "description": "UBS analysts warn that markets are underestimating the extent of future interest rate cuts by the Federal Reserve...",
      "tickers": ["UBS"],
      "keywords": ["Federal Reserve", "interest rates", "economic data"],
      "insights": [
        {
          "ticker": "UBS",
          "sentiment": "positive",
          "sentiment_reasoning": "UBS analysts are providing a bullish outlook on the extent of future Federal Reserve rate cuts..."
        }
      ]
    }
  ]
}
```

**Publisher Information:**
- **Name**: Publisher name (e.g., Bloomberg, Reuters, Investing.com)
- **Homepage URL**: Publisher website
- **Logo URL**: Publisher logo image
- **Favicon URL**: Publisher favicon

**Sentiment Analysis:**
- **Sentiment**: positive, negative, neutral
- **Sentiment Reasoning**: Explanation of sentiment classification
- **Per-Ticker Insights**: Sentiment can vary by ticker in multi-ticker articles

**Use Cases:**
- **Market Sentiment Analysis**: Track news sentiment for portfolio holdings
- **Investment Research**: Stay informed on company developments
- **Automated Monitoring**: Alert on negative news for tracked tickers
- **Portfolio Strategy**: Adjust positions based on news flow

**Kuberan Integration:**
- ✅ Fetch news for tracked tickers (daily)
- ✅ Display recent news in stock detail pages
- ✅ Aggregate sentiment scores across articles
- ✅ Alert users on negative sentiment spikes
- ✅ Filter by date range for historical news analysis

**Example Request:**
```bash
# Get Apple news
curl "https://api.massive.com/v2/reference/news?ticker=AAPL&limit=50"

# Get news from last 7 days
curl "https://api.massive.com/v2/reference/news?published_utc.gte=2024-11-24&limit=100"

# Get news for multiple tickers (repeat ticker param)
curl "https://api.massive.com/v2/reference/news?ticker=AAPL&ticker=MSFT&ticker=GOOGL"
```

---

## Options Reference Endpoints

### 10. All Option Contracts

**Endpoint:** `GET /v3/reference/options/contracts`

**Description:**  
Comprehensive index of all options contracts (active and expired) across all underlying tickers. Returns contract specifications including type (call/put), exercise style, expiration date, strike price, shares per contract, and additional underlyings (if applicable due to corporate actions).

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `underlying_ticker` | string | No | Filter by underlying stock ticker |
| `ticker` | string | No | ⚠️ **DEPRECATED** - Use Options Contract Overview endpoint instead |
| `contract_type` | string | No | Filter by type (call, put, other) |
| `expiration_date` | string | No | Filter by expiration (YYYY-MM-DD) |
| `as_of` | string | No | Point-in-time lookup (YYYY-MM-DD, default: today) |
| `strike_price` | number | No | Filter by strike price |
| `expired` | boolean | No | Include expired contracts (default: false) |
| Range filters | various | No | `underlying_ticker.gte/gt/lte/lt`, `expiration_date.gte/gt/lte/lt`, `strike_price.gte/gt/lte/lt` |
| `order` | string | No | Sort order (asc/desc) |
| `limit` | integer | No | Results per page (max 1000, default 10) |
| `sort` | string | No | Field to sort by |

**Response Fields:**

```json
{
  "results": [
    {
      "ticker": "O:AAPL211119C00085000",
      "underlying_ticker": "AAPL",
      "contract_type": "call",
      "exercise_style": "american",
      "expiration_date": "2021-11-19",
      "strike_price": 85,
      "shares_per_contract": 100,
      "primary_exchange": "BATO",
      "cfi": "OCASPS",
      "correction": 0,
      "additional_underlyings": [
        {
          "type": "equity",
          "underlying": "VMW",
          "amount": 44
        },
        {
          "type": "currency",
          "underlying": "USD",
          "amount": 6.53
        }
      ]
    }
  ]
}
```

**Exercise Styles:**
- **American**: Can be exercised any time before expiration
- **European**: Can only be exercised at expiration
- **Bermudan**: Can be exercised on specific dates before expiration

**Additional Underlyings:**
- Present when corporate actions (splits, mergers, spinoffs) affect contract deliverables
- See [OCC documentation](https://www.optionseducation.org/referencelibrary/faq/splits-mergers-spinoffs-bankruptcies) for examples

**CFI Code:**
- 6-letter code following ISO 10962 standard
- Classifies financial instruments
- Example: "OCASPS" = Option, Call, American Style, Physical Settlement

**Use Cases:**
- **Market Availability Analysis**: Find all available options for a stock
- **Strategy Development**: Identify contracts matching strategy criteria
- **Research & Modeling**: Analyze option chains, implied volatility surfaces
- **Contract Exploration**: Discover options across strikes and expirations

**Kuberan Integration:**
- 🔮 **FUTURE USE**: When building options trading features
- ⚠️ Free tier access: Reference data only (no pricing)
- ✅ Use to populate option chain dropdowns (strikes, expirations)
- ✅ Identify available contracts for covered call/protective put strategies

**Example Request:**
```bash
# Get all Apple option contracts
curl "https://api.massive.com/v3/reference/options/contracts?underlying_ticker=AAPL&limit=1000"

# Get call options expiring in December 2024
curl "https://api.massive.com/v3/reference/options/contracts?underlying_ticker=AAPL&contract_type=call&expiration_date.gte=2024-12-01&expiration_date.lt=2025-01-01"

# Get strikes between $150-$200
curl "https://api.massive.com/v3/reference/options/contracts?underlying_ticker=AAPL&strike_price.gte=150&strike_price.lte=200"
```

---

### 11. Option Contract Overview

**Endpoint:** `GET /v3/reference/options/contracts/{options_ticker}`

**Description:**  
Detailed specifications for a specific options contract. Returns complete contract information including type, exercise style, expiration, strike, shares per contract, underlying ticker, exchange, CFI code, and additional underlyings (if applicable).

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `options_ticker` | string | Yes | Options ticker symbol (format: O:AAPL211119C00085000) |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `as_of` | string | No | Point-in-time lookup (YYYY-MM-DD, default: today) |

**Response Fields:**

```json
{
  "results": {
    "ticker": "O:AAPL211119C00085000",
    "underlying_ticker": "AAPL",
    "contract_type": "call",
    "exercise_style": "american",
    "expiration_date": "2021-11-19",
    "strike_price": 85,
    "shares_per_contract": 100,
    "primary_exchange": "BATO",
    "cfi": "OCASPS",
    "correction": 0,
    "additional_underlyings": [
      {
        "type": "equity",
        "underlying": "VMW",
        "amount": 44
      },
      {
        "type": "currency",
        "underlying": "USD",
        "amount": 6.53
      }
    ]
  }
}
```

**Options Ticker Format:**
- **Prefix**: O: (indicates options contract)
- **Underlying**: AAPL (stock ticker)
- **Expiration**: 211119 (November 19, 2021 - YYMMDD)
- **Type**: C (call) or P (put)
- **Strike**: 00085000 (strike price $85.00, 8 digits with implied decimal)

**Learn More**: [How to Read Stock Options Tickers](https://massive.com/blog/how-to-read-a-stock-options-ticker/)

**Use Cases:**
- **Contract Specifications Reference**: Get details for specific option
- **Option Chain Analysis**: Build complete option chains with details
- **Strategy Development**: Validate contract specifications for strategies
- **Portfolio Integration**: Display contract details for holdings

**Kuberan Integration:**
- 🔮 **FUTURE USE**: When building options trading features
- ✅ Use to display contract details in UI (strike, expiration, type)
- ✅ Validate options ticker format before API calls
- ⚠️ Free tier access: Reference data only (no pricing)

**Example Request:**
```bash
# Get specific Apple call option
curl "https://api.massive.com/v3/reference/options/contracts/O:AAPL211119C00085000"

# Get contract as of historical date
curl "https://api.massive.com/v3/reference/options/contracts/O:AAPL211119C00085000?as_of=2021-10-01"
```

---

## Kuberan Integration Recommendations

### Immediate Priorities (Free Tier)

#### 1. Replace Polygon.io with MASSIVE for Metadata Enrichment

**Current State:**
- Using Polygon.io for foundation metadata (CIK, FIGI, branding)
- Rate limits: 5/min, 300/hr, 7,200/day
- Progress: 1,418/12,140 tickers (11.7%)

**Migration Plan:**
```python
# backend/app/services/providers/implementations/massive_provider.py

class MASSIVEProvider(BaseProvider):
    async def fetch_ticker_overview(self, ticker: str) -> Dict:
        """Fetch comprehensive ticker metadata from MASSIVE."""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        response = await self.client.get(url, headers=self.headers)
        data = response.json()
        
        # Transform to CompanyOverview model
        return {
            "ticker": data["results"]["ticker"],
            "name": data["results"]["name"],
            "cik": data["results"]["cik"],
            "composite_figi": data["results"]["composite_figi"],
            "share_class_figi": data["results"]["share_class_figi"],
            "sic_code": data["results"]["sic_code"],
            "sic_description": data["results"]["sic_description"],
            "market_cap": data["results"].get("market_cap"),
            "total_employees": data["results"].get("total_employees"),
            "description": data["results"].get("description"),
            "homepage_url": data["results"].get("homepage_url"),
            "branding": {
                "logo_url": data["results"]["branding"]["logo_url"],
                "icon_url": data["results"]["branding"]["icon_url"]
            },
            "enrichment_status": "foundation",
            "metadata_sources": ["MASSIVE"]
        }
```

**Benefits:**
- ✅ Compatible with existing `CompanyOverview` model
- ✅ Same rate limits as Polygon.io (5/min, 300/hr, 7,200/day)
- ✅ More comprehensive data (branding, financials, SIC codes)
- ✅ Single API provider (reduce complexity)

**Background Job:**
```python
# backend/app/services/jobs/massive_foundation_builder.py

class MASSIVEFoundationBuilderJob:
    async def run(self):
        """Enrich 5 tickers per execution (respects rate limits)."""
        tickers = await self.get_base_tickers(limit=5)
        
        for ticker_obj in tickers:
            try:
                metadata = await massive_provider.fetch_ticker_overview(ticker_obj.ticker)
                await metadata_service.update_ticker_metadata(ticker_obj.ticker, metadata)
                await asyncio.sleep(12)  # 5 calls/min = 1 call per 12 seconds
            except Exception as e:
                logger.error("Enrichment failed", extra={"ticker": ticker_obj.ticker}, exc_info=True)
```

#### 2. Fetch and Cache Reference Data (One-Time)

**Data to Cache Permanently:**
- **Ticker Types**: Used for filtering and categorization
- **Exchanges**: Used for exchange name lookups
- **Condition Codes**: Used when processing market data (future)

**Implementation:**
```python
# backend/app/scripts/fetch_massive_reference_data.py

async def fetch_and_cache_reference_data():
    """One-time script to fetch and cache reference data."""
    
    # Fetch ticker types
    types = await massive_provider.fetch_ticker_types()
    await reference_repository.save_ticker_types(types)
    
    # Fetch exchanges
    exchanges = await massive_provider.fetch_exchanges()
    await reference_repository.save_exchanges(exchanges)
    
    # Fetch condition codes (optional for now)
    conditions = await massive_provider.fetch_condition_codes(limit=1000)
    await reference_repository.save_condition_codes(conditions)
    
    logger.info("Reference data cached successfully")
```

**Schedule:** Run once, refresh quarterly (data rarely changes)

#### 3. Add Dividend & Split Tracking

**Implementation:**
```python
# backend/app/services/stock/corporate_actions_service.py

class CorporateActionsService:
    async def fetch_dividends(self, ticker: str) -> List[Dict]:
        """Fetch dividend history for ticker."""
        url = f"{self.base_url}/v3/reference/dividends"
        params = {"ticker": ticker, "limit": 1000, "sort": "ex_dividend_date", "order": "desc"}
        response = await self.client.get(url, params=params, headers=self.headers)
        return response.json()["results"]
    
    async def fetch_splits(self, ticker: str) -> List[Dict]:
        """Fetch stock split history."""
        url = f"{self.base_url}/v3/reference/splits"
        params = {"ticker": ticker, "limit": 1000, "sort": "execution_date", "order": "desc"}
        response = await self.client.get(url, params=params, headers=self.headers)
        return response.json()["results"]
```

**Background Job:**
```python
# backend/app/services/jobs/corporate_actions_collector.py

class CorporateActionsCollectorJob:
    async def run(self):
        """Fetch dividends and splits for tracked tickers (weekly)."""
        tickers = await ticker_config_repository.get_active_tickers()
        
        for ticker_obj in tickers:
            # Fetch dividends
            dividends = await corporate_actions_service.fetch_dividends(ticker_obj.ticker)
            await stock_repository.save_dividends(dividends)
            
            # Fetch splits
            splits = await corporate_actions_service.fetch_splits(ticker_obj.ticker)
            await stock_repository.save_splits(splits)
            
            await asyncio.sleep(12)  # Rate limit: 5 calls/min
```

**Schedule:** Weekly (Monday 2:00 AM EST)

#### 4. Integrate News Feed

**Implementation:**
```python
# backend/app/services/stock/news_service.py

class NewsService:
    async def fetch_news(self, ticker: str, limit: int = 50) -> List[Dict]:
        """Fetch recent news for ticker."""
        url = f"{self.base_url}/v2/reference/news"
        params = {"ticker": ticker, "limit": limit, "sort": "published_utc", "order": "desc"}
        response = await self.client.get(url, params=params, headers=self.headers)
        return response.json()["results"]
    
    async def analyze_sentiment(self, ticker: str, days: int = 7) -> Dict:
        """Aggregate sentiment from recent news."""
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = f"{self.base_url}/v2/reference/news"
        params = {
            "ticker": ticker,
            "published_utc.gte": from_date,
            "limit": 1000
        }
        response = await self.client.get(url, params=params, headers=self.headers)
        articles = response.json()["results"]
        
        # Aggregate sentiment
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for article in articles:
            for insight in article.get("insights", []):
                if insight["ticker"] == ticker:
                    sentiments[insight["sentiment"]] += 1
        
        return {
            "ticker": ticker,
            "period_days": days,
            "article_count": len(articles),
            "sentiments": sentiments,
            "sentiment_score": (sentiments["positive"] - sentiments["negative"]) / len(articles) if articles else 0
        }
```

**API Endpoint:**
```python
# backend/app/routers/stocks.py

@router.get("/news/{ticker}")
async def get_stock_news(ticker: str, limit: int = Query(50, le=1000)):
    """Get recent news for ticker."""
    news = await news_service.fetch_news(ticker, limit)
    return {"ticker": ticker, "count": len(news), "articles": news}

@router.get("/sentiment/{ticker}")
async def get_sentiment_analysis(ticker: str, days: int = Query(7, le=30)):
    """Get sentiment analysis from recent news."""
    sentiment = await news_service.analyze_sentiment(ticker, days)
    return sentiment
```

### Future Enhancements (Paid Tier)

When you upgrade to a paid tier, you'll gain access to 130+ additional endpoints:

**Real-Time & Historical Prices:**
- Aggregate bars (OHLC data)
- Intraday trades & quotes
- Snapshots (current market state)
- Previous close data

**Technical Indicators:**
- SMA, EMA, DEMA, TEMA
- RSI, MACD, Stochastic
- Bollinger Bands, ATR
- Aroon, ADX, CCI

**Market Data:**
- Options pricing (bid/ask, Greeks)
- Market status & hours
- Forex rates
- Cryptocurrency prices

**Advanced Features:**
- WebSocket streaming (real-time data)
- Level 2 market data
- Options Greeks calculations
- Historical earnings data

**Migration Strategy:**
1. Keep reference endpoint integrations (already built)
2. Add new paid endpoints incrementally
3. Use same `MASSIVEProvider` class structure
4. Update rate limit configurations
5. Expand background jobs for real-time data collection

---

## Next Steps

### Immediate Actions

1. **✅ COMPLETE**: Fetched all 11 reference endpoint documentation
2. **✅ COMPLETE**: Created comprehensive reference guide
3. **⏭️ TODO**: Update Copilot workspace instructions
4. **⏭️ TODO**: Implement MASSIVE provider class
5. **⏭️ TODO**: Migrate from Polygon.io to MASSIVE
6. **⏭️ TODO**: Add corporate actions tracking (splits, dividends)
7. **⏭️ TODO**: Integrate news feed

### Documentation Updates

**Copilot Instructions** (`.github/copilot-instructions.md`):
- Reference this guide for MASSIVE API questions
- Note free tier limitations (reference endpoints only)
- Mention planned migration from Polygon.io

**Project README** (`README.md`):
- Add MASSIVE as primary metadata provider
- Document free tier capabilities
- Note future expansion plans

**API Documentation** (`docs/API.md`):
- Document new endpoints (news, dividends, splits)
- Update provider architecture notes

### Testing Copilot Context

Ask Copilot:
- "How do I get all stock tickers from MASSIVE API?"
- "What parameters does the ticker overview endpoint accept?"
- "How do I fetch dividend history for AAPL?"
- "What's the rate limit for MASSIVE free tier?"
- "Show me how to integrate MASSIVE news feed"

Copilot should reference this guide and provide accurate answers.

---

**Last Updated:** December 1, 2025  
**Guide Version:** 1.0  
**Tier:** Free (11 Reference Endpoints)  
**Future:** Upgradable to 141+ endpoints (paid tier)
