# 🛠️ AgentForge

> A live, free-to-run **A2A + MCP marketplace** of specialist LLM agents — built with Groq Llama, FastAPI, FastMCP, and React.

**🔗 Live demo:** **https://agent-forge-seven-nu.vercel.app/**
**🧠 Backend (A2A REST + MCP):** `[https://agentforge-y34u.onrender.com](https://agentforge-y34u.onrender.com)`

AgentForge is a working reference implementation of an **agent marketplace**: a directory of role-specialised AI agents that can be **discovered, called individually, or orchestrated together** by an LLM-powered router. The same agents are exposed over two industry-standard protocols at once — **A2A** for agent-to-agent communication and **MCP** for tool-style integration with IDEs and chat clients.

---

## ✨ What is an "agent marketplace"?

Think of it as an **App Store for AI agents**. Each agent:

1. Publishes a public **Agent Card** describing who it is, what skills it has, what model it runs on, and how fast/expensive it is.
2. Exposes a **standard endpoint** (`POST /agents/{name}/tasks`) so any other agent — or a UI, or a CLI, or a script — can hire it for a task.
3. Plays nicely with a **router agent** that can read all the cards, plan multi-step work, and delegate each step to the best specialist.

AgentForge ships with four specialists:

| Agent | Emoji | Model | Specialty |
|---|---|---|---|
| **Coder** | 💻 | Llama 3.3 70B | Production code, algorithms, debugging |
| **Analyst** | 📊 | Llama 3.3 70B | Data analysis, statistics, visualisation specs |
| **Designer** | 🎨 | Llama 3.1 8B | UX writing, design rationale, fast iteration |
| **Reviewer** | 🔍 | Llama 3.3 70B | Code review, critique, security & quality checks |

---

## 📖 Key terms (decoded)

