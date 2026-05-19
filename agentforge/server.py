"""Single-process entrypoint: A2A FastAPI + FastMCP (Streamable HTTP) on one port.

Run:
    python -m agentforge.server

Endpoints:
    REST/A2A:  http://HOST:PORT/...
    MCP:       http://HOST:PORT/mcp
"""
from __future__ import annotations

import os

import uvicorn
from dotenv import load_dotenv

from .a2a import create_a2a_app
from .mcp_server import mcp

load_dotenv()


def build_app():
    app = create_a2a_app()
    # FastMCP exposes a Starlette app for streamable-http transport.
    app.mount("/", mcp.streamable_http_app())
    return app


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(build_app(), host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
