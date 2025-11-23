"""
ETF API Router.

Endpoints for ETF analysis including:
- ETF profile retrieval
- Holdings queries
- Sector allocations
- Comparable ETF discovery
"""

from typing import Optional, Dict
from fastapi import APIRouter, Query, Path, HTTPException, Body
from app.core.logging_config import get_logger
from app.services.etf.etf_profile_service import etf_profile_service
from app.services.etf.etf_comparison_service import etf_comparison_service
from app.services.etf.etf_discovery_service import etf_discovery_service
from app.services.etf.etf_screening_service import etf_screening_service
from app.services.etf.etf_performance_service import etf_performance_service
from app.services.etf.etf_tco_service import etf_tco_service
from app.services.etf.etf_portfolio_service import etf_portfolio_service
from app.services.etf.etf_dividend_service import etf_dividend_service
from app.services.etf.etf_tax_service import etf_tax_service
from app.services.etf.etf_risk_service import etf_risk_service
from app.services.etf.etf_theme_service import etf_theme_service
from app.services.etf.etf_investor_service import etf_investor_service
from app.services.etf.etf_analytics_service import etf_analytics_service
from app.services.etf.etf_backtesting_service import etf_backtesting_service
from app.services.etf.etf_data_service import etf_data_service

logger = get_logger(__name__)

router = APIRouter(prefix="/etf", tags=["ETF Analysis"])


@router.get("/profile/{ticker}")
async def get_etf_profile(
    ticker: str,
    force_refresh: bool = Query(False, description="Force refresh from API (bypass cache)")
):
    """
    Get complete ETF profile including fundamentals, holdings, and sectors.
    
    **Caching**: Profiles are cached for 30 days by default.
    
    **Example**: `GET /etf/profile/SPY`
    
    **Response**:
    ```json
    {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "fundamentals": {
            "net_assets": 450000000000,
            "net_expense_ratio": 0.0009,
            "expense_ratio_pct": 0.09,
            "dividend_yield": 0.0125,
            "dividend_yield_pct": 1.25
        },
        "holdings": {
            "total": 503,
            "top_10": [...],
            "complete_list": [...]
        },
        "sectors": [...],
        "metadata": {
            "source_provider": "ALPHA_VANTAGE",
            "last_updated": "2025-11-23T..."
        }
    }
    ```
    
    **Parameters**:
    - `ticker`: ETF ticker symbol (case-insensitive)
    - `force_refresh`: Bypass cache and fetch fresh data (optional, default=false)
    
    **Returns**: Complete ETF profile with holdings and sectors
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid ticker
    - 404: ETF not found
    - 429: Rate limit exceeded
    - 500: Server error
    """
    try:
        logger.info("GET /etf/profile/{ticker}", extra={"ticker": ticker})
        
        profile = await etf_profile_service.get_etf_profile(
            ticker=ticker,
            force_refresh=force_refresh
        )
        
        logger.info(
            "ETF profile request successful",
            extra={"ticker": ticker, "holdings": profile.get("holdings", {}).get("total", 0)}
        )
        
        return profile
        
    except ValueError as e:
        logger.warning("Invalid ETF profile request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF profile request failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        
        # Check for rate limit in error message
        if "rate limit" in str(e).lower() or "api call frequency" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        raise HTTPException(status_code=500, detail="Failed to fetch ETF profile")


@router.get("/holdings/{ticker}")
async def get_etf_holdings(
    ticker: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Max holdings to return"),
    min_weight: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum weight (e.g., 0.01 for 1%)")
):
    """
    Get ETF holdings list with optional filtering.
    
    **Example**: `GET /etf/holdings/SPY?limit=10&min_weight=0.01`
    
    **Response**:
    ```json
    {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "total_holdings": 503,
        "returned_count": 10,
        "holdings": [
            {
                "symbol": "NVDA",
                "description": "NVIDIA CORP",
                "weight": 0.0783,
                "weight_pct": 7.83
            },
            ...
        ],
        "last_updated": "2025-11-23T..."
    }
    ```
    
    **Parameters**:
    - `ticker`: ETF ticker symbol
    - `limit`: Maximum number of holdings to return (optional)
    - `min_weight`: Minimum weight threshold as decimal (optional, e.g., 0.01 = 1%)
    
    **Returns**: Holdings list with filtering applied
    
    **Use Cases**:
    - Top 10 holdings: `?limit=10`
    - Holdings >1%: `?min_weight=0.01`
    - Large positions only: `?min_weight=0.05`
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid parameters
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info(
            "GET /etf/holdings/{ticker}",
            extra={"ticker": ticker, "limit": limit, "min_weight": min_weight}
        )
        
        holdings = await etf_profile_service.get_etf_holdings(
            ticker=ticker,
            limit=limit,
            min_weight=min_weight
        )
        
        logger.info(
            "ETF holdings request successful",
            extra={
                "ticker": ticker,
                "total": holdings.get("total_holdings"),
                "returned": holdings.get("returned_count")
            }
        )
        
        return holdings
        
    except ValueError as e:
        logger.warning("Invalid ETF holdings request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF holdings request failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to fetch ETF holdings")


@router.get("/sectors/{ticker}")
async def get_etf_sectors(ticker: str):
    """
    Get ETF sector allocation breakdown.
    
    **Example**: `GET /etf/sectors/SPY`
    
    **Response**:
    ```json
    {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "sector_allocations": [
            {
                "sector": "INFORMATION TECHNOLOGY",
                "weight": 0.348,
                "weight_pct": 34.8
            },
            {
                "sector": "FINANCIALS",
                "weight": 0.112,
                "weight_pct": 11.2
            },
            ...
        ],
        "last_updated": "2025-11-23T..."
    }
    ```
    
    **Parameters**:
    - `ticker`: ETF ticker symbol
    
    **Returns**: Sector allocation with percentages
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid ticker
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info("GET /etf/sectors/{ticker}", extra={"ticker": ticker})
        
        sectors = await etf_profile_service.get_etf_sectors(ticker=ticker)
        
        logger.info(
            "ETF sectors request successful",
            extra={"ticker": ticker, "sectors": len(sectors.get("sector_allocations", []))}
        )
        
        return sectors
        
    except ValueError as e:
        logger.warning("Invalid ETF sectors request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF sectors request failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to fetch ETF sectors")




@router.get("/compare")
async def compare_etfs(
    ticker1: str = Query(..., description="First ETF ticker symbol"),
    ticker2: str = Query(..., description="Second ETF ticker symbol"),
    force_refresh: bool = Query(False, description="Force fresh data fetch, bypass cache")
):
    """
    Compare two ETFs side-by-side.
    
    Provides comprehensive comparison including:
    - Holdings overlap by weight
    - Common vs unique holdings
    - Sector allocation drift
    - Overweight/underweight positions
    
    **Overlap Calculation**: weighted methodology
    `overlap = sum(min(weight1[stock], weight2[stock])) for all common stocks`
    
    **Example**: `GET /etf/compare?ticker1=SPY&ticker2=QQQ`
    
    **Expected Results**:
    - SPY vs QQQ: ~52% overlap (QQQ is tech-heavy)
    - SPY vs VOO: ~98.5% overlap (nearly identical S&P 500 ETFs)
    - QQQ vs VGT: ~70% overlap (both tech-focused)
    
    **Response**:
    ```json
    {
        "ticker1": "SPY",
        "ticker2": "QQQ",
        "comparison_summary": {
            "overlap_by_weight": 0.52,
            "overlap_by_weight_pct": 52.0,
            "common_holdings_count": 88
        },
        "common_holdings": {
            "count": 88,
            "top_20": [...]
        },
        "sector_drift": [...],
        "overweight_positions": {
            "etf1": [...],
            "etf2": [...]
        }
    }
    ```
    
    Args:
        ticker1: First ETF ticker symbol
        ticker2: Second ETF ticker symbol
        force_refresh: If True, bypass cache and fetch fresh data
        
    Returns:
        Complete comparison with overlap, drift, and position analysis
        
    Status Codes:
        - 200: Success
        - 400: Invalid tickers
        - 404: One or both ETFs not found
        - 429: Rate limit exceeded
        - 500: Server error
    """
    try:
        logger.info(
            "Comparing ETFs",
            extra={"ticker1": ticker1, "ticker2": ticker2, "force_refresh": force_refresh}
        )
        
        comparison = await etf_comparison_service.compare_etfs(
            ticker1=ticker1,
            ticker2=ticker2,
            force_refresh=force_refresh
        )
        
        return comparison
    
    except ValueError as e:
        logger.error(
            "Invalid comparison parameters",
            extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        elif "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        else:
            logger.error(
                "Failed to compare ETFs",
                extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)},
                exc_info=True
            )
            raise HTTPException(status_code=500, detail="Failed to compare ETFs")


@router.get("/search")
async def search_etfs_by_stock(
    stock: str = Query(..., description="Stock ticker symbol (e.g., AAPL, NVDA)"),
    min_weight: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum weight threshold (0.0-1.0). Example: 0.05 = only ETFs with >5% allocation"
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
):
    """
    Find all ETFs that hold a specific stock.
    
    **Use Cases**:
    - Discover ETF exposure: "Which ETFs hold AAPL?"
    - Find largest holders: "Which ETFs have >5% NVDA?"
    - Compare sector ETFs: Which tech ETFs hold MSFT?
    
    **How It Works**:
    1. Searches all cached ETF profiles in database
    2. Filters by minimum weight threshold (if specified)
    3. Sorts by weight (largest holders first)
    4. Returns ETF details + holding information
    
    **Examples**:
    ```
    # Find all ETFs holding Apple
    GET /etf/search?stock=AAPL
    
    # Find ETFs with >5% Apple allocation
    GET /etf/search?stock=AAPL&min_weight=0.05
    
    # Top 10 NVDA holders
    GET /etf/search?stock=NVDA&limit=10
    ```
    
    **Response Structure**:
    ```json
    {
      "stock_symbol": "AAPL",
      "total_etfs_found": 45,
      "statistics": {
        "average_weight": 0.0543,
        "average_weight_pct": 5.43,
        "highest_weight_etf": "QQQ",
        "highest_weight_pct": 8.71
      },
      "etfs": [
        {
          "ticker": "QQQ",
          "name": "Invesco QQQ Trust",
          "weight": 0.0871,
          "weight_pct": 8.71,
          "rank": 2,  // AAPL is 2nd largest holding
          "total_holdings": 102,
          "expense_ratio_pct": 0.20
        }
      ]
    }
    ```
    
    **Notes**:
    - Only searches ETFs already in database (call /etf/profile/{ticker} first to cache)
    - Results sorted by weight (descending)
    - Weight = percentage of ETF allocated to this stock
    - Rank = position in ETF's holdings (1 = largest holding)
    
    Args:
        stock: Stock ticker symbol (case-insensitive)
        min_weight: Minimum weight threshold (0.0 to 1.0, optional)
        limit: Maximum results to return (optional)
        
    Returns:
        List of ETFs holding the stock with detailed holding information
        
    Raises:
        400: Invalid stock symbol or parameters
        500: Internal server error
    """
    try:
        result = await etf_discovery_service.find_etfs_holding_stock(
            stock_symbol=stock.upper(),
            min_weight=min_weight,
            limit=limit
        )
        return result
    
    except ValueError as e:
        # Invalid input
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            "Failed to search ETFs by stock",
            extra={
                "stock": stock,
                "min_weight": min_weight,
                "error": str(e)
            },
            exc_info=True
        )
        
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to search ETFs by stock"
            )


@router.get("/exposure/{stock}")
async def get_stock_exposure_summary(
    stock: str = Path(..., description="Stock ticker symbol (e.g., AAPL, NVDA)")
):
    """
    Get comprehensive ETF exposure summary for a stock.
    
    **Provides**:
    - Categorization by weight (heavy/moderate/light holders)
    - Top 10 position analysis (ETFs where stock is in top 10)
    - Statistics across all holders
    
    **Categories**:
    - **Heavy Holders**: >5% allocation (concentrated exposure)
    - **Moderate Holders**: 1-5% allocation (balanced exposure)
    - **Light Holders**: <1% allocation (diversified exposure)
    - **Top 10 Positions**: Stock is in ETF's top 10 holdings
    
    **Use Cases**:
    - Understand ETF exposure landscape for a stock
    - Identify specialized vs broad market ETFs
    - Compare tech ETFs vs S&P 500 ETFs
    
    **Example**:
    ```
    GET /etf/exposure/AAPL
    
    Response:
    {
      "stock_symbol": "AAPL",
      "total_etfs_found": 45,
      "exposure_breakdown": {
        "heavy_holders": {
          "count": 3,
          "description": "ETFs with >5% allocation",
          "etfs": [{"ticker": "QQQ", "weight_pct": 8.71}, ...]
        },
        "top_10_positions": {
          "count": 12,
          "description": "ETFs where stock is in top 10 holdings"
        }
      },
      "top_holders": [...]  // Top 5 by weight
    }
    ```
    
    Args:
        stock: Stock ticker symbol
        
    Returns:
        Comprehensive exposure summary with categorization
        
    Raises:
        400: Invalid stock symbol
        500: Internal server error
    """
    try:
        result = await etf_discovery_service.get_stock_exposure_summary(
            stock_symbol=stock.upper()
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            "Failed to get stock exposure summary",
            extra={"stock": stock, "error": str(e)},
            exc_info=True
        )
        
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to get stock exposure summary"
            )


