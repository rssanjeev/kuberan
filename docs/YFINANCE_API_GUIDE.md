# YFinance API Guide - Comprehensive Reference

**Last Updated:** December 13, 2025  
**Library:** yfinance (Python)  
**Documentation:** https://github.com/ranaroussi/yfinance  
**Primary Use:** EOD prices, adjusted OHLCV, fundamental ratios, extended hours

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Core Methods](#core-methods)
4. [Data Fields Available](#data-fields-available)
5. [Historical Data Intervals](#historical-data-intervals)
6. [Limitations & Gotchas](#limitations--gotchas)
7. [Best Practices](#best-practices)
8. [Code Examples](#code-examples)

---

## Overview

### What is YFinance?

YFinance is a Python library that provides free access to Yahoo Finance data. It's an unofficial API wrapper that scrapes data from Yahoo Finance's public pages and APIs.

### Strengths

✅ **Free & No API Key:** No registration or authentication required  
✅ **Comprehensive Coverage:** 120+ data fields from `Ticker.info`  
✅ **Historical Data:** OHLCV data with multiple intervals (1m to 1mo)  
✅ **Adjusted Prices:** Split and dividend-adjusted close prices  
✅ **Extended Hours:** Premarket and afterhours data  
✅ **Financial Statements:** Income, balance sheet, cash flow  
✅ **Dividends & Splits:** Complete corporate action history  
✅ **Batch Requests:** Download multiple tickers simultaneously  

### Limitations

❌ **Unofficial API:** No SLA or guaranteed uptime  
❌ **Data Delays:** 15-20 minute delay for real-time quotes  
❌ **Rate Limiting:** ~2000 requests/hour per IP (soft limit)  
❌ **Historical Limits:** 7 days max for 1-minute interval data  
❌ **Missing Data:** Some tickers may have incomplete data  
❌ **Web Scraping:** Subject to breakage if Yahoo changes HTML structure  

### When to Use YFinance

**Primary Use Cases:**
- EOD (end-of-day) adjusted close prices
- Historical OHLCV data (daily, weekly, monthly)
- Fundamental ratios (P/E, P/B, dividend yield)
- Extended hours data (premarket/afterhours)
- Financial statements (income, balance, cash flow)
- 52-week high/low tracking
- Dividend and split history

**Not Recommended For:**
- Real-time quotes (use MASSIVE instead)
- Tick-level data (use MASSIVE instead)
- Regulatory identifiers (use MASSIVE for CIK, FIGI, CUSIP)
- High-frequency trading (unreliable latency)

---

## Installation & Setup

### Installation

```bash
pip install yfinance
```

### Basic Usage

```python
import yfinance as yf

# Create ticker object
ticker = yf.Ticker("AAPL")

# Get all info (120+ fields)
info = ticker.info

# Get historical prices
history = ticker.history(period="1mo")
```

### Dependencies

```
pandas>=1.3.0
numpy>=1.21.0
requests>=2.26.0
lxml>=4.6.3
multitasking>=0.0.11
```

---

## Core Methods

### 1. Ticker.info

Returns dictionary with 120+ fundamental and market data fields.

```python
ticker = yf.Ticker("AAPL")
info = ticker.info

# Access fields
company_name = info['longName']
market_cap = info['marketCap']
pe_ratio = info['trailingPE']
```

**Returns:** `Dict[str, Any]`  
**Cache:** Should be cached for 7+ days (slow to fetch)  
**Fields:** See [Data Fields Available](#data-fields-available) section

### 2. Ticker.history()

Fetches historical OHLCV data with adjustments.

```python
# Last 1 month of daily data
history = ticker.history(period="1mo")

# Custom date range
history = ticker.history(start="2024-01-01", end="2024-12-31")

# 1-minute intraday data (7 days max)
history = ticker.history(period="7d", interval="1m")
```

**Parameters:**
- `period` (str): Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
- `interval` (str): Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
- `start` (str/datetime): Start date (YYYY-MM-DD)
- `end` (str/datetime): End date (YYYY-MM-DD)
- `auto_adjust` (bool): Auto-adjust OHLC prices (default True)
- `actions` (bool): Include dividends/splits (default True)
- `prepost` (bool): Include premarket/postmarket (default False)

**Returns:** `pandas.DataFrame` with columns:
- Open, High, Low, Close, Volume
- Dividends (if actions=True)
- Stock Splits (if actions=True)

### 3. Ticker.dividends

Returns complete dividend history.

```python
dividends = ticker.dividends

# Latest dividend
latest = dividends.iloc[-1]
```

**Returns:** `pandas.Series` indexed by date  
**Values:** Dividend amount per share

### 4. Ticker.splits

Returns stock split history.

```python
splits = ticker.splits

# Check if splits exist
if not splits.empty:
    last_split = splits.iloc[-1]
```

**Returns:** `pandas.Series` indexed by date  
**Values:** Split ratio (e.g., 4.0 for 4-for-1 split)

### 5. Ticker.financials

Returns income statement (annual).

```python
financials = ticker.financials

# Latest year revenue
revenue = financials.loc['Total Revenue'].iloc[0]
```

**Returns:** `pandas.DataFrame` (rows=metrics, cols=fiscal years)  
**Similar Methods:**
- `ticker.quarterly_financials` - Quarterly income statement
- `ticker.balance_sheet` - Annual balance sheet
- `ticker.quarterly_balance_sheet` - Quarterly balance sheet
- `ticker.cashflow` - Annual cash flow statement
- `ticker.quarterly_cashflow` - Quarterly cash flow

### 6. Ticker.recommendations

Returns analyst recommendations (last 6 months).

```python
recommendations = ticker.recommendations

# Count by firm
firm_counts = recommendations['Firm'].value_counts()
```

**Returns:** `pandas.DataFrame` with columns:
- Firm, To Grade, From Grade, Action, Date

### 7. Ticker.calendar

Returns upcoming earnings and dividend dates.

```python
calendar = ticker.calendar

# Earnings date
earnings_date = calendar['Earnings Date'][0]
```

**Returns:** Dictionary with:
- Earnings Date
- Earnings Average
- Earnings Low
- Earnings High
- Revenue Average
- Revenue Low
- Revenue High

### 8. Ticker.options

Returns available option expiration dates.

```python
# Get expiration dates
expirations = ticker.options

# Get option chain for specific date
opt_chain = ticker.option_chain(expirations[0])
calls = opt_chain.calls
puts = opt_chain.puts
```

**Returns:** `tuple` of expiration date strings

---

## Data Fields Available

### From Ticker.info (120+ fields)

**Basic Information (10 fields):**
- `symbol` - Ticker symbol
- `longName` - Full company name
- `shortName` - Abbreviated name
- `exchange` - Stock exchange (e.g., "NMS" for NASDAQ)
- `quoteType` - Security type (EQUITY, ETF, etc.)
- `currency` - Trading currency (USD, EUR, etc.)
- `sector` - Business sector
- `industry` - Industry classification
- `country` - Country of domicile
- `website` - Company website URL

**Market Data (15 fields):**
- `currentPrice` - Last trade price
- `previousClose` - Prior day closing price
- `open` - Today's opening price
- `dayLow` - Today's low price
- `dayHigh` - Today's high price
- `regularMarketVolume` - Today's volume
- `averageVolume` - Average daily volume (10 days)
- `averageVolume10days` - 10-day average volume
- `averageDailyVolume10Day` - Same as above
- `bid` - Current bid price
- `ask` - Current ask price
- `bidSize` - Bid size
- `askSize` - Ask size
- `fiftyTwoWeekLow` - 52-week low price
- `fiftyTwoWeekHigh` - 52-week high price

**Valuation Metrics (15 fields):**
- `marketCap` - Market capitalization
- `enterpriseValue` - Enterprise value
- `trailingPE` - Trailing P/E ratio
- `forwardPE` - Forward P/E ratio
- `pegRatio` - PEG ratio
- `priceToBook` - Price-to-book ratio
- `priceToSalesTrailing12Months` - P/S ratio (TTM)
- `enterpriseToRevenue` - EV/Revenue
- `enterpriseToEbitda` - EV/EBITDA
- `bookValue` - Book value per share
- `priceToBook` - Price-to-book ratio
- `earningsQuarterlyGrowth` - QoQ earnings growth
- `revenueQuarterlyGrowth` - QoQ revenue growth
- `netIncomeToCommon` - Net income (common shareholders)
- `trailingEps` - Trailing 12-month EPS

**Profitability Metrics (10 fields):**
- `profitMargins` - Net profit margin
- `grossMargins` - Gross profit margin
- `operatingMargins` - Operating margin
- `ebitdaMargins` - EBITDA margin
- `returnOnAssets` - ROA
- `returnOnEquity` - ROE
- `revenuePerShare` - Revenue per share
- `totalRevenue` - Total revenue (TTM)
- `grossProfits` - Gross profit (TTM)
- `ebitda` - EBITDA (TTM)

**Financial Health (10 fields):**
- `totalCash` - Cash and cash equivalents
- `totalCashPerShare` - Cash per share
- `totalDebt` - Total debt
- `debtToEquity` - Debt-to-equity ratio
- `currentRatio` - Current ratio
- `quickRatio` - Quick ratio
- `freeCashflow` - Free cash flow (TTM)
- `operatingCashflow` - Operating cash flow (TTM)
- `totalAssets` - Total assets
- `totalLiabilities` - Total liabilities

**Share Structure (10 fields):**
- `sharesOutstanding` - Total shares outstanding
- `floatShares` - Floating shares
- `sharesShort` - Shares shorted
- `sharesShortPriorMonth` - Prior month short shares
- `shortRatio` - Days to cover ratio
- `shortPercentOfFloat` - Short % of float
- `heldPercentInsiders` - Insider ownership %
- `heldPercentInstitutions` - Institutional ownership %
- `impliedSharesOutstanding` - Implied shares outstanding
- `sharesPercentSharesOut` - Short % of shares out

**Dividends (5 fields):**
- `dividendRate` - Annual dividend per share
- `dividendYield` - Dividend yield %
- `exDividendDate` - Ex-dividend date (Unix timestamp)
- `payoutRatio` - Payout ratio
- `fiveYearAvgDividendYield` - 5-year avg dividend yield

**Trading Stats (10 fields):**
- `beta` - Beta (3-year)
- `beta3Year` - 3-year beta
- `fiftyDayAverage` - 50-day SMA
- `twoHundredDayAverage` - 200-day SMA
- `trailingAnnualDividendRate` - Trailing annual dividend
- `trailingAnnualDividendYield` - Trailing annual yield
- `volume` - Current volume
- `averageVolume` - Average volume
- `averageVolume10days` - 10-day average volume
- `regularMarketVolume` - Regular market volume

**Other Fields (45+ fields):**
- Employee count, addresses, phone, fax
- Business summary, long business summary
- Target prices (mean, high, low, median)
- Recommendation key (buy, hold, sell)
- Number of analyst opinions
- Most recent quarter, next fiscal year end
- Last split date, last split factor
- And many more...

---

## Historical Data Intervals

### Supported Intervals

| Interval | Max Period | Use Case |
|----------|-----------|----------|
| **1m** | 7 days | Intraday scalping, tick charts |
| **2m** | 60 days | Short-term intraday |
| **5m** | 60 days | Intraday trading |
| **15m** | 60 days | Intraday swing trading |
| **30m** | 60 days | Intraday position tracking |
| **60m** (1h) | 730 days (2 years) | Hourly trend analysis |
| **90m** | 60 days | 1.5-hour bars |
| **1d** | Unlimited | Daily EOD analysis |
| **5d** | Unlimited | Weekly aggregates |
| **1wk** | Unlimited | Weekly bars |
| **1mo** | Unlimited | Monthly bars |
| **3mo** | Unlimited | Quarterly bars |

### Important Limitations

**1-Minute Data:**
```python
# ❌ This will fail (period too long)
history = ticker.history(period="1mo", interval="1m")

# ✅ This works (7 days or less)
history = ticker.history(period="7d", interval="1m")
```

**Intraday Data Limits:**
- 1m, 2m, 5m, 15m, 30m: Max 60 days
- 1h, 90m: Max 730 days (2 years)
- 1d and above: Unlimited (subject to data availability)

---

## Limitations & Gotchas

### 1. Rate Limiting

**Soft Limit:** ~2000 requests/hour per IP

**Symptoms:**
- 429 HTTP errors
- Empty DataFrames
- "No data found" messages

**Workaround:**
```python
import time

for ticker in tickers:
    data = yf.Ticker(ticker).history(period="1d")
    time.sleep(0.5)  # 0.5 second delay
```

### 2. Data Delays

**Free Tier:** 15-20 minute delay for real-time quotes

**Impact:**
- `currentPrice` in `Ticker.info` is delayed
- Use MASSIVE for true real-time data

### 3. Missing/Incomplete Data

**Common Issues:**
- Small-cap stocks: Missing fundamentals
- Foreign stocks: Currency conversion issues
- Delisted stocks: Historical data may be incomplete

**Validation:**
```python
info = ticker.info

# Check if data exists
if 'marketCap' not in info:
    print(f"No market cap data for {ticker}")
```

### 4. Timestamp Issues

**Problem:** Timestamps in UTC, but market hours are in EST

**Solution:**
```python
import pandas as pd

# Convert to EST
history.index = pd.to_datetime(history.index).tz_convert('America/New_York')
```

### 5. Auto-Adjust Default

**Default Behavior:** `auto_adjust=True` adjusts OHLC for splits/dividends

**Impact:**
- Historical prices won't match raw exchange data
- Use `auto_adjust=False` if you need raw OHLC

```python
# Raw OHLC (not adjusted)
raw = ticker.history(period="1y", auto_adjust=False)

# Adjusted OHLC (recommended for analysis)
adjusted = ticker.history(period="1y", auto_adjust=True)
```

### 6. Extended Hours Data

**Default:** `prepost=False` (excludes premarket/afterhours)

**Get Extended Hours:**
```python
# Include premarket and afterhours
extended = ticker.history(period="1d", interval="1m", prepost=True)
```

---

## Best Practices

### 1. Batch Requests for Multiple Tickers

**Efficient:**
```python
import yfinance as yf

# Download multiple tickers at once
tickers = ['AAPL', 'MSFT', 'GOOGL']
data = yf.download(tickers, period="1mo", group_by='ticker')

# Access individual ticker data
aapl_data = data['AAPL']
```

**Benefits:**
- Faster than sequential requests
- Better rate limit management
- Single HTTP session

### 2. Cache Ticker.info Data

**Problem:** `Ticker.info` is slow (fetches 120+ fields)

**Solution:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class YFinanceCache:
    def __init__(self):
        self.cache = {}
        self.ttl = timedelta(days=7)
    
    def get_info(self, ticker: str):
        if ticker in self.cache:
            data, timestamp = self.cache[ticker]
            if datetime.now() - timestamp < self.ttl:
                return data
        
        # Fetch fresh data
        data = yf.Ticker(ticker).info
        self.cache[ticker] = (data, datetime.now())
        return data
```

### 3. Validate Data Before Storing

**Always check:**
```python
def validate_yfinance_data(data: pd.DataFrame) -> bool:
    # Check for empty DataFrame
    if data.empty:
        return False
    
    # Check for negative prices
    if (data['Close'] < 0).any():
        return False
    
    # Check for future dates
    if data.index.max() > pd.Timestamp.now():
        return False
    
    # Check for volume sanity
    if (data['Volume'] < 0).any():
        return False
    
    return True
```

### 4. Handle Exceptions Gracefully

**Robust error handling:**
```python
from requests.exceptions import HTTPError, Timeout
import yfinance as yf

def safe_fetch(ticker: str, retries: int = 3):
    for attempt in range(retries):
        try:
            data = yf.Ticker(ticker).history(period="1mo")
            if not data.empty:
                return data
        except (HTTPError, Timeout) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    return None
```

### 5. Use Adjusted Close for Analysis

**Recommended:**
```python
# Get adjusted close (accounts for splits/dividends)
history = ticker.history(period="1y")
adjusted_close = history['Close']  # Already adjusted

# Calculate returns
returns = adjusted_close.pct_change()
```

**Why:**
- Accurate return calculations
- Comparable across time periods
- Accounts for corporate actions

---

## Code Examples

### Example 1: Basic Quote Retrieval

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

quote = {
    "ticker": info['symbol'],
    "price": info['currentPrice'],
    "change": info['currentPrice'] - info['previousClose'],
    "change_percent": ((info['currentPrice'] / info['previousClose']) - 1) * 100,
    "volume": info['regularMarketVolume'],
    "market_cap": info['marketCap'],
    "pe_ratio": info.get('trailingPE'),
    "52_week_high": info['fiftyTwoWeekHigh'],
    "52_week_low": info['fiftyTwoWeekLow']
}

print(f"AAPL: ${quote['price']:.2f} ({quote['change_percent']:+.2f}%)")
```

### Example 2: Historical Data with Date Range

```python
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("MSFT")

# Last 6 months of daily data
history = ticker.history(
    start="2024-06-01",
    end="2024-12-01",
    interval="1d",
    auto_adjust=True
)

# Calculate daily returns
history['Returns'] = history['Close'].pct_change()

# Calculate 50-day SMA
history['SMA_50'] = history['Close'].rolling(window=50).mean()

print(f"Total days: {len(history)}")
print(f"Avg daily return: {history['Returns'].mean():.4f}")
print(f"Volatility (std): {history['Returns'].std():.4f}")
```

### Example 3: Multi-Ticker Batch Request

```python
import yfinance as yf

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

# Download all at once
data = yf.download(
    tickers,
    period="1mo",
    interval="1d",
    group_by='ticker',
    threads=True  # Parallel downloads
)

# Access individual ticker data
for ticker in tickers:
    ticker_data = data[ticker]
    latest_close = ticker_data['Close'].iloc[-1]
    print(f"{ticker}: ${latest_close:.2f}")
```

### Example 4: Financial Statements Extraction

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get annual financials
income = ticker.financials
balance = ticker.balance_sheet
cashflow = ticker.cashflow

# Extract key metrics (latest year)
latest_year = income.columns[0]

financial_metrics = {
    "ticker": "AAPL",
    "fiscal_year": latest_year.year,
    "revenue": income.loc['Total Revenue', latest_year],
    "gross_profit": income.loc['Gross Profit', latest_year],
    "operating_income": income.loc['Operating Income', latest_year],
    "net_income": income.loc['Net Income', latest_year],
    "total_assets": balance.loc['Total Assets', latest_year],
    "total_debt": balance.loc['Total Debt', latest_year],
    "free_cash_flow": cashflow.loc['Free Cash Flow', latest_year]
}

# Calculate ratios
financial_metrics['profit_margin'] = (
    financial_metrics['net_income'] / financial_metrics['revenue']
)

print(f"Revenue: ${financial_metrics['revenue']:,.0f}")
print(f"Net Income: ${financial_metrics['net_income']:,.0f}")
print(f"Profit Margin: {financial_metrics['profit_margin']:.2%}")
```

### Example 5: Error Handling Pattern

```python
import yfinance as yf
from requests.exceptions import HTTPError, Timeout, ConnectionError
import time
import logging

logger = logging.getLogger(__name__)

class YFinanceFetcher:
    def __init__(self, max_retries: int = 3, backoff: float = 2.0):
        self.max_retries = max_retries
        self.backoff = backoff
    
    def fetch_with_retry(self, ticker: str, **kwargs):
        """Fetch data with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                data = yf.Ticker(ticker).history(**kwargs)
                
                if data.empty:
                    logger.warning(f"Empty data for {ticker}")
                    return None
                
                # Validate data
                if not self._validate(data):
                    logger.error(f"Invalid data for {ticker}")
                    return None
                
                logger.info(f"Successfully fetched {ticker} data")
                return data
                
            except (HTTPError, Timeout, ConnectionError) as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {ticker}: {e}"
                )
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.backoff ** attempt
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retries exhausted for {ticker}")
                    raise
        
        return None
    
    def _validate(self, data) -> bool:
        """Validate fetched data."""
        if data.empty:
            return False
        if (data['Close'] < 0).any():
            return False
        if (data['Volume'] < 0).any():
            return False
        return True

# Usage
fetcher = YFinanceFetcher(max_retries=3, backoff=2.0)
history = fetcher.fetch_with_retry("AAPL", period="1mo")
```

---

## Summary

**YFinance Strengths:**
- ✅ Free, no API key required
- ✅ Comprehensive data (120+ fields)
- ✅ Adjusted OHLCV prices
- ✅ Extended hours data
- ✅ Financial statements

**YFinance Weaknesses:**
- ❌ 15-20 minute delay
- ❌ Unofficial API (no SLA)
- ❌ Rate limiting (~2000/hour)
- ❌ Missing data for small caps

**Primary Use in Kuberan:**
- EOD adjusted close prices (daily/weekly/monthly)
- Fundamental ratios (P/E, P/B, dividend yield)
- 52-week high/low tracking
- Extended hours data (premarket/afterhours)
- Dividend and split history
- Financial statement backup (when MASSIVE unavailable)

**Not Recommended For:**
- Real-time quotes (use MASSIVE)
- Regulatory identifiers (use MASSIVE)
- High-frequency data (use MASSIVE)

---

**Next Steps:**
- See [MASSIVE_PROVIDER_GUIDE.md](MASSIVE_PROVIDER_GUIDE.md) for real-time data
- See [DATA_PRIORITY_MATRIX.md](DATA_PRIORITY_MATRIX.md) for field-level priorities
- See [CONFLICT_RESOLUTION_STRATEGY.md](CONFLICT_RESOLUTION_STRATEGY.md) for handling conflicts
