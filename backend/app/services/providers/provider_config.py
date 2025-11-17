"""
Provider configuration models and utilities.

Supports:
- Environment variable configuration
- YAML/JSON file configuration
- Runtime configuration updates
- Tier-based defaults
"""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
import os
import json
import yaml

from .base_provider import DataType, ProviderCapability


class ProviderTier(str, Enum):
    """Provider subscription tier."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RateLimitConfig(BaseModel):
    """Rate limit configuration for a provider."""
    per_minute: Optional[int] = Field(
        None,
        description="Maximum requests per minute (None = unlimited)"
    )
    per_day: Optional[int] = Field(
        None,
        description="Maximum requests per day (None = unlimited)"
    )
    per_month: Optional[int] = Field(
        None,
        description="Maximum requests per month (None = unlimited)"
    )


class ProviderConfig(BaseModel):
    """
    Configuration for a data provider.
    
    Can be loaded from:
    - Environment variables ({PROVIDER}_KEY, {PROVIDER}_TIER, etc.)
    - YAML/JSON config files
    - Runtime updates via API
    
    Example YAML:
        providers:
          alpha_vantage:
            name: AlphaVantageProvider
            enabled: true
            priority: 2
            tier: premium
            api_key: ${ALPHA_VANTAGE_KEY}
            rate_limits:
              per_minute: 75
              per_day: 1500
            capabilities:
              REAL_TIME_QUOTE: EXCELLENT
              HISTORICAL_PRICES: EXCELLENT
            cost_per_call: 0.002
    
    Example Environment:
        ALPHA_VANTAGE_KEY=your_key_here
        ALPHA_VANTAGE_ENABLED=true
        ALPHA_VANTAGE_TIER=premium
        ALPHA_VANTAGE_PRIORITY=2
        ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE=75
        ALPHA_VANTAGE_RATE_LIMIT_PER_DAY=1500
    """
    
    name: str = Field(..., description="Provider class name (e.g., AlphaVantageProvider)")
    enabled: bool = Field(True, description="Whether provider is enabled")
    priority: int = Field(5, description="Provider priority (1=primary, 2=backup, etc.)")
    tier: ProviderTier = Field(ProviderTier.FREE, description="Subscription tier")
    
    api_key: Optional[str] = Field(None, description="API key (if required)")
    api_secret: Optional[str] = Field(None, description="API secret (if required)")
    
    rate_limits: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limit configuration"
    )
    
    capabilities: Dict[DataType, ProviderCapability] = Field(
        default_factory=dict,
        description="Provider capabilities by data type"
    )
    
    cost_per_call: float = Field(
        0.0,
        description="Average cost per API call (USD)"
    )
    
    timeout_seconds: int = Field(
        30,
        description="Request timeout in seconds"
    )
    
    max_retries: int = Field(
        3,
        description="Maximum number of retries for failed requests"
    )
    
    base_url: Optional[str] = Field(
        None,
        description="Custom base URL (if applicable)"
    )
    
    additional_config: Dict = Field(
        default_factory=dict,
        description="Provider-specific configuration"
    )
    
    class Config:
        use_enum_values = True


class ProviderConfigLoader:
    """
    Loads provider configurations from multiple sources.
    
    Priority order (highest to lowest):
    1. Environment variables
    2. Config file (YAML/JSON)
    3. Default values
    """
    
    @staticmethod
    def load_from_env(provider_prefix: str) -> Optional[ProviderConfig]:
        """
        Load provider config from environment variables.
        
        Args:
            provider_prefix: Provider prefix (e.g., ALPHA_VANTAGE, FINNHUB)
        
        Returns:
            ProviderConfig or None if not configured
        
        Environment variables:
            {PREFIX}_KEY: API key
            {PREFIX}_ENABLED: Enable/disable (default: true)
            {PREFIX}_PRIORITY: Priority (default: 5)
            {PREFIX}_TIER: Tier (free/basic/premium/enterprise)
            {PREFIX}_RATE_LIMIT_PER_MINUTE: Per-minute limit
            {PREFIX}_RATE_LIMIT_PER_DAY: Per-day limit
            {PREFIX}_RATE_LIMIT_PER_MONTH: Per-month limit
            {PREFIX}_COST_PER_CALL: Cost per API call (USD)
            {PREFIX}_TIMEOUT: Request timeout (seconds)
            {PREFIX}_MAX_RETRIES: Max retries
        """
        prefix = provider_prefix.upper()
        
        # Check if provider is configured
        api_key = os.getenv(f"{prefix}_KEY")
        
        # Special case: yfinance doesn't require API key
        if not api_key and provider_prefix.upper() != "YFINANCE":
            return None
        
        # Load configuration
        return ProviderConfig(
            name=f"{provider_prefix.title().replace('_', '')}Provider",
            enabled=os.getenv(f"{prefix}_ENABLED", "true").lower() == "true",
            priority=int(os.getenv(f"{prefix}_PRIORITY", "5")),
            tier=ProviderTier(os.getenv(f"{prefix}_TIER", "free")),
            api_key=api_key,
            api_secret=os.getenv(f"{prefix}_SECRET"),
            rate_limits=RateLimitConfig(
                per_minute=int(os.getenv(f"{prefix}_RATE_LIMIT_PER_MINUTE"))
                if os.getenv(f"{prefix}_RATE_LIMIT_PER_MINUTE") else None,
                per_day=int(os.getenv(f"{prefix}_RATE_LIMIT_PER_DAY"))
                if os.getenv(f"{prefix}_RATE_LIMIT_PER_DAY") else None,
                per_month=int(os.getenv(f"{prefix}_RATE_LIMIT_PER_MONTH"))
                if os.getenv(f"{prefix}_RATE_LIMIT_PER_MONTH") else None,
            ),
            cost_per_call=float(os.getenv(f"{prefix}_COST_PER_CALL", "0.0")),
            timeout_seconds=int(os.getenv(f"{prefix}_TIMEOUT", "30")),
            max_retries=int(os.getenv(f"{prefix}_MAX_RETRIES", "3")),
            base_url=os.getenv(f"{prefix}_BASE_URL"),
        )
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, ProviderConfig]:
        """
        Load provider configs from YAML or JSON file.
        
        Args:
            file_path: Path to config file (.yaml, .yml, or .json)
        
        Returns:
            Dictionary mapping provider name to config
        
        Example YAML structure:
            providers:
              alpha_vantage:
                name: AlphaVantageProvider
                enabled: true
                priority: 2
                tier: premium
                api_key: ${ALPHA_VANTAGE_KEY}
                rate_limits:
                  per_minute: 75
                  per_day: 1500
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        # Load file
        with open(file_path, 'r') as f:
            if file_path.endswith(('.yaml', '.yml')):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Parse providers
        providers = {}
        for provider_name, config_dict in data.get("providers", {}).items():
            # Expand environment variables
            config_dict = ProviderConfigLoader._expand_env_vars(config_dict)
            
            # Create config
            providers[provider_name] = ProviderConfig(**config_dict)
        
        return providers
    
    @staticmethod
    def _expand_env_vars(config: Dict) -> Dict:
        """
        Expand environment variables in config (${VAR_NAME} format).
        
        Example:
            api_key: ${ALPHA_VANTAGE_KEY}
            → api_key: actual_key_value
        """
        expanded = {}
        
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract env var name
                env_var = value[2:-1]
                expanded[key] = os.getenv(env_var, value)
            elif isinstance(value, dict):
                # Recursively expand nested dicts
                expanded[key] = ProviderConfigLoader._expand_env_vars(value)
            else:
                expanded[key] = value
        
        return expanded
    
    @staticmethod
    def get_default_config(provider_name: str) -> ProviderConfig:
        """
        Get default configuration for a provider.
        
        Args:
            provider_name: Provider name (alpha_vantage, finnhub, yfinance)
        
        Returns:
            Default ProviderConfig
        """
        defaults = {
            "alpha_vantage": ProviderConfig(
                name="AlphaVantageProvider",
                priority=2,
                tier=ProviderTier.FREE,
                rate_limits=RateLimitConfig(per_minute=5, per_day=500),
                cost_per_call=0.0,
            ),
            "finnhub": ProviderConfig(
                name="FinnhubProvider",
                priority=3,
                tier=ProviderTier.FREE,
                rate_limits=RateLimitConfig(per_minute=60),
                cost_per_call=0.0,
            ),
            "yfinance": ProviderConfig(
                name="YFinanceProvider",
                priority=1,
                tier=ProviderTier.FREE,
                rate_limits=RateLimitConfig(per_minute=2000),  # Very generous
                cost_per_call=0.0,
            ),
        }
        
        return defaults.get(provider_name.lower(), ProviderConfig(name=provider_name))