@router.get("/screen")
async def screen_etfs(
    # Sector filters
    sector: Optional[str] = Query(None, description="Sector name (e.g., 'INFORMATION TECHNOLOGY', 'FINANCIALS')"),
    min_sector_weight: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum sector allocation (0.0-1.0). Example: 0.30 = >30% in sector"
    ),
    
    # Fundamental filters
    min_assets: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum AUM in dollars. Example: 1000000000 = $1B"
    ),
    max_expense_ratio: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Maximum expense ratio (0.0-1.0). Example: 0.001 = 0.1% (10 bps)"
    ),
    min_dividend_yield: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum dividend yield (0.0-1.0)"
    ),
    
    # Holdings filters
    min_holdings: Optional[int] = Query(
        None,
        ge=1,
        description="Minimum number of holdings (for focused ETFs)"
    ),
    max_holdings: Optional[int] = Query(
        None,
        ge=1,
        description="Maximum number of holdings (for diversified ETFs)"
    ),
    
    # Sorting
    sort_by: str = Query(
        "net_assets",
        description="Sort field: 'net_assets', 'expense_ratio', 'total_holdings'"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: 'asc' or 'desc'"
    ),
    
    # Pagination
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum results to return"
    )
):
    """
    Screen ETFs based on multiple criteria.
    
    **Advanced Filtering** - Find ETFs matching specific investment criteria
    
    **Use Cases**:
    - **Large-cap tech ETFs**: sector="INFORMATION TECHNOLOGY", min_sector_weight=0.30, min_assets=1B
    - **Low-cost S&P 500 ETFs**: max_expense_ratio=0.001, min_holdings=400
    - **Focused sector ETFs**: sector="HEALTHCARE", min_sector_weight=0.80, max_holdings=100
    - **Dividend ETFs**: min_dividend_yield=0.02, min_assets=500M
    
    **Examples**:
    ```
    # Find large tech ETFs with >30% tech allocation
    GET /etf/screen?sector=INFORMATION TECHNOLOGY&min_sector_weight=0.30&min_assets=1000000000
    
    # Find low-cost S&P 500 ETFs
    GET /etf/screen?max_expense_ratio=0.001&min_holdings=400&min_assets=10000000000
    
    # Find focused healthcare ETFs
    GET /etf/screen?sector=HEALTHCARE&min_sector_weight=0.80&max_holdings=100
    ```
    
    **Response Structure**:
    ```json
    {
      "total_etfs_screened": 15,
      "total_matches": 3,
      "etfs": [
        {
          "ticker": "QQQ",
          "total_holdings": 102,
          "net_assets_billions": 410.8,
          "expense_ratio_pct": 0.20,
          "expense_ratio_bps": 20,
          "sector_allocation": {
            "sector": "INFORMATION TECHNOLOGY",
            "weight_pct": 48.5
          },
          "top_sectors": [...]
        }
      ],
      "filters_applied": {...}
    }
    ```
    
    **Notes**:
    - Only screens ETFs already in database (fetch profiles first)
    - All filters are AND-ed together (must match all criteria)
    - Expense ratio in basis points: 20 bps = 0.20%
    - Assets in billions for readability
    
    Args:
        sector: Sector name (case-insensitive)
        min_sector_weight: Minimum allocation to specified sector
        min_assets: Minimum AUM in dollars
        max_expense_ratio: Maximum expense ratio (fraction)
        min_dividend_yield: Minimum dividend yield (fraction)
        min_holdings: Minimum number of holdings
        max_holdings: Maximum number of holdings
        sort_by: Field to sort by
        sort_order: "asc" or "desc"
        limit: Maximum results to return
        
    Returns:
        List of ETFs matching all criteria with detailed metrics
        
    Raises:
        400: Invalid parameters
        500: Internal server error
    """
    try:
        result = await etf_screening_service.screen_etfs(
            sector=sector,
            min_sector_weight=min_sector_weight,
            min_assets=min_assets,
            max_expense_ratio=max_expense_ratio,
            min_dividend_yield=min_dividend_yield,
            min_holdings=min_holdings,
            max_holdings=max_holdings,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            "Failed to screen ETFs",
            extra={
                "sector": sector,
                "min_sector_weight": min_sector_weight,
                "error": str(e)
            },
            exc_info=True
        )
        
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to screen ETFs"
            )


@router.get("/similar/{ticker}")
async def find_similar_etfs(
    ticker: str = Path(..., description="Reference ETF ticker (e.g., SPY)"),
    max_expense_ratio_delta: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Max expense ratio difference. Example: 0.001 = within 0.1%"
    ),
    max_holdings_delta: Optional[int] = Query(
        None,
        ge=0,
        description="Max holdings count difference"
    ),
    limit: Optional[int] = Query(
        10,
        ge=1,
        le=50,
        description="Maximum results to return"
    )
):
    """
    Find ETFs similar to a reference ETF.
    
    **Similarity Metrics**:
    - Sector allocation similarity (primary metric)
    - Expense ratio proximity
    - Holdings count similarity
    
    **Use Cases**:
    - Find alternatives to SPY (other S&P 500 ETFs)
    - Discover lower-cost equivalents
    - Compare similar sector ETFs
    
    **Examples**:
    ```
    # Find ETFs similar to SPY
    GET /etf/similar/SPY?limit=5
    
    # Find low-cost alternatives (within 0.05% expense ratio)
    GET /etf/similar/SPY?max_expense_ratio_delta=0.0005&limit=10
    
    # Find similar ETFs with similar holdings count (±50 holdings)
    GET /etf/similar/QQQ?max_holdings_delta=50
    ```
    
    **Response Structure**:
    ```json
    {
      "reference_ticker": "SPY",
      "reference_etf": {
        "ticker": "SPY",
        "total_holdings": 504,
        "expense_ratio": 0.000945
      },
      "total_similar_found": 2,
      "similar_etfs": [
        {
          "ticker": "VOO",
          "holdings_delta": -39,
          "expense_ratio_delta": -0.000645,
          "sector_similarity": 0.9856,
          "sector_similarity_pct": 98.56
        }
      ]
    }
    ```
    
    **Similarity Score**: 0-100%, where 100% = identical sector allocations
    
    Args:
        ticker: Reference ETF ticker
        max_expense_ratio_delta: Max difference in expense ratio
        max_holdings_delta: Max difference in holdings count
        limit: Maximum results to return
        
    Returns:
        List of similar ETFs sorted by sector similarity
        
    Raises:
        400: Invalid ticker
        404: Reference ETF not found
        500: Internal server error
    """
    try:
        result = await etf_screening_service.find_similar_etfs(
            reference_ticker=ticker.upper(),
            max_expense_ratio_delta=max_expense_ratio_delta,
            max_holdings_delta=max_holdings_delta,
            limit=limit
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            "Failed to find similar ETFs",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to find similar ETFs"
            )


@router.get("/comparables/{ticker}")
async def get_comparable_etfs(
    ticker: str,
    limit: int = Query(10, ge=1, le=50, description="Max comparables to return")
):
    """
    Find comparable ETFs based on holdings overlap.
    
    **Note**: Full implementation requires Phase 2 (ETF Comparison Service).
    Currently returns placeholder response.
    
    **Example**: `GET /etf/comparables/SPY?limit=10`
    
    **Future Response** (Phase 2):
    ```json
    {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "comparables": [
            {
                "ticker": "VOO",
                "name": "Vanguard S&P 500 ETF",
                "overlap_pct": 0.985,
                "expense_ratio": 0.0003,
                "assets": 459000000000
            },
            ...
        ]
    }
    ```
    
    **Parameters**:
    - `ticker`: ETF ticker symbol
    - `limit`: Maximum number of comparables to return (default=10)
    
    **Returns**: List of comparable ETFs sorted by overlap
    
    **Status Codes**:
    - 200: Success (currently with note about Phase 2)
    - 400: Invalid ticker
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info(
            "GET /etf/comparables/{ticker}",
            extra={"ticker": ticker, "limit": limit}
        )
        
        comparables = await etf_profile_service.get_comparable_etfs(
            ticker=ticker,
            limit=limit
        )
        
        logger.info(
            "ETF comparables request successful",
            extra={"ticker": ticker, "count": len(comparables.get("comparables", []))}
        )
        
        return comparables
        
    except ValueError as e:
        logger.warning("Invalid ETF comparables request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF comparables request failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to fetch comparable ETFs")


# ==================== Phase 5: Performance Endpoints ====================

# NOTE: /performance/compare MUST come before /performance/{ticker}
# to avoid "compare" being interpreted as a ticker

@router.get("/performance/compare")
async def compare_etf_performance(
    ticker1: str = Query(..., description="First ETF ticker"),
    ticker2: str = Query(..., description="Second ETF ticker"),
    period: str = Query("1Y", description="Comparison period (1D, 1W, 1M, 3M, YTD, 1Y)")
):
    """
    Compare performance of two ETFs over a specific period.
    
    **Returns**:
    - Side-by-side performance comparison
    - Return differences
    - Risk-adjusted metrics (Sharpe ratio)
    - Winner determination
    
    **Example**: `GET /etf/performance/compare?ticker1=VOO&ticker2=SPY&period=1Y`
    
    **Response**:
    ```json
    {
        "ticker1": "VOO",
        "ticker2": "SPY",
        "period": "1Y",
        "comparison": {
            "ticker1_return": 0.2888,
            "ticker2_return": 0.2876,
            "return_difference": 0.0012,
            "return_difference_pct": 0.12,
            "winner": "VOO"
        },
        "risk_comparison": {
            "ticker1_volatility": 0.1230,
            "ticker2_volatility": 0.1235,
            "volatility_difference": -0.0005,
            "ticker1_sharpe": 1.87,
            "ticker2_sharpe": 1.85,
            "sharpe_difference": 0.02,
            "better_risk_adjusted": "VOO"
        }
    }
    ```
    
    **Valid Periods**:
    - `1D`: 1-day return
    - `1W`: 1-week return
    - `1M`: 1-month return
    - `3M`: 3-month return
    - `YTD`: Year-to-date return
    - `1Y`: 1-year return
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid input
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info(
            "GET /etf/performance/compare",
            extra={"ticker1": ticker1, "ticker2": ticker2, "period": period}
        )
        
        comparison = await etf_performance_service.compare_etf_performance(
            ticker1=ticker1,
            ticker2=ticker2,
            period=period
        )
        
        logger.info(
            "ETF performance comparison successful",
            extra={
                "ticker1": ticker1,
                "ticker2": ticker2,
                "winner": comparison['comparison'].get('winner')
            }
        )
        
        return comparison
        
    except ValueError as e:
        logger.warning("Invalid ETF comparison request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF comparison request failed",
            extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to compare ETF performance")


@router.get("/performance/{ticker}")
async def get_etf_performance(
    ticker: str = Path(..., description="ETF ticker symbol"),
    force_refresh: bool = Query(False, description="Force fresh data fetch")
):
    """
    Get comprehensive performance metrics for an ETF.
    
    **Returns**:
    - Multi-period returns (1D, 1W, 1M, 3M, YTD, 1Y)
    - Risk metrics (volatility, Sharpe ratio, max drawdown)
    - Current price and date
    
    **Example**: `GET /etf/performance/SPY`
    
    **Response**:
    ```json
    {
        "ticker": "SPY",
        "current_price": 458.32,
        "as_of_date": "2025-11-22",
        "returns": {
            "1D": 0.0123,
            "1W": 0.0234,
            "1M": 0.0456,
            "3M": 0.0789,
            "YTD": 0.2145,
            "1Y": 0.2876
        },
        "risk_metrics": {
            "volatility_30d": 0.1234,
            "volatility_90d": 0.1456,
            "sharpe_ratio": 1.85,
            "max_drawdown": -0.0567
        }
    }
    ```
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid ticker
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info(
            "GET /etf/performance/{ticker}",
            extra={"ticker": ticker, "force_refresh": force_refresh}
        )
        
        performance = await etf_performance_service.get_etf_performance(
            ticker=ticker,
            force_refresh=force_refresh
        )
        
        logger.info(
            "ETF performance request successful",
            extra={"ticker": ticker, "1Y_return": performance['returns'].get('1Y')}
        )
        
        return performance
        
    except ValueError as e:
        logger.warning("Invalid ETF performance request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ETF performance request failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to fetch ETF performance")


# ================================
# Phase 6: Total Cost of Ownership
# ================================

@router.post("/tco")
async def calculate_etf_tco(
    ticker: str = Query(..., description="ETF ticker symbol"),
    holding_periods: list[int] = Query([1, 3, 5, 10], description="Holding periods in years"),
    commission: float = Query(0.0, description="Trading commission per transaction")
):
    """
    Calculate Total Cost of Ownership (TCO) for an ETF over multiple holding periods.
    
    **TCO Components**:
    - **Expense Ratio**: Annual management fee (from ETF profile)
    - **Bid/Ask Spread**: Trading cost estimated from volume (2x for buy + sell)
    - **Commission**: Broker fee per transaction (2x for buy + sell)
    
    **Formula**: `TCO = (expense_ratio × years) + (spread × 2) + (commission × 2)`
    
    **Use Case**: Understand true ownership costs before investing.
    
    **Example**: `POST /etf/tco?ticker=SPY&holding_periods=1&holding_periods=5&commission=0`
    
    **Response**:
    ```json
    {
        "ticker": "SPY",
        "expense_ratio": 0.0009,
        "bid_ask_spread_pct": 0.0001,
        "commission": 0.0,
        "tco_by_period": {
            "1y": {
                "expense_ratio_cost": 0.09,
                "spread_cost": 0.02,
                "commission_cost": 0.0,
                "total_tco_pct": 0.11
            },
            "5y": {
                "expense_ratio_cost": 0.45,
                "spread_cost": 0.02,
                "commission_cost": 0.0,
                "total_tco_pct": 0.47
            }
        }
    }
    ```
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid ticker or parameters
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/tco",
            extra={
                "ticker": ticker,
                "holding_periods": holding_periods,
                "commission": commission
            }
        )
        
        tco = await etf_tco_service.calculate_multi_period_tco(
            ticker=ticker,
            periods=holding_periods,
            commission=commission
        )
        
        logger.info(
            "ETF TCO calculation successful",
            extra={
                "ticker": ticker,
                "periods": list(tco['periods'].keys())
            }
        )
        
        return tco
        
    except ValueError as e:
        logger.warning("Invalid TCO calculation request", extra={"ticker": ticker, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "TCO calculation failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to calculate TCO")


@router.post("/tco/compare")
async def compare_etf_tco(
    ticker1: str = Query(..., description="First ETF ticker symbol"),
    ticker2: str = Query(..., description="Second ETF ticker symbol"),
    holding_period_years: int = Query(5, description="Holding period in years"),
    commission: float = Query(0.0, description="Trading commission per transaction")
):
    """
    Compare Total Cost of Ownership between two ETFs.
    
    **Purpose**: Help choose between similar ETFs (e.g., SPY vs VOO vs IVV).
    
    **Returns**:
    - Side-by-side cost breakdown
    - Difference in percentage points
    - Dollar savings per $10k invested
    - Dollar savings per $100k invested
    
    **Use Case**: "Should I buy SPY (0.09% ER) or VOO (0.03% ER) for long-term holding?"
    
    **Example**: `POST /etf/tco/compare?ticker1=SPY&ticker2=VOO&holding_period_years=5&commission=0`
    
    **Response**:
    ```json
    {
        "ticker1": "SPY",
        "ticker2": "VOO",
        "holding_period_years": 5,
        "commission": 0.0,
        "ticker1_tco": {
            "expense_ratio": 0.0009,
            "expense_ratio_cost": 0.45,
            "spread_cost": 0.02,
            "commission_cost": 0.0,
            "total_tco_pct": 0.47
        },
        "ticker2_tco": {
            "expense_ratio": 0.0003,
            "expense_ratio_cost": 0.15,
            "spread_cost": 0.01,
            "commission_cost": 0.0,
            "total_tco_pct": 0.16
        },
        "comparison": {
            "difference_pct": 0.31,
            "savings_per_10k": 155,
            "savings_per_100k": 1550,
            "cheaper_etf": "VOO"
        }
    }
    ```
    
    **Interpretation**:
    - VOO is 0.31% cheaper over 5 years
    - On $10k investment: Save $155
    - On $100k investment: Save $1,550
    - VOO is the cheaper option
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid tickers or parameters
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/tco/compare",
            extra={
                "ticker1": ticker1,
                "ticker2": ticker2,
                "holding_period_years": holding_period_years,
                "commission": commission
            }
        )
        
        comparison = await etf_tco_service.compare_tco(
            ticker1=ticker1,
            ticker2=ticker2,
            holding_period_years=holding_period_years,
            commission=commission
        )
        
        logger.info(
            "ETF TCO comparison successful",
            extra={
                "ticker1": ticker1,
                "ticker2": ticker2,
                "cheaper_etf": comparison['comparison']['cheaper_etf'],
                "savings": comparison['comparison']['savings_with_cheaper']
            }
        )
        
        return comparison
        
    except ValueError as e:
        logger.warning(
            "Invalid TCO comparison request",
            extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "TCO comparison failed",
            extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to compare TCO")


# ================================
# Phase 7: Portfolio Builder
# ================================

@router.post("/portfolio/create")
async def create_portfolio(
    name: str = Query(..., description="Portfolio name (e.g., '3-Fund Portfolio')"),
    holdings: str = Query(..., description="Holdings in format: VTI:60,VXUS:30,BND:10"),
    description: Optional[str] = Query(None, description="Optional portfolio description")
):
    """
    Create a new ETF portfolio with allocation weights.
    
    **Holdings Format**: `ticker:weight,ticker:weight,...`
    - Example: `VTI:60,VXUS:30,BND:10` (weights must sum to 100%)
    
    **Use Case**: Build a multi-ETF portfolio for tracking or analysis.
    
    **Example**: `POST /etf/portfolio/create?name=3-Fund&holdings=VTI:60,VXUS:30,BND:10`
    
    **Response**:
    ```json
    {
        "portfolio_id": "portfolio_20251123_120000",
        "name": "3-Fund Portfolio",
        "holdings": [
            {"ticker": "VTI", "weight": 60.0, "name": "Vanguard Total Stock Market"},
            {"ticker": "VXUS", "weight": 30.0, "name": "Vanguard Total International"},
            {"ticker": "BND", "weight": 10.0, "name": "Vanguard Total Bond Market"}
        ],
        "total_weight": 100.0,
        "etf_count": 3
    }
    ```
    
    **Status Codes**:
    - 200: Portfolio created successfully
    - 400: Invalid holdings format or weights don't sum to 100%
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/portfolio/create",
            extra={"portfolio_name": name, "holdings_str": holdings}
        )
        
        # Parse holdings string
        holdings_list = []
        for holding_str in holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid holding format: {holding_str}. Use 'TICKER:WEIGHT'")
            
            ticker = parts[0].strip()
            weight = float(parts[1].strip())
            
            holdings_list.append({"ticker": ticker, "weight": weight})
        
        portfolio = await etf_portfolio_service.create_portfolio(
            name=name,
            holdings=holdings_list,
            description=description
        )
        
        logger.info(
            "Portfolio created",
            extra={
                "portfolio_id": portfolio['portfolio_id'],
                "etf_count": portfolio['etf_count']
            }
        )
        
        return portfolio
        
    except ValueError as e:
        logger.warning("Invalid portfolio creation request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Portfolio creation failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to create portfolio")


