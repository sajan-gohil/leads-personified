# Leads Personified — Detailed System Design (Backend, Frontend, Integrations, Data)

## 1) Goals, scope, and assumptions
- **Primary goal (MVP):** score leads using **graph propagation** + conversion‑likelihood classification, render a **relationship graph**, and provide a **ranked outreach order**.
- **Enrichment is optional and post‑MVP:** enrichment providers are only called if a user selects a source.  
  MVP assumes most data is already enriched via CRM/CSV or an external system.
- **Re‑scoring is user‑triggered:** scores can be recalculated after new outreach activity updates arrive in CRM.
- **Multi‑tenant SaaS:** strict tenant isolation with RBAC and audit logging.

## 2) Architecture overview
**Core services**
- **API service (FastAPI):** authentication, data source config, lead CRUD, scoring endpoints, graph APIs.
- **Worker service:** ingestion sync, graph build, scoring jobs, explanation generation.
- **Scoring engine:** graph propagation + conversion likelihood classifier.
- **Storage:** Postgres (primary), object storage (CSV uploads), vector store (optional).

**Data stores**
- **Postgres** for core entities, scoring, graph edges (adjacency list), and audit logs.
- **Optional vector store** (pgvector or external) for semantic similarity features.

## 3) Data flows
### 3.1 Ingestion & normalization
1. User connects CRM or uploads CSV.
2. Ingestion job normalizes fields → canonical schema.
3. Identity resolution merges duplicates (email + domain + fuzzy matching).

### 3.2 Graph building
1. Create/refresh graph nodes for accounts, contacts, interactions, intent, and outcomes.
2. Create edges with typed weights (e.g., contact→account, contact→interaction, account→intent).

### 3.3 Scoring & outreach ordering
1. **Graph propagation** scores flow through edges to compute relationship influence.
2. **Conversion likelihood classifier** outputs probability of conversion.
3. Final score = weighted blend of propagation score + classifier output + business rules.
4. Ranked outreach list generated per workspace and SDR queue.

### 3.4 Re‑scoring on demand
1. CRM update event arrives or batch sync finishes.
2. User chooses “Recalculate scores.”
3. Scoring engine recalculates with latest interactions and outcomes.

## 4) Backend design
### 4.1 API surface (representative)
- **Auth & tenancy**
  - `POST /auth/login`, `POST /auth/logout`
  - `GET /tenants`, `POST /tenants`, `GET /tenants/{id}`
  - `GET /memberships`, `POST /memberships`
- **Data sources & imports**
  - `POST /data-sources` (CRM connections, tokens)
  - `POST /imports/csv` (upload + parse)
  - `GET /imports/{id}/status`
- **Leads & graph**
  - `GET /leads`, `GET /leads/{id}`, `PATCH /leads/{id}`
  - `GET /graph/summary`, `GET /graph/nodes`, `GET /graph/edges`
- **Scoring**
  - `POST /scores/recalculate` (user‑triggered)
  - `GET /scores/leaderboard`
  - `GET /scores/explanations/{lead_id}`
- **Webhooks**
  - `POST /webhooks/salesforce`
  - `POST /webhooks/hubspot`

### 4.2 Scoring engine details
**Graph propagation**
- Start with seed nodes (intent spikes, known conversions, high‑engagement actions).
- Propagate scores along weighted edges with decay (e.g., by edge type and time).
- Aggregate node‑level contributions for each lead and account.

**Conversion likelihood classifier**
- Binary classifier (converted vs not) using features:
  - Engagement counts, recency, intent score, firmographic fit, graph centrality.
- Outputs calibrated probability (e.g., Platt scaling or isotonic calibration).

**Final score**
- `final_score = w1 * propagation_score + w2 * conversion_prob + w3 * rule_adjustments`
- Score bands map to **MQL/SQL** thresholds per workspace.

### 4.3 Background jobs
- **Sync jobs** for CRM/MA sources (incremental cursor).
- **Graph build jobs** after each sync or import.
- **Scoring jobs** on schedule or user‑triggered.
- **Explanation jobs** generating top feature contributions.

## 5) Frontend design
### 5.1 Core pages
- **Auth / workspace selection**
- **Data sources**
  - CRM connection status
  - Enrichment provider selection (disabled in MVP, “Coming soon”)
- **Lead import**
  - CSV upload + field mapping
- **Graph view**
  - Interactive node/edge visualization
  - Filters by account, segment, intent topic
- **Outreach order**
  - Ranked list with score breakdown
  - Bulk actions: assign owner, export, create CRM tasks
- **Lead detail**
  - Score explanation, history, last rescore timestamp

