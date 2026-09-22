# ORG-XRAY — Real-World Functional Build Plan (Antigravity + AI/ML)

## 0. Scope lock

This plan converts the existing ORG-XRAY specification into a production-oriented implementation plan while preserving the documented product modules, algorithms, roles, and terminology.

**Explicitly out of scope for this phase:** visual design, UI/UX design, branding, typography, component styling, animations, dashboard aesthetics, responsive-layout decisions, and design-system decisions.

The UI layer should remain functional and implementation-friendly using the existing React structure, but no UI/UX redesign work should be undertaken until the separate UI/UX specification is provided.

### Lean-scope decisions for this plan

The following items are intentionally removed from the build scope unless a later business requirement explicitly reintroduces them:

- advanced vendor prediction features such as vendor churn/availability prediction and other speculative vendor ML;
- opaque vendor "trust" scoring as a decision authority; vendor data is retained, but factual operational metrics are used instead;
- learning-to-rank for asset reuse; asset matching remains transparent/rule-based for the first release;
- ML-based IoT/time-series anomaly detection; v1 physical monitoring uses deterministic thresholds and status transitions;
- refund/credit-note automation inside the returns module; returns remain a request/status/audit workflow;
- budget forecasting and a separate budget-management subsystem; purchase limits and approval policies remain;
- separate analytics warehouse; PostgreSQL queries/materialized views are sufficient initially;
- autonomous AI action execution; the assistant can retrieve information, explain, recommend, and create drafts, but cannot execute final approvals or purchasing actions;
- mobile applications, blockchain, custom autonomous-agent frameworks, and other platform expansions unrelated to the documented ORG-XRAY workflows.

These cuts reduce implementation risk and keep the first production version focused on the documented ORG-XRAY capabilities.

---

## 1. Source baseline to preserve

The current specification defines ORG-XRAY as an enterprise process-intelligence and procurement-governance platform covering procurement workflows, shadow-process detection, duplicate-invoice flagging, GSTIN verification, asset lifecycle management, and physical sensor monitoring.

The documented frontend baseline is React 19 + Vite + TypeScript, with React Router v7, route-level code splitting, RBAC for employee/manager/admin, React Context state, and localStorage persistence. The main service areas are invoice, shadow-process, demand, event-log, analytics, and AI-chat services. [Source: ORG-XRAY specification]

Core functional modules to preserve:

1. Process Mining & Shadow Process Intelligence
2. Smart Invoice Ingestion & Verification
3. GSTIN Verification
4. Demand Routing & Procurement Assistant
5. Physical Infrastructure & Asset Recovery
6. Procurement/approval governance flows implied by the service/page structure
7. Returns and activity/event logging flows present in the project structure

The documented business rules include the composite shadow score, GSTIN checksum validation, keyword-based demand routing, invoice duplicate detection, 18% GST arithmetic validation, asset reallocation, and IoT status monitoring. These are the functional baseline, not to be discarded during the productionization effort.

---

## 2. Target outcome

Build a real, multi-user application where:

- users authenticate against a real identity system;
- business data is stored in a real transactional database;
- files are uploaded to durable object storage;
- invoice processing can handle text and scanned PDFs;
- critical verification runs on the server, not only in the browser;
- AI/ML services have observable inputs, outputs, confidence, versioning, and fallback behavior where AI/ML is actually used;
- procurement recommendations are grounded in approved organization data and policies;
- approvals are transactional and auditable;
- sensor/asset events can arrive continuously;
- every material decision can be traced to data, rules, model version, or human feedback;
- the application can be deployed to staging and production with repeatable CI/CD;
- the existing React SPA remains the application client, while business-critical logic moves behind secure APIs.

---

## 3. Recommended production architecture

```text
                                   ┌───────────────────────────┐
                                   │   React 19 / TS / Vite   │
                                   │ Existing ORG-XRAY SPA    │
                                   └─────────────┬─────────────┘
                                                 │ HTTPS / JSON
                                                 ▼
                              ┌────────────────────────────────────┐
                              │ API / Application Backend         │
                              │ Auth • RBAC • Workflows • CRUD    │
                              │ Approvals • Audit • Integrations │
                              └──────────────┬─────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
          ┌─────────────────┐     ┌─────────────────┐      ┌──────────────────┐
          │ PostgreSQL      │     │ Redis / Queue   │      │ Object Storage   │
          │ transactional DB│     │ jobs/cache      │      │ PDFs, exports    │
          └─────────────────┘     └────────┬────────┘      └──────────────────┘
                                           │
                     ┌─────────────────────┼────────────────────────┐
                     │                     │                        │
                     ▼                     ▼                        ▼
             ┌───────────────┐     ┌────────────────┐      ┌─────────────────┐
             │ Invoice/OCR   │     │ ML/AI workers  │      │ Event/IoT worker│
             │ extraction    │     │ models + RAG   │      │ anomaly engine  │
             └──────┬────────┘     └───────┬────────┘      └───────┬─────────┘
                    │                      │                       │
                    └──────────────────────┼───────────────────────┘
                                           ▼
                                ┌──────────────────────┐
                                │ Model / Rule Registry │
                                │ versions + thresholds │
                                └──────────────────────┘

External integrations:
- Identity provider / SSO
- Gemini / approved LLM endpoint
- GSTIN verification provider
- ERP / procurement source systems
- Email / notification provider
- IoT gateway / MQTT / HTTPS ingestion
```

