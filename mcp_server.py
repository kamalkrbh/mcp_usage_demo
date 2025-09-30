# MCP Server for Demo: "MCP server ≠ Function Calling"
from fastmcp import FastMCP
import sys
import os
import psutil
import time
import requests
import socket

mcp = FastMCP(name="DemoMCPServer")

# Simple tools for demonstration
@mcp.tool
def get_weather(city: str) -> dict: ##Get Weather
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

# Simple resources for demonstration
@mcp.resource("demo://docs/welcome")
def welcome_doc() -> str:
    """Welcome documentation for the demo server."""
    return """
# Welcome to MCP Demo Server

This is a simple demonstration server showing:
- Tool discovery and execution
- Resource access
- Prompt templates

Available tools: get_weather, calculate, get_user_info
    """.strip()

@mcp.resource("demo://config/server")
def server_config() -> dict:
    """Server configuration information."""
    return {
        "name": "DemoMCPServer",
        "version": "1.0.0",
        "tools_count": 3,
        "resources_count": 3,
        "prompts_count": 2,
        "supported_transports": ["sse", "http", "streamable-http", "stdio"]
    }

@mcp.resource("demo://data/sample")
def sample_data() -> dict:
    """Sample data for demonstration."""
    return {
        "users": ["Alice", "Bob", "Charlie"],
        "cities": ["New York", "London", "Tokyo"],
        "operations": ["add", "subtract", "multiply", "divide"],
        "timestamp": "2025-09-19T12:00:00Z"
    }

# Simple prompts for demonstration
@mcp.prompt
def greeting(name: str = "User") -> str:
    """Generate a personalized greeting."""
    return f"Hello {name}! Welcome to the MCP Demo Server. How can I help you today?"

@mcp.prompt  
def tool_help(tool_name: str = "all") -> str:
    """Provide help information for tools."""
    help_text = {
        "get_weather": "Use get_weather(city) to get weather info for New York, London, or Tokyo",
        "calculate": "Use calculate(operation, a, b) with operations: add, subtract, multiply, divide", 
        "get_user_info": "Use get_user_info(user_id) with IDs 1, 2, or 3 to get user details",
        "all": "Available tools: get_weather, calculate, get_user_info. Each tool has specific parameters."
    }
    return help_text.get(tool_name, f"No help available for tool: {tool_name}")

# Utility functions for MCP server management
def is_port_in_use(port, host='localhost'):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def is_mcp_server_running(port=8765):
    """Check if MCP server is running on the specified port by testing the MCP endpoint"""
    try:
        # Test the SSE endpoint which is the default for MCP
        response = requests.get(f"http://localhost:{port}/sse", timeout=2)
        # MCP SSE endpoint should return something, even if it's an error about missing headers
        return True
    except requests.RequestException:
        try:
            # Also test HTTP endpoint as fallback
            response = requests.get(f"http://localhost:{port}", timeout=2)
            return True
        except requests.RequestException:
            return False

def get_port_info(port):
    """Get information about what's running on a port"""
    if not is_port_in_use(port):
        return None
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    
    return {'pid': 'Unknown', 'name': 'Unknown', 'cmdline': 'Unknown process using port'}

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


