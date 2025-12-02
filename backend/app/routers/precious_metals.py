"""
Precious Metals API Router
Endpoints for gold and silver price data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.services.precious_metals.metals_price_service import metals_price_service
from app.services.jobs.metals_price_collector import metals_price_collector_job
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/precious-metals", tags=["Precious Metals"])


# ============================================================================
# Manual Fetching Endpoints
# ============================================================================

@router.post("/fetch/gold")
async def fetch_gold_prices():
    """
    Manually trigger gold price fetching and save to database.
    
    Uses Puppeteer browser automation to bypass Cloudflare protection.
    
    Returns:
        Status and fetched gold price data
    """
    logger.info("POST /precious-metals/fetch/gold")
    
    try:
        result = await metals_price_service.fetch_and_save_gold_prices()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to fetch gold prices")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Gold fetching endpoint error",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fetch/silver")
async def fetch_silver_prices():
    """
    Manually trigger silver price fetching and save to database.
    
    Returns:
        Status and fetched silver price data
    """
    logger.info("POST /precious-metals/fetch/silver")
    
    try:
        result = await metals_price_service.fetch_and_save_silver_prices()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Silver fetching endpoint error",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fetch/all")
async def fetch_all_prices():
    """
    Manually trigger both gold and silver price fetching.
    
    Returns:
        Combined status for both metals
    """
    logger.info("POST /precious-metals/fetch/all")
    
    try:
        result = await metals_price_service.fetch_and_save_all_prices()
        return result
    except Exception as e:
        logger.error(
            "All metals fetching endpoint error",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Data Retrieval Endpoints
# ============================================================================

@router.get("/latest")
async def get_latest_prices(city: str = Query("Chennai")):
    """
    Get latest gold and silver prices from database.
    
    Query Parameters:
        city: City name (default: Chennai)
    
    Returns:
        Latest prices for both metals
    """
    logger.info("GET /precious-metals/latest", extra={"city": city})
    
    try:
        result = await metals_price_service.get_latest_prices(city)
        
        if not result["gold"] and not result["silver"]:
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for {city}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Latest prices endpoint error",
            extra={"error": str(e), "city": city},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/gold")
async def get_gold_history(
    city: str = Query("Chennai"),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get historical gold prices.
    
    Query Parameters:
        city: City name (default: Chennai)
        days: Number of days of history (1-365, default: 30)
    
    Returns:
        List of historical gold prices
    """
    logger.info(
        "GET /precious-metals/history/gold",
        extra={"city": city, "days": days}
    )
    
    try:
        history = await metals_price_service.get_price_history(
            metal="gold",
            city=city,
            days=days
        )
        
        return {
            "city": city,
            "days": days,
            "count": len(history),
            "data": history
        }
    except Exception as e:
        logger.error(
            "Gold history endpoint error",
            extra={"error": str(e), "city": city},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/silver")
async def get_silver_history(
    city: str = Query("Chennai"),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get historical silver prices.
    
    Query Parameters:
        city: City name (default: Chennai)
        days: Number of days of history (1-365, default: 30)
    
    Returns:
        List of historical silver prices
    """
    logger.info(
        "GET /precious-metals/history/silver",
        extra={"city": city, "days": days}
    )
    
    try:
        history = await metals_price_service.get_price_history(
            metal="silver",
            city=city,
            days=days
        )
        
        return {
            "city": city,
            "days": days,
            "count": len(history),
            "data": history
        }
    except Exception as e:
        logger.error(
            "Silver history endpoint error",
            extra={"error": str(e), "city": city},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Job Management Endpoints
# ============================================================================

@router.post("/job/trigger")
async def trigger_collection_job():
    """
    Manually trigger the scheduled collection job.
    Useful for testing and immediate updates.
    
    Returns:
        Job execution result
    """
    logger.info("POST /precious-metals/job/trigger")
    
    try:
        result = await metals_price_collector_job.run_manual()
        return {
            "message": "Job triggered successfully",
            "result": result
        }
    except Exception as e:
        logger.error(
            "Job trigger endpoint error",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/job/stats")
async def get_job_stats():
    """
    Get statistics about the scheduled collection job.
    
    Returns:
        Job execution statistics
    """
    logger.info("GET /precious-metals/job/stats")
    
    try:
        stats = metals_price_collector_job.get_stats()
        return stats
    except Exception as e:
        logger.error(
            "Job stats endpoint error",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
