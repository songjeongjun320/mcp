"""
Authentication providers and utilities for Google MCP Toolbox integration.

This module provides various authentication mechanisms including Google Cloud authentication,
custom token providers, and utility functions for token management.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, Union
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import Google Auth libraries
try:
    from google.auth import default
    from google.auth.transport.requests import Request
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logger.warning("Google Auth libraries not available. Google authentication will not work.")


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def get_token(self) -> str:
        """Get authentication token asynchronously."""
        pass
    
    def get_token_sync(self) -> str:
        """Get authentication token synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_token())
        finally:
            loop.close()


class GoogleAuthProvider(AuthProvider):
    """Google Cloud authentication provider using default credentials."""
    
    def __init__(self, 
                 target_audience: Optional[str] = None,
                 scopes: Optional[list] = None,
                 project_id: Optional[str] = None):
        """
        Initialize Google authentication provider.
        
        Args:
            target_audience: Target audience for ID token (required for Cloud Run)
            scopes: OAuth scopes to request
            project_id: Google Cloud project ID
        """
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google Auth libraries not available. Install with: pip install google-auth")
        
        self.target_audience = target_audience
        self.scopes = scopes or ['https://www.googleapis.com/auth/cloud-platform']
        self.project_id = project_id
        self._cached_token = None
        self._token_expiry = None
        
    async def get_token(self) -> str:
        """Get Google ID token or access token."""
        try:
            # Check if we have a cached token that's still valid
            if self._cached_token and self._token_expiry:
                if datetime.now() < self._token_expiry:
                    return self._cached_token
            
            # Get credentials
            credentials, project = default(scopes=self.scopes)
            
            if self.target_audience:
                # For ID tokens (e.g., Cloud Run authentication)
                request = Request()
                credentials.refresh(request)
                
                # Create ID token for the target audience
                id_token_credentials = id_token.fetch_id_token(request, self.target_audience)
                token = id_token_credentials
            else:
                # For access tokens
                request = Request()
                credentials.refresh(request)
                token = credentials.token
            
            # Cache the token (assume 55 minutes validity for safety)
            self._cached_token = f"Bearer {token}"
            self._token_expiry = datetime.now() + timedelta(minutes=55)
            
            return self._cached_token
            
        except Exception as e:
            logger.error(f"Failed to get Google authentication token: {e}")
            raise


class StaticTokenProvider(AuthProvider):
    """Simple static token provider for testing or simple authentication."""
    
    def __init__(self, token: str):
        """
        Initialize with a static token.
        
        Args:
            token: Static authentication token
        """
        self.token = token
        
    async def get_token(self) -> str:
        """Return the static token."""
        return self.token


class EnvironmentTokenProvider(AuthProvider):
    """Token provider that reads from environment variables."""
    
    def __init__(self, env_var_name: str = "TOOLBOX_AUTH_TOKEN"):
        """
        Initialize with environment variable name.
        
        Args:
            env_var_name: Name of environment variable containing the token
        """
        self.env_var_name = env_var_name
        
    async def get_token(self) -> str:
        """Get token from environment variable."""
        token = os.getenv(self.env_var_name)
        if not token:
            raise ValueError(f"Environment variable {self.env_var_name} not set")
        return token


class CustomTokenProvider(AuthProvider):
    """Custom token provider that accepts a callable for token generation."""
    
    def __init__(self, token_func: Callable[[], Union[str, Any]]):
        """
        Initialize with a custom token function.
        
        Args:
            token_func: Function that returns an authentication token
        """
        self.token_func = token_func
        
    async def get_token(self) -> str:
        """Get token from custom function."""
        result = self.token_func()
        if asyncio.iscoroutine(result):
            result = await result
        return str(result)


# Convenience functions for common authentication scenarios

async def get_google_id_token(target_audience: str) -> str:
    """
    Get Google ID token for the specified target audience.
    
    Args:
        target_audience: Target audience (e.g., Cloud Run service URL)
        
    Returns:
        Bearer token string
    """
    provider = GoogleAuthProvider(target_audience=target_audience)
    return await provider.get_token()


def get_google_id_token_sync(target_audience: str) -> str:
    """
    Get Google ID token synchronously.
    
    Args:
        target_audience: Target audience (e.g., Cloud Run service URL)
        
    Returns:
        Bearer token string
    """
    provider = GoogleAuthProvider(target_audience=target_audience)
    return provider.get_token_sync()


async def get_google_access_token(scopes: Optional[list] = None) -> str:
    """
    Get Google access token for the specified scopes.
    
    Args:
        scopes: OAuth scopes to request
        
    Returns:
        Bearer token string
    """
    provider = GoogleAuthProvider(scopes=scopes)
    return await provider.get_token()


def create_auth_provider(
    auth_type: str,
    **kwargs
) -> AuthProvider:
    """
    Factory function to create authentication providers.
    
    Args:
        auth_type: Type of authentication ('google', 'static', 'env', 'custom')
        **kwargs: Additional arguments for the provider
        
    Returns:
        AuthProvider instance
    """
    if auth_type == 'google':
        return GoogleAuthProvider(**kwargs)
    elif auth_type == 'static':
        return StaticTokenProvider(**kwargs)
    elif auth_type == 'env':
        return EnvironmentTokenProvider(**kwargs)
    elif auth_type == 'custom':
        return CustomTokenProvider(**kwargs)
    else:
        raise ValueError(f"Unknown auth_type: {auth_type}")


# Utility functions for token management

def validate_token_format(token: str) -> bool:
    """
    Validate that token has proper format.
    
    Args:
        token: Token string to validate
        
    Returns:
        True if token format is valid
    """
    if not token:
        return False
    
    # Check if it's a Bearer token
    if token.startswith("Bearer "):
        return len(token) > 7
    
    # Check if it looks like a JWT token
    if token.count('.') == 2:
        return True
    
    # Basic length check
    return len(token) > 10


def extract_token_claims(token: str) -> Dict[str, Any]:
    """
    Extract claims from a JWT token (without verification).
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary of token claims
    """
    try:
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        # Split JWT token
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format")
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        import base64
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    
    except Exception as e:
        logger.error(f"Failed to extract token claims: {e}")
        return {}


def is_token_expired(token: str) -> bool:
    """
    Check if JWT token is expired.
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is expired
    """
    try:
        claims = extract_token_claims(token)
        if 'exp' in claims:
            exp_timestamp = claims['exp']
            return datetime.now().timestamp() > exp_timestamp
        return False
    except Exception:
        return True  # Assume expired if we can't parse 