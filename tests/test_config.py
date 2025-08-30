"""Tests for configuration management."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from pitfall_detector.config import Config


class TestConfig:
    """Test the Config class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = Config()
        # Override config directory for testing
        self.config.config_dir = self.temp_dir
        self.config.config_file = self.temp_dir / 'config.yaml'
        self.config.tools_file = self.temp_dir / 'tools.yaml'
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test that default configuration is created."""
        config_data = self.config._create_default_config()
        
        assert 'api' in config_data
        assert 'github' in config_data
        assert 'output' in config_data
        assert config_data['api']['provider'] == 'openai'
    
    def test_get_set_config(self):
        """Test getting and setting configuration values."""
        # Test setting a value
        self.config.set('api.model', 'gpt-4')
        assert self.config.get('api.model') == 'gpt-4'
        
        # Test getting with default
        assert self.config.get('nonexistent.key', 'default') == 'default'
        
        # Test nested setting
        self.config.set('new.nested.value', 'test')
        assert self.config.get('new.nested.value') == 'test'
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-openai-key'})
    def test_get_api_key_from_env(self):
        """Test getting API key from environment variable."""
        self.config._config = {'api': {'provider': 'openai', 'api_key': None}}
        api_key = self.config.get_api_key()
        assert api_key == 'test-openai-key'
    
    def test_get_api_key_from_config(self):
        """Test getting API key from config."""
        self.config._config = {'api': {'provider': 'openai', 'api_key': 'config-key'}}
        api_key = self.config.get_api_key()
        assert api_key == 'config-key'
    
    def test_load_save_tools(self):
        """Test loading and saving tools."""
        test_tools = {
            'test_tool': {
                'name': 'test_tool',
                'url': 'https://github.com/user/repo',
                'description': 'A test tool'
            }
        }
        
        # Save tools
        self.config.save_tools(test_tools)
        
        # Load tools
        loaded_tools = self.config.load_tools()
        
        assert loaded_tools == test_tools
        assert 'test_tool' in loaded_tools
        assert loaded_tools['test_tool']['name'] == 'test_tool'
    
    def test_load_tools_empty(self):
        """Test loading tools when file doesn't exist."""
        tools = self.config.load_tools()
        assert tools == {}
    
    def test_config_persistence(self):
        """Test that configuration persists across instances."""
        # Set a value
        self.config.set('test.key', 'test_value')
        
        # Create new config instance with same directory
        new_config = Config()
        new_config.config_dir = self.temp_dir
        new_config.config_file = self.temp_dir / 'config.yaml'
        new_config._config = new_config._load_config()
        
        # Check that value persists
        assert new_config.get('test.key') == 'test_value'