### Architecture principle

The browser remains a client. It must not be trusted as the final authority for approvals, invoices, tax calculations, duplicate decisions, permissions, or AI policy checks.

---

## 4. Technology plan

### Frontend

Keep the documented baseline:

- React 19
- TypeScript
- Vite
- React Router v7
- Existing Context patterns initially, but move high-value server state to a query/cache layer where appropriate
- Existing PDF.js capability can remain as a client preview/helper, but production invoice processing must also have server-side processing

Do not redesign the UI.

### Backend

Recommended:

- Python + FastAPI for the primary backend because the platform needs AI/ML, document processing, data pipelines, and model-serving capabilities.
- Pydantic for API contracts and validation.
- SQLAlchemy + Alembic for PostgreSQL persistence and migrations.
- Background jobs via Celery/RQ/Arq or an equivalent queue system backed by Redis.

An equivalent TypeScript backend is acceptable if the implementation team strongly prefers Node.js, but AI/ML workers should remain Python-capable.

### Data

- PostgreSQL: source of truth for transactional/business data.
- Redis: queue, short-lived cache, rate limiting, locks.
- S3-compatible object storage: invoices, PDFs, attachments, exports, model artifacts where appropriate.
- pgvector within PostgreSQL for the procurement knowledge base.

### AI/ML

Use a hybrid architecture:

- deterministic rules for compliance-critical checks;
- classical ML for anomaly/detection/routing problems;
- LLMs for extraction assistance, explanations, conversational search, and policy-aware procurement assistance;
- retrieval-augmented generation for organization-specific information;
- human feedback to create labeled training/evaluation data.

### Observability

- structured JSON logs;
- metrics for latency, queue time, error rates, model confidence, false-positive feedback, and integration health;
- error tracking;
- immutable audit records for governance actions.

### Delivery

- Docker for local/staging/production parity;
- CI pipeline for lint, type check, unit tests, integration tests, security checks, migrations, build, and deploy;
- infrastructure-as-code recommended for production;
- separate development, staging, and production configuration/secrets.

---

## 5. Production data model

Create an explicit relational schema. At minimum:

### Organization and identity

- organizations
- users
- roles
- permissions
- user_roles
- departments
- approval_policies
- purchase_limits

### Procurement

- purchase_requests
- purchase_request_items
- approval_steps
- approval_actions
- vendors
- purchase_orders

### Invoices

- invoices
- invoice_items
- invoice_documents
- invoice_extractions
- invoice_validation_results
- invoice_duplicate_candidates
- invoice_duplicate_decisions

### Process intelligence

- process_definitions
- process_events
- process_cases
- process_variants
- shadow_alerts
- shadow_scores
- shadow_feedback
- process_anomaly_features

### Assets and physical infrastructure

- assets
- asset_assignments
- asset_returns
- asset_reallocations
- physical_areas
- sensors
- sensor_readings
- equipment_status_events
- infrastructure_alerts

### AI/ML governance

- model_versions
- model_predictions
- prompt_versions
- knowledge_documents
- knowledge_chunks
- feedback_labels
- evaluation_runs

### Platform operations

- notifications
- integration_connections
- integration_sync_runs
- activity_events
- audit_log
- job_runs
- idempotency_keys

Every major table should have stable IDs, timestamps, created/updated metadata, and organization scoping where multi-tenancy is enabled.

---

## 6. Authentication, authorization, and enterprise controls

Replace demo credentials and local session state with real authentication.

### Authentication

Implement one of:

- organization SSO/OIDC;
- managed identity provider;
- secure email/password only if SSO is not initially available.

Use short-lived access tokens and rotating refresh/session mechanisms. Keep secrets server-side.

### RBAC

Preserve the documented three roles:

- employee
- manager
- admin

Then implement permission-level authorization under the roles so that future roles do not require hard-coded route rewrites.

Examples:

- `demand:create`
- `invoice:submit`
- `invoice:approve`
- `shadow:review`
- `procurement:recommend`
- `purchase:approve`
- `asset:reallocate`
- `sensor:read`
- `admin:configure`
- `audit:read`

The backend must enforce authorization even when a user bypasses the frontend.

### Audit requirements

Record:

- who performed an action;
- when;
- organization/department;
- old/new values when appropriate;
- source IP/session metadata where policy allows;
- affected record;
- rule/model version when a machine decision was involved;
- human override and reason.

---

## 7. Process Mining & Shadow Process Intelligence

The documented shadow score is preserved:

