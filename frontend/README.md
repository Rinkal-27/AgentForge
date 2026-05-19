# AgentForge frontend

Vite + React + TypeScript UI for the [AgentForge](../README.md) A2A backend. Uses Tailwind via CDN for styling and `react-markdown` for rendering agent output.

## Develop

```bash
cp .env.example .env       # set VITE_API_URL to your backend (default http://localhost:8000)
npm install
npm run dev                # http://localhost:5173
```

## Build

```bash
npm run build              # static site in dist/
npm run preview            # preview the build locally
```

## Deploy (free)

The build is a fully static SPA — push it to any free host:

- **Vercel** — `vercel` from this folder. Set the `VITE_API_URL` env var to your Render backend URL.
- **Netlify** — drag-and-drop `dist/` or connect the repo with build command `npm run build` and publish dir `dist`.
- **Cloudflare Pages** — same: `npm run build`, output `dist`.

Make sure the backend's `CORS_ORIGINS` env var lists your deployed frontend origin (or `*` for any).
