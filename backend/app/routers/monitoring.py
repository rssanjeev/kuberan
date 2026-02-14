"""
Monitoring API endpoints for provider metrics.

Provides endpoints to query API call tracking data, provider statistics,
and performance metrics.
"""

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.models.monitoring import ProviderAPICall, ProviderDailyStats, CallStatus
from app.core.logging_config import get_logger

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = get_logger(__name__)


@router.get("/providers/summary")
async def get_providers_summary():
    """
    Get summary statistics for all providers (today).
    
    Returns:
        Summary with total calls, success rate, avg response time per provider
    """
    logger.info("Fetching provider summary")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    providers = ["alpha_vantage", "finnhub", "yfinance"]
    summaries = []
    
    for provider in providers:
        calls = await ProviderAPICall.find(
            ProviderAPICall.provider == provider,
            ProviderAPICall.timestamp >= today_start
        ).to_list()
        
        total = len(calls)
        
        if total == 0:
            summaries.append({
                "provider": provider,
                "total_calls_today": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "rate_limited_calls": 0,
                "timeout_calls": 0,
                "success_rate": 0.0,
                "avg_response_time_ms": 0.0
            })
            continue
        
        successful = sum(1 for c in calls if c.status == CallStatus.SUCCESS)
        failed = sum(1 for c in calls if c.status == CallStatus.FAILURE)
        rate_limited = sum(1 for c in calls if c.status == CallStatus.RATE_LIMITED)
        timeout = sum(1 for c in calls if c.status == CallStatus.TIMEOUT)
        
        response_times = [c.response_time_ms for c in calls if c.response_time_ms is not None]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        summaries.append({
            "provider": provider,
            "total_calls_today": total,
            "successful_calls": successful,
            "failed_calls": failed,
            "rate_limited_calls": rate_limited,
            "timeout_calls": timeout,
            "success_rate": round(successful / total, 4) if total > 0 else 0,
            "avg_response_time_ms": round(avg_response, 2)
        })
    
    logger.info("Provider summary fetched", extra={"provider_count": len(summaries)})
    
    return {
        "providers": summaries,
        "as_of": datetime.utcnow().isoformat()
    }


@router.get("/providers/{provider}/stats")
async def get_provider_stats(
    provider: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve")
):
    """
    Get daily statistics for a provider over N days.
    
    Args:
        provider: Provider name (alpha_vantage, finnhub, yfinance)
        days: Number of days to retrieve (1-90)
        
    Returns:
        Daily statistics including call counts, success rates, response times
    """
    logger.info(
        "Fetching provider stats",
        extra={"provider": provider, "days": days}
    )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = await ProviderDailyStats.find(
        ProviderDailyStats.provider == provider,
        ProviderDailyStats.date >= start_date
    ).sort([("date", -1)]).to_list()
    
    if not stats:
        logger.warning(
            "No statistics found",
            extra={"provider": provider, "days": days}
        )
        raise HTTPException(
            status_code=404,
            detail=f"No statistics found for provider '{provider}' in last {days} days"
        )
    
    return {
        "provider": provider,
        "period_days": days,
        "stats_count": len(stats),
        "daily_stats": [
            {
                "date": s.date.isoformat(),
                "total_calls": s.total_calls,
                "successful_calls": s.successful_calls,
                "failed_calls": s.failed_calls,
                "rate_limited_calls": s.rate_limited_calls,
                "timeout_calls": s.timeout_calls,
                "success_rate": s.success_rate,
                "avg_response_time_ms": s.avg_response_time_ms,
                "min_response_time_ms": s.min_response_time_ms,
                "max_response_time_ms": s.max_response_time_ms,
                "calls_by_data_type": s.calls_by_data_type,
                "estimated_cost": s.estimated_cost,
                "uptime_percentage": s.uptime_percentage
            }
            for s in stats
        ]
    }


