from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.stock_service import stock_service
from app.config_loader import config_loader
from app.services.price_poller import price_poller

router = APIRouter(prefix="/stocks", tags=["stocks"])

class TickerList(BaseModel):
    tickers: List[str]

@router.get("/configured")
async def get_configured_stocks():
    """
    Get stock information for all tickers configured in YAML.
    """
    tickers = config_loader.get_tickers()
    if not tickers:
        raise HTTPException(status_code=404, detail="No tickers configured")
    
    stocks = await stock_service.get_multiple_stocks(tickers)
    return {
        "count": len(stocks),
        "stocks": stocks
    }

@router.get("/{ticker}")
async def get_stock(ticker: str):
    """
    Get current stock information for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
    """
    stock = await stock_service.get_stock_info(ticker.upper())
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock data not found for {ticker}")
    return stock

@router.get("/{ticker}/price")
async def get_stock_price(ticker: str):
    """
    Get just the current price for a specific ticker (lightweight).
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
    """
    price = await stock_service.get_stock_price(ticker.upper())
    if not price:
        raise HTTPException(status_code=404, detail=f"Price not found for {ticker}")
    return price

@router.post("/custom")
async def get_custom_stocks(ticker_list: TickerList):
    """
    Get stock information for a custom list of tickers.
    This endpoint allows frontend to override YAML configuration.
    
    Args:
        ticker_list: List of ticker symbols
    """
    if not ticker_list.tickers:
        raise HTTPException(status_code=400, detail="Ticker list cannot be empty")
    
    stocks = await stock_service.get_multiple_stocks(ticker_list.tickers)
    return {
        "count": len(stocks),
        "stocks": stocks
    }

@router.get("/{ticker}/history")
async def get_stock_history(ticker: str, period: str = "1mo"):
    """
    Get historical stock data for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    """
    history = await stock_service.get_stock_history(ticker.upper(), period)
    if not history:
        raise HTTPException(status_code=404, detail=f"History not found for {ticker}")
    return history

@router.get("/config/tickers")
async def get_configured_tickers():
    """
    Get the list of tickers configured in YAML.
    """
    return {
        "tickers": config_loader.get_tickers(),
        "refresh_interval": config_loader.get_refresh_interval()
    }

@router.post("/poll/trigger")
async def trigger_price_poll():
    """
    Manually trigger a price poll for all configured tickers.
    Useful for testing the polling system.
    """
    await price_poller.run_now()
    return {
        "message": "Price poll triggered successfully",
        "tickers": config_loader.get_tickers()
    }

@router.get("/{ticker}/prices/collected")
async def get_collected_prices(ticker: str, limit: int = 100):
    """
    Get collected price data from MongoDB for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of records to return (default 100)
    """
    from app.repositories.stock_repository import stock_repository
    
    prices = await stock_repository.get_price_history(ticker.upper(), limit)
    
    if not prices:
        return {
            "ticker": ticker.upper(),
            "count": 0,
            "prices": []
        }
    
    return {
        "ticker": ticker.upper(),
        "count": len(prices),
        "prices": [
            {
                "price": p.current_price,
                "timestamp": p.timestamp.isoformat()
            }
            for p in prices
        ]
    }

@router.get("/prices/stats")
async def get_collection_stats():
    """
    Get statistics about collected price data.
    """
    from app.models import StockPrice
    
    # Count total records
    total = await StockPrice.count()
    
    # Get unique tickers
    tickers = await StockPrice.distinct("ticker")
    
    # Get date range
    oldest = await StockPrice.find_all().sort("-timestamp").limit(1).to_list()
    newest = await StockPrice.find_all().sort("+timestamp").limit(1).to_list()
    
    return {
        "total_records": total,
        "tickers": sorted(tickers) if tickers else [],
        "ticker_count": len(tickers) if tickers else 0,
        "oldest_record": oldest[0].timestamp.isoformat() if oldest else None,
        "newest_record": newest[0].timestamp.isoformat() if newest else None
    }