class ProviderConfigManager:
    """
    Manages provider configurations with live updates.
    
    Features:
    - Load configs from multiple sources
    - Runtime config updates
    - Config validation
    - Hot-reload support
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_file: Optional path to YAML/JSON config file
        """
        self.config_file = config_file
        self.configs: Dict[str, ProviderConfig] = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load configurations from all sources."""
        # Load from file if specified
        if self.config_file and os.path.exists(self.config_file):
            self.configs = ProviderConfigLoader.load_from_file(self.config_file)
        
        # Override with environment variables
        provider_prefixes = ["ALPHA_VANTAGE", "FINNHUB", "YFINANCE"]
        
        for prefix in provider_prefixes:
            env_config = ProviderConfigLoader.load_from_env(prefix)
            if env_config:
                self.configs[prefix.lower()] = env_config
    
    def get_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """
        Get configuration for a provider.
        
        Args:
            provider_name: Provider name (alpha_vantage, finnhub, yfinance)
        
        Returns:
            ProviderConfig or None if not configured
        """
        return self.configs.get(provider_name.lower())
    
    def update_config(self, provider_name: str, config: ProviderConfig):
        """
        Update configuration for a provider.
        
        Args:
            provider_name: Provider name
            config: New configuration
        """
        self.configs[provider_name.lower()] = config
    
    def reload_configs(self):
        """Reload configurations from all sources."""
        self._load_configs()
    
    def get_all_configs(self) -> Dict[str, ProviderConfig]:
        """Get all provider configurations."""
        return self.configs
    
    def save_to_file(self, file_path: str):
        """
        Save current configurations to file.
        
        Args:
            file_path: Path to save config (.yaml or .json)
        """
        data = {
            "providers": {
                name: config.dict(exclude_none=True)
                for name, config in self.configs.items()
            }
        }
        
        with open(file_path, 'w') as f:
            if file_path.endswith(('.yaml', '.yml')):
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)


# Global config manager instance
config_manager = ProviderConfigManager()
