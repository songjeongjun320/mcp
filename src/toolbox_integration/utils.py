"""
Utility functions and configuration management for Google MCP Toolbox integration.

This module provides configuration classes, logging setup, and various utility functions
to support the toolbox integration functionality.
"""

import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
import yaml


@dataclass
class ToolboxConfig:
    """Configuration class for Toolbox integration."""
    
    # Service configuration
    default_url: str = "http://127.0.0.1:5000"
    timeout: int = 30
    max_retries: int = 3
    
    # Authentication configuration
    auth_type: Optional[str] = None
    google_project_id: Optional[str] = None
    google_region: str = "us-central1"
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Tool configuration
    default_toolset: Optional[str] = None
    bind_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced configuration
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    health_check_interval: int = 300  # 5 minutes
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'ToolboxConfig':
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
            
        Returns:
            ToolboxConfig instance
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                try:
                    import yaml
                    data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML configuration files")
            else:
                data = json.load(f)
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'ToolboxConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            ToolboxConfig instance
        """
        env_mapping = {
            'TOOLBOX_URL': 'default_url',
            'TOOLBOX_TIMEOUT': 'timeout',
            'TOOLBOX_MAX_RETRIES': 'max_retries',
            'TOOLBOX_AUTH_TYPE': 'auth_type',
            'GOOGLE_CLOUD_PROJECT': 'google_project_id',
            'GOOGLE_CLOUD_REGION': 'google_region',
            'TOOLBOX_LOG_LEVEL': 'log_level',
            'TOOLBOX_DEFAULT_TOOLSET': 'default_toolset',
            'TOOLBOX_ENABLE_CACHING': 'enable_caching',
            'TOOLBOX_CACHE_TTL': 'cache_ttl',
            'TOOLBOX_HEALTH_CHECK_INTERVAL': 'health_check_interval',
        }
        
        kwargs = {}
        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if attr_name in ['timeout', 'max_retries', 'cache_ttl', 'health_check_interval']:
                    kwargs[attr_name] = int(value)
                elif attr_name == 'enable_caching':
                    kwargs[attr_name] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    kwargs[attr_name] = value
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'default_url': self.default_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'auth_type': self.auth_type,
            'google_project_id': self.google_project_id,
            'google_region': self.google_region,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'default_toolset': self.default_toolset,
            'bind_parameters': self.bind_parameters,
            'enable_caching': self.enable_caching,
            'cache_ttl': self.cache_ttl,
            'health_check_interval': self.health_check_interval,
        }
    
    def save_to_file(self, config_path: Union[str, Path]):
        """
        Save configuration to a file.
        
        Args:
            config_path: Path to save configuration file
        """
        config_path = Path(config_path)
        data = self.to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                try:
                    import yaml
                    yaml.safe_dump(data, f, default_flow_style=False)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML configuration files")
            else:
                json.dump(data, f, indent=2)


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    handlers: Optional[List[logging.Handler]] = None
) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom log format string
        handlers: Custom log handlers
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    if handlers is None:
        # Default console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers = [console_handler]
    
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    root_logger.setLevel(log_level)
    
    # Set specific logger levels
    logging.getLogger('toolbox_integration').setLevel(log_level)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    current_file = Path(__file__)
    # Go up from src/toolbox_integration/utils.py to project root
    return current_file.parent.parent.parent


def load_config(config_path: Optional[Union[str, Path]] = None) -> ToolboxConfig:
    """
    Load configuration with fallback hierarchy.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ToolboxConfig instance
    """
    # Priority order:
    # 1. Explicitly provided config file
    # 2. Environment variables
    # 3. Default config file in project
    # 4. Default configuration
    
    if config_path:
        return ToolboxConfig.from_file(config_path)
    
    # Try to load from environment
    try:
        return ToolboxConfig.from_env()
    except Exception:
        pass
    
    # Try default config file
    project_root = get_project_root()
    default_config_paths = [
        project_root / "config" / "settings.py",
        project_root / "config" / "config.json",
        project_root / "config" / "config.yaml",
        project_root / "toolbox_config.json",
        project_root / "toolbox_config.yaml",
    ]
    
    for config_file in default_config_paths:
        if config_file.exists():
            try:
                return ToolboxConfig.from_file(config_file)
            except Exception:
                continue
    
    # Return default configuration
    return ToolboxConfig()


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error message with context.
    
    Args:
        error: Exception object
        context: Optional context string
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if context:
        return f"{context}: {error_type}: {error_message}"
    else:
        return f"{error_type}: {error_message}"


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            import asyncio
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise
                    
                    delay = backoff_factor * (2 ** attempt)
                    logging.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    await asyncio.sleep(delay)
        
        def sync_wrapper(*args, **kwargs):
            import time
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise
                    
                    delay = backoff_factor * (2 ** attempt)
                    logging.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def create_tool_signature(tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Create a string signature for a tool and its parameters.
    
    Args:
        tool_name: Name of the tool
        parameters: Tool parameters
        
    Returns:
        String signature
    """
    param_str = ", ".join([f"{k}={v}" for k, v in sorted(parameters.items())])
    return f"{tool_name}({param_str})"


def sanitize_log_data(data: Any) -> Any:
    """
    Sanitize data for logging by removing sensitive information.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['token', 'password', 'secret', 'key']):
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    else:
        return data


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'python_executable': sys.executable,
        'working_directory': os.getcwd(),
        'environment_variables': {
            k: v for k, v in os.environ.items() 
            if k.startswith('TOOLBOX_') or k.startswith('GOOGLE_')
        }
    } 