`Shadow Score = 0.25*Deviation + 0.20*Recurrence + 0.15*Consistency + 0.15*CrossSystemActivity + 0.25*BusinessRisk`

with the documented score bands 0–30 Normal, 31–60 Process Variation, 61–80 Suspicious, 81–100 Strong Shadow Process.

### Production implementation

#### Step A — Event ingestion

Create a canonical event schema:

```text
case_id
organization_id
actor_id
actor_role
source_system
process_name
activity
activity_category
timestamp
object_id
amount
metadata
correlation_id
```

Sources can include ERP events, procurement systems, email-derived events, approved manual events, spreadsheet uploads, and application activity logs.

#### Step B — Normalize events

Map heterogeneous source events into canonical process activities.

Example:

`Excel purchase tracker updated` → `manual_purchase_tracking`

`PO submitted in ERP` → `purchase_order_submitted`

#### Step C — Official process model

Store the approved process definition and expected transitions.

#### Step D — Variant analysis

Build actual variants from event sequences and compare them with the official process model.

Metrics:

- missing expected steps;
- unexpected steps;
- repeated steps;
- timing deviation;
- unauthorized path frequency;
- cross-system handoff count.

#### Step E — Shadow score

Calculate the documented weighted score as the explainable governance score.

#### Step F — ML anomaly score

Add a separate ML anomaly score rather than silently changing the documented business score.

Candidate first model:

- engineered event-sequence features;
- frequency features;
- time-delay features;
- actor/process/source features;
- Isolation Forest or equivalent unsupervised anomaly detector for initial rollout.

Later, after sufficient labeled data:

- supervised classifier trained from manager feedback;
- sequence models if event volume justifies them.

#### Step G — Explainability

Each alert should contain:

- top contributing rule features;
- process deviation description;
- recurrence evidence;
- business-risk factors;
- ML confidence/anomaly score;
- historical context;
- recommended human review action.

Do not generate explanations that claim a fact not present in the supporting data.

#### Step H — Human feedback

Preserve the documented categories:

- Valid Shadow Process
- Normal Variation
- False Alert
- Needs Investigation

Persist every label. These labels become training/evaluation data.

### Acceptance criteria

A manager can trace an alert from raw events → normalized process sequence → score components → model output → human decision.

---

## 8. Smart Invoice Ingestion & Verification

The current documentation describes PDF.js client-side extraction of GSTIN, vendor, dates, line items and totals, plus duplicate detection and 18% GST arithmetic validation. Production must extend this beyond selectable-text PDFs.

### Pipeline

```text
Upload
  ↓
Malware/file validation
  ↓
Object storage
  ↓
Create invoice-processing job
  ↓
PDF/image preprocessing
  ↓
Text extraction OR OCR
  ↓
Field extraction
  ↓
Normalization
  ↓
Deterministic validation
  ↓
Duplicate candidate search
  ↓
ML duplicate scoring
  ↓
GSTIN verification
  ↓
Human review when confidence/risk is low
  ↓
Final invoice status
```

### Required extracted fields

- vendor name
- vendor GSTIN
- invoice number
- invoice date
- due date if present
- currency
- tax components
- taxable amounts
- line items
- subtotal
- total tax
- grand total
- purchase order/reference number
- document hash
- extraction confidence

### OCR strategy

Support:

1. text-layer extraction;
2. OCR for scanned PDFs/images;
3. field validation against invoice structure.

Do not store raw API keys in the browser.

### Duplicate detection v1

Use a cascade:

1. document hash/exact file match;
2. exact vendor + invoice number;
3. normalized vendor GSTIN + invoice number;
4. GSTIN + amount + date-window candidate search;
5. fuzzy field similarity;
6. optional embedding similarity for difficult near-duplicates.

Return candidate matches with evidence, not just a yes/no output.

### GST arithmetic

Preserve the documented 18% validation rule where the business policy explicitly requires it, but model the tax rate as data rather than hard-code it in all future logic. Validate taxable base, tax amount, total, rounding tolerance, and applicable tax components.

### Invoice state machine

`UPLOADED → PROCESSING → EXTRACTED → VALIDATED → REVIEW_REQUIRED / VERIFIED / REJECTED`

All state transitions are server-side and audited.

---

## 9. GSTIN verification

Preserve the documented MOD-36 checksum validation for structural verification.

Production flow:

```text
Input GSTIN
  ↓
Normalize uppercase / trim
  ↓
Format validation
  ↓
MOD-36 checksum
  ↓
Optional live provider verification
  ↓
Cache response with timestamp/provider metadata
  ↓
Return status + evidence
```

Separate these outcomes:

- structurally valid;
- structurally invalid;
- live provider verified;
- live provider unavailable;
- live provider returned negative result;
- verification stale.

Do not represent local checksum validity as proof that a GST registration is currently active.

The current specification supports a configurable GSTIN REST endpoint. The production version should wrap the selected provider behind an internal adapter so the frontend is independent of vendor choice.

