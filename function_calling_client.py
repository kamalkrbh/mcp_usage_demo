#!/usr/bin/env python3
"""
Traditional Function Calling Demo - AI with Direct Function Calls

This demonstrate    print("TRADITIONAL FUNCTION CALLING DEMO (Real LLM Integration)")
    print("=" * 65)
    
    # Show available functions
    function_schemas = create_function_schema_from_mcp_tools()
    
    print(f"\nUsing actual functions from mcp_server.py:")
    for name in ["get_weather", "calculate", "get_user_info"]:
        print(f"  - {name}")
    
    print(f"\nGenerated {len(function_schemas)} function schemas dynamically")
    print("Schemas created from function signatures & docstrings")
    
    # Show function schemas
    print(f"\nFUNCTION CALLING SCHEMAS:")
    print("=" * 35)nction calling where we import the actual functions 
from the MCP server and use them directly (without the @mcp.tool decorator effect).

Usage:
    export GROQ_API_KEY=your_api_key_here
    python function_calling_demo.py
"""

import json
import inspect
import os
from mcp_server import get_weather, calculate, get_user_info
from groq import Groq


# Groq client for LLM calls
GROQ_API_KEY = os.getenv('GROQ_API_KEY') or "your-groq-api-key-here"
groq_client = Groq(api_key=GROQ_API_KEY)


def create_function_schema_from_mcp_tools():
    """Create function calling schemas dynamically from MCP server tools"""
    # Define the actual functions (not the MCP decorated versions)
    def get_weather_func(city: str) -> dict:
        """Get weather information for a city."""
        # Simulated weather data
        weather_data = {
            "New York": {"temperature": 22, "condition": "sunny", "humidity": 65},
            "London": {"temperature": 15, "condition": "cloudy", "humidity": 80},
            "Tokyo": {"temperature": 28, "condition": "rainy", "humidity": 90}
        }
        return weather_data.get(city, {"error": f"Weather data not available for {city}"})
    
    def calculate_func(operation: str, a: float, b: float) -> dict:
        """Perform basic mathematical operations."""
        operations = {
            "add": a + b,
            "subtract": a - b, 
            "multiply": a * b,
            "divide": a / b if b != 0 else "Error: Division by zero"
        }
        result = operations.get(operation, "Error: Invalid operation")
        return {"operation": operation, "a": a, "b": b, "result": result}
    
    def get_user_info_func(user_id: int) -> dict:
        """Get user information by ID."""
        users = {
            1: {"name": "Alice", "email": "alice@example.com", "role": "admin"},
            2: {"name": "Bob", "email": "bob@example.com", "role": "user"}, 
            3: {"name": "Charlie", "email": "charlie@example.com", "role": "manager"}
        }
        return users.get(user_id, {"error": f"User {user_id} not found"})
    
    # Map function names to actual callable functions
    mcp_functions = {
        "get_weather": get_weather_func,
        "calculate": calculate_func, 
        "get_user_info": get_user_info_func
    }
    
    schemas = []
    for func_name, func in mcp_functions.items():
        # Get function signature and docstring
        sig = inspect.signature(func)
        doc = func.__doc__ or f"Function {func_name}"
        
        # Build parameters schema from function signature
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # default
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == str:
                param_type = "string"
            
            properties[param_name] = {
                "type": param_type,
                "description": f"The {param_name} parameter"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        schema = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": doc.strip(),
                "parameters": {
                    "type": "object", 
                    "properties": properties,
                    "required": required
                }
            }
        }
        schemas.append(schema)
    
    return schemas, mcp_functions


