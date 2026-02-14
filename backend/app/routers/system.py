"""
System monitoring and management endpoints.

Provides APIs for:
- Provider status monitoring
- Provider configuration hot-reload
- Load distribution stats
- Health checks
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional

from app.core.logging_config import get_logger
from app.services.providers import (
    provider_manager,
    provider_registry,
    load_balancer
)
from app.services.scheduler.scheduler import job_scheduler
from app.services.jobs.metadata_collector import metadata_collector_job
from app.services.jobs.massive_ticker_discovery import massive_ticker_discovery
from app.services.stock.metadata_enrichment_service import metadata_enrichment_service
from app.models.provider import CompanyOverview

logger = get_logger(__name__)
router = APIRouter(prefix="/system", tags=["System Management"])


@router.get("/health")
async def health_check():
    """
    System health check.
    
    Returns:
        {
            "status": "healthy",
            "providers_active": 3,
            "providers_healthy": 2
        }
    """
    stats = provider_manager.get_provider_stats()
    
    healthy_count = sum(1 for p in stats if p["is_healthy"])
    
    return {
        "status": "healthy" if healthy_count > 0 else "degraded",
        "providers_active": len(stats),
        "providers_healthy": healthy_count
    }


@router.get("/providers/status")
async def get_provider_status():
    """
    Get detailed status for all providers.
    
    Returns provider health, reliability, quota usage, and capabilities.
    
    Returns:
        {
            "providers": [
                {
                    "name": "AlphaVantageProvider",
                    "priority": 2,
                    "tier": "premium",
                    "is_healthy": true,
                    "reliability_score": 0.98,
                    "consecutive_failures": 0,
                    "success_rate": 0.99,
                    "total_calls": 1250,
                    "successful_calls": 1238,
                    "failed_calls": 12,
                    "average_response_time_ms": 245.6,
                    "capabilities": {
                        "REAL_TIME_QUOTE": "EXCELLENT",
                        "HISTORICAL_PRICES": "EXCELLENT"
                    }
                },
                ...
            ],
            "total_providers": 3,
            "healthy_providers": 2
        }
    
    Example:
        curl http://localhost:8000/system/providers/status
    """
    stats = provider_manager.get_provider_stats()
    
    healthy_count = sum(1 for p in stats if p["is_healthy"])
    
    return {
        "providers": stats,
        "total_providers": len(stats),
        "healthy_providers": healthy_count
    }


@router.get("/providers/load-distribution")
async def get_load_distribution():
    """
    Get load distribution statistics across providers.
    
    Shows how requests are being distributed based on
    quota availability, reliability, and other factors.
    
    Returns:
        {
            "distribution": {
                "AlphaVantageProvider": {
                    "total_calls": 450,
                    "percentage": 36.0,
                    "last_selected": "2025-11-16T10:30:00Z"
                },
                "YFinanceProvider": {
                    "total_calls": 550,
                    "percentage": 44.0,
                    "last_selected": "2025-11-16T10:29:45Z"
                },
                "FinnhubProvider": {
                    "total_calls": 250,
                    "percentage": 20.0,
                    "last_selected": "2025-11-16T10:29:30Z"
                }
            },
            "total_calls": 1250
        }
    
    Example:
        curl http://localhost:8000/system/providers/load-distribution
    """
    stats = load_balancer.get_load_distribution_stats()
    
    return stats


@router.post("/providers/reload")
async def reload_providers():
    """
    Hot-reload provider configurations.
    
    Use this endpoint after:
    - Upgrading API tier
    - Adding new API keys to environment
    - Changing provider priorities
    - Modifying rate limits
    
    The system will automatically:
    - Re-scan environment variables
    - Detect tier changes
    - Update rate limits
    - Reload provider instances
    
    Returns:
        {
            "status": "success",
            "message": "Providers reloaded successfully",
            "providers_loaded": 3,
            "providers": ["AlphaVantageProvider", "YFinanceProvider", "FinnhubProvider"]
        }
    
    Example:
        curl -X POST http://localhost:8000/system/providers/reload
    """
    try:
        await provider_manager.reload_providers()
        
        stats = provider_manager.get_provider_stats()
        
        return {
            "status": "success",
            "message": "Providers reloaded successfully",
            "providers_loaded": len(stats),
            "providers": [p["name"] for p in stats]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload providers: {str(e)}"
        )


@router.get("/providers/{provider_name}/health")
async def get_provider_health(provider_name: str):
    """
    Get health details for a specific provider.
    
    Args:
        provider_name: Provider name (e.g., AlphaVantageProvider)
    
    Returns:
        {
            "name": "AlphaVantageProvider",
            "is_healthy": true,
            "last_success": "2025-11-16T10:29:45Z",
            "last_failure": "2025-11-16T09:15:20Z",
            "consecutive_failures": 0,
            "total_calls": 1250,
            "successful_calls": 1238,
            "failed_calls": 12,
            "success_rate": 0.99,
            "average_response_time_ms": 245.6,
            "reliability_score": 0.98
        }
    
    Example:
        curl http://localhost:8000/system/providers/AlphaVantageProvider/health
    """
    stats = provider_manager.get_provider_stats()
    
    provider_stat = next(
        (p for p in stats if p["name"] == provider_name),
        None
    )
    
    if not provider_stat:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )
    
    return provider_stat


@router.get("/providers/{provider_name}/capabilities")
async def get_provider_capabilities(provider_name: str):
    """
    Get capabilities for a specific provider.
    
    Shows what data types the provider supports and
    at what capability level (EXCELLENT, GOOD, BASIC, NONE).
    
    Args:
        provider_name: Provider name
    
    Returns:
        {
            "name": "AlphaVantageProvider",
            "capabilities": {
                "REAL_TIME_QUOTE": "EXCELLENT",
                "HISTORICAL_PRICES": "EXCELLENT",
                "TECHNICAL_INDICATOR": "EXCELLENT",
                "FUNDAMENTAL_DATA": "EXCELLENT",
                "NEWS": "GOOD",
                "DIVIDENDS": "BASIC",
                "SPLITS": "BASIC",
                "EARNINGS": "EXCELLENT"
            }
        }
    
    Example:
        curl http://localhost:8000/system/providers/AlphaVantageProvider/capabilities
    """
    stats = provider_manager.get_provider_stats()
    
    provider_stat = next(
        (p for p in stats if p["name"] == provider_name),
        None
    )
    
    if not provider_stat:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )
    
    return {
        "name": provider_name,
        "capabilities": provider_stat["capabilities"]
    }


@router.post("/providers/{provider_name}/disable")
async def disable_provider(provider_name: str):
    """
    Temporarily disable a provider.
    
    Useful for:
    - Maintenance windows
    - Testing failover behavior
    - Quota exhaustion recovery
    
    Args:
        provider_name: Provider to disable
    
    Returns:
        {
            "status": "success",
            "message": "Provider disabled",
            "provider": "AlphaVantageProvider"
        }
    
    Example:
        curl -X POST http://localhost:8000/system/providers/AlphaVantageProvider/disable
    """
    try:
        # Remove provider from registry
        provider_registry.remove_provider(provider_name)
        
        return {
            "status": "success",
            "message": "Provider disabled",
            "provider": provider_name
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disable provider: {str(e)}"
        )


@router.post("/providers/{provider_name}/enable")
async def enable_provider(provider_name: str):
    """
    Re-enable a previously disabled provider.
    
    Args:
        provider_name: Provider to enable
    
    Returns:
        {
            "status": "success",
            "message": "Provider enabled",
            "provider": "AlphaVantageProvider"
        }
    
    Example:
        curl -X POST http://localhost:8000/system/providers/AlphaVantageProvider/enable
    """
    try:
        # Reload all providers (will pick up enabled ones)
        await provider_manager.reload_providers()
        
        return {
            "status": "success",
            "message": "Provider enabled",
            "provider": provider_name
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable provider: {str(e)}"
        )


# ============================================================================
# Scheduler Management Endpoints
# ============================================================================

@router.get("/scheduler/info")
async def get_scheduler_info():
    """
    Get comprehensive scheduler information.
    
    Returns information about all scheduled jobs including:
    - Job ID, name, and schedule (cron expression)
    - Next run time
    - Scheduler status (running/stopped)
    
    This endpoint provides complete observability into the background
    job system, showing all automated tasks and their execution schedule.
    
    Returns:
        {
            "scheduler_status": "running",
            "total_jobs": 3,
            "jobs": [
                {
                    "id": "price_collector",
                    "name": "Stock Price Collection",
                    "next_run": "2025-11-17T14:35:00-05:00",
                    "trigger": "cron[day_of_week='mon-fri', hour='9-16', minute='*', second='0']"
                },
                {
                    "id": "market_close_poll",
                    "name": "Market Close Price Poll",
                    "next_run": "2025-11-17T17:00:00-05:00",
                    "trigger": "cron[day_of_week='mon-fri', hour='17', minute='0', second='0']"
                },
                {
                    "id": "metals_price_collector",
                    "name": "Precious Metals Price Collection",
                    "next_run": "2025-11-18T10:00:00+05:30",
                    "trigger": "cron[hour='10', minute='0', second='0']"
                }
            ]
        }
    
    Example:
        curl http://localhost:8000/system/scheduler/info
    """
    try:
        jobs = job_scheduler.get_all_jobs()
        
        # Filter out None values (jobs that might have been removed)
        valid_jobs = [job for job in jobs if job is not None]
        
        return {
            "scheduler_status": "running" if job_scheduler.is_running else "stopped",
            "total_jobs": len(valid_jobs),
            "jobs": valid_jobs
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduler info: {str(e)}"
        )


@router.get("/scheduler/jobs/{job_id}")
async def get_job_info(job_id: str):
    """
    Get detailed information for a specific scheduled job.
    
    Args:
        job_id: Job identifier (e.g., 'price_collector', 'market_close_poll')
    
    Returns:
        {
            "id": "price_collector",
            "name": "Stock Price Collection",
            "next_run": "2025-11-17T14:35:00-05:00",
            "trigger": "cron[day_of_week='mon-fri', hour='9-16', minute='*', second='0']"
        }
    
    Example:
        curl http://localhost:8000/system/scheduler/jobs/price_collector
    """
    try:
        job_status = job_scheduler.get_job_status(job_id)
        
        if not job_status:
            raise HTTPException(
                status_code=404,
                detail=f"Job '{job_id}' not found"
            )
        
        return job_status
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job info: {str(e)}"
        )


# ============================================================================
# Metadata Management Endpoints
# ============================================================================

@router.post("/metadata/discovery/trigger")
async def trigger_metadata_discovery(
    limit: Optional[int] = None,
    test_mode: bool = False
):
    """
    Manually trigger one-off metadata discovery.
    
    Process:
    1. Fetch all tickers from Alpha Vantage LISTING_STATUS
    2. Collect base metadata from YFinance (batch processing)
    3. Queue high-priority tickers for enrichment
    
    Args:
        limit: Limit number of tickers to process (optional)
        test_mode: If True, only process first 20 tickers for testing
    
    Returns:
        {
            "status": "success",
            "discovered_tickers": 10000,
            "processed_tickers": 10000,
            "collection_stats": {
                "success": 9500,
                "failure": 500,
                "total": 10000
            },
            "priority_enrichment_queued": 200,
            "elapsed_seconds": 3000.5,
            "asset_type_breakdown": {
                "Stock": 8500,
                "ETF": 1500
            }
        }
    
    Example:
        # Test with 20 tickers
        curl -X POST "http://localhost:8000/system/metadata/discovery/trigger?test_mode=true"
        
        # Full discovery
        curl -X POST http://localhost:8000/system/metadata/discovery/trigger
        
        # Limited to 1000 tickers
        curl -X POST "http://localhost:8000/system/metadata/discovery/trigger?limit=1000"
    """
    try:
        result = await metadata_collector_job.run_one_off_discovery(
            limit=limit,
            test_mode=test_mode
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger discovery: {str(e)}"
        )


@router.post("/metadata/collection/batch")
async def trigger_incremental_batch_collection():
    """
    Manually trigger incremental batch collection.
    
    Process:
    - Collects 30 tickers per batch
    - Ordered by market cap (descending)
    - Failed tickers moved to next run
    - Runs 24 times/day automatically (every hour, 00:00 - 23:00)
    - Total: 720 tickers/day
    
    Returns:
        {
            "status": "success",
            "processed": 30,
            "success": 28,
            "failure": 2,
            "elapsed_seconds": 45.2
        }
    
    Example:
        curl -X POST http://localhost:8000/system/metadata/collection/batch
    """
    try:
        result = await metadata_collector_job.run_incremental_batch_collection()
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger batch collection: {str(e)}"
        )


@router.post("/metadata/discovery/massive")
async def trigger_massive_discovery(
    max_batches: Optional[int] = Query(None, description="Max batches to process (None = all)"),
    test_mode: bool = Query(False, description="Test mode: process only 1 batch (1,000 tickers)")
):
    """
    Bulk ticker discovery using MASSIVE/Polygon.io.
    
    Process:
    1. Paginate through Polygon.io ticker list (1,000 tickers per call)
    2. Save minimal placeholders to database for base collection
    3. Respect 5 calls/minute rate limit (12 seconds between calls)
    
    Timeline:
    - 10,000 tickers ÷ 1,000 per call = 10 API calls
    - 5 calls/minute = 2 minutes total
    - Concurrent saves: ~30 seconds
    - Total: ~2.5 minutes for full discovery
    
    Args:
        max_batches: Limit batches to process (1 batch = 1,000 tickers)
        test_mode: If True, process only 1 batch for testing
    
    Returns:
        {
            "status": "success",
            "batches_processed": 10,
            "tickers_discovered": 10000,
            "placeholders_created": 9950,
            "failures": 50,
            "elapsed_seconds": 150.5,
            "database_stats": {
                "total_tickers": 11066,
                "needs_base_metadata": 8934
            },
            "rate_info": {
                "tickers_per_minute": 4000,
                "api_calls": 10,
                "rate_limit": "5 calls/minute"
            }
        }
    
    Example:
        # Test with 1,000 tickers (1 batch)
        curl -X POST "http://localhost:8000/system/metadata/discovery/massive?test_mode=true"
        
        # Process 3 batches (3,000 tickers)
        curl -X POST "http://localhost:8000/system/metadata/discovery/massive?max_batches=3"
        
        # Full discovery (~10,000 tickers)
        curl -X POST http://localhost:8000/system/metadata/discovery/massive
    """
    try:
        result = await massive_ticker_discovery.run(
            limit_per_batch=1000,
            max_batches=max_batches,
            test_mode=test_mode
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger MASSIVE discovery: {str(e)}"
        )


@router.post("/metadata/enrich/{ticker}")
async def trigger_ticker_enrichment(ticker: str):
    """
    Manually trigger Alpha Vantage enrichment for specific ticker.
    
    Useful for high-priority tickers that need immediate enrichment.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, VOO)
    
    Returns:
        {
            "status": "success",
            "ticker": "AAPL",
            "enrichment_status": "enriched",
            "message": "Metadata enriched successfully"
        }
    
    Example:
        curl -X POST http://localhost:8000/system/metadata/enrich/AAPL
        curl -X POST http://localhost:8000/system/metadata/enrich/VOO
    """
    try:
        # Get existing metadata
        existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker.upper())
        
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"No metadata found for ticker {ticker}. Run discovery first."
            )
        
        # Enrich with Alpha Vantage
        enriched = await metadata_enrichment_service.enrich_with_alpha_vantage(
            ticker=ticker.upper(),
            existing_metadata=existing
        )
        
        if not enriched:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enrich metadata for {ticker}"
            )
        
        # Save enriched metadata
        saved = await metadata_enrichment_service.save_metadata(enriched)
        
        return {
            "status": "success",
            "ticker": ticker.upper(),
            "enrichment_status": saved.enrichment_status,
            "message": "Metadata enriched successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enrich ticker: {str(e)}"
        )


@router.post("/metadata/foundation/{ticker}")
async def trigger_foundation_collection(ticker: str):
    """
    [TEST ENDPOINT] Trigger foundation metadata collection via MASSIVE for specific ticker.
    
    This endpoint is for Phase 3 testing - validates that all 30+ MASSIVE fields
    are properly captured and stored at top level (not in extended_data).
    
    Args:
        ticker: Ticker symbol to enrich
        
    Returns:
        {
            "status": "success",
            "ticker": "MSFT",
            "enrichment_status": "foundation",
            "fields_captured": 32,
            "has_cik": true,
            "has_branding": true,
            "metadata": {...}
        }
    """
    try:
        ticker = ticker.upper()
        
        # Collect foundation metadata from MASSIVE
        metadata = await metadata_enrichment_service.collect_foundation_metadata(ticker)
        
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Could not collect foundation metadata for {ticker}"
            )
        
        # Save to database
        saved = await metadata_enrichment_service.save_metadata(metadata)
        
        # Count non-null fields for verification
        saved_dict = saved.dict()
        fields_captured = len([v for v in saved_dict.values() if v is not None and v != "" and v != []])
        
        return {
            "status": "success",
            "ticker": ticker,
            "enrichment_status": saved.enrichment_status,
            "fields_captured": fields_captured,
            "has_cik": bool(saved.cik),
            "has_composite_figi": bool(saved.composite_figi),
            "has_logo_url": bool(saved.logo_url),
            "has_icon_url": bool(saved.icon_url),
            "has_address1": bool(saved.address1),
            "has_phone_number": bool(saved.phone_number),
            "metadata_sources": saved.metadata_sources,
            "message": f"Foundation metadata collected successfully ({fields_captured} fields)"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to trigger foundation collection",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect foundation metadata: {str(e)}"
        )


@router.get("/metadata/stats")
async def get_metadata_statistics():
    """
    Get metadata collection statistics.
    
    Returns:
        {
            "total_tickers": 10000,
            "by_enrichment_status": {
                "base": 9500,
                "enriched": 450,
                "failed": 50
            },
            "by_asset_type": {
                "Stock": 8500,
                "ETF": 1500
            },
            "by_exchange": {
                "NASDAQ": 4000,
                "NYSE": 3500,
                "Other": 2500
            },
            "enrichment_queue": {
                "etfs_pending": 150,
                "large_caps_pending": 300,
                "total_pending": 9500
            },
            "job_status": {
                "is_running": false,
                "last_discovery_run": "2025-11-22T10:30:00Z",
                "last_enrichment_run": "2025-11-22T02:00:00Z",
                "discovery_count": 9500,
                "enrichment_count": 450
            }
        }
    
    Example:
        curl http://localhost:8000/system/metadata/stats
    """
    try:
        # Get total count
        total = await CompanyOverview.count()
        
        # Count by enrichment status
        base_count = await CompanyOverview.find(
            {"enrichment_status": "base"}
        ).count()
        
        foundation_count = await CompanyOverview.find(
            {"enrichment_status": "foundation"}
        ).count()
        
        enriched_count = await CompanyOverview.find(
            {"enrichment_status": "enriched"}
        ).count()
        
        failed_count = await CompanyOverview.find(
            {"enrichment_status": "failed"}
        ).count()
        
        # Count by asset type
        stocks = await CompanyOverview.find(
            CompanyOverview.asset_type == "Stock"
        ).count()
        
        etfs = await CompanyOverview.find(
            CompanyOverview.asset_type == "ETF"
        ).count()
        
        # Count ETFs pending enrichment
        etfs_pending = await CompanyOverview.find(
            CompanyOverview.asset_type == "ETF",
            CompanyOverview.enrichment_status == "base"
        ).count()
        
        # Count large caps pending enrichment
        large_caps_pending = await CompanyOverview.find(
            CompanyOverview.asset_type == "Stock",
            CompanyOverview.enrichment_status == "base",
            CompanyOverview.market_cap > 10_000_000_000
        ).count()
        
        # Get job status
        job_status = metadata_collector_job.get_job_status()
        
        return {
            "total_tickers": total,
            "by_enrichment_status": {
                "base": base_count,
                "foundation": foundation_count,
                "enriched": enriched_count,
                "failed": failed_count
            },
            "by_asset_type": {
                "Stock": stocks,
                "ETF": etfs,
                "Other": total - stocks - etfs
            },
            "enrichment_queue": {
                "etfs_pending": etfs_pending,
                "large_caps_pending": large_caps_pending,
                "needs_foundation": base_count,
                "total_pending": base_count
            },
            "job_status": job_status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metadata stats: {str(e)}"
        )


@router.get("/metadata/failed")
async def get_failed_tickers(
    limit: int = Query(100, description="Maximum number of failed tickers to return"),
    skip: int = Query(0, description="Number of failed tickers to skip for pagination")
):
    """
    Get list of tickers that have exhausted retry attempts.
    
    A ticker is considered "failed" if it has collection_attempts >= 3.
    These tickers will not be retried automatically.
    
    Query Parameters:
        - limit: Maximum number of results (default: 100)
        - skip: Number of results to skip for pagination (default: 0)
    
    Returns:
        {
            "total_failed": 28,
            "returned": 28,
            "failed_tickers": [
                {
                    "ticker": "ZYXI",
                    "collection_attempts": 4,
                    "last_collection_attempt": "2025-11-23T13:32:46Z",
                    "collection_error": "YFinance rate limit exceeded",
                    "has_metadata": true,
                    "market_cap": 18777138
                },
                ...
            ]
        }
    
    Example:
        curl http://localhost:8000/system/metadata/failed?limit=50
    """
    try:
        # Count total failed tickers
        total_failed = await CompanyOverview.find(
            CompanyOverview.collection_attempts >= 3
        ).count()
        
        # Get failed tickers with details
        failed_docs = await CompanyOverview.find(
            CompanyOverview.collection_attempts >= 3
        ).sort([
            ("collection_attempts", -1),  # Most attempts first
            ("ticker", 1)  # Then alphabetically
        ]).skip(skip).limit(limit).to_list()
        
        # Format response
        failed_tickers = []
        for doc in failed_docs:
            failed_tickers.append({
                "ticker": doc.ticker,
                "collection_attempts": doc.collection_attempts,
                "last_collection_attempt": doc.last_collection_attempt.isoformat() if doc.last_collection_attempt else None,
                "collection_error": doc.collection_error,
                "has_metadata": bool(doc.name or doc.market_cap),  # Check if metadata exists
                "market_cap": doc.market_cap,
                "enrichment_status": doc.enrichment_status
            })
        
        return {
            "total_failed": total_failed,
            "returned": len(failed_tickers),
            "skip": skip,
            "limit": limit,
            "failed_tickers": failed_tickers
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get failed tickers: {str(e)}"
        )
