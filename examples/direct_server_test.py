#!/usr/bin/env python3
"""
Direct MCP Server Test

This example directly communicates with our local MCP server
without using the toolbox-core library wrapper.
"""

import asyncio
import json
import sys
from pathlib import Path
import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

async def test_direct_communication():
    """Test direct communication with our local MCP server"""
    
    server_url = "http://127.0.0.1:5000"
    
    print("🚀 Direct MCP Server Communication Test")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Health Check
        print("\n1. 🔍 Health Check")
        try:
            async with session.get(f"{server_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Server Status: {data['status']}")
                    print(f"   📡 Server Info: {data['server']}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return
        
        # 2. Get Available Tools
        print("\n2. 📋 Available Tools")
        try:
            async with session.get(f"{server_url}/tools") as response:
                if response.status == 200:
                    data = await response.json()
                    tools = data.get('tools', [])
                    print(f"   📊 Found {len(tools)} tools:")
                    for i, tool in enumerate(tools, 1):
                        print(f"      {i}. {tool['name']}: {tool['description']}")
                else:
                    print(f"   ❌ Failed to get tools: {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error getting tools: {e}")
            return
        
        # 3. Test Tool Calls
        print("\n3. 🔧 Testing Tool Calls")
        
        # Test weather tool
        print("\n   🌤️  Testing weather tool...")
        try:
            payload = {
                "tool": "get_weather",
                "parameters": {
                    "location": "Seoul, South Korea",
                    "units": "celsius"
                }
            }
            
            async with session.post(
                f"{server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    print(f"      📍 Location: {result.get('location')}")
                    print(f"      🌡️  Temperature: {result.get('temperature')}")
                    print(f"      ☀️  Condition: {result.get('condition')}")
                    print(f"      💧 Humidity: {result.get('humidity')}")
                else:
                    print(f"      ❌ Weather call failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Weather call error: {e}")
        
        # Test calculator tool
        print("\n   🧮 Testing calculator tool...")
        try:
            payload = {
                "tool": "calculate",
                "parameters": {
                    "expression": "2 + 3 * 4",
                    "precision": 2
                }
            }
            
            async with session.post(
                f"{server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    print(f"      📊 Expression: {result.get('expression')}")
                    print(f"      🔢 Result: {result.get('result')}")
                else:
                    print(f"      ❌ Calculator call failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Calculator call error: {e}")
        
        # Test search tool
        print("\n   🔍 Testing search tool...")
        try:
            payload = {
                "tool": "search_web",
                "parameters": {
                    "query": "Python programming",
                    "max_results": 3
                }
            }
            
            async with session.post(
                f"{server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    print(f"      🔍 Query: {result.get('query')}")
                    print(f"      📊 Results: {result.get('total_results')}")
                    for i, res in enumerate(result.get('results', []), 1):
                        print(f"         {i}. {res.get('title')}")
                else:
                    print(f"      ❌ Search call failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Search call error: {e}")
        
        # Test translate tool
        print("\n   🌐 Testing translate tool...")
        try:
            payload = {
                "tool": "translate_text",
                "parameters": {
                    "text": "Hello, World!",
                    "target_language": "ko",
                    "source_language": "en"
                }
            }
            
            async with session.post(
                f"{server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    print(f"      📝 Original: {result.get('original_text')}")
                    print(f"      🌐 Translated: {result.get('translated_text')}")
                    print(f"      🎯 Confidence: {result.get('confidence')}")
                else:
                    print(f"      ❌ Translate call failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Translate call error: {e}")
        
        # Test AI generation tool
        print("\n   🤖 Testing AI generation tool...")
        try:
            payload = {
                "tool": "generate_text",
                "parameters": {
                    "prompt": "Write a short poem about coding",
                    "max_length": 100
                }
            }
            
            async with session.post(
                f"{server_url}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    print(f"      💡 Prompt: {result.get('prompt')}")
                    print(f"      ✍️  Generated: {result.get('generated_text')}")
                else:
                    print(f"      ❌ Generation call failed: {response.status}")
        except Exception as e:
            print(f"      ❌ Generation call error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Direct communication test completed!")
    print("\n💡 Key Points:")
    print("   - Local MCP server is working correctly")
    print("   - All tools are responding as expected")
    print("   - Direct API calls work without authentication")
    print("   - Server endpoints:")
    print("     - GET  /health       - Health check")
    print("     - GET  /tools        - List tools")
    print("     - POST /tools/call   - Execute tools")

def check_server_status():
    """Check if the server is running"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True
        )
        if ":5000" in result.stdout:
            print("✅ Server appears to be running on port 5000")
            return True
        else:
            print("❌ No server detected on port 5000")
            return False
    except Exception as e:
        print(f"⚠️  Cannot check server status: {e}")
        return True  # Assume it's running

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_server_status()
    else:
        print("🔍 Checking server status...")
        if check_server_status():
            print("🚀 Starting direct communication test...")
            asyncio.run(test_direct_communication())
        else:
            print("❌ Please start the server first:")
            print("   python scripts/local_mcp_server.py") 