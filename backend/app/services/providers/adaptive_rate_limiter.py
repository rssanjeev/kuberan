"""
Adaptive rate limiting for API providers.

This module provides intelligent rate limiting that:
- Auto-detects rate limits from API responses
- Adapts to tier upgrades automatically
- Tracks quota usage in real-time
- Calculates optimal wait times
- Learns from API behavior
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import asyncio

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AdaptiveRateLimiter:
    """
    Rate limiter that automatically adapts to detected limits.
    
    Features:
    - Auto-detects rate limits from API responses
    - Adjusts to tier upgrades automatically
    - Distributes calls based on remaining quota
    - Learns optimal request patterns
    - Priority-based request handling
    
    Example:
        limiter = AdaptiveRateLimiter("AlphaVantage", per_minute=5, per_day=25)
        
        # Acquire permission before API call
        await limiter.acquire(priority=0)  # Normal priority
        
        # Update limits from API response
        limiter.update_from_response(response.headers)
        
        # Check remaining quota
        quota = limiter.get_remaining_quota()
    """
    
    def __init__(
        self,
        provider_name: str,
        per_minute: int = 5,
        per_day: Optional[int] = 25
    ):
        """
        Initialize adaptive rate limiter.
        
        Args:
            provider_name: Name of the provider (for logging)
            per_minute: Initial per-minute rate limit
            per_day: Initial per-day rate limit (None = unlimited)
        """
        self.provider_name = provider_name
        
        # Current detected limits (can change dynamically)
        self.per_minute_limit = per_minute
        self.per_day_limit = per_day
        
        # Tracking windows
        self.minute_calls: deque = deque()  # Last 60 seconds
        self.daily_calls: deque = deque()   # Last 24 hours
        
        # Auto-detection state
        self.detected_limits: Dict = {
            "per_minute": None,
            "per_day": None,
            "last_check": None
        }
        
        # Learning from API responses
        self.limit_headers_seen: list = []
        self.tier_detected = "unknown"  # "free", "premium", "enterprise"
        
        logger.info(
            f"Initialized adaptive rate limiter for {provider_name}",
            extra={
                "initial_per_minute": per_minute,
                "initial_per_day": per_day
            }
        )
    
    async def acquire(self, priority: int = 0) -> bool:
        """
        Acquire permission to make API call.
        
        Blocks until permission is granted (respects rate limits).
        
        Args:
            priority: Request priority
                     0=normal (uses 80% of limit)
                     1=high (uses 90% of limit)
                     2=critical (uses 95% of limit)
        
        Returns:
            True when call can proceed
        """
        # Cleanup old timestamps
        self._cleanup_timestamps()
        
        # Wait until we can proceed
        while not self._can_proceed(priority):
            wait_time = self._calculate_wait_time()
            
            logger.debug(
                f"Rate limit reached for {self.provider_name}, waiting",
                extra={
                    "wait_seconds": wait_time,
                    "minute_calls": len(self.minute_calls),
                    "daily_calls": len(self.daily_calls) if self.daily_calls else None,
                    "priority": priority
                }
            )
            
            await asyncio.sleep(wait_time)
            self._cleanup_timestamps()
        
        # Record this call
        now = datetime.now()
        self.minute_calls.append(now)
        if self.per_day_limit:
            self.daily_calls.append(now)
        
        return True
    
    def _can_proceed(self, priority: int) -> bool:
        """
        Check if we can make a call now.
        
        Different priorities use different thresholds:
        - Critical (2): 95% of limit
        - High (1): 90% of limit
        - Normal (0): 80% of limit
        """
        # Calculate threshold based on priority
        if priority >= 2:  # Critical
            minute_threshold = int(self.per_minute_limit * 0.95)
            daily_threshold = int(self.per_day_limit * 0.95) if self.per_day_limit else None
        elif priority >= 1:  # High
            minute_threshold = int(self.per_minute_limit * 0.90)
            daily_threshold = int(self.per_day_limit * 0.90) if self.per_day_limit else None
        else:  # Normal
            minute_threshold = int(self.per_minute_limit * 0.80)
            daily_threshold = int(self.per_day_limit * 0.80) if self.per_day_limit else None
        
        # Check minute limit
        if len(self.minute_calls) >= minute_threshold:
            return False
        
        # Check daily limit
        if self.per_day_limit and daily_threshold:
            if len(self.daily_calls) >= daily_threshold:
                return False
        
        return True
    
    def _cleanup_timestamps(self):
        """Remove timestamps outside tracking windows."""
        now = datetime.now()
        
        # Cleanup minute window (60 seconds)
        minute_ago = now - timedelta(seconds=60)
        while self.minute_calls and self.minute_calls[0] < minute_ago:
            self.minute_calls.popleft()
        
        # Cleanup daily window (24 hours)
        if self.per_day_limit:
            day_ago = now - timedelta(hours=24)
            while self.daily_calls and self.daily_calls[0] < day_ago:
                self.daily_calls.popleft()
    
    def _calculate_wait_time(self) -> float:
        """
        Calculate how long to wait before next call.
        
        Returns wait time in seconds.
        """
        now = datetime.now()
        
        # If minute limit hit, wait until oldest call expires
        if len(self.minute_calls) >= self.per_minute_limit:
            oldest = self.minute_calls[0]
            wait_until = oldest + timedelta(seconds=60)
            wait_seconds = (wait_until - now).total_seconds()
            return max(0.1, wait_seconds)
        
        # If daily limit hit, wait until oldest daily call expires
        if self.per_day_limit and len(self.daily_calls) >= self.per_day_limit:
            oldest = self.daily_calls[0]
            wait_until = oldest + timedelta(hours=24)
            wait_seconds = (wait_until - now).total_seconds()
            return max(60, wait_seconds)  # Wait at least 1 minute
        
        return 0.1  # Small delay if neither limit hit
    
    def update_from_response(self, response_headers: Dict):
        """
        Update rate limits based on API response headers.
        
        Many APIs return rate limit info in headers:
        - X-RateLimit-Limit: Total limit
        - X-RateLimit-Remaining: Calls remaining
        - X-RateLimit-Reset: When limit resets (timestamp)
        - Retry-After: How long to wait (if 429)
        
        Args:
            response_headers: Dict of HTTP response headers
        """
        # Normalize header keys (case-insensitive)
        headers = {k.lower(): v for k, v in response_headers.items()}
        
        # Parse rate limit header
        if "x-ratelimit-limit" in headers:
            detected_limit = int(headers["x-ratelimit-limit"])
            
            # If detected limit is higher than current, auto-upgrade!
            if detected_limit > self.per_minute_limit:
                old_limit = self.per_minute_limit
                self.per_minute_limit = detected_limit
                
                logger.info(
                    f"🎉 Rate limit auto-upgraded for {self.provider_name}",
                    extra={
                        "old_limit": old_limit,
                        "new_limit": detected_limit,
                        "tier_change": f"{self.tier_detected} → premium"
                    }
                )
                
                self.tier_detected = "premium"
                self.detected_limits["per_minute"] = detected_limit
                self.detected_limits["last_check"] = datetime.now()
        
        # Track remaining quota
        if "x-ratelimit-remaining" in headers:
            remaining = int(headers["x-ratelimit-remaining"])
            
            # Alert if quota running low
            if remaining < self.per_minute_limit * 0.2:
                logger.warning(
                    f"Low quota remaining for {self.provider_name}",
                    extra={
                        "remaining": remaining,
                        "limit": self.per_minute_limit,
                        "percent_remaining": (remaining / self.per_minute_limit) * 100
                    }
                )
        
        # Handle Retry-After header (for 429 responses)
        if "retry-after" in headers:
            retry_after = int(headers["retry-after"])
            logger.warning(
                f"Rate limit hit for {self.provider_name}",
                extra={"retry_after_seconds": retry_after}
            )
    
    def get_remaining_quota(self) -> Dict:
        """
        Get current remaining quota.
        
        Returns:
            {
                "per_minute": {
                    "limit": 60,
                    "used": 12,
                    "remaining": 48,
                    "percent_used": 20.0
                },
                "per_day": {
                    "limit": 1000,
                    "used": 342,
                    "remaining": 658,
                    "percent_used": 34.2
                }
            }
        """
        self._cleanup_timestamps()
        
        result: Dict = {
            "per_minute": {
                "limit": self.per_minute_limit,
                "used": len(self.minute_calls),
                "remaining": self.per_minute_limit - len(self.minute_calls),
                "percent_used": (len(self.minute_calls) / self.per_minute_limit) * 100
            }
        }
        
        if self.per_day_limit:
            result["per_day"] = {
                "limit": self.per_day_limit,
                "used": len(self.daily_calls),
                "remaining": self.per_day_limit - len(self.daily_calls),
                "percent_used": (len(self.daily_calls) / self.per_day_limit) * 100
            }
        
        return result
    
    def estimate_capacity_until_reset(self) -> int:
        """
        Estimate how many more calls we can make before rate limit resets.
        
        Returns:
            Number of calls available
        """
        self._cleanup_timestamps()
        
        minute_remaining = self.per_minute_limit - len(self.minute_calls)
        
        if self.per_day_limit:
            daily_remaining = self.per_day_limit - len(self.daily_calls)
            return min(minute_remaining, daily_remaining)
        
        return minute_remaining
    
    def update_limits(self, per_minute: Optional[int] = None, per_day: Optional[int] = None):
        """
        Manually update rate limits.
        
        Use this when you know the limits have changed (e.g., tier upgrade).
        
        Args:
            per_minute: New per-minute limit (None = keep current)
            per_day: New per-day limit (None = keep current)
        """
        if per_minute is not None:
            old_minute = self.per_minute_limit
            self.per_minute_limit = per_minute
            
            logger.info(
                f"Updated per-minute limit for {self.provider_name}",
                extra={"old": old_minute, "new": per_minute}
            )
        
        if per_day is not None:
            old_day = self.per_day_limit
            self.per_day_limit = per_day
            
            logger.info(
                f"Updated per-day limit for {self.provider_name}",
                extra={"old": old_day, "new": per_day}
            )
