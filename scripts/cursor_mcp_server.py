#!/usr/bin/env python3
"""
Cursor MCP Server for Google MCP Toolbox

This server follows the MCP protocol for integration with Cursor.
"""

import asyncio
import json
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorMCPServer:
    """MCP Server for Cursor integration"""
    
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
                
                result = {
                    "location": location,
                    "temperature": f"{temp}{temp_symbol}",
                    "condition": "Sunny",
                    "humidity": "65%",
                    "wind": "10 km/h",
                    "forecast": "Clear skies expected"
                }
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Weather for {location}:\n"
                                   f"Temperature: {result['temperature']}\n"
                                   f"Condition: {result['condition']}\n"
                                   f"Humidity: {result['humidity']}\n"
                                   f"Wind: {result['wind']}\n"
                                   f"Forecast: {result['forecast']}"
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
                translated = f"[Mock translation to {target_lang}] {text}"
                
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

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
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

async def main():
    """Main server loop"""
    server = CursorMCPServer()
    
    logger.info("Cursor MCP Server started")
    logger.info("Available tools:")
    for tool in server.list_tools():
        logger.info(f"   - {tool['name']}: {tool['description']}")
    
    try:
        # Read from stdin and write to stdout (MCP protocol)
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                
                # Handle request
                response = await server.handle_request(request)
                
                # Send response
                response_json = json.dumps(response)
                print(response_json, flush=True)
                
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Server error: {str(e)}"
                        }
                    ],
                    "isError": True
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("MCP Server shutdown")

if __name__ == "__main__":
    asyncio.run(main()) 