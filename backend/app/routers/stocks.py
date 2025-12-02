"""
Stock Router - All stock-related API endpoints

IMPORTANT: When modifying endpoints in this file, update the API documentation:
    docs/API.md

This ensures the API documentation stays in sync with the actual implementation.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import pytz
from app.services.stock.fetcher import stock_fetcher as stock_service
from app.core.market_calendar import is_market_open
from app.models.provider import CompanyOverview
from app.services.ticker_type_service import ticker_type_service
from typing import Dict, Any, List


router = APIRouter(prefix="/stocks", tags=["stocks"])

# New endpoint: List all tickers with metadata
@router.get("/tickers")
async def list_all_tickers(
    enrichment_status: Optional[str] = None,
    asset_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "market_cap",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = None,
    skip: int = 0
) -> Dict[str, Any]:
    """
    List all tickers with metadata (CompanyOverview).
    Supports filtering by enrichment_status, asset_type, search, sorting, and pagination.
    
    Args:
        enrichment_status: Filter by enrichment status (base, foundation, enriched, failed)
        asset_type: Filter by asset type (Stock, ETF)
        search: Substring match on ticker or name
        sort_by: Field to sort by (market_cap, ticker, name)
        sort_order: "asc" or "desc"
        limit: Max results (default None = all results, max 50000)
        skip: Pagination offset
    Returns:
        {
            "total": <int>,
            "returned": <int>,
            "skip": <int>,
            "limit": <int>,
            "tickers": [
                {
                    "ticker": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "market_cap": 2500000000000,
                    "enrichment_status": "foundation",
                    "asset_type": "Stock",
                    "exchange": "NASDAQ",
                    "country": "USA",
                    "fetched_at": "2025-11-30T10:00:00Z"
                    # ...other CompanyOverview fields
                },
                ...
            ]
        }
    """
    try:
        # Build query filters
        filters = []
        if enrichment_status:
            filters.append(CompanyOverview.enrichment_status == enrichment_status)
        if asset_type:
            filters.append(CompanyOverview.asset_type == asset_type)
        if search:
            # Use MongoDB regex for case-insensitive substring search
            from beanie.operators import Or, RegEx
            search_pattern = {"$regex": search, "$options": "i"}
            filters.append(
                Or(
                    {"ticker": search_pattern},
                    {"name": search_pattern}
                )
            )
        
        # Sorting
        sort_map = {
            "market_cap": "market_cap",
            "ticker": "ticker",
            "name": "name"
        }
        sort_field = sort_map.get(sort_by, "market_cap")
        sort_dir = -1 if sort_order == "desc" else 1
        
        # Limit and skip handling
        if limit is None:
            # No limit specified - return all results (up to 50k safety limit)
            limit = 50000
        else:
            # Limit specified - constrain to reasonable range
            limit = min(max(limit, 1), 50000)
        skip = max(skip, 0)
        
        # Query total count
        total = await CompanyOverview.find(*filters).count()
        
        # Query documents
        docs = await CompanyOverview.find(*filters).sort([(sort_field, sort_dir)]).skip(skip).limit(limit).to_list()
        
        # Format response
        tickers = []
        for doc in docs:
            tickers.append({
                "ticker": doc.ticker,
                "name": doc.name,
                "sector": doc.sector,
                "industry": doc.industry,
                "market_cap": doc.market_cap,
                "enrichment_status": doc.enrichment_status,
                "asset_type": doc.asset_type,
                "exchange": doc.exchange,
                "country": doc.country,
                "fetched_at": doc.fetched_at.isoformat() if doc.fetched_at else None
            })
        
        return {
            "total": total,
            "returned": len(tickers),
            "skip": skip,
            "limit": limit,
            "tickers": tickers
        }
    except Exception as e:
        # Log error and return empty result
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(
            "Failed to fetch tickers",
            extra={"error": str(e)},
            exc_info=True
        )
        return {
            "total": 0,
            "returned": 0,
            "skip": skip,
            "limit": limit,
            "tickers": []
        }


@router.get("/tickers/types")
async def get_ticker_types(
    asset_class: Optional[str] = None,
    locale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get official ticker type classifications from MASSIVE API.
    
    Returns reference data showing all valid ticker types (CS, ETF, ADRC, PFD, etc.)
    with descriptions. This is cached reference data - types rarely change.
    
    Args:
        asset_class: Filter by asset class (stocks, options, crypto, fx, indices)
        locale: Filter by locale (us, global)
        
    Returns:
        {
            "count": <int>,
            "results": [
                {
                    "code": "CS",
                    "description": "Common Stock",
                    "asset_class": "stocks",
                    "locale": "us"
                },
                {
                    "code": "ETF",
                    "description": "Exchange Traded Fund",
                    "asset_class": "stocks",
                    "locale": "us"
                }
            ]
        }
    
    Common Ticker Types:
        - CS: Common Stock
        - ETF: Exchange Traded Fund
        - ADRC: American Depository Receipt Common
        - PFD: Preferred Stock
        - WARRANT: Warrant
        - RIGHT: Rights
        - UNIT: Unit
        - FUND: Mutual Fund
        - INDEX: Index
        - ETN: Exchange Traded Note
        
    Use Cases:
        - Filter tickers by security type
        - Validate ticker type classifications
        - Educational reference for users
        - System integration and data classification
    """
    try:
        types = await ticker_type_service.get_types(
            asset_class=asset_class,
            locale=locale
        )
        
        return {
            "count": len(types),
            "results": [
                {
                    "code": t.code,
                    "description": t.description,
                    "asset_class": t.asset_class,
                    "locale": t.locale
                }
                for t in types
            ]
        }
    except Exception as e:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(
            "Failed to fetch ticker types",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch ticker types"
        )


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

