# Leads Personified — Development Task Breakdown

## 1) Project setup & foundations
- [ ] Confirm product scope (MVP vs V1) and success metrics
- [ ] Finalize core user stories and acceptance criteria
- [ ] Define roles/permissions for tenant members (owner/admin/member)
- [ ] Establish environment variable template (.env.example)
- [ ] Set up local dev scripts for backend and frontend
- [ ] Define API versioning and error response conventions
- [ ] Create shared constants for status enums and error codes
- [ ] Add structured logging and request correlation IDs

## 2) Data model & migrations
- [ ] Implement multi-tenant tables (tenants, users, memberships)
- [ ] Add leads/accounts/contacts schema with indexes
- [ ] Add ingestion/import tables and status enums
- [ ] Add scoring tables (lead_scores, score_explanations)
- [ ] Add audit_logs table and action taxonomy
- [ ] Add migration tooling and baseline migration
- [ ] Add seed data scripts for dev/demo tenants

## 3) Authentication & tenancy
- [ ] Implement email/password auth with hashed passwords
- [ ] Add login/logout endpoints and token issuing
- [ ] Implement tenant selection and membership checks
- [ ] Enforce tenant scoping on all queries
- [ ] Add RBAC middleware for admin-only endpoints
- [ ] Add audit log entries for auth and admin actions

## 4) Ingestion & normalization
- [ ] Build CSV upload endpoint with validation
- [ ] Add field mapping and normalization rules
- [ ] Implement duplicate detection and merge strategy
- [ ] Store original file metadata in object storage
- [ ] Add import status tracking and progress updates
- [ ] Add export endpoints for normalized data

## 5) Enrichment (optional toggle)
- [ ] Implement provider selector and configuration storage
- [ ] Add enrichment job queue and worker
- [ ] Add per-tenant quota enforcement
- [ ] Add caching to avoid re-enrichment
- [ ] Add provider-specific adapters (Clearbit/ZoomInfo/etc.)

## 6) Scoring & graph pipeline
- [ ] Build graph node/edge builders for leads and interactions
- [ ] Implement graph propagation score computation
- [ ] Add conversion-likelihood classifier pipeline
- [ ] Combine scores into final score with weights
- [ ] Persist score versions and score bands
- [ ] Add rescore endpoint with job tracking
- [ ] Add scoring explanation generation

## 7) Lead management & workflows
- [ ] Implement lead status updates (converted/failed/in-progress)
- [ ] Add bulk status update endpoint
- [ ] Add reranking rules and persistent ordering
- [ ] Add lead detail API with explanation data
- [ ] Add outreach queue APIs (create, reorder, assign)

## 8) Frontend foundations
- [ ] Build auth screens and tenant selector
- [ ] Add navigation shell and routing
- [ ] Add data source management screens
- [ ] Add CSV upload and mapping workflow UI
- [ ] Add lead list, filters, and detail view
- [ ] Add graph visualization view
- [ ] Add scoring explanation panel
- [ ] Add outreach queue UI with bulk actions

## 9) Observability & reliability
- [ ] Add metrics for ingestion latency and scoring runtime
- [ ] Add background job monitoring dashboard
- [ ] Add alerting for failed syncs and stale scores
- [ ] Add error tracking and frontend crash reporting

## 10) Billing & payments (Razorpay)
- [ ] Define pricing plans and entitlements
- [ ] Add Razorpay order creation endpoint
- [ ] Add Razorpay payment verification endpoint
- [ ] Add webhook endpoint for payment events
- [ ] Persist subscription/payment records per tenant
- [ ] Add billing portal UI and upgrade flow
- [ ] Enforce entitlements based on plan

## 11) Security & compliance
- [ ] Add input validation and request size limits
- [ ] Add rate limiting for auth and payment routes
- [ ] Secure secrets management for integrations
- [ ] Add audit log export capability
- [ ] Add data retention and deletion workflows

## 12) Deployment & CI/CD
- [ ] Add Dockerfiles for backend and frontend
- [ ] Add deployment manifests (Render/Fly/Heroku/etc.)
- [ ] Add CI checks for linting, tests, and builds
- [ ] Add staging environment with seed data
- [ ] Add backup and restore procedures
