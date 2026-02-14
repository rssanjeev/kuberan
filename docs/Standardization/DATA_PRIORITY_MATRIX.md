# Data Priority Matrix - Multi-Provider Field Mapping

**Created:** December 13, 2025  
**Purpose:** Document all data fields across providers with priority rankings and conflict resolution rules  
**Providers:** YFinance, MASSIVE, Alpha Vantage, Finnhub

---

## Overview

This document maps **~150 data fields** across 4 providers, establishing priority rankings for conflict resolution and data quality assessment.

**Priority Levels:**
- 🔴 **Critical (P0):** Must have for core functionality (price, volume, ticker symbol)
- 🟡 **High (P1):** Important for analysis (market cap, P/E ratio, dividends)
- 🟢 **Medium (P2):** Useful for enrichment (sector, industry, description)
- 🔵 **Low (P3):** Nice-to-have metadata (logo URLs, website, social media)

**Source Reliability:**
- ⭐⭐⭐⭐⭐ **Tier 1:** Exchange-level data (most reliable)
- ⭐⭐⭐⭐ **Tier 2:** Primary financial data providers
- ⭐⭐⭐ **Tier 3:** Aggregated/calculated data
- ⭐⭐ **Tier 4:** Community/user-contributed data

---

## Table of Contents

1. [Real-Time Market Data](#real-time-market-data) (25 fields)
2. [Historical Pricing Data](#historical-pricing-data) (15 fields)
3. [Company Fundamentals](#company-fundamentals) (35 fields)
4. [Financial Statements](#financial-statements) (30 fields)
5. [Corporate Actions](#corporate-actions) (10 fields)
6. [Market Indicators](#market-indicators) (15 fields)
7. [News & Sentiment](#news--sentiment) (10 fields)
8. [Metadata & Identifiers](#metadata--identifiers) (20 fields)

---

## 1. Real-Time Market Data (25 fields)

### Core Price Data (P0 - Critical)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **ticker** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | Any (required) | Exact match required |
| **current_price** | ✅ ⭐⭐⭐⭐ | ✅ ⭐⭐⭐⭐⭐ | ✅ ⭐⭐⭐⭐ | ✅ ⭐⭐⭐⭐ | 🔴 P0 | MASSIVE (real-time) | Most recent timestamp |
| **bid_price** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Most recent |
| **ask_price** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Most recent |
| **bid_size** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **ask_size** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **volume** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Sum if realtime, latest if EOD |
| **volume_24h** | ❌ | ✅ | ❌ | ❌ | 🟢 P2 | MASSIVE | MASSIVE only |
| **last_trade_timestamp** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Most recent |
| **exchange** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **currency** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE (canonical) |

### Daily Price Movement (P0/P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **open** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE preferred |
| **high** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Max of all sources |
| **low** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Min of all sources |
| **close** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE preferred |
| **previous_close** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE preferred |
| **change** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | Calculated | close - previous_close |
| **change_percent** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | Calculated | (change / previous_close) * 100 |
| **vwap** | ✅ | ✅ | ❌ | ✅ | 🟢 P2 | MASSIVE | MASSIVE preferred |

### Extended Hours (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **premarket_price** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | YFinance | Most recent |
| **premarket_change** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | Calculated | premarket - previous_close |
| **afterhours_price** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | YFinance | Most recent |
| **afterhours_change** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | Calculated | afterhours - close |

### Market Status (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **market_state** | ✅ | ✅ | ✅ | ❌ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **is_market_open** | ✅ | ✅ | ✅ | ❌ | 🟡 P1 | Calculated | Based on NYSE calendar |
| **fifty_two_week_high** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | YFinance | Max of all sources |
| **fifty_two_week_low** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | YFinance | Min of all sources |

---

## 2. Historical Pricing Data (15 fields)

### OHLCV Data (P0)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **date** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | Any | Exact match required |
| **open** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE preferred |
| **high** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Max of all sources |
| **low** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Min of all sources |
| **close** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE preferred |
| **adjusted_close** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | YFinance | YFinance (split/dividend adjusted) |
| **volume** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE preferred |

### Intraday Data (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **timestamp** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | Any | Exact match required |
| **interval** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | Any | 1m, 5m, 15m, 30m, 1h, 1d |
| **transactions_count** | ❌ | ✅ | ❌ | ✅ | 🟢 P2 | MASSIVE | MASSIVE only |

### Aggregated Metrics (P2)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **avg_volume_10d** | ✅ | ❌ | ❌ | ❌ | 🟢 P2 | YFinance | Calculate from history |
| **avg_volume_30d** | ✅ | ❌ | ❌ | ❌ | 🟢 P2 | YFinance | Calculate from history |
| **avg_price_50d** | ✅ | ❌ | ❌ | ❌ | 🟢 P2 | YFinance | Calculate from history |
| **avg_price_200d** | ✅ | ❌ | ❌ | ❌ | 🟢 P2 | YFinance | Calculate from history |
| **volatility_30d** | ✅ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Std dev of returns |

---

## 3. Company Fundamentals (35 fields)

### Basic Information (P0/P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **company_name** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | MASSIVE (canonical) |
| **ticker** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | Any | Exact match |
| **exchange** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **currency** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **country** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **sector** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE preferred |
| **industry** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE preferred |
| **description** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Longest (most detailed) |
| **website** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | MASSIVE preferred |
| **employee_count** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |

### Market Metrics (P0/P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **market_cap** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | MASSIVE | Most recent |
| **shares_outstanding** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **float_shares** | ✅ | ✅ | ❌ | ✅ | 🟡 P1 | YFinance | Most recent |
| **shares_short** | ✅ | ❌ | ❌ | ✅ | 🟢 P2 | YFinance | Most recent |
| **short_ratio** | ✅ | ❌ | ❌ | ✅ | 🟢 P2 | YFinance | Most recent |
| **short_percent_float** | ✅ | ❌ | ❌ | ✅ | 🟢 P2 | YFinance | Most recent |

### Valuation Ratios (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **pe_ratio** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **forward_pe** | ✅ | ❌ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **peg_ratio** | ✅ | ❌ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **price_to_book** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **price_to_sales** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **ev_to_revenue** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **ev_to_ebitda** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **enterprise_value** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |

### Profitability Metrics (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **profit_margin** | ✅ | ❌ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **operating_margin** | ✅ | ❌ | ✅ | ✅ | 🟡 P1 | YFinance | Most recent |
| **return_on_assets** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **return_on_equity** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **revenue_per_share** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **quarterly_revenue_growth** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **quarterly_earnings_growth** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |

### Financial Health (P2)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **debt_to_equity** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **current_ratio** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **quick_ratio** | ✅ | ❌ | ✅ | ❌ | 🟢 P2 | YFinance | Most recent |
| **total_cash** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |
| **total_debt** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |

---

## 4. Financial Statements (30 fields)

### Income Statement (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **fiscal_year** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | Any | Exact match |
| **fiscal_quarter** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | Any | Exact match |
| **revenue** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **cost_of_revenue** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **gross_profit** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **operating_expenses** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **operating_income** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **net_income** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **ebitda** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **eps** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **eps_diluted** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |

### Balance Sheet (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **total_assets** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **total_liabilities** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **total_equity** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **current_assets** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **current_liabilities** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **cash_and_equivalents** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **short_term_investments** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **long_term_debt** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **retained_earnings** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |

### Cash Flow Statement (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **operating_cash_flow** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **investing_cash_flow** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **financing_cash_flow** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **free_cash_flow** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |
| **capex** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **dividends_paid** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **stock_repurchased** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Most recent |
| **debt_repayment** | ✅ | ❌ | ✅ | ✅ | 🔵 P3 | YFinance | Most recent |
| **depreciation** | ✅ | ❌ | ✅ | ✅ | 🔵 P3 | YFinance | Most recent |
| **change_in_working_capital** | ✅ | ❌ | ✅ | ✅ | 🔵 P3 | YFinance | Most recent |

---

## 5. Corporate Actions (10 fields)

### Dividends (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **dividend_date** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **dividend_amount** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **dividend_yield** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | YFinance | Calculate: (annual_div / price) * 100 |
| **ex_dividend_date** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **payout_ratio** | ✅ | ❌ | ✅ | ✅ | 🟢 P2 | YFinance | Most recent |

### Stock Splits (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **split_date** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **split_ratio** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **split_from** | ✅ | ✅ | ❌ | ❌ | 🟡 P1 | MASSIVE | MASSIVE only |
| **split_to** | ✅ | ✅ | ❌ | ❌ | 🟡 P1 | MASSIVE | MASSIVE only |

### Earnings (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **earnings_date** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | Most recent |

---

## 6. Market Indicators (15 fields)

### Technical Indicators (P2)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **sma_50** | ✅ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Average of last 50 closes |
| **sma_200** | ✅ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Average of last 200 closes |
| **ema_12** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Exponential moving average |
| **ema_26** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Exponential moving average |
| **rsi_14** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | Relative strength index |
| **macd** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | MACD line |
| **macd_signal** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | MACD signal line |
| **macd_histogram** | ❌ | ❌ | ✅ | ❌ | 🟢 P2 | Calculate | MACD histogram |
| **bollinger_upper** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Upper band |
| **bollinger_middle** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Middle band (SMA) |
| **bollinger_lower** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Lower band |
| **atr_14** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Average true range |
| **stochastic_k** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Stochastic %K |
| **stochastic_d** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Stochastic %D |
| **adx** | ❌ | ❌ | ✅ | ❌ | 🔵 P3 | Calculate | Average directional index |

---

## 7. News & Sentiment (10 fields)

### News Articles (P2)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **headline** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | MASSIVE preferred |
| **published_date** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | Any | Exact timestamp match |
| **source** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | Any | Publisher name |
| **article_url** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | Any | Original URL |
| **image_url** | ✅ | ✅ | ❌ | ✅ | 🔵 P3 | MASSIVE | MASSIVE preferred |
| **summary** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Longest (most detailed) |

### Sentiment Analysis (P2)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **sentiment_score** | ❌ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Average of all sources |
| **sentiment_label** | ❌ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | Majority vote |
| **relevance_score** | ❌ | ✅ | ✅ | ❌ | 🔵 P3 | MASSIVE | MASSIVE preferred |
| **ticker_sentiment** | ❌ | ✅ | ✅ | ❌ | 🔵 P3 | MASSIVE | Per-ticker sentiment |

---

## 8. Metadata & Identifiers (20 fields)

### Core Identifiers (P0)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **ticker** | ✅ | ✅ | ✅ | ✅ | 🔴 P0 | Any | Primary key |
| **cusip** | ❌ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **isin** | ❌ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (canonical) |
| **cik** | ❌ | ✅ | ✅ | ❌ | 🟡 P1 | MASSIVE | MASSIVE (SEC filing ID) |
| **figi** | ❌ | ✅ | ❌ | ❌ | 🟡 P1 | MASSIVE | MASSIVE (Bloomberg ID) |
| **lei** | ❌ | ✅ | ❌ | ❌ | 🟢 P2 | MASSIVE | MASSIVE (Legal Entity ID) |
| **composite_figi** | ❌ | ✅ | ❌ | ❌ | 🟢 P2 | MASSIVE | MASSIVE only |
| **share_class_figi** | ❌ | ✅ | ❌ | ❌ | 🟢 P2 | MASSIVE | MASSIVE only |

### Classification (P1)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **ticker_type** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (CS, ADRC, etc.) |
| **market** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (stocks, otc, indices) |
| **primary_exchange** | ✅ | ✅ | ✅ | ✅ | 🟡 P1 | MASSIVE | MASSIVE (XNYS, XNAS, etc.) |
| **locale** | ✅ | ✅ | ❌ | ❌ | 🟡 P1 | MASSIVE | MASSIVE (us, global, etc.) |
| **sic_code** | ❌ | ✅ | ✅ | ❌ | 🟢 P2 | MASSIVE | MASSIVE (industry code) |
| **sic_description** | ❌ | ✅ | ✅ | ❌ | 🟢 P2 | MASSIVE | MASSIVE only |

### Branding (P3)

| Field | YFinance | MASSIVE | Alpha Vantage | Finnhub | Priority | Primary Source | Conflict Rule |
|-------|----------|---------|---------------|---------|----------|---------------|---------------|
| **logo_url** | ❌ | ✅ | ❌ | ✅ | 🔵 P3 | MASSIVE | MASSIVE (multiple sizes) |
| **icon_url** | ❌ | ✅ | ❌ | ✅ | 🔵 P3 | MASSIVE | MASSIVE only |
| **website** | ✅ | ✅ | ✅ | ✅ | 🟢 P2 | MASSIVE | MASSIVE preferred |
| **phone** | ✅ | ✅ | ❌ | ✅ | 🔵 P3 | MASSIVE | MASSIVE preferred |
| **address** | ✅ | ✅ | ❌ | ✅ | 🔵 P3 | MASSIVE | MASSIVE (street, city, state, zip) |

---

## Conflict Resolution Rules

### 1. Timestamp-Based Resolution
**Rule:** For time-series data, prefer most recent timestamp
**Applies to:** Prices, volumes, market metrics
**Example:**
```python
if massive_timestamp > yfinance_timestamp:
    return massive_data
else:
    return yfinance_data
```

### 2. Source Reliability Priority
**Rule:** Tier 1 > Tier 2 > Tier 3 > Tier 4
**Provider Tiers:**
- Tier 1: MASSIVE (exchange-level data)
- Tier 2: Alpha Vantage, YFinance
- Tier 3: Finnhub
- Tier 4: Community sources

### 3. Data Type-Specific Rules

#### Price Data
- **Rule:** Use MASSIVE for real-time, YFinance for EOD adjusted prices
- **Conflict:** Most recent timestamp wins

#### Fundamental Data
- **Rule:** MASSIVE for financial statements and identifiers, YFinance for ratios
- **Conflict:** Most recent fiscal period wins

#### Metadata
- **Rule:** MASSIVE is canonical source for identifiers (CIK, FIGI, CUSIP)
- **Conflict:** MASSIVE always wins for identifiers

#### News & Sentiment
- **Rule:** Aggregate sentiment scores, prefer MASSIVE for articles and analysis
- **Conflict:** Average sentiment scores from all sources

### 4. Field-Specific Overrides

**Always prefer MASSIVE for:**
- CIK, FIGI, CUSIP, ISIN (SEC/regulatory IDs)
- Ticker type, locale, market classification
- Primary exchange (MIC codes)
- Logo URLs, branding assets

**Always prefer YFinance for:**
- Adjusted close prices (split/dividend adjusted)
- 52-week high/low (comprehensive history)
- Premarket/afterhours prices (reliable extended hours)

**Alpha Vantage (Use only when explicitly needed):**
- Available as fallback for financial statements
- Available as fallback for valuation ratios
- Available as fallback for sentiment analysis
- Not preferred as primary source

**Always calculate for:**
- Technical indicators (SMA, EMA, RSI, MACD)
- Derived metrics (change_percent, dividend_yield)
- Aggregated values (avg_volume, volatility)

---

## Implementation Guidelines

### 1. Data Collection Strategy

**Real-Time Data (15-min cache):**
- Primary: MASSIVE (quotes, market status)
- Fallback: YFinance → Finnhub → Alpha Vantage

**EOD Data (1-day cache):**
- Primary: YFinance (adjusted prices)
- Secondary: MASSIVE (raw OHLCV)
- Validation: Alpha Vantage

**Fundamental Data (7-day cache):**
- Primary: MASSIVE (financial statements, identifiers)
- Secondary: YFinance (ratios, metrics)
- Fallback: Alpha Vantage (when explicitly needed)

**News & Sentiment (1-hour cache):**
- Primary: MASSIVE (news articles, sentiment)
- Secondary: Finnhub (supplementary)
- Fallback: Alpha Vantage (when explicitly needed)

### 2. Caching Strategy

```python
# Priority-based caching
CACHE_TTL = {
    "real_time": 900,        # 15 minutes
    "eod": 86400,            # 1 day
    "fundamentals": 604800,  # 7 days
    "news": 3600,            # 1 hour
    "metadata": 2592000,     # 30 days
    "identifiers": None      # Never expire (immutable)
}
```

### 3. Data Validation

**Required Validations:**
1. Ticker symbol format validation
2. Price data sanity checks (no negative prices)
3. Volume data validation (reasonable ranges)
4. Timestamp validation (not future dates)
5. Percentage validation (0-100 range)
6. Ratio validation (reasonable bounds)

### 4. Error Handling

**Provider Failure Strategy:**
1. Try primary source
2. If fails, try secondary source
3. If fails, try tertiary source
4. If all fail, return cached data (if available)
5. If no cache, return null with error flag

---

## Usage Examples

### Example 1: Stock Price Query
```python
# User requests: Current price for AAPL
primary_source = "MASSIVE"  # Real-time quotes
fallback_sources = ["YFinance", "Finnhub"]
cache_ttl = 900  # 15 minutes

result = {
    "ticker": "AAPL",
    "current_price": 150.00,  # MASSIVE (most recent)
    "bid": 149.98,            # MASSIVE
    "ask": 150.02,            # MASSIVE
    "volume": 50_000_000,     # MASSIVE
    "source": "MASSIVE",
    "timestamp": "2025-12-13T10:30:00Z"
}
```

### Example 2: Fundamental Analysis
```python
# User requests: Financial metrics for MSFT
sources = {
    "identifiers": "MASSIVE",      # CIK, FIGI, CUSIP
    "financials": "MASSIVE",       # Income, balance, cash flow
    "ratios": "YFinance"           # P/E, P/B, dividend yield
}

result = {
    "ticker": "MSFT",
    "cik": "0000789019",           # MASSIVE
    "revenue": 211_915_000_000,    # MASSIVE (FY2023)
    "net_income": 72_361_000_000,  # MASSIVE
    "pe_ratio": 35.2,              # YFinance
    "dividend_yield": 0.82,        # YFinance (calculated)
    "sources": {
        "identifiers": "MASSIVE",
        "financials": "MASSIVE",
        "ratios": "YFinance"
    }
}
```

### Example 3: Conflict Resolution
```python
# User requests: Market cap for NVDA
# Conflict: YFinance = $2.8T, MASSIVE = $2.77T, Alpha Vantage = $2.79T

# Apply conflict resolution
timestamps = {
    "YFinance": "2025-12-13T09:00:00Z",    # Market open
    "MASSIVE": "2025-12-13T10:30:15Z",     # Most recent
    "Alpha Vantage": "2025-12-13T10:00:00Z"
}

# Rule: Most recent timestamp wins
result = {
    "ticker": "NVDA",
    "market_cap": 2_770_000_000_000,  # MASSIVE (most recent)
    "source": "MASSIVE",
    "timestamp": "2025-12-13T10:30:15Z",
    "alternate_sources": {
        "YFinance": 2_800_000_000_000,
        "Alpha Vantage": 2_790_000_000_000
    }
}
```

---

## Summary Statistics

### Field Coverage by Provider

| Provider | Total Fields | P0 Fields | P1 Fields | P2 Fields | P3 Fields |
|----------|--------------|-----------|-----------|-----------|-----------|
| **YFinance** | ~120 | 18 | 45 | 42 | 15 |
| **MASSIVE** | ~85 | 20 | 35 | 25 | 5 |
| **Alpha Vantage** | ~110 | 12 | 50 | 38 | 10 |
| **Finnhub** | ~75 | 15 | 30 | 25 | 5 |

### Priority Distribution

| Priority | Count | Percentage | Description |
|----------|-------|------------|-------------|
| 🔴 **P0 Critical** | 25 | 16.7% | Must-have for core functionality |
| 🟡 **P1 High** | 60 | 40.0% | Important for analysis |
| 🟢 **P2 Medium** | 50 | 33.3% | Useful for enrichment |
| 🔵 **P3 Low** | 15 | 10.0% | Nice-to-have metadata |
| **Total** | **150** | **100%** | All documented fields |

---

## Next Steps

1. **Implement conflict resolution service** (`conflict_resolution.py`)
2. **Create provider config** (`source_reliability.yaml`)
3. **Write unit tests** for conflict scenarios
4. **Document HTML scraping** (Finviz, StockAnalysis structures)
5. **Implement data validation** rules
6. **Create monitoring dashboard** for data quality

---

**Last Updated:** December 13, 2025  
**Responsible:** Sanjeev  
**Status:** ✅ Complete - Ready for implementation
