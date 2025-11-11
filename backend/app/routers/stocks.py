"""
Stock Router - All stock-related API endpoints

IMPORTANT: When modifying endpoints in this file, update the API documentation:
    docs/API.md

This ensures the API documentation stays in sync with the actual implementation.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import pytz
from app.services.stock.fetcher import stock_fetcher as stock_service
from app.config_loader import config_loader
from app.services.jobs.price_collector import price_collector_job
from app.repositories.ticker_config_repository import ticker_config_repository
from app.repositories.stock_repository import stock_repository
from app.core.market_calendar import is_market_open
from app.models import StockPrice

router = APIRouter(prefix="/stocks", tags=["stocks"])

class TickerList(BaseModel):
    tickers: List[str]

@router.get("/configured")
async def get_configured_stocks():
    """
    Get stock information for all tickers configured in MongoDB.
    """
    tickers = await config_loader.get_tickers()
    if not tickers:
        raise HTTPException(status_code=404, detail="No tickers configured")
    
    stocks = await stock_service.get_multiple_stocks(tickers)
    return {
        "count": len(stocks),
        "stocks": stocks
    }

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

@router.get("/history/{ticker}")
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

@router.post("/poll/trigger")
async def trigger_price_poll():
    """
    Manually trigger a price poll for all configured tickers.
    Useful for testing the polling system.
    """
    result = await price_collector_job.run_manual()
    return result

@router.get("/market/status")
async def get_market_status():
    """
    Check if the NYSE market is open today.
    """
    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()
    is_open = is_market_open(today)
    
    return {
        "date": today.isoformat(),
        "is_market_open": is_open,
        "message": "Market is open for trading" if is_open else "Market is closed (holiday or weekend)"
    }

# Price-related endpoints
@router.get("/price/stats")
async def get_collection_stats():
    """
    Get statistics about collected price data.
    """
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

@router.get("/price/collected/{ticker}")
async def get_collected_prices(ticker: str, limit: int = 100):
    """
    Get collected price data from MongoDB for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of records to return (default 100)
    """
    # Pass start_time=None explicitly or use a very old date to get all records
    from datetime import timedelta
    prices = await stock_repository.get_price_history(
        ticker.upper(), 
        start_time=datetime.utcnow() - timedelta(days=365),  # Get last year of data
        limit=limit
    )
    
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

@router.get("/price/{ticker}")
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

# Ticker Management Endpoints
@router.get("/tickers/")
async def list_all_tickers():
    """
    List all configured tickers (enabled and disabled).
    Shows full ticker configuration with status and timestamps.
    """
    configs = await ticker_config_repository.get_all_tickers()
    return {
        "tickers": [
            {
                "ticker": c.ticker,
                "enabled": c.enabled,
                "added_at": c.added_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in configs
        ]
    }

@router.get("/tickers/active/")
async def list_active_tickers():
    """
    Get list of active (enabled) tickers only.
    """
    tickers = await config_loader.get_tickers()
    return {
        "tickers": tickers,
        "count": len(tickers)
    }

@router.post("/tickers/add/{ticker}")
async def add_ticker(ticker: str, enabled: bool = True):
    """
    Add a new ticker to the configuration.
    
    Args:
        ticker: Stock ticker symbol
        enabled: Whether to enable polling for this ticker (default: True)
    
    Raises:
        HTTPException 400: If ticker already exists
    """
    try:
        config = await ticker_config_repository.add_ticker(ticker, enabled)
        return {
            "message": f"Ticker {ticker} added successfully",
            "ticker": config.ticker,
            "enabled": config.enabled
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/tickers/remove/{ticker}")
async def remove_ticker(ticker: str):
    """
    Remove a ticker from configuration.
    
    Args:
        ticker: Stock ticker symbol to remove
    
    Raises:
        HTTPException 404: If ticker does not exist
    """
    try:
        await ticker_config_repository.remove_ticker(ticker)
        return {"message": f"Ticker {ticker} removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.put("/tickers/{ticker}/enable")
async def enable_ticker(ticker: str):
    """
    Enable polling for a ticker.
    
    Args:
        ticker: Stock ticker symbol
    """
    config = await ticker_config_repository.enable_ticker(ticker)
    if not config:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    return {
        "message": f"Ticker {ticker} enabled",
        "ticker": config.ticker,
        "enabled": config.enabled
    }

@router.put("/tickers/{ticker}/disable")
async def disable_ticker(ticker: str):
    """
    Disable polling for a ticker (keeps in database).
    
    Args:
        ticker: Stock ticker symbol
    """
    config = await ticker_config_repository.disable_ticker(ticker)
    if not config:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    return {
        "message": f"Ticker {ticker} disabled",
        "ticker": config.ticker,
        "enabled": config.enabled
    }

# Stock info endpoints (with {ticker} at the end)
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

