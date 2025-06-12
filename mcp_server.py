#!/usr/bin/env python3
"""
Simple MCP Server Example
This demonstrates the basic concepts of an MCP server with tools and resources.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# MCP Protocol Message Types
@dataclass
class MCPMessage:
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPServer:
    def __init__(self):
        self.tools = {
            "get_weather": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["city"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform basic arithmetic calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
        
        self.resources = {
            "file://notes.txt": {
                "uri": "file://notes.txt",
                "name": "Personal Notes",
                "description": "A simple text file with personal notes",
                "mimeType": "text/plain"
            }
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            params = message.get("params", {})
            msg_id = message.get("id")
            
            if method == "initialize":
                return self.handle_initialize(msg_id, params)
            elif method == "tools/list":
                return self.handle_tools_list(msg_id)
            elif method == "tools/call":
                return await self.handle_tools_call(msg_id, params)
            elif method == "resources/list":
                return self.handle_resources_list(msg_id)
            elif method == "resources/read":
                return self.handle_resources_read(msg_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def handle_initialize(self, msg_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "example-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_tools_list(self, msg_id: str) -> Dict[str, Any]:
        """Return list of available tools"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    async def handle_tools_call(self, msg_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_weather":
            city = arguments.get("city", "Unknown")
            # Simulate weather data
            weather_data = {
                "city": city,
                "temperature": "22°C",
                "condition": "Sunny",
                "humidity": "65%",
                "timestamp": datetime.now().isoformat()
            }
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Weather in {city}: {weather_data['condition']}, {weather_data['temperature']}, Humidity: {weather_data['humidity']}"
                        }
                    ]
                }
            }
        
        elif tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Simple and safe evaluation for basic arithmetic
                allowed_chars = set("0123456789+-*/(). ")
                if not all(c in allowed_chars for c in expression):
                    raise ValueError("Invalid characters in expression")
                
                result = eval(expression)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"{expression} = {result}"
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32602,
                        "message": f"Calculation error: {str(e)}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    def handle_resources_list(self, msg_id: str) -> Dict[str, Any]:
        """Return list of available resources"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "resources": list(self.resources.values())
            }
        }
    
    def handle_resources_read(self, msg_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource"""
        uri = params.get("uri")
        
        if uri == "file://notes.txt":
            # Simulate reading a notes file
            notes_content = """Personal Notes
===============

1. Remember to buy groceries
2. Call dentist for appointment
3. Finish MCP server project
4. Review quarterly reports

Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": notes_content
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }

async def main():
    """Main server loop"""
    server = MCPServer()
    
    print("MCP Server starting...", file=sys.stderr)
    print("Server capabilities:", file=sys.stderr)
    print("- Tools: get_weather, calculate", file=sys.stderr)
    print("- Resources: file://notes.txt", file=sys.stderr)
    print("Ready for connections.", file=sys.stderr)
    
    # Read messages from stdin and write responses to stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            message = json.loads(line.strip())
            response = await server.handle_message(message)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            break

if __name__ == "__main__":
    asyncio.run(main())