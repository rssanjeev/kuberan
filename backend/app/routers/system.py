"""
System monitoring and management endpoints.

Provides APIs for:
- Provider status monitoring
- Provider configuration hot-reload
- Load distribution stats
- Health checks
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List

from app.services.providers import (
    provider_manager,
    provider_registry,
    load_balancer
)
from app.services.scheduler.scheduler import job_scheduler

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
