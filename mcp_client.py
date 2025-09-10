# Minimal MCP Client using fastmcp
import asyncio
from fastmcp import Client

async def main():
    """
    An asynchronous function to connect to the MCP server and call a tool.
    """
    client = Client("mcp_server.py")

    async with client:
        print("Connecting to server and calling 'get_system_info' tool...")

        result = await client.call_tool("get_system_info", {})

        print(f"Server responded: {result.structured_content}")

if __name__ == "__main__":
    asyncio.run(main())
