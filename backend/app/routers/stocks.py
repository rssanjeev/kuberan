"""
Stock Router - All stock-related API endpoints

IMPORTANT: When modifying endpoints in this file, update the API documentation:
    docs/API.md

This ensures the API documentation stays in sync with the actual implementation.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
import pytz
import asyncio
from app.services.stock.fetcher import stock_fetcher as stock_service
from app.core.market_calendar import is_market_open
from app.models.provider import CompanyOverview, DataSource
from app.services.ticker_type_service import ticker_type_service
from app.repositories.provider_repository import provider_repository
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
            # Check for exact match first
            exact_match = await CompanyOverview.find_one(
                CompanyOverview.ticker == search.upper()
            )
            
            if exact_match:
                # Found exact match - return only this ticker
                return {
                    "total": 1,
                    "returned": 1,
                    "skip": 0,
                    "limit": 1,
                    "tickers": [{
                        "ticker": exact_match.ticker,
                        "name": exact_match.name,
                        "sector": exact_match.sector,
                        "industry": exact_match.industry,
                        "market_cap": exact_match.market_cap,
                        "enrichment_status": exact_match.enrichment_status,
                        "asset_type": exact_match.asset_type,
                        "exchange": exact_match.exchange,
                        "country": exact_match.country,
                        "fetched_at": exact_match.fetched_at.isoformat() if exact_match.fetched_at else None
                    }]
                }
            
            # No exact match - use regex for partial matches
            from beanie.operators import Or
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
@router.get("/complete/{ticker}")
async def get_complete_stock_info(ticker: str):
    """
    Get comprehensive stock information combining real-time data and MASSIVE metadata.
    
    Combines:
    - Real-time pricing from Yahoo Finance (price, volume, day high/low, etc.)
    - MASSIVE foundation metadata from database (CIK, FIGI, logos, descriptions, etc.)
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA)
        
    Returns:
        Complete stock information with ~50+ fields including both real-time and metadata
    """
    from app.models.provider import CompanyOverview
    
    # Fetch real-time data from Yahoo Finance
    stock_data = await stock_service.get_stock_info(ticker.upper())
    if not stock_data:
        raise HTTPException(status_code=404, detail=f"Stock data not found for {ticker}")
    
    # Fetch MASSIVE metadata from database
    company_overview = await CompanyOverview.find_one(
        CompanyOverview.ticker == ticker.upper()
    )
    
    if not company_overview:
        # No MASSIVE data available, return just yfinance data
        return {
            **stock_data,
            "massive_metadata_available": False,
            "enrichment_status": None
        }
    
    # Merge yfinance data with MASSIVE metadata
    # yfinance data takes precedence for overlapping fields
    massive_data = {
        # Identifiers
        "cik": getattr(company_overview, "cik", None),
        "composite_figi": getattr(company_overview, "composite_figi", None),
        "share_class_figi": getattr(company_overview, "share_class_figi", None),
        "lei": getattr(company_overview, "lei", None),
        "sic_code": getattr(company_overview, "sic_code", None),
        "sic_description": getattr(company_overview, "sic_description", None),
        
        # Company info
        "description": getattr(company_overview, "description", None),
        "homepage_url": getattr(company_overview, "homepage_url", None),
        "total_employees": getattr(company_overview, "total_employees", None),
        "list_date": getattr(company_overview, "list_date", None),
        
        # Address
        "address": getattr(company_overview, "address", None),
        "phone_number": getattr(company_overview, "phone_number", None),
        
        # Branding
        "logo_url": getattr(company_overview, "logo_url", None),
        "icon_url": getattr(company_overview, "icon_url", None),
        
        # Financials
        "weighted_shares_outstanding": getattr(company_overview, "weighted_shares_outstanding", None),
        "share_class_shares_outstanding": getattr(company_overview, "share_class_shares_outstanding", None),
        
        # Metadata
        "enrichment_status": getattr(company_overview, "enrichment_status", None),
        "metadata_sources": getattr(company_overview, "metadata_sources", None),
        "massive_metadata_available": True,
        "fetched_at": company_overview.fetched_at.isoformat() if company_overview.fetched_at else None
    }
    
    # Merge with preference for yfinance real-time data
    return {**massive_data, **stock_data}


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
        
        # Mode 1: Date-range query (database cache only)
        if start_date and end_date:
            from app.core.logging_config import get_logger
            logger = get_logger(__name__)
            
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
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        
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


@router.get("/related-companies/{ticker}")
async def get_related_companies(
    ticker: str,
    limit: int = Query(20, ge=1, le=100),
    relationship_type: Optional[str] = None,
    min_correlation: Optional[float] = Query(None, ge=-1.0, le=1.0)
) -> Dict[str, Any]:
    """
    Get related companies (peers, competitors, correlated stocks) for a ticker.
    
    PHASE 4: Related Tickers Feature
    
    Returns companies with similar business models, market sectors, or price correlations.
    Useful for competitive analysis, sector tracking, and portfolio diversification.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum results (1-100, default 20)
        relationship_type: Filter by type (direct_competitor, sector_peer, correlated, loosely_related)
        min_correlation: Minimum correlation score (-1.0 to 1.0)
    
    Returns:
        {
            "ticker": "AAPL",
            "count": 8,
            "relationships": [
                {
                    "related_ticker": "MSFT",
                    "name": "Microsoft Corporation",
                    "relationship_type": "direct_competitor",
                    "correlation_score": 0.85,
                    "market_cap": 2800000000000,
                    "sector": "Technology",
                    "last_updated": "2025-12-01T10:30:00Z"
                },
                ...
            ]
        }
    
    Example:
        GET /stocks/related-companies/AAPL?limit=10&relationship_type=direct_competitor
    """
    from app.models.provider import RelatedCompany
    from app.core.logging_config import get_logger
    
    logger = get_logger(__name__)
    
    try:
        # Build query filters
        filters = [RelatedCompany.ticker == ticker.upper()]
        
        if relationship_type:
            filters.append(RelatedCompany.relationship_type == relationship_type)
        
        if min_correlation is not None:
            filters.append(RelatedCompany.correlation_score >= min_correlation)
        
        # Query RelatedCompany collection
        query = RelatedCompany.find(*filters)
        
        # Sort by correlation score descending (most correlated first)
        query = query.sort([("correlation_score", -1)])
        
        # Apply limit
        relationships = await query.limit(limit).to_list()
        
        if not relationships:
            return {
                "ticker": ticker.upper(),
                "count": 0,
                "relationships": [],
                "message": "No related companies found. Try running the background job to populate data."
            }
        
        # Transform to response format
        result_list = []
        
        for rel in relationships:
            # Fetch company overview for related ticker (if available)
            related_overview = await CompanyOverview.find_one(
                CompanyOverview.ticker == rel.related_ticker
            )
            
            result_list.append({
                "related_ticker": rel.related_ticker,
                "name": related_overview.name if related_overview else None,
                "relationship_type": rel.relationship_type,
                "correlation_score": rel.correlation_score,
                "market_cap": related_overview.market_cap if related_overview else None,
                "sector": related_overview.sector if related_overview else None,
                "industry": related_overview.industry if related_overview else None,
                "last_updated": rel.last_updated.isoformat() if rel.last_updated else None
            })
        
        logger.info(
            f"Returned {len(result_list)} related companies for {ticker}",
            extra={
                "ticker": ticker,
                "count": len(result_list),
                "relationship_type": relationship_type,
                "min_correlation": min_correlation
            }
        )
        
        return {
            "ticker": ticker.upper(),
            "count": len(result_list),
            "filters": {
                "relationship_type": relationship_type,
                "min_correlation": min_correlation,
                "limit": limit
            },
            "relationships": result_list
        }
    
    except Exception as e:
        logger.error(
            f"Failed to fetch related companies for {ticker}",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch related companies: {str(e)}"
        )



