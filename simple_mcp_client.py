#!/usr/bin/env python3
"""
Complete MCP Client Demo - Non-AI Application

This demonstrates comprehensive MCP protocol usage including:
- Tool discovery and execution
- Resource content reading
- Prompt template generation
- Server connectivity and health checks

Shows that MCP is NOT just for AI - any application can use MCP protocol 
to discover and call tools, read resources, and generate content.

Usage:
    python simple_mcp_client.py
    
Interactive Usage (VS Code Interactive, Jupyter, etc.):
    await simple_mcp_client_demo()
    or
    await run_interactive_demo()
"""

import asyncio
import json
from fastmcp import Client


async def run_interactive_demo():
    """Convenience function for interactive environments"""
    print("Running MCP demo in interactive mode...")
    await simple_mcp_client_demo()
    print("Demo completed! You can run it again with: await run_interactive_demo()")


async def simple_mcp_client_demo():
    """Demonstrate non-AI application using MCP protocol"""
    print("SIMPLE MCP CLIENT DEMO (Non-AI Application)")
    print("=" * 50)
    
    # MCP Client URL Options based on server transport:
    # - SSE (current):           "http://localhost:8765/sse"
    # - HTTP:                    "http://localhost:8765"
    # - Streamable HTTP:         "http://localhost:8765/stream"
    # - STDIO:                   Client("mcp_server.py") - simple file path syntax
    client = Client("http://localhost:8765/sse")
    async with client:
        # 1. Server Health Check & Connection Status
        print("\nSERVER CONNECTIVITY:")
        print("=" * 25)
        try:
            ping_result = await client.ping()
            print("Server ping successful!")
            
            # Show connection status
            is_connected = client.is_connected()
            print(f"Connection status: {'Connected' if is_connected else 'Disconnected'}")
        except Exception as e:
            print(f"Server ping failed: {e}")
            return
        
        # 2. Complete Discovery via MCP Protocol
        print("\nDISCOVERY - ALL AVAILABLE FEATURES:")
        print("=" * 45)
        
        # Tools discovery
        print("\nAvailable Tools:")
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Resources discovery
        print("\nAvailable Resources:")
        try:
            resources = await client.list_resources()
            if resources:
                print(f"Found {len(resources)} resources:")
                for resource in resources:
                    print(f"  - {resource.uri}: {resource.name}")
                    print(f"    Description: {resource.description}")
            else:
                print("  No resources available")
        except Exception as e:
            print(f"  No resources available: {e}")
        
        # Prompts discovery
        print("\nAvailable Prompts:")
        try:
            prompts = await client.list_prompts()
            if prompts:
                print(f"Found {len(prompts)} prompts:")
                for prompt in prompts:
                    print(f"  - {prompt.name}: {prompt.description}")
                    if hasattr(prompt, 'arguments') and prompt.arguments:
                        args = [arg.name for arg in prompt.arguments]
                        print(f"    Parameters: {args}")
            else:
                print("  No prompts available")
        except Exception as e:
            print(f"  No prompts available: {e}")
        
        # 3. Show MCP Tool Syntax and Parameters
        print("\nMCP TOOL SYNTAX & PARAMETERS:")
        print("=" * 40)
        for tool in tools:
            print(f"\nTool: {tool.name}")
            print(f"   Description: {tool.description}")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"   Parameters Schema:")
                print(json.dumps(tool.inputSchema, indent=4))
            else:
                print("   Parameters: No schema available")
        
        # 4. Execute tools via MCP Protocol
        print("\nEXECUTING MCP TOOLS:")
        print("=" * 30)
        
        print("\nCalling get_weather tool...")
        weather_result = await client.call_tool("get_weather", {"city": "London"})
        print(f"Result: {weather_result.structured_content}")
        
        print("\nCalling calculate tool...")
        calc_result = await client.call_tool("calculate", {"operation": "multiply", "a": 15, "b": 4})
        print(f"Result: {calc_result.structured_content}")
        
        print("\nCalling calculate tool...")
        calc_result = await client.call_tool("calculate", {"operation": "multiply", "a": 15, "b": 4})
        print(f"Result: {calc_result.structured_content}")
        
        print("\nCalling get_user_info tool...")
        user_result = await client.call_tool("get_user_info", {"user_id": 1})
        print(f"Result: {user_result.structured_content}")
        
        # 5. Read Resources via MCP Protocol
        print("\nREADING MCP RESOURCES:")
        print("=" * 30)
        try:
            resources = await client.list_resources()
            if resources:
                print(f"\nReading content from {len(resources)} resources:")
                for resource in resources[:3]:  # Read first 3 resources to avoid spam
                    try:
                        print(f"\nReading resource: {resource.uri}")
                        content = await client.read_resource(resource.uri)
                        if content and len(content) > 0:
                            # Handle different content types safely
                            try:
                                text_content = str(content[0])
                                # Show preview of content
                                preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                                print(f"Content preview: {preview}")
                            except Exception:
                                print(f"Content: [Available but not displayable as text]")
                        else:
                            print("Content: [Empty]")
                    except Exception as e:
                        print(f"Error reading {resource.uri}: {e}")
            else:
                print("No resources available to read")
        except Exception as e:
            print(f"Resource reading failed: {e}")
        
        # 6. Generate Content from Prompt Templates
        print("\nGENERATING FROM PROMPT TEMPLATES:")
        print("=" * 40)
        try:
            prompts = await client.list_prompts()
            if prompts:
                print(f"\nGenerating content from {len(prompts)} prompt templates:")
                for prompt in prompts[:3]:  # Use first 3 prompts
                    try:
                        print(f"\nUsing prompt template: {prompt.name}")
                        
                        # Handle different prompt types with appropriate parameters
                        if prompt.name == "greeting":
                            result = await client.get_prompt("greeting", {"name": "MCP User"})
                        elif prompt.name == "tool_help":
                            result = await client.get_prompt("tool_help", {"tool_name": "get_weather"})
                        elif prompt.name == "system_info":
                            result = await client.get_prompt("system_info", {})
                        else:
                            # Try with empty parameters for unknown prompts
                            result = await client.get_prompt(prompt.name, {})
                        
                        # Display generated content
                        if result and result.messages:
                            content = str(result.messages[0].content) if result.messages else "No content generated"
                            print(f"Generated content: {content}")
                        else:
                            print("Generated content: [No content]")
                            
                    except Exception as e:
                        print(f"Error generating from {prompt.name}: {e}")
            else:
                print("No prompt templates available")
        except Exception as e:
            print(f"Prompt generation failed: {e}")
        
        print("\nMCP DEMO COMPLETED!")
        print("=" * 25)
        print("Demonstrated MCP features:")
        print("- Server connectivity and health checks")
        print("- Complete discovery (tools, resources, prompts)")
        print("- Tool execution with parameters")
        print("- Resource content reading")
        print("- Prompt template generation")
        print("- All without AI - pure MCP protocol!")

def main():
    """Main function to run the complete MCP demo"""
    print("Complete MCP Client Demo - All Features")
    print("Make sure MCP server is running: python mcp_server.py")
    print("This demo shows tools, resources, and prompts - all MCP features!")
    print()
    asyncio.run(simple_mcp_client_demo())


# Check for interactive environment FIRST, before the __name__ check
try:
    # Check if we're in an interactive environment with a running event loop
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        print("VS Code Interactive mode detected!")
        print("Running MCP demo...")
        # Use create_task to run in the existing event loop
        demo_task = asyncio.create_task(simple_mcp_client_demo())
except RuntimeError:
    # No event loop running - safe to use the standard script approach
    if __name__ == "__main__":
        main()