# Stock info endpoints
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


@router.get("/config/routing")
async def get_provider_routing_config():
    """
    Get provider routing configuration showing which data source is used for each data type.
    
    Returns the system's current strategy for selecting providers:
    - Which provider is preferred for each data type (price, fundamentals, news, etc.)
    - Fallback providers if primary fails
    - Reasoning behind each choice
    
    This endpoint provides transparency into multi-provider data sourcing.
    
    Example response:
    {
        "routing_strategy": {
            "quote": {
                "primary": "yfinance",
                "fallback": ["alpha_vantage", "finnhub"],
                "reason": "YFinance free tier, good coverage for prices"
            },
            "company_overview": {
                "primary": "alpha_vantage",
                "fallback": ["finnhub"],
                "reason": "AlphaVantage provides more comprehensive company data"
            }
        },
        "last_updated": "2025-11-17T10:00:00Z"
    }
    """
    # Define provider routing configuration
    routing_config = {
        "quote": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage", "finnhub"],
            "reason": "YFinance free tier with good coverage, unlimited API calls",
            "data_points": ["price", "open", "high", "low", "volume", "change", "change_percent"]
        },
        "historical_prices": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance has 20+ years of historical data, free and unlimited",
            "data_points": ["OHLCV data", "adjusted close", "split/dividend adjustments"]
        },
        "company_overview": {
            "primary": "alpha_vantage",
            "fallback": ["finnhub"],
            "reason": "AlphaVantage provides comprehensive company fundamentals",
            "data_points": ["sector", "industry", "description", "market_cap", "pe_ratio", "address", "website"]
        },
        "fundamentals": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "Only AlphaVantage provides complete financial statements via MCP tools",
            "data_points": ["income_statement", "balance_sheet", "cash_flow", "earnings"]
        },
        "technical_indicators": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "AlphaVantage has 50+ technical indicators via MCP tools",
            "data_points": ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands", "40+ more"]
        },
        "dividends": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance has complete dividend history, free and unlimited",
            "data_points": ["dividend_date", "dividend_amount", "historical_dividends"]
        },
        "splits": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance provides detailed split history with ratios",
            "data_points": ["split_date", "split_ratio", "split_description"]
        },
        "earnings": {
            "primary": "alpha_vantage",
            "fallback": ["finnhub"],
            "reason": "AlphaVantage provides both historical and estimated earnings",
            "data_points": ["quarterly_earnings", "annual_earnings", "earnings_estimates"]
        },
        "news": {
            "primary": "finnhub",
            "fallback": ["alpha_vantage"],
            "reason": "Finnhub specializes in financial news with excellent coverage",
            "data_points": ["headline", "summary", "source", "timestamp", "sentiment"]
        },
        "analyst_ratings": {
            "primary": "finnhub",
            "fallback": [],
            "reason": "Only Finnhub provides analyst recommendations and upgrades/downgrades",
            "data_points": ["buy", "hold", "sell", "strong_buy", "strong_sell"]
        },
        "price_targets": {
            "primary": "finnhub",
            "fallback": [],
            "reason": "Finnhub provides analyst price targets",
            "data_points": ["target_high", "target_low", "target_mean", "target_median"]
        },
        "etf_holdings": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "Only AlphaVantage provides ETF holdings via ETF_PROFILE MCP tool",
            "data_points": ["holdings", "asset_allocation", "sector_weights", "top_10_holdings"]
        }
    }
    
    return {
        "routing_strategy": routing_config,
        "active_providers": ["yfinance", "alpha_vantage", "finnhub"],
        "can_switch_providers": True,
        "switch_method": "Update provider_routing_config.py or modify preferred_provider parameter in API calls",
        "last_updated": "2025-11-17T00:00:00Z",
        "documentation": "See docs/MULTI_PROVIDER_ARCHITECTURE.md for detailed architecture"
    }


