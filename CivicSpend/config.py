"""Configuration management for CivicSpend."""
import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Config:
    """Configuration manager."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self.load()
    
    def load(self, config_path: str = None):
        """Load configuration from YAML file."""
        if config_path is None:
            # Default to config/default.yaml
            root = Path(__file__).parent.parent.parent
            config_path = root / "config" / "default.yaml"
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    @property
    def db_path(self) -> str:
        """Get database path."""
        return self.get('database.path', 'data/civicspend.duckdb')
    
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.get('api.base_url')
    
    @property
    def api_rate_limit(self) -> int:
        """Get API rate limit."""
        return self.get('api.rate_limit', 5)
    
    @property
    def fuzzy_threshold(self) -> int:
        """Get fuzzy matching threshold."""
        return self.get('normalization.fuzzy_threshold', 85)
    
    @property
    def ml_contamination(self) -> float:
        """Get ML contamination parameter."""
        return self.get('ml.contamination', 0.05)
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get('logging.level', 'INFO')


# Singleton instance
config = Config()