---

## 10. Demand Routing & Procurement AI

The current implementation uses keyword rules to route demands to Finance, PR, or Technical and includes a Gemini-powered assistant for price estimation, vendors, and purchase-limit checks.

Preserve keyword rules as the deterministic fallback, then add ML/LLM routing.

### Routing pipeline

```text
Demand text
   ↓
Normalization
   ↓
Rule classifier
   ↓
ML classifier
   ↓
Confidence threshold
   ├── high confidence → route
   └── low confidence → human review / LLM assist
```

### Initial ML model

Train a multi-class text classifier for:

- Finance
- PR
- Technical

Features can begin with TF-IDF + linear model because it is easy to audit and cheap to operate. Move to embeddings or a transformer classifier once enough labeled organization-specific data exists.

### Procurement assistant

The assistant must use controlled tools rather than unrestricted database access.

Recommended tools:

- `get_purchase_limit(user, department)`
- `search_approved_vendors(category, region)`
- `get_recent_prices(item)`
- `search_procurement_policy(question)`
- `get_asset_reuse_candidates(item)`
- `create_draft_purchase_request(...)`

The LLM may retrieve information and create drafts. Server-side policy code remains the only authority for approval and final transaction state.

### RAG

Create a knowledge base from:

- procurement policies;
- approval matrix;
- approved-vendor lists;
- purchasing limits;
- product catalogs;
- contract summaries;
- FAQ/internal SOP material.

Store document metadata and chunk provenance. Every answer about organization policy should be traceable to source documents.

### Guardrails

- no direct unrestricted SQL from the LLM;
- no autonomous purchase-order or approval execution by the LLM;
- no approval bypass;
- no fabricated vendor facts;
- structured tool calls only;
- response citations/provenance for internal policy answers.

---

## 11. Approved vendor data

Use a normalized vendor profile only for facts needed by procurement workflows and the assistant:

- identity and GSTIN metadata;
- category;
- approval status;
- historical spend;
- order count;
- on-time rate;
- return/defect rate;
- invoice anomaly history;
- average lead time;
- price history where available;
- user/manager feedback.

Do not build a separate opaque vendor trust score or predictive vendor-risk program in the first production release. The assistant must present source-backed vendor facts rather than inventing or hiding a ranking model.

## 12. Asset lifecycle and reallocation intelligence

Preserve:

- assigned asset tracking;
- returned asset handling;
- reallocation to new purchase requests;
- reduction of redundant PO generation.

### Recommendation model

When a request is created, rank compatible existing assets using:

- asset type compatibility;
- technical specifications;
- current location;
- current assignment state;
- condition;
- warranty status;
- age/depreciation policy;
- expected remaining life;
- upcoming demand.

Keep the first production release rule-based and transparent. Reuse recommendations should be explainable from the compatibility and lifecycle fields above.

### Guardrail

Asset reallocation recommendation must never silently change ownership. A human-approved transaction must finalize assignment.

---

## 13. IoT / physical infrastructure monitoring

Create an ingestion endpoint and/or MQTT integration behind a gateway.

### Sensor record

```text
sensor_id
area_id
device_id
timestamp
metric_type
metric_value
unit
quality
```

### v1 alerting

Use deterministic thresholds and state transitions for:

- capacity/occupancy;
- temperature if available;
- equipment heartbeat;
- ONLINE / WARNING / MAINTENANCE.

Do not add ML or time-series anomaly detection to the first production release. The system should first establish clean, reliable sensor history and operational alert handling.

Alerts should include the measured signal, configured threshold result, timestamp, sensor, and recommended operational next step.

## 14. Returns and operational workflows

The existing structure includes return request management and email preview/return flows.

Productionize with:

- return request entity;
- reason code;
- supporting attachment;
- approval/status transitions;
- vendor linkage;
- communication event log;
- audit trail.

Keep communications recordable, but do not build automated refund/credit-note processing in this release.

---

## 15. Analytics layer

Keep KPI calculations server-side for consistency.

### Core metrics

- purchase-request volume;
- approval turnaround;
- procurement cycle time;
- shadow-process rate;
- invoice verification pass rate;
- duplicate invoice rate;
- GSTIN verification rate;
- asset reuse rate;
- avoided purchase count/value;
- vendor delivery performance;
- sensor warning/maintenance rate;
- AI recommendation acceptance rate;
- human override rate where applicable.

### Analytics architecture

Use PostgreSQL analytical queries/materialized views. Do not introduce a separate analytics warehouse in the first production release.

Every KPI must have:

- definition;
- time window;
- population/filter;
- source tables/events;
- timezone handling;
- test cases.

---

## 16. API contract plan

Use a versioned API, for example `/api/v1`.

### Example domains