@router.get("/providers/{provider}/recent-calls")
async def get_recent_calls(
    provider: str,
    limit: int = Query(50, ge=1, le=500, description="Number of calls to retrieve"),
    status: Optional[str] = Query(None, description="Filter by status (success, failure, timeout, rate_limited)"),
    data_type: Optional[str] = Query(None, description="Filter by data type (quote, historical, etc.)")
):
    """
    Get recent API calls for a provider.
    
    Args:
        provider: Provider name
        limit: Maximum number of calls to return
        status: Optional status filter
        data_type: Optional data type filter
        
    Returns:
        List of recent API calls with details
    """
    logger.info(
        "Fetching recent calls",
        extra={
            "provider": provider,
            "limit": limit,
            "status_filter": status,
            "data_type_filter": data_type
        }
    )
    
    # Build query
    query = ProviderAPICall.provider == provider
    
    if status:
        try:
            status_enum = CallStatus(status)
            query = query & (ProviderAPICall.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be: success, failure, timeout, rate_limited"
            )
    
    if data_type:
        query = query & (ProviderAPICall.data_type == data_type)
    
    calls = await ProviderAPICall.find(query) \
        .sort([("timestamp", -1)]) \
        .limit(limit) \
        .to_list()
    
    logger.info(
        "Recent calls fetched",
        extra={"provider": provider, "count": len(calls)}
    )
    
    return {
        "provider": provider,
        "count": len(calls),
        "filters": {
            "status": status,
            "data_type": data_type
        },
        "calls": [
            {
                "timestamp": c.timestamp.isoformat(),
                "data_type": c.data_type,
                "status": c.status.value,
                "response_time_ms": c.response_time_ms,
                "ticker": c.ticker,
                "endpoint": c.endpoint,
                "error_message": c.error_message,
                "http_status_code": c.http_status_code
            }
            for c in calls
        ]
    }


