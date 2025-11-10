# Stock Data Management Implementation

## Overview
This implementation provides an efficient, scalable architecture for fetching and storing stock data with MongoDB persistence.

## Architecture

### 1. **Data Separation**
Stock data is split into two categories:

#### Frequently Changing Data (Stock Prices)
- Current price
- Open/Close prices
- Day high/low
- Volume
- **Update Frequency:** Real-time to every few minutes
- **Storage:** Time-series in `stock_prices` collection

#### Infrequently Changing Data (Metadata)
- Company name
- Sector/Industry
- Market cap
- Exchange, Country
- Description
- **Update Frequency:** Daily to weekly
- **Storage:** Cached in `stock_metadata` collection

### 2. **MongoDB Collections**

#### `stock_metadata`
```python
{
    ticker: "AAPL",
    name: "Apple Inc.",
    sector: "Technology",
    industry: "Consumer Electronics",
    market_cap: 3000000000000,
    currency: "USD",
    exchange: "NASDAQ",
    updated_at: ISODate("2025-11-09T...")
}
```
- **Indexes:** ticker (unique)
- **Refresh:** Every 7 days (configurable)

#### `stock_prices`
```python
{
    ticker: "AAPL",
    current_price: 182.50,
    previous_close: 181.00,
    open: 181.50,
    day_high: 183.00,
    day_low: 180.50,
    volume: 50000000,
    timestamp: ISODate("2025-11-09T15:30:00Z")
}
```
- **Indexes:** ticker, timestamp, compound (ticker + timestamp)
- **Use:** Time-series analysis, charting

#### `user_watchlists`
```python
{
    user_id: "user123",
    tickers: ["AAPL", "GOOGL", "MSFT"],
    created_at: ISODate("..."),
    updated_at: ISODate("...")
}
```
- **Indexes:** user_id
- **Use:** User-specific ticker tracking

### 3. **Service Methods**

#### `get_stock_price(ticker)`
- Fetches only price data (fast API call)
- Uses `yfinance.fast_info` for minimal latency
- Call this frequently for real-time updates

#### `get_stock_metadata(ticker)`
- Fetches company information (slower API call)
- Call this infrequently or on initial load
- Data is cached in MongoDB

#### `get_stock_info_with_cache(ticker, save_to_db=True)`
- **Smart caching logic:**
  1. Always fetches fresh price data
  2. Checks if metadata is stale (>7 days)
  3. Uses cached metadata if fresh
  4. Fetches metadata only when needed
  5. Saves both to MongoDB

### 4. **Repository Pattern**

The `StockRepository` handles all database operations:

- `save_stock_metadata()` - Upsert metadata
- `get_stock_metadata()` - Retrieve from cache
- `is_metadata_stale()` - Check if refresh needed
- `save_stock_price()` - Store price snapshot
- `get_latest_price()` - Get most recent price
- `get_price_history()` - Query time-series data
- `add_to_watchlist()` - User watchlist management
- `remove_from_watchlist()` - Remove ticker from watchlist

### 5. **Benefits**

✅ **Performance:**
- Reduced API calls to Yahoo Finance
- Fast price updates (only fetch what changes)
- Cached metadata reduces latency

✅ **Scalability:**
- Time-series storage for historical analysis
- User-specific watchlists
- Background jobs can update prices independently

✅ **Cost Efficiency:**
- Fewer external API calls
- Metadata cached for 7 days (configurable)
- Price data stored for analytics

✅ **Future Features:**
- Price alerts (compare new vs. stored prices)
- Historical charting (query time-series)
- Trend analysis (aggregate price data)
- User portfolios (extend watchlists)

### 6. **Usage Example**

```python
# For real-time price updates (call frequently)
price = await stock_service.get_stock_price("AAPL")
await stock_repository.save_stock_price(price)

# For complete info with smart caching (call on page load)
info = await stock_service.get_stock_info_with_cache("AAPL")

# Get historical prices for charting
history = await stock_repository.get_price_history(
    ticker="AAPL",
    start_time=datetime.utcnow() - timedelta(days=7)
)
```

### 7. **Configuration**

In `backend/config/tickers.yaml`:
```yaml
tickers:
  - AAPL
  - GOOGL
  
refresh_interval: 300  # Price update frequency (seconds)
data_retention_days: 30  # How long to keep price history
```

### 8. **Next Steps**

1. **Background Tasks:**
   - Schedule periodic price updates
   - Clean up old price data

2. **API Enhancements:**
   - Add endpoints for price history
   - User watchlist CRUD operations
   - Price alerts

3. **Optimization:**
   - Batch inserts for multiple prices
   - Aggregation pipeline for analytics
   - WebSocket for real-time updates

4. **Monitoring:**
   - Track API call rates
   - Monitor cache hit rates
   - Alert on stale data
