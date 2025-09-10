# Minimal MCP Server using fastmcp
from fastmcp import FastMCP

mcp = FastMCP(name="MyMCPServer")

@mcp.tool
def get_system_info() -> dict:
    """Get basic system information."""
    return {"hostname": "mcp-server", "os": "Linux", "note": "fastmcp response"}

if __name__ == "__main__":
    mcp.run()