import yaml
from pathlib import Path
from typing import List
from app.repositories.ticker_config_repository import ticker_config_repository


class ConfigLoader:
    """Load and manage configuration from YAML files and MongoDB."""
    
    def __init__(self, config_path: str = "config/tickers.yaml"):
        self.config_path = Path(__file__).parent.parent / config_path
        self._config = None
        self._use_mongodb = True  # Default to MongoDB
    
    def load(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        return self._config
    
    async def get_tickers_from_yaml(self) -> List[str]:
        """Get tickers from YAML file."""
        if self._config is None:
            try:
                self.load()
            except FileNotFoundError:
                return []
        return self._config.get('tickers', [])
    
    async def get_tickers(self) -> List[str]:
        """
        Get list of enabled tickers.
        Priority: MongoDB > YAML fallback
        """
        if self._use_mongodb:
            try:
                # Try to get from MongoDB
                tickers = await ticker_config_repository.get_all_enabled_tickers()
                
                # If MongoDB is empty, seed from YAML
                if not tickers:
                    yaml_tickers = await self.get_tickers_from_yaml()
                    if yaml_tickers:
                        count = await ticker_config_repository.seed_from_yaml(yaml_tickers)
                        print(f"✓ Seeded {count} tickers from YAML to MongoDB")
                        tickers = yaml_tickers
                
                return tickers
            except Exception as e:
                print(f"Warning: Could not load from MongoDB: {e}")
                # Fallback to YAML
                return await self.get_tickers_from_yaml()
        else:
            # Use YAML only
            return await self.get_tickers_from_yaml()
    
    def get_refresh_interval(self) -> int:
        """Get refresh interval in seconds."""
        if self._config is None:
            try:
                self.load()
            except FileNotFoundError:
                return 300  # Default
        return self._config.get('refresh_interval', 300)


# Singleton instance
config_loader = ConfigLoader()

