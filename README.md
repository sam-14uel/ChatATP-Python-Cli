# ChatATP CLI

```text
 ██████╗██╗  ██╗ █████╗ ████████╗ █████╗ ████████╗██████╗ 
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
██║     ███████║███████║   ██║   ███████║   ██║   ██████╔╝
██║     ██╔══██║██╔══██║   ██║   ██╔══██║   ██║   ██╔═══╝ 
╚██████╗██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ██║     
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝     
```

A powerful terminal interface for the ChatATP API, built with Python. Interact with ChatATP's AI models, manage chatrooms, toolkits, integrations, and more directly from your command line.

## ✨ What's New (v1.0.7)

### 🚀 Agentic Loop Support
- **Interactive Conversations**: Back-and-forth chat with persistent context
- **Real-time Streaming**: Responses appear as they're generated with tool call visualization
- **Auto-enter Chatrooms**: `chat new` now creates AND enters chat automatically
- **In-chat Commands**: Rich command system during conversations (`/exit`, `/help`, `/clear`, `/history`)

### 🔄 Chat Evolution
- **Before**: One-shot messages that exit immediately
- **Now**: Persistent interactive sessions with agentic conversations
- **Streaming**: Tool calls, thinking blocks, and responses all visualized in real-time

## Features

- **Account Management**: View your ChatATP account information
- **Model Management**: List and manage AI models
- **Interactive Chat**: Agentic loop support with back-and-forth conversations
- **Toolkit Management**: Browse and manage your toolkits and collections
- **Integration Management**: Manage OAuth and custom integrations
- **AI Configuration**: Configure AI providers, models, and settings
- **Media Management**: Browse and manage uploaded media files
- **Store Access**: Browse featured, popular, and recommended toolkits
- **MCP Support**: Manage MCP servers and connections

## Installation

### From PyPI (Recommended)

```bash
pip install chatatp-cli
```

### From Source

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the script executable (optional):
   ```bash
   chmod +x main.py
   ```

## Quick Start

When you run the CLI, you'll see the beautiful ASCII banner:

```text
 ██████╗██╗  ██╗ █████╗ ████████╗ █████╗ ████████╗██████╗ 
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
██║     ███████║███████║   ██║   ███████║   ██║   ██████╔╝
██║     ██╔══██║██╔══██║   ██║   ██╔══██║   ██║   ██╔═══╝ 
╚██████╗██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ██║     
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝     
```

Then get help with:

```bash
chatatp --help
# or
python main.py --help

## Configuration

Before using the CLI, you need to configure your API token:

```bash
chatatp config set-token YOUR_API_TOKEN_HERE
```

You can also configure other settings:

```bash
# Set custom API base URL (default: https://api.chat-atp.com)
chatatp config set-base-url https://your-custom-api-url.com

# Set default model
chatatp config set-default-model gpt-oss-120b

# View current configuration
chatatp config show
```

## 🔔 Desktop Notifications

The ChatATP CLI now supports **cross-platform desktop notifications** with sound alerts! Get notified when AI starts responding, without keeping your terminal window focused.

### ✅ Cross-Platform Support

Works on **any operating system**:
- **Windows**: Native toast notifications + system sounds
- **macOS**: Native notifications + system sounds  
- **Linux**: System tray notifications + audio playback
- **Fallback**: System bell on unsupported systems

### 🔊 Notification Triggers

- **🤖 AI Response Start**: Desktop notification when AI begins typing/responding
- **🔧 Tool Completion**: Optional notifications for tool execution results
- **❌ Error Alerts**: Sound notifications for connection issues

### ⚙️ Configuration

```bash
# Enable desktop notifications
chatatp config enable-notifications

# Disable desktop notifications  
chatatp config disable-notifications

# Enable sound alerts (with notifications)
chatatp config enable-sound

# Disable sound alerts
chatatp config disable-sound
```

### 📱 Notification Experience

When chatting interactively:

```bash
$ chatatp chat new "Tell me about AI"

