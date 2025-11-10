# MongoDB Setup Guide

## Quick Start

1. **Start services:**
   ```bash
   ./scripts/mongodb.sh start
   ```

2. **Check status:**
   ```bash
   ./scripts/mongodb.sh status
   ```

3. **Connect to MongoDB shell:**
   ```bash
   ./scripts/mongodb.sh shell
   ```

## Accessing Your Data

### Using MongoDB Shell (mongosh)

Once in the shell:
```javascript
// Show all collections
show collections

// View users
db.users.find().pretty()

// View stock metadata
db.stock_metadata.find().pretty()

// View latest stock prices (10 most recent)
db.stock_prices.find().sort({timestamp: -1}).limit(10).pretty()

// Find prices for a specific ticker
db.stock_prices.find({ticker: "AAPL"}).sort({timestamp: -1}).limit(5).pretty()

// View user watchlists
db.user_watchlists.find().pretty()

// Count documents in a collection
db.stock_prices.countDocuments()

// Exit shell
exit
```

### Using MongoDB Compass (GUI)

1. **Download:** https://www.mongodb.com/products/compass
2. **Connect:** Use connection string `mongodb://localhost:27017`
3. **Browse:** Select `kuberan` database and explore collections visually

## Common Commands

```bash
# Start everything
./scripts/mongodb.sh start

# Stop everything
./scripts/mongodb.sh stop

# View backend logs
./scripts/mongodb.sh logs backend

# View MongoDB logs
./scripts/mongodb.sh logs mongodb

# Restart services
./scripts/mongodb.sh restart

# Backup data
./scripts/mongodb.sh backup

# Clean all data (WARNING: destructive)
./scripts/mongodb.sh clean
```

## Useful MongoDB Queries

### Check if data is being persisted:
```javascript
// In mongosh
use kuberan

// Check latest stock price updates
db.stock_prices.find().sort({timestamp: -1}).limit(1).pretty()

// See all tickers with data
db.stock_prices.distinct("ticker")

// Get price history for a ticker
db.stock_prices.find(
  {ticker: "AAPL"},
  {current_price: 1, timestamp: 1, _id: 0}
).sort({timestamp: -1}).limit(20)
```

## Troubleshooting

### Services won't start:
```bash
# Check if port 27017 is already in use
lsof -i :27017

# Stop any running MongoDB
docker stop kuberan-mongodb

# Start fresh
./scripts/mongodb.sh start
```

### Can't connect to MongoDB:
```bash
# Check if container is running
docker ps | grep mongodb

# Check logs
./scripts/mongodb.sh logs mongodb

# Restart
./scripts/mongodb.sh restart
```

### Clear all data and start fresh:
```bash
./scripts/mongodb.sh clean
./scripts/mongodb.sh start
```

## API Endpoints to Test

Once backend is running, test these endpoints at http://localhost:8000/docs:

1. `POST /register` - Register a user
2. `POST /token` - Login and get JWT token
3. `GET /stocks/configured` - Fetch configured stocks (saves to DB)
4. `GET /stocks/AAPL` - Get Apple stock data
5. `POST /stocks/custom` - Fetch custom ticker list

Then check MongoDB to see the persisted data!

## Next Steps

- Install MongoDB Compass for visual data exploration
- Test the API endpoints to populate data
- Query the database to verify persistence
- Set up background jobs for periodic price updates
