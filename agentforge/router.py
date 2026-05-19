"""LLM-powered router that decomposes a task into a sequence of agent calls."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from .agents import AGENTS, get_agent
from .llm import get_llm


def _agent_catalog() -> str:
    lines = []
    for a in AGENTS.values():
        skills = ", ".join(s.name for s in a.skills)
        lines.append(f"- {a.name}: {a.description} (skills: {skills})")
    return "\n".join(lines)


_PLAN_SYSTEM = (
    "You orchestrate a small marketplace of specialist agents. "
    "Given a user task, produce a plan: an ordered list of steps, each "
    "step calls exactly one agent. Each later step may reference the "
    "output of earlier steps using `{{stepN}}` placeholders.\n\n"
    "Available agents:\n{catalog}\n\n"
    "Reply ONLY with strict JSON of the shape:\n"
    '{{"plan": [{{"agent": "coder|analyst|designer|reviewer", '
    '"task": "...", "uses": [0, 1]}}, ...]}}\n'
    "Keep the plan minimal -- typically 1 to 4 steps. End with a `reviewer` "
    "step when the task produces an artifact worth reviewing."
)


def _make_plan(task: str, max_steps: int) -> List[Dict[str, Any]]:
    llm = get_llm(size="large", temperature=0.0)
    resp = llm.invoke(
        [
            SystemMessage(content=_PLAN_SYSTEM.format(catalog=_agent_catalog())),
            HumanMessage(content=f"User task:\n{task}\n\nMax steps: {max_steps}"),
        ]
    )
    match = re.search(r"\{.*\}", resp.content, flags=re.DOTALL)
    if not match:
        # fallback: single coder step
        return [{"agent": "coder", "task": task, "uses": []}]
    try:
        data = json.loads(match.group(0))
        plan = data.get("plan", [])
    except json.JSONDecodeError:
        return [{"agent": "coder", "task": task, "uses": []}]

    # Validate & clamp
    cleaned: List[Dict[str, Any]] = []
    for step in plan[:max_steps]:
        if step.get("agent") not in AGENTS:
            continue
        cleaned.append(
            {
                "agent": step["agent"],
                "task": str(step.get("task", "")).strip() or task,
                "uses": [int(i) for i in step.get("uses", []) if isinstance(i, int)],
            }
        )
    return cleaned or [{"agent": "coder", "task": task, "uses": []}]


def _resolve_placeholders(text: str, outputs: List[str]) -> str:
    def repl(m: re.Match[str]) -> str:
        idx = int(m.group(1))
        return outputs[idx] if 0 <= idx < len(outputs) else m.group(0)

    return re.sub(r"\{\{step(\d+)\}\}", repl, text)


def route_task(task: str, max_steps: int = 4) -> Dict[str, Any]:
    """Plan the task with the router, then dispatch to each agent in order."""
    plan = _make_plan(task, max_steps=max_steps)
    trace: List[Dict[str, Any]] = []
    outputs: List[str] = []

    for i, step in enumerate(plan):
        agent = get_agent(step["agent"])
        context_parts = [outputs[j] for j in step["uses"] if 0 <= j < len(outputs)]
        context = "\n\n---\n\n".join(context_parts) if context_parts else None
        resolved_task = _resolve_placeholders(step["task"], outputs)
        output = agent.invoke(resolved_task, context=context)
        outputs.append(output)
        trace.append(
            {
                "step": i,
                "agent": agent.name,
                "task": resolved_task,
                "uses": step["uses"],
                "output_preview": output[:400],
            }
        )

    return {
        "task": task,
        "plan": plan,
        "trace": trace,
        "final": outputs[-1] if outputs else "",
    }
