"""Configuration management for AI Pitfall Detector."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration settings for the AI Pitfall Detector."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ai-pitfall-detector'
        self.config_file = self.config_dir / 'config.yaml'
        self.tools_file = self.config_dir / 'tools.yaml'
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            return self._create_default_config()
            
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default_config = {
            'api': {
                'provider': 'openai',  # or 'anthropic'
                'api_key': None,
                'model': 'gpt-3.5-turbo',
                'max_tokens': 2000
            },
            'github': {
                'token': None,  # Optional for higher rate limits
                'timeout': 30
            },
            'output': {
                'format': 'human',  # or 'json'
                'colors': True,
                'verbose': False
            }
        }
        
        self.config_dir.mkdir(exist_ok=True)
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        self._save_config(self._config)
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from config or environment variable."""
        api_key = self.get('api.api_key')
        if api_key:
            return api_key
            
        # Try environment variables
        provider = self.get('api.provider', 'openai')
        if provider == 'openai':
            return os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            return os.getenv('ANTHROPIC_API_KEY')
            
        return None
    
    def load_tools(self) -> Dict[str, Any]:
        """Load saved tools from file."""
        if not self.tools_file.exists():
            return {}
            
        try:
            with open(self.tools_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def save_tools(self, tools: Dict[str, Any]):
        """Save tools to file."""
        self.config_dir.mkdir(exist_ok=True)
        try:
            with open(self.tools_file, 'w') as f:
                yaml.dump(tools, f, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save tools: {e}")


# Global config instance
config = Config()