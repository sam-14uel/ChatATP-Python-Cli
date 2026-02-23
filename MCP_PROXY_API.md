# ChatATP MCP Proxy Server API Documentation

## Overview

The ChatATP MCP Proxy Server exposes local MCP (Model Context Protocol) servers as REST API endpoints with optional public HTTPS access via ngrok.

## Base URL

- **Local**: `http://127.0.0.1:8001`
- **Public**: `https://your-ngrok-subdomain.ngrok-free.dev` (when ngrok enabled)

## Authentication

Currently no authentication required for the proxy endpoints.

## Endpoints

### GET /

Get server information and available endpoints.

**Response:**

```json
{
  "name": "ChatATP MCP Proxy Server",
  "version": "1.0.0",
  "scheme": "https",
  "local_url": "http://127.0.0.1:8001",
  "public_url": "https://your-ngrok-url.ngrok-free.dev",
  "servers": ["context7", "tavily-mcp", "firecrawl-mcp", "filesystem"],
  "endpoints": {
    "tools": "/tools/{server_name}/{tool_name}",
    "resources": "/resources/{server_name}/{uri}",
    "prompts": "/prompts/{server_name}",
    "servers": "/servers"
  }
}
```

### GET /servers

List all configured MCP servers with their status and capabilities.

**Response:**

```json
{
  "servers": [
    {
      "name": "context7",
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "@upstash/context7-mcp@latest"
        ]
      },
      "info": {
        "server_name": "Context7",
        "server_version": "2.1.1",
        "server_title": null,
        "capabilities": {
          "tools": true,
          "resources": false,
          "prompts": false,
          "experimental": false,
          "completions": false,
          "streaming": false
        },
        "instructions": "Use this server to retrieve up-to-date documentation and code examples for any library."
      },
      "status": "connected"
    },
    {
      "name": "tavily-mcp",
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "tavily-mcp@0.1.2"
        ],
        "env": {
          "TAVILY_API_KEY": "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"
        }
      },
      "info": {
        "server_name": "tavily-mcp",
        "server_version": "0.1.0",
        "server_title": null,
        "capabilities": {
          "tools": true,
          "resources": true,
          "prompts": true,
          "experimental": false,
          "completions": false,
          "streaming": false
        },
        "instructions": null
      },
      "status": "connected"
    },
    {
      "name": "firecrawl-mcp",
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "firecrawl-mcp"
        ],
        "env": {
          "FIRECRAWL_API_KEY": "fc-8dda7a8d648c48619f304e8adba174fb"
        }
      },
      "info": {
        "server_name": "firecrawl-fastmcp",
        "server_version": "3.0.0",
        "server_title": null,
        "capabilities": {
          "tools": true,
          "resources": false,
          "prompts": false,
          "experimental": false,
          "completions": false,
          "streaming": false
        },
        "instructions": null
      },
      "status": "connected"
    },
    {
      "name": "filesystem",
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-filesystem",
          "/Users/",
          "/Users/User/Desktop/",
          "/Users/User/Desktop/PROJECTS/"
        ]
      },
      "info": {
        "server_name": "secure-filesystem-server",
        "server_version": "0.2.0",
        "server_title": null,
        "capabilities": {
          "tools": true,
          "resources": false,
          "prompts": false,
          "experimental": false,
          "completions": false,
          "streaming": false
        },
        "instructions": null
      },
      "status": "connected"
    }
  ]
}
```

### GET /servers/{server_name}

Get detailed information about a specific MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server

**Response:**

```json
{
  "name": "tavily-mcp",
  "config": {
    "command": "npx",
    "args": [
      "-y",
      "tavily-mcp@0.1.2"
    ],
    "env": {
      "TAVILY_API_KEY": "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"
    }
  },
  "info": {
    "server_name": "tavily-mcp",
    "server_version": "0.1.0",
    "server_title": null,
    "capabilities": {
      "tools": true,
      "resources": true,
      "prompts": true,
      "experimental": false,
      "completions": false,
      "streaming": false
    },
    "instructions": null
  },
  "status": "connected"
}
```

