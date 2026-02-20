"""
MCP Client Manager for ChatATP CLI
Handles creation and management of MCP clients for local MCP server connections
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, List
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport, StdioTransport, SSETransport
from fastmcp.exceptions import ToolError

logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    Manages MCP clients for local MCP server connections.
    Each server config gets its own configured client instance.
    """

    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._active_contexts: Dict[str, Any] = {}
        self._server_configs: Dict[str, Dict[str, Any]] = {}

    def load_server_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load MCP server configurations from various config files.

        Looks for:
        - mcp.json
        - mcp_config.json
        - mcp_server.json
        - claude_desktop_config.json (Claude format)
        """
        configs = {}

        # Possible config file locations
        config_paths = [
            Path.home() / 'mcp.json',
            Path.home() / 'mcp_config.json',
            Path.home() / '.chatatp' / 'mcp.json',
            Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json',  # macOS
            Path.home() / 'AppData' / 'Roaming' / 'Claude' / 'claude_desktop_config.json',  # Windows
            Path.home() / '.cursor' / 'mcp.json',  # Cursor
            Path.home() / '.gemini' / 'antigravity' / 'mcp_server.json',  # Gemini
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        data = json.load(f)

                    # Handle different config formats
                    if 'mcpServers' in data:
                        # Claude desktop config format
                        for server_name, server_config in data['mcpServers'].items():
                            configs[server_name] = server_config
                    elif isinstance(data, dict):
                        # Direct server configs (check for both mcpServers and direct format)
                        if 'mcpServers' in data:
                            for server_name, server_config in data['mcpServers'].items():
                                configs[server_name] = server_config
                        else:
                            # Direct server configs
                            for server_name, server_config in data.items():
                                if isinstance(server_config, dict):
                                    configs[server_name] = server_config

                    logger.info(f"Loaded MCP configs from {config_path}")

                except Exception as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")

        # Also check for .chatatp directory and create if it doesn't exist
        chatatp_dir = Path.home() / '.chatatp'
        chatatp_dir.mkdir(exist_ok=True)

        # Create default mcp.json in .chatatp if it doesn't exist and no configs found
        chatatp_mcp_file = chatatp_dir / 'mcp.json'
        if not configs and not chatatp_mcp_file.exists():
            try:
                default_config = {}
                with open(chatatp_mcp_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default MCP config at {chatatp_mcp_file}")
            except Exception as e:
                logger.warning(f"Failed to create default config: {e}")

        self._server_configs = configs
        return configs

    def get_available_servers(self) -> List[str]:
        """Get list of available server names"""
        return list(self._server_configs.keys())

    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server"""
        return self._server_configs.get(server_name)

    async def get_client(self, server_name: str) -> Client:
        """
        Get or create a client for the specified server.

        Args:
            server_name: Name of the MCP server

        Returns:
            Client instance
        """
        if server_name not in self._server_configs:
            raise ValueError(f"MCP server '{server_name}' not found in configuration")

        # Return existing client if already connected
        if server_name in self._clients:
            if server_name in self._active_contexts:
                return self._clients[server_name]
            else:
                # Client exists but is not connected
                async with self._clients[server_name] as context:
                    self._active_contexts[server_name] = context
                return self._clients[server_name]

        # Create and connect a new client
        client = await self._create_client(server_name)
        async with client as context:
            self._clients[server_name] = client
            self._active_contexts[server_name] = context

        return client

    async def _create_client(self, server_name: str) -> Client:
        """Create a client instance for the given server"""
        config = self._server_configs[server_name]

        # Determine transport type
        transport_type = config.get('transport', 'stdio').lower()

        if transport_type in ["stdio", "STDIO"]:
            transport = StdioTransport(
                command=config.get('command', 'npx'),
                args=config.get('args', []),
                env=config.get('env', {}),
            )
        elif transport_type in ["sse", "SSE"]:
            transport = SSETransport(
                url=config.get('url', ''),
                headers=config.get('headers', {})
            )
        elif transport_type in ["http", "https", "HTTP", "HTTPS"]:
            transport = StreamableHttpTransport(
                url=config.get('url', ''),
                headers=config.get('headers', {})
            )
        else:
            # Default to stdio for backwards compatibility
            transport = StdioTransport(
                command=config.get('command', 'npx'),
                args=config.get('args', []),
                env=config.get('env', {}),
            )

        client = Client(transport)
        logger.info(f"Created MCP client for server '{server_name}'")

        return client

    async def initialize_client(self, server_name: str) -> Dict[str, Any]:
        """
        Initialize a client connection and perform handshake.

        Args:
            server_name: Name of the MCP server

        Returns:
            Dictionary with initialization results
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                # Server info is available after entering context
                return {
                    "server_name": getattr(client.initialize_result.serverInfo, 'name', server_name) if hasattr(client, 'initialize_result') else server_name,
                    "server_version": getattr(client.initialize_result.serverInfo, 'version', 'unknown') if hasattr(client, 'initialize_result') else 'unknown',
                    "server_title": getattr(client.initialize_result.serverInfo, 'title', server_name) if hasattr(client, 'initialize_result') else server_name,
                    "capabilities": {
                        "tools": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.tools is not None,
                        "resources": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.resources is not None,
                        "prompts": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.prompts is not None,
                        "experimental": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.experimental is not None,
                        "completions": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.completions is not None,
                        "streaming": hasattr(client, 'initialize_result') and client.initialize_result.capabilities.tasks is not None
                    },
                    "instructions": getattr(client.initialize_result, 'instructions', '') if hasattr(client, 'initialize_result') else ''
                }

            except Exception as e:
                logger.error(f"Failed to initialize client for {server_name}: {e}")
                raise

    async def close_client(self, server_name: str):
        """
        Close a client connection and clean up resources.

        Args:
            server_name: Name of the MCP server
        """
        if server_name in self._active_contexts:
            try:
                client = self._clients.get(server_name)
                if client:
                    await client.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing client {server_name}: {e}")
            finally:
                del self._active_contexts[server_name]
                if server_name in self._clients:
                    del self._clients[server_name]

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List all available tools for a server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool definitions
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                tools_result = await client.list_tools()

                # Convert to dictionary format
                tools = []
                for tool in tools_result:
                    tools.append({
                        "name": tool.name,
                        "title": tool.title if hasattr(tool, 'title') and tool.title else tool.name,
                        "description": getattr(tool, 'description', ''),
                        "input_schema": getattr(tool, 'inputSchema', {}),
                        "output_schema": getattr(tool, 'outputSchema', {})
                    })

                return tools

            except Exception as e:
                logger.error(f"Failed to list tools for {server_name}: {e}")
                raise

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: Optional[float] = None,
        raise_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
            timeout: Optional timeout in seconds
            raise_on_error: Whether to raise exception on tool error

        Returns:
            Dictionary with tool results
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                result = await client.call_tool(
                    name=tool_name,
                    arguments=arguments,
                    timeout=timeout,
                    raise_on_error=raise_on_error
                )

                # Return structured response
                response = {
                    "success": not result.is_error,
                    "data": result.data,
                    "structured_content": getattr(result, 'structured_content', []),
                    "content": [],
                    "meta": getattr(result, "_meta", {})
                }

                # Add content blocks
                for content_block in result.content:
                    if hasattr(content_block, 'text'):
                        response["content"].append({
                            "type": "text",
                            "text": content_block.text
                        })
                    elif hasattr(content_block, 'data'):
                        response["content"].append({
                            "type": "image",
                            "data": content_block.data,
                            "mimeType": content_block.mimeType
                        })

                return response

            except ToolError as e:
                logger.error(f"Tool error for {server_name}.{tool_name}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "data": None,
                    "content": []
                }

            except Exception as e:
                logger.error(f"Failed to call tool {tool_name} for {server_name}: {e}")
                raise

    async def list_resources(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List all available resources for a server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of resource definitions
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                resources_result = await client.list_resources()

                # Convert to dictionary format
                resources = []
                for resource in resources_result:
                    resources.append({
                        "uri": resource.uri,
                        "name": resource.name,
                        "description": getattr(resource, 'description', ''),
                        "mimeType": getattr(resource, 'mimeType', None),
                    })

                return resources

            except Exception as e:
                logger.error(f"Failed to list resources for {server_name}: {e}")
                raise

    async def read_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """
        Read a resource from the MCP server.

        Args:
            server_name: Name of the MCP server
            uri: URI of the resource to read

        Returns:
            Dictionary with resource content
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                contents = await client.read_resource(uri)

                # Convert to dictionary format
                response = {
                    "uri": uri,
                    "content": []
                }

                for content in contents:
                    if hasattr(content, 'text'):
                        response["content"].append({
                            "type": "text",
                            "text": content.text,
                            "uri": getattr(content, 'uri', uri),
                            "mimeType": getattr(content, 'mimeType', None)
                        })
                    elif hasattr(content, 'blob'):
                        response["content"].append({
                            "type": "blob",
                            "blob": content.blob,
                            "uri": getattr(content, 'uri', uri),
                            "mimeType": content.mimeType
                        })

                return response

            except Exception as e:
                logger.error(f"Failed to read resource {uri} for {server_name}: {e}")
                raise

    async def list_prompts(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List all available prompts for a server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of prompt definitions
        """
        client = await self._create_client(server_name)

        async with client:
            try:
                prompts_result = await client.list_prompts()

                # Convert to dictionary format
                prompts = []
                for prompt in prompts_result:
                    prompts.append({
                        "name": prompt.name,
                        "description": getattr(prompt, 'description', ''),
                        "arguments": [
                            {
                                "name": arg.name,
                                "description": getattr(arg, 'description', ''),
                                "required": getattr(arg, 'required', False)
                            }
                            for arg in (getattr(prompt, 'arguments', []) or [])
                        ]
                    })

                return prompts

            except Exception as e:
                logger.error(f"Failed to list prompts for {server_name}: {e}")
                raise

    async def cleanup_all(self):
        """
        Close all active client connections.
        """
        for server_name in list(self._active_contexts.keys()):
            try:
                client = self._clients.get(server_name)
                if client:
                    await client.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error cleaning up client {server_name}: {e}")

        self._clients.clear()
        self._active_contexts.clear()


# Global singleton instance
mcp_client_manager = MCPClientManager()
