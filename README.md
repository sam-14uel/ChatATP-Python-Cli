# ChatATP CLI

A powerful terminal interface for the ChatATP API, built with Python. Interact with ChatATP's AI models, manage chatrooms, toolkits, integrations, and more directly from your command line.

## Features

- **Account Management**: View your ChatATP account information
- **Model Management**: List and manage AI models
- **Chat Interface**: Create chatrooms and send messages with streaming responses
- **Toolkit Management**: Browse and manage your toolkits and collections
- **Integration Management**: Manage OAuth and custom integrations
- **AI Configuration**: Configure AI providers, models, and settings
- **Media Management**: Browse and manage uploaded media files
- **Store Access**: Browse featured and popular toolkits
- **MCP Support**: Manage MCP servers and connections

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the script executable (optional):
   ```bash
   chmod +x main.py
   ```

## Configuration

Before using the CLI, you need to configure your API token:

```bash
python main.py config set-token YOUR_API_TOKEN_HERE
```

You can also configure other settings:

```bash
# Set custom API base URL (default: https://api.chat-atp.com)
python main.py config set-base-url https://your-custom-api-url.com

# Set default model
python main.py config set-default-model gpt-oss-120b

# View current configuration
python main.py config show
```

## Usage

### Getting Help

```bash
python main.py --help
```

### Account Information

```bash
python main.py account
```

### Models

```bash
# List available models
python main.py models

# List models for a specific provider
python main.py ai provider-models PROVIDER_ID
```

### Chat Management

```bash
# List your chatrooms
python main.py chat rooms

# Show details of a specific chatroom
python main.py chat show ROOM_ID

# Create a new chatroom
python main.py chat new "Hello, how are you?"

# Send a message to a chatroom
python main.py chat send ROOM_ID "Your message here"

# Send message with specific model and toolkits
python main.py chat send ROOM_ID "Analyze this data" --model gpt-oss-120b --toolkits TOOLKIT_ID1 TOOLKIT_ID2
```

### Toolkits

```bash
# List your toolkits
python main.py toolkits

# Browse featured toolkits
python main.py store featured

# Browse popular toolkits
python main.py store popular
```

### Integrations

```bash
# List OAuth integrations
python main.py integrations list

# List custom integrations
python main.py integrations custom
```

### AI Management

```bash
# List AI providers
python main.py ai providers

# List AI configurations
python main.py ai configs

# Show AI settings
python main.py ai settings
```

### Media

```bash
# List your media files
python main.py media

# Search media
python main.py media --search "document name"

# Filter by type
python main.py media --type image

# Pagination
python main.py media --page 2 --page-size 20
```

### Pricing

```bash
# View pricing plans
python main.py pricing
```

## Authentication

All commands require authentication. Make sure you've set your API token using:

```bash
python main.py config set-token YOUR_TOKEN
```

The token will be stored securely in your home directory under `~/.chatatp/config.yaml`.

## Error Handling

The CLI provides clear error messages for common issues:
- Missing API token
- Invalid room IDs
- Network errors
- Authentication failures

## Streaming Chat

Chat responses are streamed in real-time for a smooth conversational experience. The CLI will display responses as they arrive from the ChatATP API.

## Dependencies

- requests: HTTP client
- click: Command line interface
- rich: Beautiful terminal output
- pyyaml: Configuration file handling
- python-dotenv: Environment variable support

## Contributing

Feel free to submit issues and pull requests to improve the ChatATP CLI.

## License

This project is licensed under the MIT License.