```text
POST   /auth/session
GET    /me

POST   /demands
GET    /demands
GET    /demands/:id
POST   /demands/:id/classify
POST   /demands/:id/submit

POST   /invoices
GET    /invoices
GET    /invoices/:id
POST   /invoices/:id/reprocess
POST   /invoices/:id/review
GET    /invoices/:id/duplicates

POST   /gstin/verify

GET    /processes
GET    /processes/:id/variants
GET    /shadow-alerts
GET    /shadow-alerts/:id
POST   /shadow-alerts/:id/feedback

GET    /vendors
GET    /vendors/:id

GET    /assets
GET    /assets/:id
POST   /assets/:id/reallocate
GET    /assets/recommendations

GET    /physical/areas
GET    /physical/sensors
POST   /physical/events
GET    /physical/alerts

POST   /assistant/query
POST   /assistant/actions/preview

GET    /analytics/overview
GET    /analytics/procurement
GET    /analytics/processes

GET    /audit-log
GET    /health
GET    /ready
```

Generate TypeScript API types from the backend OpenAPI contract so frontend/backend drift is minimized.

---

## 17. Background-job design

Use asynchronous jobs for expensive or external operations.

### Job examples

- invoice OCR
- invoice extraction
- duplicate candidate scoring
- GSTIN external verification
- process event ingestion/normalization
- shadow-score recalculation
- ML prediction
- analytics aggregation
- notification dispatch
- document indexing/embedding for the approved procurement knowledge base

Every job needs:

- idempotency key;
- retry policy;
- timeout;
- dead-letter handling;
- status;
- structured error;
- trace/correlation ID.

---

## 18. AI/ML model lifecycle

Create a basic MLOps loop from the beginning.

```text
Raw data
  ↓
Label/clean
  ↓
Feature generation
  ↓
Train
  ↓
Offline evaluation
  ↓
Register model version
  ↓
Deploy
  ↓
Monitor confidence/error/feedback
  ↓
Retrain when threshold reached
```

### Required model metadata

- model name;
- version;
- training data window;
- feature version;
- evaluation metrics;
- threshold;
- deployment status;
- owner;
- created timestamp;
- rollback target.

### First models to build

1. Demand routing classifier
2. Process anomaly model

Invoice duplicate detection should begin with deterministic exact/fuzzy matching rather than requiring a separate ML model. Asset reuse remains rule-based, and IoT alerting remains threshold-based in the first release.

Use simple, auditable models first; only add a more complex model when measured performance and available labeled data justify it.

---

## 19. LLM engineering plan

Use the existing Gemini integration concept, but move it to the backend and treat the model as an untrusted reasoning component rather than a policy authority.

### LLM gateway responsibilities

- authentication to the provider;
- model selection;
- prompt versioning;
- token/cost controls;
- rate limiting;
- request/response logging with sensitive-data controls;
- timeout/retry;
- schema validation;
- fallback;
- evaluation hooks.

### Structured output

Require JSON-schema-constrained outputs for operations such as:

- demand classification;
- invoice field extraction;
- procurement recommendations;
- explanation generation;
- action proposals.

### Prompt registry

Store prompts by version:

`procurement_assistant/v1`, `invoice_extractor/v1`, etc.

Never silently modify production prompts without versioning.

---

## 20. Security plan

Minimum production controls:

- HTTPS only;
- secure cookies/token handling;
- CSRF protection where cookie-based auth is used;
- CORS allowlist;
- input validation;
- parameterized queries/ORM;
- rate limiting;
- file-type and size validation;
- malware scanning for uploaded documents;
- server-side authorization;
- secret manager/environment-based secrets;
- no provider API keys in frontend bundles;
- encrypted storage and transport;
- least-privilege service accounts;
- dependency and container vulnerability scanning;
- audit logging;
- backup and restore tests;
- database migration controls;
- retention/deletion policy for invoices and sensitive data.

For enterprise deployment, legal/compliance review must determine applicable India-specific tax, privacy, retention, data residency, and sector requirements instead of hard-coding assumptions into the application.

---

## 21. Testing strategy

### Unit tests

Cover:

- GSTIN checksum algorithm;
- normalization functions;
- shadow score math;
- score bands;
- routing fallback rules;
- tax calculations;
- duplicate matching;
- asset compatibility;
- permission checks;
- approval transition rules.

### Integration tests

Test:

- API → DB;
- API → queue;
- queue → worker;
- worker → object storage;
- worker → AI/ML service;
- external-provider failure/fallback;
- audit-log creation;
- approval transitions.

### AI/ML evaluation

Maintain fixed evaluation datasets.

Metrics:

- classification accuracy/F1 for routing;
- precision/recall for duplicate detection;
- false-positive rate for shadow alerts;
- ranking metrics for asset recommendations;
- anomaly precision at reviewed threshold;
- extraction field accuracy for invoices;
- LLM structured-output validity;
- grounded-answer rate for RAG;
- human acceptance/override rate.

### End-to-end tests

Use browser automation to test complete workflows without depending on visual design:

`login → create demand → route → submit → manager approval → audit record`

`upload invoice → extract → validate → duplicate check → review → finalize`

