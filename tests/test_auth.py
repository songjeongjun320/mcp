"""
Tests for authentication providers and utilities.

This module contains tests for various authentication providers
and utility functions for token management.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any, Dict, Optional

from toolbox_integration.auth import (
    AuthProvider,
    StaticTokenProvider,
    EnvironmentTokenProvider,
    CustomTokenProvider,
    create_auth_provider,
    validate_token_format,
    extract_token_claims,
    is_token_expired,
)


class TestStaticTokenProvider:
    """Tests for StaticTokenProvider."""
    
    @pytest.mark.asyncio
    async def test_get_token_async(self):
        """Test async token retrieval."""
        provider = StaticTokenProvider("test-token")
        token = await provider.get_token()
        assert token == "test-token"
    
    def test_get_token_sync(self):
        """Test sync token retrieval."""
        provider = StaticTokenProvider("test-token")
        token = provider.get_token_sync()
        assert token == "test-token"


class TestEnvironmentTokenProvider:
    """Tests for EnvironmentTokenProvider."""
    
    @pytest.mark.asyncio
    async def test_get_token_success(self):
        """Test successful token retrieval from environment."""
        os.environ["TEST_TOKEN"] = "env-token"
        try:
            provider = EnvironmentTokenProvider("TEST_TOKEN")
            token = await provider.get_token()
            assert token == "env-token"
        finally:
            del os.environ["TEST_TOKEN"]
    
    @pytest.mark.asyncio
    async def test_get_token_missing_env_var(self):
        """Test error when environment variable is missing."""
        provider = EnvironmentTokenProvider("MISSING_TOKEN")
        with pytest.raises(ValueError, match="Environment variable MISSING_TOKEN not set"):
            await provider.get_token()


class TestCustomTokenProvider:
    """Tests for CustomTokenProvider."""
    
    @pytest.mark.asyncio
    async def test_get_token_sync_function(self):
        """Test with synchronous token function."""
        def sync_token_func():
            return "sync-token"
        
        provider = CustomTokenProvider(sync_token_func)
        token = await provider.get_token()
        assert token == "sync-token"
    
    @pytest.mark.asyncio
    async def test_get_token_async_function(self):
        """Test with asynchronous token function."""
        async def async_token_func():
            return "async-token"
        
        provider = CustomTokenProvider(async_token_func)
        token = await provider.get_token()
        assert token == "async-token"


class TestAuthProviderFactory:
    """Tests for create_auth_provider factory function."""
    
    def test_create_static_provider(self):
        """Test creating static token provider."""
        provider = create_auth_provider("static", token="test-token")
        assert isinstance(provider, StaticTokenProvider)
        assert provider.token == "test-token"
    
    def test_create_env_provider(self):
        """Test creating environment token provider."""
        provider = create_auth_provider("env", env_var_name="TEST_VAR")
        assert isinstance(provider, EnvironmentTokenProvider)
        assert provider.env_var_name == "TEST_VAR"
    
    def test_create_custom_provider(self):
        """Test creating custom token provider."""
        token_func = lambda: "custom-token"
        provider = create_auth_provider("custom", token_func=token_func)
        assert isinstance(provider, CustomTokenProvider)
        assert provider.token_func == token_func
    
    def test_create_unknown_provider(self):
        """Test error with unknown provider type."""
        with pytest.raises(ValueError, match="Unknown auth_type: unknown"):
            create_auth_provider("unknown")


class TestTokenUtilities:
    """Tests for token utility functions."""
    
    def test_validate_token_format_bearer(self):
        """Test validating Bearer token format."""
        assert validate_token_format("Bearer abc123") is True
        assert validate_token_format("Bearer ") is False
        assert validate_token_format("Bearer") is False
    
    def test_validate_token_format_jwt(self):
        """Test validating JWT token format."""
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert validate_token_format(jwt_token) is True
    
    def test_validate_token_format_invalid(self):
        """Test validating invalid token formats."""
        assert validate_token_format("") is False
        assert validate_token_format("invalid") is False
        assert validate_token_format("short") is False
    
    def test_extract_token_claims_valid_jwt(self):
        """Test extracting claims from valid JWT token."""
        # This is a test JWT token (header.payload.signature)
        # payload: {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        claims = extract_token_claims(jwt_token)
        assert claims["sub"] == "1234567890"
        assert claims["name"] == "John Doe"
        assert claims["iat"] == 1516239022
    
    def test_extract_token_claims_bearer_token(self):
        """Test extracting claims from Bearer token."""
        jwt_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        claims = extract_token_claims(jwt_token)
        assert claims["sub"] == "1234567890"
        assert claims["name"] == "John Doe"
    
    def test_extract_token_claims_invalid_token(self):
        """Test extracting claims from invalid token."""
        claims = extract_token_claims("invalid-token")
        assert claims == {}
    
    def test_is_token_expired_valid(self):
        """Test checking if token is expired."""
        # Create a token that expires in the future
        import time
        future_exp = int(time.time()) + 3600  # 1 hour from now
        
        # Mock JWT with exp claim
        with patch('toolbox_integration.auth.extract_token_claims') as mock_extract:
            mock_extract.return_value = {"exp": future_exp}
            
            assert is_token_expired("valid-token") is False
    
    def test_is_token_expired_expired(self):
        """Test checking if token is expired."""
        # Create a token that expired in the past
        import time
        past_exp = int(time.time()) - 3600  # 1 hour ago
        
        # Mock JWT with exp claim
        with patch('toolbox_integration.auth.extract_token_claims') as mock_extract:
            mock_extract.return_value = {"exp": past_exp}
            
            assert is_token_expired("expired-token") is True
    
    def test_is_token_expired_no_exp_claim(self):
        """Test checking token expiration without exp claim."""
        with patch('toolbox_integration.auth.extract_token_claims') as mock_extract:
            mock_extract.return_value = {}
            
            assert is_token_expired("no-exp-token") is False
    
    def test_is_token_expired_invalid_token(self):
        """Test checking expiration of invalid token."""
        with patch('toolbox_integration.auth.extract_token_claims') as mock_extract:
            mock_extract.side_effect = Exception("Invalid token")
            
            assert is_token_expired("invalid-token") is True


class TestGoogleAuthProvider:
    """Tests for GoogleAuthProvider (mocked)."""
    
    @pytest.mark.asyncio
    async def test_google_auth_not_available(self):
        """Test GoogleAuthProvider when Google Auth is not available."""
        with patch('toolbox_integration.auth.GOOGLE_AUTH_AVAILABLE', False):
            with pytest.raises(ImportError, match="Google Auth libraries not available"):
                from toolbox_integration.auth import GoogleAuthProvider
                GoogleAuthProvider()
    
    @pytest.mark.asyncio
    async def test_google_auth_with_target_audience(self):
        """Test GoogleAuthProvider with target audience."""
        with patch('toolbox_integration.auth.GOOGLE_AUTH_AVAILABLE', True):
            with patch('toolbox_integration.auth.default') as mock_default:
                with patch('toolbox_integration.auth.id_token') as mock_id_token:
                    mock_creds = Mock()
                    mock_default.return_value = (mock_creds, "test-project")
                    mock_id_token.fetch_id_token.return_value = "id-token"
                    
                    from toolbox_integration.auth import GoogleAuthProvider
                    provider = GoogleAuthProvider(target_audience="https://example.com")
                    
                    token = await provider.get_token()
                    assert token == "Bearer id-token"
    
    @pytest.mark.asyncio
    async def test_google_auth_with_scopes(self):
        """Test GoogleAuthProvider with custom scopes."""
        with patch('toolbox_integration.auth.GOOGLE_AUTH_AVAILABLE', True):
            with patch('toolbox_integration.auth.default') as mock_default:
                mock_creds = Mock()
                mock_creds.token = "access-token"
                mock_default.return_value = (mock_creds, "test-project")
                
                from toolbox_integration.auth import GoogleAuthProvider
                provider = GoogleAuthProvider(scopes=["custom-scope"])
                
                token = await provider.get_token()
                assert token == "Bearer access-token"
    
    @pytest.mark.asyncio
    async def test_google_auth_token_caching(self):
        """Test GoogleAuthProvider token caching."""
        with patch('toolbox_integration.auth.GOOGLE_AUTH_AVAILABLE', True):
            with patch('toolbox_integration.auth.default') as mock_default:
                mock_creds = Mock()
                mock_creds.token = "cached-token"
                mock_default.return_value = (mock_creds, "test-project")
                
                from toolbox_integration.auth import GoogleAuthProvider
                provider = GoogleAuthProvider()
                
                # First call should fetch token
                token1 = await provider.get_token()
                assert token1 == "Bearer cached-token"
                
                # Second call should return cached token
                token2 = await provider.get_token()
                assert token2 == "Bearer cached-token"
                
                # Should only call default once due to caching
                mock_default.assert_called_once()


class TestAuthIntegration:
    """Integration tests for authentication scenarios."""
    
    @pytest.mark.asyncio
    async def test_auth_provider_in_client_headers(self):
        """Test auth provider integration with client headers."""
        provider = StaticTokenProvider("Bearer integration-token")
        
        # Simulate how auth provider would be used in client headers
        token_getter = provider.get_token
        
        # Test that we can get the token
        token = await token_getter()
        assert token == "Bearer integration-token"
    
    @pytest.mark.asyncio
    async def test_multiple_auth_providers(self):
        """Test using multiple authentication providers."""
        providers = {
            "static": StaticTokenProvider("static-token"),
            "env": EnvironmentTokenProvider("TEST_ENV_TOKEN"),
            "custom": CustomTokenProvider(lambda: "custom-token")
        }
        
        # Set up environment for env provider
        os.environ["TEST_ENV_TOKEN"] = "env-token"
        
        try:
            # Test each provider
            tokens = {}
            for name, provider in providers.items():
                if name == "env":
                    tokens[name] = await provider.get_token()
                else:
                    tokens[name] = await provider.get_token()
            
            assert tokens["static"] == "static-token"
            assert tokens["env"] == "env-token"
            assert tokens["custom"] == "custom-token"
            
        finally:
            if "TEST_ENV_TOKEN" in os.environ:
                del os.environ["TEST_ENV_TOKEN"] 