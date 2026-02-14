# FinViz Dual-Pipeline Ingestion Architecture

**Last Updated:** 2025-12-22  
**Status:** 🟢 Active - Authoritative Reference  
**Purpose:** Define the two-stage FinViz data extraction strategy for anti-blocking optimization

---

## Overview

FinViz data extraction uses a **dual-pipeline architecture** to:
1. **Minimize blocking risk** by spreading requests across different page types
2. **Maximize data coverage** by combining screener bulk extraction with quote page deep dives
3. **Optimize rate limiting** by leveraging screener's 20-tickers-per-request efficiency

### Field Distribution

| Source | Fields | Description |
|--------|--------|-------------|
| Screener Only | 8 | Fields unique to screener (change_from_open, gap, etc.) |
| Quote Page Only | 31 | Deep-dive fields (employees, enterprise_value, income, etc.) |
| Both Sources | 56 | Overlapping fields (price, market_cap, P/E, etc.) |
| **Total** | **95** | Complete FinViz coverage |

---

## Pipeline 1: Screener Extraction (Bulk Collection)

### Purpose
Extract data for **20 tickers per request** across 4 tabs, achieving high throughput with minimal requests.

### Characteristics

| Aspect | Value |
|--------|-------|
| URL Pattern | `https://finviz.com/screener.ashx?v={view}&r={offset}` |
| Tickers per Page | 20 |
| Available Views/Tabs | 4 (Overview, Valuation, Financial, Technical) |
| Fields per Tab | 10-12 columns |
| Total Fields | ~42 unique fields across all tabs |

### Screener Tabs (Views)

| Tab | View Code | Fields Extracted |
|-----|-----------|------------------|
| **Overview** | v=111 | ticker, company, sector, industry, country, market_cap, P/E, price, change, volume |
| **Valuation** | v=121 | market_cap, P/E, forward_pe, peg, P/S, P/B, P/C, P/FCF, eps_ttm, eps_growth |
| **Financial** | v=161 | market_cap, dividend_yield, ROA, ROE, ROIC, current_ratio, quick_ratio, debt/eq, margins |
| **Technical** | v=171 | price, change, volume, RSI, SMA20, SMA50, SMA200, high_52w, low_52w, beta |

### Screener-Only Fields (8 fields)

These fields are **only available in the screener**, not on quote pages:

| Field | Screener Key | Description |
|-------|--------------|-------------|
| `change_from_open` | Change from Open | % change from today's open |
| `gap` | Gap | Opening gap percentage |
| `company_name` | Company | Full company name |
| `sector` | Sector | Business sector |
| `industry` | Industry | Industry classification |
| `country` | Country | Country of incorporation |
| `optionable` | Optionable | Has options trading |
| `shortable` | Shortable | Can be shorted |

### Execution Strategy

```
For each batch of 1000 tickers:
  1. Navigate to screener with filter (or no filter for full universe)
  2. For each tab (Overview → Valuation → Financial → Technical):
     a. Paginate through 50 pages (20 tickers × 50 = 1000)
     b. Extract HTML table rows
     c. Parse into structured data
  3. Store partial FinvizSnapshot documents (source.is_complete = false)
  4. Wait 2-5 seconds between tab switches
  5. Wait 10-30 seconds between batches
```

### Anti-Blocking Measures

- **Tab Rotation**: Switch between tabs naturally
- **Pagination Delays**: 2-5 seconds between pages
- **Session Limits**: Max 200 pages per session
- **User-Agent Rotation**: Randomize browser fingerprint

---

## Pipeline 2: Quote Page Extraction (Deep Dive)

### Purpose
Collect the **31 quote-page-only fields** plus validate/update screener data for targeted tickers.

### Characteristics

| Aspect | Value |
|--------|-------|
| URL Pattern | `https://finviz.com/quote.ashx?t={ticker}&p=d` |
| Tickers per Page | 1 |
| Snapshot Table Fields | 83+ (overlaps with screener) |
| Quote-Only Fields | 31 unique fields |
| Related Entities | Peers, Held-by-ETFs |

### Quote-Page-Only Fields (31 fields)

Fields that **require** quote page extraction:

#### Identity & Structure
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `index` | Index | Index memberships (S&P 500, DJIA, etc.) |
| `employees` | Employees | Number of employees |
| `ipo_date` | IPO | IPO date |