Chatroom created: abc123
Entered chatroom: abc123
Type your message or '/exit' to quit, '/help' for commands

You: Tell me about AI

# 🔔 Desktop notification appears: "ChatATP is thinking..."
# 🔊 Sound plays (if enabled)
# 💻 Terminal shows response as it streams

ChatATP ·

AI, or Artificial Intelligence, refers to the simulation of human intelligence...
```

### 🔇 Privacy & Control

- **Opt-in by default**: Notifications disabled until you enable them
- **Sound optional**: Enable notifications without sound, or both together
- **Non-intrusive**: Only triggers on AI responses, not every message
- **Cross-platform**: Same experience regardless of your OS

### 🛠️ Technical Details

- Uses `plyer` library for cross-platform compatibility
- Sound support via system audio (Windows/macOS/Linux)
- Fallback to terminal bell if audio unavailable
- No external dependencies for basic notifications
- Configuration persists across sessions

## Usage

### Getting Help

```bash
chatatp --help
```

### Account Information

```bash
chatatp account
```

### Models

```bash
# List available models
chatatp models

# List models for a specific provider
chatatp ai provider-models PROVIDER_ID
```

## 🎯 Interactive Chat System

The ChatATP CLI now supports **true agentic conversations** with persistent context, just like chatting with ChatGPT or Claude!

### New Interactive Commands

#### **Start New Interactive Chat**
```bash
chatatp chat new "Tell me about machine learning"
```
- Creates a new chatroom
- Automatically enters interactive mode
- Sends your initial message
- Starts back-and-forth conversation loop

#### **Enter Existing Chatroom**
```bash
chatatp chat converse ROOM_ID
```
- Enter any existing chatroom for interactive chat
- Continue conversations where you left off
- Same interactive experience as new chats

### In-Chat Commands

While in interactive mode, you have access to these commands:

- **`/exit`**, **`/quit`**, **`/q`** - Exit the current chat session
- **`/help`**, **`/h`** - Show available commands
- **`/clear`** - Clear the screen and show current chat info
- **`/history`** - Show recent messages from chat history

### Interactive Chat Flow

```
$ chatatp chat new "Hello, let's discuss AI"

Chatroom created: abc123
Entered chatroom: abc123
Type your message or '/exit' to quit, '/help' for commands

You: Hello, let's discuss AI

ChatATP ·

Hello! I'd be happy to discuss AI with you. What specific aspects of artificial intelligence are you interested in? Whether it's machine learning algorithms, current trends, ethical considerations, or practical applications, I'm here to help!

─────────────────────────────────
You: Tell me about neural networks

ChatATP ·

Neural networks are fascinating! Let me explain them step by step:

A neural network is a computational model inspired by the human brain's neural structure. It consists of interconnected nodes (neurons) organized in layers...

─────────────────────────────────
You: /help

Available commands:
  /exit, /quit, /q  - Exit the chat
  /help, /h         - Show this help
  /clear             - Clear the screen
  /history           - Show chat history

You: /exit
Exiting chat...
```

### Legacy Commands (Still Supported)

#### **One-shot Message Sending**

```bash
# Send single message (legacy - exits immediately)
chatatp chat send ROOM_ID "Your message here"

# Send with specific model and toolkits
chatatp chat send ROOM_ID "Analyze this data" --model gpt-oss-120b --toolkits TOOLKIT_ID1 TOOLKIT_ID2

# Debug mode to see raw chunks
chatatp chat send ROOM_ID "Debug message" --debug
```

#### **Chatroom Management**

```bash
# List your chatrooms
chatatp chat rooms

# Show details of a specific chatroom
chatatp chat show ROOM_ID
```

### Toolkits

```bash
# List your toolkits
chatatp toolkits

# Browse featured toolkits
chatatp store featured

# Browse popular toolkits
chatatp store popular

# Browse recommended toolkits
chatatp store recommended
```

### Integrations

```bash
# List OAuth integrations
chatatp integrations list

