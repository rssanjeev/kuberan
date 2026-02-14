"""
Monitoring and Metrics Models.

Beanie ODM models for tracking system health, provider performance,
and API usage statistics.
"""

from beanie import Document
from pydantic import Field
from pymongo import IndexModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    """API call status."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class ProviderAPICall(Document):
    """
    Track individual API calls to external providers.
    
    Timeseries collection with 30-day TTL for API usage monitoring.
    """
    
    # Provider identification
    provider: str = Field(..., description="Provider name (alpha_vantage, yfinance, finnhub)")
    data_type: str = Field(..., description="Type of data requested (quote, historical, news, etc.)")
    
    # Call details
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the call was made")
    status: CallStatus = Field(..., description="Call result status")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    
    # Request information
    ticker: Optional[str] = Field(None, description="Ticker symbol if applicable")
    endpoint: Optional[str] = Field(None, description="API endpoint called")
    
    # Error information (if failed)
    error_message: Optional[str] = Field(None, description="Error message if call failed")
    http_status_code: Optional[int] = Field(None, description="HTTP status code")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional call metadata")
    
    class Settings:
        name = "provider_api_calls"
        timeseries = {
            "time_field": "timestamp",
            "meta_field": "provider",
            "granularity": "minutes"
        }
        indexes = [
            IndexModel([("provider", 1), ("timestamp", -1)]),
            IndexModel([("provider", 1), ("status", 1), ("timestamp", -1)]),
            IndexModel([("provider", 1), ("data_type", 1), ("timestamp", -1)]),
            IndexModel([("ticker", 1), ("timestamp", -1)]),
        ]


class ProviderDailyStats(Document):
    """
    Daily aggregated statistics per provider.
    
    Permanent storage for historical analysis and cost tracking.
    """
    
    # Identification
    provider: str = Field(..., description="Provider name")
    date: datetime = Field(..., description="Date (midnight UTC)")
    
    # Call counts by status
    total_calls: int = Field(default=0, description="Total API calls")
    successful_calls: int = Field(default=0, description="Successful calls")
    failed_calls: int = Field(default=0, description="Failed calls")
    rate_limited_calls: int = Field(default=0, description="Rate limited calls")
    timeout_calls: int = Field(default=0, description="Timeout calls")
    
    # Performance metrics
    avg_response_time_ms: Optional[float] = Field(None, description="Average response time")
    min_response_time_ms: Optional[int] = Field(None, description="Minimum response time")
    max_response_time_ms: Optional[int] = Field(None, description="Maximum response time")
    
    # Call breakdown by data type
    calls_by_data_type: Dict[str, int] = Field(default_factory=dict, description="Calls per data type")
    
    # Cost tracking (if applicable)
    estimated_cost: Optional[float] = Field(None, description="Estimated cost based on pricing tier")
    
    # Reliability metrics
    success_rate: float = Field(default=0.0, description="Success rate (0.0 to 1.0)")
    uptime_percentage: float = Field(default=100.0, description="Uptime percentage")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "provider_daily_stats"
        indexes = [
            IndexModel([("provider", 1), ("date", -1)], unique=True),
            IndexModel([("date", -1)]),
            IndexModel([("provider", 1), ("success_rate", -1)]),
        ]


class ProviderHealthCheck(Document):
    """
    Provider health check results.
    
    Timeseries collection with 7-day TTL for monitoring provider availability.
    """
    
    # Provider identification
    provider: str = Field(..., description="Provider name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    
    # Health status
    is_healthy: bool = Field(..., description="Whether provider is operational")
    status_code: Optional[int] = Field(None, description="HTTP status code from health check")
    response_time_ms: Optional[int] = Field(None, description="Response time")
    
    # Current state
    consecutive_failures: int = Field(default=0, description="Number of consecutive failures")
    reliability_score: float = Field(default=1.0, description="Current reliability score (0.0-1.0)")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    
    class Settings:
        name = "provider_health_checks"
        timeseries = {
            "time_field": "timestamp",
            "meta_field": "provider",
            "granularity": "minutes"
        }
        indexes = [
            IndexModel([("provider", 1), ("timestamp", -1)]),
            IndexModel([("provider", 1), ("is_healthy", 1), ("timestamp", -1)]),
        ]


class RateLimitStatus(Document):
    """
    Current rate limit status per provider.
    
    Real-time tracking of rate limit usage (short TTL: 1 hour).
    """
    
    # Provider identification
    provider: str = Field(..., description="Provider name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Status timestamp")
    
    # Rate limit information
    limit_per_minute: Optional[int] = Field(None, description="Max calls per minute")
    limit_per_day: Optional[int] = Field(None, description="Max calls per day")
    limit_per_month: Optional[int] = Field(None, description="Max calls per month")
    
    # Current usage
    calls_this_minute: int = Field(default=0, description="Calls in current minute")
    calls_today: int = Field(default=0, description="Calls today")
    calls_this_month: int = Field(default=0, description="Calls this month")
    
    # Remaining capacity
    remaining_minute: Optional[int] = Field(None, description="Remaining calls this minute")
    remaining_today: Optional[int] = Field(None, description="Remaining calls today")
    remaining_month: Optional[int] = Field(None, description="Remaining calls this month")
    
    # Reset times
    minute_resets_at: Optional[datetime] = Field(None, description="When minute limit resets")
    day_resets_at: Optional[datetime] = Field(None, description="When daily limit resets")
    month_resets_at: Optional[datetime] = Field(None, description="When monthly limit resets")
    
    # Metadata
    pricing_tier: Optional[str] = Field(None, description="Free, Premium, etc.")
    
    class Settings:
        name = "rate_limit_status"
        timeseries = {
            "time_field": "timestamp",
            "meta_field": "provider",
            "granularity": "minutes"
        }
        indexes = [
            IndexModel([("provider", 1), ("timestamp", -1)]),
        ]