#### Valuation & Financials
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `enterprise_value` | Enterprise Value | EV calculation |
| `ev_to_ebitda` | EV/EBITDA | EV/EBITDA ratio |
| `ev_to_sales` | EV/Sales | EV/Sales ratio |
| `income` | Income | Net income TTM |
| `sales` | Sales | Revenue TTM |
| `book_value_per_share` | Book/sh | Book value per share |
| `cash_per_share` | Cash/sh | Cash per share |

#### Ownership
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `insider_ownership` | Insider Own | Insider ownership % |
| `insider_transactions` | Insider Trans | Recent insider activity |
| `institutional_ownership` | Inst Own | Institutional ownership % |
| `institutional_transactions` | Inst Trans | Institutional activity |
| `shares_outstanding` | Shs Outstand | Total shares |
| `shares_float` | Shs Float | Float shares |
| `float_short` | Float Short | Short % of float |

#### Dividend Details
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `dividend` | Dividend | Dividend amount |
| `payout_ratio` | Payout | Dividend payout ratio |
| `ex_dividend_date` | Ex-Div Date | Ex-dividend date |

#### Growth Estimates
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `eps_next_year` | EPS next Y | EPS estimate next year |
| `eps_next_quarter` | EPS next Q | EPS estimate next quarter |
| `eps_growth_quarter` | EPS Q/Q | Quarterly EPS growth |
| `sales_growth_quarter` | Sales Q/Q | Quarterly sales growth |

#### Technical Details
| Field | Quote Key | Description |
|-------|-----------|-------------|
| `prev_close` | Prev Close | Previous close price |
| `trades` | Trades | Number of trades |
| `volatility_week` | Volatility W | Weekly volatility |
| `volatility_month` | Volatility M | Monthly volatility |
| `atr` | ATR | Average True Range |
| `target_price` | Target Price | Analyst target price |
| `recom` | Recom | Analyst recommendation |

#### Related Entities
| Field | Location | Description |
|-------|----------|-------------|
| `peers` | Peers row | Related company tickers |
| `held_by_etfs` | Held by row | ETFs holding this stock |

### Execution Strategy

```
For each ticker needing quote-page data:
  1. Check if screener data exists (source.screener_collected_at != null)
  2. Navigate to quote page
  3. Handle popups/ads (3 interceptors)
  4. Extract snapshot table (83 fields)
  5. Extract peers and held_by_etfs
  6. Merge with existing screener data
  7. Set source.quote_page_collected_at
  8. Set source.is_complete = true (if screener also done)
  9. Wait 5-10 seconds before next ticker
```

### Priority for Quote Page

Not all tickers need quote page extraction. Prioritize:

1. **Watchlist tickers** - User's actively tracked stocks
2. **Holdings in ETFs** - Underlying stocks in tracked ETFs
3. **High interest** - Tickers queried via API
4. **Incomplete data** - `source.is_complete = false`

---

## MongoDB Model Structure

The `FinvizSnapshot` model is designed to handle both pipelines:

```python
class FinvizSnapshot(Document):
    ticker: str
    entity_type: str  # "stock" or "etf"
    as_of: datetime
    
    # Structured sections (aligned with FINVIZ_SCHEMA.json)
    identity: FinvizIdentity      # company_name, sector, industry, etc.
    price: FinvizPrice            # price, change, volume, etc.
    valuation: FinvizValuation    # market_cap, P/E, P/B, etc.
    financials: FinvizFinancials  # income, sales, book/share, cash/share
    profitability: FinvizProfitability  # ROA, ROE, margins
    liquidity: FinvizLiquidity    # current_ratio, debt_to_equity
    dividend: FinvizDividend      # yield, payout, ex-date
    growth: FinvizGrowth          # EPS growth, sales growth
    ownership: FinvizOwnership    # insider, institutional, short
    technical: FinvizTechnical    # RSI, SMA, beta, ATR
    performance: FinvizPerformance  # weekly, monthly, YTD
    
    # Related entities (quote_page only)
    peers: List[str]
    held_by_etfs: List[str]
    
    # Source tracking for dual-pipeline
    source: FinvizSourceInfo
        screener_collected_at: datetime  # When screener data was collected
        quote_page_collected_at: datetime  # When quote page data was collected
        screener_tab: str  # Which tab was used (overview, valuation, etc.)
        is_complete: bool  # True when both sources collected
        screener_fields_count: int
        quote_page_fields_count: int
    
    # Unmapped fields storage
    extra_fields: Dict[str, Any]  # Any fields not in structured sections
```

### Data Merge Logic

When merging screener and quote page data:

