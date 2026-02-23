import os
from typing import Optional
import yaml
from pathlib import Path

class Config:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(Path.home(), '.chatatp', 'config.yaml')
        self._config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = {}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            self._config = {}

    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    @property
    def api_base_url(self) -> str:
        return self._config.get('api_base_url', 'https://api.chat-atp.com')

    @api_base_url.setter
    def api_base_url(self, value: str):
        self._config['api_base_url'] = value
        self.save_config()

    @property
    def api_token(self) -> Optional[str]:
        return self._config.get('api_token')

    @api_token.setter
    def api_token(self, value: str):
        self._config['api_token'] = value
        self.save_config()

    @property
    def default_model(self) -> str:
        return self._config.get('default_model', 'gpt-oss-120b')

    @default_model.setter
    def default_model(self, value: str):
        self._config['default_model'] = value
        self.save_config()

    @property
    def notifications_enabled(self) -> bool:
        return self._config.get('notifications_enabled', True)

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool):
        self._config['notifications_enabled'] = value
        self.save_config()

    @property
    def sound_enabled(self) -> bool:
        return self._config.get('sound_enabled', True)

    @sound_enabled.setter
    def sound_enabled(self, value: bool):
        self._config['sound_enabled'] = value
        
    @property
    def agent_mode(self) -> bool:
        return self._config.get('agent_mode', False)

    @agent_mode.setter
    def agent_mode(self, value: bool):
        self._config['agent_mode'] = value
        self.save_config()

    @property
    def proxy_host(self) -> str:
        return self._config.get('proxy_host', '127.0.0.1')

    @proxy_host.setter
    def proxy_host(self, value: str):
        self._config['proxy_host'] = value
        self.save_config()

    @property
    def proxy_port(self) -> int:
        return self._config.get('proxy_port', 8001)

    @proxy_port.setter
    def proxy_port(self, value: int):
        self._config['proxy_port'] = value
        self.save_config()

    @property
    def proxy_enabled(self) -> bool:
        return self._config.get('proxy_enabled', False)

    @proxy_enabled.setter
    def proxy_enabled(self, value: bool):
        self._config['proxy_enabled'] = value

    @property
    def proxy_ngrok_token(self) -> Optional[str]:
        return self._config.get('proxy_ngrok_token')

    @proxy_ngrok_token.setter
    def proxy_ngrok_token(self, value: str):
        self._config['proxy_ngrok_token'] = value
        self.save_config()

    @property
    def proxy_auto_start(self) -> bool:
        return self._config.get('proxy_auto_start', False)

    @proxy_auto_start.setter
    def proxy_auto_start(self, value: bool):
        self._config['proxy_auto_start'] = value
        self.save_config()

    @property
    def proxy_use_ngrok(self) -> bool:
        return self._config.get('proxy_use_ngrok', True)

    @proxy_use_ngrok.setter
    def proxy_use_ngrok(self, value: bool):
        self._config['proxy_use_ngrok'] = value
        self.save_config()

    def get_headers(self) -> dict:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_token:
            headers['Authorization'] = f'Token {self.api_token}'
        return headers
