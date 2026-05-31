# Leads Personified → Micro‑SaaS Product Plan

## 1) Product vision & USP
**Vision:** Turn Leads Personified into a micro‑SaaS that ranks and routes leads using a **lead‑relationship graph** (company ↔ people ↔ interactions ↔ intent), not just isolated scores.  
**USP:** “Graph‑native lead scoring” that surfaces **why** a lead ranks high (shared tech stack, shared buyers, topical intent spikes, adjacency to converted accounts).

---

## 2) Target users & primary use cases
**Primary users:** SMB/mid‑market B2B sales + marketing teams, RevOps, growth.  
**Use cases:**
- Prioritize inbound leads and SDR queues.
- Improve MQL→SQL conversion by scoring fit + intent + engagement.
- Account‑based prioritization (company‑level intent and relationship graph).
- Enrichment‑optional lead routing and segmentation (use existing enriched fields when available).

---

## 3) Competitive landscape (lead scoring + enrichment)
Public pricing and features frequently change; many vendors quote custom pricing. Use this as a **market snapshot**.

| Product | Lead scoring approach | Notable capabilities | Pricing (public / typical) |
|---|---|---|---|
| **HubSpot Marketing Hub** | Rule‑based + predictive scoring, CRM‑native | Email/automation, lifecycle stages, scoring workflows | Public tiers; pro/enterprise in multi‑thousand monthly range【https://prometheusagency.co/insights/top-marketing-automation-platforms】【https://wifitalents.com/best/lead-scoring-software/】 |
| **Salesforce Account Engagement (Pardot)** | Scoring + grading, Einstein AI | Deep Salesforce integration, ABM, analytics | Public base tier ~$1,250/mo; higher tiers custom【https://valeriumoraru.com/hubspot-vs-salesforce-pardot-account-engagement-comprehensive-2025-comparison/】 |
| **Adobe Marketo Engage** | Advanced scoring, multi‑model | Enterprise automation, ABM, analytics | Generally custom; mid‑four‑figure monthly estimates【https://prometheusagency.co/insights/top-marketing-automation-platforms】 |
| **6sense** | Predictive account/lead + intent | ABM orchestration, intent signals | Custom enterprise pricing【https://wifitalents.com/best/lead-scoring-software/】 |
| **ZoomInfo** | Predictive scoring + intent | Data enrichment, intent, org charts | Custom pricing (often annual contracts)【https://wifitalents.com/best/lead-scoring-software/】 |
| **Apollo.io** | Rules‑based scoring + sequencing | Prospecting + outreach suite | Public self‑serve per‑seat pricing【https://wifitalents.com/best/lead-scoring-software/】 |
| **Clearbit** | Enrichment‑based fit scoring | Real‑time enrichment + segmentation | Mostly custom or usage‑based【https://wifitalents.com/best/lead-scoring-software/】 |
| **D&B Lattice Engines** | Predictive scoring | D&B data + lookalikes | Custom enterprise pricing【https://wifitalents.com/best/lead-scoring-software/】 |

**Takeaway:** Market leaders compete on **data depth (enrichment + intent)** and **workflow integration**. Most do not provide a **relationship‑graph view** as a primary scoring modality—an opening for a differentiated micro‑SaaS.

---

## 4) Lead enrichment sources (what data they provide)
You can blend multiple data sources; start with **one firmographic + one intent** provider.  
**Enrichment is optional and post‑MVP**: only call a provider if the user explicitly selects a source.  
MVP assumes enriched fields are already present from CRM/CSV or another system.

| Source | Data types | Notes |
|---|---|---|
| **Clearbit** | Company + person enrichment (firmographic, contact, social, metrics)【https://help.clearbit.com/hc/en-us/articles/5975301365655-What-Enrichment-Attributes-Does-Clearbit-Return】【https://clearbit.com/attributes】 | Strong for firmographics + contact/role data |
| **People Data Labs** | Contact + person identity | API‑first enrichment |
| **ZoomInfo / Apollo** | Contact + firmographic + intent add‑ons | Strong B2B contact databases |
| **BuiltWith** | Technographic stack (what tech a company runs) | Useful for fit + targeting tech‑stack users |
| **Bombora** | Intent signals and Company Surge® scores (0–100; 60+ indicates spike)【https://customers.bombora.com/crc-brand/thresholding】 | Great for prioritizing in‑market accounts |
| **Crunchbase** | Funding and company growth signals | Useful for high‑growth targeting |