```python
def merge_finviz_data(existing: FinvizSnapshot, new_data: dict, source: str):
    """
    Merge new data into existing snapshot.
    
    Rules:
    1. Quote page data takes precedence for overlapping fields
    2. Screener-only fields preserved if quote page doesn't have them
    3. Source timestamps updated appropriately
    4. is_complete set to True when both sources collected
    """
    if source == "screener":
        # Update screener fields
        existing.source.screener_collected_at = datetime.now()
        existing.source.screener_tab = new_data.get("tab", "overview")
        # Don't overwrite quote_page data if it exists
        for section in ["identity", "price", "valuation", ...]:
            merge_section(existing, new_data, section, overwrite=False)
    
    elif source == "quote_page":
        # Quote page takes precedence
        existing.source.quote_page_collected_at = datetime.now()
        for section in ["identity", "price", "valuation", ...]:
            merge_section(existing, new_data, section, overwrite=True)
        # Add quote-only data
        existing.peers = new_data.get("peers", [])
        existing.held_by_etfs = new_data.get("held_by_etfs", [])
    
    # Check completeness
    existing.source.is_complete = (
        existing.source.screener_collected_at is not None and
        existing.source.quote_page_collected_at is not None
    )
```

---

## Execution Schedule

### Daily Screener Run (Night/Off-Hours)

```
Schedule: 10:00 PM EST (after market close + settlement)
Duration: ~2-3 hours for full S&P 500

Steps:
1. Run Pipeline 1 for all 500 tickers
2. Cycle through 4 tabs
3. Store with source.screener_collected_at
4. 25 pages × 4 tabs × 5 sec delay = ~8 min per 500 tickers
```

### Targeted Quote Page Run (Background)

```
Schedule: Continuous, low priority, 1 ticker every 10-30 seconds
Priority: Watchlist > Holdings > Recent Queries > Random

Steps:
1. Query for tickers where source.is_complete = false
2. Run Pipeline 2 for highest priority ticker
3. Merge with existing screener data
4. Mark as complete
```

### On-Demand Quote Page (User Request)

```
Trigger: API request for ticker with stale/missing quote data
Timeout: 15 seconds
Fallback: Return screener-only data if quote page fails
```

---

## Rate Limiting Strategy

### Request Budget

| Time Window | Max Requests | Notes |
|-------------|--------------|-------|
| Per Second | 1 | Minimum 1 second between requests |
| Per Minute | 10 | ~6 second average gap |
| Per Hour | 100 | Conservative for sustained runs |
| Per Day | 1000 | With session rotation |

### Session Management

```python
SESSION_ROTATION = {
    "max_pages_per_session": 200,
    "session_cooldown_minutes": 30,
    "concurrent_sessions": 1,  # Never parallel
    "user_agents": [...],  # Rotate 10+ user agents
}
```

---

## Comparison: Screener vs Quote Page

| Aspect | Screener (Pipeline 1) | Quote Page (Pipeline 2) |
|--------|----------------------|-------------------------|
| **Tickers per request** | 20 | 1 |
| **Unique fields** | 8 | 31 |
| **Overlapping fields** | 34 | 52 |
| **Request efficiency** | High (bulk) | Low (individual) |
| **Blocking risk** | Low (normal browsing) | Medium (repeated pattern) |
| **Use case** | Full universe scan | Targeted deep dive |
| **Schedule** | Nightly batch | On-demand + background |

---

## Implementation Checklist

### Phase 1: Screener Pipeline (Current Priority)
- [ ] Update screener parser for 4-tab support
- [ ] Create screener extraction job
- [ ] Implement pagination handling
- [ ] Add tab rotation logic
- [ ] Store partial snapshots with source tracking

### Phase 2: Quote Page Pipeline
- [ ] Update quote page parser for structured sections
- [ ] Create quote page extraction job
- [ ] Implement merge logic
- [ ] Add priority queue for ticker selection
- [ ] Handle on-demand requests

### Phase 3: Integration
- [ ] API endpoints for combined data
- [ ] Completeness monitoring dashboard
- [ ] Rate limit monitoring
- [ ] Error recovery and retry logic

---

## Related Documentation

- [FINVIZ_SCHEMA.json](FINVIZ_SCHEMA.json) - Complete field definitions
- [FINVIZ_QUOTE_PAGE_STRUCTURE.md](FINVIZ_QUOTE_PAGE_STRUCTURE.md) - Quote page HTML structure
- [FINVIZ_SCREENER_TABS_COMPARISON.md](FINVIZ_SCREENER_TABS_COMPARISON.md) - Screener tab analysis
- [WEB_SCRAPING.md](../../.github/docs/WEB_SCRAPING.md) - General scraping guidelines