def function_calling_demo():
    """Demonstrate traditional function calling with AI using actual MCP server functions and real LLM"""
    print("TRADITIONAL FUNCTION CALLING DEMO (Real LLM Integration)")
    print("=" * 65)
    
    # Generate schemas from actual MCP server functions
    function_schemas, available_functions = create_function_schema_from_mcp_tools()
    
    print(f"\nUsing actual functions from mcp_server.py:")
    for func_name in available_functions.keys():
        print(f"  - {func_name}")
    
    print(f"\nGenerated {len(function_schemas)} function schemas dynamically")
    print("Schemas created from function signatures & docstrings")
    
    # Show function calling schemas in detail
    print(f"\nFUNCTION CALLING SCHEMAS:")
    print("=" * 35)
    for i, schema in enumerate(function_schemas, 1):
        print(f"\n{i}. Function: {schema['function']['name']}")
        print(f"   Description: {schema['function']['description']}")
        print(f"   Parameters:")
        properties = schema['function']['parameters']['properties']
        required = schema['function']['parameters']['required']
        for param_name, param_info in properties.items():
            req_mark = " (required)" if param_name in required else " (optional)"
            print(f"     • {param_name}: {param_info['type']}{req_mark}")
            print(f"       {param_info['description']}")
    
    # Show one complete example schema
    print(f"\nComplete JSON Schema Example (get_weather):")
    print(json.dumps(function_schemas[0], indent=2))
    
    # Simulate user requests with LLM integration
    user_requests = [
        "What's the weather in New York?",
        "Add 10 and 15", 
        "Get user 3's information"
    ]
    
    print(f"\nEXECUTING FUNCTION CALLS WITH LLM:")
    print("=" * 40)
    
    for user_input in user_requests:
        print(f"\nUser: {user_input}")
        
        # Create prompt for LLM with function schemas
        functions_description = []
        for schema in function_schemas:
            func_info = schema['function']
            name = func_info['name']
            desc = func_info['description']
            params = func_info['parameters']['properties']
            required = func_info['parameters']['required']
            
            param_list = []
            for param, details in params.items():
                param_type = details['type']
                is_req = " (required)" if param in required else " (optional)"
                param_list.append(f"{param}: {param_type}{is_req}")
            
            functions_description.append(f"- {name}: {desc} | Parameters: {', '.join(param_list)}")
        
        functions_list = "\n".join(functions_description)
        
        prompt = f"""You are an AI assistant that can call functions to help users.
Available functions:
{functions_list}

User query: "{user_input}"

Based on the user query, determine which function to call and what parameters to provide.
Respond with ONLY a JSON object in this format:
{{
    "function_name": "function_name_here",
    "parameters": {{"param1": "value1", "param2": "value2"}}
}}

Do not include any other text in your response."""

        try:
            # Call LLM to decide which function to use
            print("Asking LLM to choose the right function...")
            
            if GROQ_API_KEY != "your-groq-api-key-here":
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.1
                )
                
                llm_response = (chat_completion.choices[0].message.content or "").strip()
                print(f"LLM response: {llm_response}")
                
                # Parse LLM response
                try:
                    function_choice = json.loads(llm_response)
                    function_name = function_choice["function_name"]
                    parameters = function_choice["parameters"]
                    
                    print(f"AI selected: {function_name} with parameters {parameters}")
                    
                    # Call the chosen function directly
                    result = None
                    if function_name in available_functions:
                        if function_name == "get_weather":
                            result = available_functions[function_name](parameters["city"])
                        elif function_name == "calculate":
                            result = available_functions[function_name](
                                parameters["operation"], 
                                parameters["a"], 
                                parameters["b"]
                            )
                        elif function_name == "get_user_info":
                            result = available_functions[function_name](parameters["user_id"])
                        
                        if result is not None:
                            print(f"   Result: {result}")
                        else:
                            print("Function execution failed")
                    else:
                        print(f"Unknown function: {function_name}")
                        
                except json.JSONDecodeError:
                    print("Failed to parse LLM response as JSON")
            else:
                # Fallback simulation when no API key
                print("⚠️  No Groq API key - simulating LLM response...")
                function_choice = None
                if "weather" in user_input.lower():
                    city = "New York" if "new york" in user_input.lower() else "London"
                    function_choice = {"function_name": "get_weather", "parameters": {"city": city}}
                elif "add" in user_input.lower():
                    function_choice = {"function_name": "calculate", "parameters": {"operation": "add", "a": 10, "b": 15}}
                elif "user" in user_input.lower():
                    function_choice = {"function_name": "get_user_info", "parameters": {"user_id": 3}}
                
                if function_choice:
                    print(f"Simulated AI choice: {function_choice['function_name']} with parameters {function_choice['parameters']}")
                    
                    # Execute the simulated choice
                    result = None
                    if function_choice["function_name"] == "get_weather":
                        result = available_functions["get_weather"](function_choice["parameters"]["city"])
                    elif function_choice["function_name"] == "calculate":
                        result = available_functions["calculate"](
                            function_choice["parameters"]["operation"],
                            function_choice["parameters"]["a"],
                            function_choice["parameters"]["b"]
                        )
                    elif function_choice["function_name"] == "get_user_info":
                        result = available_functions["get_user_info"](function_choice["parameters"]["user_id"])
                    
                    if result is not None:
                        print(f"   Result: {result}")
                    else:
                        print("Function execution failed")
                else:
                    print("Could not determine appropriate function for query")
                
        except Exception as e:
            print(f"Error in LLM call or function execution: {e}")
    
    print("\nFunction calling demo completed!")
    print("Key insight: LLM chooses functions based on user query and function schemas")
    print("Notice: Same functions from MCP server, but called directly with LLM guidance")
    print("LLM analyzes schemas -> chooses function -> app executes direct call")


def main():
    """Main function to run the demo"""
    print("Traditional Function Calling Demo")
    print("Uses functions directly from mcp_server.py (no MCP protocol)")
    print("Set GROQ_API_KEY environment variable for real LLM calls")
    print("   Or demo will run in simulation mode")
    print()
    
    function_calling_demo()


# Check for interactive environment FIRST, before the __name__ check
try:
    # Check if we're in an interactive environment with a running event loop
    import asyncio
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        print("VS Code Interactive mode detected!")
        print("Running Function Calling demo...")
        # Function calling demo is synchronous, so we can run it directly
        function_calling_demo()
except RuntimeError:
    # No event loop running - safe to use the standard script approach
    if __name__ == "__main__":
        main()