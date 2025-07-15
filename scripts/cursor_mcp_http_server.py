#!/usr/bin/env python3
"""
HTTP-based Cursor MCP Server for Google MCP Toolbox

This server provides MCP protocol over HTTP for URL-based connections with Cursor.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from aiohttp import web, WSMsgType
from aiohttp.web import Request, Response, WebSocketResponse
import aiohttp_cors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CursorMCPHTTPServer:
    """HTTP-based MCP Server for Cursor integration"""
    
    def __init__(self):
        self.tools = {
            "get_weather": {
                "name": "get_weather",
                "description": "Get current weather information for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to get weather for"
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units (celsius/fahrenheit)",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform basic mathematical calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        },
                        "precision": {
                            "type": "integer",
                            "description": "Number of decimal places",
                            "default": 2
                        }
                    },
                    "required": ["expression"]
                }
            },
            "search_web": {
                "name": "search_web",
                "description": "Search the web for information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            "translate_text": {
                "name": "translate_text",
                "description": "Translate text to another language",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to translate"
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (e.g., 'ko', 'en', 'ja')"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code",
                            "default": "auto"
                        }
                    },
                    "required": ["text", "target_language"]
                }
            },
            "generate_text": {
                "name": "generate_text",
                "description": "Generate text using AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text generation prompt"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum length of generated text",
                            "default": 200
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        try:
            if name not in self.tools:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Tool '{name}' not found"
                        }
                    ],
                    "isError": True
                }
            
            # Mock implementation for each tool
            if name == "get_weather":
                location = arguments.get("location", "Unknown")
                units = arguments.get("units", "celsius")
                temp_symbol = "°C" if units == "celsius" else "°F"
                temp = 22 if units == "celsius" else 72
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Weather for {location}:\n"
                                   f"Temperature: {temp}{temp_symbol}\n"
                                   f"Condition: Sunny\n"
                                   f"Humidity: 65%\n"
                                   f"Wind: 10 km/h\n"
                                   f"Forecast: Clear skies expected"
                        }
                    ]
                }
            
            elif name == "calculate":
                expression = arguments.get("expression", "")
                precision = arguments.get("precision", 2)
                
                try:
                    # Simple and safe evaluation
                    allowed_chars = set("0123456789+-*/.() ")
                    if all(c in allowed_chars for c in expression):
                        result = eval(expression)
                        formatted_result = round(result, precision)
                        
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Expression: {expression}\n"
                                           f"Result: {formatted_result}"
                                }
                            ]
                        }
                    else:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Error: Invalid expression. Only numbers and basic operators (+, -, *, /, (, )) are allowed."
                                }
                            ],
                            "isError": True
                        }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Calculation error: {str(e)}"
                            }
                        ],
                        "isError": True
                    }
            
            elif name == "search_web":
                query = arguments.get("query", "")
                max_results = arguments.get("max_results", 5)
                
                # Mock search results
                results = [
                    {
                        "title": f"Search Result {i+1} for '{query}'",
                        "url": f"https://example.com/result{i+1}",
                        "snippet": f"This is mock search result {i+1} for your query about {query}."
                    }
                    for i in range(min(max_results, 3))
                ]
                
                result_text = f"Search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    result_text += f"{i}. {result['title']}\n"
                    result_text += f"   URL: {result['url']}\n"
                    result_text += f"   {result['snippet']}\n\n"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            
            elif name == "translate_text":
                text = arguments.get("text", "")
                target_lang = arguments.get("target_language", "en")
                source_lang = arguments.get("source_language", "auto")
                
                # Mock translation
                if target_lang == "ko":
                    translated = f"[한국어로 번역됨] {text}"
                elif target_lang == "en":
                    translated = f"[Translated to English] {text}"
                else:
                    translated = f"[Translated to {target_lang}] {text}"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Original text: {text}\n"
                                   f"Translated to {target_lang}: {translated}\n"
                                   f"Source language: {source_lang}\n"
                                   f"Confidence: 95%"
                        }
                    ]
                }
            
            elif name == "generate_text":
                prompt = arguments.get("prompt", "")
                max_length = arguments.get("max_length", 200)
                
                # Mock AI generation
                generated = f"This is AI-generated text based on your prompt: '{prompt}'. "
                generated += "The generated content would continue here with relevant information about the topic. "
                generated += "This is a mock implementation that demonstrates the text generation capability."
                
                # Truncate to max length
                if len(generated) > max_length:
                    generated = generated[:max_length] + "..."
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Generated text for prompt: '{prompt}'\n\n{generated}"
                        }
                    ]
                }
            
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Unknown tool '{name}'"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool {name}: {str(e)}"
                    }
                ],
                "isError": True
            }

    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return {
                    "tools": self.list_tools()
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Error: Tool name is required"
                            }
                        ],
                        "isError": True
                    }
                
                return self.call_tool(tool_name, arguments)
            
            elif method == "ping":
                return {"pong": True}
            
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Unknown method '{method}'"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Internal server error: {str(e)}"
                    }
                ],
                "isError": True
            }

# Initialize server
mcp_server = CursorMCPHTTPServer()

async def handle_health(request: Request) -> Response:
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy", 
        "server": "Cursor MCP HTTP Server",
        "protocol": "MCP over HTTP"
    })

async def handle_mcp_request(request: Request) -> Response:
    """Handle MCP protocol requests"""
    try:
        # Only handle POST requests for MCP protocol
        if request.method != 'POST':
            return web.json_response({
                "error": "MCP endpoint only accepts POST requests"
            }, status=405)
        
        data = await request.json()
        result = mcp_server.handle_mcp_request(data)
        return web.json_response(result)
    
    except json.JSONDecodeError:
        return web.json_response({
            "content": [
                {
                    "type": "text",
                    "text": "Error: Invalid JSON"
                }
            ],
            "isError": True
        }, status=400)
    except Exception as e:
        logger.error(f"Request error: {e}")
        return web.json_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Server error: {str(e)}"
                }
            ],
            "isError": True
        }, status=500)

async def handle_tools_list(request: Request) -> Response:
    """List available tools"""
    tools = mcp_server.list_tools()
    return web.json_response({"tools": tools})

async def handle_tool_call(request: Request) -> Response:
    """Handle tool calls"""
    try:
        data = await request.json()
        tool_name = data.get("name")
        arguments = data.get("arguments", {})
        
        if not tool_name:
            return web.json_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Tool name is required"
                    }
                ],
                "isError": True
            }, status=400)
        
        result = mcp_server.call_tool(tool_name, arguments)
        return web.json_response(result)
    
    except json.JSONDecodeError:
        return web.json_response({
            "content": [
                {
                    "type": "text",
                    "text": "Error: Invalid JSON"
                }
            ],
            "isError": True
        }, status=400)
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return web.json_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }, status=500)

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
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    app.router.add_post("/", handle_mcp_request)     # Main MCP endpoint (root)
    app.router.add_post("/mcp", handle_mcp_request)  # Main MCP endpoint (mcp)
    app.router.add_get("/tools", handle_tools_list)  # List tools
    app.router.add_post("/tools/call", handle_tool_call)  # Call tool
    
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
    
    logger.info("Cursor MCP HTTP Server started")
    logger.info("Server running at: http://127.0.0.1:5000")
    logger.info("MCP Protocol endpoint: http://127.0.0.1:5000/mcp")
    logger.info("Available endpoints:")
    logger.info("   - GET  /health       - Health check")
    logger.info("   - POST /mcp          - MCP protocol requests")
    logger.info("   - GET  /tools        - List available tools")
    logger.info("   - POST /tools/call   - Call a tool")
    logger.info("")
    logger.info("Available tools:")
    for tool in mcp_server.list_tools():
        logger.info(f"   - {tool['name']}: {tool['description']}")
    
    logger.info("")
    logger.info("Server ready! Press Ctrl+C to stop")
    
    try:
        # Keep the server running
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        await runner.cleanup()
        logger.info("MCP Server shutdown")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Goodbye!") 