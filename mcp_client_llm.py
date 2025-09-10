# MCP Client with Groq LLM Layer
import asyncio
import os
from groq import Groq
from fastmcp import Client as MCPClient

# --- LLM Configuration ---
# Ensure the GROQ_API_KEY is set as an environment variable
if not os.environ.get("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable not set!")

groq_client = Groq()

# Define the tools the LLM can use, matching the server's tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get basic system information from the MCP server.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

async def run_llm_interaction():
    """
    Runs the full Model-Context-Protocol interaction.
    """
    # 1. Model: Ask the LLM a question
    user_prompt = "What is the system info?"
    print(f"-> User Prompt: {user_prompt}")

    # Initialize context object
    context = {
        "user_input": user_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
        "tool_results": {},
        "metadata": {"session_id": os.urandom(4).hex()},
    }

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=context["messages"],
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    response_message = response.choices[0].message

    # 2. Protocol: Check if the model wants to call a tool
    if not response_message.tool_calls:
        print(f"<- LLM Response: {response_message.content}")
        return

    print("-> LLM decided to call a tool.")
    context["messages"].append({"role": "assistant", "content": response_message.content or "", "tool_calls": getattr(response_message, "tool_calls", None)})

    # 3. Context: Execute the tool call using the MCP client
    mcp_client = MCPClient("mcp_server.py")
    async with mcp_client:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            if function_name == "get_system_info":
                print(f"-> Calling tool '{function_name}' on MCP Server...")
                tool_result = await mcp_client.call_tool(function_name, {})
                print(f"<- Tool responded: {tool_result.structured_content}")
                # Store tool result in context
                context["tool_results"][function_name] = tool_result.structured_content
                # Append the tool's response to the message history
                context["messages"].append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_result.structured_content),
                    }
                )

    # 4. Model: Send the tool's output back to the LLM for a final answer
    print("-> Sending tool result back to LLM for final response...")
    final_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=context["messages"],
        temperature=0,
    )
    print(f"<- Final LLM Response: {final_response.choices[0].message.content}")


async def main():
    """
    Main asynchronous function.
    """
    await run_llm_interaction()

if __name__ == "__main__":
    asyncio.run(main())