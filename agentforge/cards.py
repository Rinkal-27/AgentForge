"""Agent Card schema (A2A convention) + simple in-memory latency tracker."""
from __future__ import annotations

from collections import deque
from threading import Lock
from time import perf_counter
from typing import Deque, Dict, List

from pydantic import BaseModel, Field


class AgentSkill(BaseModel):
    name: str
    description: str


class AgentCard(BaseModel):
    name: str
    display_name: str
    description: str
    model: str
    skills: List[AgentSkill]
    input_modes: List[str] = Field(default_factory=lambda: ["text"])
    output_modes: List[str] = Field(default_factory=lambda: ["text"])
    avg_latency_ms: float | None = None
    invocations: int = 0


class _LatencyStat:
    """Tracks a rolling window of recent call latencies (ms)."""

    def __init__(self, window: int = 20) -> None:
        self._samples: Deque[float] = deque(maxlen=window)
        self._total = 0
        self._lock = Lock()

    def record(self, ms: float) -> None:
        with self._lock:
            self._samples.append(ms)
            self._total += 1

    def snapshot(self) -> tuple[float | None, int]:
        with self._lock:
            if not self._samples:
                return None, self._total
            return sum(self._samples) / len(self._samples), self._total


_STATS: Dict[str, _LatencyStat] = {}


def stat_for(agent_name: str) -> _LatencyStat:
    if agent_name not in _STATS:
        _STATS[agent_name] = _LatencyStat()
    return _STATS[agent_name]


class Timer:
    """Context manager that records elapsed ms into an agent's latency stat."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        self._start = 0.0

    def __enter__(self) -> "Timer":
        self._start = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        elapsed_ms = (perf_counter() - self._start) * 1000.0
        stat_for(self.agent_name).record(elapsed_ms)
