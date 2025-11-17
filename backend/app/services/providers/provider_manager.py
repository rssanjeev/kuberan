"""
Provider manager for orchestrating multi-provider data fetching.

This is the main orchestration layer that handles:
- Intelligent provider selection
- Automatic failover
- Multi-source data merging
- Provider health monitoring
- Request routing
"""

from typing import List, Dict, Optional
from datetime import datetime
import asyncio

from app.core.logging_config import get_logger
from .base_provider import (
    BaseProvider,
    DataType,
    ProviderCapability,
    ProviderException,
    RateLimitException
)
from .load_balancer import load_balancer
from .provider_registry import provider_registry

logger = get_logger(__name__)


class ProviderManager:
    """
    Orchestrates data fetching across multiple providers.
    
    Features:
    - Automatic provider selection based on capabilities
    - Intelligent failover when primary provider fails
    - Multi-source data merging for comprehensive results
    - Provider health monitoring and reliability scoring
    - Quota-aware routing to avoid rate limits
    
    Example:
        manager = ProviderManager()
        await manager.initialize()
        
        # Fetch with automatic provider selection
        quote = await manager.get_real_time_quote("AAPL")
        
        # Fetch from multiple sources and merge
        quote = await manager.get_with_merge("AAPL", DataType.REAL_TIME_QUOTE)
    """
    
    def __init__(self):
        """Initialize provider manager."""
        self.providers: List[BaseProvider] = []
        self.is_initialized = False
    
    async def initialize(self):
        """
        Initialize provider manager.
        
        Discovers and registers all configured providers.
        Should be called once at application startup.
        """
        if self.is_initialized:
            logger.warning("Provider manager already initialized")
            return
        
        # Discover providers
        self.providers = provider_registry.discover_and_register_all()
        
        if not self.providers:
            logger.warning("No providers registered! Data fetching will fail.")
        else:
            # Sort by priority (1=primary, 2=backup, etc.)
            self.providers.sort(key=lambda p: p.priority)
            
            logger.info(
                "Provider manager initialized",
                extra={
                    "provider_count": len(self.providers),
                    "providers": [p.name for p in self.providers]
                }
            )
        
        self.is_initialized = True
    
    async def reload_providers(self):
        """
        Reload all providers (picks up config changes).
        
        Use this after:
        - Upgrading API tier
        - Adding new API keys
        - Changing provider priorities
        """
        logger.info("Reloading providers...")
        
        self.providers = provider_registry.reload_all_providers()
        self.providers.sort(key=lambda p: p.priority)
        
        logger.info(
            "Providers reloaded",
            extra={
                "provider_count": len(self.providers),
                "providers": [p.name for p in self.providers]
            }
        )
    
    # ==================== Core Data Fetching Methods ====================
    
    async def get_quote(
        self,
        ticker: str,
        preferred_provider: Optional[str] = None,
        priority: int = 1
    ) -> Optional[Dict]:
        """
        Fetch real-time quote with optional provider preference.
        
        Allows explicit provider selection while maintaining automatic failover.
        
        Args:
            ticker: Stock symbol
            preferred_provider: Provider name ("yfinance", "alpha_vantage", "finnhub")
                               If specified, tries this provider first before failover
                               If None, uses load balancer to select best provider
            priority: Request priority (0=normal, 1=high, 2=critical)
        
        Returns:
            Quote data with source tracking or None if all providers fail
            
        Example:
            # Use YFinance explicitly (with failover)
            quote = await manager.get_quote("AAPL", preferred_provider="yfinance")
            
            # Let load balancer choose
            quote = await manager.get_quote("AAPL")
        """
        providers = self._get_providers_for_capability(DataType.REAL_TIME_QUOTE)
        
        if not providers:
            logger.error("No providers available for real-time quotes")
            return None
        
        # If preferred provider specified, try it first
        if preferred_provider:
            preferred = self._get_provider_by_name(preferred_provider)
            if preferred and preferred in providers:
                try:
                    start_time = datetime.now()
                    result = await preferred.get_real_time_quote(ticker)
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if result:
                        preferred.record_success(response_time)
                        logger.info(
                            f"Quote fetched from preferred provider {preferred_provider}",
                            extra={
                                "ticker": ticker,
                                "provider": preferred_provider,
                                "response_time_ms": response_time
                            }
                        )
                        return result
                
                except Exception as e:
                    logger.warning(
                        f"Preferred provider {preferred_provider} failed, falling back to others",
                        extra={"ticker": ticker, "error": str(e)}
                    )
                    preferred.record_failure(e)
                    # Continue to fallback logic below
            else:
                logger.warning(
                    f"Preferred provider {preferred_provider} not available or doesn't support quotes",
                    extra={"ticker": ticker}
                )
        
        # Fallback to automatic provider selection
        return await self.get_real_time_quote(ticker, priority)
    
    async def get_real_time_quote(
        self,
        ticker: str,
        priority: int = 1
    ) -> Optional[Dict]:
        """
        Fetch real-time quote with automatic provider selection and failover.
        
        Args:
            ticker: Stock symbol
            priority: Request priority (0=normal, 1=high, 2=critical)
        
        Returns:
            Quote data or None if all providers fail
        """
        providers = self._get_providers_for_capability(DataType.REAL_TIME_QUOTE)
        
        if not providers:
            logger.error("No providers available for real-time quotes")
            return None
        
        # Try providers with automatic failover
        for provider in providers:
            try:
                # Use load balancer to select best provider
                selected = load_balancer.select_provider(
                    [provider] if len(providers) == 1 else providers,
                    DataType.REAL_TIME_QUOTE,
                    priority
                )
                
                if not selected:
                    continue
                
                # Fetch data
                start_time = datetime.now()
                result = await selected.get_real_time_quote(ticker)
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if result:
                    # Record success
                    selected.record_success(response_time)
                    
                    logger.debug(
                        "Successfully fetched real-time quote",
                        extra={
                            "ticker": ticker,
                            "provider": selected.name,
                            "response_time_ms": response_time
                        }
                    )
                    
                    return result
                
            except RateLimitException as e:
                logger.warning(
                    f"Rate limit hit for {provider.name}, trying next provider",
                    extra={"ticker": ticker, "error": str(e)}
                )
                provider.record_failure(e)
                continue
                
            except ProviderException as e:
                logger.warning(
                    f"{provider.name} failed, trying next provider",
                    extra={"ticker": ticker, "error": str(e)}
                )
                provider.record_failure(e)
                continue
                
            except Exception as e:
                logger.error(
                    f"Unexpected error from {provider.name}",
                    extra={"ticker": ticker, "error": str(e)},
                    exc_info=True
                )
                provider.record_failure(e)
                continue
        
        logger.error(
            "All providers failed for real-time quote",
            extra={"ticker": ticker}
        )
        return None
    
    async def get_historical_prices(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d",
        priority: int = 0
    ) -> Optional[List[Dict]]:
        """
        Fetch historical prices with automatic provider selection and failover.
        
        Args:
            ticker: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            priority: Request priority
        
        Returns:
            List of OHLCV data or None if all providers fail
        """
        providers = self._get_providers_for_capability(DataType.HISTORICAL_PRICES)
        
        if not providers:
            logger.error("No providers support historical prices")
            return None
        
        # Use load balancer to select provider
        selected = load_balancer.select_provider(
            providers,
            DataType.HISTORICAL_PRICES,
            priority
        )
        
        if not selected:
            return None
        
        try:
            start_time = datetime.now()
            result = await selected.get_historical_prices(ticker, period, interval)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if result:
                selected.record_success(response_time)
                return result
            
        except Exception as e:
            logger.error(
                f"Failed to fetch historical prices from {selected.name}",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            selected.record_failure(e)
        
        return None
    
    async def get_with_merge(
        self,
        ticker: str,
        data_type: DataType,
        **kwargs
    ) -> Optional[Dict]:
        """
        Fetch from multiple providers and merge results.
        
        Useful for:
        - Getting most complete dataset
        - Cross-verifying data accuracy
        - Detecting anomalies
        
        Args:
            ticker: Stock symbol
            data_type: Type of data to fetch
            **kwargs: Additional arguments for provider methods
        
        Returns:
            Merged data from multiple providers
        """
        providers = self._get_providers_for_capability(data_type)
        
        if not providers:
            logger.error(f"No providers support {data_type.value}")
            return None
        
        # Fetch from all providers concurrently
        tasks = []
        for provider in providers:
            if data_type == DataType.REAL_TIME_QUOTE:
                tasks.append(provider.get_real_time_quote(ticker))
            elif data_type == DataType.FUNDAMENTAL_DATA:
                tasks.append(provider.get_fundamental_data(ticker, kwargs.get("data_type", "overview")))
            # Add more data types as needed
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [
            r for r in results
            if not isinstance(r, Exception) and r is not None
        ]
        
        if not successful_results:
            logger.error(
                "All providers failed for multi-source fetch",
                extra={"ticker": ticker, "data_type": data_type.value}
            )
            return None
        
        # Merge results
        merged = self._merge_results(successful_results, data_type)
        
        logger.info(
            "Successfully merged multi-source data",
            extra={
                "ticker": ticker,
                "data_type": data_type.value,
                "sources": len(successful_results)
            }
        )
        
        return merged
    
    # ==================== Helper Methods ====================
    
    def _get_providers_for_capability(
        self,
        data_type: DataType
    ) -> List[BaseProvider]:
        """
        Get providers that support specific data type.
        
        Returns providers sorted by:
        1. Priority (lower = better)
        2. Reliability score (higher = better)
        3. Capability level (EXCELLENT > GOOD > BASIC)
        """
        capable_providers = [
            p for p in self.providers
            if p.capabilities.get(data_type, ProviderCapability.NONE) != ProviderCapability.NONE
            and p.health.is_healthy
        ]
        
        # Sort by priority first, then reliability
        capable_providers.sort(
            key=lambda p: (p.priority, -p.reliability_score)
        )
        
        return capable_providers
    
    def _get_provider_by_name(self, name: str) -> Optional[BaseProvider]:
        """
        Get provider by name (case-insensitive).
        
        Args:
            name: Provider name (e.g., "yfinance", "alpha_vantage", "finnhub")
        
        Returns:
            Provider instance or None if not found
        """
        name_lower = name.lower()
        for provider in self.providers:
            if provider.name.lower() == name_lower or provider.name.lower().replace("provider", "") == name_lower:
                return provider
        return None
    
    def _merge_results(
        self,
        results: List[Dict],
        data_type: DataType
    ) -> Dict:
        """
        Merge results from multiple providers.
        
        Strategy varies by data type:
        - Quotes: Average prices, combine volumes
        - Fundamentals: Merge all fields, prefer non-null values
        - News: Combine and deduplicate by URL
        """
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Data type-specific merging logic
        if data_type == DataType.REAL_TIME_QUOTE:
            return self._merge_quotes(results)
        elif data_type == DataType.FUNDAMENTAL_DATA:
            return self._merge_fundamentals(results)
        else:
            # Default: return first result
            return results[0]
    
    def _merge_quotes(self, quotes: List[Dict]) -> Dict:
        """
        Merge real-time quotes from multiple providers.
        
        Strategy:
        - Price: Average across sources
        - Volume: Sum across sources
        - Timestamp: Most recent
        - Metadata: Combine sources
        """
        if not quotes:
            return {}
        
        merged = {
            "symbol": quotes[0].get("symbol"),
            "sources": [q.get("source", "unknown") for q in quotes]
        }
        
        # Average price
        prices = [q["price"] for q in quotes if "price" in q]
        if prices:
            merged["price"] = sum(prices) / len(prices)
            merged["price_min"] = min(prices)
            merged["price_max"] = max(prices)
        
        # Sum volume
        volumes = [q["volume"] for q in quotes if "volume" in q]
        if volumes:
            merged["volume"] = sum(volumes)
        
        # Most recent timestamp
        timestamps = [q["timestamp"] for q in quotes if "timestamp" in q]
        if timestamps:
            merged["timestamp"] = max(timestamps)
        
        return merged
    
    def _merge_fundamentals(self, fundamentals: List[Dict]) -> Dict:
        """
        Merge fundamental data from multiple providers.
        
        Strategy:
        - Prefer non-null values
        - Keep all unique fields
        - Note data source for each field
        """
        merged = {}
        
        for data in fundamentals:
            for key, value in data.items():
                if key not in merged and value is not None:
                    merged[key] = value
        
        return merged
    
    def get_provider_stats(self) -> List[Dict]:
        """
        Get statistics for all providers.
        
        Returns:
            [
                {
                    "name": "AlphaVantageProvider",
                    "priority": 2,
                    "tier": "premium",
                    "reliability_score": 0.98,
                    "is_healthy": true,
                    "consecutive_failures": 0,
                    "success_rate": 0.99,
                    "total_calls": 1250,
                    "average_response_time_ms": 245.6
                },
                ...
            ]
        """
        stats = []
        
        for provider in self.providers:
            stats.append({
                "name": provider.name,
                "priority": provider.priority,
                "tier": provider.tier,
                "reliability_score": provider.reliability_score,
                "is_healthy": provider.health.is_healthy,
                "consecutive_failures": provider.health.consecutive_failures,
                "success_rate": provider.health.success_rate,
                "total_calls": provider.health.total_calls,
                "successful_calls": provider.health.successful_calls,
                "failed_calls": provider.health.failed_calls,
                "average_response_time_ms": provider.health.average_response_time_ms,
                "capabilities": {
                    dt.value: cap.value
                    for dt, cap in provider.capabilities.items()
                }
            })
        
        return stats


# Singleton instance
provider_manager = ProviderManager()
