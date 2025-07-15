"""
Tests for ToolboxClientWrapper and ToolboxSyncClientWrapper classes.

This module contains comprehensive tests for the client wrapper functionality
including connection management, tool loading, and error handling.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any, Dict, Optional

from toolbox_integration.client import ToolboxClientWrapper, ToolboxSyncClientWrapper
from toolbox_integration.auth import StaticTokenProvider, GoogleAuthProvider
from toolbox_integration.utils import ToolboxConfig


class TestToolboxClientWrapper:
    """Tests for the async ToolboxClientWrapper class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ToolboxConfig(
            default_url="http://test.example.com",
            timeout=10,
            max_retries=2,
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def auth_provider(self):
        """Create a mock auth provider."""
        return StaticTokenProvider("Bearer test-token")
    
    @pytest.fixture
    def mock_toolbox_client(self):
        """Create a mock ToolboxClient."""
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        return mock_client
    
    @pytest.mark.asyncio
    async def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        wrapper = ToolboxClientWrapper("http://test.example.com")
        
        assert wrapper.url == "http://test.example.com"
        assert wrapper.auth_provider is None
        assert wrapper.client_headers == {}
        assert wrapper.config is not None
        assert wrapper._client is None
        assert wrapper._closed is False
    
    @pytest.mark.asyncio
    async def test_init_with_auth_provider(self, auth_provider):
        """Test initialization with auth provider."""
        wrapper = ToolboxClientWrapper(
            "http://test.example.com",
            auth_provider=auth_provider
        )
        
        assert wrapper.auth_provider == auth_provider
        assert "Authorization" in wrapper.client_headers
    
    @pytest.mark.asyncio
    async def test_init_with_config(self, config):
        """Test initialization with custom config."""
        wrapper = ToolboxClientWrapper(
            "http://test.example.com",
            config=config
        )
        
        assert wrapper.config == config
        assert wrapper.url == "http://test.example.com"
    
    @pytest.mark.asyncio
    async def test_context_manager_connect_and_close(self, mock_toolbox_client):
        """Test context manager connect and close functionality."""
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                assert wrapper._client is not None
                assert not wrapper._closed
                mock_toolbox_client.__aenter__.assert_called_once()
            
            # After context exit
            assert wrapper._closed
            mock_toolbox_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_manual_connect_and_close(self, mock_toolbox_client):
        """Test manual connect and close functionality."""
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            await wrapper.connect()
            assert wrapper._client is not None
            assert not wrapper._closed
            mock_toolbox_client.__aenter__.assert_called_once()
            
            await wrapper.close()
            assert wrapper._closed
            mock_toolbox_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_already_connected(self, mock_toolbox_client):
        """Test that connect() doesn't reconnect if already connected."""
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            await wrapper.connect()
            client_instance = wrapper._client
            
            # Second connect should not create new client
            await wrapper.connect()
            assert wrapper._client is client_instance
            mock_toolbox_client.__aenter__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_tool_success(self, mock_toolbox_client):
        """Test successful tool loading."""
        mock_tool = AsyncMock()
        mock_tool.__name__ = "test_tool"
        mock_toolbox_client.load_tool = AsyncMock(return_value=mock_tool)
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                tool = await wrapper.load_tool("test_tool")
                
                assert tool == mock_tool
                mock_toolbox_client.load_tool.assert_called_once_with(
                    "test_tool",
                    auth_token_getters=None,
                    bound_params=None
                )
    
    @pytest.mark.asyncio
    async def test_load_tool_with_auth_and_params(self, mock_toolbox_client):
        """Test tool loading with authentication and bound parameters."""
        mock_tool = AsyncMock()
        mock_toolbox_client.load_tool = AsyncMock(return_value=mock_tool)
        
        auth_getters = {"api_key": lambda: "test-key"}
        bound_params = {"param1": "value1"}
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                tool = await wrapper.load_tool(
                    "test_tool",
                    auth_token_getters=auth_getters,
                    bound_params=bound_params
                )
                
                assert tool == mock_tool
                mock_toolbox_client.load_tool.assert_called_once_with(
                    "test_tool",
                    auth_token_getters=auth_getters,
                    bound_params=bound_params
                )
    
    @pytest.mark.asyncio
    async def test_load_tool_not_connected(self):
        """Test that load_tool raises error when not connected."""
        wrapper = ToolboxClientWrapper("http://test.example.com")
        
        with pytest.raises(RuntimeError, match="Client not connected"):
            await wrapper.load_tool("test_tool")
    
    @pytest.mark.asyncio
    async def test_load_tool_error_handling(self, mock_toolbox_client):
        """Test error handling in load_tool."""
        mock_toolbox_client.load_tool = AsyncMock(side_effect=Exception("Load error"))
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                with pytest.raises(Exception, match="Load error"):
                    await wrapper.load_tool("test_tool")
    
    @pytest.mark.asyncio
    async def test_load_toolset_success(self, mock_toolbox_client):
        """Test successful toolset loading."""
        mock_tools = [AsyncMock(), AsyncMock()]
        mock_toolbox_client.load_toolset = AsyncMock(return_value=mock_tools)
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                tools = await wrapper.load_toolset()
                
                assert tools == mock_tools
                mock_toolbox_client.load_toolset.assert_called_once_with(
                    None,
                    auth_token_getters=None,
                    bound_params=None
                )
    
    @pytest.mark.asyncio
    async def test_load_toolset_with_name(self, mock_toolbox_client):
        """Test toolset loading with specific name."""
        mock_tools = [AsyncMock()]
        mock_toolbox_client.load_toolset = AsyncMock(return_value=mock_tools)
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                tools = await wrapper.load_toolset("my-toolset")
                
                assert tools == mock_tools
                mock_toolbox_client.load_toolset.assert_called_once_with(
                    "my-toolset",
                    auth_token_getters=None,
                    bound_params=None
                )
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_toolbox_client):
        """Test successful health check."""
        mock_toolbox_client.load_toolset = AsyncMock(return_value=[])
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                is_healthy = await wrapper.health_check()
                
                assert is_healthy is True
                mock_toolbox_client.load_toolset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_toolbox_client):
        """Test health check failure."""
        mock_toolbox_client.load_toolset = AsyncMock(side_effect=Exception("Health check failed"))
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                is_healthy = await wrapper.health_check()
                
                assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_connect_error_handling(self):
        """Test error handling during connection."""
        with patch('toolbox_integration.client.ToolboxClient', side_effect=Exception("Connection error")):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            with pytest.raises(Exception, match="Connection error"):
                await wrapper.connect()
    
    @pytest.mark.asyncio
    async def test_close_error_handling(self, mock_toolbox_client):
        """Test error handling during close."""
        mock_toolbox_client.__aexit__ = AsyncMock(side_effect=Exception("Close error"))
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                pass  # Should not raise despite close error
            
            # Error should be logged but not raised
            assert wrapper._closed


