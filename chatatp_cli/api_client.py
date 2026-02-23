import requests
from typing import Dict, List, Optional, Any
import json
from .config import Config
import asyncio

class ChatATPAPI:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request"""
        url = f"{self.config.api_base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request"""
        url = f"{self.config.api_base_url}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make PATCH request"""
        url = f"{self.config.api_base_url}{endpoint}"
        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str) -> Dict:
        """Make DELETE request"""
        url = f"{self.config.api_base_url}{endpoint}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json() if response.content else {}

    # Account endpoints
    def get_account(self) -> Dict:
        """Get user account information"""
        return self._get('/api/v1/account/')

    # Models endpoints
    def list_models(self) -> List[Dict]:
        """List available models"""
        return self._get('/api/v1/list-models/')

    # Collections/Toolkits endpoints
    def list_collections(self) -> Dict:
        """List toolkits collections"""
        return self._get('/api/v1/collections/toolkits/')

    # MCP endpoints
    def list_mcp_connections(self) -> Dict:
        """List MCP connections"""
        return self._get('/api/v1/mcp/connections/')

    def list_mcp_servers(self) -> Dict:
        """List MCP servers"""
        return self._get('/api/v1/mcp/servers/')

    def register_proxy(self, proxy_url: str, servers: List[str]) -> Dict:
        """Register MCP proxy server with ChatATP API"""
        data = {
            "proxy_url": proxy_url,
            "servers": servers
        }
        return self._post('/api/v1/mcp/device/register-proxy/', data)

    def unregister_proxy(self) -> Dict:
        """Unregister MCP proxy server from ChatATP API"""
        return self._delete('/api/v1/mcp/device/unregister-proxy/')

    # Chat endpoints
    def list_chatrooms(self) -> Dict:
        """List chatrooms"""
        return self._get('/api/v1/chatrooms/')

    def get_chatroom(self, room_id: str) -> Dict:
        """Get chatroom details"""
        return self._get(f'/api/v1/chats/{room_id}/')

    def create_chatroom(self, message: str, model: str = None, toolkit_ids: List[str] = None,
                       mcp_server_connection_ids: List[str] = None) -> Dict:
        """Create new chatroom"""
        data = {'message': message}
        if model:
            data['model'] = model
        if toolkit_ids:
            data['toolkit_ids'] = toolkit_ids
        if mcp_server_connection_ids:
            data['mcp_server_connection_ids'] = mcp_server_connection_ids
        return self._post('/api/v1/chats/new/', data)

    def send_chat_message_stream(self, room_id: str, message: str, model: str = None,
                               toolkit_ids: List[str] = None, mcp_server_connection_ids: List[str] = None,
                               attachments: List = None, agent_mode: bool = False):
        """Send chat message and yield streaming response chunks"""
        url = f"{self.config.api_base_url}/api/v1/chats/{room_id}/completions/stream/"
        data = {
            'message_type': 'chat_message',
            'message': message,
            'model': model or self.config.default_model,
            'toolkit_ids': toolkit_ids or [],
            'mcp_server_connection_ids': mcp_server_connection_ids or [],
            'attachments': attachments or []
        }

        # Add device tools if agent mode is enabled
        if agent_mode:
            device_tools = self._collect_device_tools()
            if device_tools:
                data['device_tools'] = device_tools

        with self.session.post(url, json=data, stream=True) as response:
            response.raise_for_status()
            buffer = ""

            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode('utf-8')

                # Handle SSE format: "data: {...}"
                if line.startswith('data: '):
                    line = line[6:]

                # Skip SSE comments or keep-alive
                if line.startswith(':'):
                    continue

                buffer += line

                # Try to parse whatever is in the buffer
                while buffer:
                    buffer = buffer.strip()
                    if not buffer:
                        break
                    try:
                        chunk, idx = json.JSONDecoder().raw_decode(buffer)
                        yield chunk
                        buffer = buffer[idx:].strip()
                    except json.JSONDecodeError:
                        # Incomplete JSON, wait for more data
                        break

    # Media endpoints
    def list_media(self, page: int = 1, page_size: int = 12, media_type: str = None, search: str = None) -> Dict:
        """List user media"""
        params = {'page': page, 'page_size': page_size}
        if media_type:
            params['type'] = media_type
        if search:
            params['search'] = search
        return self._get('/api/v1/media/', params)

    # Integrations endpoints
    def list_integrations(self) -> Dict:
        """List integrated accounts"""
        return self._get('/api/v1/integrations/')

    def list_custom_integrations(self) -> Dict:
        """List custom integrated accounts"""
        return self._get('/api/v1/integrations/custom/')

    def list_ai_configs(self) -> List[Dict]:
        """List AI provider configurations"""
        return self._get('/api/v1/integrations/ai/providers/configs/')

    def list_ai_providers(self) -> List[Dict]:
        """List AI providers"""
        return self._get('/api/v1/integrations/ai/providers/')

    def list_provider_models(self, provider_id: str) -> List[Dict]:
        """List models for a provider"""
        return self._get('/api/v1/list-provider-models/', {'provider': provider_id})

    def get_ai_settings(self) -> Dict:
        """Get AI settings"""
        return self._get('/api/v1/integrations/ai/settings/')

    # Store endpoints
    def list_featured_toolkits(self) -> Dict:
        """List featured toolkits"""
        return self._get('/api/v1/store/toolkits/featured/')

    def list_popular_toolkits(self) -> Dict:
        """List popular toolkits"""
        return self._get('/api/v1/store/toolkits/popular/')

    def list_recommended_toolkits(self) -> Dict:
        """List recommended toolkits"""
        return self._get('/api/v1/store/toolkits/for_you/')

    # Pricing endpoints
    def get_pricing(self) -> List[Dict]:
        """Get pricing information"""
        return self._get('/api/v1/payments/pricing/')

    def _collect_device_tools(self) -> List[Dict]:
        """Collect all available MCP tools from configured servers for agent mode"""
        try:
            from .mcp_client import mcp_client_manager

            device_tools = []
            configs = mcp_client_manager.load_server_configs()

            for server_name in configs:
                try:
                    # Get tools for this server
                    tools = asyncio.run(mcp_client_manager.list_tools(server_name))
                    for tool in tools:
                        device_tools.append({
                            'server_name': server_name,
                            'title': tool.get('title', tool['name']),
                            'name': tool.get('name'),
                            'description': tool.get('description', ''),
                            'input_schema': tool.get('inputSchema', {}),
                            'output_schema': tool.get('outputSchema', {})
                        })
                except Exception as e:
                    # Skip servers that fail to load
                    continue

            return device_tools
        except Exception as e:
            # If anything fails, return empty list
            return []
