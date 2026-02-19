#!/usr/bin/env python3
"""
ChatATP CLI - Terminal Interface for ChatATP API
"""

import click
import json
import sys
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from .config import Config
from .api_client import ChatATPAPI

console = Console()
config_manager = Config()
api = ChatATPAPI(config_manager)

def format_json(data) -> str:
    """Format JSON data for display"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def check_auth():
    """Check if user is authenticated"""
    if not config_manager.api_token:
        console.print("[red]Error: No API token configured. Use 'chatatp config set-token <token>' to set it.[/red]")
        sys.exit(1)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """ChatATP CLI - Terminal Interface for ChatATP API"""
    pass

# Configuration commands
@cli.group()
def config():
    """Configuration management"""
    pass

@config.command()
@click.argument('token')
def set_token(token):
    """Set API token"""
    config_manager.api_token = token
    console.print("[green]API token set successfully![/green]")

@config.command()
@click.argument('url')
def set_base_url(url):
    """Set API base URL"""
    config_manager.api_base_url = url
    console.print("[green]API base URL set successfully![/green]")

@config.command()
@click.argument('model')
def set_default_model(model):
    """Set default model"""
    config_manager.default_model = model
    console.print("[green]Default model set successfully![/green]")

@config.command()
def show():
    """Show current configuration"""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("API Base URL", config_manager.api_base_url)
    table.add_row("API Token", config_manager.api_token[:20] + "..." if config_manager.api_token else "Not set")
    table.add_row("Default Model", config_manager.default_model)

    console.print(table)

# Account commands
@cli.command()
def account():
    """Get account information"""
    check_auth()
    try:
        with console.status("[bold green]Fetching account info..."):
            data = api.get_account()

        user = data['user_account']['user']
        console.print(Panel.fit(
            f"[bold blue]Name:[/bold blue] {user['first_name']} {user['last_name']}\n"
            f"[bold blue]Username:[/bold blue] {user['username']}\n"
            f"[bold blue]Email:[/bold blue] {user['email']}\n"
            f"[bold blue]Bio:[/bold blue] {data['user_account']['bio']}\n"
            f"[bold blue]Company:[/bold blue] {data['user_account']['company_name']}\n"
            f"[bold blue]Credits:[/bold blue] {data['user_account']['credits']}",
            title="Account Information"
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Models commands
@cli.command()
def models():
    """List available models"""
    check_auth()
    try:
        with console.status("[bold green]Fetching models..."):
            data = api.list_models()

        table = Table(title="Available Models")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Default", style="green")

        for model in data:
            table.add_row(
                model['id'],
                model['name'],
                model['description'],
                "✓" if model.get('default', False) else ""
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Toolkits commands
@cli.command()
def toolkits():
    """List user's toolkits"""
    check_auth()
    try:
        with console.status("[bold green]Fetching toolkits..."):
            data = api.list_collections()

        table = Table(title="Your Toolkits")
        table.add_column("Name", style="cyan")
        table.add_column("Display Name", style="magenta")
        table.add_column("Category", style="white")
        table.add_column("Installs", style="green")

        for toolkit in data['toolkits']:
            table.add_row(
                toolkit['tool_kit']['name'],
                toolkit['tool_kit']['display_name'],
                toolkit['tool_kit']['category'],
                str(toolkit['tool_kit']['installs'])
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Chat commands
@cli.group()
def chat():
    """Chat management"""
    pass

@chat.command()
def rooms():
    """List chatrooms"""
    check_auth()
    try:
        with console.status("[bold green]Fetching chatrooms..."):
            data = api.list_chatrooms()

        table = Table(title="Chat Rooms")
        table.add_column("Room ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Created", style="white")

        for room in data['chatrooms']:
            table.add_row(
                room['room_id'],
                room['group_name'],
                room['created'][:19]
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@chat.command()
@click.argument('room_id')
def show(room_id):
    """Show chatroom details"""
    check_auth()
    try:
        with console.status("[bold green]Fetching chat details..."):
            data = api.get_chatroom(room_id)

        room = data['chatroom']
        console.print(Panel.fit(
            f"[bold blue]Name:[/bold blue] {room['group_name']}\n"
            f"[bold blue]Description:[/bold blue] {room['group_description']}\n"
            f"[bold blue]Created:[/bold blue] {room['created'][:19]}\n"
            f"[bold blue]Members:[/bold blue] {len(room['members'])}",
            title=f"Chat Room: {room['room_id']}"
        ))

        if data['chats']:
            console.print("\n[bold]Recent Messages:[/bold]")
            for chat in data['chats'][-5:]:  # Show last 5 messages
                sender = chat['sender_account']['user']['first_name']
                time = chat['created'][:19]
                message = chat['text'][:100] + "..." if len(chat['text']) > 100 else chat['text']
                console.print(f"[cyan]{time}[/cyan] [magenta]{sender}:[/magenta] {message}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def chat_loop(room_id, initial_message=None, model=None, toolkits=None, mcp_connections=None):
    """Interactive chat loop for back-and-forth conversation"""
    console.print(f"\n[bold cyan]Entered chatroom: {room_id}[/bold cyan]")
    console.print("[dim]Type your message or '/exit' to quit, '/help' for commands[/dim]\n")

    # Send initial message if provided
    if initial_message:
        console.print(f"[bold green]You:[/bold green] {initial_message}")
        send_single_message(room_id, initial_message, model, toolkits, mcp_connections)

    while True:
        try:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['/exit', '/quit', '/q']:
                console.print("[yellow]Exiting chat...[/yellow]")
                break
            elif user_input.lower() in ['/help', '/h']:
                console.print("\n[bold]Available commands:[/bold]")
                console.print("  /exit, /quit, /q  - Exit the chat")
                console.print("  /help, /h         - Show this help")
                console.print("  /clear             - Clear the screen")
                console.print("  /history           - Show chat history")
                console.print()
                continue
            elif user_input.lower() == '/clear':
                console.clear()
                console.print(f"[bold cyan]Chatroom: {room_id}[/bold cyan]")
                console.print("[dim]Type your message or '/exit' to quit[/dim]\n")
                continue
            elif user_input.lower() == '/history':
                try:
                    with console.status("[bold cyan]Loading history...[/bold cyan]"):
                        data = api.get_chatroom(room_id)
                    if data.get('chats'):
                        console.print("\n[bold]Recent messages:[/bold]")
                        for chat in data['chats'][-10:]:  # Last 10 messages
                            sender = chat['sender_account']['user']['first_name']
                            time = chat['created'][:19]
                            message = chat['text'][:100] + "..." if len(chat['text']) > 100 else chat['text']
                            if sender == "ChatATP":
                                console.print(f"[cyan]{time}[/cyan] [magenta]{sender}:[/magenta] {message}")
                            else:
                                console.print(f"[cyan]{time}[/cyan] [green]{sender}:[/green] {message}")
                        console.print()
                    else:
                        console.print("[yellow]No chat history found.[/yellow]\n")
                except Exception as e:
                    console.print(f"[red]Error loading history: {e}[/red]\n")
                continue

            # Send the message
            send_single_message(room_id, user_input, model, toolkits, mcp_connections)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Use '/exit' to quit properly.[/yellow]")
        except EOFError:
            console.print("\n[yellow]EOF received. Exiting...[/yellow]")
            break

def send_single_message(room_id, message, model=None, toolkits=None, mcp_connections=None, debug=False):
    """Send a single message and handle the streaming response"""
    try:
        full_response = ""
        in_think_block = False
        chunk_count = 0
        response_started = False
        tool_lines = []

        with console.status("[bold cyan]Sending...[/bold cyan]", spinner="dots") as status:

            for chunk in api.send_chat_message_stream(
                room_id=room_id,
                message=message,
                model=model,
                toolkit_ids=list(toolkits) if toolkits else None,
                mcp_server_connection_ids=list(mcp_connections) if mcp_connections else None
            ):
                chunk_count += 1

                if debug:
                    console.print(f"[dim]CHUNK #{chunk_count}: {chunk}[/dim]")

                msg_type = chunk.get('message_type', '')

                # ── tool_call ──────────────────────────────────────────────
                if msg_type == 'tool_call':
                    tool      = chunk.get('tool', {})
                    tool_name = tool.get('name') or chunk.get('toolkit_name') or 'tool'
                    toolkit   = chunk.get('toolkit_name', '')
                    args      = tool.get('arguments', {})

                    arg_hint = ''
                    if args:
                        first_val = next(iter(args.values()), None)
                        if first_val and isinstance(first_val, str) and len(first_val) < 60:
                            arg_hint = f' [dim]"{first_val}"[/dim]'

                    # Print a running line — no emoji, clean mono style
                    console.print(
                        f"\n  [dim]┌[/dim] [bold white]{tool_name}[/bold white]"
                        f"[dim] · {toolkit}{arg_hint}[/dim]"
                    )
                    status.update(
                        f"[cyan]Running [bold]{tool_name}[/bold]...[/cyan]"
                    )

                # ── tool_result ────────────────────────────────────────────
                elif msg_type == 'tool_result':
                    executions = chunk.get('timing_metrics', {}).get('tool_executions', [])
                    if executions:
                        last      = executions[-1]
                        tool_name = last.get('tool_name', 'tool')
                        duration  = last.get('execution_duration', 0)
                        ok        = last.get('status', 'success') == 'success'
                        mark      = '[bold green]done[/bold green]' if ok else '[bold red]failed[/bold red]'
                        console.print(
                            f"  [dim]└[/dim] {mark} [dim]{duration:.2f}s[/dim]"
                        )
                    else:
                        console.print(f"  [dim]└[/dim] [bold green]done[/bold green]")

                    status.update("[cyan]Processing...[/cyan]")

                # ── chat_message ───────────────────────────────────────────
                elif msg_type == 'chat_message':
                    message_chunk = chunk.get('message', '')

                    if message_chunk:
                        if '<think>' in message_chunk:
                            in_think_block = True

                        if in_think_block:
                            if '</think>' in message_chunk:
                                in_think_block = False
                                status.update("[cyan]Processing...[/cyan]")
                            else:
                                status.update("[yellow]Thinking...[/yellow]")
                            continue

                        if not response_started:
                            response_started = True
                            status.stop()
                            console.print(
                                f"\n[bold white]ChatATP[/bold white] [dim]·[/dim]\n"
                            )

                        full_response += message_chunk

                    if chunk.get('is_typing') == False:
                        break

        if response_started:
            console.print(Markdown(full_response))
            console.print("\n[dim]─────────────────────────────────[/dim]")
        elif chunk_count == 0:
            console.print("[red]No data received.[/red]")
        else:
            console.print(f"[yellow]No message content in {chunk_count} chunks.[/yellow]")
            if not debug:
                console.print("[dim]Run with --debug to inspect.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            import traceback
            traceback.print_exc()

@chat.command()
@click.argument('message')
@click.option('--model', default=None, help='Model to use')
@click.option('--toolkits', multiple=True, help='Toolkit IDs to use')
@click.option('--mcp-connections', multiple=True, help='MCP connection IDs to use')
def new(message, model, toolkits, mcp_connections):
    """Create new chatroom and start interactive chat"""
    check_auth()
    try:
        with console.status("[bold green]Creating chatroom..."):
            data = api.create_chatroom(
                message=message,
                model=model,
                toolkit_ids=list(toolkits) if toolkits else None,
                mcp_server_connection_ids=list(mcp_connections) if mcp_connections else None
            )

        room_id = data['room_id']
        console.print(f"[green]Chatroom created: {room_id}[/green]")

        # Start the interactive chat loop
        chat_loop(room_id, initial_message=message, model=model, toolkits=toolkits, mcp_connections=mcp_connections)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@chat.command()
@click.argument('room_id')
@click.option('--model', default=None, help='Model to use')
@click.option('--toolkits', multiple=True, help='Toolkit IDs to use')
@click.option('--mcp-connections', multiple=True, help='MCP connection IDs to use')
def converse(room_id, model, toolkits, mcp_connections):
    """Enter existing chatroom for interactive chat"""
    check_auth()
    try:
        # Verify the room exists
        with console.status("[bold cyan]Entering chatroom...[/bold cyan]"):
            data = api.get_chatroom(room_id)

        # Start the interactive chat loop
        chat_loop(room_id, initial_message=None, model=model, toolkits=toolkits, mcp_connections=mcp_connections)

    except Exception as e:
        console.print(f"[red]Error entering chatroom: {e}[/red]")

@chat.command()
@click.argument('room_id')
@click.argument('message')
@click.option('--model', default=None, help='Model to use')
@click.option('--toolkits', multiple=True, help='Toolkit IDs to use')
@click.option('--mcp-connections', multiple=True, help='MCP connection IDs to use')
@click.option('--debug', is_flag=True, help='Show raw stream chunks')
def send(room_id, message, model, toolkits, mcp_connections, debug):
    """Send message to chatroom"""
    check_auth()
    try:
        full_response = ""
        in_think_block = False
        chunk_count = 0
        response_started = False
        tool_lines = []  # track printed tool lines to update them

        with console.status("[bold cyan]Sending...[/bold cyan]", spinner="dots") as status:

            for chunk in api.send_chat_message_stream(
                room_id=room_id,
                message=message,
                model=model,
                toolkit_ids=list(toolkits) if toolkits else None,
                mcp_server_connection_ids=list(mcp_connections) if mcp_connections else None
            ):
                chunk_count += 1

                if debug:
                    console.print(f"[dim]CHUNK #{chunk_count}: {chunk}[/dim]")

                msg_type = chunk.get('message_type', '')

                # ── tool_call ──────────────────────────────────────────────
                if msg_type == 'tool_call':
                    tool      = chunk.get('tool', {})
                    tool_name = tool.get('name') or chunk.get('toolkit_name') or 'tool'
                    toolkit   = chunk.get('toolkit_name', '')
                    args      = tool.get('arguments', {})

                    arg_hint = ''
                    if args:
                        first_val = next(iter(args.values()), None)
                        if first_val and isinstance(first_val, str) and len(first_val) < 60:
                            arg_hint = f' [dim]"{first_val}"[/dim]'

                    # Print a running line — no emoji, clean mono style
                    console.print(
                        f"\n  [dim]┌[/dim] [bold white]{tool_name}[/bold white]"
                        f"[dim] · {toolkit}{arg_hint}[/dim]"
                    )
                    status.update(
                        f"[cyan]Running [bold]{tool_name}[/bold]...[/cyan]"
                    )

                # ── tool_result ────────────────────────────────────────────
                elif msg_type == 'tool_result':
                    executions = chunk.get('timing_metrics', {}).get('tool_executions', [])
                    if executions:
                        last      = executions[-1]
                        tool_name = last.get('tool_name', 'tool')
                        duration  = last.get('execution_duration', 0)
                        ok        = last.get('status', 'success') == 'success'
                        mark      = '[bold green]done[/bold green]' if ok else '[bold red]failed[/bold red]'
                        console.print(
                            f"  [dim]└[/dim] {mark} [dim]{duration:.2f}s[/dim]"
                        )
                    else:
                        console.print(f"  [dim]└[/dim] [bold green]done[/bold green]")

                    status.update("[cyan]Processing...[/cyan]")

                # ── chat_message ───────────────────────────────────────────
                elif msg_type == 'chat_message':
                    message_chunk = chunk.get('message', '')

                    if message_chunk:
                        if '<think>' in message_chunk:
                            in_think_block = True

                        if in_think_block:
                            if '</think>' in message_chunk:
                                in_think_block = False
                                status.update("[cyan]Processing...[/cyan]")
                            else:
                                status.update("[yellow]Thinking...[/yellow]")
                            continue

                        if not response_started:
                            response_started = True
                            status.stop()
                            console.print(
                                f"\n[bold white]ChatATP[/bold white] [dim]·[/dim]\n"
                            )

                        full_response += message_chunk

                    if chunk.get('is_typing') == False:
                        break

        if response_started:
            console.print(Markdown(full_response))
            console.print("\n[dim]─────────────────────────────────[/dim]")
        elif chunk_count == 0:
            console.print("[red]No data received.[/red]")
        else:
            console.print(f"[yellow]No message content in {chunk_count} chunks.[/yellow]")
            if not debug:
                console.print("[dim]Run with --debug to inspect.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            import traceback
            traceback.print_exc()

# Integrations commands
@cli.group()
def integrations():
    """Integration management"""
    pass

@integrations.command()
def list():
    """List integrations"""
    check_auth()
    try:
        with console.status("[bold green]Fetching integrations..."):
            data = api.list_integrations()

        table = Table(title="OAuth Integrations")
        table.add_column("Platform", style="cyan")
        table.add_column("Display Name", style="magenta")
        table.add_column("Status", style="green")

        for integration in data['integrations']:
            platform = integration['platform']['display_name'] if integration.get('platform') else 'N/A'
            table.add_row(
                integration['platform']['name'] if integration.get('platform') else 'Unknown',
                platform,
                "Connected" if integration.get('access_token') else "Not Connected"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@integrations.command()
def custom():
    """List custom integrations"""
    check_auth()
    try:
        with console.status("[bold green]Fetching custom integrations..."):
            data = api.list_custom_integrations()

        table = Table(title="Custom Integrations")
        table.add_column("Name", style="cyan")
        table.add_column("Unique Name", style="magenta")
        table.add_column("API Key", style="green")

        for integration in data['integrations']:
            table.add_row(
                integration['name'],
                integration['unique_name'],
                "Set" if integration['api_key'] else "Not Set"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# AI commands
@cli.group()
def ai():
    """AI management"""
    pass

@ai.command()
def providers():
    """List AI providers"""
    check_auth()
    try:
        with console.status("[bold green]Fetching providers..."):
            data = api.list_ai_providers()

        table = Table(title="AI Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Unique Name", style="magenta")
        table.add_column("Category", style="white")
        table.add_column("Connected", style="green")

        for provider in data:
            table.add_row(
                provider['name'],
                provider['unique_name'],
                provider['category'],
                "✓" if provider.get('connected', False) else ""
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@ai.command()
def configs():
    """List AI configurations"""
    check_auth()
    try:
        with console.status("[bold green]Fetching configs..."):
            data = api.list_ai_configs()

        table = Table(title="AI Configurations")
        table.add_column("Provider", style="cyan")
        table.add_column("Config ID", style="magenta")
        table.add_column("Default", style="green")
        table.add_column("API Key", style="white")

        for config_item in data:
            provider_name = config_item['provider']['name']
            table.add_row(
                provider_name,
                config_item['config_id'],
                "✓" if config_item.get('default', False) else "",
                "Set" if config_item.get('api_key') else "Not Set"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@ai.command()
@click.argument('provider_id')
def provider_models(provider_id):
    """List models for a provider"""
    check_auth()
    try:
        with console.status("[bold green]Fetching provider models..."):
            data = api.list_provider_models(provider_id)

        table = Table(title=f"Models for Provider {provider_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="white")

        for model in data:
            table.add_row(
                model['id'],
                model['name'],
                model['description']
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@ai.command()
def settings():
    """Show AI settings"""
    check_auth()
    try:
        with console.status("[bold green]Fetching settings..."):
            data = api.get_ai_settings()

        console.print(Panel.fit(
            f"[bold blue]Default Chat Model:[/bold blue] {data['default_chat_completion_model_id']}\n"
            f"[bold blue]Default Image Model:[/bold blue] {data['default_image_gen_model_id']}\n"
            f"[bold blue]Default Speech Model:[/bold blue] {data['default_speech_gen_model_id']}\n"
            f"[bold blue]Temperature:[/bold blue] {data['temperature']}\n"
            f"[bold blue]Max Tokens:[/bold blue] {data['max_tokens']}\n"
            f"[bold blue]System Instruction:[/bold blue] {data['system_instruction'][:100]}...",
            title="AI Settings"
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# MCP commands
@cli.group()
def mcp():
    """MCP management"""
    pass

@mcp.command()
def connections():
    """List MCP connections"""
    check_auth()
    try:
        with console.status("[bold green]Fetching MCP connections..."):
            data = api.list_mcp_connections()

        console.print(format_json(data))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@mcp.command()
def servers():
    """List MCP servers"""
    check_auth()
    try:
        with console.status("[bold green]Fetching MCP servers..."):
            data = api.list_mcp_servers()

        console.print(format_json(data))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Store commands
@cli.group()
def store():
    """Store management"""
    pass

@store.command()
def featured():
    """List featured toolkits"""
    check_auth()
    try:
        with console.status("[bold green]Fetching featured toolkits..."):
            data = api.list_featured_toolkits()

        table = Table(title="Featured Toolkits")
        table.add_column("Name", style="cyan")
        table.add_column("Display Name", style="magenta")
        table.add_column("Category", style="white")
        table.add_column("Installs", style="green")

        for toolkit in data['featured']:
            table.add_row(
                toolkit['name'],
                toolkit['display_name'],
                toolkit['category'],
                str(toolkit['installs'])
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@store.command()
def popular():
    """List popular toolkits"""
    check_auth()
    try:
        with console.status("[bold green]Fetching popular toolkits..."):
            data = api.list_popular_toolkits()

        table = Table(title="Popular Toolkits")
        table.add_column("Name", style="cyan")
        table.add_column("Display Name", style="magenta")
        table.add_column("Category", style="white")
        table.add_column("Installs", style="green")

        for toolkit in data['popular_toolkits']:
            table.add_row(
                toolkit['name'],
                toolkit['display_name'],
                toolkit['category'],
                str(toolkit['installs'])
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@store.command()
def recommended():
    """List recommended toolkits"""
    check_auth()
    try:
        with console.status("[bold green]Fetching recommended toolkits..."):
            data = api.list_recommended_toolkits()

        table = Table(title="Recommended Toolkits")
        table.add_column("Name", style="cyan")
        table.add_column("Display Name", style="magenta")
        table.add_column("Category", style="white")
        table.add_column("Installs", style="green")

        for toolkit in data['recommended']:
            table.add_row(
                toolkit['name'],
                toolkit['display_name'],
                toolkit['category'],
                str(toolkit['installs'])
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Media commands
@cli.command()
@click.option('--page', default=1, help='Page number')
@click.option('--page-size', default=12, help='Items per page')
@click.option('--type', 'media_type', help='Media type (image, video, audio, document)')
@click.option('--search', help='Search query')
def media(page, page_size, media_type, search):
    """List user media"""
    check_auth()
    try:
        with console.status("[bold green]Fetching media..."):
            data = api.list_media(page=page, page_size=page_size, media_type=media_type, search=search)

        table = Table(title="Media Files")
        table.add_column("Type", style="cyan")
        table.add_column("File Name", style="magenta")
        table.add_column("Created", style="white")
        table.add_column("URL", style="green")

        for item in data['results']:
            media_type_display = "Document" if item['media_is_doc'] else "Image" if item['media_is_img'] else "Video" if item['media_is_vid'] else "Audio" if item['media_is_aud'] else "Other"
            filename = item['extra_data'].get('original_name', 'Unknown')
            table.add_row(
                media_type_display,
                filename,
                item['created'][:19],
                item['media_url'][:50] + "..."
            )

        console.print(table)
        console.print(f"\nPage {data['next']} of {len(data['results'])} items")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

# Pricing command
@cli.command()
def pricing():
    """Show pricing information"""
    check_auth()
    try:
        with console.status("[bold green]Fetching pricing..."):
            data = api.get_pricing()

        for plan in data:
            console.print(Panel.fit(
                f"[bold blue]Name:[/bold blue] {plan['name']}\n"
                f"[bold blue]Description:[/bold blue] {plan['description']}\n"
                f"[bold blue]Features:[/bold blue]\n" +
                "\n".join(f"  • {feature}" for feature in plan['features']),
                title=f"Plan: {plan['name']}"
            ))

            if plan.get('prices'):
                console.print("[bold]Pricing:[/bold]")
                for price in plan['prices']:
                    interval = price['interval']
                    amount = price['amount']
                    currency = price['currency'].upper()
                    console.print(f"  {interval.capitalize()}: ${amount} {currency}")

            console.print()  # Spacing between plans
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == '__main__':
    cli()
