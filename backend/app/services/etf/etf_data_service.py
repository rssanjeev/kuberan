"""
ETF Data Management Service.

Provides bulk data refresh, cache management, and system health monitoring
for the ETF platform.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from statistics import mean

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ETFDataService:
    """Data management service for ETF platform."""
    
    def __init__(self):
        """Initialize data service."""
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "last_refresh": datetime.now()
        }
        self._refresh_history: List[Dict[str, Any]] = []
        logger.info("ETF Data Service initialized")
    
    # =========================================================================
    # BULK DATA REFRESH
    # =========================================================================
    
    async def bulk_refresh_etf_data(
        self,
        tickers: List[str],
        data_types: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Refresh ETF data in bulk for multiple tickers.
        
        Efficiently updates data for multiple ETFs in a single operation,
        reducing API calls and improving performance.
        
        Args:
            tickers: List of ETF tickers to refresh
            data_types: Types of data to refresh (profile, holdings, performance, etc.)
            force_refresh: Force refresh even if data is recent
        
        Returns:
            Refresh summary with success/failure counts
        """
        logger.info(
            "Starting bulk data refresh",
            extra={
                "ticker_count": len(tickers),
                "data_types": data_types,
                "force_refresh": force_refresh
            }
        )
        
        start_time = datetime.now()
        
        # Default to all data types if none specified
        if data_types is None:
            data_types = [
                "profile",
                "holdings",
                "performance",
                "dividends",
                "risk_metrics"
            ]
        
        # Validate tickers
        if not tickers:
            raise ValueError("At least one ticker must be provided")
        
        if len(tickers) > 50:
            raise ValueError("Maximum 50 tickers per bulk refresh")
        
        # Initialize results
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        # Process each ticker
        for ticker in tickers:
            try:
                ticker_result = await self._refresh_ticker_data(
                    ticker=ticker,
                    data_types=data_types,
                    force_refresh=force_refresh
                )
                
                if ticker_result["status"] == "success":
                    results["success"].append(ticker_result)
                elif ticker_result["status"] == "skipped":
                    results["skipped"].append(ticker_result)
                else:
                    results["failed"].append(ticker_result)
            
            except Exception as e:
                logger.warning(
                    "Failed to refresh ticker",
                    extra={"ticker": ticker, "error": str(e)}
                )
                results["failed"].append({
                    "ticker": ticker,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Calculate statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Store refresh history
        refresh_record = {
            "timestamp": end_time,
            "ticker_count": len(tickers),
            "success_count": len(results["success"]),
            "failed_count": len(results["failed"]),
            "skipped_count": len(results["skipped"]),
            "duration_seconds": duration,
            "data_types": data_types
        }
        self._refresh_history.append(refresh_record)
        
        # Keep only last 100 refresh records
        if len(self._refresh_history) > 100:
            self._refresh_history = self._refresh_history[-100:]
        
        logger.info(
            "Bulk data refresh completed",
            extra={
                "success_count": len(results["success"]),
                "failed_count": len(results["failed"]),
                "duration_seconds": duration
            }
        )
        
        return {
            "summary": {
                "total_tickers": len(tickers),
                "successful": len(results["success"]),
                "failed": len(results["failed"]),
                "skipped": len(results["skipped"]),
                "duration_seconds": round(duration, 2),
                "tickers_per_second": round(len(tickers) / duration, 2) if duration > 0 else 0
            },
            "results": results,
            "data_types_refreshed": data_types,
            "force_refresh": force_refresh,
            "timestamp": end_time.isoformat()
        }
    
    async def _refresh_ticker_data(
        self,
        ticker: str,
        data_types: List[str],
        force_refresh: bool
    ) -> Dict[str, Any]:
        """Refresh data for a single ticker."""
        # Simulate data refresh (in production, would call actual data providers)
        ticker_upper = ticker.upper()
        
        # Check if refresh is needed (unless forced)
        if not force_refresh:
            last_refresh = self._get_last_refresh_time(ticker_upper)
            if last_refresh and (datetime.now() - last_refresh) < timedelta(hours=1):
                return {
                    "ticker": ticker_upper,
                    "status": "skipped",
                    "reason": "Data is recent (less than 1 hour old)",
                    "last_refresh": last_refresh.isoformat()
                }
        
        # Simulate refresh delay
        await asyncio.sleep(0.1)
        
        # Simulate successful refresh
        refreshed_data = {}
        for data_type in data_types:
            refreshed_data[data_type] = {
                "status": "refreshed",
                "timestamp": datetime.now().isoformat(),
                "records_updated": self._simulate_record_count(data_type)
            }
        
        return {
            "ticker": ticker_upper,
            "status": "success",
            "data_types": refreshed_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_last_refresh_time(self, ticker: str) -> Optional[datetime]:
        """Get last refresh time for ticker (simulated)."""
        # In production, would query database
        # For now, return None to allow refresh
        return None
    
    def _simulate_record_count(self, data_type: str) -> int:
        """Simulate number of records updated."""
        record_counts = {
            "profile": 1,
            "holdings": 50,
            "performance": 1,
            "dividends": 12,
            "risk_metrics": 1
        }
        return record_counts.get(data_type, 1)
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    async def manage_cache(
        self,
        operation: str,
        cache_types: Optional[List[str]] = None,
        max_age_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Manage cache operations for ETF data.
        
        Provides cache clearing, statistics, and optimization operations
        to improve system performance.
        
        Args:
            operation: Cache operation (clear, stats, optimize, evict_old)
            cache_types: Types of cache to manage (quotes, profiles, holdings, etc.)
            max_age_hours: Maximum age for cache entries (for evict_old operation)
        
        Returns:
            Operation results with cache statistics
        """
        logger.info(
            "Cache management operation",
            extra={
                "operation": operation,
                "cache_types": cache_types,
                "max_age_hours": max_age_hours
            }
        )
        
        # Default to all cache types if none specified
        if cache_types is None:
            cache_types = [
                "quotes",
                "profiles",
                "holdings",
                "performance",
                "dividends",
                "risk_metrics",
                "comparisons",
                "screening"
            ]
        
        # Validate operation
        valid_operations = ["clear", "stats", "optimize", "evict_old"]
        if operation not in valid_operations:
            raise ValueError(f"Invalid operation. Must be one of: {valid_operations}")
        
        # Execute operation
        if operation == "clear":
            result = await self._clear_cache(cache_types)
        elif operation == "stats":
            result = await self._get_cache_stats(cache_types)
        elif operation == "optimize":
            result = await self._optimize_cache(cache_types)
        elif operation == "evict_old":
            if max_age_hours is None:
                max_age_hours = 24  # Default 24 hours
            result = await self._evict_old_cache(cache_types, max_age_hours)
        
        logger.info(
            "Cache management completed",
            extra={
                "operation": operation,
                "affected_caches": len(cache_types)
            }
        )
        
        return {
            "operation": operation,
            "cache_types": cache_types,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _clear_cache(self, cache_types: List[str]) -> Dict[str, Any]:
        """Clear specified cache types."""
        cleared = {}
        
        for cache_type in cache_types:
            # Simulate cache clearing
            await asyncio.sleep(0.05)
            
            entries_cleared = self._simulate_cache_size(cache_type)
            cleared[cache_type] = {
                "entries_cleared": entries_cleared,
                "memory_freed_mb": round(entries_cleared * 0.001, 2)
            }
        
        total_cleared = sum(c["entries_cleared"] for c in cleared.values())
        total_memory_freed = sum(c["memory_freed_mb"] for c in cleared.values())
        
        return {
            "caches_cleared": cleared,
            "summary": {
                "total_entries_cleared": total_cleared,
                "total_memory_freed_mb": round(total_memory_freed, 2),
                "cache_types_cleared": len(cache_types)
            }
        }
    
    async def _get_cache_stats(self, cache_types: List[str]) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {}
        
        for cache_type in cache_types:
            entries = self._simulate_cache_size(cache_type)
            hit_rate = self._simulate_hit_rate(cache_type)
            
            stats[cache_type] = {
                "entries": entries,
                "size_mb": round(entries * 0.001, 2),
                "hit_rate_pct": hit_rate,
                "avg_age_hours": self._simulate_avg_age(cache_type),
                "oldest_entry_hours": self._simulate_oldest_entry(cache_type)
            }
        
        total_entries = sum(s["entries"] for s in stats.values())
        total_size = sum(s["size_mb"] for s in stats.values())
        avg_hit_rate = mean([s["hit_rate_pct"] for s in stats.values()]) if stats else 0
        
        return {
            "cache_stats": stats,
            "summary": {
                "total_entries": total_entries,
                "total_size_mb": round(total_size, 2),
                "avg_hit_rate_pct": round(avg_hit_rate, 2),
                "cache_types_monitored": len(cache_types)
            }
        }
    
    async def _optimize_cache(self, cache_types: List[str]) -> Dict[str, Any]:
        """Optimize cache performance."""
        optimized = {}
        
        for cache_type in cache_types:
            await asyncio.sleep(0.05)
            
            # Simulate optimization
            before_entries = self._simulate_cache_size(cache_type)
            after_entries = int(before_entries * 0.85)  # 15% reduction
            
            optimized[cache_type] = {
                "before_entries": before_entries,
                "after_entries": after_entries,
                "entries_removed": before_entries - after_entries,
                "compression_ratio": round(after_entries / before_entries, 2) if before_entries > 0 else 1.0
            }
        
        total_removed = sum(o["entries_removed"] for o in optimized.values())
        
        return {
            "optimization_results": optimized,
            "summary": {
                "total_entries_removed": total_removed,
                "avg_compression_ratio": round(
                    mean([o["compression_ratio"] for o in optimized.values()]) if optimized else 1.0,
                    2
                ),
                "cache_types_optimized": len(cache_types)
            }
        }
    
    async def _evict_old_cache(
        self,
        cache_types: List[str],
        max_age_hours: int
    ) -> Dict[str, Any]:
        """Evict cache entries older than specified age."""
        evicted = {}
        
        for cache_type in cache_types:
            await asyncio.sleep(0.05)
            
            total_entries = self._simulate_cache_size(cache_type)
            old_entries = int(total_entries * 0.3)  # Assume 30% are old
            
            evicted[cache_type] = {
                "total_entries": total_entries,
                "entries_evicted": old_entries,
                "entries_remaining": total_entries - old_entries
            }
        
        total_evicted = sum(e["entries_evicted"] for e in evicted.values())
        
        return {
            "eviction_results": evicted,
            "max_age_hours": max_age_hours,
            "summary": {
                "total_entries_evicted": total_evicted,
                "cache_types_processed": len(cache_types)
            }
        }
    
    def _simulate_cache_size(self, cache_type: str) -> int:
        """Simulate cache size for a cache type."""
        cache_sizes = {
            "quotes": 5000,
            "profiles": 2000,
            "holdings": 8000,
            "performance": 3000,
            "dividends": 1500,
            "risk_metrics": 2500,
            "comparisons": 1000,
            "screening": 500
        }
        return cache_sizes.get(cache_type, 1000)
    
    def _simulate_hit_rate(self, cache_type: str) -> float:
        """Simulate cache hit rate."""
        hit_rates = {
            "quotes": 92.5,
            "profiles": 88.3,
            "holdings": 85.7,
            "performance": 90.2,
            "dividends": 87.4,
            "risk_metrics": 89.1,
            "comparisons": 82.5,
            "screening": 78.9
        }
        return hit_rates.get(cache_type, 85.0)
    
    def _simulate_avg_age(self, cache_type: str) -> float:
        """Simulate average cache entry age in hours."""
        return round(12.5 + (hash(cache_type) % 10), 1)
    
    def _simulate_oldest_entry(self, cache_type: str) -> float:
        """Simulate oldest cache entry age in hours."""
        return round(48.0 + (hash(cache_type) % 20), 1)
    
    # =========================================================================
    # SYSTEM HEALTH MONITORING
    # =========================================================================
    
    async def get_system_health(
        self,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Monitors data freshness, API health, cache performance,
        and overall system metrics.
        
        Args:
            include_details: Include detailed metrics for each component
        
        Returns:
            System health report with status indicators
        """
        logger.info(
            "Generating system health report",
            extra={"include_details": include_details}
        )
        
        # Collect health metrics
        data_health = await self._check_data_health()
        api_health = await self._check_api_health()
        cache_health = await self._check_cache_health()
        database_health = await self._check_database_health()
        
        # Calculate overall health score (0-100)
        health_scores = [
            data_health["health_score"],
            api_health["health_score"],
            cache_health["health_score"],
            database_health["health_score"]
        ]
        overall_score = mean(health_scores)
        
        # Determine overall status
        if overall_score >= 90:
            overall_status = "healthy"
        elif overall_score >= 70:
            overall_status = "degraded"
        elif overall_score >= 50:
            overall_status = "warning"
        else:
            overall_status = "critical"
        
        # Collect issues
        all_issues = []
        all_issues.extend(data_health.get("issues", []))
        all_issues.extend(api_health.get("issues", []))
        all_issues.extend(cache_health.get("issues", []))
        all_issues.extend(database_health.get("issues", []))
        
        health_report = {
            "overall_status": overall_status,
            "overall_health_score": round(overall_score, 2),
            "timestamp": datetime.now().isoformat(),
            "components": {
                "data_layer": {
                    "status": data_health["status"],
                    "health_score": data_health["health_score"]
                },
                "api_layer": {
                    "status": api_health["status"],
                    "health_score": api_health["health_score"]
                },
                "cache_layer": {
                    "status": cache_health["status"],
                    "health_score": cache_health["health_score"]
                },
                "database": {
                    "status": database_health["status"],
                    "health_score": database_health["health_score"]
                }
            },
            "issues": all_issues,
            "recommendations": self._generate_recommendations(
                overall_score,
                all_issues
            )
        }
        
        # Add detailed metrics if requested
        if include_details:
            health_report["details"] = {
                "data_layer": data_health.get("details", {}),
                "api_layer": api_health.get("details", {}),
                "cache_layer": cache_health.get("details", {}),
                "database": database_health.get("details", {})
            }
        
        logger.info(
            "System health report generated",
            extra={
                "overall_status": overall_status,
                "health_score": overall_score,
                "issues_count": len(all_issues)
            }
        )
        
        return health_report
    
    async def _check_data_health(self) -> Dict[str, Any]:
        """Check data layer health."""
        # Simulate data freshness checks
        await asyncio.sleep(0.1)
        
        data_sources = {
            "etf_profiles": {"freshness_hours": 2.5, "completeness_pct": 98.5},
            "holdings_data": {"freshness_hours": 4.0, "completeness_pct": 95.2},
            "price_data": {"freshness_hours": 0.5, "completeness_pct": 99.8},
            "dividend_data": {"freshness_hours": 24.0, "completeness_pct": 92.1}
        }
        
        issues = []
        health_score = 100.0
        
        for source, metrics in data_sources.items():
            if metrics["freshness_hours"] > 24:
                issues.append(f"{source}: Data is stale ({metrics['freshness_hours']}h old)")
                health_score -= 10
            
            if metrics["completeness_pct"] < 90:
                issues.append(f"{source}: Low completeness ({metrics['completeness_pct']}%)")
                health_score -= 10
        
        status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "warning"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "details": data_sources
        }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API layer health."""
        await asyncio.sleep(0.1)
        
        api_metrics = {
            "response_time_ms": 145.3,
            "error_rate_pct": 0.8,
            "rate_limit_remaining_pct": 78.5,
            "active_requests": 12
        }
        
        issues = []
        health_score = 100.0
        
        if api_metrics["response_time_ms"] > 500:
            issues.append(f"High API response time ({api_metrics['response_time_ms']}ms)")
            health_score -= 15
        elif api_metrics["response_time_ms"] > 300:
            issues.append(f"Elevated API response time ({api_metrics['response_time_ms']}ms)")
            health_score -= 5
        
        if api_metrics["error_rate_pct"] > 5:
            issues.append(f"High API error rate ({api_metrics['error_rate_pct']}%)")
            health_score -= 20
        elif api_metrics["error_rate_pct"] > 2:
            issues.append(f"Elevated API error rate ({api_metrics['error_rate_pct']}%)")
            health_score -= 10
        
        if api_metrics["rate_limit_remaining_pct"] < 20:
            issues.append(f"Low rate limit remaining ({api_metrics['rate_limit_remaining_pct']}%)")
            health_score -= 10
        
        status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "warning"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "details": api_metrics
        }
    
    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache layer health."""
        await asyncio.sleep(0.1)
        
        cache_metrics = {
            "hit_rate_pct": 87.5,
            "memory_usage_mb": 245.8,
            "memory_limit_mb": 512.0,
            "eviction_rate_per_min": 3.2
        }
        
        cache_metrics["memory_usage_pct"] = round(
            (cache_metrics["memory_usage_mb"] / cache_metrics["memory_limit_mb"]) * 100,
            2
        )
        
        issues = []
        health_score = 100.0
        
        if cache_metrics["hit_rate_pct"] < 70:
            issues.append(f"Low cache hit rate ({cache_metrics['hit_rate_pct']}%)")
            health_score -= 15
        elif cache_metrics["hit_rate_pct"] < 80:
            issues.append(f"Suboptimal cache hit rate ({cache_metrics['hit_rate_pct']}%)")
            health_score -= 5
        
        if cache_metrics["memory_usage_pct"] > 90:
            issues.append(f"High cache memory usage ({cache_metrics['memory_usage_pct']}%)")
            health_score -= 20
        elif cache_metrics["memory_usage_pct"] > 80:
            issues.append(f"Elevated cache memory usage ({cache_metrics['memory_usage_pct']}%)")
            health_score -= 10
        
        if cache_metrics["eviction_rate_per_min"] > 10:
            issues.append(f"High cache eviction rate ({cache_metrics['eviction_rate_per_min']}/min)")
            health_score -= 10
        
        status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "warning"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "details": cache_metrics
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        await asyncio.sleep(0.1)
        
        db_metrics = {
            "connection_pool_usage_pct": 45.2,
            "query_time_avg_ms": 28.5,
            "active_connections": 8,
            "max_connections": 100,
            "storage_usage_gb": 12.8,
            "storage_limit_gb": 50.0
        }
        
        db_metrics["storage_usage_pct"] = round(
            (db_metrics["storage_usage_gb"] / db_metrics["storage_limit_gb"]) * 100,
            2
        )
        
        issues = []
        health_score = 100.0
        
        if db_metrics["connection_pool_usage_pct"] > 90:
            issues.append(f"High connection pool usage ({db_metrics['connection_pool_usage_pct']}%)")
            health_score -= 20
        elif db_metrics["connection_pool_usage_pct"] > 75:
            issues.append(f"Elevated connection pool usage ({db_metrics['connection_pool_usage_pct']}%)")
            health_score -= 10
        
        if db_metrics["query_time_avg_ms"] > 100:
            issues.append(f"Slow database queries ({db_metrics['query_time_avg_ms']}ms)")
            health_score -= 15
        elif db_metrics["query_time_avg_ms"] > 50:
            issues.append(f"Elevated query times ({db_metrics['query_time_avg_ms']}ms)")
            health_score -= 5
        
        if db_metrics["storage_usage_pct"] > 90:
            issues.append(f"High storage usage ({db_metrics['storage_usage_pct']}%)")
            health_score -= 20
        elif db_metrics["storage_usage_pct"] > 80:
            issues.append(f"Elevated storage usage ({db_metrics['storage_usage_pct']}%)")
            health_score -= 10
        
        status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "warning"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "details": db_metrics
        }
    
    def _generate_recommendations(
        self,
        overall_score: float,
        issues: List[str]
    ) -> List[str]:
        """Generate recommendations based on health score and issues."""
        recommendations = []
        
        if overall_score < 70:
            recommendations.append("System health is degraded - immediate attention required")
        
        if any("stale" in issue.lower() for issue in issues):
            recommendations.append("Run bulk data refresh to update stale data")
        
        if any("cache" in issue.lower() for issue in issues):
            recommendations.append("Optimize cache configuration or clear old entries")
        
        if any("high" in issue.lower() or "elevated" in issue.lower() for issue in issues):
            recommendations.append("Monitor resource usage and consider scaling resources")
        
        if any("error" in issue.lower() for issue in issues):
            recommendations.append("Investigate error logs and fix failing API calls")
        
        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")
        
        return recommendations


# Singleton instance
etf_data_service = ETFDataService()
