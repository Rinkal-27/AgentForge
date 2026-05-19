"""AgentForge — A2A + MCP marketplace of specialist Groq agents."""
from .agents import AGENTS
from .router import route_task

__all__ = ["AGENTS", "route_task"]