@router.post("/portfolio/analyze")
async def analyze_portfolio(
    holdings: str = Query(..., description="Holdings in format: VTI:60,VXUS:30,BND:10"),
    investment_amount: float = Query(10000.0, description="Portfolio value for cost calculations"),
    holding_period_years: int = Query(5, description="Time horizon for TCO calculation (1-50 years)")
):
    """
    Analyze portfolio characteristics and metrics.
    
    **Analyzes**:
    - Weighted expense ratio
    - Portfolio Total Cost of Ownership (TCO)
    - Sector allocation and diversification
    - Geographic exposure (US vs International)
    - Asset class breakdown (Equity, Fixed Income, etc.)
    - Quality/diversification score (0-100)
    - Personalized recommendations
    
    **Use Case**: "I have a 60/30/10 VTI/VXUS/BND portfolio. How is it?"
    
    **Example**: `POST /etf/portfolio/analyze?holdings=VTI:60,VXUS:30,BND:10&investment_amount=10000`
    
    **Response**:
    ```json
    {
        "aggregate_metrics": {
            "weighted_expense_ratio": 0.05,
            "portfolio_tco": 25.50,
            "portfolio_tco_pct": 0.26
        },
        "diversification": {
            "sector_allocation": {"Technology": 25.5, "Healthcare": 15.2},
            "geographic_exposure": {"US": 70.0, "International": 30.0},
            "asset_class": {"Equity": 90.0, "Fixed Income": 10.0}
        },
        "quality_score": 85,
        "recommendations": [
            "Portfolio is well-diversified",
            "Excellent low-cost portfolio (0.05%)"
        ]
    }
    ```
    
    **Status Codes**:
    - 200: Analysis complete
    - 400: Invalid holdings or parameters
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/portfolio/analyze",
            extra={
                "holdings_str": holdings,
                "investment": investment_amount,
                "period": holding_period_years
            }
        )
        
        # Parse holdings
        holdings_list = []
        for holding_str in holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid holding format: {holding_str}")
            
            ticker = parts[0].strip()
            weight = float(parts[1].strip())
            holdings_list.append({"ticker": ticker, "weight": weight})
        
        analysis = await etf_portfolio_service.analyze_portfolio(
            holdings=holdings_list,
            investment_amount=investment_amount,
            holding_period_years=holding_period_years
        )
        
        logger.info(
            "Portfolio analysis complete",
            extra={
                "quality_score": analysis['quality_score'],
                "weighted_er": analysis['aggregate_metrics']['weighted_expense_ratio']
            }
        )
        
        return analysis
        
    except ValueError as e:
        logger.warning("Invalid analysis request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Portfolio analysis failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to analyze portfolio")


@router.post("/portfolio/rebalance")
async def calculate_rebalancing(
    current_holdings: str = Query(..., description="Current holdings: VTI:65,VXUS:25,BND:10"),
    target_holdings: str = Query(..., description="Target holdings: VTI:60,VXUS:30,BND:10"),
    portfolio_value: float = Query(..., description="Current portfolio value"),
    threshold: float = Query(5.0, description="Minimum drift % to trigger rebalance (default 5%)")
):
    """
    Calculate rebalancing recommendations.
    
    Compares current vs target allocations and suggests trades to rebalance.
    
    **Use Case**: "My portfolio has drifted. Should I rebalance?"
    
    **Example**: 
    ```
    POST /etf/portfolio/rebalance?
        current_holdings=VTI:65,VXUS:25,BND:10&
        target_holdings=VTI:60,VXUS:30,BND:10&
        portfolio_value=10000&
        threshold=5
    ```
    
    **Response**:
    ```json
    {
        "needs_rebalancing": true,
        "drift_analysis": [
            {
                "ticker": "VTI",
                "current_weight": 65.0,
                "target_weight": 60.0,
                "drift": 5.0,
                "drift_pct": 8.3,
                "needs_action": true
            }
        ],
        "rebalancing_trades": [
            {"ticker": "VTI", "action": "SELL", "amount": 500.00},
            {"ticker": "VXUS", "action": "BUY", "amount": 500.00}
        ],
        "estimated_cost": {
            "spread_cost": 1.00,
            "total_cost": 1.00
        }
    }
    ```
    
    **Threshold Explanation**:
    - 5% (default): Rebalance when drift exceeds 5 percentage points
    - Example: Target 60% → Rebalance if current is <55% or >65%
    
    **Status Codes**:
    - 200: Rebalancing calculation complete
    - 400: Invalid parameters
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/portfolio/rebalance",
            extra={
                "portfolio_value": portfolio_value,
                "threshold": threshold
            }
        )
        
        # Parse holdings
        current_list = []
        for holding_str in current_holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid current holding format: {holding_str}")
            current_list.append({"ticker": parts[0].strip(), "weight": float(parts[1].strip())})
        
        target_list = []
        for holding_str in target_holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid target holding format: {holding_str}")
            target_list.append({"ticker": parts[0].strip(), "weight": float(parts[1].strip())})
        
        rebalancing = await etf_portfolio_service.calculate_rebalancing_needs(
            current_holdings=current_list,
            target_holdings=target_list,
            current_portfolio_value=portfolio_value,
            rebalancing_threshold=threshold
        )
        
        logger.info(
            "Rebalancing calculation complete",
            extra={
                "needs_rebalancing": rebalancing['needs_rebalancing'],
                "trades": len(rebalancing['rebalancing_trades'])
            }
        )
        
        return rebalancing
        
    except ValueError as e:
        logger.warning("Invalid rebalancing request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Rebalancing calculation failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to calculate rebalancing")


