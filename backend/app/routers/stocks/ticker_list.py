"""
Ticker List Module - List and filter tickers

Endpoints:
    - GET /tickers: List all tickers with filtering, sorting, pagination
    - GET /tickers/types: Get official ticker type classifications
"""
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from app.models.provider import CompanyOverview
from app.services.ticker_type_service import ticker_type_service

router = APIRouter()


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
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch ticker types"
        )
