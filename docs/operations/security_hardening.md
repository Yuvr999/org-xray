# Security Hardening & Compliance Runbook

## 1. Security Architecture & Principles
- **Least Privilege**: Application runs as unprivileged user `appuser` (UID 10001) in Docker.
- **Defense in Depth**: Security headers middleware enforces HSTS, CSP, X-Frame-Options: `DENY`, X-Content-Type-Options: `nosniff`, and Referrer-Policy.
- **Server-Authoritative RBAC**: Authorization enforced strictly at endpoint dependencies.
- **Zero Client Secrets**: No LLM, DB, or GSTIN API credentials exposed in frontend bundles.

---

## 2. OWASP Top 10 Mitigations
- **Injection**: Parameterized queries via SQLAlchemy async ORM; inputs validated via Pydantic v2 models.
- **Broken Authentication**: JWT tokens with bcrypt-hashed passwords (cost factor >= 12); rate limiting on auth endpoints.
- **Sensitive Data Exposure**: HTTPS/TLS in transit; passwords and tokens never written to audit logs; environment-based secrets.
- **Security Misconfiguration**: Debug modes disabled in production (`ENVIRONMENT=production`); CORS allowlist restricted to verified domains.
- **Vulnerable Dependencies**: Automated vulnerability scanning in CI via Bandit and Safety/pip-audit.

---

## 3. Secret Management & Rotation
- Never commit `.env` or secrets to git.
- Rotate `SECRET_KEY` and database passwords every 90 days.
- When rotating `SECRET_KEY`, issue a rolling key transition to minimize invalidating active sessions.

---

## 4. Rate Limiting Policy
- **Public & Health**: 120 req/minute per IP.
- **Authentication (`/auth/login`)**: 30 req/minute per IP to prevent brute-force attacks.
- **AI & OCR endpoints (`/assistant/query`, `/invoices/upload`)**: 30 req/minute per authenticated user.