`create asset request → recommendation → manager approval → reallocation`

`sensor event → alert → manager/admin review`

---

## 22. Data quality and reliability

Add validation at ingestion boundaries.

Examples:

- duplicate event IDs ignored safely;
- invoice numbers normalized before matching;
- numeric currency precision enforced;
- timestamps stored in UTC and rendered in configured organization timezone;
- missing sensor data marked distinctly from zero-valued readings;
- soft-delete/retention semantics defined explicitly;
- external verification responses cached with provenance and expiry.

Build reconciliation jobs for external systems so local state can be compared with source-of-truth systems.

---

## 23. Migration away from the current demo architecture

Do not rewrite everything at once.

### Migration sequence

1. Keep the React application running.
2. Introduce backend API.
3. Introduce PostgreSQL schema.
4. Add database repositories/services.
5. Move authentication/RBAC to backend.
6. Move invoice processing server-side.
7. Move AI calls server-side.
8. Add queue/workers.
9. Move shadow/process events to persistent storage.
10. Move sensor/asset state to persistent storage.
11. Keep localStorage only for non-authoritative client preferences/cache where appropriate.
12. Remove demo seed behavior after production migration is validated.

The existing `DataContext` should gradually become an API-backed client state layer rather than the source of truth.

---

## 24. Repository structure for implementation

Recommended evolution from the documented source tree:

```text
org-xray/
├── apps/
│   ├── web/                    # React 19 + Vite + TypeScript
│   └── api/                    # FastAPI backend
├── services/
│   ├── invoice-worker/         # OCR/extraction/validation
│   ├── ml-worker/              # demand/process ML inference jobs
│   ├── process-worker/         # event normalization/shadow scoring
│   └── iot-worker/             # sensor ingestion/threshold alert processing
├── packages/
│   ├── contracts/              # generated API/client contracts
│   ├── domain/                 # shared business types
│   └── test-fixtures/          # deterministic fixtures
├── ml/
│   ├── datasets/
│   ├── notebooks/
│   ├── training/
│   ├── evaluation/
│   └── registry/
├── infra/
│   ├── docker/
│   ├── migrations/
│   ├── terraform/              # or equivalent IaC
│   └── ci/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── ml/
│   └── operations/
├── scripts/
├── .env.example
├── docker-compose.yml
└── README.md
```

The existing domain component/service/page naming can be preserved within `apps/web` during migration.

---

## 25. Antigravity execution model

Google describes Antigravity as an agentic development platform that can plan, execute, and verify multi-step tasks across the editor, terminal, and browser, and Antigravity 2.0 supports parallel agent orchestration and artifacts. Use that capability as a controlled engineering workflow rather than one giant prompt. citeturn774845search0turn774845search4

### Recommended agent lanes

#### Agent A — Architecture / Contracts

Owns:

- repo structure;
- API specification;
- domain boundaries;
- database schema;
- shared types;
- ADRs.

#### Agent B — Backend / Security

Owns:

- FastAPI app;
- authentication;
- RBAC;
- repositories;
- business services;
- audit logging;
- integration adapters.

#### Agent C — Invoice / GST

Owns:

- upload pipeline;
- PDF processing;
- OCR;
- extraction;
- GST validation;
- duplicate engine.

#### Agent D — Process Intelligence

Owns:

- event ingestion;
- normalization;
- variant analysis;
- shadow scoring;
- anomaly detection;
- feedback loop.

#### Agent E — Procurement AI / ML

Owns:

- demand classifier;
- Gemini gateway;
- tool calling;
- RAG;
- approved-vendor retrieval.

#### Agent F — Assets / IoT

Owns:

- asset lifecycle;
- reuse recommendations;
- sensor ingestion;
- alerting;
- anomaly model.

#### Agent G — QA / Verification

Owns:

- automated tests;
- integration tests;
- browser workflow tests;
- performance checks;
- security tests;
- regression suite.

### Orchestration rule

Only one agent should own a given domain file set at a time. Agents must publish an artifact describing changed files, tests executed, assumptions, and remaining risks.

---

## 26. Antigravity master prompt

Use this as the initial project instruction after importing the source specification:

