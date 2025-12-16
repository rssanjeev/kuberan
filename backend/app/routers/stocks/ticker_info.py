"""
Ticker Info Module - Individual ticker information and quotes

Endpoints:
    - GET /{ticker}: Get current stock information
    - GET /price/{ticker}: Get just the current price (lightweight)
    - GET /complete/{ticker}: Get comprehensive stock info (real-time + metadata)
    - GET /standardized/{ticker}: Get standardized ticker view with data sources
    - GET /related-companies/{ticker}: Get related companies
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from app.services.stock.fetcher import stock_fetcher as stock_service
from app.services.standardization_engine import StandardizationEngine
from app.models.provider import CompanyOverview, RelatedCompany
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


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
