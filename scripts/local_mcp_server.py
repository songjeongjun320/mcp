#!/usr/bin/env python3
"""
Local MCP Server for Testing

This is a simple MCP server that runs locally for testing the Google MCP Toolbox integration.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from aiohttp import web, WSMsgType
from aiohttp.web import Request, Response, WebSocketResponse
import aiohttp_cors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockMCPServer:
    """Mock MCP Server for testing"""
    
    def __init__(self):
        self.tools = {
            "get_weather": {
                "name": "get_weather",
                "description": "Get current weather information",
                "parameters": {
                    "location": {"type": "string", "description": "Location to get weather for"},
                    "units": {"type": "string", "description": "Temperature units (celsius/fahrenheit)", "default": "celsius"}
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform basic mathematical calculations",
                "parameters": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"},
                    "precision": {"type": "integer", "description": "Number of decimal places", "default": 2}
                }
            },
            "search_web": {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum number of results", "default": 5}
                }
            },
            "translate_text": {
                "name": "translate_text",
                "description": "Translate text to another language",
                "parameters": {
                    "text": {"type": "string", "description": "Text to translate"},
                    "target_language": {"type": "string", "description": "Target language code"},
                    "source_language": {"type": "string", "description": "Source language code", "default": "auto"}
                }
            },
            "generate_text": {
                "name": "generate_text",
                "description": "Generate text using AI",
                "parameters": {
                    "prompt": {"type": "string", "description": "Text generation prompt"},
                    "max_length": {"type": "integer", "description": "Maximum length of generated text", "default": 100}
                }
            }
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return list(self.tools.values())
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get specific tool by name"""
        return self.tools.get(name)
    
    def call_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with parameters"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        
        # Mock responses for each tool
        if name == "get_weather":
            location = parameters.get("location", "Unknown")
            units = parameters.get("units", "celsius")
            temp_symbol = "°C" if units == "celsius" else "°F"
            temp = 22 if units == "celsius" else 72
            
            return {
                "location": location,
                "temperature": f"{temp}{temp_symbol}",
                "condition": "Sunny",
                "humidity": "65%",
                "wind": "10 km/h",
                "forecast": "Clear skies expected"
            }
        
        elif name == "calculate":
            expression = parameters.get("expression", "")
            precision = parameters.get("precision", 2)
            
            try:
                # Simple and safe evaluation for basic math
                allowed_chars = set("0123456789+-*/.() ")
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return {
                        "expression": expression,
                        "result": round(result, precision),
                        "precision": precision
                    }
                else:
                    return {"error": "Invalid expression"}
            except Exception as e:
                return {"error": f"Calculation error: {str(e)}"}
        
        elif name == "search_web":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 5)
            
            mock_results = [
                {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/result{i+1}", "snippet": f"This is a mock search result {i+1} for your query about {query}"}
                for i in range(min(max_results, 3))
            ]
            
            return {
                "query": query,
                "results": mock_results,
                "total_results": len(mock_results)
            }
        
        elif name == "translate_text":
            text = parameters.get("text", "")
            target_lang = parameters.get("target_language", "en")
            source_lang = parameters.get("source_language", "auto")
            
            return {
                "original_text": text,
                "translated_text": f"[Translated to {target_lang}] {text}",
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.95
            }
        
        elif name == "generate_text":
            prompt = parameters.get("prompt", "")
            max_length = parameters.get("max_length", 100)
            
            generated = f"This is AI-generated text based on your prompt: '{prompt}'. " * (max_length // 50 + 1)
            generated = generated[:max_length]
            
            return {
                "prompt": prompt,
                "generated_text": generated,
                "length": len(generated)
            }
        
        else:
            return {"error": f"Unknown tool: {name}"}

# Initialize server
mcp_server = MockMCPServer()

async def handle_health(request: Request) -> Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "server": "Mock MCP Server"})

async def handle_tools(request: Request) -> Response:
    """Get available tools"""
    tools = mcp_server.get_tools()
    return web.json_response({"tools": tools})

async def handle_tool_call(request: Request) -> Response:
    """Handle tool calls"""
    try:
        data = await request.json()
        tool_name = data.get("tool")
        parameters = data.get("parameters", {})
        
        if not tool_name:
            return web.json_response({"error": "Tool name is required"}, status=400)
        
        result = mcp_server.call_tool(tool_name, parameters)
        return web.json_response({"result": result})
    
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_websocket(request: Request) -> WebSocketResponse:
    """Handle WebSocket connections"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    logger.info("WebSocket client connected")
    
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                response = {"type": "response", "data": data}
                await ws.send_text(json.dumps(response))
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "Invalid JSON"}))
        elif msg.type == WSMsgType.ERROR:
            logger.error(f"WebSocket error: {ws.exception()}")
    
    logger.info("WebSocket client disconnected")
    return ws

async def create_app() -> web.Application:
    """Create the web application"""
    app = web.Application()
    
    # Add CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get("/health", handle_health)
    app.router.add_get("/tools", handle_tools)
    app.router.add_post("/tools/call", handle_tool_call)
    app.router.add_get("/ws", handle_websocket)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def main():
    """Main server function"""
    app = await create_app()
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "127.0.0.1", 5000)
    await site.start()
    
    print("🚀 Mock MCP Server started!")
    print("🌐 Server running at: http://127.0.0.1:5000")
    print("💡 Available endpoints:")
    print("   - GET  /health       - Health check")
    print("   - GET  /tools        - List available tools")
    print("   - POST /tools/call   - Call a tool")
    print("   - GET  /ws           - WebSocket endpoint")
    print("\n🔧 Available tools:")
    for tool in mcp_server.get_tools():
        print(f"   - {tool['name']}: {tool['description']}")
    
    print("\n✅ Server ready! You can now run:")
    print("   python examples/basic_usage.py")
    print("   python examples/production_example.py")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    try:
        # Keep the server running
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!") 