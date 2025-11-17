"""
Multi-provider data fetching infrastructure.

This package provides a provider-agnostic architecture for fetching
financial data from multiple sources (Alpha Vantage, Finnhub, yfinance, etc.).

Key Components:
- BaseProvider: Abstract interface all providers must implement
- ProviderManager: Orchestrates provider selection and failover
- AdaptiveRateLimiter: Auto-adjusts to API rate limits
- LoadBalancer: Distributes calls intelligently across providers
- ProviderRegistry: Auto-discovers and registers providers

Features:
- Automatic failover on provider failure
- Dynamic rate limit adaptation
- Intelligent load distribution
- Multi-source data merging
- Zero-code provider additions
"""

from .base_provider import (
    BaseProvider,
    DataType,
    ProviderCapability,
    ProviderHealth,
    ProviderException,
    RateLimitException
)
from .provider_manager import provider_manager
from .provider_registry import provider_registry
from .load_balancer import load_balancer
from .adaptive_rate_limiter import AdaptiveRateLimiter
from .provider_config import (
    ProviderConfig,
    ProviderTier,
    RateLimitConfig,
    ProviderConfigLoader,
    ProviderConfigManager,
    config_manager
)

__all__ = [
    # Base classes and enums
    'BaseProvider',
    'DataType',
    'ProviderCapability',
    'ProviderHealth',
    'ProviderException',
    'RateLimitException',
    
    # Core components (singletons)
    'provider_manager',
    'provider_registry',
    'load_balancer',
    
    # Rate limiting
    'AdaptiveRateLimiter',
    
    # Configuration
    'ProviderConfig',
    'ProviderTier',
    'RateLimitConfig',
    'ProviderConfigLoader',
    'ProviderConfigManager',
    'config_manager',
]
