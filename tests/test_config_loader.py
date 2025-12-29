"""
Unit tests for ConfigLoader
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.config_loader import ConfigLoader, ConfigurationError, LearningModule


@pytest.fixture
def sample_config():
    """Create a sample configuration."""
    return {
        'modules': {
            'colors': {
                'display_name': 'Colors',
                'repeat_count': 3,
                'items': [
                    {'name': 'Red', 'color': [255, 0, 0]},
                    {'name': 'Blue', 'color': [0, 0, 255]}
                ]
            }
        },
        'settings': {
            'default_module': 'colors',
            'fullscreen': False,
            'window_width': 800,
            'window_height': 600
        }
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        return f.name


def test_config_loader_initialization(temp_config_file):
    """Test ConfigLoader initialization."""
    loader = ConfigLoader(temp_config_file)
    assert loader is not None
    assert len(loader.get_available_modules()) > 0


def test_get_module(temp_config_file):
    """Test getting a module."""
    loader = ConfigLoader(temp_config_file)
    module = loader.get_module('colors')
    assert module.name == 'colors'
    assert module.display_name == 'Colors'
    assert module.repeat_count == 3


def test_get_nonexistent_module(temp_config_file):
    """Test getting a module that doesn't exist."""
    loader = ConfigLoader(temp_config_file)
    with pytest.raises(ConfigurationError):
        loader.get_module('nonexistent')


def test_get_default_module(temp_config_file):
    """Test getting the default module."""
    loader = ConfigLoader(temp_config_file)
    module = loader.get_default_module()
    assert module.name == 'colors'


def test_learning_module_get_item():
    """Test LearningModule get_item method."""
    config = {
        'display_name': 'Test',
        'repeat_count': 2,
        'items': [
            {'name': 'Item1'},
            {'name': 'Item2'}
        ]
    }
    module = LearningModule('test', config)
    
    assert module.get_item(0)['name'] == 'Item1'
    assert module.get_item(1)['name'] == 'Item2'
    assert module.get_item(2)['name'] == 'Item1'  # Wraps around


def test_invalid_config_file():
    """Test loading an invalid config file."""
    with pytest.raises(ConfigurationError):
        ConfigLoader('nonexistent_file.yaml')

