import yaml
from pathlib import Path
from typing import List

class ConfigLoader:
    """Load and manage configuration from YAML files."""
    
    def __init__(self, config_path: str = "config/tickers.yaml"):
        self.config_path = Path(__file__).parent.parent / config_path
        self._config = None
    
    def load(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        return self._config
    
    def get_tickers(self) -> List[str]:
        """Get list of tickers from config."""
        if self._config is None:
            self.load()
        return self._config.get('tickers', [])
    
    def get_refresh_interval(self) -> int:
        """Get refresh interval in seconds."""
        if self._config is None:
            self.load()
        return self._config.get('refresh_interval', 300)

# Singleton instance
config_loader = ConfigLoader()
