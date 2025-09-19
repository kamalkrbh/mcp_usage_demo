# MCP Server for Demo: "MCP server ≠ Function Calling"
from fastmcp import FastMCP
import sys
import psutil
import time
import requests

mcp = FastMCP(name="DemoMCPServer")

# Simple tools for demonstration
@mcp.tool
def get_weather(city: str) -> dict:
    """Get weather information for a city."""
    # Simulated weather data
    weather_data = {
        "New York": {"temperature": 22, "condition": "sunny", "humidity": 65},
        "London": {"temperature": 15, "condition": "cloudy", "humidity": 80},
        "Tokyo": {"temperature": 28, "condition": "rainy", "humidity": 90}
    }
    return weather_data.get(city, {"error": f"Weather data not available for {city}"})

@mcp.tool
def calculate(operation: str, a: float, b: float) -> dict:
    """Perform basic mathematical operations."""
    operations = {
        "add": a + b,
        "subtract": a - b, 
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    result = operations.get(operation, "Error: Invalid operation")
    return {"operation": operation, "a": a, "b": b, "result": result}

@mcp.tool
def get_user_info(user_id: int) -> dict:
    """Get user information by ID."""
    users = {
        1: {"name": "Alice", "email": "alice@example.com", "role": "admin"},
        2: {"name": "Bob", "email": "bob@example.com", "role": "user"}, 
        3: {"name": "Charlie", "email": "charlie@example.com", "role": "manager"}
    }
    return users.get(user_id, {"error": f"User {user_id} not found"})

# Utility functions for MCP server management
def find_mcp_server_processes():
    """Find running MCP server processes"""
    mcp_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 1:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'mcp_server.py' in cmdline and 'python' in cmdline:
                    mcp_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return mcp_processes

def stop_mcp_server(verify_with_health_check=True):
    """Stop any running MCP server processes
    
    Args:
        verify_with_health_check (bool): If True, also check HTTP endpoint to verify server is stopped
    """
    print("🛑 STOPPING MCP SERVER")
    print("=" * 25)
    
    existing_processes = find_mcp_server_processes()
    if existing_processes:
        print(f"🔍 Found {len(existing_processes)} existing MCP server process(es)")
        for proc in existing_processes:
            try:
                print(f"🛑 Stopping MCP server (PID: {proc.pid})")
                proc.terminate()
                proc.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
                print(f"✅ Terminated process {proc.pid}")
            except psutil.TimeoutExpired:
                print(f"⚠️  Process {proc.pid} didn't terminate gracefully, force killing...")
                proc.kill()
                print(f"💀 Force killed process {proc.pid}")
            except Exception as e:
                print(f"❌ Error stopping process {proc.pid}: {e}")
        
        # Optional health check verification
        if verify_with_health_check:
            time.sleep(2)
            try:
                response = requests.get("http://localhost:8765/health", timeout=2)
                print("⚠️  Server might still be running - check manually")
            except requests.RequestException:
                print("✅ Server is no longer responding - successfully stopped")
    else:
        print("✅ No MCP server processes found - nothing to stop")
    
    print("\n🏁 Stop operation completed!")


def start_mcp_server(transport="sse", host="0.0.0.0", port=8765):
    """Start the MCP server."""
    print(f"🚀 Starting MCP server with transport={transport} on {host}:{port}")
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "http":
        mcp.run(host=host, port=port, transport="http")
    elif transport == "sse":
        mcp.run(host=host, port=port, transport="sse")
    elif transport == "streamable-http":
        mcp.run(host=host, port=port, transport="streamable-http")
    else:
        mcp.run(host=host, port=port, transport="sse")  # default fallback

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "sse"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    start_mcp_server(transport=transport, port=port)