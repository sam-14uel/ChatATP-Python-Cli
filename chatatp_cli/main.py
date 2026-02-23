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
from .notifications import notification_manager
from .mcp_client import mcp_client_manager
import asyncio

console = Console()
config_manager = Config()
api = ChatATPAPI(config_manager)

# Initialize notification manager with config settings
notification_manager.enabled = config_manager.notifications_enabled
notification_manager._sound_enabled = config_manager.sound_enabled

def format_json(data) -> str:
    """Format JSON data for display"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def check_auth():
    """Check if user is authenticated"""
    if not config_manager.api_token:
        console.print("[red]Error: No API token configured. Use 'chatatp config set-token <token>' to set it.[/red]")
        sys.exit(1)

def print_banner():
    """Print ASCII banner for ChatATP CLI"""
    banner = """
 ██████╗██╗  ██╗ █████╗ ████████╗ █████╗ ████████╗██████╗ 
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
██║     ███████║███████║   ██║   ███████║   ██║   ██████╔╝
██║     ██╔══██║██╔══██║   ██║   ██╔══██║   ██║   ██╔═══╝ 
╚██████╗██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ██║     
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝     
"""
    console.print(banner, style="bold cyan")

@click.group(invoke_without_command=True)
@click.version_option(version="1.1.1", prog_name="ChatATP CLI")
@click.pass_context
def cli(ctx):
    """ChatATP CLI - Terminal Interface for ChatATP API"""
    # If no subcommand was given, show help and banner
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print(ctx.get_help())

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

@config.command()
def enable_notifications():
    """Enable desktop notifications"""
    config_manager.notifications_enabled = True
    notification_manager.enable_notifications()
    console.print("[green]Desktop notifications enabled![/green]")

@config.command()
def disable_notifications():
    """Disable desktop notifications"""
    config_manager.notifications_enabled = False
    notification_manager.disable_notifications()
    console.print("[yellow]Desktop notifications disabled.[/yellow]")

@config.command()
def enable_sound():
    """Enable notification sounds"""
    config_manager.sound_enabled = True
    notification_manager.enable_sound()
    console.print("[green]Notification sounds enabled![/green]")

@config.command()
def disable_sound():
    """Disable notification sounds"""
    config_manager.sound_enabled = False
    notification_manager.disable_sound()
    console.print("[yellow]Notification sounds disabled.[/yellow]")

@config.command()
def proxy_status():
    """Show MCP proxy configuration and status"""
    table = Table(title="MCP Proxy Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Host", config_manager.proxy_host)
    table.add_row("Port", str(config_manager.proxy_port))
    table.add_row("Use Ngrok", "[green]Yes[/green]" if config_manager.proxy_use_ngrok else "[red]No[/red]")
    table.add_row("Ngrok Token", "Set" if config_manager.proxy_ngrok_token else "Not set")

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
        tool_lines = []  # track printed tool lines to update them

        with console.status("[bold cyan]Sending...[/bold cyan]", spinner="dots") as status:

            for chunk in api.send_chat_message_stream(
                room_id=room_id,
                message=message,
                model=model,
                toolkit_ids=list(toolkits) if toolkits else None,
                mcp_server_connection_ids=list(mcp_connections) if mcp_connections else None,
                agent_mode=config_manager.agent_mode
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

                    # Check if this is a device tool call that we need to execute locally
                    execution_type = chunk.get('execution_type')
                    if execution_type == 'device' and config_manager.agent_mode:
                        # Execute device tool locally
                        result = asyncio.run(_execute_device_tool(chunk))
                        if result:
                            # Send result back to API
                            asyncio.run(_send_tool_result(room_id, chunk, result))
                        continue

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

                            # Send notification when AI starts responding
                            notification_manager.notify_ai_start(model)

                            # Start live markdown display for streaming response
                            live = Live(Markdown(""), console=console, auto_refresh=False)
                            live.start()
                            update_count = 0

                        full_response += message_chunk
                        live.update(Markdown(full_response))
                        update_count += 1
                        if update_count % 3 == 0:
                            live.refresh()

                    if chunk.get('is_typing') == False:
                        # Mark as completed, but continue processing chunks
                        pass

        if response_started:
            live.stop()
            notification_manager.notify_ai_complete(model)
            console.print()
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
                mcp_server_connection_ids=list(mcp_connections) if mcp_connections else None,
                agent_mode=config_manager.agent_mode            
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

                    # Check if this is a device tool call that we need to execute locally
                    execution_type = chunk.get('execution_type')
                    if execution_type == 'device' and config_manager.agent_mode:
                        # Execute device tool locally
                        result = asyncio.run(_execute_device_tool(chunk))
                        if result:
                            # Send result back to API
                            asyncio.run(_send_tool_result(room_id, chunk, result))
                        continue

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

                            # Send notification when AI starts responding
                            notification_manager.notify_ai_start(model)

                            # Start live markdown display for streaming response
                            live = Live(Markdown(""), console=console, auto_refresh=False)
                            live.start()
                            update_count = 0

                        full_response += message_chunk
                        live.update(Markdown(full_response))
                        update_count += 1
                        if update_count % 3 == 0:
                            live.refresh()

                    if chunk.get('is_typing') == False:
                        # Mark as completed, but continue processing chunks
                        pass

        if response_started:
            live.stop()
            notification_manager.notify_ai_complete(model)
            console.print()
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

        table = Table(title=f"MCP Connections ({data.get('count', 0)} total)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Auth Type", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Last Used", style="white")
        table.add_column("Expires", style="red")

        for connection in data.get('connections', []):
            server_details = connection.get('server_details', {})
            name = server_details.get('name', 'Unknown')
            category = server_details.get('category', 'N/A')
            auth_type = server_details.get('auth_type', 'N/A')

            status = connection.get('status', 'unknown')
            status_display = {
                'connected': '[green]Connected[/green]',
                'disconnected': '[red]Disconnected[/red]',
                'connecting': '[yellow]Connecting[/yellow]',
                'error': '[red]Error[/red]'
            }.get(status, f'[dim]{status}[/dim]')

            last_used = connection.get('last_used')
            if last_used:
                last_used = last_used[:10]  # YYYY-MM-DD format
            else:
                last_used = "Never"

            expires_at = connection.get('expires_at')
            if expires_at:
                expires_at = expires_at[:10]  # YYYY-MM-DD format
                if connection.get('is_token_expired'):
                    expires_at = f"[red]{expires_at} (expired)[/red]"
                elif connection.get('requires_reconnect'):
                    expires_at = f"[yellow]{expires_at} (reconnect)[/yellow]"
                else:
                    expires_at = f"[green]{expires_at}[/green]"
            else:
                expires_at = "[dim]Never[/dim]"

            table.add_row(
                name,
                category or "[dim]N/A[/dim]",
                auth_type,
                status_display,
                last_used,
                expires_at
            )

        console.print(table)

        # Show summary
        connected_count = sum(1 for c in data.get('connections', []) if c.get('status') == 'connected')
        expired_count = sum(1 for c in data.get('connections', []) if c.get('is_token_expired'))
        reconnect_count = sum(1 for c in data.get('connections', []) if c.get('requires_reconnect'))

        if expired_count > 0 or reconnect_count > 0:
            console.print(f"\n[bold]Summary:[/bold] {connected_count} connected")
            if expired_count > 0:
                console.print(f"  [red]{expired_count} expired tokens[/red]")
            if reconnect_count > 0:
                console.print(f"  [yellow]{reconnect_count} need reconnection[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@mcp.command()
def servers():
    """List MCP servers"""
    check_auth()
    try:
        with console.status("[bold green]Fetching MCP servers..."):
            data = api.list_mcp_servers()

        table = Table(title=f"MCP Servers ({data.get('count', 0)} total)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Type", style="yellow")
        table.add_column("Auth", style="green")
        table.add_column("Public", style="white")
        table.add_column("URL", style="blue")

        for server in data.get('servers', []):
            name = server.get('name', 'Unknown')
            category = server.get('category', 'N/A')
            server_type = server.get('server_type', 'N/A')
            auth_type = server.get('auth_type', 'N/A')
            is_public = "[green]Yes[/green]" if server.get('is_public') else "[red]No[/red]"

            url = server.get('server_url', 'N/A')
            if url and len(url) > 40:
                url = url[:37] + "..."

            table.add_row(
                name,
                category or "[dim]N/A[/dim]",
                server_type,
                auth_type,
                is_public,
                url or "[dim]N/A[/dim]"
            )

        console.print(table)

        # Show summary by type
        custom_count = sum(1 for s in data.get('servers', []) if s.get('server_type') == 'custom')
        prebuilt_count = sum(1 for s in data.get('servers', []) if s.get('server_type') == 'prebuilt')
        public_count = sum(1 for s in data.get('servers', []) if s.get('is_public'))

        console.print(f"\n[bold]Summary:[/bold] {custom_count} custom, {prebuilt_count} prebuilt, {public_count} public")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@mcp.command()
def local_servers():
    """List configured local MCP servers"""
    try:
        # Load server configurations
        configs = mcp_client_manager.load_server_configs()

        if not configs:
            console.print("[yellow]No MCP server configurations found.[/yellow]")
            console.print("Create a configuration file at one of these locations:")
            console.print("  - ~/mcp.json")
            console.print("  - ~/mcp_config.json")
            console.print("  - ~/.chatatp/mcp.json")
            console.print("  - ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)")
            console.print("  - ~/AppData/Roaming/Claude/claude_desktop_config.json (Windows)")
            return

        table = Table(title=f"Local MCP Servers ({len(configs)} configured)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Command", style="magenta")
        table.add_column("Transport", style="yellow")
        table.add_column("URL/Args", style="green")

        for server_name, config in configs.items():
            command = config.get('command', 'npx')
            transport = config.get('transport', 'stdio').lower()

            if transport in ['http', 'https', 'sse']:
                url_args = config.get('url', 'N/A')
            else:
                args = config.get('args', [])
                url_args = ' '.join(str(arg) for arg in args) if args else 'N/A'
                if len(url_args) > 40:
                    url_args = url_args[:37] + "..."

            table.add_row(
                server_name,
                command,
                transport.upper(),
                url_args
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@mcp.command()
@click.argument('server_name')
def local_connect(server_name):
    """Connect to a local MCP server"""
    try:
        async def _connect():
            with console.status(f"[bold cyan]Connecting to {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                # Get client (this will create and connect)
                client = await mcp_client_manager.get_client(server_name)

                # Initialize and get server info
                server_info = await mcp_client_manager.initialize_client(server_name)

            console.print(Panel.fit(
                f"[bold blue]Server:[/bold blue] {server_info['server_name']}\n"
                f"[bold blue]Version:[/bold blue] {server_info['server_version']}\n"
                f"[bold blue]Title:[/bold blue] {server_info['server_title']}\n"
                f"[bold blue]Capabilities:[/bold blue]\n" +
                "\n".join(f"  • {cap}: {'✓' if enabled else '✗'}" for cap, enabled in server_info['capabilities'].items()),
                title=f"Connected to {server_name}"
            ))

            if server_info.get('instructions'):
                console.print(f"\n[bold]Instructions:[/bold] {server_info['instructions']}")

        asyncio.run(_connect())

    except Exception as e:
        console.print(f"[red]Error connecting to {server_name}: {e}[/red]")

@mcp.command()
@click.argument('server_name')
def local_tools(server_name):
    """List tools available on a local MCP server"""
    try:
        async def _list_tools():
            with console.status(f"[bold cyan]Fetching tools from {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                tools = await mcp_client_manager.list_tools(server_name)

            if not tools:
                console.print(f"[yellow]No tools available on {server_name}.[/yellow]")
                return

            table = Table(title=f"Tools on {server_name}")
            table.add_column("Name", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("Description", style="white")

            for tool in tools:
                description = tool.get('description', '')
                if len(description) > 80:
                    description = description[:77] + "..."

                table.add_row(
                    tool['name'],
                    tool.get('title', tool['name']),
                    description
                )

            console.print(table)

        asyncio.run(_list_tools())

    except Exception as e:
        console.print(f"[red]Error listing tools for {server_name}: {e}[/red]")

@mcp.command()
@click.argument('server_name')
@click.argument('tool_name')
@click.option('--args', help='JSON arguments for the tool')
def local_call_tool(server_name, tool_name, args):
    """Call a tool on a local MCP server"""
    try:
        async def _call_tool():
            # Parse arguments
            arguments = {}
            if args:
                try:
                    arguments = json.loads(args)
                except json.JSONDecodeError as e:
                    console.print(f"[red]Invalid JSON arguments: {e}[/red]")
                    return

            with console.status(f"[bold cyan]Calling {tool_name} on {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                result = await mcp_client_manager.call_tool(server_name, tool_name, arguments)

            # Display result
            if result['success']:
                console.print(f"[green]Tool executed successfully[/green]")
                if result.get('content'):
                    console.print("[bold]Content:[/bold]")
                    for content_block in result['content']:
                        if content_block['type'] == 'text':
                            console.print(Markdown(content_block['text']))
                        elif content_block['type'] == 'image':
                            console.print(f"[dim]Image: {content_block.get('mimeType', 'unknown')}[/dim]")
            else:
                console.print(f"[red]Tool execution failed: {result.get('error', 'Unknown error')}[/red]")

        asyncio.run(_call_tool())

    except Exception as e:
        console.print(f"[red]Error calling tool {tool_name} on {server_name}: {e}[/red]")


@mcp.command()
@click.option('--host', default='127.0.0.1', help='Host to bind the proxy server to')
@click.option('--port', default=8001, type=int, help='Port to bind the proxy server to')
@click.option('--https/--no-https', default=False, help='Enable HTTPS with self-signed certificate')
@click.option('--cert-file', help='Path to SSL certificate file (for HTTPS)')
@click.option('--key-file', help='Path to SSL private key file (for HTTPS)')
@click.option('--ngrok/--no-ngrok', default=False, help='Expose server publicly using ngrok')
@click.option('--ngrok-token', help='ngrok authentication token (required for ngrok)')
def proxy(host, port, https, cert_file, key_file, ngrok, ngrok_token):
    """Start MCP proxy server to expose local servers as HTTP/HTTPS endpoints"""
    try:
        from .mcp_proxy import start_proxy_server
        console.print(f"[green]Starting MCP Proxy Server on {host}:{port}[/green]")

        if https:
            console.print("[yellow]HTTPS enabled with self-signed certificate[/yellow]")
        if ngrok:
            console.print("[blue]Ngrok tunnel will be established for public access[/blue]")
            if not ngrok_token:
                console.print("[yellow]Warning: No ngrok token provided. Make sure ngrok is authenticated.[/yellow]")

        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")

        # Start the proxy server
        start_proxy_server(
            host=host,
            port=port,
            use_https=https,
            cert_file=cert_file,
            key_file=key_file,
            use_ngrok=ngrok,
            ngrok_auth_token=ngrok_token
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]MCP Proxy Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting MCP proxy server: {e}[/red]")

@mcp.command()
def proxy_stop():
    """Stop the background MCP proxy server"""
    try:
        # Check if proxy is running by trying to connect to it
        import requests
        response = requests.get(f"http://{config_manager.proxy_host}:{config_manager.proxy_port}/", timeout=2)
        if response.status_code == 200:
            console.print("[yellow]Proxy server is running. To stop it, exit all CLI processes.[/yellow]")
            console.print("[dim]The proxy runs in a daemon thread and stops when the CLI process terminates.[/dim]")
        else:
            console.print("[green]Proxy server is not running.[/green]")
    except requests.exceptions.RequestException:
        console.print("[green]Proxy server is not running.[/green]")

    console.print("\n[bold]Background proxy behavior:[/bold]")
    console.print("• Starts automatically when auto-start is enabled")
    console.print("• Runs in daemon thread during CLI sessions")
    console.print("• Stops automatically when CLI process exits")
    console.print("• Each CLI command starts a new proxy instance")


@mcp.command()
@click.argument('server_name')
def local_resources(server_name):
    """List resources available on a local MCP server"""
    try:
        async def _list_resources():
            with console.status(f"[bold cyan]Fetching resources from {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                resources = await mcp_client_manager.list_resources(server_name)

            if not resources:
                console.print(f"[yellow]No resources available on {server_name}.[/yellow]")
                return

            table = Table(title=f"Resources on {server_name}")
            table.add_column("URI", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Description", style="white")
            table.add_column("MIME Type", style="green")

            for resource in resources:
                uri = resource['uri']
                if len(uri) > 50:
                    uri = uri[:47] + "..."

                description = resource.get('description', '')
                if len(description) > 60:
                    description = description[:57] + "..."

                table.add_row(
                    uri,
                    resource.get('name', 'N/A'),
                    description,
                    resource.get('mimeType', 'N/A')
                )

            console.print(table)

        asyncio.run(_list_resources())

    except Exception as e:
        console.print(f"[red]Error listing resources for {server_name}: {e}[/red]")

@mcp.command()
@click.argument('server_name')
@click.argument('uri')
def local_read_resource(server_name, uri):
    """Read a resource from a local MCP server"""
    try:
        async def _read_resource():
            with console.status(f"[bold cyan]Reading resource {uri} from {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                result = await mcp_client_manager.read_resource(server_name, uri)

            console.print(f"[bold]Resource:[/bold] {result['uri']}")
            console.print("[bold]Content:[/bold]")

            for content in result['content']:
                if content['type'] == 'text':
                    console.print(Markdown(content['text']))
                elif content['type'] == 'blob':
                    console.print(f"[dim]Binary data ({content.get('mimeType', 'unknown')}): {len(content['blob'])} bytes[/dim]")

        asyncio.run(_read_resource())

    except Exception as e:
        console.print(f"[red]Error reading resource {uri} from {server_name}: {e}[/red]")

@mcp.command()
@click.argument('server_name')
def local_prompts(server_name):
    """List prompts available on a local MCP server"""
    try:
        async def _list_prompts():
            with console.status(f"[bold cyan]Fetching prompts from {server_name}...[/bold cyan]"):
                # Ensure configs are loaded
                mcp_client_manager.load_server_configs()

                prompts = await mcp_client_manager.list_prompts(server_name)

            if not prompts:
                console.print(f"[yellow]No prompts available on {server_name}.[/yellow]")
                return

            table = Table(title=f"Prompts on {server_name}")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Arguments", style="green")

            for prompt in prompts:
                description = prompt.get('description', '')
                if len(description) > 80:
                    description = description[:77] + "..."

                args_list = prompt.get('arguments', [])
                args_display = ', '.join(f"{arg['name']}{' (required)' if arg.get('required') else ''}" for arg in args_list)
                if len(args_display) > 40:
                    args_display = args_display[:37] + "..."

                table.add_row(
                    prompt['name'],
                    description,
                    args_display if args_list else "[dim]None[/dim]"
                )

            console.print(table)

        asyncio.run(_list_prompts())

    except Exception as e:
        console.print(f"[red]Error listing prompts for {server_name}: {e}[/red]")

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

# Agent mode command
@cli.command()
@click.option('--enable/--disable', default=None, help='Enable or disable agent mode')
def agent_mode(enable):
    """Manage agent mode for device tool execution"""
    if enable is None:
        # Show current status
        current_status = "[green]ENABLED[/green]" if config_manager.agent_mode else "[red]DISABLED[/red]"
        console.print(f"Agent mode is currently: {current_status}")
        console.print("\nAgent mode allows the CLI to act as an agent on your device:")
        console.print("  • Automatically discovers and shares local MCP tools with the API")
        console.print("  • Executes device-based tool calls locally when requested")
        console.print("  • Returns tool execution results back to the API")
        console.print("\nUse --enable or --disable to change the setting.")
    else:
        config_manager.agent_mode = enable
        status = "[green]ENABLED[/green]" if enable else "[red]DISABLED[/red]"
        console.print(f"Agent mode {status}")

# Helper functions for agent mode
async def _execute_device_tool(chunk):
    """Execute a device tool call locally"""
    try:
        tool = chunk.get('tool', {})
        server_name = tool.get('server_name')
        tool_name = tool.get('name')
        arguments = tool.get('arguments', {})

        if not server_name or not tool_name:
            console.print(f"[red]Invalid device tool call: missing server_name or tool_name[/red]")
            return None

        # Execute the tool using MCP client
        result = await mcp_client_manager.call_tool(server_name, tool_name, arguments)

        if result['success']:
            console.print(f"[green]✓[/green] [dim]Device tool executed: {server_name}.{tool_name}[/dim]")
            return result
        else:
            console.print(f"[red]✗[/red] [dim]Device tool failed: {server_name}.{tool_name}[/dim]")
            return result

    except Exception as e:
        console.print(f"[red]Error executing device tool: {e}[/red]")
        return {'success': False, 'error': str(e)}

async def _send_tool_result(room_id, tool_chunk, tool_result):
    """Send tool execution result back to the API"""
    try:
        # tool_call_id lives inside the nested "tool" object
        tool_call_id = tool_chunk.get('tool', {}).get('id')  # ← was tool_chunk.get('tool_call_id')
        
        result_data = {
            'tool_call_id': tool_call_id,
            'result': {
                'success': tool_result.get('success', False),
                'content': tool_result.get('content', []),
                'error': tool_result.get('error'),
                'mode': 'device'
            }
        }

        # Send the result to the API
        response = api._post(f'/api/v1/chats/{room_id}/tool-result/', result_data)

        # if response.status == 200:
        #     console.print(f"[dim]Tool result sent to API[/dim]")
        # else:
        #     console.print(f"[yellow]Warning: Failed to send tool result to API ({response.status_code})[/yellow]")

    except Exception as e:
        console.print(f"[red]Error sending tool result to API: {e}[/red]")

if __name__ == '__main__':
    cli()