**Error Response (404):**

```json
{
  "detail": "Server 'unknown_server' not found"
}
```

### GET /servers/{server_name}/tools

List all tools available on a specific MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server

**Response:**

```json
{
  "tools": [
    {
      "name": "read_text_file",
      "title": "Read Text File",
      "description": "Read the complete contents of a file from the file system as text. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Use the 'head' parameter to read only the first N lines of a file, or the 'tail' parameter to read only the last N lines of a file. Operates on the file as text regardless of extension. Only works within allowed directories.",
      "input_schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "path": {
            "type": "string"
          },
          "tail": {
            "description": "If provided, returns only the last N lines of the file",
            "type": "number"
          },
          "head": {
            "description": "If provided, returns only the first N lines of the file",
            "type": "number"
          }
        },
        "required": [
          "path"
        ]
      },
      "output_schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "content": {
            "type": "string"
          }
        },
        "required": [
          "content"
        ],
        "additionalProperties": false
      }
    }
  ]
}
```

### POST /tools/{server_name}/{tool_name}

Execute a tool on a specific MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server
- `tool_name` (path): Name of the tool to execute

**Request Body:**

```json
{
  "arguments": {
    "query": "search term",
    "limit": 10
  }
}
```

**Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool execution result..."
    }
  ],
  "isError": false
}
```

**Error Response (500):**

```json
{
  "detail": "Failed to call tool: [error message]"
}
```

### GET /servers/{server_name}/resources

List all resources available on a specific MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server

**Response:**

```json
{
  "resources": [
    {
      "uri": "file:///path/to/document.txt",
      "name": "document.txt",
      "description": "A text document",
      "mimeType": "text/plain"
    }
  ]
}
```

### GET /resources/{server_name}/{uri}

Read a specific resource from an MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server
- `uri` (path): URI of the resource to read

**Response:**

```json
{
  "contents": [
    {
      "uri": "file:///path/to/document.txt",
      "mimeType": "text/plain",
      "text": "Content of the document..."
    }
  ]
}
```

### GET /servers/{server_name}/prompts

List all prompts available on a specific MCP server.

**Parameters:**

- `server_name` (path): Name of the MCP server

**Response:**

```json
{
  "prompts": [
    {
      "name": "analyze_code",
      "description": "Analyze code for issues",
      "arguments": [
        {
          "name": "language",
          "description": "Programming language",
          "required": true
        }
      ]
    }
  ]
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

- **404 Not Found**: Server or resource not found
- **500 Internal Server Error**: Server execution error

Error response format:

```json
{
  "detail": "Error description"
}
```

## MCP Server Configuration

MCP servers are configured in JSON files. The proxy automatically discovers and loads configurations from:

- `~/mcp.json`
- `~/mcp_config.json`
- `~/.chatatp/mcp.json`
- `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- `~/AppData/Roaming/Claude/claude_desktop_config.json` (Windows)

Example configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/allowed/path"],
      "env": {}
    },
    "tavily-mcp": {
      "command": "npx",
      "args": ["tavily-mcp@0.1.2"],
      "env": {
        "TAVILY_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Usage Examples

### Calling a Tool

```bash
curl -X POST "https://your-proxy-url.ngrok-free.dev/tools/filesystem/list_dir" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"path": "/tmp"}}'
```

### Reading a Resource

```bash
curl "https://your-proxy-url.ngrok-free.dev/resources/filesystem/file:///etc/hostname"
```

### Listing Server Tools

```bash
curl "https://your-proxy-url.ngrok-free.dev/servers/filesystem/tools"
```

## Background Operation

When auto-start is enabled, the proxy server runs in the background automatically when any CLI command is executed. The server shuts down when the CLI process terminates.

To manually control the proxy:

- `chatatp mcp proxy --ngrok --ngrok-token TOKEN` - Start manually
- `chatatp config enable-proxy-auto-start --ngrok-token TOKEN` - Enable auto-start
- `chatatp config disable-proxy-auto-start` - Disable auto-start
- `chatatp config proxy-status` - Check status
