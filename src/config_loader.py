"""
Configuration Loader
Handles loading and validation of YAML configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""
    pass


class LearningModule:
    """Represents a single learning module (e.g., colors, animals)."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.display_name = config.get('display_name', name.capitalize())
        self.repeat_count = config.get('repeat_count', 1)
        self.items = config.get('items', [])
        
        if not self.items:
            raise ConfigurationError(f"Module '{name}' has no items defined")
        
        if self.repeat_count < 1:
            raise ConfigurationError(f"Module '{name}' repeat_count must be >= 1")
    
    def get_item(self, index: int) -> Dict[str, Any]:
        """Get item by index (wraps around if index exceeds item count)."""
        if not self.items:
            raise ConfigurationError(f"Module '{self.name}' has no items")
        return self.items[index % len(self.items)]
    
    def get_item_count(self) -> int:
        """Get total number of items in this module."""
        return len(self.items)


class ConfigLoader:
    """Loads and manages application configuration."""
    
    def __init__(self, config_path: str):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._modules: Dict[str, LearningModule] = {}
        self._settings: Dict[str, Any] = {}
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load and parse configuration file."""
        if not self.config_path.exists():
            raise ConfigurationError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        
        if not self._config:
            raise ConfigurationError("Config file is empty")
        
        # Load modules
        modules_config = self._config.get('modules', {})
        if not modules_config:
            raise ConfigurationError("No modules defined in configuration")
        
        for module_name, module_config in modules_config.items():
            try:
                self._modules[module_name] = LearningModule(module_name, module_config)
            except Exception as e:
                raise ConfigurationError(f"Failed to load module '{module_name}': {e}")
        
        # Load settings
        self._settings = self._config.get('settings', {})
    
    def get_module(self, module_name: str) -> LearningModule:
        """
        Get a learning module by name.
        
        Args:
            module_name: Name of the module to retrieve
            
        Returns:
            LearningModule instance
            
        Raises:
            ConfigurationError: If module doesn't exist
        """
        if module_name not in self._modules:
            raise ConfigurationError(f"Module '{module_name}' not found")
        return self._modules[module_name]
    
    def get_default_module(self) -> LearningModule:
        """Get the default learning module."""
        default_name = self._settings.get('default_module')
        
        if not default_name:
            # Return first available module
            if self._modules:
                return next(iter(self._modules.values()))
            raise ConfigurationError("No modules available")
        
        return self.get_module(default_name)
    
    def get_available_modules(self) -> List[str]:
        """Get list of available module names."""
        return list(self._modules.keys())
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting."""
        return self._settings.get(key, default)
    
    def is_fullscreen(self) -> bool:
        """Check if fullscreen mode is enabled."""
        return self._settings.get('fullscreen', False)
    
    def get_window_size(self) -> tuple[int, int]:
        """Get window size (width, height)."""
        width = self._settings.get('window_width', 1024)
        height = self._settings.get('window_height', 768)
        return width, height
    
    def get_background_color(self) -> tuple[int, int, int]:
        """Get background color as RGB tuple."""
        color = self._settings.get('background_color', [245, 245, 245])
        return tuple(color)
    
    def get_text_color(self) -> tuple[int, int, int]:
        """Get text color as RGB tuple."""
        color = self._settings.get('text_color', [50, 50, 50])
        return tuple(color)
    
    def get_font_size(self) -> int:
        """Get font size for text display."""
        return self._settings.get('font_size', 72)