class TestToolboxSyncClientWrapper:
    """Tests for the sync ToolboxSyncClientWrapper class."""
    
    @pytest.fixture
    def mock_sync_client(self):
        """Create a mock ToolboxSyncClient."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        return mock_client
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        wrapper = ToolboxSyncClientWrapper("http://test.example.com")
        
        assert wrapper.url == "http://test.example.com"
        assert wrapper.auth_provider is None
        assert wrapper.client_headers == {}
        assert wrapper.config is not None
        assert wrapper._client is None
        assert wrapper._closed is False
    
    def test_context_manager_connect_and_close(self, mock_sync_client):
        """Test context manager connect and close functionality."""
        with patch('toolbox_integration.client.ToolboxSyncClient', return_value=mock_sync_client):
            wrapper = ToolboxSyncClientWrapper("http://test.example.com")
            
            with wrapper:
                assert wrapper._client is not None
                assert not wrapper._closed
                mock_sync_client.__enter__.assert_called_once()
            
            # After context exit
            assert wrapper._closed
            mock_sync_client.__exit__.assert_called_once()
    
    def test_load_tool_success(self, mock_sync_client):
        """Test successful tool loading."""
        mock_tool = Mock()
        mock_tool.__name__ = "test_tool"
        mock_sync_client.load_tool = Mock(return_value=mock_tool)
        
        with patch('toolbox_integration.client.ToolboxSyncClient', return_value=mock_sync_client):
            wrapper = ToolboxSyncClientWrapper("http://test.example.com")
            
            with wrapper:
                tool = wrapper.load_tool("test_tool")
                
                assert tool == mock_tool
                mock_sync_client.load_tool.assert_called_once_with(
                    "test_tool",
                    auth_token_getters=None,
                    bound_params=None
                )
    
    def test_load_tool_not_connected(self):
        """Test that load_tool raises error when not connected."""
        wrapper = ToolboxSyncClientWrapper("http://test.example.com")
        
        with pytest.raises(RuntimeError, match="Client not connected"):
            wrapper.load_tool("test_tool")
    
    def test_load_toolset_success(self, mock_sync_client):
        """Test successful toolset loading."""
        mock_tools = [Mock(), Mock()]
        mock_sync_client.load_toolset = Mock(return_value=mock_tools)
        
        with patch('toolbox_integration.client.ToolboxSyncClient', return_value=mock_sync_client):
            wrapper = ToolboxSyncClientWrapper("http://test.example.com")
            
            with wrapper:
                tools = wrapper.load_toolset()
                
                assert tools == mock_tools
                mock_sync_client.load_toolset.assert_called_once_with(
                    None,
                    auth_token_getters=None,
                    bound_params=None
                )
    
    def test_health_check_success(self, mock_sync_client):
        """Test successful health check."""
        mock_sync_client.load_toolset = Mock(return_value=[])
        
        with patch('toolbox_integration.client.ToolboxSyncClient', return_value=mock_sync_client):
            wrapper = ToolboxSyncClientWrapper("http://test.example.com")
            
            with wrapper:
                is_healthy = wrapper.health_check()
                
                assert is_healthy is True
                mock_sync_client.load_toolset.assert_called_once()
    
    def test_health_check_failure(self, mock_sync_client):
        """Test health check failure."""
        mock_sync_client.load_toolset = Mock(side_effect=Exception("Health check failed"))
        
        with patch('toolbox_integration.client.ToolboxSyncClient', return_value=mock_sync_client):
            wrapper = ToolboxSyncClientWrapper("http://test.example.com")
            
            with wrapper:
                is_healthy = wrapper.health_check()
                
                assert is_healthy is False


class TestIntegrationScenarios:
    """Integration tests for various client scenarios."""
    
    @pytest.mark.asyncio
    async def test_client_with_google_auth(self):
        """Test client with Google authentication provider."""
        with patch('toolbox_integration.auth.GOOGLE_AUTH_AVAILABLE', True):
            with patch('toolbox_integration.auth.default') as mock_default:
                mock_creds = Mock()
                mock_default.return_value = (mock_creds, "test-project")
                
                auth_provider = GoogleAuthProvider(
                    target_audience="https://example.com"
                )
                
                wrapper = ToolboxClientWrapper(
                    "http://test.example.com",
                    auth_provider=auth_provider
                )
                
                assert wrapper.auth_provider == auth_provider
                assert "Authorization" in wrapper.client_headers
    
    @pytest.mark.asyncio
    async def test_client_with_custom_headers(self):
        """Test client with custom headers."""
        custom_headers = {
            "X-Custom-Header": lambda: "custom-value",
            "Authorization": lambda: "Bearer custom-token"
        }
        
        wrapper = ToolboxClientWrapper(
            "http://test.example.com",
            client_headers=custom_headers
        )
        
        assert wrapper.client_headers == custom_headers
    
    @pytest.mark.asyncio
    async def test_client_error_propagation(self, mock_toolbox_client):
        """Test that errors are properly propagated."""
        mock_toolbox_client.load_tool = AsyncMock(side_effect=ValueError("Invalid tool"))
        
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            async with wrapper:
                with pytest.raises(ValueError, match="Invalid tool"):
                    await wrapper.load_tool("invalid_tool")
    
    def test_sync_client_with_async_auth_provider(self):
        """Test sync client with async auth provider."""
        async def async_token_getter():
            return "Bearer async-token"
        
        auth_provider = Mock()
        auth_provider.get_token = async_token_getter
        
        wrapper = ToolboxSyncClientWrapper(
            "http://test.example.com",
            auth_provider=auth_provider
        )
        
        # Should have sync token getter
        assert "Authorization" in wrapper.client_headers
        token_getter = wrapper.client_headers["Authorization"]
        
        # This should work without raising (would run async function in sync context)
        assert callable(token_getter)
    
    @pytest.mark.asyncio
    async def test_client_resource_cleanup(self, mock_toolbox_client):
        """Test that resources are properly cleaned up."""
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            # Use context manager - should auto-cleanup
            async with wrapper:
                assert wrapper._client is not None
                assert not wrapper._closed
            
            # Should be cleaned up
            assert wrapper._closed
            mock_toolbox_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_double_close(self, mock_toolbox_client):
        """Test that double close is handled gracefully."""
        with patch('toolbox_integration.client.ToolboxClient', return_value=mock_toolbox_client):
            wrapper = ToolboxClientWrapper("http://test.example.com")
            
            await wrapper.connect()
            await wrapper.close()
            
            # Second close should not raise
            await wrapper.close()
            
            # Should only call __aexit__ once
            mock_toolbox_client.__aexit__.assert_called_once() 