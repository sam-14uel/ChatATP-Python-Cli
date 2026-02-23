#!/usr/bin/env python3
"""
MCP Proxy Server - Exposes local MCP servers as HTTP/HTTPS endpoints with ngrok support
"""

import asyncio
import json
import logging
import ssl
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pyngrok import ngrok

from .mcp_client import mcp_client_manager

from .config import Config
from .api_client import ChatATPAPI

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ChatATP MCP Proxy Server",
    description="REST API proxy for local MCP servers with HTTPS and remote access support",
    version="1.0.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolCallRequest(BaseModel):
    arguments: Dict[str, Any] = {}

class ResourceReadRequest(BaseModel):
    pass

@app.get("/")
async def root(request: Request):
    """Root endpoint with server information"""
    configs = mcp_client_manager.load_server_configs()

    # Get public URL if using ngrok
    public_url = getattr(app, 'public_url', None)
    scheme = "https" if getattr(app, 'use_https', False) else "http"

    return {
        "name": "ChatATP MCP Proxy Server",
        "version": "1.0.1",
        "scheme": scheme,
        "local_url": f"{scheme}://{request.url.hostname}:{request.url.port}",
        "public_url": public_url,
        "servers": list(configs.keys()),
        "endpoints": {
            "tools": "/tools/{server_name}/{tool_name}",
            "resources": "/resources/{server_name}/{uri}",
            "prompts": "/prompts/{server_name}",
            "servers": "/servers"
        }
    }

@app.get("/servers")
async def list_servers():
    """List all configured MCP servers"""
    configs = mcp_client_manager.load_server_configs()
    servers = []

    for server_name, config in configs.items():
        try:
            # Try to get server info
            info = await mcp_client_manager.initialize_client(server_name)
            servers.append({
                "name": server_name,
                "config": config,
                "info": info,
                "status": "connected"
            })
        except Exception as e:
            servers.append({
                "name": server_name,
                "config": config,
                "error": str(e),
                "status": "error"
            })

    return {"servers": servers}

@app.get("/servers/{server_name}")
async def get_server_info(server_name: str):
    """Get information about a specific MCP server"""
    configs = mcp_client_manager.load_server_configs()
    if server_name not in configs:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")

    try:
        info = await mcp_client_manager.initialize_client(server_name)
        return {
            "name": server_name,
            "config": configs[server_name],
            "info": info,
            "status": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to server: {str(e)}")

@app.get("/servers/{server_name}/tools")
async def list_server_tools(server_name: str):
    """List tools available on a specific MCP server"""
    try:
        tools = await mcp_client_manager.list_tools(server_name)
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.post("/tools/{server_name}/{tool_name}")
async def call_tool(server_name: str, tool_name: str, request: ToolCallRequest):
    """Call a tool on a specific MCP server"""
    try:
        result = await mcp_client_manager.call_tool(
            server_name=server_name,
            tool_name=tool_name,
            arguments=request.arguments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to call tool: {str(e)}")

@app.get("/resources/{server_name}/{uri:path}")
async def read_resource(server_name: str, uri: str):
    """Read a resource from a specific MCP server"""
    try:
        result = await mcp_client_manager.read_resource(server_name, uri)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(e)}")

@app.get("/servers/{server_name}/resources")
async def list_server_resources(server_name: str):
    """List resources available on a specific MCP server"""
    try:
        resources = await mcp_client_manager.list_resources(server_name)
        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")

@app.get("/servers/{server_name}/prompts")
async def list_server_prompts(server_name: str):
    """List prompts available on a specific MCP server"""
    try:
        prompts = await mcp_client_manager.list_prompts(server_name)
        return {"prompts": prompts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")

def generate_self_signed_cert(cert_file: str, key_file: str):
    """Generate a self-signed SSL certificate for HTTPS"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    import datetime

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ChatATP"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write certificate and key files
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

def start_ngrok_tunnel(port: int, use_https: bool = False) -> str:
    """Start ngrok tunnel and return the public URL"""
    try:       
        # Disconnect any existing tunnels to avoid conflicts
        existing_tunnels = ngrok.get_tunnels()
        for tunnel in existing_tunnels:
            ngrok.disconnect(tunnel.public_url)
            logger.info(f"Disconnected existing tunnel: {tunnel.public_url}")

        # Configure ngrok
        tunnel_config = {
            "addr": port,
            "proto": "https" if use_https else "http"
        }

        # Start tunnel
        tunnel = ngrok.connect(**tunnel_config)
        public_url = tunnel.public_url

        logger.info(f"Ngrok tunnel established: {public_url}")
        return public_url

    except ImportError:
        logger.error("pyngrok not installed. Install with: pip install pyngrok")
        raise
    except Exception as e:
        logger.error(f"Failed to start ngrok tunnel: {e}")
        raise

def start_proxy_server(host: str = "127.0.0.1", port: int = 8001, use_https: bool = False,
                       cert_file: str = None, key_file: str = None, use_ngrok: bool = False,
                       ngrok_auth_token: str = None):
    """Start the MCP proxy server with HTTPS and ngrok support"""
    logger.info(f"Starting MCP Proxy Server on {host}:{port}")

    # Configure ngrok if requested
    public_url = None
    if use_ngrok:
        try:
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
            public_url = start_ngrok_tunnel(port, use_https)
            app.public_url = public_url
            logger.info(f"Public URL: {public_url}")
            # Also print to console so it's visible in CLI
            print(f"\n🎉 MCP Proxy Server is now publicly accessible at: {public_url}")
            print("Remote MCP clients can connect to your local servers via this URL\n")

            # Register proxy with ChatATP API (hybrid mode)
            try:
                config = Config()
                api = ChatATPAPI(config)
                servers = mcp_client_manager.get_available_servers()
                api.register_proxy(public_url, servers)
                logger.info(f"Successfully registered proxy with ChatATP API: {public_url} with servers {servers}")
                print(f"🔗 Registered proxy with ChatATP API (hybrid mode enabled)\n")
            except Exception as e:
                logger.warning(f"Failed to register proxy with ChatATP API: {e}")
                print(f"⚠️  Proxy registration failed, but server is still running: {e}\n")
        except Exception as e:
            logger.warning(f"Failed to start ngrok tunnel: {e}")
            print(f"\n⚠️  Failed to establish ngrok tunnel: {e}")
            print("Server will run locally only\n")

    # Configure HTTPS if requested
    ssl_context = None
    if use_https:
        if cert_file and key_file:
            # Use provided certificates
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
        else:
            # Generate self-signed certificate
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_f:
                cert_file = cert_f.name
            with tempfile.NamedTemporaryFile(mode='w', suffix='.key', delete=False) as key_f:
                key_file = key_f.name

            generate_self_signed_cert(cert_file, key_file)
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            logger.info("Using self-signed SSL certificate")

        app.use_https = True
    else:
        app.use_https = False

    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        ssl_keyfile=key_file if use_https else None,
        ssl_certfile=cert_file if use_https else None
    )
