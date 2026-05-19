export type AgentSkill = { name: string; description: string };

export type AgentCard = {
  name: string;
  display_name: string;
  description: string;
  model: string;
  skills: AgentSkill[];
  avg_latency_ms: number | null;
  invocations: number;
};

export type RouteStep = {
  step: number;
  agent: string;
  task: string;
  uses: number[];
  output_preview: string;
};

export type RouteResult = {
  task: string;
  plan: { agent: string; task: string; uses: number[] }[];
  trace: RouteStep[];
  final: string;
};

const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return (await res.json()) as T;
}

export const api = {
  baseUrl: API_URL,

  listAgents(): Promise<AgentCard[]> {
    return jsonFetch<AgentCard[]>("/.well-known/agents.json");
  },

  sendTask(agent: string, task: string, context?: string) {
    return jsonFetch<{ agent: string; output: string }>(
      `/agents/${agent}/tasks`,
      { method: "POST", body: JSON.stringify({ task, context: context ?? null }) }
    );
  },

  routeTask(task: string, max_steps: number) {
    return jsonFetch<RouteResult>("/tasks/route", {
      method: "POST",
      body: JSON.stringify({ task, max_steps }),
    });
  },

  health() {
    return jsonFetch<{ status: string; agents: string[] }>("/health");
  },
};
