# AgentForge 🛠️

> A2A + MCP marketplace of specialist Llama agents — built free with Groq, FastAPI, FastMCP and React.

AgentForge exposes a small team of role-specialised LLM agents (Coder, Analyst, Designer, Reviewer) behind **two complementary protocols**:

- **A2A (Agent-to-Agent)** — REST endpoints describing agents and accepting tasks (`/.well-known/agents.json`, `/agents/{name}/tasks`, `/tasks/route`).
- **MCP (Model Context Protocol)** — same agents exposed as MCP tools so any MCP-compatible client (Claude Desktop, Cursor, VS Code) can call them.

An internal **LLM router** decomposes a high-level request into a multi-step plan and delegates each step to the best specialist.

## Architecture

```
                              ┌─────────────────────────┐
   Browser (React UI) ───────►│   FastAPI (A2A REST)    │
                              │  /.well-known/agents... │
                              │  /agents/{name}/tasks   │──┐
   MCP client (Claude/Cursor)─►│   FastMCP (/mcp)        │  │
                              └─────────────────────────┘  │
                                            ▲              │
                                            │              ▼
                                     ┌──────┴──────┐  ┌──────────┐
                                     │  Router LLM │  │ Specialists│
                                     │  (Groq 70B) │─►│ Coder       │
                                     └─────────────┘  │ Analyst     │
                                                      │ Designer    │
                                                      │ Reviewer    │
                                                      └─────────────┘
```

## Quick start

### 1. Backend

```bash
cp .env.example .env  # add your GROQ_API_KEY
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m agentforge.server         # serves A2A + MCP on http://localhost:8000
```

Endpoints:

- `GET  /health`
- `GET  /.well-known/agents.json` — agent directory
- `GET  /agents/{name}/card` — single agent card
- `POST /agents/{name}/tasks` — run a single agent
- `POST /tasks/route` — let the router plan + execute across agents
- `POST /mcp` — MCP Streamable HTTP endpoint

### 2. React frontend

```bash
cd frontend
cp .env.example .env       # point VITE_API_URL at your backend
npm install
npm run dev                # http://localhost:5173
```

Build for production:

```bash
npm run build              # output in frontend/dist
```

## Deploy free

- **Backend** → Render (`render.yaml` included). Set `GROQ_API_KEY` and `CORS_ORIGINS` (your Vercel URL).
- **Frontend** → Vercel / Netlify / Cloudflare Pages. Set `VITE_API_URL` to the Render URL.

## CLI

```bash
python -m agentforge.cli --agent coder "write a python LRU cache"
python -m agentforge.cli "analyze cohort retention and visualize it"   # auto-route
```

## MCP usage

Point any MCP client at `https://<your-render-url>/mcp`. Tools exposed:

- `list_agents`
- `ask_coder`, `ask_analyst`, `ask_designer`, `ask_reviewer`
- `route_task_tool`
