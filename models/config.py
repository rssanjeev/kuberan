"""
Configuration management for investment projection tool.
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""

    def __init__(self, env_file: str = ".env"):
        """Initialize configuration by loading environment variables."""
        load_dotenv(env_file)
        self._strategies = self._load_strategies()
        self._quarters = int(os.getenv("QUARTERS", "12"))
        self._ticker = os.getenv("TICKER", "VXUS")

    def _load_strategies(self) -> List[Dict[str, Any]]:
        """Load investment strategies from environment variables."""
        strategies = []
        i = 1
        while True:
            strategy_key = f"STRATEGY_{i}"
            strategy_value = os.getenv(strategy_key)
            if not strategy_value:
                break

            # Parse strategy format: name:initial_amount:monthly_amount
            parts = strategy_value.split(':')
            if len(parts) == 3:
                name, initial, monthly = parts
                strategies.append({
                    "name": name,
                    "initial": int(initial),
                    "monthly": int(monthly)
                })
            i += 1

        return strategies

    @property
    def strategies(self) -> List[Dict[str, Any]]:
        """Get the list of investment strategies."""
        return self._strategies

    @property
    def quarters(self) -> int:
        """Get the number of quarters for projection."""
        return self._quarters

    @property
    def ticker(self) -> str:
        """Get the default ticker symbol."""
        return self._ticker