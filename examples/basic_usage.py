"""
Basic usage examples for Google MCP Toolbox integration.

This example demonstrates how to use both async and sync toolbox clients
for basic tool loading and invocation.
"""

import asyncio
import logging
from typing import Any, Dict

from toolbox_integration import ToolboxClientWrapper, ToolboxSyncClientWrapper
from toolbox_integration.utils import setup_logging

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


async def async_basic_example():
    """
    Demonstrate basic async usage of the toolbox client.
    """
    print("=== Async Basic Example ===")
    
    # Initialize the toolbox client
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        async with ToolboxClientWrapper(toolbox_url) as client:
            print(f"Connected to toolbox service at {toolbox_url}")
            
            # Perform health check
            is_healthy = await client.health_check()
            print(f"Service health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
            
            if not is_healthy:
                print("Service is not healthy, skipping tool operations")
                return
            
            # Load a single tool
            print("\n--- Loading Single Tool ---")
            try:
                weather_tool = await client.load_tool("get_weather")
                print(f"✓ Loaded tool: get_weather")
                
                # Invoke the tool
                result = await weather_tool(location="Seoul")
                print(f"Weather result: {result}")
                
            except Exception as e:
                print(f"✗ Failed to load or invoke weather tool: {e}")
            
            # Load a toolset
            print("\n--- Loading Toolset ---")
            try:
                tools = await client.load_toolset()
                print(f"✓ Loaded {len(tools)} tools from default toolset")
                
                # List available tools
                for tool in tools:
                    print(f"  - {tool.__name__ if hasattr(tool, '__name__') else 'Unknown tool'}")
                
            except Exception as e:
                print(f"✗ Failed to load toolset: {e}")
            
            # Load specific toolset
            print("\n--- Loading Specific Toolset ---")
            try:
                specific_tools = await client.load_toolset("my-toolset")
                print(f"✓ Loaded {len(specific_tools)} tools from 'my-toolset'")
                
            except Exception as e:
                print(f"✗ Failed to load specific toolset: {e}")
    
    except Exception as e:
        print(f"✗ Failed to connect to toolbox service: {e}")
        logger.error(f"Connection error: {e}")


def sync_basic_example():
    """
    Demonstrate basic sync usage of the toolbox client.
    """
    print("\n=== Sync Basic Example ===")
    
    # Initialize the sync toolbox client
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        with ToolboxSyncClientWrapper(toolbox_url) as client:
            print(f"Connected to toolbox service at {toolbox_url}")
            
            # Perform health check
            is_healthy = client.health_check()
            print(f"Service health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
            
            if not is_healthy:
                print("Service is not healthy, skipping tool operations")
                return
            
            # Load a single tool
            print("\n--- Loading Single Tool ---")
            try:
                weather_tool = client.load_tool("get_weather")
                print(f"✓ Loaded tool: get_weather")
                
                # Invoke the tool
                result = weather_tool(location="Busan")
                print(f"Weather result: {result}")
                
            except Exception as e:
                print(f"✗ Failed to load or invoke weather tool: {e}")
            
            # Load a toolset
            print("\n--- Loading Toolset ---")
            try:
                tools = client.load_toolset()
                print(f"✓ Loaded {len(tools)} tools from default toolset")
                
                # List available tools
                for tool in tools:
                    print(f"  - {tool.__name__ if hasattr(tool, '__name__') else 'Unknown tool'}")
                
            except Exception as e:
                print(f"✗ Failed to load toolset: {e}")
    
    except Exception as e:
        print(f"✗ Failed to connect to toolbox service: {e}")
        logger.error(f"Connection error: {e}")


async def async_with_error_handling():
    """
    Demonstrate async usage with comprehensive error handling.
    """
    print("\n=== Async Error Handling Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        async with ToolboxClientWrapper(toolbox_url) as client:
            # Try to load a tool that might not exist
            try:
                nonexistent_tool = await client.load_tool("nonexistent_tool")
                result = await nonexistent_tool(param="value")
                print(f"Result: {result}")
            except Exception as e:
                print(f"Expected error loading nonexistent tool: {e}")
            
            # Try to invoke a tool with wrong parameters
            try:
                weather_tool = await client.load_tool("get_weather")
                result = await weather_tool(wrong_param="value")
                print(f"Result: {result}")
            except Exception as e:
                print(f"Expected error with wrong parameters: {e}")
    
    except Exception as e:
        print(f"Connection error: {e}")


async def async_with_tool_parameters():
    """
    Demonstrate async usage with various tool parameter scenarios.
    """
    print("\n=== Async Tool Parameters Example ===")
    
    toolbox_url = "http://127.0.0.1:5000"
    
    try:
        async with ToolboxClientWrapper(toolbox_url) as client:
            # Load tool with bound parameters
            print("\n--- Tool with Bound Parameters ---")
            try:
                bound_params = {"api_key": "demo-key", "timeout": 30}
                api_tool = await client.load_tool(
                    "api_call",
                    bound_params=bound_params
                )
                print(f"✓ Loaded tool with bound parameters: {list(bound_params.keys())}")
                
                # Invoke tool (bound parameters will be automatically applied)
                result = await api_tool(endpoint="/status")
                print(f"API result: {result}")
                
            except Exception as e:
                print(f"✗ Error with bound parameters: {e}")
            
            # Load tool with authentication
            print("\n--- Tool with Authentication ---")
            try:
                auth_token_getters = {
                    "my_auth": lambda: "demo-token"
                }
                auth_tool = await client.load_tool(
                    "authenticated_api",
                    auth_token_getters=auth_token_getters
                )
                print(f"✓ Loaded tool with authentication")
                
                result = await auth_tool(data="test")
                print(f"Authenticated result: {result}")
                
            except Exception as e:
                print(f"✗ Error with authentication: {e}")
    
    except Exception as e:
        print(f"Connection error: {e}")


def demonstrate_configuration():
    """
    Demonstrate various configuration options.
    """
    print("\n=== Configuration Example ===")
    
    from toolbox_integration.utils import ToolboxConfig
    
    # Create configuration from environment variables
    config = ToolboxConfig.from_env()
    print(f"Configuration from env: {config.to_dict()}")
    
    # Create custom configuration
    custom_config = ToolboxConfig(
        default_url="https://my-toolbox.example.com",
        timeout=60,
        max_retries=5,
        log_level="DEBUG"
    )
    
    print(f"Custom configuration: {custom_config.to_dict()}")


async def main():
    """
    Main function that runs all examples.
    """
    print("Google MCP Toolbox Integration - Basic Usage Examples")
    print("=" * 60)
    
    # Run async examples
    await async_basic_example()
    
    # Run sync examples
    sync_basic_example()
    
    # Run advanced examples
    await async_with_error_handling()
    await async_with_tool_parameters()
    
    # Demonstrate configuration
    demonstrate_configuration()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nNote: Some examples may fail if the toolbox service is not running")
    print("or if specific tools are not available in your toolbox configuration.")


if __name__ == "__main__":
    asyncio.run(main()) 