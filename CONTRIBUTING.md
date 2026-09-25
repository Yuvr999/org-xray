# Contributing to ORG-XRAY

Thanks for taking the time to contribute! This document covers everything you need to get set up and submit a clean pull request.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Coding Conventions](#coding-conventions)
- [Branch & Commit Strategy](#branch--commit-strategy)
- [Pull Request Checklist](#pull-request-checklist)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Development Setup

### Backend (FastAPI)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env   # then edit .env with your values
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)

```bash
cd apps/web
npm install
# Create .env.local:
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### Running Tests

```bash
# Backend
cd apps/api
pytest tests/ -v

# Frontend (if you add Vitest tests)
cd apps/web
npm run test
```

---

## Coding Conventions

### Python (Backend)

- Follow **PEP 8** — use `black` for formatting
- All route handlers must have **Pydantic schemas** for both request body and response
- Business logic lives in `app/services/` — keep route handlers thin
- Use async/await throughout — no synchronous DB calls
- Log meaningful events using the shared `logger` from `app/core/logging`

```bash
# Format before committing
pip install black
black apps/api/
```

### TypeScript (Frontend)

- Use **functional components** with hooks — no class components
- Keep components small and focused — if a file exceeds ~200 lines, split it
- Global state goes in `AppContext` — don't create new context providers without discussion
- Use Tailwind utility classes only — no inline `style={{}}` props for visual styling
- All API calls go through `getApiUrl()` from `src/lib/api.ts`

```bash
# Lint before committing
cd apps/web
npm run lint
```

---

## Branch & Commit Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code — Render deploys from here |
| `dev` | Integration branch for in-progress features |
| `feat/<name>` | Feature branches — branch off `dev` |
| `fix/<name>` | Bug fix branches |

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(invoice): add three-way PO match validation
fix(auth): token expiry not refreshed on re-login
refactor(llm): extract prompt builder to separate module
chore(deps): bump fastapi to 0.115.5
```

---

## Pull Request Checklist

Before opening a PR, make sure:

- [ ] Code is formatted (`black` for Python, Prettier/ESLint for TS)
- [ ] Tests pass (`pytest` / `npm run test`)
- [ ] No console errors in the browser
- [ ] New features have a corresponding entry in the **Roadmap** section of README if applicable
- [ ] Environment variables are documented in `.env.example`
- [ ] PR title follows the Conventional Commits format
- [ ] PR description explains **what** changed and **why** (not just how)

---

## Reporting Bugs

Open a GitHub Issue with:

1. **What you expected** to happen
2. **What actually happened** (include the full error message or screenshot)
3. **Steps to reproduce** (as minimal as possible)
4. **Environment**: OS, Node version, Python version, browser

---

## Requesting Features

Open a GitHub Issue with the `enhancement` label. Describe:

1. The problem you're trying to solve
2. Your proposed solution
3. Any alternatives you considered

If it's a large change, we'll discuss design in the issue before any code is written.
