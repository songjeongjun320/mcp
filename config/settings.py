"""
Configuration settings for Google MCP Toolbox integration.

This module contains default settings and configuration options for the toolbox integration.
Settings can be overridden through environment variables or configuration files.
"""

import os
from typing import Dict, Any, Optional, List

# =============================================================================
# Service Configuration
# =============================================================================

# Default toolbox service URL
DEFAULT_TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000")

# Connection timeout in seconds
TOOLBOX_TIMEOUT = int(os.getenv("TOOLBOX_TIMEOUT", "30"))

# Maximum number of retry attempts
TOOLBOX_MAX_RETRIES = int(os.getenv("TOOLBOX_MAX_RETRIES", "3"))

# Request timeout settings
REQUEST_TIMEOUT = {
    "total": TOOLBOX_TIMEOUT,
    "connect": 10,
    "read": 20,
}

# =============================================================================
# Authentication Configuration
# =============================================================================

# Authentication type (google, static, env, custom)
AUTH_TYPE = os.getenv("TOOLBOX_AUTH_TYPE", None)

# Google Cloud Project ID
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", None)

# Google Cloud Region
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Default OAuth scopes for Google authentication
DEFAULT_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
]

# =============================================================================
# Logging Configuration
# =============================================================================

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("TOOLBOX_LOG_LEVEL", "INFO")