@router.get("/providers/{provider}/performance")
async def get_provider_performance(
    provider: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
):
    """
    Get performance metrics for a provider over the last N hours.
    
    Args:
        provider: Provider name
        hours: Number of hours to analyze (1-168)
        
    Returns:
        Performance metrics including response times, success rate, error breakdown
    """
    logger.info(
        "Fetching provider performance",
        extra={"provider": provider, "hours": hours}
    )
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    calls = await ProviderAPICall.find(
        ProviderAPICall.provider == provider,
        ProviderAPICall.timestamp >= start_time
    ).to_list()
    
    if not calls:
        raise HTTPException(
            status_code=404,
            detail=f"No calls found for provider '{provider}' in last {hours} hours"
        )
    
    # Calculate metrics
    total = len(calls)
    successful = sum(1 for c in calls if c.status == CallStatus.SUCCESS)
    failed = sum(1 for c in calls if c.status == CallStatus.FAILURE)
    rate_limited = sum(1 for c in calls if c.status == CallStatus.RATE_LIMITED)
    timeout = sum(1 for c in calls if c.status == CallStatus.TIMEOUT)
    
    response_times = [c.response_time_ms for c in calls if c.response_time_ms is not None]
    
    # Group by data type
    data_type_breakdown: Dict[str, int] = {}
    for call in calls:
        data_type = call.data_type or "unknown"
        data_type_breakdown[data_type] = data_type_breakdown.get(data_type, 0) + 1
    
    # Recent errors
    error_calls = [c for c in calls if c.error_message is not None]
    recent_errors = [
        {
            "timestamp": c.timestamp.isoformat(),
            "data_type": c.data_type,
            "error_message": c.error_message,
            "http_status_code": c.http_status_code
        }
        for c in sorted(error_calls, key=lambda x: x.timestamp, reverse=True)[:10]
    ]
    
    return {
        "provider": provider,
        "period_hours": hours,
        "total_calls": total,
        "status_breakdown": {
            "successful": successful,
            "failed": failed,
            "rate_limited": rate_limited,
            "timeout": timeout
        },
        "success_rate": round(successful / total, 4) if total > 0 else 0,
        "response_times": {
            "avg_ms": round(sum(response_times) / len(response_times), 2) if response_times else 0,
            "min_ms": min(response_times) if response_times else 0,
            "max_ms": max(response_times) if response_times else 0,
            "p50_ms": round(sorted(response_times)[len(response_times)//2], 2) if response_times else 0,
            "p95_ms": round(sorted(response_times)[int(len(response_times)*0.95)], 2) if len(response_times) > 0 else 0
        },
        "data_type_breakdown": data_type_breakdown,
        "recent_errors": recent_errors
    }


@router.get("/calls/all")
async def get_all_recent_calls(
    limit: int = Query(100, ge=1, le=1000, description="Number of calls to retrieve"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back")
):
    """
    Get recent API calls across all providers.
    
    Args:
        limit: Maximum number of calls to return
        hours: Number of hours to look back
        
    Returns:
        List of recent API calls from all providers
    """
    logger.info("Fetching all recent calls", extra={"limit": limit, "hours": hours})
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    calls = await ProviderAPICall.find(
        ProviderAPICall.timestamp >= start_time
    ).sort([("timestamp", -1)]).limit(limit).to_list()
    
    return {
        "count": len(calls),
        "period_hours": hours,
        "calls": [
            {
                "timestamp": c.timestamp.isoformat(),
                "provider": c.provider,
                "data_type": c.data_type,
                "status": c.status.value,
                "response_time_ms": c.response_time_ms,
                "ticker": c.ticker,
                "error_message": c.error_message
            }
            for c in calls
        ]
    }


@router.get("/stats/aggregate")
async def get_aggregate_stats(
    days: int = Query(7, ge=1, le=90, description="Number of days to aggregate")
):
    """
    Get aggregated statistics across all providers.
    
    Args:
        days: Number of days to aggregate (1-90)
        
    Returns:
        Aggregated statistics for all providers
    """
    logger.info("Fetching aggregate stats", extra={"days": days})
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = await ProviderDailyStats.find(
        ProviderDailyStats.date >= start_date
    ).to_list()
    
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"No statistics found for last {days} days"
        )
    
    # Aggregate by provider
    provider_totals: Dict[str, Dict[str, Any]] = {}
    
    for stat in stats:
        if stat.provider not in provider_totals:
            provider_totals[stat.provider] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "rate_limited_calls": 0,
                "timeout_calls": 0,
                "total_response_time": 0,
                "response_time_count": 0
            }
        
        pt = provider_totals[stat.provider]
        pt["total_calls"] += stat.total_calls
        pt["successful_calls"] += stat.successful_calls
        pt["failed_calls"] += stat.failed_calls
        pt["rate_limited_calls"] += stat.rate_limited_calls
        pt["timeout_calls"] += stat.timeout_calls
        
        if stat.avg_response_time_ms:
            pt["total_response_time"] += stat.avg_response_time_ms * stat.total_calls
            pt["response_time_count"] += stat.total_calls
    
    # Calculate averages
    aggregated = []
    for provider, totals in provider_totals.items():
        total = totals["total_calls"]
        aggregated.append({
            "provider": provider,
            "total_calls": total,
            "successful_calls": totals["successful_calls"],
            "failed_calls": totals["failed_calls"],
            "rate_limited_calls": totals["rate_limited_calls"],
            "timeout_calls": totals["timeout_calls"],
            "success_rate": round(totals["successful_calls"] / total, 4) if total > 0 else 0,
            "avg_response_time_ms": round(
                totals["total_response_time"] / totals["response_time_count"], 2
            ) if totals["response_time_count"] > 0 else 0
        })
    
    # Sort by total calls
    aggregated.sort(key=lambda x: x["total_calls"], reverse=True)
    
    return {
        "period_days": days,
        "providers": aggregated,
        "grand_total": sum(p["total_calls"] for p in aggregated)
    }
