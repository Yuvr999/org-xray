# ORG-XRAY

**AI-powered enterprise procurement intelligence platform** — built to eliminate shadow IT, prevent invoice fraud, and give organizations real-time visibility into every rupee spent.

> Live demo → **[https://org-xray-web-ylo3.onrender.com](https://org-xray-web-ylo3.onrender.com)**

---

## What Is ORG-XRAY?

ORG-XRAY is a full-stack procurement intelligence dashboard designed for mid-to-large enterprises. It sits on top of your existing procurement data and uses AI to surface problems that traditional ERP systems miss:

- **Employees raising demand requests that bypass approved vendor lists** (shadow IT)
- **Invoices that don't match purchase orders** (three-way mismatch fraud)
- **Idle assets sitting in storage** that could be reallocated instead of repurchased
- **Approval bottlenecks** killing procurement velocity
- **Policy violations** nobody caught until the quarter-end audit

Think of it as a co-pilot for your procurement manager — one that reads every PO, invoice, and vendor contract in real time and flags what matters before it becomes a problem.

---

## Feature Overview

| Module | What It Does |
|--------|-------------|
| **Process Mining** | Visualizes your end-to-end procurement workflow. Spots bottlenecks, duplicate approvals, and out-of-sequence steps using event log analysis. |
| **Invoice Verification** | Matches invoices against POs. Catches GSTIN mismatches, quantity discrepancies, and duplicate submissions before payment is released. |
| **Demand Routing** | Classifies incoming purchase requests by department and intent. Routes them to the right approver and flags any that touch shadow-IT categories. |
| **Asset Recovery** | Tracks asset lifecycle. Shows idle hardware that can be reassigned before a new PO is raised for the same equipment. |
| **Governance & Compliance** | Policy violation scoring, approval matrix enforcement, and an immutable audit trail for every action taken in the system. |
| **AI Copilot** | A Gemini-powered chat assistant that answers procurement policy questions, queries vendor databases, and explains approval rules in plain English. |

---

## Tech Stack

### Frontend
- **React 18** + TypeScript
- **Vite** — for fast dev server and optimized production builds
- **Tailwind CSS v4** — utility-first styling with CSS custom properties
- **Framer Motion** — page transitions and micro-animations
- **Lucide React** — icon set

### Backend
- **FastAPI** (Python 3.11) — async REST API
- **SQLAlchemy 2.0** (async ORM) + **aiosqlite** for local dev / **PostgreSQL** for production
- **Alembic** — database migrations
- **Google Gemini API** — LLM integration (gemini-2.0-flash → gemini-1.5-flash cascade fallback)
- **JWT** — stateless auth tokens
- **scikit-learn** — local ML model for demand classification

### Infrastructure
- **Render** — cloud deployment (free tier)
- **Docker** — containerized local development
- **GitHub Actions** — CI/CD pipeline

---

## Project Structure

```
org-xray/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/v1/         # Route handlers (invoices, assets, demands, auth...)
│   │   │   ├── core/           # Config, DB engine, middleware, logging
│   │   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── schemas/        # Pydantic request/response schemas
│   │   │   ├── services/       # Business logic (LLM gateway, GSTIN verifier...)
│   │   │   └── ml/             # Demand classifier model
│   │   ├── alembic/            # Database migration scripts
│   │   ├── tests/              # Pytest test suite
│   │   └── requirements.txt
│   │
│   └── web/                    # React frontend
│       └── src/
│           ├── components/     # Reusable UI components (layout, modals, charts)
│           ├── views/          # Full-page modules (ProcessMining, Invoices, etc.)
│           ├── context/        # AppContext — global state
│           ├── lib/            # API client, mock data, utilities
│           └── styles/         # Global CSS tokens
│
├── render.yaml                 # Render.com infrastructure-as-code
├── docker-compose.yml          # Local dev environment
└── .env.example                # Environment variable reference
```

---

## Getting Started

### Prerequisites

- **Node.js** v20+ and **npm** v10+
- **Python** 3.11+
- **Docker** (optional — for local PostgreSQL + Redis)

### 1. Clone the repo

```bash
git clone https://github.com/Yuvr999/org-xray.git
cd org-xray
```

### 2. Set up environment variables

```bash
cp .env.example apps/api/.env
```

Open `apps/api/.env` and fill in:

```env
SECRET_KEY=your-secret-key-min-32-chars
GEMINI_API_KEY=your-google-gemini-api-key   # from https://aistudio.google.com
```

For the frontend, create `apps/web/.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

### 3. Start the backend

```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.  
Interactive docs → `http://localhost:8000/api/v1/docs`

### 4. Start the frontend

```bash
cd apps/web
npm install
npm run dev
```

Frontend → `http://localhost:5173`

### 5. (Optional) Docker Compose for full stack

```bash
# From project root
docker-compose up --build
```

This starts the API, the web dev server, PostgreSQL, and Redis together.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | JWT signing key (min 32 chars, random) |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for the AI Copilot |
| `GEMINI_MODEL` | — | Model name (default: `gemini-2.0-flash`) |
| `DATABASE_URL` | — | DB connection string (defaults to SQLite for local dev) |
| `ENVIRONMENT` | — | `development` or `production` |
| `CORS_ORIGINS` | — | Comma-separated list of allowed frontend origins |
| `REDIS_URL` | — | Redis connection string (optional — disables caching if unset) |
| `LOG_LEVEL` | — | `DEBUG`, `INFO`, `WARNING` (default: `INFO`) |

---

## Demo Login Credentials

The app ships with a seeded demo dataset. Use any of these to log in:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Manager | `manager` | `manager123` |
| Employee | `employee` | `employee123` |

Each role unlocks a different default view:
- **Admin** → Process Mining dashboard (full access)
- **Manager** → Governance & compliance view
- **Employee** → Demand routing form

---

## Deployment on Render

The project includes a `render.yaml` blueprint for one-click deployment.

1. Push your fork to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Connect your GitHub repo
4. Render will create two services:
   - `org-xray-api` — Python web service (FastAPI)
   - `org-xray-web` — Static site (React build)
5. After deploy, go to the **API service → Environment** tab and set `GEMINI_API_KEY`

> **Note:** The free tier API service sleeps after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to respond — this is normal Render free-tier behavior.

---

## API Overview

Base URL: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login and receive JWT token |
| `GET` | `/health` | Service health check |
| `GET` | `/invoices/` | List all invoices |
| `POST` | `/invoices/verify` | Run three-way match verification |
| `GET` | `/assets/` | List assets with telemetry data |
| `GET` | `/demands/` | List procurement demand requests |
| `POST` | `/demands/classify` | AI-powered demand department routing |
| `POST` | `/assistant/query` | Chat with the AI Copilot |
| `GET` | `/governance/policies` | Fetch active compliance policies |

Full interactive docs are available at `/api/v1/docs` (Swagger UI).

---

## How the AI Copilot Works

The AI Copilot in the right drawer routes user queries through a **LLM Gateway** service:

1. Query is enriched with relevant context (vendor data, policies, assets) from the database
2. A versioned system prompt is loaded based on query type (`policy_rag/v1`, `demand_classifier/v1`, etc.)
3. The enriched prompt is sent to Gemini via the REST API
4. If Gemini is unavailable or the API key is invalid, a **deterministic local fallback engine** synthesizes a policy-grounded response from the cached procurement rules
5. Response is returned with metadata: model version, latency, token count

This means the app works even without a Gemini API key — it just falls back to rule-based answers.

---

## Running Tests

```bash
cd apps/api
pytest tests/ -v
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for setup details, coding conventions, and the PR checklist.

---

## Architecture

For a deeper look at system design decisions, data flow, and the ML pipeline, see [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

## Roadmap

- [ ] PostgreSQL production database (Supabase integration)
- [ ] Real-time WebSocket notifications for approval events
- [ ] ERP integration connectors (SAP, Oracle, Zoho Books)
- [ ] Multi-tenant organization support
- [ ] Export procurement reports to PDF/Excel
- [ ] Mobile-responsive layout improvements
- [ ] Role-based access control (RBAC) with granular permissions
