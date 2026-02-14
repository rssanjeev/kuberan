#!/bin/bash
# Helper script to check collected stock prices

show_help() {
    echo "Usage: ./scripts/check-prices.sh [command]"
    echo ""
    echo "Commands:"
    echo "  stats           Show collection statistics"
    echo "  latest [n]      Show latest n prices (default: 10)"
    echo "  ticker SYMBOL   Show prices for a specific ticker"
    echo "  today           Show all prices collected today"
    echo "  count           Count total records"
    echo "  morning         Show prices from 9-11 AM EST"
    echo "  all             Show all records"
    echo ""
}

case "$1" in
    stats)
        echo "📊 Collection Statistics:"
        curl -s http://localhost:8000/stocks/prices/stats | python3 -m json.tool
        ;;
    
    latest)
        LIMIT=${2:-10}
        echo "📈 Latest $LIMIT prices:"
        docker exec kuberan-mongodb mongosh kuberan --quiet --eval \
          "db.stock_prices.find().sort({timestamp: -1}).limit($LIMIT).forEach(
            doc => print(doc.ticker + ': $' + doc.current_price + ' at ' + doc.timestamp)
          )"
        ;;
    
    ticker)
        if [ -z "$2" ]; then
            echo "❌ Please specify a ticker symbol"
            exit 1
        fi
        TICKER=$(echo "$2" | tr '[:lower:]' '[:upper:]')
        echo "📊 Prices for $TICKER:"
        curl -s "http://localhost:8000/stocks/$TICKER/prices/collected?limit=20" | python3 -m json.tool
        ;;
    
    today)
        TODAY=$(date +%Y-%m-%d)
        echo "📅 Prices collected today ($TODAY):"
        docker exec kuberan-mongodb mongosh kuberan --quiet --eval \
          "db.stock_prices.find({
            timestamp: {
              \$gte: new Date('${TODAY}T00:00:00'),
              \$lt: new Date('${TODAY}T23:59:59')
            }
          }).count()"
        echo "records found"
        ;;
    
    count)
        echo "🔢 Total records:"
        docker exec kuberan-mongodb mongosh kuberan --quiet --eval \
          "db.stock_prices.countDocuments()"
        ;;
    
    morning)
        TODAY=$(date +%Y-%m-%d)
        echo "🌅 Prices from 9-11 AM EST today:"
        docker exec kuberan-mongodb mongosh kuberan --quiet --eval \
          "db.stock_prices.find({
            timestamp: {
              \$gte: new Date('${TODAY}T14:00:00Z'),
              \$lt: new Date('${TODAY}T16:00:00Z')
            }
          }).forEach(
            doc => print(doc.ticker + ': $' + doc.current_price + ' at ' + doc.timestamp)
          )"
        ;;
    
    all)
        echo "📋 All records by ticker:"
        docker exec kuberan-mongodb mongosh kuberan --quiet --eval \
          "db.stock_prices.aggregate([
            {\$group: {_id: '\$ticker', count: {\$sum: 1}}},
            {\$sort: {count: -1}}
          ])"
        ;;
    
    *)
        show_help
        ;;
esac