# List custom integrations
chatatp integrations custom
```

### MCP Management

```bash
# List MCP connections
chatatp mcp connections

# List MCP servers
chatatp mcp servers
```

### 🔧 Local MCP Client

ChatATP CLI now includes a **built-in MCP (Model Context Protocol) client** that can directly connect to local MCP servers configured in standard config files. This allows you to use MCP tools, resources, and prompts directly from your terminal without going through the ChatATP API.

### 📁 Supported Configuration Files

The MCP client automatically discovers and loads configurations from:

- `~/mcp.json` - Standard MCP configuration
- `~/mcp_config.json` - Alternative config format
- `~/.chatatp/mcp.json` - ChatATP-specific config (auto-created)
- `~/Library/Application Support/Claude/claude_desktop_config.json` - macOS Claude config
- `~/AppData/Roaming/Claude/claude_desktop_config.json` - Windows Claude config
- `~/.cursor/mcp.json` - Cursor editor config
- `~/.gemini/antigravity/mcp_server.json` - Gemini config

### 📋 Configuration Format

Create an `mcp.json` file in your home directory:

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp@latest"]
  },
  "tavily-search": {
    "command": "npx",
    "args": ["-y", "tavily-mcp@0.1.2"],
    "env": {
      "TAVILY_API_KEY": "your-api-key-here"
    }
  },
  "my-custom-server": {
    "command": "python",
    "args": ["-m", "my_mcp_server"],
    "env": {
      "CUSTOM_ENV_VAR": "value"
    }
  }
}
```

### 🚀 Local MCP Commands

#### **List Configured Servers**

```bash
chatatp mcp local-servers
```

#### **Connect to a Server**

```bash
chatatp mcp local-connect context7
```

Shows server capabilities, version info, and available features.

#### **List Available Tools**

```bash
chatatp mcp local-tools context7
```

#### **Call a Tool**

```bash
# Call a tool with JSON arguments
chatatp mcp local-call-tool context7 search_web --args '{"query": "latest AI news"}'

# Call without arguments
chatatp mcp local-call-tool context7 get_weather --args '{}'
```

#### **List Resources**

```bash
chatatp mcp local-resources context7
```

#### **Read a Resource**

```bash
chatatp mcp local-read-resource context7 file:///path/to/resource
```

#### **List Prompts**

```bash
chatatp mcp local-prompts context7
```

### 💡 Example Usage

```bash
# First, create a config file
echo '{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp@latest"]
  }
}' > ~/mcp.json

# List configured servers
$ chatatp mcp local-servers

Local MCP Servers (1 configured)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name       ┃ Command    ┃ Transport  ┃ URL/Args                     ┃
├────────────┼────────────┼────────────┼─────────────────────────────┤
┃ context7   ┃ npx        ┃ STDIO      ┃ -y @upstash/context7-mcp@latest ┃
└────────────┴────────────┴────────────┴─────────────────────────────┘

# Connect and explore
$ chatatp mcp local-connect context7

Connected to context7
─────────────────────
Server: Context7 MCP Server
Version: 1.0.0
Title: Context7
Capabilities:
  • tools: ✓
  • resources: ✗
  • prompts: ✗
  • experimental: ✗
  • completions: ✗
  • streaming: ✗

# List tools
$ chatatp mcp local-tools context7

Tools on context7
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                          ┃ Title                          ┃ Description                   ┃
├───────────────────────────────┼────────────────────────────────┼───────────────────────────────┤
┃ search_web                    ┃ Web Search                     ┃ Search the web for information ┃
┃ get_page_content              ┃ Get Page Content              ┃ Get content from a web page   ┃
└───────────────────────────────┴────────────────────────────────┴───────────────────────────────┘

# Call a tool
$ chatatp mcp local-call-tool context7 search_web --args '{"query": "latest AI developments"}'

Tool executed successfully
Content:
# AI Developments 2024

Recent advancements in artificial intelligence include...

[Results continue...]
```