---

## 5) Lead scoring metrics and evaluation (industry norms + quality KPIs)
**Typical model structure:**  
**Fit (explicit) + Engagement (implicit) + Intent + Relationship signals**

**Common metrics:**
- **Fit / Firmographic:** industry, employee count, revenue, tech stack, region, ICP match.
- **Role fit:** job title, seniority, department.
- **Engagement:** demo request, pricing page views, product usage, email clicks, event attendance.
- **Intent:** topic‑level intent spikes (e.g., Bombora Company Surge score 0–100; **60+ = strong spike**【https://customers.bombora.com/crc-brand/thresholding】).
- **Lifecycle / CRM stage:** lead → MQL → SQL → opportunity.

**Common score ranges and thresholds:**
- Many systems use **1–100** lead scores; enterprise tiers often allow **1–500** for granularity【https://knowledge.hubspot.com/scoring/understand-the-lead-scoring-tool】.
- **MQL thresholds commonly fall in the 50–80 range** on the 1–100 scale (varies by sales capacity and close rates)【https://www.xcellimark.com/blog/how-to-build-lead-scoring-in-hubspot-2025-update】.
- Intent providers (e.g., Bombora) use **0–100 intent scores**, with **60+** as a recommended action threshold【https://customers.bombora.com/crc-brand/thresholding】.

**Scoring quality evaluation (how to judge the model):**
- **Ranking quality:** precision@K / recall@K, NDCG; top‑decile conversion lift vs baseline rules.
- **Conversion likelihood accuracy:** ROC‑AUC / PR‑AUC; calibration (predicted vs actual conversion rate).
- **Business impact:** MQL→SQL lift, win‑rate lift, pipeline velocity, meetings booked per rep.
- **Operational quality:** score coverage (% of leads scored), data freshness, stability/drift by segment.
- **Validation approach:** time‑based backtests on historical CRM outcomes + A/B tests vs legacy routing.

**What competitors market themselves on:**
- **Pipeline impact** (more qualified pipeline, higher win rates).
- **Seller productivity** (faster prioritization, fewer wasted touches).
- **Conversion lift** (higher MQL→SQL and SQL→Opp rates).
- **Forecast reliability** (better prioritization → more predictable pipeline).

---

## 6) Data you will need (minimum viable dataset)
**Identity & normalization**
- Company domain, company name, website, location.
- Contact email, name, title, seniority, department.

**Firmographic / fit**
- Industry, employee count, revenue, funding stage.
- Tech stack or signals (optional but differentiating).

**Behavioral / engagement**
- Page views, pricing/demo views, form fills, email opens/clicks.
- Webinar/event attendance, product usage events.

**Outcome labels (for model training)**
- MQL, SQL, opportunity, closed‑won/lost.
- Time‑to‑conversion, ARR/ACV where available.

---

## 7) Integrations that make adoption easy
**CRMs:** Salesforce, HubSpot, Microsoft Dynamics, Pipedrive, Zoho  
**Marketing automation:** Marketo, Account Engagement (Pardot), HubSpot, Mailchimp  
**Sales engagement:** Outreach, Salesloft, Apollo, Groove  
**Data pipelines:** Segment, RudderStack, Zapier/Make, native webhooks  
**Enrichment/intent:** Clearbit, ZoomInfo, Apollo, Bombora, BuiltWith  
**Collaboration:** Slack, Teams  
**Data warehouse:** Snowflake, BigQuery, Postgres

---

## 8) Product scope & roadmap
**MVP (6–10 weeks)**
- CSV/Sheets import + basic CRM integration.
- **Bring‑your‑own enrichment fields** (assume enriched data exists; no vendor calls in MVP).
- **Graph‑propagation scoring** with conversion‑likelihood classification.
- **Graph view** of accounts and related leads.
- **Outreach order** view (ranked lead/sequence list).
- Scoring explanation panel (“why this lead is top 5”).
- **User‑triggered re‑score** when new CRM outreach updates are available.

**V1 (3–6 months)**
- Multiple integrations (Salesforce + HubSpot + Segment).
- **Optional enrichment providers** (user‑selected; usage‑metered).
- Intent provider (Bombora) + technographic (BuiltWith).
- ML‑assisted scoring with score decay.
- Alerting + routing (Slack/CRM task creation).

**V2 (6–12 months)**
- Self‑serve model tuning + experimentation.
- Multi‑tenant graph analytics and cohort insights.
- Predictive conversion likelihood + revenue impact forecasting.

---

## 9) Multi‑agent architecture (core agents)
Assuming lead data arrives from integrations, the product can be structured around **specialized agents**:

1. **Ingestion Agent** – pulls data from CRM/MA, dedupes, normalizes fields.
2. **Identity Resolution Agent** – merges contacts/companies (email + domain + fuzzy matching).
3. **Enrichment Agent (optional, post‑MVP)** – calls Clearbit/ZoomInfo/BuiltWith/Bombora only when selected.
4. **Graph Builder Agent** – updates relationship graph (people↔company↔intent↔events).
5. **Scoring Agent** – graph‑propagation scoring + conversion‑likelihood classification; supports on‑demand re‑scores.
6. **Explanation Agent** – creates “why this score” summaries.
7. **Routing Agent** – assigns leads to owners/queues, creates CRM tasks.
8. **Monitoring/QA Agent** – checks data freshness, anomaly detection, model drift.

---

## 10) Engineering components (to show real depth)
- **Data ingestion pipeline** (CDC/webhooks + batch sync).
- **Feature store** for scoring inputs.
- **Graph database** (Neo4j, Neptune, or Postgres + graph layer).
- **Vector store** for semantic similarity (lead persona embeddings).
- **Scoring service** (graph propagation + conversion classifier + decay + intent scaling).
- **Workflow orchestration** (temporal / celery / dagster).
- **Explainability layer** (traceable feature contributions).
- **Audit logging + RBAC** (enterprise readiness).
- **Billing & usage metering** (per contact / per enrichment credit).

---

## 11) Pricing & packaging (suggested)
**Starter** – $99/mo, 5k leads, 1 integration, basic scoring  
**Growth** – $299/mo, 25k leads, 3 integrations, graph view, intent add‑on  
**Pro** – $799/mo, 100k leads, multi‑workspace, custom scoring rules  
**Usage add‑ons:** enrichment credits, intent credits, extra seats

---

## 12) Risks & mitigations
- **Data quality** → automated QA agent + source confidence scoring.
- **Model drift** → scheduled retraining & decay.
- **Integration fatigue** → strong native CRM integration + Zapier.
- **Compliance** → GDPR/CCPA, data retention policies.

---

## References (pricing, scoring, enrichment)
- HubSpot lead scoring tool (score ranges)【https://knowledge.hubspot.com/scoring/understand-the-lead-scoring-tool】  
- HubSpot scoring thresholds (MQL 50–80 guidance)【https://www.xcellimark.com/blog/how-to-build-lead-scoring-in-hubspot-2025-update】  
- Bombora Company Surge® thresholds (intent score 0–100, 60+ spike)【https://customers.bombora.com/crc-brand/thresholding】  
- Clearbit enrichment attributes【https://help.clearbit.com/hc/en-us/articles/5975301365655-What-Enrichment-Attributes-Does-Clearbit-Return】  
- Clearbit data attribute index【https://clearbit.com/attributes】  
- Lead scoring software overview/pricing comparisons【https://wifitalents.com/best/lead-scoring-software/】  
- HubSpot vs Pardot comparison (pricing tiers)【https://valeriumoraru.com/hubspot-vs-salesforce-pardot-account-engagement-comprehensive-2025-comparison/】  
- Marketing automation platform comparison (HubSpot/Marketo/Pardot)【https://prometheusagency.co/insights/top-marketing-automation-platforms】  
