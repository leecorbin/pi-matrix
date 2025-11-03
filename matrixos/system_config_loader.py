"""
MatrixOS System Configuration

Manages system-wide configuration set by installer/admin.
Separate from user settings which are managed in the Settings app.
"""

import os
import json
from pathlib import Path


_config_cache = None


def get_system_config_path():
    """Get path to system config file."""
    matrixos_dir = Path(__file__).parent
    return matrixos_dir / "system_config.json"


def load_system_config():
    """Load system configuration with defaults.
    
    Returns:
        dict: System configuration
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    # Default configuration
    default_config = {
        "version": "1.0",
        "system": {
            "emoji_download_enabled": True,
            "emoji_cache_dir": "~/.matrixos/emoji_cache"
        },
        "display": {
            "default_width": 128,
            "default_height": 128,
            "default_brightness": 80
        },
        "apps": {
            "auto_install_dependencies": False,
            "allow_background_apps": True
        }
    }
    
    config_path = get_system_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults (in case new keys added)
            config = default_config.copy()
            config.update(loaded_config)
            
            _config_cache = config
            return config
        except Exception as e:
            print(f"Warning: Could not load system config: {e}")
            print("Using defaults")
    
    _config_cache = default_config
    return default_config


def save_system_config(config):
    """Save system configuration.
    
    Args:
        config: Configuration dict to save
    """
    global _config_cache
    
    config_path = get_system_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        _config_cache = config
        return True
    except Exception as e:
        print(f"Error saving system config: {e}")
        return False


def get_setting(path, default=None):
    """Get a setting by dot-separated path.
    
    Args:
        path: Setting path like "system.emoji_download_enabled"
        default: Default value if not found
        
    Returns:
        Setting value or default
    """
    config = load_system_config()
    
    parts = path.split('.')
    value = config
    
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default
    
    return value


def set_setting(path, value):
    """Set a setting by dot-separated path.
    
    Args:
        path: Setting path like "system.emoji_download_enabled"
        value: Value to set
        
    Returns:
        True if successful
    """
    config = load_system_config()
    
    parts = path.split('.')
    current = config
    
    # Navigate to parent
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Set value
    current[parts[-1]] = value
    
    return save_system_config(config)


# Convenience functions
def is_emoji_download_enabled():
    """Check if on-demand emoji downloads are enabled."""
    return get_setting('system.emoji_download_enabled', True)


def set_emoji_download_enabled(enabled):
    """Enable or disable on-demand emoji downloads."""
    return set_setting('system.emoji_download_enabled', enabled)


def get_emoji_cache_dir():
    """Get emoji cache directory path."""
    cache_dir = get_setting('system.emoji_cache_dir', '~/.matrixos/emoji_cache')
    return Path(cache_dir).expanduser()


if __name__ == '__main__':
    # Test
    print("System Config Test")
    print("=" * 60)
    
    config = load_system_config()
    print(f"Emoji downloads enabled: {is_emoji_download_enabled()}")
    print(f"Emoji cache dir: {get_emoji_cache_dir()}")
    
    print("\nFull config:")
    print(json.dumps(config, indent=2))
