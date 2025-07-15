"""
Authentication examples for Google MCP Toolbox integration.

This example demonstrates how to use various authentication methods
including Google Cloud authentication, static tokens, and custom auth providers.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from toolbox_integration import ToolboxClientWrapper
from toolbox_integration.auth import (
    GoogleAuthProvider,
    StaticTokenProvider,
    EnvironmentTokenProvider,
    CustomTokenProvider,
    get_google_id_token,
    create_auth_provider,
)
from toolbox_integration.utils import setup_logging

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


async def google_cloud_auth_example():
    """
    Demonstrate Google Cloud authentication for Cloud Run or other GCP services.
    """
    print("=== Google Cloud Authentication Example ===")
    
    # Example for Cloud Run service
    cloud_run_url = "https://your-toolbox-service-abc123-uc.a.run.app"
    
    try:
        # Method 1: Using GoogleAuthProvider directly
        print("\n--- Method 1: Using GoogleAuthProvider ---")
        auth_provider = GoogleAuthProvider(target_audience=cloud_run_url)
        
        async with ToolboxClientWrapper(
            cloud_run_url,
            auth_provider=auth_provider
        ) as client:
            print(f"✓ Connected with Google Cloud authentication")
            
            # Test with a simple tool load
            try:
                tools = await client.load_toolset()
                print(f"✓ Loaded {len(tools)} tools")
            except Exception as e:
                print(f"✗ Failed to load tools: {e}")
        
        # Method 2: Using convenience function
        print("\n--- Method 2: Using convenience function ---")
        token_getter = lambda: get_google_id_token(cloud_run_url)
        
        async with ToolboxClientWrapper(
            cloud_run_url,
            client_headers={"Authorization": token_getter}
        ) as client:
            print(f"✓ Connected with convenience function")
            
            # Test health check
            is_healthy = await client.health_check()
            print(f"Health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        
        # Method 3: Using access token for API calls
        print("\n--- Method 3: Using access token ---")
        auth_provider = GoogleAuthProvider(scopes=[
            "https://www.googleapis.com/auth/cloud-platform"
        ])
        
        async with ToolboxClientWrapper(
            cloud_run_url,
            auth_provider=auth_provider
        ) as client:
            print(f"✓ Connected with access token")
            
    except Exception as e:
        print(f"✗ Google Cloud authentication failed: {e}")
        print("Note: Ensure you have proper Google Cloud credentials configured")
        print("Run: gcloud auth application-default login")


async def static_token_auth_example():
    """
    Demonstrate static token authentication for testing or simple scenarios.
    """
    print("\n=== Static Token Authentication Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        # Create static token provider
        static_token = "your-static-api-token"
        auth_provider = StaticTokenProvider(static_token)
        
        async with ToolboxClientWrapper(
            toolbox_url,
            auth_provider=auth_provider
        ) as client:
            print(f"✓ Connected with static token authentication")
            
            # Load tool with additional authentication
            try:
                auth_tool = await client.load_tool(
                    "authenticated_api",
                    auth_token_getters={"api_key": lambda: "additional-key"}
                )
                print(f"✓ Loaded authenticated tool")
                
                # Invoke the tool
                result = await auth_tool(data="test")
                print(f"Result: {result}")
                
            except Exception as e:
                print(f"✗ Tool operation failed: {e}")
                
    except Exception as e:
        print(f"✗ Static token authentication failed: {e}")


async def environment_token_auth_example():
    """
    Demonstrate environment variable token authentication.
    """
    print("\n=== Environment Token Authentication Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        # Set up environment variable for demo
        os.environ["TOOLBOX_AUTH_TOKEN"] = "Bearer demo-token-from-env"
        
        # Create environment token provider
        auth_provider = EnvironmentTokenProvider("TOOLBOX_AUTH_TOKEN")
        
        async with ToolboxClientWrapper(
            toolbox_url,
            auth_provider=auth_provider
        ) as client:
            print(f"✓ Connected with environment token authentication")
            
            # Test connection
            is_healthy = await client.health_check()
            print(f"Health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
            
    except Exception as e:
        print(f"✗ Environment token authentication failed: {e}")
    finally:
        # Clean up environment variable
        if "TOOLBOX_AUTH_TOKEN" in os.environ:
            del os.environ["TOOLBOX_AUTH_TOKEN"]


async def custom_token_auth_example():
    """
    Demonstrate custom token authentication with dynamic token generation.
    """
    print("\n=== Custom Token Authentication Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        # Custom token function that could fetch from cache, database, etc.
        async def custom_token_func():
            # Simulate token retrieval from external source
            print("  Fetching token from custom source...")
            await asyncio.sleep(0.1)  # Simulate async operation
            return "Bearer custom-dynamic-token"
        
        # Create custom token provider
        auth_provider = CustomTokenProvider(custom_token_func)
        
        async with ToolboxClientWrapper(
            toolbox_url,
            auth_provider=auth_provider
        ) as client:
            print(f"✓ Connected with custom token authentication")
            
            # Load tools with custom auth
            try:
                tools = await client.load_toolset()
                print(f"✓ Loaded {len(tools)} tools with custom auth")
                
            except Exception as e:
                print(f"✗ Failed to load tools: {e}")
                
    except Exception as e:
        print(f"✗ Custom token authentication failed: {e}")


async def multiple_auth_methods_example():
    """
    Demonstrate using multiple authentication methods for different tools.
    """
    print("\n=== Multiple Authentication Methods Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        # Primary authentication for client connection
        primary_auth = StaticTokenProvider("Bearer primary-token")
        
        async with ToolboxClientWrapper(
            toolbox_url,
            auth_provider=primary_auth
        ) as client:
            print(f"✓ Connected with primary authentication")
            
            # Tool with different authentication requirements
            print("\n--- Tool with Multiple Auth Requirements ---")
            try:
                # Define multiple auth token getters
                auth_token_getters = {
                    "google_auth": lambda: get_google_id_token("https://example.com"),
                    "api_key": lambda: "api-key-123",
                    "oauth_token": lambda: "oauth-token-456"
                }
                
                multi_auth_tool = await client.load_tool(
                    "multi_auth_api",
                    auth_token_getters=auth_token_getters
                )
                print(f"✓ Loaded tool with multiple auth methods")
                
                # Use the tool
                result = await multi_auth_tool(endpoint="/secure-data")
                print(f"Multi-auth result: {result}")
                
            except Exception as e:
                print(f"✗ Multi-auth tool failed: {e}")
                
    except Exception as e:
        print(f"✗ Multiple authentication methods failed: {e}")


async def auth_provider_factory_example():
    """
    Demonstrate using the auth provider factory for dynamic authentication.
    """
    print("\n=== Auth Provider Factory Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    # Test different auth types
    auth_configs = [
        {
            "type": "static",
            "token": "Bearer static-factory-token"
        },
        {
            "type": "env",
            "env_var_name": "DEMO_TOKEN"
        },
        {
            "type": "custom",
            "token_func": lambda: "Bearer custom-factory-token"
        }
    ]
    
    for config in auth_configs:
        try:
            auth_type = config.pop("type")
            auth_provider = create_auth_provider(auth_type, **config)
            
            # Set up environment variable for env auth test
            if auth_type == "env":
                os.environ["DEMO_TOKEN"] = "Bearer env-factory-token"
            
            async with ToolboxClientWrapper(
                toolbox_url,
                auth_provider=auth_provider
            ) as client:
                print(f"✓ Connected with {auth_type} auth provider from factory")
                
                # Test connection
                is_healthy = await client.health_check()
                print(f"  Health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
                
        except Exception as e:
            print(f"✗ {auth_type} auth provider failed: {e}")
        finally:
            # Clean up environment variable
            if "DEMO_TOKEN" in os.environ:
                del os.environ["DEMO_TOKEN"]


async def auth_error_handling_example():
    """
    Demonstrate authentication error handling and recovery.
    """
    print("\n=== Authentication Error Handling Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    # Test with invalid token
    print("\n--- Testing with Invalid Token ---")
    try:
        invalid_auth = StaticTokenProvider("Bearer invalid-token")
        
        async with ToolboxClientWrapper(
            toolbox_url,
            auth_provider=invalid_auth
        ) as client:
            print(f"✓ Connected (this might work depending on server configuration)")
            
            # This should potentially fail
            tools = await client.load_toolset()
            print(f"✓ Loaded {len(tools)} tools")
            
    except Exception as e:
        print(f"✗ Expected authentication error: {e}")
    
    # Test with expired token simulation
    print("\n--- Testing Token Refresh ---")
    try:
        class RefreshableTokenProvider:
            def __init__(self):
                self.token_count = 0
            
            async def get_token(self):
                self.token_count += 1
                if self.token_count == 1:
                    # Simulate expired token on first call
                    raise Exception("Token expired")
                return f"Bearer refreshed-token-{self.token_count}"
        
        # This would require retry logic in practice
        refreshable_auth = RefreshableTokenProvider()
        
        # Simulate token refresh
        try:
            await refreshable_auth.get_token()
        except Exception:
            print("✓ Caught token expiration, refreshing...")
            token = await refreshable_auth.get_token()
            print(f"✓ Got refreshed token: {token[:20]}...")
            
    except Exception as e:
        print(f"✗ Token refresh simulation failed: {e}")


async def main():
    """
    Main function that runs all authentication examples.
    """
    print("Google MCP Toolbox Integration - Authentication Examples")
    print("=" * 70)
    
    # Run authentication examples
    await google_cloud_auth_example()
    await static_token_auth_example()
    await environment_token_auth_example()
    await custom_token_auth_example()
    await multiple_auth_methods_example()
    await auth_provider_factory_example()
    await auth_error_handling_example()
    
    print("\n" + "=" * 70)
    print("Authentication examples completed!")
    print("\nNote: Some examples may fail if:")
    print("- The toolbox service is not running")
    print("- Google Cloud credentials are not configured")
    print("- The service doesn't require authentication")
    print("- Required environment variables are not set")


if __name__ == "__main__":
    asyncio.run(main()) 