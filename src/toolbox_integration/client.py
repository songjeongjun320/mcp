"""
Enhanced ToolboxClient wrappers with additional functionality for authentication,
parameter binding, and error handling.
"""

import logging
from typing import Any, Dict, Optional, Callable, Union, List
import asyncio
import aiohttp
from contextlib import asynccontextmanager, contextmanager

try:
    from toolbox_core import ToolboxClient, ToolboxSyncClient
except ImportError:
    # Fallback for development/testing
    logging.warning("toolbox_core not installed. Using mock classes for development.")
    class ToolboxClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def load_tool(self, *args, **kwargs):
            pass
        async def load_toolset(self, *args, **kwargs):
            pass
        async def close(self):
            pass
    
    class ToolboxSyncClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def load_tool(self, *args, **kwargs):
            pass
        def load_toolset(self, *args, **kwargs):
            pass
        def close(self):
            pass

from .auth import AuthProvider, GoogleAuthProvider
from .utils import ToolboxConfig, setup_logging

logger = logging.getLogger(__name__)


class ToolboxClientWrapper:
    """
    Enhanced async wrapper for ToolboxClient with additional features:
    - Automatic authentication handling
    - Parameter binding
    - Error handling and retries
    - Logging and monitoring
    """
    
    def __init__(
        self,
        url: str,
        auth_provider: Optional[AuthProvider] = None,
        client_headers: Optional[Dict[str, Callable]] = None,
        session: Optional[aiohttp.ClientSession] = None,
        config: Optional[ToolboxConfig] = None,
        **kwargs
    ):
        self.url = url
        self.auth_provider = auth_provider
        self.config = config or ToolboxConfig()
        self.session = session
        self.client_headers = client_headers or {}
        self.kwargs = kwargs
        self._client: Optional[ToolboxClient] = None
        self._closed = False
        
        # Setup logging
        setup_logging(self.config.log_level)
        
        # Add authentication headers if auth_provider is provided
        if self.auth_provider and "Authorization" not in self.client_headers:
            self.client_headers["Authorization"] = self.auth_provider.get_token

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def connect(self):
        """Initialize the connection to the toolbox service."""
        if self._client is not None:
            return
            
        try:
            self._client = ToolboxClient(
                self.url,
                client_headers=self.client_headers,
                session=self.session,
                **self.kwargs
            )
            await self._client.__aenter__()
            logger.info(f"Connected to toolbox service at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to toolbox service: {e}")
            raise
            
    async def close(self):
        """Close the connection to the toolbox service."""
        if self._client and not self._closed:
            try:
                await self._client.__aexit__(None, None, None)
                self._closed = True
                logger.info("Closed connection to toolbox service")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
                
    async def load_tool(
        self,
        tool_name: str,
        auth_token_getters: Optional[Dict[str, Callable]] = None,
        bound_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Load a single tool with optional authentication and parameter binding.
        
        Args:
            tool_name: Name of the tool to load
            auth_token_getters: Authentication token getters for the tool
            bound_params: Parameters to bind to the tool
            **kwargs: Additional arguments to pass to the tool loader
            
        Returns:
            The loaded tool instance
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Use async with or call connect() first.")
            
        try:
            tool = await self._client.load_tool(
                tool_name,
                auth_token_getters=auth_token_getters,
                bound_params=bound_params,
                **kwargs
            )
            logger.info(f"Loaded tool: {tool_name}")
            return tool
        except Exception as e:
            logger.error(f"Failed to load tool {tool_name}: {e}")
            raise
            
    async def load_toolset(
        self,
        toolset_name: Optional[str] = None,
        auth_token_getters: Optional[Dict[str, Callable]] = None,
        bound_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Load a toolset with optional authentication and parameter binding.
        
        Args:
            toolset_name: Name of the toolset to load (None for all)
            auth_token_getters: Authentication token getters for the tools
            bound_params: Parameters to bind to the tools
            **kwargs: Additional arguments to pass to the toolset loader
            
        Returns:
            List of loaded tools
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Use async with or call connect() first.")
            
        try:
            tools = await self._client.load_toolset(
                toolset_name,
                auth_token_getters=auth_token_getters,
                bound_params=bound_params,
                **kwargs
            )
            logger.info(f"Loaded toolset: {toolset_name or 'all'}")
            return tools
        except Exception as e:
            logger.error(f"Failed to load toolset {toolset_name}: {e}")
            raise
            
    async def health_check(self) -> bool:
        """
        Check if the toolbox service is healthy.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            # Simple health check by attempting to load an empty toolset
            await self.load_toolset()
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False


class ToolboxSyncClientWrapper:
    """
    Enhanced sync wrapper for ToolboxSyncClient with additional features:
    - Automatic authentication handling
    - Parameter binding
    - Error handling
    - Logging and monitoring
    """
    
    def __init__(
        self,
        url: str,
        auth_provider: Optional[AuthProvider] = None,
        client_headers: Optional[Dict[str, Callable]] = None,
        config: Optional[ToolboxConfig] = None,
        **kwargs
    ):
        self.url = url
        self.auth_provider = auth_provider
        self.config = config or ToolboxConfig()
        self.client_headers = client_headers or {}
        self.kwargs = kwargs
        self._client: Optional[ToolboxSyncClient] = None
        self._closed = False
        
        # Setup logging
        setup_logging(self.config.log_level)
        
        # Add authentication headers if auth_provider is provided
        if self.auth_provider and "Authorization" not in self.client_headers:
            # For sync client, we need a sync version of the token getter
            def sync_token_getter():
                if hasattr(self.auth_provider.get_token, '__call__'):
                    token = self.auth_provider.get_token()
                    if asyncio.iscoroutine(token):
                        # If it's a coroutine, we need to run it in an event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            return loop.run_until_complete(token)
                        finally:
                            loop.close()
                    return token
                return None
            
            self.client_headers["Authorization"] = sync_token_getter

    def __enter__(self):
        """Sync context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        self.close()
        
    def connect(self):
        """Initialize the connection to the toolbox service."""
        if self._client is not None:
            return
            
        try:
            self._client = ToolboxSyncClient(
                self.url,
                client_headers=self.client_headers,
                **self.kwargs
            )
            self._client.__enter__()
            logger.info(f"Connected to toolbox service at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to toolbox service: {e}")
            raise
            
    def close(self):
        """Close the connection to the toolbox service."""
        if self._client and not self._closed:
            try:
                self._client.__exit__(None, None, None)
                self._closed = True
                logger.info("Closed connection to toolbox service")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
                
    def load_tool(
        self,
        tool_name: str,
        auth_token_getters: Optional[Dict[str, Callable]] = None,
        bound_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Load a single tool with optional authentication and parameter binding.
        
        Args:
            tool_name: Name of the tool to load
            auth_token_getters: Authentication token getters for the tool
            bound_params: Parameters to bind to the tool
            **kwargs: Additional arguments to pass to the tool loader
            
        Returns:
            The loaded tool instance
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Use with or call connect() first.")
            
        try:
            tool = self._client.load_tool(
                tool_name,
                auth_token_getters=auth_token_getters,
                bound_params=bound_params,
                **kwargs
            )
            logger.info(f"Loaded tool: {tool_name}")
            return tool
        except Exception as e:
            logger.error(f"Failed to load tool {tool_name}: {e}")
            raise
            
    def load_toolset(
        self,
        toolset_name: Optional[str] = None,
        auth_token_getters: Optional[Dict[str, Callable]] = None,
        bound_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Load a toolset with optional authentication and parameter binding.
        
        Args:
            toolset_name: Name of the toolset to load (None for all)
            auth_token_getters: Authentication token getters for the tools
            bound_params: Parameters to bind to the tools
            **kwargs: Additional arguments to pass to the toolset loader
            
        Returns:
            List of loaded tools
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Use with or call connect() first.")
            
        try:
            tools = self._client.load_toolset(
                toolset_name,
                auth_token_getters=auth_token_getters,
                bound_params=bound_params,
                **kwargs
            )
            logger.info(f"Loaded toolset: {toolset_name or 'all'}")
            return tools
        except Exception as e:
            logger.error(f"Failed to load toolset {toolset_name}: {e}")
            raise
            
    def health_check(self) -> bool:
        """
        Check if the toolbox service is healthy.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            # Simple health check by attempting to load an empty toolset
            self.load_toolset()
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False 