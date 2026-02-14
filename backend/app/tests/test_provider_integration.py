"""
Test script for provider integration with repository layer.

Tests end-to-end data flow:
1. Provider fetches data
2. Repository saves data
3. Models persist to MongoDB
4. Data can be queried back

Usage:
    python3 test_provider_integration.py
"""

import asyncio
import sys
from datetime import datetime

from app.core.logging_config import get_logger
from app.services.providers.implementations.yfinance_provider import YFinanceProvider
from app.repositories.provider_repository import provider_repository
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import DOCUMENT_MODELS

logger = get_logger(__name__)


async def init_db():
    """Initialize database connection."""
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    await init_beanie(database=client.kuberan, document_models=DOCUMENT_MODELS)
    logger.info("Database initialized")


async def test_yfinance_quote():
    """Test YFinance real-time quote integration."""
    logger.info("=" * 60)
    logger.info("Testing YFinance Real-Time Quote")
    logger.info("=" * 60)
    
    provider = YFinanceProvider(priority=1)
    ticker = "AAPL"
    
    try:
        # Fetch quote
        logger.info(f"Fetching quote for {ticker}...")
        quote = await provider.get_real_time_quote(ticker)
        
        if quote:
            logger.info(f"✅ Quote fetched: {quote['symbol']} @ ${quote['price']}")
            
            # Verify data in MongoDB
            saved_quote = await provider_repository.get_latest_quote(ticker)
            
            if saved_quote:
                logger.info(f"✅ Quote found in MongoDB: {saved_quote.ticker} @ ${saved_quote.price}")
                logger.info(f"   Source: {saved_quote.source_provider}")
                logger.info(f"   Timestamp: {saved_quote.quote_timestamp}")
                return True
            else:
                logger.error(f"❌ Quote not found in MongoDB")
                return False
        else:
            logger.error(f"❌ Failed to fetch quote")
            return False
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def test_yfinance_historical():
    """Test YFinance historical prices integration."""
    logger.info("=" * 60)
    logger.info("Testing YFinance Historical Prices")
    logger.info("=" * 60)
    
    provider = YFinanceProvider(priority=1)
    ticker = "AAPL"
    
    try:
        # Fetch historical data (last 5 days)
        logger.info(f"Fetching historical data for {ticker}...")
        history = await provider.get_historical_prices(ticker, period="5d", interval="1d")
        
        if history and len(history) > 0:
            logger.info(f"✅ Fetched {len(history)} historical data points")
            logger.info(f"   Latest: {history[0]['date']} - Close: ${history[0]['close']}")
            
            # Verify data in MongoDB
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            saved_prices = await provider_repository.get_historical_prices(
                ticker=ticker,
                start_date=start_date.strftime("%Y-%m-%d"),  # Convert to string
                end_date=end_date.strftime("%Y-%m-%d"),      # Convert to string
                interval="1d"
            )
            
            if saved_prices and len(saved_prices) > 0:
                logger.info(f"✅ Found {len(saved_prices)} historical prices in MongoDB")
                logger.info(f"   Latest: {saved_prices[0].timestamp} - Close: ${saved_prices[0].close}")
                return True
            else:
                logger.error(f"❌ Historical prices not found in MongoDB")
                return False
        else:
            logger.error(f"❌ Failed to fetch historical data")
            return False
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def test_yfinance_dividends():
    """Test YFinance dividends integration."""
    logger.info("=" * 60)
    logger.info("Testing YFinance Dividends")
    logger.info("=" * 60)
    
    provider = YFinanceProvider(priority=1)
    ticker = "AAPL"
    
    try:
        # Fetch dividends
        logger.info(f"Fetching dividends for {ticker}...")
        dividends = await provider.get_dividends(ticker)
        
        if dividends and len(dividends) > 0:
            logger.info(f"✅ Fetched {len(dividends)} dividend records")
            logger.info(f"   Latest: {dividends[-1]['date']} - ${dividends[-1]['amount']}")
            
            # Verify data in MongoDB
            saved_dividends = await provider_repository.get_dividends(ticker)
            
            if saved_dividends and len(saved_dividends) > 0:
                logger.info(f"✅ Found {len(saved_dividends)} dividends in MongoDB")
                logger.info(f"   Latest: {saved_dividends[-1].ex_date} - ${saved_dividends[-1].amount}")
                return True
            else:
                logger.error(f"❌ Dividends not found in MongoDB")
                return False
        else:
            logger.warning(f"⚠️  No dividend data available for {ticker}")
            return True  # Not an error if no dividends exist
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def test_yfinance_news():
    """Test YFinance news integration."""
    logger.info("=" * 60)
    logger.info("Testing YFinance News")
    logger.info("=" * 60)
    
    provider = YFinanceProvider(priority=1)
    ticker = "AAPL"
    
    try:
        # Fetch news
        logger.info(f"Fetching news for {ticker}...")
        news = await provider.get_news(ticker, limit=5)
        
        if news and len(news) > 0:
            logger.info(f"✅ Fetched {len(news)} news articles")
            logger.info(f"   Latest: {news[0]['title'][:50]}...")
            
            # Verify data in MongoDB
            saved_news = await provider_repository.get_news_for_ticker(ticker, limit=5)
            
            if saved_news and len(saved_news) > 0:
                logger.info(f"✅ Found {len(saved_news)} news articles in MongoDB")
                logger.info(f"   Latest: {saved_news[0].title[:50]}...")
                return True
            else:
                logger.error(f"❌ News articles not found in MongoDB")
                return False
        else:
            logger.warning(f"⚠️  No news available for {ticker}")
            return True  # Not an error if no news
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def test_mongodb_indexes():
    """Test that MongoDB indexes are working."""
    logger.info("=" * 60)
    logger.info("Testing MongoDB Indexes")
    logger.info("=" * 60)
    
    try:
        from app.models.provider import StockQuote
        
        # Get index information
        indexes = await StockQuote.get_pymongo_collection().index_information()
        
        logger.info(f"✅ StockQuote collection has {len(indexes)} indexes:")
        for idx_name, idx_info in indexes.items():
            logger.info(f"   - {idx_name}: {idx_info.get('key', [])}")
        
        # Test compound index query performance
        ticker = "AAPL"
        quotes = await StockQuote.find(
            StockQuote.ticker == ticker
        ).sort(-StockQuote.quote_timestamp).limit(1).to_list()
        
        if quotes:
            logger.info(f"✅ Compound index query works: found latest quote for {ticker}")
            return True
        else:
            logger.warning(f"⚠️  No quotes found for {ticker} (may not have run previous tests)")
            return True
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def run_all_tests():
    """Run all integration tests."""
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("PROVIDER INTEGRATION TEST SUITE")
    logger.info("=" * 60)
    logger.info("\n")
    
    # Initialize database
    await init_db()
    
    # Run tests
    results = {}
    
    results["YFinance Quote"] = await test_yfinance_quote()
    await asyncio.sleep(2)  # Rate limiting
    
    results["YFinance Historical"] = await test_yfinance_historical()
    await asyncio.sleep(2)
    
    results["YFinance Dividends"] = await test_yfinance_dividends()
    await asyncio.sleep(2)
    
    results["YFinance News"] = await test_yfinance_news()
    await asyncio.sleep(2)
    
    results["MongoDB Indexes"] = await test_mongodb_indexes()
    
    # Summary
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
