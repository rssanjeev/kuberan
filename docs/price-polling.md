# Price Polling Service

## Overview
The price polling service automatically fetches stock prices for configured tickers every 60 seconds during market hours (9 AM - 5 PM EST, Monday-Friday) and saves them to MongoDB.

## Configuration

Tickers are configured in `/backend/config/tickers.yaml`:
```yaml
tickers:
  - AAPL
  - GOOGL
  - MSFT
  - TSLA
  - AMZN

refresh_interval: 300  # Not used by poller (uses 60 seconds)
data_retention_days: 30
```

## Schedule

**Polling Times:**
- **Days**: Monday through Friday
- **Hours**: 9:00 AM to 5:00 PM EST
- **Frequency**: Every 60 seconds (every minute on the minute)

**What gets saved:**
- Ticker symbol
- Current price
- Timestamp

## Testing

### 1. Manual Trigger (Anytime)
```bash
curl -X POST http://localhost:8000/stocks/poll/trigger
```

### 2. Check Recent Prices in MongoDB
```bash
docker exec kuberan-mongodb mongosh kuberan --quiet --eval "
  db.stock_prices.find().sort({timestamp: -1}).limit(10).forEach(
    doc => print(doc.ticker + ': $' + doc.current_price + ' at ' + doc.timestamp)
  )"
```

### 3. Count Total Price Records
```bash
docker exec kuberan-mongodb mongosh kuberan --quiet --eval "
  db.stock_prices.countDocuments()
"
```

### 4. Watch Backend Logs Live
```bash
docker logs -f kuberan-backend-1
```

During market hours, you'll see output like:
```
[2025-11-09 09:00:00 EST] Polling stock prices...
✓ Saved price for AAPL: $268.47
✓ Saved price for GOOGL: $278.83
✓ Saved price for MSFT: $496.82
✓ Saved price for TSLA: $429.52
✓ Saved price for AMZN: $244.41
Poll complete: 5 successful, 0 failed
```

### 5. Query Price History for a Ticker
```bash
docker exec kuberan-mongodb mongosh kuberan --quiet --eval "
  db.stock_prices.find({ticker: 'AAPL'})
    .sort({timestamp: -1})
    .limit(10)
    .forEach(doc => print(doc.current_price + ' at ' + doc.timestamp))
"
```

## Architecture

**Flow:**
1. APScheduler triggers `poll_prices()` every 60 seconds during market hours
2. Service loads tickers from `tickers.yaml`
3. Fetches prices concurrently using `stock_service.get_stock_price()`
4. Saves each price to MongoDB via `stock_repository.save_stock_price()`
5. Logs results to console

**Key Files:**
- `/backend/app/services/price_poller.py` - Scheduler service
- `/backend/app/services/stock_service.py` - Stock data fetching
- `/backend/app/repositories/stock_repository.py` - MongoDB persistence
- `/backend/config/tickers.yaml` - Ticker configuration

## Monitoring

### Check if Poller is Running
Look for this in the logs on startup:
```
✓ Price poller started at 2025-11-09 17:59:13 EST
  Polling every 60 seconds during market hours (9 AM - 5 PM EST, Mon-Fri)
  Monitoring tickers: AAPL, GOOGL, MSFT, TSLA, AMZN
✓ Application started successfully
```

### During Market Hours
The poller will automatically run every minute and log each poll:
```
[2025-11-09 09:01:00 EST] Polling stock prices...
✓ Saved price for AAPL: $268.47
...
Poll complete: 5 successful, 0 failed
```

### After Hours
The poller is active but won't execute until next market open (9 AM EST).

## Data Storage

Prices are stored in the `stock_prices` collection with schema:
```json
{
  "_id": ObjectId,
  "ticker": "AAPL",
  "current_price": 268.47,
  "timestamp": "2025-11-09T23:00:09.332Z"
}
```

This creates a time-series of price data that can be queried for:
- Historical price charts
- Price change analysis
- Volatility calculations
- Alert triggers (future feature)

## Notes

- **Current time**: The system uses EST timezone for market hours
- **Market closed**: Poller runs but doesn't execute outside 9 AM - 5 PM EST
- **Weekends**: No polling on Saturday/Sunday
- **Holidays**: Poller will still run (consider adding holiday calendar check)
- **Data retention**: Currently unlimited; implement cleanup if needed
