"""FastMCP server exposing every agent as MCP tools.

Mounted alongside the A2A FastAPI app in `server.py` so a single process
serves both protocols on the same port.
"""
from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

from .agents import AGENTS, get_agent
from .router import route_task

mcp = FastMCP(
    name="agentforge",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
)


@mcp.tool()
def list_agents() -> str:
    """Return all agent cards as JSON (name, skills, model, latency)."""
    return json.dumps([a.card().model_dump() for a in AGENTS.values()], indent=2)


@mcp.tool()
def ask_coder(task: str, context: str | None = None) -> str:
    """Ask the Coder to write/refactor/debug code."""
    return get_agent("coder").invoke(task, context=context)


@mcp.tool()
def ask_analyst(task: str, context: str | None = None) -> str:
    """Ask the Analyst to derive insights / suggest charts."""
    return get_agent("analyst").invoke(task, context=context)


@mcp.tool()
def ask_designer(task: str, context: str | None = None) -> str:
    """Ask the Designer for UX copy / wireframes / design rationale."""
    return get_agent("designer").invoke(task, context=context)


@mcp.tool()
def ask_reviewer(target: str, criteria: str | None = None) -> str:
    """Have the Reviewer critique `target` (code/copy/analysis). Optional criteria."""
    task = "Review the following artifact."
    if criteria:
        task += f"\nFocus on: {criteria}"
    return get_agent("reviewer").invoke(task, context=target)


@mcp.tool()
def route_task_tool(task: str, max_steps: int = 4) -> str:
    """Let the LLM router decompose `task` and dispatch it across agents."""
    max_steps = max(1, min(int(max_steps), 6))
    return json.dumps(route_task(task, max_steps=max_steps), indent=2)