# Log format
LOG_FORMAT = os.getenv(
    "TOOLBOX_LOG_FORMAT", 
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Enable file logging
ENABLE_FILE_LOGGING = os.getenv("TOOLBOX_ENABLE_FILE_LOGGING", "false").lower() == "true"

# Log file path
LOG_FILE_PATH = os.getenv("TOOLBOX_LOG_FILE_PATH", "logs/toolbox.log")

# Maximum log file size in bytes
MAX_LOG_FILE_SIZE = int(os.getenv("TOOLBOX_MAX_LOG_FILE_SIZE", "10485760"))  # 10MB

# Number of log files to keep
LOG_FILE_BACKUP_COUNT = int(os.getenv("TOOLBOX_LOG_FILE_BACKUP_COUNT", "5"))

# =============================================================================
# Tool Configuration
# =============================================================================

# Default toolset to load
DEFAULT_TOOLSET = os.getenv("TOOLBOX_DEFAULT_TOOLSET", None)

# Default parameters to bind to all tools
DEFAULT_BIND_PARAMETERS: Dict[str, Any] = {}

# Tool loading timeout in seconds
TOOL_LOADING_TIMEOUT = int(os.getenv("TOOLBOX_TOOL_LOADING_TIMEOUT", "30"))

# =============================================================================
# Caching Configuration
# =============================================================================

# Enable caching
ENABLE_CACHING = os.getenv("TOOLBOX_ENABLE_CACHING", "true").lower() == "true"

# Cache TTL in seconds
CACHE_TTL = int(os.getenv("TOOLBOX_CACHE_TTL", "3600"))  # 1 hour

# Cache backend (memory, redis, file)
CACHE_BACKEND = os.getenv("TOOLBOX_CACHE_BACKEND", "memory")

# Cache configuration
CACHE_CONFIG = {
    "memory": {
        "maxsize": 1000,
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD", None),
    },
    "file": {
        "cache_dir": os.getenv("TOOLBOX_CACHE_DIR", ".cache"),
        "max_size": int(os.getenv("TOOLBOX_CACHE_MAX_SIZE", "100")),  # MB
    }
}

# =============================================================================
# Health Check Configuration
# =============================================================================

# Health check interval in seconds
HEALTH_CHECK_INTERVAL = int(os.getenv("TOOLBOX_HEALTH_CHECK_INTERVAL", "300"))  # 5 minutes

# Enable automatic health checks
ENABLE_HEALTH_CHECKS = os.getenv("TOOLBOX_ENABLE_HEALTH_CHECKS", "true").lower() == "true"

# Health check timeout
HEALTH_CHECK_TIMEOUT = int(os.getenv("TOOLBOX_HEALTH_CHECK_TIMEOUT", "10"))

# =============================================================================
# Security Configuration
# =============================================================================

# Enable HTTPS verification
VERIFY_SSL = os.getenv("TOOLBOX_VERIFY_SSL", "true").lower() == "true"

# SSL certificate path (for custom certificates)
SSL_CERT_PATH = os.getenv("TOOLBOX_SSL_CERT_PATH", None)

# Enable request/response logging (be careful with sensitive data)
ENABLE_REQUEST_LOGGING = os.getenv("TOOLBOX_ENABLE_REQUEST_LOGGING", "false").lower() == "true"

# Sensitive headers to redact in logs
SENSITIVE_HEADERS = ["Authorization", "X-API-Key", "X-Auth-Token", "Cookie"]

# =============================================================================
# Development Configuration
# =============================================================================

# Enable development mode
DEV_MODE = os.getenv("TOOLBOX_DEV_MODE", "false").lower() == "true"

# Enable debug logging
DEBUG_MODE = os.getenv("TOOLBOX_DEBUG_MODE", "false").lower() == "true"

# Enable mock mode for testing
MOCK_MODE = os.getenv("TOOLBOX_MOCK_MODE", "false").lower() == "true"

# Development server URL
DEV_SERVER_URL = os.getenv("TOOLBOX_DEV_SERVER_URL", "http://localhost:5000")

# =============================================================================
# Performance Configuration
# =============================================================================

# Connection pool size
CONNECTION_POOL_SIZE = int(os.getenv("TOOLBOX_CONNECTION_POOL_SIZE", "10"))

# Maximum connections per host
MAX_CONNECTIONS_PER_HOST = int(os.getenv("TOOLBOX_MAX_CONNECTIONS_PER_HOST", "5"))

# Request rate limiting (requests per second)
RATE_LIMIT_RPS = int(os.getenv("TOOLBOX_RATE_LIMIT_RPS", "10"))

# Enable request compression
ENABLE_COMPRESSION = os.getenv("TOOLBOX_ENABLE_COMPRESSION", "true").lower() == "true"

# =============================================================================
# Integration Configuration
# =============================================================================

# LangChain integration settings
LANGCHAIN_CONFIG = {
    "enable_structured_tools": True,
    "parse_docstring": True,
    "include_raw_output": False,
}

# LangGraph integration settings
LANGGRAPH_CONFIG = {
    "enable_streaming": False,
    "checkpoint_enabled": False,
    "memory_enabled": True,
}

# =============================================================================
# Error Handling Configuration
# =============================================================================

# Enable detailed error messages
DETAILED_ERROR_MESSAGES = os.getenv("TOOLBOX_DETAILED_ERROR_MESSAGES", "true").lower() == "true"

# Error retry configuration
ERROR_RETRY_CONFIG = {
    "max_retries": TOOLBOX_MAX_RETRIES,
    "backoff_factor": 1.0,
    "retry_on_status": [429, 500, 502, 503, 504],
    "retry_on_exceptions": ["ConnectionError", "TimeoutError", "HTTPError"],
}

# =============================================================================
# Monitoring Configuration
# =============================================================================

# Enable metrics collection
ENABLE_METRICS = os.getenv("TOOLBOX_ENABLE_METRICS", "false").lower() == "true"

# Metrics backend (prometheus, statsd, console)
METRICS_BACKEND = os.getenv("TOOLBOX_METRICS_BACKEND", "console")

# Metrics configuration
METRICS_CONFIG = {
    "prometheus": {
        "port": int(os.getenv("PROMETHEUS_PORT", "8000")),
        "path": "/metrics",
    },
    "statsd": {
        "host": os.getenv("STATSD_HOST", "localhost"),
        "port": int(os.getenv("STATSD_PORT", "8125")),
        "prefix": "toolbox.",
    },
    "console": {
        "interval": 60,  # seconds
    }
}

# =============================================================================
# Environment-specific Configuration
# =============================================================================

def get_environment_config() -> Dict[str, Any]:
    """
    Get environment-specific configuration.
    
    Returns:
        Dictionary with environment-specific settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    configs = {
        "development": {
            "debug": True,
            "log_level": "DEBUG",
            "enable_caching": False,
            "verify_ssl": False,
            "toolbox_url": DEV_SERVER_URL,
        },
        "testing": {
            "debug": True,
            "log_level": "WARNING",
            "enable_caching": False,
            "verify_ssl": False,
            "mock_mode": True,
        },
        "staging": {
            "debug": False,
            "log_level": "INFO",
            "enable_caching": True,
            "verify_ssl": True,
        },
        "production": {
            "debug": False,
            "log_level": "WARNING",
            "enable_caching": True,
            "verify_ssl": True,
            "enable_metrics": True,
        }
    }
    
    return configs.get(environment, configs["development"])


# =============================================================================
# Validation Functions
# =============================================================================

def validate_config() -> List[str]:
    """
    Validate configuration settings.
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Validate URL
    if not DEFAULT_TOOLBOX_URL.startswith(("http://", "https://")):
        errors.append("DEFAULT_TOOLBOX_URL must start with http:// or https://")
    
    # Validate timeout values
    if TOOLBOX_TIMEOUT <= 0:
        errors.append("TOOLBOX_TIMEOUT must be positive")
    
    if TOOLBOX_MAX_RETRIES < 0:
        errors.append("TOOLBOX_MAX_RETRIES must be non-negative")
    
    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOG_LEVEL.upper() not in valid_log_levels:
        errors.append(f"LOG_LEVEL must be one of {valid_log_levels}")
    
    # Validate cache TTL
    if CACHE_TTL <= 0:
        errors.append("CACHE_TTL must be positive")
    
    # Validate health check interval
    if HEALTH_CHECK_INTERVAL <= 0:
        errors.append("HEALTH_CHECK_INTERVAL must be positive")
    
    return errors


# =============================================================================
# Configuration Summary
# =============================================================================

def get_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration.
    
    Returns:
        Dictionary with configuration summary
    """
    return {
        "service": {
            "url": DEFAULT_TOOLBOX_URL,
            "timeout": TOOLBOX_TIMEOUT,
            "max_retries": TOOLBOX_MAX_RETRIES,
        },
        "auth": {
            "type": AUTH_TYPE,
            "google_project": GOOGLE_CLOUD_PROJECT,
            "google_region": GOOGLE_CLOUD_REGION,
        },
        "logging": {
            "level": LOG_LEVEL,
            "file_logging": ENABLE_FILE_LOGGING,
            "file_path": LOG_FILE_PATH if ENABLE_FILE_LOGGING else None,
        },
        "caching": {
            "enabled": ENABLE_CACHING,
            "backend": CACHE_BACKEND,
            "ttl": CACHE_TTL,
        },
        "health_checks": {
            "enabled": ENABLE_HEALTH_CHECKS,
            "interval": HEALTH_CHECK_INTERVAL,
        },
        "security": {
            "verify_ssl": VERIFY_SSL,
            "request_logging": ENABLE_REQUEST_LOGGING,
        },
        "performance": {
            "connection_pool_size": CONNECTION_POOL_SIZE,
            "rate_limit_rps": RATE_LIMIT_RPS,
            "compression": ENABLE_COMPRESSION,
        },
        "monitoring": {
            "metrics_enabled": ENABLE_METRICS,
            "metrics_backend": METRICS_BACKEND,
        }
    } 