### 5.2 UI components
- Score band badges (Hot/Warm/Cold)
- “Recalculate scores” button (with confirmation)
- Insights panel (top drivers, key edges, data freshness)

## 6) Integrations
### 6.1 CRM integrations (MVP + V1)
- **Salesforce / HubSpot**
  - Entities: Leads, Contacts, Accounts, Activities, Opportunities
  - Sync strategy: webhook + periodic backfill
  - Field mapping: custom fields for score, score band, explanation URL

### 6.2 Optional enrichment (post‑MVP)
- Providers (Clearbit, ZoomInfo, BuiltWith, Bombora)
- Activated only when user selects a source
- Usage metering and quota enforcement per tenant

### 6.3 Event & workflow integrations
- Slack/Teams for alerts
- Zapier/Make for routing automation

## 7) Database schema (multi‑tenant)
> All tables include `tenant_id` and `created_at` / `updated_at`.

### 7.1 Core tenancy tables
- **tenants**
  - `id` (PK), `name`, `plan`, `status`
- **users**
  - `id` (PK), `email` (unique), `password_hash`, `status`
- **memberships**
  - `id` (PK), `tenant_id` (FK), `user_id` (FK), `role` (owner/admin/member)

### 7.2 Data sources & sync
- **data_sources**
  - `id`, `tenant_id`, `type` (salesforce/hubspot/csv), `config_json`, `status`
- **sync_runs**
  - `id`, `tenant_id`, `data_source_id`, `started_at`, `ended_at`, `status`, `cursor`
- **imports**
  - `id`, `tenant_id`, `filename`, `status`, `original_file_path`

### 7.3 Lead & account entities
- **accounts**
  - `id`, `tenant_id`, `external_id`, `domain`, `name`, `industry`, `employees`, `attributes_json`
  - Unique: `(tenant_id, external_id)` or `(tenant_id, domain)`
- **contacts**
  - `id`, `tenant_id`, `external_id`, `account_id`, `email`, `name`, `title`, `attributes_json`
  - Unique: `(tenant_id, email)`
- **leads**
  - `id`, `tenant_id`, `contact_id`, `account_id`, `status`, `source`, `attributes_json`

### 7.4 Engagement & intent
- **interactions**
  - `id`, `tenant_id`, `contact_id`, `account_id`, `type`, `occurred_at`, `metadata_json`
- **intent_signals**
  - `id`, `tenant_id`, `account_id`, `topic`, `score`, `occurred_at`

### 7.5 Graph storage
- **graph_nodes**
  - `id`, `tenant_id`, `node_type` (account/contact/intent/event), `ref_id`
- **graph_edges**
  - `id`, `tenant_id`, `from_node_id`, `to_node_id`, `edge_type`, `weight`, `last_seen_at`
  - Index: `(tenant_id, from_node_id)`, `(tenant_id, to_node_id)`

### 7.6 Scoring & explanations
- **lead_scores**
  - `id`, `tenant_id`, `lead_id`, `score`, `score_band`, `conversion_prob`, `score_version`
  - Index: `(tenant_id, lead_id)`, `(tenant_id, score_band)`
- **score_explanations**
  - `id`, `tenant_id`, `lead_id`, `summary`, `top_factors_json`

### 7.7 Outreach ordering
- **outreach_queues**
  - `id`, `tenant_id`, `name`, `owner_id`
- **outreach_queue_items**
  - `id`, `tenant_id`, `queue_id`, `lead_id`, `rank`, `status`

### 7.8 Enrichment (post‑MVP, optional)
- **enrichment_providers**
  - `id`, `tenant_id`, `provider`, `status`, `quota`, `config_json`
- **enrichment_jobs**
  - `id`, `tenant_id`, `provider_id`, `entity_type`, `entity_id`, `status`, `requested_at`

### 7.9 Auditing & ops
- **audit_logs**
  - `id`, `tenant_id`, `user_id`, `action`, `object_type`, `object_id`, `metadata_json`

## 8) Security, compliance, and tenancy isolation
- **RBAC** enforced at API layer with tenant scoping.
- **Row‑level isolation**: every query filtered by `tenant_id`.
- **Secrets management** for CRM tokens.
- **Audit logs** for all scoring updates and user actions.

## 9) Observability & reliability
- Metrics: ingestion latency, score refresh time, drift, conversion lift.
- Logs: per‑tenant API logs with correlation IDs.
- Alerts: failed syncs, stale scores, queue backlog.

## 10) MVP‑to‑V1 migration notes
- Add optional enrichment providers (user‑selected).
- Introduce ML‑assisted scoring with decay.
- Extend integrations with additional CRMs and marketing tools.