### 🔧 Transport Types

The MCP client supports all standard MCP transport types:

- **STDIO**: Command-line tools that communicate via stdin/stdout
- **HTTP**: Web-based MCP servers
- **SSE**: Server-sent events for streaming responses

### 🛡️ Security & Isolation

- **No API Keys Required**: Direct local connections to your MCP servers
- **Environment Variables**: Securely pass credentials via `env` config
- **Process Isolation**: Each MCP server runs in its own process
- **No Data Leakage**: All communication stays local unless using remote servers

### 🔗 Integration with ChatATP

While the local MCP client works independently, you can also use MCP connections through ChatATP's API for cloud-hosted MCP servers. The local client provides direct access for local development and testing.

### 🐛 Troubleshooting

**Server not found**: Ensure your config file exists and is properly formatted
**Connection failed**: Check that the MCP server command is installed and available
**Tool errors**: Verify tool arguments match the expected schema from `local-tools`

## AI Management

```bash
# List AI providers
chatatp ai providers

# List AI configurations
chatatp ai configs

# Show AI settings
chatatp ai settings
```

### Media

```bash
# List your media files
chatatp media

# Search media
chatatp media --search "document name"

# Filter by type
chatatp media --type image

# Pagination
chatatp media --page 2 --page-size 20
```

### Pricing

```bash
# View pricing plans
chatatp pricing
```

## Authentication

All commands require authentication. Make sure you've set your API token using:

```bash
chatatp config set-token YOUR_TOKEN
```

The token will be stored securely in your home directory under `~/.chatatp/config.yaml`.

## Advanced Features

### Real-time Streaming with Tool Visualization

The CLI now provides rich visualization of:

- **Tool Calls**: See when tools are being executed with timing
- **Thinking Blocks**: Visual indicators when AI is reasoning
- **Progress Indicators**: Spinners and status updates during processing
- **Error Handling**: Graceful handling of network issues and API errors

### Example with Tool Calls

```
You: Search for information about OpenClaw AI

ChatATP ·

I need to search for information about OpenClaw AI. Let me use the search tool.

  ┌ search_web · web_search_toolkit
  └ done 0.34s

Based on my search, OpenClaw is...
```

### Interactive vs One-shot Mode Comparison

| Feature | Interactive Mode (`chat new/converse`) | One-shot Mode (`chat send`) |
|---------|----------------------------------------|----------------------------|
| **Persistence** | ✅ Back-and-forth conversation | ❌ Single message only |
| **Context** | ✅ Full conversation history | ❌ No context retention |
| **Commands** | ✅ Rich in-chat commands | ❌ None |
| **Tool Visualization** | ✅ Real-time with progress | ✅ Basic streaming |
| **Exit Behavior** | Manual exit with `/exit` | Auto-exit after response |
| **Use Case** | Deep conversations, exploration | Quick questions, automation |

## Error Handling

The CLI provides clear error messages for common issues:
- Missing API token
- Invalid room IDs
- Network errors
- Authentication failures
- Streaming interruptions

## Dependencies

- requests: HTTP client
- click: Command line interface
- rich: Beautiful terminal output with progress indicators
- pyyaml: Configuration file handling
- python-dotenv: Environment variable support

## Migration Guide

### From v1.x to v2.0

**Old workflow:**
```bash
# Create room
chatatp chat new "Hello"
# Copy room ID
# Send messages one by one
chatatp chat send ROOM_ID "Follow up question"
chatatp chat send ROOM_ID "Another question"
```

**New workflow:**
```bash
# Single command starts interactive session
chatatp chat new "Hello, let's have a conversation"
# Now chat back and forth naturally!
# Type /exit when done
```

**Legacy commands still work:** All v1.x commands (`chat send`, etc.) remain fully functional for scripts and automation.

## Contributing

Feel free to submit issues and pull requests to improve the ChatATP CLI.

## License

This project is licensed under the MIT License.