```text
You are building ORG-XRAY from the attached product specification.

Goal:
Convert the existing React 19 + Vite + TypeScript demo architecture into a production-oriented, real-world functional enterprise process intelligence and procurement governance platform.

Hard constraints:
1. Preserve the documented product modules and terminology.
2. Preserve the documented shadow-score formula and score bands.
3. Preserve GSTIN MOD-36 structural validation.
4. Preserve the documented employee / manager / admin roles.
5. Preserve keyword routing as a deterministic fallback.
6. Do not redesign, restyle, restructure, or make UI/UX decisions. The user will provide UI/UX separately; implement backend/domain behavior and only the minimum existing UI wiring required to make functions work.
7. Do not use localStorage as the authoritative store for production business data.
8. Do not expose Gemini/GST/provider secrets in frontend code.
9. All business-critical decisions must be server-authoritative.
10. Every AI/ML result must have model/version/confidence/provenance metadata where applicable.
11. All important workflow mutations must create audit records.
12. Write automated tests for each business-critical rule and workflow.

Architecture target:
- React 19 + TypeScript + Vite frontend
- FastAPI backend
- PostgreSQL transactional database
- Redis-backed jobs/cache
- object storage for invoice documents
- Python AI/ML workers
- server-side Gemini gateway
- configurable GSTIN provider adapter
- persistent event logging
- model/prompt version registry

Execution rules:
- First inspect the repository and source specification.
- Produce an implementation plan and task list before editing code.
- Break work into domain milestones.
- Do not make large unrelated refactors.
- Keep API contracts explicit.
- Add migrations with every schema change.
- Add tests with every business rule.
- Run lint/typecheck/tests/build after each milestone.
- Use browser automation only for functional verification, not visual redesign.
- Never fabricate missing business data or provider capabilities.
- Mark assumptions clearly.

Definition of done:
The application can authenticate real users, persist real organizational data, process uploaded invoices, validate GSTINs, detect duplicate invoices, classify/reroute demands, support approval workflows, calculate shadow-process risk, accept human feedback, recommend reusable assets, ingest sensor events, provide grounded procurement assistance, and expose auditable analytics through stable APIs.
```

---

## 27. Implementation phases

### Phase 0 — Repository audit and baseline

Tasks:

- inventory all current pages/components/services/types;
- identify mock-only behavior;
- map all localStorage keys;
- identify direct external API calls;
- inventory all current environment variables;
- run tests/build/lint baseline;
- produce architecture decision record.

Deliverable:
`docs/architecture/baseline.md`

### Phase 1 — Production foundation

Build:

- monorepo structure;
- backend skeleton;
- PostgreSQL;
- migrations;
- Redis;
- object storage adapter;
- configuration system;
- health/readiness endpoints;
- structured logging;
- CI pipeline.

Exit criteria:
Backend starts cleanly, DB migrations are repeatable, CI passes, and frontend can reach `/api/v1/health`.

### Phase 2 — Identity and RBAC

Build:

- real auth integration;
- users/roles/departments;
- backend permission middleware;
- session lifecycle;
- audit logging.

Exit criteria:
Employee, manager, and admin can only perform allowed server-side actions.

### Phase 3 — Procurement/demand core

Build:

- demands;
- routing rules;
- ML classifier scaffold;
- approval workflow;
- purchase limits;
- vendor catalog.

Exit criteria:
Demand → classify → submit → approve/reject is transactional and auditable.

### Phase 4 — Invoice intelligence

Build:

- secure upload;
- object storage;
- worker queue;
- PDF text extraction;
- OCR adapter;
- normalized extraction;
- tax validation;
- duplicate engine;
- review workflow.

Exit criteria:
A user can submit a real invoice and receive an auditable processing result without browser-only authority.

### Phase 5 — GSTIN verification

Build:

- checksum service;
- provider adapter;
- caching;
- provider outage handling;
- verification provenance.

Exit criteria:
Structural and live-verification states are clearly separated.

### Phase 6 — Process intelligence

Build:

- canonical event schema;
- ingestion endpoints/connectors;
- event normalization;
- process variants;
- documented shadow score;
- anomaly model;
- feedback persistence.

Exit criteria:
Manager sees a traceable alert with score components, anomaly evidence, and feedback.

### Phase 7 — Procurement AI + RAG

Build:

- Gemini gateway;
- structured outputs;
- policy tool calls;
- knowledge ingestion;
- vector search/pgvector;
- citations/provenance;
- guardrails;
- cost/rate controls.

Exit criteria:
Assistant can answer organization-specific procurement questions from approved sources and propose but not bypass controlled actions.

### Phase 8 — Assets and IoT

Build:

- asset lifecycle;
- compatibility/reuse recommendation engine;
- sensor ingestion;
- threshold alerts;
- maintenance status lifecycle.

Exit criteria:
A request can be matched to an eligible returned asset and a sensor event can produce a persistent threshold-based operational alert.

### Phase 9 — Analytics and governance

Build:

- KPI definitions;
- server-side aggregates;
- model-performance analytics;
- human override metrics;
- audit reporting.

Exit criteria:
KPIs reconcile against transactional data and model metrics have explicit evaluation datasets.

### Phase 10 — Hardening and release

Build:

- backup/restore;
- security scan;
- dependency/container scanning;
- load testing;
- failure-injection tests for providers/queues;
- alerting;
- production deployment;
- runbooks;
- incident procedures.

Exit criteria:
Staging passes all release gates and production deployment is reproducible.

---

## 28. Priority order for MVP

The first real-world release should prioritize the flows that create the core system of record:

