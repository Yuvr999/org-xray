# Architecture — ORG-XRAY

This document covers the high-level system design, data flow, and key architectural decisions behind ORG-XRAY.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│                                                             │
│   React 18 + TypeScript (Vite)                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │ Process  │  │ Invoice  │  │  Demand  │  │  Asset   │  │
│   │  Mining  │  │  Verify  │  │  Router  │  │ Recovery │  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                     ↓ REST / JSON                           │
└────────────────────────────────────────────────────────────-┘
                       ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Python 3.11)               │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Auth     │  │ Invoice  │  │ Demand   │  │ Assistant  │ │
│  │ Router   │  │ Router   │  │ Router   │  │ Router     │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
│                       ↓                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Service Layer                         │ │
│  │  LLM Gateway │ GSTIN Verifier │ Demand Classifier      │ │
│  └────────────────────────────────────────────────────────┘ │
│                       ↓                                     │
│  ┌──────────────────────┐   ┌──────────────────────────┐   │
│  │  SQLAlchemy (async)  │   │  Google Gemini API (ext) │   │
│  │  SQLite / PostgreSQL │   │  gemini-2.0-flash         │   │
│  └──────────────────────┘   └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### State Management

Global application state is managed in a single `AppContext` (React Context API). This holds:

- `invoices` — fetched invoice records
- `demands` — active procurement demand requests
- `assets` — hardware/software asset inventory
- `shadowAlerts` — flagged shadow-IT detections
- `customFeatures` — user-defined feature toggles (persisted to localStorage)

No Redux or Zustand — the app's data access patterns are simple enough that context with `useReducer` is sufficient and adds no dependency overhead.

### Routing

The app uses **in-component tab routing** rather than React Router. Each tab switch is animated with Framer Motion's `AnimatePresence`. This decision was made because:

1. There are only 6 views — a full router adds complexity without benefit at this scale
2. Each view is a heavy, data-fetching component — lazy loading via React Suspense would be the next step if the bundle grows

### API Client

All HTTP calls go through `getApiUrl()` in `src/lib/api.ts`. This function reads `VITE_API_URL` at build time (injected by Vite) and prefixes all endpoint paths. This keeps all env-dependent URL logic in one place.

---

## Backend Architecture

### Layered Design

```
apps/api/app/
├── api/v1/          ← HTTP layer: route handlers only, no business logic
├── services/        ← Business logic: LLM calls, GSTIN validation, ML inference
├── models/          ← SQLAlchemy ORM models (database schema)
├── schemas/         ← Pydantic models (request/response validation)
├── core/            ← Cross-cutting: config, DB engine, logging, middleware
└── ml/              ← Demand classification model (scikit-learn)
```

Route handlers are intentionally thin — they validate input (via Pydantic), call the relevant service, and return a response. All logic lives in services.

### Database

- **Local development**: SQLite via `aiosqlite` (zero-config, no external dependency)
- **Production**: PostgreSQL recommended (Render managed DB or Supabase)
- **ORM**: SQLAlchemy 2.0 async — all queries use `async with session:` pattern
- **Migrations**: Alembic — run `alembic upgrade head` to apply migrations

The connection string is read from `DATABASE_URL`. If it's a `sqlite://` URL, the engine is initialized without connection pooling (SQLite doesn't support it). If it's a `postgresql://` URL, standard pool settings apply.

### LLM Gateway

`app/services/llm_gateway.py` is the single integration point for all AI capabilities.

**How it works:**

1. Caller passes a `prompt_id` (e.g., `"policy_rag/v1"`) and user message
2. Gateway loads the corresponding versioned system prompt from `app/core/prompts.py`
3. If `GEMINI_API_KEY` is set, it builds the Gemini REST payload and attempts the call
4. Model cascade: tries the configured model first, then falls back through `gemini-2.0-flash → gemini-1.5-flash → gemini-2.5-flash → gemini-1.5-pro`
5. If all models fail or no key is set, a **deterministic fallback engine** generates a policy-grounded response from cached procurement rules
6. Returns a structured response with latency, token count, and model version metadata

This design means the system **always returns an answer** — even with no internet or no API key.

### Demand Classifier

`apps/api/app/ml/` contains a lightweight scikit-learn classifier trained on procurement request text. It assigns incoming demands to departments (`Technical`, `Finance`, `PR`, `General`) and returns a confidence score.

The ML model runs locally — no external API call needed for this feature.

### Security

- JWT-based authentication (`pyjwt` + `bcrypt`)
- `SecurityHeadersMiddleware` adds `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` headers
- `RequestCorrelationMiddleware` adds a `X-Request-ID` to every request for tracing
- CORS is restricted to known frontend origins in production (configured via `CORS_ORIGINS` env var)

---

## Deployment Architecture (Render)

```
GitHub (master branch)
        ↓ push triggers auto-deploy
  ┌──────────────────────────────┐
  │  Render Blueprint (oxyrayss) │
  │                              │
  │  org-xray-api  (web service) │  ← Python, Oregon, port $PORT
  │  org-xray-web  (static site) │  ← React build, global CDN
  └──────────────────────────────┘
```

- The **API service** runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- The **static site** runs `npm install && npm run build` and serves `dist/`
- `VITE_API_URL` is baked into the frontend bundle at build time — it must point to the deployed API URL
- SQLite is used on Render free tier (no managed DB needed). The database file is ephemeral — it resets on each deploy. For persistent storage, switch `DATABASE_URL` to a PostgreSQL connection string.
- The API service sleeps after 15 minutes of inactivity on the free tier. First request after sleep takes ~30 seconds.

---

## Key Design Decisions

### Why FastAPI over Django/Flask?

FastAPI's async-first design pairs well with concurrent LLM API calls. Its automatic OpenAPI docs generation and Pydantic integration reduce boilerplate significantly. The performance profile is also better than WSGI frameworks for I/O-bound workloads.

### Why SQLite for local dev?

Zero setup friction. A developer can clone the repo and run the backend in under 2 minutes without installing any database. Alembic handles the schema either way — switching to PostgreSQL for production is a one-line env var change.

### Why not Redux?

The data flow in ORG-XRAY is primarily: fetch on mount → display → user triggers action → re-fetch. Context + local state handles this cleanly. Adding Redux would introduce boilerplate (actions, reducers, selectors) without solving a real problem at this scale.

### Why Tailwind CSS v4?

The v4 alpha uses native CSS layers and `@import "tailwindcss"` instead of PostCSS configuration. This makes the build pipeline simpler and removes the `tailwind.config.js` file from the project root. The trade-off is slightly less community documentation, but the core utility API is stable.
