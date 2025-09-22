# MCP vs Function Calling Demo

**Thesis:** "MCP server ≠ Function Calling and is NOT only used in case of AI"

This demo suite demonstrates the key differences between MCP (Model Context Protocol) and traditional function calling, showing that MCP provides much more than just AI function calling capabilities.

## 🚀 Quick Start

### Option 1: Interactive Demo Runner (Recommended)
```bash
.venv/bin/python demo_runner.py
```
This provides an interactive menu to run all demos in the correct order.

### Option 2: Run Individual Modules

1. **Start MCP Server:**
```bash
# Method 1: Direct start (foreground)
.venv/bin/python mcp_server.py sse 8765

# Method 2: Background with logging
nohup .venv/bin/python mcp_server.py sse 8765 > server.log 2>&1 &

# Method 3: Using demo runner
.venv/bin/python demo_runner.py  # Then select option 1
```

2. **Simple MCP Client (Complete Features):**
```bash
.venv/bin/python simple_mcp_client.py
```

3. **AI + MCP Integration Demo:**
```bash
export GROQ_API_KEY=your_api_key_here  # Required for AI demos
.venv/bin/python ai_mcp_client.py
```

4. **Traditional Function Calling Demo:**
```bash
export GROQ_API_KEY=your_api_key_here  # Optional, will simulate if not set
.venv/bin/python function_calling_client.py
```

5. **Stop Server:**
```bash
.venv/bin/python -c "from mcp_server import stop_mcp_server; stop_mcp_server()"
```

## 📁 Project Structure

```
mcp_usage_demo/
├── demo_runner.py              # Interactive demo runner
├── mcp_server.py              # MCP server with tools, resources, prompts
├── simple_mcp_client.py       # Complete MCP client demo (tools, resources, prompts)
├── ai_mcp_client.py           # AI + MCP integration demo
├── function_calling_client.py # Traditional function calling demo
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Demo Modules Explained

### 1. Simple MCP Client (`simple_mcp_client.py`)
- **Purpose:** Complete MCP protocol demonstration for non-AI applications
- **Demonstrates:** All core MCP features without requiring AI
- **Key Features:**
  - Tool discovery and execution
  - Resource content reading (documentation, config, data)
  - Prompt template generation
  - Server connectivity and health checks
  - Protocol-level features (connection management)
  - Cross-language compatibility
- **No AI Required:** Pure MCP protocol usage

### 2. AI + MCP Integration (`ai_mcp_client.py`)
- **Purpose:** Show AI using MCP protocol for tool selection
- **Demonstrates:** LLM + MCP integration
- **Key Features:**
  - LLM discovers tools via MCP
  - AI chooses appropriate tools
  - Network-based tool execution
  - Works with any MCP server

### 3. Traditional Function Calling (`function_calling_client.py`)
- **Purpose:** Traditional function calling for comparison
- **Demonstrates:** How function calling typically works
- **Key Features:**
  - LLM choosing from predefined functions
  - Direct in-process function execution
  - Same functions as MCP server, but called directly

### 5. Demo Runner (`demo_runner.py`)
- **Purpose:** Orchestrate all demos with easy menu interface
- **Features:**
  - Interactive menu system
  - Server management (start/stop)
  - Sequential demo execution
  - Environment checking

## 🔑 Key Differences Demonstrated

| Aspect | MCP Protocol | Function Calling |
|--------|-------------|------------------|
| **Communication** | Network-based (HTTP/SSE/WS) | In-process direct calls |
| **Discovery** | Dynamic via protocol | Static schemas |
| **AI Integration** | LLM + dynamic MCP tools | LLM + static function schemas |
| **Language Support** | Language agnostic | Language dependent |
| **Scalability** | Multi-client, distributed | Single application |
| **Use Cases** | Universal tool sharing | AI-specific functionality |
| **Resources** | Built-in resource system | Not available |
| **Prompts** | Template system | Not available |
| **Health Checks** | Built-in monitoring | Not available |

## 🎓 Learning Outcomes

After running these demos, you'll understand:

1. **MCP ≠ Function Calling** - They serve different purposes
2. **MCP is NOT AI-only** - Non-AI apps can use MCP tools
3. **Universal Tool Sharing** - MCP enables cross-language tool access
4. **Rich Protocol Features** - Resources, prompts, health checks, etc.
5. **Dynamic Discovery** - Tools/resources discovered at runtime
6. **Standardized Approach** - Consistent across different implementations

## 🛠️ Prerequisites

- Python 3.8+
- Required packages: `pip install -r requirements.txt`
- Optional: Groq API key for real LLM calls (simulates without it)

## 🚀 Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
export GROQ_API_KEY=your_groq_api_key_here

# Run interactive demo
.venv/bin/python demo_runner.py
```

## 🎯 Recommended Demo Flow

1. **Start with Simple MCP Demo** - See non-AI MCP usage
2. **Run AI + MCP Demo** - See LLM + MCP integration  
3. **Run Function Calling Demo** - Compare with traditional approach
4. **Explore Advanced Features** - See unique MCP capabilities
5. **Compare Results** - Understand the key differences

## 🤝 Interactive Usage

The demo modules are designed for interactive exploration:

- Run in IPython/Jupyter for step-by-step execution
- Modify parameters to see different behaviors
- Experiment with different tool combinations
- Add your own tools to the MCP server

## 🔧 Extending the Demos

- **Add Tools:** Modify `mcp_server.py` with new `@mcp.tool` functions
- **Add Resources:** Add new `@mcp.resource` endpoints
- **Add Prompts:** Create new `@mcp.prompt` templates
- **Custom Clients:** Create new client demos using `fastmcp.Client`

## 📝 Notes

- Server runs on `localhost:8765` by default
- Demos include error handling and fallback modes
- All demos can run without external API keys (simulation mode)
- MCP server supports multiple transport types (SSE, HTTP, STDIO)

## 🎉 Conclusion

These demos prove that **MCP provides a standardized protocol for tool sharing that goes far beyond traditional function calling**, enabling universal tool access across applications, languages, and use cases - not just AI!