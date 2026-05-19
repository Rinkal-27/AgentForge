import { useEffect, useState } from "react";
import { api, type AgentCard, type RouteResult } from "./api";
import AgentCardList from "./components/AgentCardList";
import MarkdownOutput from "./components/MarkdownOutput";
import RouteResultView from "./components/RouteResultView";

type Mode = "route" | "single";

const EXAMPLES = [
  "Write a Python function to debounce a callback, then have the reviewer critique it for thread-safety.",
  "Analyze a CSV of e-commerce orders (order_id, customer_id, amount, country, ts) and suggest charts.",
  "Design the empty-state copy for a new AI inbox feature and explain the rationale.",
];

export default function App() {
  const [agents, setAgents] = useState<AgentCard[]>([]);
  const [agentError, setAgentError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("route");
  const [selectedAgent, setSelectedAgent] = useState<string>("coder");
  const [task, setTask] = useState("");
  const [maxSteps, setMaxSteps] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [singleOutput, setSingleOutput] = useState<string | null>(null);
  const [routeResult, setRouteResult] = useState<RouteResult | null>(null);

  async function refreshAgents() {
    setAgentError(null);
    try {
      const data = await api.listAgents();
      setAgents(data);
    } catch (e) {
      setAgentError(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    void refreshAgents();
  }, []);

  async function run() {
    if (!task.trim()) return;
    setLoading(true);
    setError(null);
    setSingleOutput(null);
    setRouteResult(null);
    try {
      if (mode === "route") {
        const r = await api.routeTask(task, maxSteps);
        setRouteResult(r);
      } else {
        const r = await api.sendTask(selectedAgent, task);
        setSingleOutput(r.output);
      }
      void refreshAgents(); // refresh latency stats
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛠️</span>
            <div>
              <h1 className="text-lg font-semibold">AgentForge</h1>
              <p className="text-xs text-slate-400">
                A2A + MCP marketplace · powered by Groq Llama
              </p>
            </div>
          </div>
          <div className="text-xs text-slate-500 font-mono truncate max-w-xs">
            {api.baseUrl}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 grid lg:grid-cols-[1fr_1.4fr] gap-8">
        {/* Left: agent cards + controls */}
        <section className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm uppercase tracking-wider text-slate-400">
                Agents
              </h2>
              <button
                onClick={() => void refreshAgents()}
                className="text-xs text-slate-400 hover:text-slate-200"
              >
                Refresh
              </button>
            </div>
            {agentError && (
              <div className="text-xs text-red-400 mb-2">
                Cannot reach backend: {agentError}
              </div>
            )}
            <AgentCardList
              agents={agents}
              selected={mode === "single" ? selectedAgent : null}
              onSelect={(n) => {
                setMode("single");
                setSelectedAgent(n);
              }}
            />
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
            <div>
              <h3 className="text-xs uppercase tracking-wider text-slate-400 mb-2">
                Mode
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={() => setMode("route")}
                  className={`flex-1 text-sm rounded-lg py-2 border ${
                    mode === "route"
                      ? "border-indigo-400 bg-indigo-500/10 text-indigo-200"
                      : "border-slate-700 bg-slate-900 text-slate-300"
                  }`}
                >
                  Auto-route
                </button>
                <button
                  onClick={() => setMode("single")}
                  className={`flex-1 text-sm rounded-lg py-2 border ${
                    mode === "single"
                      ? "border-indigo-400 bg-indigo-500/10 text-indigo-200"
                      : "border-slate-700 bg-slate-900 text-slate-300"
                  }`}
                >
                  Pick agent
                </button>
              </div>
            </div>

            {mode === "route" ? (
              <label className="block text-xs text-slate-400">
                max_steps: <span className="text-slate-200">{maxSteps}</span>
                <input
                  type="range"
                  min={1}
                  max={6}
                  value={maxSteps}
                  onChange={(e) => setMaxSteps(Number(e.target.value))}
                  className="w-full accent-indigo-400 mt-1"
                />
              </label>
            ) : (
              <div className="text-xs text-slate-400">
                Selected:{" "}
                <span className="text-slate-200 font-medium">
                  {selectedAgent}
                </span>
              </div>
            )}
          </div>

          <div>
            <h3 className="text-xs uppercase tracking-wider text-slate-400 mb-2">
              Examples
            </h3>
            <div className="space-y-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setTask(ex)}
                  className="block w-full text-left text-xs text-slate-300 hover:text-slate-100 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Right: task input + output */}
        <section className="space-y-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-400 mb-2">
              Task
            </label>
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              rows={5}
              placeholder="Describe what you want done…"
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-sm placeholder:text-slate-600 focus:outline-none focus:border-indigo-400"
            />
            <div className="mt-3 flex items-center justify-end">
              <button
                onClick={() => void run()}
                disabled={loading || !task.trim()}
                className="rounded-lg bg-indigo-500 hover:bg-indigo-400 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2"
              >
                {loading ? "Running…" : "Run"}
              </button>
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-900 bg-red-500/10 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {loading && (
            <div className="text-sm text-slate-400 animate-pulse">
              Calling agents on Groq…
            </div>
          )}

          {singleOutput && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <MarkdownOutput text={singleOutput} />
            </div>
          )}

          {routeResult && <RouteResultView result={routeResult} />}
        </section>
      </main>

      <footer className="max-w-6xl mx-auto px-6 py-8 text-center text-xs text-slate-600">
        Built with FastAPI · FastMCP · React · Groq · ❤️
      </footer>
    </div>
  );
}
