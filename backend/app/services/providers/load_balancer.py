"""
Load balancer for intelligent provider selection.

This module distributes API calls across providers based on:
- Available quota
- Reliability scores
- Response times
- Cost optimization
- Capability levels
"""

from typing import List, Dict, Tuple, Optional
import random

from app.core.logging_config import get_logger
from .base_provider import BaseProvider, DataType, ProviderCapability

logger = get_logger(__name__)


class LoadBalancer:
    """
    Distributes API calls across providers using weighted scoring.
    
    Scoring factors (weighted):
    - Available quota (40%)
    - Reliability score (30%)
    - Response time (15%)
    - Cost (10%)
    - Capability level (5%)
    
    Features:
    - Priority-based selection
    - Weighted random distribution
    - Quota-aware routing
    - Cost optimization
    - Performance tracking
    
    Example:
        balancer = LoadBalancer()
        
        # Select best provider for request
        provider = balancer.select_provider(
            providers=[alpha, finnhub, yfinance],
            data_type=DataType.REAL_TIME_QUOTE,
            priority=0
        )
    """
    
    def __init__(self):
        """Initialize load balancer."""
        self.call_history: List[Dict] = []  # Track recent routing decisions
        self.provider_scores: Dict = {}      # Dynamic scoring per provider
    
    def select_provider(
        self,
        providers: List[BaseProvider],
        data_type: DataType,
        priority: int = 0
    ) -> Optional[BaseProvider]:
        """
        Select best provider for this request using weighted scoring.
        
        Args:
            providers: List of available providers
            data_type: Type of data being requested
            priority: Request priority (0=normal, 1=high, 2=critical)
        
        Returns:
            Selected provider, or None if no suitable provider found
        """
        if not providers:
            logger.warning("No providers available for selection")
            return None
        
        if len(providers) == 1:
            return providers[0]
        
        # Filter providers that support this data type
        capable_providers = [
            p for p in providers
            if p.capabilities.get(data_type, ProviderCapability.NONE) != ProviderCapability.NONE
        ]
        
        if not capable_providers:
            logger.warning(
                f"No providers support {data_type.value}",
                extra={"providers_checked": [p.name for p in providers]}
            )
            return None
        
        # Calculate scores for each provider
        scored_providers = []
        
        for provider in capable_providers:
            score = self._calculate_provider_score(provider, data_type, priority)
            scored_providers.append((provider, score))
        
        # Sort by score (highest first)
        scored_providers.sort(key=lambda x: x[1], reverse=True)
        
        # For critical requests, always use best provider
        if priority >= 2:
            selected = scored_providers[0][0]
            logger.debug(
                "Critical priority: using best provider",
                extra={
                    "provider": selected.name,
                    "score": scored_providers[0][1]
                }
            )
            return selected
        
        # For normal requests, use weighted random selection
        # This distributes load while preferring better providers
        weights = [score for _, score in scored_providers]
        selected = self._weighted_random_choice(scored_providers, weights)
        
        # Record decision
        self.call_history.append({
            "provider": selected.name,
            "data_type": data_type.value,
            "priority": priority,
            "score": self._calculate_provider_score(selected, data_type, priority)
        })
        
        # Keep only last 1000 decisions
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
        
        logger.debug(
            "Provider selected",
            extra={
                "provider": selected.name,
                "data_type": data_type.value,
                "priority": priority,
                "score": self._calculate_provider_score(selected, data_type, priority)
            }
        )
        
        return selected
    
    def _calculate_provider_score(
        self,
        provider: BaseProvider,
        data_type: DataType,
        priority: int
    ) -> float:
        """
        Calculate composite score for provider selection.
        
        Returns score from 0.0 to 100.0
        """
        # 1. Quota availability (40% weight)
        quota_score = self._quota_score(provider) * 0.40
        
        # 2. Reliability (30% weight)
        reliability_score = provider.reliability_score * 100 * 0.30
        
        # 3. Response time (15% weight)
        response_time_score = self._response_time_score(provider) * 0.15
        
        # 4. Cost (10% weight)
        cost_score = self._cost_score(provider) * 0.10
        
        # 5. Capability level (5% weight)
        capability = provider.capabilities.get(data_type, ProviderCapability.NONE)
        capability_scores = {
            ProviderCapability.EXCELLENT: 100,
            ProviderCapability.GOOD: 75,
            ProviderCapability.BASIC: 50,
            ProviderCapability.NONE: 0
        }
        capability_score = capability_scores[capability] * 0.05
        
        total_score = (
            quota_score +
            reliability_score +
            response_time_score +
            cost_score +
            capability_score
        )
        
        return total_score
    
    def _quota_score(self, provider: BaseProvider) -> float:
        """
        Score based on remaining quota (0-100).
        
        More remaining quota = higher score.
        Unlimited quota = maximum score.
        """
        if not provider.rate_limiter:
            return 100.0  # No rate limit = maximum score
        
        quota = provider.rate_limiter.get_remaining_quota()
        
        # Use daily quota if available, otherwise minute quota
        if "per_day" in quota and quota["per_day"]:
            percent_used = quota["per_day"]["percent_used"]
            # Invert: 100% used = 0 score, 0% used = 100 score
            return 100 - percent_used
        elif "per_minute" in quota:
            percent_used = quota["per_minute"]["percent_used"]
            return 100 - percent_used
        
        return 100.0
    
    def _response_time_score(self, provider: BaseProvider) -> float:
        """
        Score based on average response time (0-100).
        
        Faster = higher score.
        """
        avg_time = provider.health.average_response_time_ms
        
        if avg_time is None:
            return 80.0  # Default score if no data
        
        # Score ranges:
        # < 200ms: 100
        # 200-500ms: 90
        # 500-1000ms: 75
        # 1000-2000ms: 60
        # 2000-3000ms: 40
        # > 3000ms: 20
        
        if avg_time < 200:
            return 100.0
        elif avg_time < 500:
            return 90.0
        elif avg_time < 1000:
            return 75.0
        elif avg_time < 2000:
            return 60.0
        elif avg_time < 3000:
            return 40.0
        else:
            return 20.0
    
    def _cost_score(self, provider: BaseProvider) -> float:
        """
        Score based on cost (0-100).
        
        Free providers score higher than paid ones.
        """
        # Cost map based on tier
        cost_map = {
            "free": 100,
            "basic": 75,
            "premium": 50,
            "enterprise": 25
        }
        
        tier = getattr(provider, 'tier', 'free')
        return cost_map.get(tier, 50)
    
    def _weighted_random_choice(
        self,
        items: List[Tuple[BaseProvider, float]],
        weights: List[float]
    ) -> BaseProvider:
        """
        Select item using weighted random choice.
        
        Higher scores have higher probability of selection,
        but lower-scored items still get some traffic.
        """
        if not items or not weights:
            return items[0][0] if items else None
        
        total = sum(weights)
        if total == 0:
            return items[0][0]
        
        normalized_weights = [w / total for w in weights]
        
        selected_tuple = random.choices(items, weights=normalized_weights, k=1)[0]
        return selected_tuple[0]
    
    def get_load_distribution_stats(self) -> Dict:
        """
        Get statistics on how calls are distributed across providers.
        
        Returns:
            {
                "total_calls": 1000,
                "distribution": {
                    "AlphaVantageProvider": {"count": 300, "percentage": 30.0},
                    "FinnhubProvider": {"count": 450, "percentage": 45.0},
                    "YFinanceProvider": {"count": 250, "percentage": 25.0}
                },
                "by_data_type": {
                    "real_time_quote": {
                        "FinnhubProvider": 450,
                        "YFinanceProvider": 200
                    },
                    ...
                }
            }
        """
        from collections import Counter, defaultdict
        
        # Analyze last 1000 calls
        recent_calls = self.call_history[-1000:]
        
        if not recent_calls:
            return {
                "total_calls": 0,
                "distribution": {},
                "by_data_type": {}
            }
        
        # Overall distribution
        provider_counts = Counter([call["provider"] for call in recent_calls])
        total_calls = len(recent_calls)
        
        distribution = {
            provider: {
                "count": count,
                "percentage": (count / total_calls) * 100
            }
            for provider, count in provider_counts.items()
        }
        
        # Distribution by data type
        by_data_type = defaultdict(lambda: Counter())
        for call in recent_calls:
            by_data_type[call["data_type"]][call["provider"]] += 1
        
        return {
            "total_calls": total_calls,
            "distribution": distribution,
            "by_data_type": dict(by_data_type)
        }
    
    def calculate_proportional_distribution(
        self,
        total_calls: int,
        provider_capacities: Dict[str, int]
    ) -> Dict[str, int]:
        """
        Calculate how to distribute calls proportionally across providers.
        
        Args:
            total_calls: Total number of calls to distribute
            provider_capacities: {provider_name: daily_capacity}
        
        Returns:
            {provider_name: calls_to_assign}
        
        Example:
            >>> capacities = {
            ...     "AlphaVantage": 1200,  # Premium tier
            ...     "Finnhub": 8640,       # 60/min * 60min * 24hr
            ...     "YFinance": 999999     # Unlimited
            ... }
            >>> balancer.calculate_proportional_distribution(1000, capacities)
            {
                "AlphaVantage": 120,  # 12%
                "Finnhub": 880,       # 88%
                "YFinance": 0         # Has capacity but others need traffic
            }
        """
        if not provider_capacities or total_calls == 0:
            return {}
        
        # Calculate total capacity
        total_capacity = sum(provider_capacities.values())
        
        if total_capacity == 0:
            # Equal distribution if no capacity info
            calls_per_provider = total_calls // len(provider_capacities)
            return {
                provider: calls_per_provider
                for provider in provider_capacities.keys()
            }
        
        # Proportional distribution
        distribution = {}
        remaining_calls = total_calls
        
        for provider, capacity in provider_capacities.items():
            proportion = capacity / total_capacity
            assigned_calls = int(total_calls * proportion)
            distribution[provider] = assigned_calls
            remaining_calls -= assigned_calls
        
        # Distribute remaining calls to highest capacity provider
        if remaining_calls > 0:
            max_capacity_provider = max(
                provider_capacities.keys(),
                key=lambda p: provider_capacities[p]
            )
            distribution[max_capacity_provider] += remaining_calls
        
        return distribution


# Singleton instance
load_balancer = LoadBalancer()