@router.post("/portfolio/compare")
async def compare_portfolios(
    portfolio1_holdings: str = Query(..., description="Portfolio 1: VTI:60,VXUS:30,BND:10"),
    portfolio2_holdings: str = Query(..., description="Portfolio 2: SPY:55,IXUS:35,AGG:10"),
    portfolio1_name: str = Query("Portfolio 1", description="Name for portfolio 1"),
    portfolio2_name: str = Query("Portfolio 2", description="Name for portfolio 2"),
    investment_amount: float = Query(10000.0, description="Investment amount"),
    holding_period_years: int = Query(5, description="Time horizon")
):
    """
    Compare two portfolios side-by-side.
    
    **Use Case**: "Should I use Vanguard or iShares ETFs for my portfolio?"
    
    **Example**:
    ```
    POST /etf/portfolio/compare?
        portfolio1_holdings=VTI:60,VXUS:30,BND:10&
        portfolio2_holdings=SPY:60,IXUS:30,AGG:10&
        portfolio1_name=Vanguard%203-Fund&
        portfolio2_name=iShares%203-Fund
    ```
    
    **Response**:
    ```json
    {
        "portfolio1": {
            "name": "Vanguard 3-Fund",
            "analysis": {...full analysis...}
        },
        "portfolio2": {
            "name": "iShares 3-Fund",
            "analysis": {...full analysis...}
        },
        "comparison": {
            "expense_ratio_difference": -0.02,
            "tco_difference": -15.00,
            "diversification_difference": 5,
            "winner": "Vanguard 3-Fund",
            "explanation": "Vanguard 3-Fund wins: $15 cheaper, more diversified"
        }
    }
    ```
    
    **Status Codes**:
    - 200: Comparison complete
    - 400: Invalid parameters
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/portfolio/compare",
            extra={
                "portfolio1_name": portfolio1_name,
                "portfolio2_name": portfolio2_name
            }
        )
        
        # Parse portfolio 1
        p1_list = []
        for holding_str in portfolio1_holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid portfolio 1 holding: {holding_str}")
            p1_list.append({"ticker": parts[0].strip(), "weight": float(parts[1].strip())})
        
        # Parse portfolio 2
        p2_list = []
        for holding_str in portfolio2_holdings.split(','):
            parts = holding_str.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid portfolio 2 holding: {holding_str}")
            p2_list.append({"ticker": parts[0].strip(), "weight": float(parts[1].strip())})
        
        
        comparison = await etf_portfolio_service.compare_portfolios(
            portfolio1_holdings=p1_list,
            portfolio2_holdings=p2_list,
            portfolio1_name=portfolio1_name,
            portfolio2_name=portfolio2_name,
            investment_amount=investment_amount,
            holding_period_years=holding_period_years
        )
        
        logger.info(
            "Portfolio comparison complete",
            extra={"winner": comparison['comparison']['winner']}
        )
        
        return comparison
        
    except ValueError as e:
        logger.warning("Invalid comparison request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Portfolio comparison failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to compare portfolios")


# ==================== DIVIDEND ANALYSIS (Phase 8) ====================

@router.get("/dividend-history/{ticker}")
async def get_dividend_history(
    ticker: str = Path(..., description="ETF ticker symbol"),
    years: int = Query(5, ge=1, le=20, description="Years of history to retrieve"),
    force_refresh: bool = Query(False, description="Force refresh from API")
):
    """
    Get dividend payment history for an ETF.
    
    Returns comprehensive dividend data including:
    - Payment history with dates and amounts
    - Current dividend yield
    - Payment frequency (monthly, quarterly, annual)
    - Dividend growth rates
    - Payout consistency score
    
    **Phase**: 8 of 15 - Dividend Analysis & Income Tracking
    
    **Example**: `GET /etf/dividend-history/SCHD?years=5`
    
    **Response**:
    ```json
    {
        "ticker": "SCHD",
        "current_yield": 0.0382,
        "current_price": 78.45,
        "dividend_count": 20,
        "dividends": [
            {"date": "2024-12-15", "amount": 0.7812, "type": "DIVIDEND"},
            {"date": "2024-09-15", "amount": 0.7654, "type": "DIVIDEND"}
        ],
        "analysis": {
            "payment_frequency": "Quarterly",
            "annual_dividend": 3.05,
            "dividend_growth_1y": 0.0687,
            "dividend_growth_3y": 0.0523,
            "payout_consistency": 95.2
        }
    }
    ```
    """
    try:
        logger.info("Fetching dividend history", extra={"ticker": ticker, "years": years})
        
        result = await etf_dividend_service.get_etf_dividend_history(
            ticker=ticker,
            years=years,
            force_refresh=force_refresh
        )
        
        logger.info(
            "Dividend history retrieved",
            extra={"ticker": ticker, "dividend_count": result['dividend_count']}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid dividend history request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to get dividend history",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to fetch dividend history")


@router.get("/dividend-growth/{ticker}")
async def analyze_dividend_growth(
    ticker: str = Path(..., description="ETF ticker symbol"),
    periods: Optional[str] = Query(None, description="Comma-separated years (e.g., '1,3,5,10')")
):
    """
    Analyze dividend growth over multiple time periods.
    
    Calculates compound annual growth rate (CAGR) for dividends.
    
    **Phase**: 8 of 15 - Dividend Analysis & Income Tracking
    
    **Example**: `GET /etf/dividend-growth/VYM?periods=1,3,5`
    
    **Response**:
    ```json
    {
        "ticker": "VYM",
        "growth_rates": {
            "1Y": 0.0687,
            "3Y": 0.0523,
            "5Y": 0.0418
        },
        "payment_history": {
            "total_payments": 60,
            "increases": 48,
            "decreases": 2,
            "unchanged": 10,
            "consistency_score": 80.0
        },
        "current_annual_dividend": 3.25,
        "interpretation": "Moderate dividend growth (5-10% CAGR)"
    }
    ```
    """
    try:
        # Parse periods
        parsed_periods = None
        if periods:
            try:
                parsed_periods = [int(p.strip()) for p in periods.split(',')]
            except ValueError:
                raise ValueError("Periods must be comma-separated integers (e.g., '1,3,5')")
        
        logger.info("Analyzing dividend growth", extra={"ticker": ticker})
        
        result = await etf_dividend_service.analyze_dividend_growth(
            ticker=ticker,
            periods=parsed_periods
        )
        
        logger.info(
            "Dividend growth analysis complete",
            extra={"ticker": ticker}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid dividend growth request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to analyze dividend growth",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to analyze dividend growth")


@router.get("/dividend/compare")
async def compare_dividend_yields(
    tickers: str = Query(..., description="Comma-separated ETF tickers (max 10)")
):
    """
    Compare dividend yields across multiple ETFs.
    
    Useful for building income-focused portfolios.
    
    **Phase**: 8 of 15 - Dividend Analysis & Income Tracking
    
    **Example**: `GET /etf/dividend/compare?tickers=VYM,SCHD,DGRO`
    
    **Response**:
    ```json
    {
        "tickers": ["VYM", "SCHD", "DGRO"],
        "etf_count": 3,
        "comparison": [
            {
                "ticker": "SCHD",
                "current_yield": 0.0382,
                "annual_dividend": 3.05,
                "payment_frequency": "Quarterly",
                "dividend_growth_1y": 0.0687,
                "payout_consistency": 95.2
            }
        ],
        "ranked_by_yield": [...],
        "highest_yield": {"ticker": "SCHD", "current_yield": 0.0382},
        "average_yield": 0.0341
    }
    ```
    """
    try:
        # Parse tickers
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
        
        if len(ticker_list) == 0:
            raise ValueError("Must provide at least one ticker")
        
        if len(ticker_list) > 10:
            raise ValueError("Maximum 10 tickers allowed")
        
        logger.info("Comparing dividend yields", extra={"ticker_count": len(ticker_list)})
        
        result = await etf_dividend_service.compare_dividend_yields(
            tickers=ticker_list
        )
        
        logger.info(
            "Dividend yield comparison complete",
            extra={"ticker_count": result['etf_count']}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid dividend comparison request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to compare dividend yields",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to compare dividend yields")


@router.post("/portfolio/income")
async def calculate_portfolio_income(
    holdings: str = Query(..., description="Comma-separated holdings (e.g., 'VYM:40,SCHD:30,DGRO:30')"),
    investment_amount: float = Query(100000.0, gt=0, description="Total portfolio value in USD")
):
    """
    Calculate projected income from a dividend portfolio.
    
    Provides annual, quarterly, and monthly income projections based on
    current dividend yields and payment schedules.
    
    **Phase**: 8 of 15 - Dividend Analysis & Income Tracking
    
    **Example**: `POST /etf/portfolio/income?holdings=VYM:50,SCHD:50&investment_amount=100000`
    
    **Request Body**: None (all parameters in query string)
    
    **Response**:
    ```json
    {
        "investment_amount": 100000.0,
        "portfolio_yield": 0.0356,
        "income_projections": {
            "annual": 3560.00,
            "quarterly": 890.00,
            "monthly": 296.67
        },
        "holdings": [
            {
                "ticker": "VYM",
                "weight": 50.0,
                "allocation": 50000.0,
                "current_yield": 0.0325,
                "annual_income": 1625.00,
                "payment_frequency": "Quarterly"
            }
        ],
        "income_growth_potential": "Moderate - Balanced income and growth"
    }
    ```
    """
    try:
        logger.info(
            "Calculating portfolio income",
            extra={"investment_amount": investment_amount}
        )
        
        result = await etf_dividend_service.calculate_portfolio_income(
            holdings=holdings,
            investment_amount=investment_amount
        )
        
        logger.info(
            "Portfolio income calculated",
            extra={"annual_income": result['income_projections']['annual']}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid portfolio income request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to calculate portfolio income",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to calculate portfolio income")


# ==================== Phase 9: Tax Optimization ====================

@router.get("/tax-loss-harvest")
async def find_tax_loss_harvest_opportunities(
    holdings: str = Query(
        ...,
        description="Holdings with cost basis: TICKER:SHARES:COST_BASIS[:PURCHASE_DATE]",
        example="VOO:100:42000:2020-01-15,VTI:50:12000:2023-06-01"
    ),
    loss_threshold: float = Query(
        500.0,
        description="Minimum loss to consider harvesting (default: $500)",
        ge=0
    ),
    correlation_min: float = Query(
        0.90,
        description="Minimum correlation for replacement ETFs (default: 0.90)",
        ge=0,
        le=1
    )
):
    """
    Find tax-loss harvesting opportunities in your portfolio.
    
    Tax-loss harvesting: Sell positions with losses to offset capital gains
    and reduce tax liability, then buy similar (but not identical) ETFs.
    
    **IRS Wash Sale Rule**: Cannot buy substantially identical security
    30 days before or after sale.
    
    **Holdings Format**:
    - `TICKER:SHARES:COST_BASIS` - Required
    - `TICKER:SHARES:COST_BASIS:PURCHASE_DATE` - With date (YYYY-MM-DD)
    
    **Example**: `GET /etf/tax-loss-harvest?holdings=VOO:100:42000:2020-01-15`
    
    **Response**:
    ```json
    {
        "opportunities": [
            {
                "current_etf": "VOO",
                "shares": 100,
                "cost_basis": 42000,
                "current_value": 40000,
                "unrealized_loss": -2000,
                "estimated_tax_savings": 740,
                "replacements": [
                    {
                        "ticker": "IVV",
                        "name": "iShares Core S&P 500",
                        "correlation": 0.995,
                        "expense_ratio": 0.0003,
                        "reason": "Tracks same index with different structure"
                    }
                ]
            }
        ],
        "summary": {
            "total_opportunities": 1,
            "total_harvestable_loss": 2000,
            "estimated_total_tax_savings": 740
        }
    }
    ```
    
    **Parameters**:
    - `holdings`: Portfolio positions with cost basis
    - `loss_threshold`: Minimum loss amount to consider (default: $500)
    - `correlation_min`: Minimum correlation for replacements (default: 0.90)
    
    **Tags**: Phase 9, Tax Optimization
    """
    try:
        logger.info(
            "Finding tax-loss harvest opportunities",
            extra={"loss_threshold": loss_threshold}
        )
        
        result = await etf_tax_service.find_tax_loss_harvest_pairs(
            holdings=holdings,
            loss_threshold=loss_threshold,
            correlation_min=correlation_min
        )
        
        logger.info(
            "Tax-loss harvest opportunities found",
            extra={"opportunity_count": result['summary']['total_opportunities']}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid tax-loss harvest request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to find tax-loss harvest opportunities",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to find tax-loss harvest opportunities")


@router.post("/capital-gains/estimate")
async def estimate_capital_gains(
    holdings: str = Query(
        ...,
        description="Holdings with cost basis: TICKER:SHARES:COST_BASIS:PURCHASE_DATE",
        example="VOO:100:40000:2020-01-15,VTI:50:12000:2023-06-01"
    ),
    sell_percentage: float = Query(
        100.0,
        description="Percentage of position to sell (default: 100%)",
        gt=0,
        le=100
    )
):
    """
    Estimate capital gains/losses if positions were sold today.
    
    Calculates short-term vs long-term gains and estimated tax liability
    to help plan optimal selling strategy.
    
    **Tax Rates** (2025 Federal):
    - Short-term (<1 year): Taxed as ordinary income (up to 37%)
    - Long-term (>1 year): Preferential rates (0%, 15%, or 20%)
    
    **Holdings Format**:
    - `TICKER:SHARES:COST_BASIS:PURCHASE_DATE` (YYYY-MM-DD)
    
    **Example**: `POST /etf/capital-gains/estimate?holdings=VOO:100:40000:2020-01-15`
    
    **Response**:
    ```json
    {
        "holdings": [
            {
                "ticker": "VOO",
                "shares": 100,
                "cost_basis": 40000,
                "current_value": 45000,
                "capital_gain": 5000,
                "holding_period": "Long-term (>1 year)",
                "applicable_tax_rate": 0.20,
                "estimated_tax": 1000
            }
        ],
        "summary": {
            "total_cost_basis": 40000,
            "total_proceeds": 45000,
            "total_capital_gain": 5000,
            "short_term_gains": 0,
            "long_term_gains": 5000,
            "estimated_total_tax": 1000,
            "net_after_tax": 44000
        },
        "tax_optimization_tips": [
            "All gains are long-term (taxed at 20%). Well done!"
        ]
    }
    ```
    
    **Parameters**:
    - `holdings`: Portfolio positions with purchase dates
    - `sell_percentage`: Percentage to sell (useful for partial exits)
    
    **Tags**: Phase 9, Tax Optimization
    """
    try:
        logger.info(
            "Estimating capital gains",
            extra={"sell_percentage": sell_percentage}
        )
        
        result = await etf_tax_service.estimate_capital_gains(
            holdings=holdings,
            sell_percentage=sell_percentage
        )
        
        logger.info(
            "Capital gains estimated",
            extra={"total_tax_liability": result['summary']['estimated_total_tax']}
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid capital gains request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to estimate capital gains",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to estimate capital gains")


@router.get("/tax-efficient-alternatives/{ticker}")
async def get_tax_efficient_alternatives(
    ticker: str = Path(..., description="Current ETF ticker"),
    target_expense_ratio: Optional[float] = Query(
        None,
        description="Maximum acceptable expense ratio (optional)",
        ge=0,
        le=0.1
    )
):
    """
    Find more tax-efficient alternatives to a given ETF.
    
    Tax efficiency factors:
    - **Lower turnover**: Fewer taxable events
    - **Lower expense ratio**: Less drag on after-tax returns
    - **Qualified dividends**: Preferential tax treatment
    - **Index tracking**: Typically more tax-efficient than active
    
    **Example**: `GET /etf/tax-efficient-alternatives/ARKK`
    
    **Response**:
    ```json
    {
        "ticker": "ARKK",
        "current_expense_ratio": 0.0075,
        "alternatives": [
            {
                "ticker": "VTI",
                "name": "Vanguard Total Stock Market",
                "expense_ratio": 0.0003,
                "tax_efficiency_score": 95,
                "annual_savings_per_10k": 72,
                "estimated_turnover": "Low (5-15%)",
                "reason": "Lower turnover and expense ratio"
            }
        ],
        "tax_efficiency_factors": {
            "expense_ratio": "Lower fees = less drag on after-tax returns",
            "turnover": "Lower turnover = fewer taxable events",
            "fund_size": "Larger funds = better economies of scale"
        },
        "recommendation": "Strong recommendation: Switch to VTI for $72 annual savings per $10,000 invested"
    }
    ```
    
    **Parameters**:
    - `ticker`: Current ETF to analyze
    - `target_expense_ratio`: Filter alternatives by max expense ratio
    
    **Tax Efficiency Score** (0-100):
    - 90-100: Extremely tax-efficient (index funds, low turnover)
    - 75-89: Very tax-efficient
    - 50-74: Moderately tax-efficient
    - <50: Less tax-efficient (active management, high turnover)
    
    **Tags**: Phase 9, Tax Optimization
    """
    try:
        logger.info(
            "Finding tax-efficient alternatives",
            extra={"ticker": ticker}
        )
        
        result = await etf_tax_service.get_tax_efficient_alternatives(
            ticker=ticker,
            target_expense_ratio=target_expense_ratio
        )
        
        logger.info(
            "Tax-efficient alternatives found",
            extra={
                "ticker": ticker,
                "alternative_count": len(result.get('alternatives', []))
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid tax-efficient alternatives request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to find tax-efficient alternatives",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to find tax-efficient alternatives")


# =============================================================================
# Phase 10: Risk Analysis & Correlation
# =============================================================================

@router.get("/risk/{ticker}")
async def get_risk_metrics(
    ticker: str = Path(..., description="ETF ticker symbol"),
    period_days: int = Query(252, ge=30, le=1260, description="Analysis period in trading days (30-1260)"),
    benchmark: Optional[str] = Query(None, description="Benchmark ticker for beta calculation (default: SPY)")
):
    """
    Get comprehensive risk metrics for an ETF.
    
    **Risk Metrics Included**:
    - Volatility (daily and annual)
    - Sharpe ratio (risk-adjusted returns)
    - Beta (market sensitivity vs benchmark)
    - Value at Risk (VaR) at 95% confidence
    - Conditional VaR (Expected Shortfall)
    - Maximum Drawdown
    - Risk classification (Very Low to Very High)
    
    **Example**: `GET /etf/risk/VOO?period_days=252&benchmark=SPY`
    
    **Response**:
    ```json
    {
        "ticker": "VOO",
        "etf_name": "Vanguard S&P 500 ETF",
        "analysis_period_days": 252,
        "volatility": {
            "annual_pct": 18.5,
            "daily_pct": 1.17
        },
        "risk_adjusted": {
            "sharpe_ratio": 1.25,
            "sharpe_interpretation": "Good - Adequate risk-adjusted returns"
        },
        "market_risk": {
            "beta": 1.0,
            "beta_vs": "SPY",
            "beta_interpretation": "Market-like volatility (neutral)"
        },
        "downside_risk": {
            "var_95_annual_pct": -25.3,
            "cvar_95_annual_pct": -31.2,
            "max_drawdown_pct": -33.9
        },
        "risk_classification": {
            "level": "Moderate",
            "description": "Balanced risk suitable for most long-term investors"
        }
    }
    ```
    
    **Parameters**:
    - `ticker`: ETF ticker symbol (case-insensitive)
    - `period_days`: Analysis period (default 252 = 1 year, max 1260 = 5 years)
    - `benchmark`: Benchmark for beta calculation (default SPY)
    
    **Returns**: Comprehensive risk analysis including volatility, Sharpe, beta, VaR
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid parameters
    - 404: ETF not found
    - 500: Server error
    """
    try:
        logger.info(
            "GET /etf/risk/{ticker}",
            extra={"ticker": ticker, "period_days": period_days}
        )
        
        result = await etf_risk_service.get_risk_metrics(
            ticker=ticker,
            period_days=period_days,
            benchmark=benchmark
        )
        
        logger.info(
            "Risk metrics request successful",
            extra={
                "ticker": ticker,
                "volatility": result.get('volatility', {}).get('annual_pct'),
                "sharpe": result.get('risk_adjusted', {}).get('sharpe_ratio')
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid risk metrics request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to calculate risk metrics",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to calculate risk metrics")


@router.get("/correlation/matrix")
async def get_correlation_matrix(
    tickers: str = Query(..., description="Comma-separated list of ETF tickers (2-20)"),
    period_days: int = Query(252, ge=30, le=1260, description="Analysis period in trading days (30-1260)")
):
    """
    Calculate correlation matrix for multiple ETFs.
    
    **Use Cases**:
    - Assess diversification between ETFs
    - Identify redundant holdings
    - Find complementary ETFs for portfolio
    - Understand co-movement during market events
    
    **Example**: `GET /etf/correlation/matrix?tickers=VOO,VTI,VXUS,AGG&period_days=252`
    
    **Response**:
    ```json
    {
        "tickers": ["VOO", "VTI", "VXUS", "AGG"],
        "analysis_period_days": 252,
        "correlations": {
            "VOO": {"VOO": 1.0, "VTI": 0.98, "VXUS": 0.65, "AGG": 0.15},
            "VTI": {"VOO": 0.98, "VTI": 1.0, "VXUS": 0.67, "AGG": 0.12},
            "VXUS": {"VOO": 0.65, "VTI": 0.67, "VXUS": 1.0, "AGG": 0.08},
            "AGG": {"VOO": 0.15, "VTI": 0.12, "VXUS": 0.08, "AGG": 1.0}
        },
        "summary": {
            "average_correlation": 0.42,
            "highest_correlation": {
                "etf1": "VOO",
                "etf2": "VTI",
                "correlation": 0.98,
                "interpretation": "Very strong correlation - minimal diversification"
            },
            "lowest_correlation": {
                "etf1": "VXUS",
                "etf2": "AGG",
                "correlation": 0.08,
                "interpretation": "Weak correlation - good diversification"
            }
        },
        "diversification_score": {
            "score": 58.0,
            "interpretation": "Good diversification"
        }
    }
    ```
    
    **Correlation Interpretation**:
    - 1.0: Perfect positive correlation (move together)
    - 0.0: No correlation (independent)
    - -1.0: Perfect negative correlation (move opposite)
    - |r| < 0.3: Weak correlation (good diversification)
    - |r| > 0.9: Very strong correlation (minimal diversification)
    
    **Parameters**:
    - `tickers`: Comma-separated ETF tickers (2-20 required)
    - `period_days`: Analysis period (default 252 = 1 year)
    
    **Returns**: Correlation matrix with diversification analysis
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid parameters (< 2 or > 20 tickers)
    - 500: Server error
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
        
        logger.info(
            "GET /etf/correlation/matrix",
            extra={"tickers": ticker_list, "count": len(ticker_list)}
        )
        
        result = await etf_risk_service.calculate_correlation_matrix(
            tickers=ticker_list,
            period_days=period_days
        )
        
        logger.info(
            "Correlation matrix request successful",
            extra={
                "tickers": len(ticker_list),
                "avg_correlation": result.get('summary', {}).get('average_correlation')
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid correlation matrix request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to calculate correlation matrix",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to calculate correlation matrix")


@router.post("/portfolio/risk")
async def analyze_portfolio_risk(
    holdings: str = Query(..., description="Holdings as TICKER:WEIGHT pairs (e.g., VOO:0.6,VTI:0.3,VXUS:0.1)"),
    period_days: int = Query(252, ge=30, le=1260, description="Analysis period in trading days (30-1260)"),
    benchmark: Optional[str] = Query(None, description="Benchmark ticker for beta (default: SPY)")
):
    """
    Calculate portfolio-level risk metrics.
    
    **Portfolio Risk Analysis**:
    - Portfolio volatility (weighted)
    - Portfolio Sharpe ratio
    - Portfolio beta
    - Individual ETF contributions
    - Diversification benefit
    - Correlation effects
    
    **Example**: `POST /etf/portfolio/risk?holdings=VOO:0.6,VTI:0.3,VXUS:0.1&period_days=252`
    
    **Response**:
    ```json
    {
        "holdings": {"VOO": 0.6, "VTI": 0.3, "VXUS": 0.1},
        "holdings_count": 3,
        "portfolio_metrics": {
            "volatility_annual_pct": 15.2,
            "mean_return_annual_pct": 10.5,
            "sharpe_ratio": 1.32,
            "beta": 0.95
        },
        "individual_etfs": [
            {
                "ticker": "VOO",
                "weight_pct": 60.0,
                "volatility_annual_pct": 18.5,
                "sharpe_ratio": 1.25,
                "beta": 1.0
            },
            ...
        ],
        "diversification": {
            "weighted_avg_volatility_pct": 17.8,
            "portfolio_volatility_pct": 15.2,
            "diversification_benefit_pct": 2.6,
            "benefit_interpretation": "Portfolio is 2.6% less volatile than weighted average",
            "diversification_score": {
                "score": 65.0,
                "interpretation": "Good diversification"
            }
        },
        "risk_classification": {
            "level": "Moderate",
            "description": "Balanced risk suitable for most long-term investors"
        }
    }
    ```
    
    **Holdings Format**:
    - Format: `TICKER:WEIGHT` pairs separated by commas
    - Weights should sum to 1.0 (auto-normalized if not)
    - Example: `VOO:0.6,VTI:0.3,VXUS:0.1`
    
    **Diversification Benefit**:
    - Positive benefit: Portfolio less volatile than weighted average (good!)
    - Negative benefit: Portfolio more volatile (poor diversification)
    - Driven by correlation between holdings
    
    **Parameters**:
    - `holdings`: Holdings as TICKER:WEIGHT pairs (required)
    - `period_days`: Analysis period (default 252 = 1 year)
    - `benchmark`: Benchmark for beta (default SPY)
    
    **Returns**: Portfolio risk analysis with diversification metrics
    
    **Status Codes**:
    - 200: Success
    - 400: Invalid holdings format or weights
    - 500: Server error
    """
    try:
        logger.info(
            "POST /etf/portfolio/risk",
            extra={"holdings": holdings}
        )
        
        # Parse holdings
        holdings_dict = {}
        for pair in holdings.split(','):
            parts = pair.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid holdings format: {pair}")
            ticker = parts[0].strip().upper()
            try:
                weight = float(parts[1])
            except ValueError:
                raise ValueError(f"Invalid weight for {ticker}: {parts[1]}")
            holdings_dict[ticker] = weight
        
        result = await etf_risk_service.analyze_portfolio_risk(
            holdings=holdings_dict,
            period_days=period_days,
            benchmark=benchmark
        )
        
        logger.info(
            "Portfolio risk analysis successful",
            extra={
                "holdings": len(holdings_dict),
                "portfolio_vol": result.get('portfolio_metrics', {}).get('volatility_annual_pct')
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning("Invalid portfolio risk request", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to analyze portfolio risk",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to analyze portfolio risk")


# ==================== Phase 11: Sector & Theme Analysis ====================

@router.get(
    "/sector-exposure/{sector}",
    summary="Get ETFs by Sector Exposure",
    description="""
    Find all ETFs with significant exposure to a specific sector.
    
    Searches across ETF holdings to identify funds with meaningful sector allocation.
    Useful for sector rotation strategies and targeted exposure.
    
    **Parameters:**
    - `sector`: GICS Level 1 sector (Technology, Healthcare, Financials, etc.)
    - `min_exposure`: Minimum sector exposure threshold (default 5%)
    - `sort_by`: Sort order - "exposure" (default) or "assets"
    
    **Returns:**
    - List of ETFs with sector exposure percentages
    - Average exposure across matching ETFs
    - Highest exposure ETF
    - Total assets under management
    
    **Example:**
    ```
    GET /etf/sector-exposure/Technology?min_exposure=0.30
    ```
    Returns all ETFs with 30%+ Technology sector exposure.
    """
)
async def get_sector_exposure(
    sector: str = Path(..., description="Sector name (e.g., Technology, Healthcare)"),
    min_exposure: float = Query(
        0.05,
        ge=0.0,
        le=1.0,
        description="Minimum sector exposure (0.0-1.0, default 0.05 = 5%)"
    ),
    sort_by: str = Query(
        "exposure",
        description="Sort order: 'exposure' or 'assets'"
    )
):
    """
    Find ETFs with significant sector exposure.
    
    Args:
        sector: Sector name (Technology, Healthcare, Financials, etc.)
        min_exposure: Minimum exposure threshold (0.0-1.0)
        sort_by: Sort by 'exposure' or 'assets'
        
    Returns:
        ETFs with sector exposure details
    """
    logger.info(
        "GET /etf/sector-exposure/{sector}",
        extra={
            "sector": sector,
            "min_exposure": min_exposure,
            "sort_by": sort_by
        }
    )
    
    try:
        result = await etf_theme_service.get_sector_exposure(
            sector=sector,
            min_exposure=min_exposure,
            sort_by=sort_by
        )
        
        logger.info(
            "Sector exposure query successful",
            extra={
                "sector": sector,
                "etfs_found": result["etfs_found"]
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning(
            "Invalid sector exposure query",
            extra={"sector": sector, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Sector exposure query failed",
            extra={"sector": sector, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Sector exposure query failed: {str(e)}"
        )


@router.get(
    "/theme/{theme}",
    summary="Find ETFs by Investment Theme",
    description="""
    Discover ETFs by investment theme or strategy.
    
    Searches across ETF universe to find funds matching specific investment themes.
    Supports filtering by minimum assets and maximum expense ratio.
    
    **Available Themes:**
    - `esg`: Environmental, Social, Governance focused
    - `technology`: Technology sector and innovation
    - `growth`: Growth stocks and high potential
    - `value`: Value investing and dividends
    - `defensive`: Low volatility and defensive strategies
    - `international`: Global and non-US exposure
    - `fixed_income`: Bonds and fixed income
    - `real_estate`: REITs and property
    - `commodities`: Gold, energy, materials
    - `smart_beta`: Factor-based strategies
    
    **Parameters:**
    - `theme`: Investment theme (required)
    - `min_assets`: Minimum net assets in USD (optional)
    - `max_expense_ratio`: Maximum expense ratio as decimal (optional)
    
    **Returns:**
    - ETFs matching the theme
    - Theme description and keywords
    - Summary statistics (total assets, average expense ratio)
    - Largest ETF in the theme
    
    **Example:**
    ```
    GET /etf/theme/esg?min_assets=1000000000&max_expense_ratio=0.0050
    ```
    Returns ESG ETFs with >$1B assets and <0.50% expense ratio.
    """
)
async def find_thematic_etfs(
    theme: str = Path(..., description="Investment theme (esg, technology, growth, etc.)"),
    min_assets: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum net assets in USD"
    ),
    max_expense_ratio: Optional[float] = Query(
        None,
        ge=0.0,
        le=0.10,
        description="Maximum expense ratio (0.0-0.10)"
    )
):
    """
    Find ETFs by investment theme.
    
    Args:
        theme: Investment theme (esg, technology, growth, etc.)
        min_assets: Minimum net assets filter
        max_expense_ratio: Maximum expense ratio filter
        
    Returns:
        ETFs matching the theme with details
    """
    logger.info(
        "GET /etf/theme/{theme}",
        extra={
            "theme": theme,
            "min_assets": min_assets,
            "max_expense_ratio": max_expense_ratio
        }
    )
    
    try:
        result = await etf_theme_service.find_thematic_etfs(
            theme=theme,
            min_assets=min_assets,
            max_expense_ratio=max_expense_ratio
        )
        
        logger.info(
            "Thematic ETF search successful",
            extra={
                "theme": theme,
                "etfs_found": result["etfs_found"]
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning(
            "Invalid thematic ETF query",
            extra={"theme": theme, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Thematic ETF search failed",
            extra={"theme": theme, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Thematic ETF search failed: {str(e)}"
        )


@router.post(
    "/geographic-allocation",
    summary="Analyze Geographic Allocation",
    description="""
    Analyze geographic exposure across multiple ETFs.
    
    Aggregates geographic allocations to understand regional exposure in a portfolio.
    Useful for managing home country bias and international diversification.
    
    **Geographic Regions:**
    - North America (US, Canada)
    - Europe (EU, UK)
    - Asia Pacific (Japan, China, India, Australia)
    - Emerging Markets
    - Latin America
    - Middle East & Africa
    
    **Parameters:**
    - `tickers`: Comma-separated list of ETF symbols (max 20)
    - `aggregation`: "weighted" or "equal" (default "weighted")
    
    **Aggregation Methods:**
    - `weighted`: Weight by portfolio allocation (equal if not specified)
    - `equal`: Equal weight across all ETFs
    
    **Returns:**
    - Geographic breakdown by region (percentages)
    - Absolute allocations
    - Dominant region
    - Geographic diversification score
    - Individual ETF allocations
    
    **Example:**
    ```
    POST /etf/geographic-allocation?tickers=VOO,VXUS,VWO&aggregation=equal
    ```
    Returns geographic breakdown of 3-ETF portfolio with equal weights.
    """
)
async def analyze_geographic_allocation(
    tickers: str = Query(
        ...,
        description="Comma-separated list of ETF tickers (e.g., VOO,VXUS,VWO)",
        min_length=1
    ),
    aggregation: str = Query(
        "weighted",
        description="Aggregation method: 'weighted' or 'equal'"
    )
):
    """
    Analyze geographic allocation across multiple ETFs.
    
    Args:
        tickers: Comma-separated ETF ticker list
        aggregation: 'weighted' or 'equal' weight
        
    Returns:
        Geographic allocation breakdown
    """
    logger.info(
        "POST /etf/geographic-allocation",
        extra={
            "tickers": tickers,
            "aggregation": aggregation
        }
    )
    
    # Parse tickers
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    
    if not ticker_list:
        raise HTTPException(
            status_code=400,
            detail="At least one ticker is required"
        )
    
    if len(ticker_list) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 tickers allowed"
        )
    
    try:
        result = await etf_theme_service.analyze_geographic_allocation(
            tickers=ticker_list,
            aggregation=aggregation
        )
        
        logger.info(
            "Geographic allocation analysis successful",
            extra={
                "tickers": len(ticker_list),
                "dominant_region": result.get("dominant_region", {}).get("region")
            }
        )
        
        return result
        
    except ValueError as e:
        logger.warning(
            "Invalid geographic allocation query",
            extra={"tickers": tickers, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Geographic allocation analysis failed",
            extra={"tickers": tickers, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Geographic allocation analysis failed: {str(e)}"
        )


# ============================================================================
# PHASE 12: Famous Investor Portfolios (3 endpoints)
# ============================================================================


@router.get("/investors")
async def list_famous_investors():
    """
    List all famous investors available in the database.
    
    Returns metadata for all investors whose portfolios have been loaded
    into the system, including their investment style and latest portfolio data.
    
    **Features**:
    - List of all available investors
    - Investment style classification
    - Latest filing information
    - Portfolio size and update time
    
    **Response**:
    ```json
    {
      "investors_count": 10,
      "investors": [
        {
          "investor_id": "warren_buffett",
          "investor_name": "Warren Buffett",
          "entity_name": "Berkshire Hathaway Inc.",
          "investment_style": "Value Investing",
          "filing_date": "2025-09-30",
          "total_portfolio_value": 558000000000,
          "last_updated": "2025-11-16T10:30:00Z"
        },
        ...
      ],
      "timestamp": "2025-11-16T10:30:00Z"
    }
    ```
    
    **Use Cases**:
    - Browse available investors
    - Check last update times
    - Discover investment styles
    - Plan portfolio mirroring
    """
    try:
        logger.info("Listing available famous investors")
        
        result = await etf_investor_service.get_available_investors()
        
        logger.info(
            "Famous investors listed successfully",
            extra={"count": result.get("investors_count", 0)}
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid request for investor list",
            extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Failed to list famous investors",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list famous investors: {str(e)}"
        )


@router.get("/investors/search")
async def search_investor(
    q: str = Query(
        ...,
        description="Investor name to search (e.g., 'Warren Buffett', 'Ray Dalio', 'Cathie Wood')",
        example="Warren Buffett"
    )
):
    """
    Search for a famous investor's portfolio with on-demand loading.
    
    If the investor is not yet in the database, the system will attempt to
    fetch their portfolio from available sources and store it for future queries.
    
    **On-Demand Loading**:
    - First search: Fetches from source → Stores in DB → Returns portfolio
    - Subsequent searches: Returns cached data from MongoDB (fast)
    
    **Query Examples**:
    - `?q=Warren Buffett` - Get Berkshire Hathaway portfolio
    - `?q=Ray Dalio` - Get Bridgewater Associates holdings
    - `?q=Cathie Wood` - Get ARK Invest portfolio
    - `?q=carl icahn` - Case-insensitive search
    
    **Response**:
    ```json
    {
      "investor_id": "warren_buffett",
      "investor_name": "Warren Buffett",
      "entity_name": "Berkshire Hathaway Inc.",
      "investment_style": "Value Investing",
      "filing_date": "2025-09-30",
      "total_portfolio_value": 558000000000,
      "holdings": [
        {
          "ticker": "AAPL",
          "company": "Apple Inc.",
          "shares": 915560382,
          "value_usd": 174000000000,
          "weight_pct": 31.2,
          "sector": "Technology",
          "industry": "Consumer Electronics"
        },
        ...
      ],
      "sector_allocation": {
        "Technology": 31.2,
        "Financials": 28.5,
        "Consumer Staples": 15.3,
        "Energy": 12.1,
        "Consumer Discretionary": 8.2,
        "Other": 4.7
      },
      "top_10_holdings": ["AAPL", "BAC", "AXP", "KO", "CVX", ...],
      "cached": false,
      "timestamp": "2025-11-16T10:30:00Z"
    }
    ```
    
    **Available Investors** (10 total):
    1. Warren Buffett - Berkshire Hathaway (value investing)
    2. Ray Dalio - Bridgewater Associates (all-weather portfolio)
    3. Cathie Wood - ARK Invest (disruptive innovation)
    4. Carl Icahn - Icahn Enterprises (activist investing)
    5. Bill Ackman - Pershing Square (concentrated value)
    6. Seth Klarman - Baupost Group (value + distressed)
    7. David Tepper - Appaloosa Management (opportunistic)
    8. Stanley Druckenmiller - Duquesne Family Office (macro)
    9. David Einhorn - Greenlight Capital (value + shorts)
    10. Charlie Munger - Daily Journal Corp (value investing)
    
    **Use Cases**:
    - Analyze legendary investor strategies
    - Study successful portfolio allocations
    - Identify sector preferences
    - Learn from top holdings
    - Prepare for ETF mirroring
    """
    try:
        logger.info(
            "Searching for famous investor",
            extra={"query": q}
        )
        
        result = await etf_investor_service.search_investor(q)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Investor '{q}' not found. Try: Warren Buffett, Ray Dalio, Cathie Wood, etc."
            )
        
        logger.info(
            "Famous investor found",
            extra={
                "investor": result.get("investor_name"),
                "holdings_count": len(result.get("holdings", [])),
                "cached": result.get("cached", False)
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            "Invalid investor search query",
            extra={"query": q, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Investor search failed",
            extra={"query": q, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Investor search failed: {str(e)}"
        )


@router.post("/investors/mirror")
async def mirror_investor_portfolio(
    investor: str = Query(
        ...,
        description="Investor ID (e.g., 'warren_buffett', 'ray_dalio', 'cathie_wood')",
        example="warren_buffett"
    ),
    portfolio_value: float = Query(
        100000,
        description="Target portfolio value in USD",
        ge=1000,
        le=10000000,
        example=100000
    )
):
    """
    Convert a famous investor's stock portfolio to an equivalent ETF allocation.
    
    Maps individual stock positions to sector-based ETFs, preserving the
    investor's sector allocation while using liquid, diversified ETF vehicles.
    
    **Mapping Strategy**:
    - Technology stocks (AAPL, MSFT, etc.) → XLK (Technology ETF)
    - Financial stocks (BAC, JPM, etc.) → XLF (Financials ETF)
    - Healthcare stocks (UNH, JNJ, etc.) → XLV (Healthcare ETF)
    - And so on for all 11 GICS sectors
    
    **Query Parameters**:
    - `investor`: Investor ID (from search results)
    - `portfolio_value`: Target portfolio size (default $100,000)
    
    **Query Examples**:
    - `?investor=warren_buffett&portfolio_value=100000`
    - `?investor=ray_dalio&portfolio_value=50000`
    - `?investor=cathie_wood&portfolio_value=250000`
    
    **Response**:
    ```json
    {
      "investor_id": "warren_buffett",
      "investor_name": "Warren Buffett",
      "original_portfolio_value": 558000000000,
      "target_portfolio_value": 100000,
      "etf_allocation": [
        {
          "ticker": "XLK",
          "name": "Technology Select Sector SPDR",
          "sector": "Technology",
          "weight_pct": 31.2,
          "value_usd": 31200,
          "original_stocks": ["AAPL"],
          "expense_ratio": 0.10
        },
        {
          "ticker": "XLF",
          "name": "Financial Select Sector SPDR",
          "sector": "Financials",
          "weight_pct": 28.5,
          "value_usd": 28500,
          "original_stocks": ["BAC", "AXP", "MCO", "CB", "V"],
          "expense_ratio": 0.10
        },
        ...
      ],
      "sector_allocation": {
        "Technology": 31.2,
        "Financials": 28.5,
        "Consumer Staples": 15.3,
        "Energy": 12.1,
        "Consumer Discretionary": 8.2,
        "Other": 4.7
      },
      "diversification_score": 68.5,
      "estimated_annual_expense": 120.50,
      "total_etfs": 6,
      "timestamp": "2025-11-16T10:30:00Z"
    }
    ```
    
    **Benefits**:
    - **Liquidity**: Trade ETFs instead of individual stocks
    - **Simplicity**: 6-8 ETFs vs 15+ stocks
    - **Diversification**: Sector exposure without single-stock risk
    - **Cost-effective**: Low expense ratios (0.10-0.20%)
    - **Accessibility**: Smaller portfolios can replicate strategies
    
    **Use Cases**:
    - Replicate Buffett's sector allocation with $10k
    - Mirror Dalio's all-weather portfolio using ETFs
    - Copy Cathie Wood's innovation focus with sector ETFs
    - Build a "legends portfolio" with fractional allocations
    
    **Constraints**:
    - Minimum portfolio value: $1,000
    - Maximum portfolio value: $10,000,000
    - ETF allocation matches investor's sector weights
    - Excludes cash positions and alternative assets
    """
    try:
        logger.info(
            "Mirroring investor portfolio with ETFs",
            extra={"investor": investor, "portfolio_value": portfolio_value}
        )
        
        result = await etf_investor_service.mirror_with_etfs(
            investor_id=investor,
            portfolio_value=portfolio_value
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Investor '{investor}' not found. Search first to load portfolio."
            )
        
        logger.info(
            "ETF mirroring successful",
            extra={
                "investor": investor,
                "etf_count": result.get("total_etfs", 0),
                "diversification_score": result.get("diversification_score", 0)
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            "Invalid ETF mirroring request",
            extra={"investor": investor, "portfolio_value": portfolio_value, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "ETF mirroring failed",
            extra={"investor": investor, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"ETF mirroring failed: {str(e)}"
        )


# =============================================================================
# PHASE 13: ADVANCED ANALYTICS
# =============================================================================


@router.get(
    "/analytics/momentum/{ticker}",
    summary="Get Momentum Indicators",
    description="""
    Calculate momentum indicators for ETF trend analysis.
    
    **Indicators Included**:
    - **RSI (Relative Strength Index)**: 14-period RSI with overbought/oversold signals
    - **MACD (Moving Average Convergence Divergence)**: EMA-12/26 with signal line
    - **Moving Averages**: SMA-20, SMA-50, SMA-200, EMA-12, EMA-26
    - **Golden/Death Cross**: Long-term trend signals (50 vs 200 SMA)
    - **Trend Analysis**: Short/medium/long-term trend classification
    - **Momentum Score**: Composite 0-100 score with rating
    - **Trading Signals**: Actionable recommendations
    
    **Parameters**:
    - **ticker**: ETF symbol (e.g., VOO, SPY, QQQ)
    - **period**: Analysis timeframe (1m, 3m, 6m, 1y, 2y) - default 6m
    
    **Example Usage**:
    ```
    GET /etf/analytics/momentum/VOO?period=6m
    ```
    
    **Response**:
    ```json
    {
      "ticker": "VOO",
      "period": "6m",
      "price_data": {
        "current_price": 158.5,
        "period_high": 162.3,
        "period_low": 148.2,
        "price_change_pct": 5.67,
        "data_points": 180
      },
      "rsi": {
        "value": 65.3,
        "signal": "neutral",
        "interpretation": "RSI between 30-70 indicates balanced momentum"
      },
      "macd": {
        "macd_line": 2.45,
        "signal_line": 2.10,
        "histogram": 0.35,
        "signal": "bullish",
        "interpretation": "MACD above signal line indicates positive momentum"
      },
      "moving_averages": {
        "sma_20": 152.5,
        "sma_50": 150.2,
        "sma_200": 145.0,
        "ema_12": 156.8,
        "ema_26": 154.3,
        "golden_cross": true,
        "death_cross": false
      },
      "trend_analysis": {
        "short_term": "bullish",
        "medium_term": "bullish",
        "long_term": "bullish",
        "overall_trend": "bullish",
        "trend_strength": "strong"
      },
      "momentum_score": {
        "value": 75.2,
        "rating": "Good",
        "interpretation": "Positive momentum with favorable technical indicators"
      },
      "trading_signals": [
        "Golden cross detected - bullish long-term signal",
        "MACD bullish crossover - positive momentum",
        "Strong uptrend across all timeframes"
      ]
    }
    ```
    
    **Interpretation Guide**:
    - **RSI > 70**: Overbought (potential pullback)
    - **RSI < 30**: Oversold (potential bounce)
    - **RSI 30-70**: Neutral (balanced momentum)
    - **Golden Cross**: 50 SMA crosses above 200 SMA (bullish)
    - **Death Cross**: 50 SMA crosses below 200 SMA (bearish)
    - **MACD Bullish**: MACD line above signal line
    - **MACD Bearish**: MACD line below signal line
    
    **Use Cases**:
    - Identify entry/exit points for ETF positions
    - Confirm trend direction before trading
    - Spot potential trend reversals early
    - Compare momentum across multiple ETFs
    - Build technical analysis dashboards
    """,
    response_model=None,
    tags=["Phase 13: Advanced Analytics"]
)
async def get_momentum_indicators(
    ticker: str = Path(..., description="ETF ticker symbol (e.g., VOO, SPY, QQQ)"),
    period: str = Query("6m", description="Analysis period: 1m, 3m, 6m, 1y, 2y")
):
    """
    Calculate momentum indicators (RSI, MACD, moving averages, trend analysis).
    
    Returns comprehensive momentum analysis with trading signals.
    """
    try:
        logger.info(
            "Fetching momentum indicators",
            extra={"ticker": ticker, "period": period}
        )
        
        result = await etf_analytics_service.get_momentum_indicators(ticker, period)
        
        logger.info(
            "Momentum indicators calculated",
            extra={
                "ticker": ticker,
                "rsi": result.get("rsi", {}).get("value", 0),
                "momentum_score": result.get("momentum_score", {}).get("value", 0)
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid momentum request",
            extra={"ticker": ticker, "period": period, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Momentum indicators calculation failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Momentum indicators calculation failed: {str(e)}"
        )


@router.get(
    "/analytics/liquidity/{ticker}",
    summary="Analyze ETF Liquidity",
    description="""
    Analyze ETF liquidity for trading cost estimation.
    
    **Analysis Components**:
    - **Volume Metrics**: Average daily volume, trend, volatility, high-volume days %
    - **Spread Analysis**: Bid-ask spreads in basis points (bps), consistency
    - **AUM Trends**: Current AUM, period flows (inflows/outflows), consistency
    - **Liquidity Score**: Weighted composite (40% volume + 40% spread + 20% AUM)
    - **Trading Recommendations**: Guidance based on liquidity characteristics
    
    **Parameters**:
    - **ticker**: ETF symbol (e.g., SPY, VOO, QQQ)
    - **period**: Analysis timeframe (1m, 3m, 6m, 1y) - default 3m
    
    **Example Usage**:
    ```
    GET /etf/analytics/liquidity/SPY?period=3m
    ```
    
    **Response**:
    ```json
    {
      "ticker": "SPY",
      "period": "3m",
      "volume_metrics": {
        "avg_daily_volume": 50000000,
        "current_volume": 52000000,
        "volume_trend": "increasing",
        "volume_volatility": 0.12,
        "high_volume_days_pct": 22.5,
        "volume_score": 92.3
      },
      "spread_analysis": {
        "avg_spread_bps": 1.2,
        "current_spread_bps": 1.1,
        "spread_volatility": 0.05,
        "tight_spread_days_pct": 88.7,
        "spread_score": 95.8,
        "interpretation": "Very tight spread - excellent liquidity"
      },
      "aum_trends": {
        "current_aum_millions": 450000,
        "period_flow_millions": 15000,
        "flow_pct": 3.4,
        "trend": "strong_inflow",
        "consistency": 90.2,
        "aum_score": 88.5
      },
      "liquidity_score": {
        "value": 92.1,
        "rating": "Excellent",
        "interpretation": "Highly liquid with tight spreads and strong volume"
      },
      "trading_recommendations": [
        "Excellent liquidity suitable for all trading strategies",
        "Strong inflows indicate growing investor interest",
        "Very tight spreads minimize trading costs",
        "Suitable for large position sizes"
      ]
    }
    ```
    
    **Liquidity Ratings**:
    - **Excellent (≥80)**: Highly liquid, minimal trading costs, suitable for large positions
    - **Good (≥60)**: Good liquidity, reasonable costs, suitable for most strategies
    - **Fair (≥40)**: Moderate liquidity, watch for wider spreads during volatility
    - **Poor (<40)**: Low liquidity, higher trading costs, use limit orders
    
    **Spread Interpretation**:
    - **<3 bps**: Very tight spread (excellent liquidity)
    - **3-5 bps**: Tight spread (good liquidity)
    - **5-10 bps**: Moderate spread (fair liquidity)
    - **>10 bps**: Wide spread (poor liquidity, higher costs)
    
    **Use Cases**:
    - Evaluate trading costs before large orders
    - Compare liquidity across similar ETFs
    - Identify best execution timing
    - Assess suitability for active trading
    - Monitor AUM trends for ETF health
    """,
    response_model=None,
    tags=["Phase 13: Advanced Analytics"]
)
async def analyze_etf_liquidity(
    ticker: str = Path(..., description="ETF ticker symbol (e.g., SPY, VOO, QQQ)"),
    period: str = Query("3m", description="Analysis period: 1m, 3m, 6m, 1y")
):
    """
    Analyze ETF liquidity (volume, spreads, AUM trends).
    
    Returns comprehensive liquidity assessment with trading recommendations.
    """
    try:
        logger.info(
            "Analyzing ETF liquidity",
            extra={"ticker": ticker, "period": period}
        )
        
        result = await etf_analytics_service.analyze_liquidity(ticker, period)
        
        logger.info(
            "Liquidity analysis complete",
            extra={
                "ticker": ticker,
                "liquidity_score": result.get("liquidity_score", {}).get("value", 0),
                "avg_volume": result.get("volume_metrics", {}).get("avg_daily_volume", 0)
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid liquidity request",
            extra={"ticker": ticker, "period": period, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Liquidity analysis failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Liquidity analysis failed: {str(e)}"
        )


@router.get(
    "/analytics/factors/{ticker}",
    summary="Analyze Smart Beta Factors",
    description="""
    Analyze smart beta factor exposures to understand return drivers and risk.
    
    **Factors Analyzed**:
    - **Value Factor**: P/E ratio, P/B ratio, dividend yield
    - **Momentum Factor**: 6-month returns, 12-month returns, price momentum
    - **Quality Factor**: ROE (return on equity), debt-to-equity ratio, earnings stability
    - **Low-Volatility Factor**: Volatility percentage, beta vs market, max drawdown
    - **Size Factor**: Large/mid/small cap breakdown, average market cap
    
    **Parameters**:
    - **ticker**: ETF symbol (e.g., VTV for value, USMV for low-vol)
    
    **Example Usage**:
    ```
    GET /etf/analytics/factors/USMV
    ```
    
    **Response**:
    ```json
    {
      "ticker": "USMV",
      "etf_type": "low_volatility",
      "value_factor": {
        "score": 68.5,
        "rating": "Moderate Value",
        "metrics": {
          "avg_pe_ratio": 18.0,
          "avg_pb_ratio": 2.5,
          "dividend_yield_pct": 2.5
        },
        "interpretation": "Moderate value tilt with reasonable valuations"
      },
      "momentum_factor": {
        "score": 55.0,
        "rating": "Moderate Momentum",
        "metrics": {
          "returns_12m_pct": 10.0,
          "returns_6m_pct": 6.0,
          "price_momentum": 50.0
        },
        "interpretation": "Moderate momentum with positive trend"
      },
      "quality_factor": {
        "score": 75.5,
        "rating": "High Quality",
        "metrics": {
          "avg_roe_pct": 17.0,
          "avg_debt_to_equity": 1.3,
          "earnings_stability": 72.5
        },
        "interpretation": "High-quality companies with strong profitability"
      },
      "low_volatility_factor": {
        "score": 88.3,
        "rating": "Low Volatility",
        "metrics": {
          "volatility_pct": 10.0,
          "beta": 0.75,
          "max_drawdown_pct": -15.0
        },
        "interpretation": "Low volatility with defensive characteristics"
      },
      "size_factor": {
        "primary_exposure": "Large Cap",
        "market_cap_breakdown": {
          "large_cap_pct": 90.0,
          "mid_cap_pct": 8.0,
          "small_cap_pct": 2.0
        },
        "avg_market_cap_millions": 250000
      },
      "composite_analysis": {
        "overall_score": 71.8,
        "rating": "Good",
        "primary_factor_tilt": "Low Volatility",
        "tilt_strength": "Strong",
        "factor_diversification": "Concentrated in specific factors"
      },
      "investment_characteristics": [
        "Defensive approach with lower risk stocks",
        "Volatility: 10.0%",
        "Primary factor tilt: Strong Low Volatility",
        "Suitable for risk-averse investors"
      ],
      "comparison_to_market": {
        "valuation_vs_market": "Lower",
        "momentum_vs_market": "Lower",
        "quality_vs_market": "Lower",
        "volatility_vs_market": "Lower"
      }
    }
    ```
    
    **Factor Scoring**:
    - All factors scored 0-100 for easy comparison
    - Higher scores indicate stronger factor exposure
    - Composite score is equal-weighted average
    
    **Factor Ratings**:
    - **Strong (≥80)**: Dominant factor exposure
    - **High (≥60)**: Significant factor tilt
    - **Moderate (≥40)**: Balanced factor exposure
    - **Low (<40)**: Minimal factor tilt
    
    **Primary Tilt Strength**:
    - **Strong**: >20 points higher than other factors
    - **Moderate**: 10-20 points higher
    - **Weak**: <10 points difference (diversified)
    
    **ETF Type Detection**:
    - Automatically identifies ETF strategy (broad, value, growth, momentum, quality, low-vol)
    - Adjusts baseline metrics based on ETF type
    - Provides strategy-specific interpretations
    
    **Use Cases**:
    - Understand what drives ETF returns
    - Compare factor exposures across ETFs
    - Build factor-balanced portfolios
    - Identify defensive vs aggressive strategies
    - Evaluate alignment with investment goals
    - Select complementary ETFs for diversification
    """,
    response_model=None,
    tags=["Phase 13: Advanced Analytics"]
)
async def analyze_smart_beta_factors(
    ticker: str = Path(..., description="ETF ticker symbol (e.g., VTV, MTUM, QUAL, USMV)")
):
    """
    Analyze smart beta factor exposures (value, momentum, quality, low-vol).
    
    Returns comprehensive factor analysis with primary tilt identification.
    """
    try:
        logger.info(
            "Analyzing smart beta factors",
            extra={"ticker": ticker}
        )
        
        result = await etf_analytics_service.analyze_smart_beta_factors(ticker)
        
        logger.info(
            "Factor analysis complete",
            extra={
                "ticker": ticker,
                "composite_score": result.get("composite_analysis", {}).get("overall_score", 0),
                "primary_tilt": result.get("composite_analysis", {}).get("primary_factor_tilt", "Unknown")
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid factor analysis request",
            extra={"ticker": ticker, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Factor analysis failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Factor analysis failed: {str(e)}"
        )


# =============================================================================
# PHASE 14: PORTFOLIO BACKTESTING
# =============================================================================


@router.post(
    "/backtest/historical",
    summary="Run Historical Backtest",
    description="""
    Run historical backtest for a portfolio allocation with optional rebalancing.
    
    Simulates portfolio performance over a historical period to evaluate past performance
    and understand how the portfolio would have performed under real market conditions.
    
    **Request Body**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "initial_investment": 10000,
      "rebalance_frequency": "quarterly"
    }
    ```
    
    **Parameters**:
    - **portfolio**: Dictionary of ticker symbols to weights (must sum to 1.0)
    - **start_date**: Start date in YYYY-MM-DD format
    - **end_date**: End date in YYYY-MM-DD format
    - **initial_investment**: Starting portfolio value in dollars (default $10,000)
    - **rebalance_frequency**: "never", "monthly", "quarterly", "annually" (default "quarterly")
    
    **Response**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "period": {
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "trading_days": 1260
      },
      "performance_metrics": {
        "final_value": 14250.50,
        "total_return": 4250.50,
        "total_return_pct": 42.51,
        "cagr_pct": 9.25,
        "annualized_volatility_pct": 12.5,
        "sharpe_ratio": 0.82,
        "best_day_return_pct": 3.2,
        "worst_day_return_pct": -2.8
      },
      "risk_metrics": {
        "downside_volatility_pct": 8.5,
        "sortino_ratio": 1.15,
        "value_at_risk_95_pct": -1.8,
        "max_drawdown_pct": -15.2,
        "negative_days_pct": 42.5
      },
      "rebalancing_analysis": {
        "rebalance_count": 20,
        "avg_days_between_rebalances": 63,
        "interpretation": "Moderate rebalancing maintains allocation"
      }
    }
    ```
    
    **Performance Metrics**:
    - **Final Value**: Ending portfolio value
    - **Total Return**: Absolute profit/loss in dollars
    - **CAGR**: Compound Annual Growth Rate
    - **Sharpe Ratio**: Risk-adjusted return (>1.0 is good)
    - **Volatility**: Annualized standard deviation of returns
    
    **Risk Metrics**:
    - **Downside Volatility**: Volatility of negative returns only
    - **Sortino Ratio**: Risk-adjusted return using downside deviation
    - **Value at Risk (95%)**: Expected loss in worst 5% of days
    - **Max Drawdown**: Largest peak-to-trough decline
    
    **Rebalancing Strategies**:
    - **Never**: Buy and hold - no transaction costs, may drift
    - **Monthly**: Frequent rebalancing - maintains allocation, higher costs
    - **Quarterly**: Moderate - balances maintenance and costs
    - **Annually**: Minimal - low costs, may allow drift
    
    **Use Cases**:
    - Evaluate historical performance of portfolio strategy
    - Compare different asset allocations
    - Understand impact of rebalancing frequency
    - Assess risk-adjusted returns
    - Validate portfolio strategy before implementation
    """,
    response_model=None,
    tags=["Phase 14: Portfolio Backtesting"]
)
async def run_historical_backtest(
    portfolio: Dict[str, float] = Body(..., description="Portfolio allocation (ticker -> weight)"),
    start_date: str = Body(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Body(..., description="End date (YYYY-MM-DD)"),
    initial_investment: float = Body(10000.0, description="Initial investment in dollars"),
    rebalance_frequency: str = Body("quarterly", description="Rebalancing frequency")
):
    """
    Run historical backtest for portfolio allocation.
    
    Simulates portfolio performance with optional rebalancing over historical period.
    """
    try:
        logger.info(
            "Running historical backtest",
            extra={
                "tickers": list(portfolio.keys()),
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        result = await etf_backtesting_service.run_historical_backtest(
            portfolio=portfolio,
            start_date=start_date,
            end_date=end_date,
            initial_investment=initial_investment,
            rebalance_frequency=rebalance_frequency
        )
        
        logger.info(
            "Historical backtest completed",
            extra={
                "final_value": result.get("performance_metrics", {}).get("final_value", 0),
                "cagr_pct": result.get("performance_metrics", {}).get("cagr_pct", 0)
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid backtest request",
            extra={"portfolio": portfolio, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Historical backtest failed",
            extra={"portfolio": portfolio, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Historical backtest failed: {str(e)}"
        )


@router.post(
    "/backtest/monte-carlo",
    summary="Run Monte Carlo Simulation",
    description="""
    Run Monte Carlo simulation for portfolio future projections.
    
    Simulates thousands of possible future scenarios to estimate potential portfolio outcomes
    and understand the range of possibilities for your investment.
    
    **Request Body**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "initial_investment": 10000,
      "years": 10,
      "simulations": 1000,
      "confidence_level": 0.95
    }
    ```
    
    **Parameters**:
    - **portfolio**: Dictionary of ticker symbols to weights (must sum to 1.0)
    - **initial_investment**: Starting portfolio value in dollars (default $10,000)
    - **years**: Projection period in years (default 10)
    - **simulations**: Number of simulation runs (default 1000, min 100)
    - **confidence_level**: Confidence level for intervals (default 0.95)
    
    **Response**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "initial_investment": 10000,
      "projection_years": 10,
      "simulations_run": 1000,
      "simulation_statistics": {
        "mean_final_value": 25800.50,
        "median_final_value": 24500.00,
        "std_dev": 8500.00,
        "min_final_value": 12000.00,
        "max_final_value": 55000.00,
        "percentiles": {
          "p5": 15200.00,
          "p10": 17500.00,
          "p25": 21000.00,
          "p50": 24500.00,
          "p75": 29000.00,
          "p90": 36500.00,
          "p95": 42000.00
        },
        "confidence_interval": {
          "lower_bound": 15200.00,
          "upper_bound": 42000.00,
          "confidence_level": 0.95
        }
      },
      "probability_metrics": {
        "probability_of_profit_pct": 92.5,
        "probability_of_doubling_pct": 85.2,
        "probability_of_loss_pct": 7.5,
        "probability_of_major_loss_pct": 1.2,
        "interpretation": "Very high probability of profit"
      }
    }
    ```
    
    **Understanding Percentiles**:
    - **P5**: Worst-case scenario (5% of simulations worse)
    - **P10**: Very pessimistic outcome
    - **P25**: Below-average outcome
    - **P50 (Median)**: Middle outcome (50% above, 50% below)
    - **P75**: Above-average outcome
    - **P90**: Very optimistic outcome
    - **P95**: Best-case scenario (5% of simulations better)
    
    **Probability Metrics**:
    - **Probability of Profit**: Likelihood of ending above initial investment
    - **Probability of Doubling**: Likelihood of 2x return
    - **Probability of Loss**: Likelihood of negative return
    - **Probability of Major Loss**: Likelihood of losing >50%
    
    **Interpretation Guide**:
    - **>90% Profit Probability**: Very high confidence in positive returns
    - **75-90% Profit Probability**: High confidence
    - **60-75% Profit Probability**: Moderate confidence
    - **50-60% Profit Probability**: Balanced risk/reward
    - **<50% Profit Probability**: Higher risk profile
    
    **Use Cases**:
    - Estimate range of possible future outcomes
    - Understand probability of meeting financial goals
    - Compare risk profiles of different portfolios
    - Set realistic expectations for returns
    - Evaluate worst-case and best-case scenarios
    - Plan retirement or savings strategies
    """,
    response_model=None,
    tags=["Phase 14: Portfolio Backtesting"]
)
async def run_monte_carlo_simulation(
    portfolio: Dict[str, float] = Body(..., description="Portfolio allocation (ticker -> weight)"),
    initial_investment: float = Body(10000.0, description="Initial investment in dollars"),
    years: int = Body(10, description="Projection period in years"),
    simulations: int = Body(1000, description="Number of simulations (min 100)"),
    confidence_level: float = Body(0.95, description="Confidence level (0.90 or 0.95)")
):
    """
    Run Monte Carlo simulation for portfolio projections.
    
    Simulates multiple future scenarios to estimate potential outcomes.
    """
    try:
        logger.info(
            "Running Monte Carlo simulation",
            extra={
                "tickers": list(portfolio.keys()),
                "years": years,
                "simulations": simulations
            }
        )
        
        result = await etf_backtesting_service.run_monte_carlo_simulation(
            portfolio=portfolio,
            initial_investment=initial_investment,
            years=years,
            simulations=simulations,
            confidence_level=confidence_level
        )
        
        logger.info(
            "Monte Carlo simulation completed",
            extra={
                "median_value": result.get("simulation_statistics", {}).get("median_final_value", 0),
                "prob_profit": result.get("probability_metrics", {}).get("probability_of_profit_pct", 0)
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid Monte Carlo request",
            extra={"portfolio": portfolio, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Monte Carlo simulation failed",
            extra={"portfolio": portfolio, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Monte Carlo simulation failed: {str(e)}"
        )


@router.post(
    "/backtest/drawdowns",
    summary="Analyze Portfolio Drawdowns",
    description="""
    Analyze portfolio drawdowns and recovery periods.
    
    Identifies worst drawdowns, how long they lasted, and how quickly the portfolio recovered.
    Critical for understanding risk and emotional resilience required.
    
    **Request Body**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "initial_investment": 10000
    }
    ```
    
    **Parameters**:
    - **portfolio**: Dictionary of ticker symbols to weights (must sum to 1.0)
    - **start_date**: Start date in YYYY-MM-DD format
    - **end_date**: End date in YYYY-MM-DD format
    - **initial_investment**: Starting portfolio value in dollars (default $10,000)
    
    **Response**:
    ```json
    {
      "portfolio": {"VOO": 0.6, "BND": 0.4},
      "period": {
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "trading_days": 1260
      },
      "drawdown_statistics": {
        "max_drawdown_pct": -18.5,
        "avg_drawdown_pct": 6.2,
        "total_drawdowns": 8,
        "avg_duration_days": 45,
        "avg_recovery_days": 67
      },
      "major_drawdowns": [
        {
          "peak_date": "2020-02-19",
          "trough_date": "2020-03-23",
          "recovery_date": "2020-08-18",
          "drawdown_pct": -18.5,
          "duration_days": 33,
          "recovery_days": 148
        }
      ],
      "recovery_analysis": {
        "fastest_recovery_days": 15,
        "slowest_recovery_days": 148,
        "avg_recovery_days": 67,
        "interpretation": "Moderate recovery - portfolio typically recovers within 3 months"
      },
      "underwater_analysis": {
        "underwater_days": 380,
        "total_days": 1260,
        "underwater_pct": 30.2,
        "interpretation": "Portfolio frequently reaches new highs"
      },
      "current_drawdown": {
        "current_value": 14250.50,
        "peak_value": 14500.00,
        "drawdown_pct": -1.7,
        "peak_date": "2024-11-15",
        "status": "in_drawdown"
      }
    }
    ```
    
    **Understanding Drawdowns**:
    A **drawdown** is the decline from a previous peak to a trough (lowest point).
    
    **Example**: Portfolio reaches $15,000 (peak), drops to $12,000 (trough), then recovers.
    - **Drawdown**: -20% ($3,000 loss from peak)
    - **Duration**: Days from peak to trough
    - **Recovery**: Days from trough back to peak
    
    **Drawdown Statistics**:
    - **Max Drawdown**: Worst peak-to-trough decline (most important metric)
    - **Average Drawdown**: Typical decline magnitude
    - **Total Drawdowns**: Number of separate decline periods
    - **Average Duration**: Typical time to reach bottom
    - **Average Recovery**: Typical time to recover to peak
    
    **Recovery Analysis**:
    - **Fastest Recovery**: Quickest bounce-back period
    - **Slowest Recovery**: Longest time to new peak
    - **Average Recovery**: Typical recovery timeframe
    
    **Underwater Analysis**:
    **"Underwater"** = Portfolio below previous peak
    - **Underwater Days**: Days spent below peak
    - **Underwater %**: Percentage of time below peak
    - Lower % = More time at all-time highs (better)
    
    **Current Drawdown**:
    - Shows if portfolio is currently at peak or in decline
    - **Status**: "at_peak" (within 0.5% of peak) or "in_drawdown"
    
    **Risk Tolerance Assessment**:
    - **Max Drawdown -10%**: Low risk, conservative
    - **Max Drawdown -10% to -20%**: Moderate risk, balanced
    - **Max Drawdown -20% to -30%**: Higher risk, aggressive
    - **Max Drawdown >-30%**: Very high risk, very aggressive
    
    **Use Cases**:
    - Understand worst-case scenarios
    - Assess emotional/financial resilience needed
    - Compare risk profiles of portfolios
    - Evaluate impact of defensive assets (bonds, gold)
    - Plan for market downturns
    - Set realistic expectations for volatility
    """,
    response_model=None,
    tags=["Phase 14: Portfolio Backtesting"]
)
async def analyze_portfolio_drawdowns(
    portfolio: Dict[str, float] = Body(..., description="Portfolio allocation (ticker -> weight)"),
    start_date: str = Body(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Body(..., description="End date (YYYY-MM-DD)"),
    initial_investment: float = Body(10000.0, description="Initial investment in dollars")
):
    """
    Analyze portfolio drawdowns and recovery periods.
    
    Identifies worst drawdowns, duration, and recovery times.
    """
    try:
        logger.info(
            "Analyzing portfolio drawdowns",
            extra={
                "tickers": list(portfolio.keys()),
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        result = await etf_backtesting_service.analyze_drawdowns(
            portfolio=portfolio,
            start_date=start_date,
            end_date=end_date,
            initial_investment=initial_investment
        )
        
        logger.info(
            "Drawdown analysis completed",
            extra={
                "max_drawdown_pct": result.get("drawdown_statistics", {}).get("max_drawdown_pct", 0),
                "total_drawdowns": result.get("drawdown_statistics", {}).get("total_drawdowns", 0)
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning(
            "Invalid drawdown analysis request",
            extra={"portfolio": portfolio, "error": str(e)}
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Drawdown analysis failed",
            extra={"portfolio": portfolio, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Drawdown analysis failed: {str(e)}"
        )


# =============================================================================
# PHASE 15: DATA MANAGEMENT & ADMIN
# =============================================================================


@router.post(
    "/admin/bulk-refresh",
    summary="Bulk Data Refresh",
    description="""
    Refresh ETF data in bulk for multiple tickers.
    
    Efficiently updates data for multiple ETFs in a single operation,
    reducing API calls and improving performance.
    
    **Request Body**:
    ```json
    {
      "tickers": ["VOO", "BND", "VTI", "AGG"],
      "data_types": ["profile", "holdings", "performance"],
      "force_refresh": false
    }
    ```
    
    **Parameters**:
    - **tickers**: List of ETF tickers to refresh (max 50)
    - **data_types**: Types of data to refresh (optional, defaults to all)
      - `profile`: Basic ETF information
      - `holdings`: Portfolio holdings
      - `performance`: Historical performance
      - `dividends`: Dividend history
      - `risk_metrics`: Risk and volatility metrics
    - **force_refresh**: Force refresh even if data is recent
    
    **Response**:
    - Summary of refresh operation
    - Success/failure counts
    - Processing time and rate
    - Detailed results for each ticker
    
    **Use Cases**:
    - Update data after market close
    - Refresh stale data for multiple ETFs
    - Prepare data for batch analysis
    - System maintenance operations
    """
)
async def bulk_refresh_etf_data(
    tickers: list = Body(..., description="List of ETF tickers to refresh (max 50)"),
    data_types: Optional[list] = Body(None, description="Types of data to refresh"),
    force_refresh: bool = Body(False, description="Force refresh even if data is recent")
):
    """Bulk refresh ETF data for multiple tickers."""
    try:
        logger.info(
            "Bulk data refresh requested",
            extra={
                "ticker_count": len(tickers),
                "data_types": data_types,
                "force_refresh": force_refresh
            }
        )
        
        result = await etf_data_service.bulk_refresh_etf_data(
            tickers=tickers,
            data_types=data_types,
            force_refresh=force_refresh
        )
        
        logger.info(
            "Bulk data refresh completed",
            extra={
                "successful": result["summary"]["successful"],
                "failed": result["summary"]["failed"],
                "duration": result["summary"]["duration_seconds"]
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Invalid bulk refresh parameters", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Bulk data refresh failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Bulk data refresh failed: {str(e)}"
        )


@router.post(
    "/admin/cache",
    summary="Cache Management",
    description="""
    Manage cache operations for ETF data.
    
    Provides cache clearing, statistics, and optimization operations
    to improve system performance.
    
    **Request Body**:
    ```json
    {
      "operation": "stats",
      "cache_types": ["quotes", "profiles", "holdings"],
      "max_age_hours": 24
    }
    ```
    
    **Operations**:
    - **clear**: Clear cache entries
    - **stats**: Get cache statistics
    - **optimize**: Optimize cache performance
    - **evict_old**: Remove entries older than max_age_hours
    
    **Cache Types**:
    - `quotes`: Real-time quote data
    - `profiles`: ETF profile information
    - `holdings`: Portfolio holdings
    - `performance`: Historical performance
    - `dividends`: Dividend data
    - `risk_metrics`: Risk analysis
    - `comparisons`: Comparison results
    - `screening`: Screening results
    
    **Response**:
    - Operation results
    - Cache statistics
    - Memory usage
    - Hit rates and performance metrics
    
    **Use Cases**:
    - Clear cache before major updates
    - Monitor cache performance
    - Free memory by removing old entries
    - Optimize cache hit rates
    """
)
async def manage_cache(
    operation: str = Body(..., description="Cache operation (clear, stats, optimize, evict_old)"),
    cache_types: Optional[list] = Body(None, description="Types of cache to manage"),
    max_age_hours: Optional[int] = Body(None, description="Maximum age for cache entries (evict_old only)")
):
    """Manage cache operations."""
    try:
        logger.info(
            "Cache management operation requested",
            extra={
                "operation": operation,
                "cache_types": cache_types,
                "max_age_hours": max_age_hours
            }
        )
        
        result = await etf_data_service.manage_cache(
            operation=operation,
            cache_types=cache_types,
            max_age_hours=max_age_hours
        )
        
        logger.info(
            "Cache management completed",
            extra={"operation": operation}
        )
        
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Invalid cache operation", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Cache management failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Cache management failed: {str(e)}"
        )


@router.get(
    "/admin/health",
    summary="System Health Check",
    description="""
    Get comprehensive system health status.
    
    Monitors data freshness, API health, cache performance,
    and overall system metrics.
    
    **Query Parameters**:
    - **include_details**: Include detailed metrics for each component
    
    **Response Components**:
    - **Overall Status**: healthy, degraded, warning, critical
    - **Health Score**: 0-100 composite score
    - **Data Layer**: ETF data freshness and completeness
    - **API Layer**: Response times and error rates
    - **Cache Layer**: Hit rates and memory usage
    - **Database**: Connection pool and query performance
    
    **Health Indicators**:
    - ✅ **Healthy** (90-100): All systems operating normally
    - ⚠️ **Degraded** (70-89): Some performance issues detected
    - 🔶 **Warning** (50-69): Significant issues require attention
    - 🔴 **Critical** (<50): System stability at risk
    
    **Use Cases**:
    - Monitor system status
    - Detect performance degradation
    - Troubleshoot issues
    - Automated health checks
    - Dashboard monitoring
    
    **Example Response**:
    ```json
    {
      "overall_status": "healthy",
      "overall_health_score": 92.5,
      "components": {
        "data_layer": {"status": "healthy", "health_score": 95.0},
        "api_layer": {"status": "healthy", "health_score": 90.0},
        "cache_layer": {"status": "healthy", "health_score": 92.0},
        "database": {"status": "healthy", "health_score": 93.0}
      },
      "issues": [],
      "recommendations": ["System is healthy - continue monitoring"]
    }
    ```
    """
)
async def get_system_health(
    include_details: bool = Query(True, description="Include detailed metrics")
):
    """Get system health status."""
    try:
        logger.info(
            "System health check requested",
            extra={"include_details": include_details}
        )
        
        result = await etf_data_service.get_system_health(
            include_details=include_details
        )
        
        logger.info(
            "System health check completed",
            extra={
                "overall_status": result["overall_status"],
                "health_score": result["overall_health_score"],
                "issues_count": len(result["issues"])
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "System health check failed",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"System health check failed: {str(e)}"
        )

