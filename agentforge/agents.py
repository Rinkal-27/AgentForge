"""Specialist agents. Each one wraps a Groq Llama model with a focused system prompt."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from .cards import AgentCard, AgentSkill, Timer, stat_for
from .llm import get_llm


@dataclass
class Agent:
    name: str
    display_name: str
    description: str
    system_prompt: str
    skills: List[AgentSkill]
    size: str = "large"  # "large" | "small"
    temperature: float = 0.2

    def model_name(self) -> str:
        if self.size == "small":
            return os.environ.get("MODEL_SMALL", "llama-3.1-8b-instant")
        return os.environ.get("MODEL_LARGE", "llama-3.3-70b-versatile")

    def card(self) -> AgentCard:
        avg_ms, invocations = stat_for(self.name).snapshot()
        return AgentCard(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            model=self.model_name(),
            skills=self.skills,
            avg_latency_ms=avg_ms,
            invocations=invocations,
        )

    def invoke(self, task: str, context: str | None = None) -> str:
        llm = get_llm(size=self.size, temperature=self.temperature)
        user = task if not context else f"Context:\n{context}\n\nTask:\n{task}"
        with Timer(self.name):
            resp = llm.invoke(
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user),
                ]
            )
        return resp.content


# --- Specialist roster -------------------------------------------------------

CODER = Agent(
    name="coder",
    display_name="Coder",
    description="Writes, refactors, and debugs code in any common language.",
    system_prompt=(
        "You are a senior software engineer. Produce clean, idiomatic, "
        "production-ready code. Default to Python 3.11 unless the task says "
        "otherwise. Always include a short rationale at the top in a comment "
        "block, then the code. Avoid placeholder TODOs."
    ),
    skills=[
        AgentSkill(name="write_code", description="Implement a feature from a spec."),
        AgentSkill(name="refactor", description="Improve readability without changing behavior."),
        AgentSkill(name="debug", description="Locate and fix bugs in given code."),
    ],
    size="large",
    temperature=0.1,
)

ANALYST = Agent(
    name="analyst",
    display_name="Analyst",
    description="Extracts insights from data and proposes visualizations.",
    system_prompt=(
        "You are a data analyst. Given a dataset description or raw data, "
        "produce: (1) 3-5 concrete insights with supporting numbers, (2) a "
        "recommended chart per insight (chart type + axes), (3) any obvious "
        "data-quality concerns. Be specific; never invent numbers not in the data."
    ),
    skills=[
        AgentSkill(name="summarize_data", description="Headline insights from a dataset."),
        AgentSkill(name="suggest_charts", description="Recommend visualizations."),
        AgentSkill(name="spot_anomalies", description="Identify data quality issues."),
    ],
    size="large",
    temperature=0.2,
)

DESIGNER = Agent(
    name="designer",
    display_name="Designer",
    description="Writes UX copy, microcopy, and wireframe layouts in text form.",
    system_prompt=(
        "You are a product designer. Produce concise UX copy, microcopy, and "
        "low-fidelity wireframe layouts described in plain text or simple "
        "ASCII. Justify each design choice in one sentence. Optimize for "
        "clarity and accessibility."
    ),
    skills=[
        AgentSkill(name="ux_copy", description="Headlines, buttons, error messages."),
        AgentSkill(name="wireframe", description="Text-based wireframe layouts."),
        AgentSkill(name="design_rationale", description="Explain a design decision."),
    ],
    size="small",  # cheaper/faster — designer responses are short
    temperature=0.4,
)

REVIEWER = Agent(
    name="reviewer",
    display_name="Reviewer",
    description="Critiques an artifact for correctness, clarity, and security.",
    system_prompt=(
        "You are a rigorous reviewer. Given an artifact (code, copy, analysis, "
        "or design), output a Markdown review with three sections: "
        "**Strengths**, **Issues** (numbered, severity-tagged High/Med/Low), "
        "and **Recommended changes**. Be specific and actionable. "
        "If the artifact is code, also check for OWASP-style security issues."
    ),
    skills=[
        AgentSkill(name="review_code", description="Code review with severity-tagged issues."),
        AgentSkill(name="review_copy", description="Critique UX/marketing copy."),
        AgentSkill(name="review_analysis", description="Sanity-check an analyst report."),
    ],
    size="large",
    temperature=0.1,
)


AGENTS: Dict[str, Agent] = {
    a.name: a for a in (CODER, ANALYST, DESIGNER, REVIEWER)
}


def get_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise KeyError(f"Unknown agent: {name}. Available: {list(AGENTS)}")
    return AGENTS[name]