- **LLM** — Large Language Model. The reasoning engine. AgentForge uses [Groq](https://groq.com)-hosted Llama models for near-instant inference.
- **Agent** — An LLM bound to a *role*, a *system prompt*, and (optionally) *tools*. In AgentForge, each agent is a stateless function: `task → output`.
- **Agent Card** — A machine-readable description of an agent (skills, model, cost, latency). Other agents read cards to decide who to delegate to. Inspired by Google's [A2A protocol spec](https://google.github.io/A2A/).
- **A2A (Agent-to-Agent Protocol)** — A simple REST contract so agents from different vendors / frameworks can talk to each other. AgentForge implements the essential parts:
  - `GET  /.well-known/agents.json` → directory of agents
  - `GET  /agents/{name}/card` → one agent card
  - `POST /agents/{name}/tasks` → hire that agent for a single task
  - `POST /tasks/route` → ask the router to plan + execute across multiple agents
- **MCP (Model Context Protocol)** — Anthropic's open standard for exposing tools/resources to LLM clients (Claude Desktop, Cursor, VS Code Copilot, …). The same four agents are also exposed as MCP tools (`ask_coder`, `ask_analyst`, `route_task_tool`, …) over **Streamable HTTP** transport.
- **FastMCP** — The Python framework used to implement the MCP server (`mcp.server.fastmcp.FastMCP`).
- **Router** — A meta-agent (Llama 70B) that reads the directory, decomposes a high-level request into a JSON plan, and runs each step through the appropriate specialist. Step outputs are fed forward via `{{stepN}}` placeholders.
- **Streamable HTTP** — MCP transport that uses standard HTTP + Server-Sent Events. Lets you host an MCP server publicly without WebSockets.

---

## 🏗️ Architecture

```
                 ┌──────────────────────────────────────────────┐
                 │             FastAPI (single port)            │
 Browser (React) │                                              │
    ─────────────►   A2A REST  /.well-known/agents.json         │
                 │              /agents/{name}/tasks            │
                 │              /tasks/route                    │
 MCP client      │                                              │
 (Claude/Cursor) │   FastMCP   /mcp  (Streamable HTTP)          │
    ─────────────►                                              │
                 └────────────────────┬─────────────────────────┘
                                      │
                              ┌───────▼────────┐
                              │  Router (LLM)  │  plan + delegate
                              └───────┬────────┘
              ┌─────────────┬─────────┴─────────┬──────────────┐
              ▼             ▼                   ▼              ▼
          💻 Coder     📊 Analyst          🎨 Designer    🔍 Reviewer
         (Llama 70B)  (Llama 70B)         (Llama 8B)    (Llama 70B)
```

Everything runs on **free tiers**: Groq free LLM quota, Render free web service for the backend, Vercel for the React frontend.

---

## 🚀 Quick start (local)

### Backend (Python 3.11)

```bash
cd projects/agentforge
cp .env.example .env          # add your GROQ_API_KEY (https://console.groq.com)
python -m venv .venv
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
python -m agentforge.server    # http://localhost:8000
```

### Frontend (Vite + React)

```bash
cd projects/agentforge/frontend
cp .env.example .env           # VITE_API_URL=http://localhost:8000
npm install
npm run dev                    # http://localhost:5173
```

### CLI (no UI needed)

```bash
python -m agentforge.cli "analyze user retention and recommend charts"
python -m agentforge.cli --agent coder "write a thread-safe LRU cache in Python"
```

---

## 🧪 Try it via curl

```bash
BASE="https://agent-forge-seven-nu.vercel.app"   # frontend
API="https://agentforge-y34u.onrender.com"          # backend

# List agents
curl $API/.well-known/agents.json | jq

# Hire one agent
curl -X POST $API/agents/coder/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a Python decorator that retries on TimeoutError with exponential backoff."}'

# Let the router plan + execute
curl -X POST $API/tasks/route \
  -H "Content-Type: application/json" \
  -d '{"task": "Design and implement a simple URL shortener API, then review it.", "max_steps": 4}'
```

---

## 🔌 Use AgentForge as an MCP server

In Claude Desktop / Cursor / VS Code, add a streamable-HTTP MCP server pointing at:

```
https://https://agentforge-y34u.onrender.com/mcp
```

Available tools: `list_agents`, `ask_coder`, `ask_analyst`, `ask_designer`, `ask_reviewer`, `route_task_tool`.

---

## ☁️ Deploy your own (free)

| Component | Host | Notes |
|---|---|---|
| Backend (FastAPI + MCP) | [Render](https://render.com) | `render.yaml` included. Set `GROQ_API_KEY`, `CORS_ORIGINS=<your-vercel-url>`. |
| Frontend (React) | [Vercel](https://vercel.com) | Root Directory: `frontend`, env var `VITE_API_URL=<your-render-url>`. |

Why this split? Vercel's serverless functions don't fit MCP's persistent Streamable-HTTP sessions, so the backend lives on Render (free web service, cold-start ~30s). The static React bundle is perfect for Vercel.

---

## 🧱 Project structure

```
projects/agentforge/
├── agentforge/
│   ├── a2a.py            # FastAPI app — A2A REST endpoints + CORS
│   ├── mcp_server.py     # FastMCP tools (same agents, MCP protocol)
│   ├── server.py         # Single entrypoint: mounts A2A + MCP on one port
│   ├── agents.py         # Coder / Analyst / Designer / Reviewer
│   ├── router.py         # LLM-powered plan-and-execute
│   ├── cards.py          # AgentCard model + latency telemetry
│   ├── llm.py            # Groq factory
│   └── cli.py            # Terminal interface
├── frontend/             # Vite + React + TypeScript UI
│   ├── src/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   └── components/
│   └── vercel.json
├── requirements.txt
├── render.yaml
├── Procfile
└── README.md
```

---

## 🛡️ Security notes

- The free demo uses `CORS_ORIGINS=*` for convenience — lock this down to your Vercel URL for any real use.
- Never commit `.env`. The `.gitignore` covers it but always check `git status` before pushing.
- Rotate your `GROQ_API_KEY` if you ever paste it anywhere outside `.env`.

---

## 📜 License

MIT — feel free to fork, remix, and use as a starting point for your own agentic systems.

---

Built with ❤️ to demonstrate **A2A + MCP + Agentic AI** on a fully free stack.