def start_mcp_server(transport="sse", host="0.0.0.0", port=8765, force_restart=False):
    """Start the MCP server with proper port checking.
    
    Args:
        transport (str): Transport type (sse, http, stdio, streamable-http)
        host (str): Host to bind to
        port (int): Port to bind to
        force_restart (bool): If True, stop existing server and start new one
    """
    print(f"🚀 Starting MCP server with transport={transport} on {host}:{port}")
    
    # Step 1: Check if port is already in use
    if is_port_in_use(port):
        print(f"\n🔍 Port {port} is already in use!")
        
        # Check if it's an MCP server
        if is_mcp_server_running(port):
            print(f"✅ MCP server is already running on port {port}")
            if not force_restart:
                print("💡 Use --force-restart flag or stop the existing server first")
                print(f"🌐 Server available at: http://{host}:{port}")
                return
            else:
                print("🔄 Force restart requested - stopping existing server...")
                stop_mcp_server(verify_with_health_check=False)
                time.sleep(2)
                
                # Re-check if port is now free
                if is_port_in_use(port):
                    print(f"⚠️  Port {port} is still in use after stopping server")
                    port_info = get_port_info(port)
                    if port_info:
                        print(f"   PID: {port_info['pid']}")
                        print(f"   Name: {port_info['name']}")
                        print(f"   Command: {port_info['cmdline']}")
                    print("💡 Please wait a moment and try again")
                    return
                else:
                    print(f"✅ Port {port} is now free - proceeding with startup...")
                    # Continue to server startup
        else:
            # Something else is using the port
            port_info = get_port_info(port)
            print(f"❌ Port {port} is occupied by another process:")
            if port_info:
                print(f"   PID: {port_info['pid']}")
                print(f"   Name: {port_info['name']}")
                print(f"   Command: {port_info['cmdline']}")
            print(f"💡 Please stop the process or use a different port")
            return
    
    # Step 2: Check if MCP server processes exist (but maybe on different port)
    existing_processes = find_mcp_server_processes()
    if existing_processes and not force_restart:
        print(f"\n🔍 Found {len(existing_processes)} existing MCP server process(es):")
        for proc in existing_processes:
            print(f"   PID {proc.pid}: {' '.join(proc.cmdline())}")
        print("💡 These might be running on different ports")
        print("💡 Use --force-restart to stop all MCP servers first")
    
    # Step 3: Start the server
    print(f"\n🎯 Starting new MCP server...")
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


def start_demo_server_background():
    """Start MCP server in background for demo purposes."""
    import subprocess
    import time
    
    print("🔧 MCP SERVER STARTUP PROCESS")
    print("=" * 35)
    
    # Step 1: Stop any existing MCP servers
    stop_mcp_server()
    
    # Step 2: Start new MCP server
    print("🚀 Starting new MCP server...")
    
    # Use the virtual environment Python if available, otherwise python3
    python_cmd = ".venv/bin/python" if os.path.exists(".venv/bin/python") else "python3"
    server_process = subprocess.Popen(
        [python_cmd, "mcp_server.py", "sse", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Check if server is running
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.get("http://localhost:8765/health", timeout=2)
            if response.status_code == 200:
                print("✅ MCP server is running on http://localhost:8765")
                print(f"📊 Server PID: {server_process.pid}")
                return server_process
        except requests.RequestException:
            if retry < max_retries - 1:
                print(f"⏳ Retry {retry + 1}/{max_retries}...")
                time.sleep(2)
            else:
                print("⚠️  Server might still be starting... continuing anyway")
                print(f"📊 Server PID: {server_process.pid}")
                return server_process
    
    print("\n✅ MCP server startup completed!")
    print(f"🌐 Server available at: http://localhost:8765")
    print(f"📊 Process ID: {server_process.pid}")
    return server_process

if __name__ == "__main__":
    # Parse command line arguments
    transport = "sse"
    port = 8765
    host = "0.0.0.0"
    force_restart = False
    
    # Parse arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ["sse", "http", "stdio", "streamable-http"]:
            transport = args[i]
        elif args[i].isdigit():
            port = int(args[i])
        elif args[i] == "--force-restart":
            force_restart = True
        elif args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 1
        elif args[i] == "--help":
            print("🚀 MCP Server Usage:")
            print("  python mcp_server.py [transport] [port] [options]")
            print()
            print("Arguments:")
            print("  transport     Transport type: sse, http, stdio, streamable-http (default: sse)")
            print("  port          Port number (default: 8765)")
            print()
            print("Options:")
            print("  --host HOST   Host to bind to (default: 0.0.0.0)")
            print("  --force-restart  Stop existing servers and start new one")
            print("  --help        Show this help message")
            print()
            print("Examples:")
            print("  python mcp_server.py                    # Start with defaults")
            print("  python mcp_server.py sse 8080           # Start on port 8080")
            print("  python mcp_server.py --force-restart    # Force restart existing servers")
            print("  python mcp_server.py http 9000 --host localhost")
            sys.exit(0)
        i += 1
    
    print(f"🎯 MCP Server Configuration:")
    print(f"   Transport: {transport}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Force restart: {force_restart}")
    print()
    
    start_mcp_server(transport=transport, host=host, port=port, force_restart=force_restart)