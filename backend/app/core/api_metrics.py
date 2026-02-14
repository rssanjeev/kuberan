"""
API Metrics Tracking.

Utilities for tracking API calls to external providers, monitoring
performance, and managing rate limits.
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from functools import wraps
from app.core.logging_config import get_logger
from app.models.monitoring import (
    ProviderAPICall,
    CallStatus,
    ProviderDailyStats,
    RateLimitStatus,
)

logger = get_logger(__name__)


class APIMetricsTracker:
    """
    Track API call metrics for external providers.
    
    Features:
    - Automatic call logging to MongoDB
    - Performance monitoring (response times)
    - Success/failure tracking
    - Daily statistics aggregation
    - Rate limit tracking
    """
    
    def __init__(self):
        self.enabled = True
    
    async def record_call(
        self,
        provider: str,
        data_type: str,
        status: CallStatus,
        response_time_ms: Optional[int] = None,
        ticker: Optional[str] = None,
        endpoint: Optional[str] = None,
        error_message: Optional[str] = None,
        http_status_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record an API call to MongoDB.
        
        Args:
            provider: Provider name (alpha_vantage, yfinance, finnhub)
            data_type: Type of data (quote, historical, news, etc.)
            status: Call status (success, failure, timeout, rate_limited)
            response_time_ms: Response time in milliseconds
            ticker: Ticker symbol if applicable
            endpoint: API endpoint called
            error_message: Error message if failed
            http_status_code: HTTP status code
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            call = ProviderAPICall(
                provider=provider,
                data_type=data_type,
                status=status,
                response_time_ms=response_time_ms,
                ticker=ticker,
                endpoint=endpoint,
                error_message=error_message,
                http_status_code=http_status_code,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            
            await call.insert()
            
            logger.debug(
                "API call recorded",
                extra={
                    "provider": provider,
                    "data_type": data_type,
                    "status": status.value,
                    "response_time_ms": response_time_ms,
                }
            )
            
        except Exception as e:
            # Don't fail the actual API call if metrics recording fails
            logger.error(
                "Failed to record API call metrics",
                extra={"provider": provider, "error": str(e)},
                exc_info=True
            )
    
    def track_api_call(
        self,
        provider: str,
        data_type: str,
        ticker: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        Decorator to automatically track API calls.
        
        Usage:
            @api_metrics.track_api_call("yfinance", "quote", ticker="AAPL")
            async def fetch_quote(ticker: str):
                return await yf.get_quote(ticker)
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = CallStatus.SUCCESS
                error_message = None
                http_status_code = None
                result = None
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if result indicates failure
                    if result is None:
                        status = CallStatus.FAILURE
                        error_message = "Function returned None"
                    
                    return result
                    
                except TimeoutError as e:
                    status = CallStatus.TIMEOUT
                    error_message = str(e)
                    raise
                    
                except Exception as e:
                    status = CallStatus.FAILURE
                    error_message = str(e)
                    
                    # Check for rate limiting
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        status = CallStatus.RATE_LIMITED
                    
                    # Try to extract HTTP status code
                    if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                        http_status_code = e.response.status_code
                    
                    raise
                    
                finally:
                    # Calculate response time
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Record the call
                    await self.record_call(
                        provider=provider,
                        data_type=data_type,
                        status=status,
                        response_time_ms=response_time_ms,
                        ticker=ticker,
                        endpoint=endpoint,
                        error_message=error_message,
                        http_status_code=http_status_code,
                    )
            
            return wrapper
        return decorator
    
    async def get_daily_stats(
        self,
        provider: str,
        date: Optional[datetime] = None
    ) -> Optional[ProviderDailyStats]:
        """
        Get daily statistics for a provider.
        
        Args:
            provider: Provider name
            date: Date to query (defaults to today)
        
        Returns:
            ProviderDailyStats if exists, None otherwise
        """
        if date is None:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        stats = await ProviderDailyStats.find_one(
            ProviderDailyStats.provider == provider,
            ProviderDailyStats.date == date
        )
        
        return stats
    
    async def aggregate_daily_stats(
        self,
        provider: str,
        date: Optional[datetime] = None
    ) -> ProviderDailyStats:
        """
        Aggregate API calls into daily statistics.
        
        This should be run as a daily background job to compute
        statistics from the raw API call logs.
        
        Args:
            provider: Provider name
            date: Date to aggregate (defaults to yesterday)
        
        Returns:
            ProviderDailyStats document
        """
        if date is None:
            # Default to yesterday (complete day)
            date = (datetime.utcnow() - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        
        # Query all calls for this provider on this date
        start_of_day = date
        end_of_day = date + timedelta(days=1)
        
        calls = await ProviderAPICall.find(
            ProviderAPICall.provider == provider,
            ProviderAPICall.timestamp >= start_of_day,
            ProviderAPICall.timestamp < end_of_day
        ).to_list()
        
        if not calls:
            logger.warning(
                "No API calls found for aggregation",
                extra={"provider": provider, "date": date.isoformat()}
            )
            return None
        
        # Calculate statistics
        total_calls = len(calls)
        successful_calls = sum(1 for c in calls if c.status == CallStatus.SUCCESS)
        failed_calls = sum(1 for c in calls if c.status == CallStatus.FAILURE)
        rate_limited_calls = sum(1 for c in calls if c.status == CallStatus.RATE_LIMITED)
        timeout_calls = sum(1 for c in calls if c.status == CallStatus.TIMEOUT)
        
        # Response time statistics
        response_times = [c.response_time_ms for c in calls if c.response_time_ms is not None]
        avg_response_time_ms = sum(response_times) / len(response_times) if response_times else None
        min_response_time_ms = min(response_times) if response_times else None
        max_response_time_ms = max(response_times) if response_times else None
        
        # Call breakdown by data type
        calls_by_data_type = {}
        for call in calls:
            calls_by_data_type[call.data_type] = calls_by_data_type.get(call.data_type, 0) + 1
        
        # Calculate success rate
        success_rate = successful_calls / total_calls if total_calls > 0 else 0.0
        
        # Check if stats already exist (update) or create new
        existing_stats = await self.get_daily_stats(provider, date)
        
        if existing_stats:
            # Update existing
            existing_stats.total_calls = total_calls
            existing_stats.successful_calls = successful_calls
            existing_stats.failed_calls = failed_calls
            existing_stats.rate_limited_calls = rate_limited_calls
            existing_stats.timeout_calls = timeout_calls
            existing_stats.avg_response_time_ms = avg_response_time_ms
            existing_stats.min_response_time_ms = min_response_time_ms
            existing_stats.max_response_time_ms = max_response_time_ms
            existing_stats.calls_by_data_type = calls_by_data_type
            existing_stats.success_rate = success_rate
            existing_stats.updated_at = datetime.utcnow()
            
            await existing_stats.save()
            stats = existing_stats
        else:
            # Create new
            stats = ProviderDailyStats(
                provider=provider,
                date=date,
                total_calls=total_calls,
                successful_calls=successful_calls,
                failed_calls=failed_calls,
                rate_limited_calls=rate_limited_calls,
                timeout_calls=timeout_calls,
                avg_response_time_ms=avg_response_time_ms,
                min_response_time_ms=min_response_time_ms,
                max_response_time_ms=max_response_time_ms,
                calls_by_data_type=calls_by_data_type,
                success_rate=success_rate,
            )
            
            await stats.insert()
        
        logger.info(
            "Daily stats aggregated",
            extra={
                "provider": provider,
                "date": date.isoformat(),
                "total_calls": total_calls,
                "success_rate": success_rate,
            }
        )
        
        return stats
    
    async def get_rate_limit_status(
        self,
        provider: str
    ) -> Optional[RateLimitStatus]:
        """
        Get current rate limit status for provider.
        
        Args:
            provider: Provider name
        
        Returns:
            Most recent RateLimitStatus if exists
        """
        status = await RateLimitStatus.find_one(
            RateLimitStatus.provider == provider,
            sort=[("timestamp", -1)]
        )
        
        return status
    
    async def update_rate_limit_status(
        self,
        provider: str,
        limit_per_minute: Optional[int] = None,
        limit_per_day: Optional[int] = None,
        limit_per_month: Optional[int] = None,
        calls_this_minute: int = 0,
        calls_today: int = 0,
        calls_this_month: int = 0,
        pricing_tier: Optional[str] = None
    ) -> RateLimitStatus:
        """
        Update rate limit status for provider.
        
        This should be called by rate limiters after each API call.
        """
        now = datetime.utcnow()
        
        # Calculate remaining capacity
        remaining_minute = (limit_per_minute - calls_this_minute) if limit_per_minute else None
        remaining_today = (limit_per_day - calls_today) if limit_per_day else None
        remaining_month = (limit_per_month - calls_this_month) if limit_per_month else None
        
        # Calculate reset times
        minute_resets_at = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        day_resets_at = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        month_resets_at = (now.replace(day=1) + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        status = RateLimitStatus(
            provider=provider,
            timestamp=now,
            limit_per_minute=limit_per_minute,
            limit_per_day=limit_per_day,
            limit_per_month=limit_per_month,
            calls_this_minute=calls_this_minute,
            calls_today=calls_today,
            calls_this_month=calls_this_month,
            remaining_minute=remaining_minute,
            remaining_today=remaining_today,
            remaining_month=remaining_month,
            minute_resets_at=minute_resets_at,
            day_resets_at=day_resets_at,
            month_resets_at=month_resets_at,
            pricing_tier=pricing_tier,
        )
        
        await status.insert()
        
        return status


# Singleton instance
api_metrics = APIMetricsTracker()
