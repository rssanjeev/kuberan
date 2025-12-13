"""
Ticker History Module - Historical price data

Endpoints:
    - GET /history/{ticker}: Get historical OHLCV price data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from app.services.stock.fetcher import stock_fetcher as stock_service
from app.repositories.provider_repository import provider_repository
from app.models.provider import DataSource

router = APIRouter()


@router.get("/history/{ticker}")
async def get_stock_history(
    ticker: str,
    period: Optional[str] = Query(
        "1mo",
        regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$",
        description="Time period for historical data"
    ),
    interval: str = Query(
        "1d",
        regex="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$",
        description="Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)"
    ),
    start_date: Optional[str] = Query(
        None,
        description="Start date (YYYY-MM-DD) for database query mode"
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date (YYYY-MM-DD) for database query mode"
    ),
    cache: bool = Query(
        True,
        description="Cache fetched data in database for future queries"
    )
) -> Dict[str, Any]:
    """
    Get historical OHLCV price data for a ticker.
    
    Two query modes:
    1. **Period-based** (default): Fetch from Yahoo Finance using period parameter
       - Returns up to 20+ years of data depending on ticker's trading history
       - Example: AAPL with period=max returns 40+ years (since 1980)
       - Data is fetched fresh and optionally cached
    
    2. **Date-range**: Query cached data from database using start_date and end_date
       - Only returns previously cached data
       - Faster but limited to what's been cached
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        start_date: Start date for database query (YYYY-MM-DD)
        end_date: End date for database query (YYYY-MM-DD)
        cache: If true, save fetched data to database (default: true)
    
    Returns:
        {
            "ticker": "AAPL",
            "period": "5y",
            "source": "yfinance" or "cache",
            "cached_count": 1260,  # If data was cached
            "data": [
                {
                    "Date": "2019-12-03",
                    "Open": 142.50,
                    "High": 145.20,
                    "Low": 141.80,
                    "Close": 144.95,
                    "Volume": 85234000,
                    "Adj Close": 138.45
                },
                ...
            ]
        }
    
    Examples:
        # Get 5 years of daily data (fetch from Yahoo Finance)
        GET /stocks/history/AAPL?period=5y
        
        # Get maximum available history (could be 40+ years for AAPL)
        GET /stocks/history/AAPL?period=max
        
        # Get 1 year of weekly data without caching
        GET /stocks/history/MSFT?period=1y&interval=1wk&cache=false
        
        # Query cached data for specific date range
        GET /stocks/history/SPY?start_date=2024-01-01&end_date=2024-12-01
    
    Notes:
        - Period-based queries always fetch from Yahoo Finance (fresh data)
        - Date-range queries only return cached data (fast but limited)
        - Cached data has 5-year TTL (automatically expires)
        - Split/dividend adjustments included in 'Adj Close' field
    """
    try:
        ticker = ticker.upper()
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        
        # Mode 1: Date-range query (database cache only)
        if start_date and end_date:
            logger.info(
                "Querying cached historical data",
                extra={"ticker": ticker, "start_date": start_date, "end_date": end_date, "interval": interval}
            )
            
            cached_prices = await provider_repository.get_historical_prices(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
            if not cached_prices:
                raise HTTPException(
                    status_code=404,
                    detail=f"No cached data found for {ticker} between {start_date} and {end_date}. Use period parameter to fetch from Yahoo Finance."
                )
            
            # Convert to response format
            data = [
                {
                    "Date": price.date,
                    "Open": price.open,
                    "High": price.high,
                    "Low": price.low,
                    "Close": price.close,
                    "Volume": price.volume,
                    "Adj Close": price.adjusted_close
                }
                for price in cached_prices
            ]
            
            return {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
                "source": "cache",
                "count": len(data),
                "data": data
            }
        
        # Mode 2: Period-based query (fetch from Yahoo Finance)
        logger.info(
            "Fetching historical data from Yahoo Finance",
            extra={"ticker": ticker, "period": period, "interval": interval, "cache": cache}
        )
        
        # Fetch from Yahoo Finance
        history = await stock_service.get_stock_history(ticker, period)
        
        if not history or not history.get('data'):
            raise HTTPException(
                status_code=404,
                detail=f"No historical data available for ticker {ticker}"
            )
        
        # Cache data in background if requested
        cached_count = 0
        if cache and history['data']:
            try:
                # Run caching in background (don't block response)
                async def cache_data():
                    return await provider_repository.save_historical_prices_bulk(
                        ticker=ticker,
                        historical_data=history['data'],
                        source=DataSource.YFINANCE,
                        interval=interval
                    )
                
                # Start background task
                cached_count = await cache_data()
                
                logger.info(
                    "Cached historical data",
                    extra={"ticker": ticker, "cached_count": cached_count, "total_records": len(history['data'])}
                )
            except Exception as e:
                logger.error(
                    "Failed to cache historical data",
                    extra={"ticker": ticker, "error": str(e)},
                    exc_info=True
                )
                # Don't fail the request if caching fails
        
        response = {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "source": "yfinance",
            "count": len(history['data']),
            "data": history['data']
        }
        
        if cache:
            response["cached_count"] = cached_count
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(
            "Error fetching stock history",
            extra={"ticker": ticker, "period": period, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch historical data for {ticker}: {str(e)}"
        )
