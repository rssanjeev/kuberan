# Kuberan API Documentation

**Base URL:** `http://localhost:8000`

**Last Updated:** November 11, 2025

---

## Table of Contents

1. [Stock Information Endpoints](#stock-information-endpoints)
2. [Price Collection Endpoints](#price-collection-endpoints)
3. [Ticker Management Endpoints](#ticker-management-endpoints)
4. [Market Status Endpoints](#market-status-endpoints)
5. [Financier - Financial Analytics Endpoints](#financier---financial-analytics-endpoints)

---

## Stock Information Endpoints

### Get Configured Stocks
Get stock information for all tickers configured in MongoDB.

**Endpoint:** `GET /stocks/configured`

**Response:**
```json
{
  "count": 7,
  "stocks": [
    {
      "ticker": "KO",
      "name": "Coca-Cola",
      "current_price": 71.56,
      "change": 0.82,
      "change_percent": 1.16
    }
  ]
}
```

---

### Get Custom Stocks
Get stock information for a custom list of tickers (override YAML configuration).

**Endpoint:** `POST /stocks/custom`

**Request Body:**
```json
{
  "tickers": ["AAPL", "GOOGL", "MSFT"]
}
```

**Response:**
```json
{
  "count": 3,
  "stocks": [...]
}
```

**Errors:**
- `400 Bad Request` - Ticker list is empty

---

### Get Stock Information
Get current stock information for a specific ticker.

**Endpoint:** `GET /stocks/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol (e.g., AAPL)

**Example:** `GET /stocks/NVDA`

**Response:**
```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "current_price": 194.63,
  "change": 2.15,
  "change_percent": 1.12,
  "market_cap": 4782000000000,
  "sector": "Technology",
  "industry": "Semiconductors"
}
```

**Errors:**
- `404 Not Found` - Stock data not found for ticker

---

### Get Stock History
Get historical stock data for a specific ticker from Yahoo Finance.

**Endpoint:** `GET /stocks/history/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol
- `period` (query, optional) - Time period (default: `1mo`)
  - Valid values: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**Example:** `GET /stocks/history/KO?period=1mo`

**Response:**
```json
{
  "ticker": "KO",
  "period": "1mo",
  "data": [
    {
      "date": "2025-10-15",
      "open": 70.25,
      "high": 71.50,
      "low": 69.80,
      "close": 71.20,
      "volume": 15234567
    }
  ]
}
```

**Errors:**
- `404 Not Found` - History not found for ticker

---

### Get Stock Price
Get just the current price for a specific ticker (lightweight endpoint).

**Endpoint:** `GET /stocks/price/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol

**Example:** `GET /stocks/price/AAPL`

**Response:**
```json
{
  "ticker": "AAPL",
  "current_price": 178.45,
  "timestamp": "2025-11-11T19:15:00"
}
```

**Errors:**
- `404 Not Found` - Price not found for ticker

---

## Price Collection Endpoints

### Trigger Manual Price Poll
Manually trigger a price poll for all configured tickers. Useful for testing the polling system.

**Endpoint:** `POST /stocks/poll/trigger`

**Response:**
```json
{
  "message": "Manual poll complete",
  "results": {
    "success": 7,
    "failed": 0,
    "total": 7
  },
  "tickers": ["KO", "NVDA", "VZ", "VOO", "VXUS", "CVX", "XOM"]
}
```

---

### Get Collection Statistics
Get statistics about collected price data.

**Endpoint:** `GET /stocks/price/stats`

**Response:**
```json
{
  "total_records": 2967,
  "tickers": ["CVX", "KO", "NVDA", "VOO", "VXUS", "VZ", "XOM"],
  "ticker_count": 7,
  "oldest_record": "2025-11-10T13:25:08.586000",
  "newest_record": "2025-11-11T19:15:00.000000"
}
```

---

### Get Collected Prices
Get collected price data from MongoDB for a specific ticker.

**Endpoint:** `GET /stocks/price/collected/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol
- `limit` (query, optional) - Maximum number of records to return (default: 100)

**Example:** `GET /stocks/price/collected/KO?limit=5`

**Response:**
```json
{
  "ticker": "KO",
  "count": 5,
  "prices": [
    {
      "price": 71.565,
      "timestamp": "2025-11-11T19:13:01.346000"
    },
    {
      "price": 71.575,
      "timestamp": "2025-11-11T19:12:01.403000"
    }
  ]
}
```

**Note:** Returns prices from the last 365 days, sorted by most recent first.

---

## Ticker Management Endpoints

### List All Tickers
List all configured tickers (both enabled and disabled) with full configuration details.

**Endpoint:** `GET /stocks/tickers/`

**Response:**
```json
{
  "tickers": [
    {
      "ticker": "KO",
      "enabled": true,
      "added_at": "2025-11-10T10:00:00",
      "updated_at": "2025-11-10T10:00:00"
    },
    {
      "ticker": "NVDA",
      "enabled": true,
      "added_at": "2025-11-10T10:00:00",
      "updated_at": "2025-11-10T10:00:00"
    }
  ]
}
```

---

### List Active Tickers
Get list of active (enabled) tickers only.

**Endpoint:** `GET /stocks/tickers/active/`

**Response:**
```json
{
  "tickers": ["KO", "NVDA", "VZ", "VOO", "VXUS", "CVX", "XOM"],
  "count": 7
}
```

---

### Add Ticker
Add a new ticker to the configuration.

**Endpoint:** `POST /stocks/tickers/add/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol
- `enabled` (query, optional) - Whether to enable polling (default: `true`)

**Example:** `POST /stocks/tickers/add/AAPL?enabled=true`

**Response:**
```json
{
  "message": "Ticker AAPL added successfully",
  "ticker": "AAPL",
  "enabled": true
}
```

**Errors:**
- `400 Bad Request` - Ticker already exists

---

### Remove Ticker
Remove a ticker from configuration.

**Endpoint:** `DELETE /stocks/tickers/remove/{ticker}`

**Parameters:**
- `ticker` (path) - Stock ticker symbol to remove

**Example:** `DELETE /stocks/tickers/remove/AAPL`

**Response:**
```json
{
  "message": "Ticker AAPL removed successfully"
}
```

**Errors:**
- `404 Not Found` - Ticker does not exist

---

### Enable Ticker
Enable polling for a ticker.

**Endpoint:** `PUT /stocks/tickers/{ticker}/enable`

**Parameters:**
- `ticker` (path) - Stock ticker symbol

**Example:** `PUT /stocks/tickers/KO/enable`

**Response:**
```json
{
  "message": "Ticker KO enabled",
  "ticker": "KO",
  "enabled": true
}
```

**Errors:**
- `404 Not Found` - Ticker not found

---

### Disable Ticker
Disable polling for a ticker (keeps in database).

**Endpoint:** `PUT /stocks/tickers/{ticker}/disable`

**Parameters:**
- `ticker` (path) - Stock ticker symbol

**Example:** `PUT /stocks/tickers/KO/disable`

**Response:**
```json
{
  "message": "Ticker KO disabled",
  "ticker": "KO",
  "enabled": false
}
```

**Errors:**
- `404 Not Found` - Ticker not found

---

## Market Status Endpoints

### Get Market Status
Check if the NYSE market is open today.

**Endpoint:** `GET /stocks/market/status`

**Response:**
```json
{
  "date": "2025-11-11",
  "is_market_open": true,
  "message": "Market is open for trading"
}
```

**Note:** Uses NYSE calendar to determine market status, accounting for holidays and weekends.

---

## Background Jobs

The system runs two scheduled jobs:

1. **Stock Price Collection**
   - **Schedule:** Every 60 seconds, 9 AM - 5 PM EST (Monday-Friday)
   - **Job ID:** `price_collector`
   - **Description:** Automatically polls current prices for all enabled tickers during market hours

2. **Market Close Price Poll**
   - **Schedule:** Once at 5:00 PM EST (Monday-Friday)
   - **Job ID:** `market_close_poll`
   - **Description:** Captures closing prices at market close

---

## Error Responses

All endpoints follow standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

---

## Data Models

### Stock Information
```typescript
{
  ticker: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  market_cap?: number;
  sector?: string;
  industry?: string;
}
```

### Price Record
```typescript
{
  ticker: string;
  current_price: number;
  previous_close?: number;
  open?: number;
  day_high?: number;
  day_low?: number;
  volume?: number;
  timestamp: string; // ISO 8601 format
}
```

### Ticker Configuration
```typescript
{
  ticker: string;
  enabled: boolean;
  added_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
}
```

---

## Notes

- All ticker symbols are case-insensitive (automatically converted to uppercase)
- Timestamps are in ISO 8601 format
- Market hours are based on NYSE calendar (US/Eastern timezone)
- Price collection only occurs during market hours (9 AM - 5 PM EST, Monday-Friday, excluding holidays)
- Historical price data from `/stocks/price/collected/{ticker}` returns data from the last 365 days

---

## Financier - Financial Analytics Endpoints

### Comprehensive Financial Analysis
Get deep financial analysis with insights including cash flow, trends, anomalies, and health metrics.

**Endpoint:** `GET /financier/analytics/comprehensive`

**Query Parameters:**
- `year` (optional) - Filter by year (e.g., 2025)
- `month` (optional) - Filter by month (1-12)
- `category` (optional) - Filter by category (e.g., "Groceries")

**Example:** `GET /financier/analytics/comprehensive?year=2025`

**Response:**
```json
{
  "filters": {"year": 2025, "month": null, "category": null},
  "transaction_count": 178,
  "cash_flow": {
    "total_income": 5000.00,
    "total_expenses": 3842.50,
    "net_cash_flow": 1157.50
  },
  "monthly_cash_flow": [
    {
      "month": "May 2025",
      "income": 1500.00,
      "expenses": 1280.50,
      "net_cash_flow": 219.50
    }
  ],
  "category_breakdown": [
    {
      "category": "Restaurants & Dining",
      "amount": 985.25,
      "percentage": 25.6,
      "transaction_count": 43,
      "average_transaction": 22.91
    }
  ],
  "outliers": {
    "count": 3,
    "transactions": [
      {
        "transaction_date": "07/15",
        "merchant": "APPLE.COM/BILL",
        "amount": 999.00,
        "category": "Electronics",
        "z_score": 4.25,
        "deviation_from_average": 950.00
      }
    ]
  },
  "spending_spikes": [
    {
      "month": "Jul 2025",
      "spending": 1850.00,
      "average": 1200.00,
      "spike_ratio": 1.54,
      "excess_spending": 650.00
    }
  ],
  "trend_analysis": {
    "trend_direction": "increasing",
    "average_monthly_change": 45.30,
    "correlation_coefficient": 0.842,
    "statistical_significance": "significant",
    "next_month_prediction": 1345.80,
    "confidence": 0.709
  },
  "recurring_payments": [
    {
      "merchant": "NETFLIX.COM",
      "average_amount": 15.99,
      "amount_variation": 0.00,
      "occurrences": 5,
      "frequency": "monthly",
      "is_stable": true
    }
  ],
  "financial_health": {
    "savings_rate": 23.2,
    "expense_to_income_ratio": 76.8,
    "fixed_spending": 850.00,
    "discretionary_spending": 2992.50,
    "fixed_percentage": 22.1,
    "discretionary_percentage": 77.9,
    "category_concentration": 0.342,
    "diversification_score": 65.8
  }
}
```

**Features:**
- **Cash Flow Analysis**: Income, expenses, and net cash flow over time
- **Spending Breakdown**: Category-wise spending with percentages
- **Outlier Detection**: Unusual transactions using Z-score method (threshold: 3.0)
- **Spending Spikes**: Months with spending 1.5x above rolling average
- **Trend Analysis**: Linear regression showing spending direction and predictions
- **Recurring Payments**: Auto-detected subscription services and fixed expenses
- **Financial Health**: Savings rate, expense ratios, spending diversification

---

### Financial Visualizations
Generate visualization charts as base64-encoded images for frontend display.

**IMPORTANT**: This endpoint generates images for **frontend consumption only**. Images are returned as base64-encoded strings in JSON format, intended for display in React components. Do NOT use this endpoint for file downloads, PDF exports, or email attachments.

**Endpoint:** `GET /financier/analytics/visualizations`

**Query Parameters:**
- `year` (optional) - Filter by year
- `month` (optional) - Filter by month (1-12)
- `format` (optional) - Output format: `png` or `svg` (default: `png`)

**Example:** `GET /financier/analytics/visualizations?year=2025&format=png`

**Response:**
```json
{
  "income_vs_expenses": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "category_pie_chart": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "spending_trend": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "outlier_detection": "iVBORw0KGgoAAAANSUhEUgAAA..."
}
```

**Visualizations Generated:**
1. **income_vs_expenses**: Monthly income vs expenses bar chart
2. **category_pie_chart**: Spending distribution by category (pie chart)
3. **spending_trend**: Time series line chart with trend line
4. **outlier_detection**: Scatter plot highlighting unusual transactions

**Frontend Usage (React):**
```html
<img src="data:image/png;base64,{income_vs_expenses}" alt="Income vs Expenses" />
```

**Note**: Images are generated server-side and returned as base64 strings. They are NOT saved to disk or database. The frontend is responsible for displaying these images.

**Errors:**
- `400 Bad Request` - Invalid format (must be 'png' or 'svg')
- `500 Internal Server Error` - Error generating visualizations

---

### Analytics Data Models

#### Cash Flow Summary
```typescript
{
  total_income: number;      // Sum of all credits (payments received)
  total_expenses: number;    // Sum of all charges
  net_cash_flow: number;     // Income - Expenses
}
```

#### Monthly Cash Flow
```typescript
{
  month: string;             // "Jan 2025"
  income: number;
  expenses: number;
  net_cash_flow: number;
}
```

#### Category Breakdown
```typescript
{
  category: string;          // "Groceries"
  amount: number;
  percentage: number;        // % of total spending
  transaction_count: number;
  average_transaction: number;
}
```

#### Outlier Transaction
```typescript
{
  transaction_date: string;  // "MM/DD"
  merchant: string;
  amount: number;
  category: string;
  z_score: number;           // Statistical z-score (>3.0 = outlier)
  deviation_from_average: number;
}
```

#### Spending Spike
```typescript
{
  month: string;
  spending: number;
  average: number;           // 3-month rolling average
  spike_ratio: number;       // Current / Average
  excess_spending: number;   // Amount above average
}
```

#### Trend Analysis
```typescript
{
  trend_direction: "increasing" | "decreasing" | "stable";
  average_monthly_change: number;
  correlation_coefficient: number;  // -1 to 1
  statistical_significance: "significant" | "not_significant";
  next_month_prediction: number;
  confidence: number;               // R-squared (0-1)
}
```

#### Recurring Payment
```typescript
{
  merchant: string;
  average_amount: number;
  amount_variation: number;  // Standard deviation
  occurrences: number;
  frequency: "monthly" | "recurring";
  is_stable: boolean;        // Variation < $1.00
}
```

#### Financial Health Indicators
```typescript
{
  savings_rate: number | null;           // % of income saved (if income data available)
  expense_to_income_ratio: number | null; // % of income spent
  fixed_spending: number;                 // Essential expenses
  discretionary_spending: number;         // Non-essential expenses
  fixed_percentage: number;               // % of total spending
  discretionary_percentage: number;       // % of total spending
  category_concentration: number;         // Gini coefficient (0=diverse, 1=concentrated)
  diversification_score: number;          // 0-100 (higher = more diversified spending)
}
```

---

## Analytics Notes

- **Outlier Detection**: Uses Z-score method with threshold 3.0 (99.7% confidence interval)
- **Spending Spikes**: Detected when monthly spending exceeds 1.5x the 3-month rolling average
- **Trend Analysis**: Uses linear regression with statistical significance testing (p < 0.05)
- **Recurring Payments**: Requires minimum 3 occurrences to detect pattern
- **Financial Health**: Savings rate calculated only when income data is available
- **Fixed Categories**: Utilities, Insurance, Healthcare, Gas & Fuel, Transportation, Bills, Medical
- **Visualizations**: Generated server-side, returned as base64-encoded PNG or SVG images
- **Performance**: Analytics process up to 100,000 transactions per query
