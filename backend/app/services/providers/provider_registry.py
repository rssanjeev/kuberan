"""
Provider registry for auto-discovery and management.

This module automatically discovers and registers data providers based on
environment configuration, supports hot-reload, and manages provider lifecycle.
"""

from typing import List, Dict, Optional, Type
import os

from app.core.logging_config import get_logger
from .base_provider import BaseProvider

logger = get_logger(__name__)


class ProviderRegistry:
    """
    Automatically discovers and registers data providers.
    
    Features:
    - Auto-detects API keys from environment
    - Dynamically loads provider implementations
    - Supports hot-reload without restart
    - Validates provider compatibility
    - Tier detection from configuration
    
    Environment Variables:
        ALPHA_VANTAGE_KEY: API key for Alpha Vantage
        ALPHA_VANTAGE_ENABLED: Enable/disable provider (default: true)
        ALPHA_VANTAGE_TIER: Tier level (free, premium, enterprise)
        ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE: Custom rate limit
        
        (Same pattern for other providers: FINNHUB_, POLYGON_, etc.)
    
    Example:
        registry = ProviderRegistry()
        providers = registry.discover_and_register_all()
        
        # Hot-reload after config change
        providers = registry.reload_all_providers()
    """
    
    # Mapping of env var prefixes to provider classes
    # Note: Provider classes will be imported lazily to avoid circular deps
    PROVIDER_MAP: Dict[str, str] = {
        "ALPHA_VANTAGE": "implementations.alpha_vantage_provider.AlphaVantageProvider",
        "FINNHUB": "implementations.finnhub_provider.FinnhubProvider",
        "YFINANCE": "implementations.yfinance_provider.YFinanceProvider",
        "MASSIVE": "implementations.massive_provider.MassiveProvider",
        # Easy to add new providers:
        # "POLYGON": "implementations.polygon_provider.PolygonProvider",
        # "IEX": "implementations.iex_provider.IEXCloudProvider",
    }
    
    def __init__(self):
        """Initialize provider registry."""
        self.registered_providers: List[BaseProvider] = []
        self.enabled_providers: Dict[str, bool] = {}
    
    def discover_and_register_all(self) -> List[BaseProvider]:
        """
        Discover all configured providers from environment.
        
        Looks for patterns like:
        - ALPHA_VANTAGE_KEY + ALPHA_VANTAGE_ENABLED
        - FINNHUB_KEY + FINNHUB_ENABLED
        - etc.
        
        Returns:
            List of initialized provider instances
        """
        discovered = []
        
        for prefix, provider_path in self.PROVIDER_MAP.items():
            # Check if provider is enabled
            enabled_key = f"{prefix}_ENABLED"
            is_enabled = os.getenv(enabled_key, "true").lower() == "true"
            
            if not is_enabled:
                logger.info(f"{prefix} provider disabled via config")
                self.enabled_providers[prefix] = False
                continue
            
            # Special case: yfinance doesn't need API key
            if prefix == "YFINANCE":
                try:
                    provider_class = self._load_provider_class(provider_path)
                    provider = provider_class()
                    discovered.append(provider)
                    self.enabled_providers[prefix] = True
                    
                    logger.info(f"✅ Registered {prefix} provider (no API key required)")
                except Exception as e:
                    logger.error(
                        f"Failed to initialize {prefix} provider",
                        extra={"error": str(e)},
                        exc_info=True
                    )
                continue
            
            # Check for API key
            key_var = f"{prefix}_KEY"
            api_key = os.getenv(key_var)
            
            if api_key:
                try:
                    # Load provider class dynamically
                    provider_class = self._load_provider_class(provider_path)
                    
                    # Initialize provider with API key
                    provider = provider_class(api_key)
                    
                    # Auto-detect or set tier
                    tier = self._detect_tier(prefix, provider)
                    if tier:
                        provider.tier = tier
                        logger.info(f"Detected {prefix} tier: {tier}")
                    
                    # Apply custom rate limits if configured
                    self._apply_custom_limits(prefix, provider)
                    
                    discovered.append(provider)
                    self.enabled_providers[prefix] = True
                    
                    logger.info(
                        f"✅ Registered {prefix} provider",
                        extra={"tier": tier}
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Failed to initialize {prefix} provider",
                        extra={"error": str(e)},
                        exc_info=True
                    )
                    self.enabled_providers[prefix] = False
            else:
                logger.warning(f"{prefix}_KEY not found, skipping {prefix} provider")
                self.enabled_providers[prefix] = False
        
        self.registered_providers = discovered
        
        logger.info(
            "Provider discovery complete",
            extra={
                "total_registered": len(discovered),
                "providers": [p.name for p in discovered]
            }
        )
        
        return discovered
    
    def _load_provider_class(self, provider_path: str) -> Type[BaseProvider]:
        """
        Dynamically load provider class.
        
        Args:
            provider_path: Module path (e.g., "alphavantage_provider.AlphaVantageProvider")
        
        Returns:
            Provider class
        """
        module_name, class_name = provider_path.rsplit(".", 1)
        full_module = f"app.services.providers.{module_name}"
        
        # Dynamic import
        import importlib
        module = importlib.import_module(full_module)
        provider_class = getattr(module, class_name)
        
        return provider_class
    
    def _detect_tier(self, prefix: str, provider: BaseProvider) -> Optional[str]:
        """
        Detect provider tier from environment or API response.
        
        Checks for:
        - Explicit tier config: ALPHA_VANTAGE_TIER=premium
        - Rate limit config: ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE=30
        - Auto-detection via test API call (future enhancement)
        
        Returns:
            "free", "basic", "premium", or "enterprise"
        """
        # Check explicit tier config
        tier_var = f"{prefix}_TIER"
        explicit_tier = os.getenv(tier_var)
        if explicit_tier:
            return explicit_tier.lower()
        
        # Check rate limit config (indicates tier)
        rate_limit_var = f"{prefix}_RATE_LIMIT_PER_MINUTE"
        rate_limit_str = os.getenv(rate_limit_var)
        
        if rate_limit_str:
            try:
                rate_limit = int(rate_limit_str)
                
                # Infer tier from rate limit
                if prefix == "ALPHA_VANTAGE":
                    if rate_limit >= 30:
                        return "premium"
                    elif rate_limit >= 5:
                        return "free"
                elif prefix == "FINNHUB":
                    if rate_limit >= 300:
                        return "premium"
                    elif rate_limit >= 60:
                        return "free"
            except ValueError:
                logger.warning(f"Invalid rate limit value: {rate_limit_str}")
        
        # Default to free tier
        return "free"
    
    def _apply_custom_limits(self, prefix: str, provider: BaseProvider):
        """
        Apply custom rate limits from environment configuration.
        
        Args:
            prefix: Provider prefix (e.g., "ALPHA_VANTAGE")
            provider: Provider instance to configure
        """
        if not provider.rate_limiter:
            return
        
        # Check for custom per-minute limit
        minute_var = f"{prefix}_RATE_LIMIT_PER_MINUTE"
        minute_str = os.getenv(minute_var)
        
        # Check for custom per-day limit
        day_var = f"{prefix}_RATE_LIMIT_PER_DAY"
        day_str = os.getenv(day_var)
        
        try:
            per_minute = int(minute_str) if minute_str else None
            per_day = int(day_str) if day_str else None
            
            if per_minute or per_day:
                provider.rate_limiter.update_limits(
                    per_minute=per_minute,
                    per_day=per_day
                )
                
                logger.info(
                    f"Applied custom limits for {prefix}",
                    extra={
                        "per_minute": per_minute,
                        "per_day": per_day
                    }
                )
        except (ValueError, AttributeError) as e:
            logger.warning(
                f"Failed to apply custom limits for {prefix}",
                extra={"error": str(e)}
            )
    
    def add_provider(self, provider: BaseProvider) -> bool:
        """
        Manually add a provider at runtime.
        
        Useful for:
        - Testing new providers
        - Hot-reloading providers
        - Dynamic provider injection
        
        Args:
            provider: Provider instance to add
        
        Returns:
            True if added successfully, False if already exists
        """
        if provider.name in [p.name for p in self.registered_providers]:
            logger.warning(f"Provider {provider.name} already registered")
            return False
        
        self.registered_providers.append(provider)
        
        # Re-sort by priority
        self.registered_providers.sort(key=lambda p: p.priority)
        
        logger.info(f"✅ Added provider {provider.name} at runtime")
        return True
    
    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove a provider at runtime.
        
        Useful for:
        - Disabling failing providers
        - Cost control
        - Testing
        
        Args:
            provider_name: Name of provider to remove
        
        Returns:
            True if removed successfully
        """
        initial_count = len(self.registered_providers)
        
        self.registered_providers = [
            p for p in self.registered_providers
            if p.name != provider_name
        ]
        
        removed = len(self.registered_providers) < initial_count
        
        if removed:
            logger.info(f"❌ Removed provider {provider_name}")
        else:
            logger.warning(f"Provider {provider_name} not found for removal")
        
        return removed
    
    def reload_all_providers(self) -> List[BaseProvider]:
        """
        Reload all providers (pick up config changes).
        
        Useful when:
        - API keys are updated
        - Tier is upgraded
        - New providers are configured
        - Rate limits are changed
        
        Returns:
            New list of initialized providers
        """
        logger.info("Reloading all providers...")
        
        self.registered_providers.clear()
        self.enabled_providers.clear()
        
        return self.discover_and_register_all()
    
    def get_provider_by_name(self, name: str) -> Optional[BaseProvider]:
        """
        Get provider by name.
        
        Args:
            name: Provider name (e.g., "AlphaVantageProvider")
        
        Returns:
            Provider instance or None if not found
        """
        for provider in self.registered_providers:
            if provider.name == name:
                return provider
        return None


# Singleton instance
provider_registry = ProviderRegistry()