1. Authentication + RBAC
2. PostgreSQL + audit log
3. Demand creation + approval workflow
4. Invoice upload + extraction + validation
5. GSTIN verification
6. Duplicate invoice detection
7. Process event ingestion + shadow score
8. Human feedback
9. Procurement assistant with controlled retrieval/tools
10. Asset reuse
11. IoT ingestion/threshold alerts
12. Focused ML for demand routing and process anomaly detection

Do not wait for sophisticated ML before shipping deterministic business rules. The rules create clean data and feedback that later improves the ML layer.

---

## 29. Definition of done by capability

### Invoice

- accepts real PDF/image input;
- stores original document;
- extracts fields;
- exposes confidence;
- validates arithmetic;
- checks GSTIN;
- finds duplicate candidates;
- supports human resolution;
- writes audit trail.

### Process intelligence

- accepts canonical events;
- reconstructs cases/variants;
- calculates documented score;
- runs anomaly model;
- shows evidence;
- stores feedback;
- supports re-evaluation after corrections.

### Procurement AI

- classifies demand;
- checks limits and policies;
- retrieves approved vendors/prices;
- gives grounded recommendations;
- logs model/prompt version;
- cannot bypass approval controls.

### Asset recovery

- maintains assignments;
- records returns;
- identifies compatible reusable assets using explainable rules;
- records allocation decision;
- avoids duplicate purchase requests where policy permits.

### IoT

- authenticates/validates device events;
- stores readings;
- detects threshold breaches;
- creates alerts;
- tracks status transitions;
- supports replay/reconciliation.

---

## 30. Release gates

A production release should not pass until all of the following are true:

- no critical/high unresolved security findings;
- migrations apply cleanly from empty database;
- backups have been restored successfully in a test environment;
- audit logging works for all privileged mutations;
- frontend contains no production AI/GST provider secrets;
- queue retries/dead-letter behavior has been tested;
- external provider failures have deterministic fallback behavior;
- model versions are pinned;
- core business rules have unit tests;
- critical user journeys have integration/E2E tests;
- observability dashboards/alerts exist;
- a rollback path is documented.

---

## 31. First implementation tasks to give Antigravity

Start with these in order:

### Task 1
Inspect the current ORG-XRAY repo and generate:

- current architecture map;
- localStorage map;
- mock-data map;
- API/external-integration map;
- page/service/type dependency map;
- test/build baseline;
- migration risk list.

Do not modify application behavior yet.

### Task 2
Create the production monorepo skeleton and backend foundation while keeping the existing web app runnable.

### Task 3
Implement PostgreSQL models/migrations for organizations, users, roles, departments, audit events, demands, purchase requests, approvals, vendors, invoices, invoice items, process events, shadow alerts, assets, sensors, and model metadata.

### Task 4
Introduce backend authentication/RBAC and replace demo authorization as the source of truth.

### Task 5
Move invoice ingestion and AI provider calls to backend-controlled workflows.

### Task 6
Implement invoice/GST/duplicate detection end-to-end with tests.

### Task 7
Implement process-event ingestion, variant detection, shadow score, anomaly model scaffold, and human feedback.

### Task 8
Implement demand classification + procurement assistant tool layer + RAG.

### Task 9
Implement asset reuse + sensor ingestion + threshold alerts.

### Task 10
Run complete verification, security hardening, staging deployment, and production-readiness audit.

---

## 32. Important migration decisions

### Do not keep these as final production mechanisms

- localStorage as source of truth;
- client-only invoice verification;
- browser-exposed AI API keys;
- hard-coded business decisions inside UI components;
- UI-only RBAC;
- mock services pretending to be real integrations;
- unversioned prompts/models;
- AI-generated final approval decisions without policy enforcement.

### Keep these as explicit business rules/fallbacks

- documented shadow-score formula;
- score bands;
- GSTIN MOD-36 checksum validation;
- demand keyword classifier fallback;
- tax arithmetic rules;
- human-in-the-loop feedback categories.

---

## 33. Removed features — do not implement in this phase

For avoidance of doubt, Antigravity agents must not expand the product with the following unless a later written scope change requests them:

- vendor churn/availability prediction;
- opaque vendor trust/risk scoring;
- learning-to-rank for asset reuse;
- sensor ML/time-series anomaly models;
- automated refund/credit-note processing;
- separate budget management/forecasting;
- separate analytics warehouse;
- autonomous assistant action execution;
- mobile apps, blockchain, or unrelated platform products.

The assistant may retrieve approved information, explain it, and prepare drafts. Final approval, purchasing, asset ownership changes, and compliance-sensitive decisions remain explicit server-controlled workflows.

## 34. Final build philosophy

ORG-XRAY should become a system where deterministic business rules provide the compliance floor, AI/ML improves detection and recommendations, human reviewers retain governance authority, and every material outcome is traceable to data, rules, model versions, or an explicit human decision.

The existing specification already provides a useful domain skeleton. The production effort should therefore focus on persistence, security, integrations, asynchronous processing, data quality, ML lifecycle, explainability, observability, and verification rather than replacing the product concept.

UI/UX work begins only after the separate design specification is provided.
