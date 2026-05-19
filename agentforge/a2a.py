"""A2A-style FastAPI app: agent directory, cards, and task endpoints."""
from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agents import AGENTS, get_agent
from .cards import AgentCard
from .router import route_task


class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1)
    context: str | None = None


class TaskResponse(BaseModel):
    agent: str
    output: str


class RouteRequest(BaseModel):
    task: str = Field(..., min_length=1)
    max_steps: int = Field(4, ge=1, le=6)


def create_a2a_app() -> FastAPI:
    app = FastAPI(title="AgentForge A2A", version="0.1.0")

    origins_env = os.environ.get("CORS_ORIGINS", "*")
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "agents": list(AGENTS)}

    @app.get("/.well-known/agents.json", response_model=List[AgentCard])
    def well_known() -> List[AgentCard]:
        return [a.card() for a in AGENTS.values()]

    @app.get("/agents/{name}/card", response_model=AgentCard)
    def agent_card(name: str) -> AgentCard:
        try:
            return get_agent(name).card()
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    @app.post("/agents/{name}/tasks", response_model=TaskResponse)
    def send_task(name: str, req: TaskRequest) -> TaskResponse:
        try:
            agent = get_agent(name)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        output = agent.invoke(req.task, context=req.context)
        return TaskResponse(agent=agent.name, output=output)

    @app.post("/tasks/route")
    def route(req: RouteRequest) -> Dict[str, Any]:
        return route_task(req.task, max_steps=req.max_steps)

    return app
