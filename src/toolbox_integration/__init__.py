"""
Google MCP Toolbox Integration Package

This package provides a comprehensive integration for the Google MCP Toolbox Core SDK,
with enhanced features for authentication, parameter binding, and LangGraph integration.
"""

from .client import ToolboxClientWrapper, ToolboxSyncClientWrapper
from .auth import AuthProvider, GoogleAuthProvider, get_google_id_token
from .utils import ToolboxConfig, setup_logging

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "ToolboxClientWrapper",
    "ToolboxSyncClientWrapper", 
    "AuthProvider",
    "GoogleAuthProvider",
    "get_google_id_token",
    "ToolboxConfig",
    "setup_logging",
] 