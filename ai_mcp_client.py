#!/usr/bin/env python3
"""
AI + MCP Client Demo - AI Application using MCP Protocol

This shows AI using MCP protocol to access tools - demonstrating AI + MCP integration
with real LLM calls using Groq.

Usage:
    export GROQ_API_KEY=your_api_key_here
    python ai_mcp_demo.py
"""

import os
import asyncio
import json
from groq import Groq
from fastmcp import Client


# Set up Groq API key (you'll need to set this)
GROQ_API_KEY = os.getenv('GROQ_API_KEY') or "your-groq-api-key-here"
groq_client = Groq(api_key=GROQ_API_KEY)


async def ai_mcp_client_demo():
    """Demonstrate AI application using MCP protocol with actual LLM calls"""
    print("🤖 AI + MCP CLIENT DEMO (Real LLM Integration)")
    print("=" * 50)
    
    # Connect to MCP server
    # MCP Client URL Options based on server transport:
    # - SSE (current):           Client("http://localhost:8765/sse")
    # - HTTP:                    Client("http://localhost:8765")
    # - Streamable HTTP:         Client("http://localhost:8765/stream")
    # - STDIO:                   Client("mcp_server.py") - simple file path syntax
    mcp_client = Client("http://localhost:8765/sse")
    async with mcp_client:
        # Get available tools from MCP server
        print("\n📋 AI discovering tools via MCP...")
        tools = await mcp_client.list_tools()
        available_tools = [tool.name for tool in tools]
        print(f"Available tools: {available_tools}")
        
        # Show tools discovered via MCP
        print(f"\n🔍 AI discovered {len(tools)} tools via MCP:")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
        
        # User requests to process
        user_requests = [
            "What's the weather like in Tokyo?",
            "Calculate 25 divided by 5",
            "Get information for user ID 2"
        ]
        
        print("\n🎯 AI processing user requests using LLM + MCP tools:")
        
        for user_input in user_requests:
            print(f"\n👤 User: {user_input}")
            
            # Create prompt for LLM to choose the right tool - Use tools directly as strings
            tools_str = "\n\n".join(str(tool) for tool in tools)
            prompt = f"""You are an AI assistant that can call tools to help users. 
                        Available tools:
                        {tools_str}

                        User query: "{user_input}"

                        Based on the user query, determine which tool to use and what parameters to provide.
                        Respond with ONLY a JSON object in this format:
                        {{
                            "tool_name": "tool_name_here",
                            "parameters": {{"param1": "value1", "param2": "value2"}}
                        }}

                        Do not include any other text in your response."""

            try:
                # Call LLM to decide which tool to use
                print("🧠 Asking LLM to choose the right tool...")
                
                if GROQ_API_KEY != "your-groq-api-key-here":
                    chat_completion = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant",
                        temperature=0.1
                    )
                    
                    llm_response = (chat_completion.choices[0].message.content or "").strip()
                    print(f"🧠 LLM response: {llm_response}")
                    
                    # Parse LLM response
                    try:
                        tool_choice = json.loads(llm_response)
                        tool_name = tool_choice["tool_name"]
                        parameters = tool_choice["parameters"]
                        
                        print(f"🤖 AI selected: {tool_name} with parameters {parameters}")
                        
                        # Call the chosen tool via MCP
                        result = await mcp_client.call_tool(tool_name, parameters)
                        print(f"   Result: {result.structured_content}")
                        
                    except json.JSONDecodeError:
                        print("❌ Failed to parse LLM response as JSON")
                else:
                    # Fallback simulation when no API key
                    print("⚠️  No Groq API key - simulating LLM response...")
                    tool_choice = None
                    if "weather" in user_input.lower():
                        tool_choice = {"tool_name": "get_weather", "parameters": {"city": "Tokyo"}}
                    elif "calculate" in user_input.lower() or "divided" in user_input.lower():
                        tool_choice = {"tool_name": "calculate", "parameters": {"operation": "divide", "a": 25, "b": 5}}
                    elif "user" in user_input.lower():
                        tool_choice = {"tool_name": "get_user_info", "parameters": {"user_id": 2}}
                    
                    if tool_choice:
                        print(f"🤖 Simulated AI choice: {tool_choice['tool_name']} with parameters {tool_choice['parameters']}")
                        result = await mcp_client.call_tool(tool_choice["tool_name"], tool_choice["parameters"])
                        print(f"   Result: {result.structured_content}")
                    else:
                        print("❌ Could not determine appropriate tool for query")
                    
            except Exception as e:
                print(f"❌ Error in LLM call or tool execution: {e}")
        
        print("\n✅ AI + MCP demo completed!")
        print("💡 Key insight: LLM chooses tools dynamically based on user query and MCP tool schemas")
        print("📝 Notice: Same tools discovered via MCP, but LLM makes the intelligent choice!")


def main():
    """Main function to run the demo"""
    print("AI + MCP Client Demo")
    print("Make sure MCP server is running: python mcp_server.py")
    print("Set GROQ_API_KEY environment variable for real LLM calls")
    print("   Or demo will run in simulation mode")
    print()
    asyncio.run(ai_mcp_client_demo())


# Check for interactive environment FIRST, before the __name__ check
try:
    # Check if we're in an interactive environment with a running event loop
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        print("VS Code Interactive mode detected!")
        print("Running AI + MCP demo...")
        # Use create_task to run in the existing event loop
        demo_task = asyncio.create_task(ai_mcp_client_demo())
except RuntimeError:
    # No event loop running - safe to use the standard script approach
    if __name__ == "__main__":
        main()