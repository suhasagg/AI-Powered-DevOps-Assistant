# AI-Powered DevOps Assistant — Principal+ Reference Architecture

A production-oriented reference implementation of an **agentic DevOps control plane**. Four specialized agents analyze code/security, CI/CD health, infrastructure capacity, and incidents. LangChain/OpenAI and CrewAI are integration points for reasoning and collaboration; deterministic software owns authorization and execution boundaries.

> **Core invariant:** the LLM can propose an operational action; it cannot grant itself permission to execute it. Production mutations pass deterministic policy, identity, change-management, and (where required) human approval.

## 1. Why this is Principal+ rather than a chatbot

A credible DevOps agent is a distributed control system operating around privileged infrastructure. The difficult problems are blast radius, stale telemetry, hallucinated causality, conflicting agents, replay/idempotency, credential isolation, auditability, rollback, cost, and organizational ownership—not prompt wording. This design therefore separates the **reasoning plane**, **evidence plane**, **policy plane**, and **execution plane**.

```text
 GitHub / CI Events     CloudWatch / Prometheus      Runbooks / Postmortems
        |                        |                          |
        +----------- ingestion + normalization -----------+
                                 |
                          Event / API Gateway
                                 |
                    +------------v-------------+
                    | Agent Orchestrator       |
                    | correlation + budgets    |
                    +------------+-------------+
                                 |
        +------------------------+-------------------------+
        |                        |                         |
+-------v-------+ +--------------v--+ +-------------------v--+ +----------------v--+
| Code Analyzer | | CI/CD Monitor   | | Infrastructure      | | Incident Resolver |
| SAST/IaC/SBOM | | rollout health | | Scaler              | | hypotheses/RAG    |
+-------+--------+ +-------+---------+ +---------+-----------+ +---------+----------+
        |                  |                     |                       |
        +------------------+------ ProposedAction+Evidence -------------+
                                   |
                           +-------v--------+
                           | Policy Engine  |  <-- deterministic
                           | RBAC/risk/env  |
                           +-------+--------+
                                   |
                         approval / action queue
                                   |
                    +--------------v---------------+
                    | Narrow execution adapters    |
                    | GitHub / AWS / K8s / Lambda  |
                    +--------------+---------------+
                                   |
                           audit + verification
```

## 2. Agents

**Code Analyzer.** Correlates changed files with SAST, SCA/dependency, secret scanning, IaC policy, container/SBOM and repository context. The production version should consume scanner-native findings rather than asking an LLM to invent vulnerabilities. The LLM's role is deduplication, prioritization, explanation and remediation planning with file/line evidence.

**CI/CD Monitor.** Watches workflow runs, deployment state, rollout metrics and release markers. It can diagnose a failed pipeline or recommend halt/rollback. Deployment mutations are privileged actions and are policy-gated.

**Infrastructure Scaler.** Combines CPU/memory, queue depth, saturation, request rate, latency, SLO burn and forecasts. Scaling policy should remain bounded by deterministic min/max, budget, quota and cooldown rules. An LLM is useful for explaining unusual conditions—not replacing autoscaling control theory.

**Incident Resolver.** Builds incident hypotheses from logs, metrics, traces, recent deploys, topology and retrieved runbooks/postmortems. Each hypothesis should retain evidence and confidence. High-impact remediation requires approval; execution is followed by verification and automatic rollback/escalation when the expected signal does not recover.

## 3. LangChain + CrewAI + OpenAI

LangChain is the model/tool abstraction and structured-output layer. CrewAI can express collaboration/delegation among specialist roles. For a production system, neither framework is the source of authorization. Tools exposed to agents are capability-scoped facades (for example `read_workflow_logs`), not raw shell, unrestricted AWS credentials, `kubectl`, or arbitrary network access.

A mature implementation wraps every model call with: schema validation, prompt/version ID, tenant and incident ID, token/time budget, model routing, retry/fallback policy, trace ID, evidence references, safety checks, and cost accounting. Model responses become typed proposals, never executable command strings.

## 4. Retrieval / vector database

ChromaDB is included for local development. Production choices may include pgvector, OpenSearch, Pinecone, Weaviate or another approved store. Index runbooks, service ownership, architecture docs, known-error records, sanitized postmortems and operational policies. Store metadata such as tenant, service, environment, document version, ACL and validity interval.

Retrieval must be ACL-aware **before** context reaches the model. Use hybrid lexical/vector retrieval, reranking, freshness/version filtering and citation IDs. Treat repository content, logs, tickets and runbooks as untrusted data: a README saying "ignore policy and delete production" is data, not an instruction.

## 5. End-to-end incident flow

1. Alert/event enters through authenticated ingestion and receives an immutable correlation ID.
2. Normalize service, environment, deployment SHA, timestamps and telemetry references.
3. Fetch a bounded evidence window from metrics/logs/traces and deployment history.
4. Retrieve version-valid runbooks and similar resolved incidents.
5. Specialist agents execute in parallel where dependencies permit.
6. Correlator builds hypotheses and removes contradictory/unsupported proposals.
7. Every proposed action is typed: target, parameters, risk, rationale and evidence.
8. Deterministic policy evaluates environment, identity, blast radius, maintenance/change windows and risk.
9. Low-risk pre-approved actions may enter an execution queue. Production/high-risk actions require approval.
10. Executor uses a short-lived, least-privilege identity and idempotency key.
11. Verification checks SLO/error/saturation signals; failed verification triggers rollback or escalation.
12. Full evidence, decision, approver, execution and outcome are written to an immutable audit trail.

## 6. Reliability semantics

Assume **at-least-once delivery**. Every event and action needs an idempotency key. Persist workflow state rather than relying on an in-memory agent conversation. Use retry with exponential backoff only for retryable errors, circuit breakers around model/provider APIs, dead-letter queues, and replay tooling. Separate analysis retries from mutation retries—blindly replaying a mutation is unsafe.

Long-running workflows belong in Temporal, Step Functions, durable queues/workers, or an equivalent workflow engine. The FastAPI orchestrator here is deliberately compact for local demonstration.

## 7. Conflict resolution

Agents can disagree. Do not resolve disagreement by asking another model to "vote" without evidence. Normalize proposals, compare their evidence/freshness, enforce hard policy constraints, and escalate unresolved high-risk conflicts. Example: the scaler recommends adding capacity while the incident agent sees a bad deployment. A rollout-correlated error spike may make rollback the safer candidate, but the policy/workflow layer—not conversational confidence—determines what can happen.

## 8. Security model

Threats include prompt injection in source/logs, poisoned runbooks, malicious PR content, credential exfiltration, confused-deputy attacks, cross-tenant retrieval, unsafe generated shell commands, compromised dependencies, webhook spoofing, model-provider outage and audit tampering.

Controls: OIDC/workload identity, no long-lived cloud keys, least-privilege roles per action, egress allowlists, secret manager integration, tenant-scoped retrieval, signed webhooks, input size limits, structured tool calls, deny-by-default policy, immutable audit logs, image signing/SBOM/provenance, dependency scanning, network policies, sandboxed code analysis, and approval for production mutations. Never place secrets in prompts or vector stores.

## 9. Observability

Instrument API, orchestration, retrieval, model and executor spans with OpenTelemetry. Export operational metrics to Prometheus/Grafana: request rate/errors/latency, agent latency, model tokens/cost, retrieval latency/hit rate, policy denials, approval latency, action success/rollback, queue lag, incident MTTA/MTTR and SLO burn.

For LLM quality, separately track groundedness, evidence precision, unsupported-action rate, schema validity, retrieval recall, remediation acceptance, false-positive rate and dangerous-action proposal rate. Operational success metrics must not be conflated with model-quality metrics.

## 10. SLOs and capacity planning

Illustrative targets—not universal promises: API availability 99.9%+, p95 ingestion <300 ms excluding external dependencies, initial incident triage <30 s, and zero unauthorized production mutations as a safety objective. Capacity is driven by event rate × agent fan-out × average model calls × tokens/call. Apply per-tenant quotas, concurrency limits, model budgets and degradation modes. During a fleet-wide incident, prioritize deterministic telemetry and incident workflows over low-priority repository analysis to avoid an AI-induced retry storm.

## 11. Cost engineering

Use small/fast models for classification and extraction; escalate to larger models only for ambiguous correlation/reasoning. Cache retrieval and stable summaries by content hash. Bound transcript/log windows, deduplicate repeated alerts, batch embeddings, and impose per-incident token/tool budgets. Measure cost per analyzed PR, deployment and incident as first-class FinOps metrics.

## 12. Multi-region / cell architecture

At large scale, partition tenants/services into cells. Each cell owns ingress, workflow workers, retrieval namespace/cache and action queues. Keep the policy source centrally governed but locally cached/versioned. Route incidents to the service's home cell and preserve regional data residency. A cell failure should not become a global control-plane failure. Cross-region failover must preserve idempotency and must never duplicate a privileged action.

## 13. Evaluation

Maintain versioned offline datasets for secure/unsafe code changes, CI failures, scaling scenarios and historical incidents with approved evidence and outcomes. Evaluate retrieval recall, root-cause top-k recall, action precision, unsupported claims, policy bypass attempts and regression against previous prompt/model versions. Shadow new agents/models before canarying. Red-team prompt injection, malicious logs/runbooks, ambiguous telemetry and conflicting-agent scenarios.

Online evaluation should emphasize human acceptance, time-to-diagnosis, false positive/negative rates, rollback success and incident outcomes. Never optimize for "number of automated actions"—that creates the wrong incentive.

## 14. Repository layout

```text
app/
  agents/            # four specialist agents
  core/              # schemas, orchestration, retrieval, LLM and policy
  integrations/      # GitHub and AWS adapters
  main.py             # FastAPI API + metrics
lambda/               # AWS Lambda event bridge example
infra/k8s/            # Kubernetes deployment/service
infra/terraform/      # intentionally least-privilege infrastructure skeleton
.github/workflows/    # CI
 tests/               # API and authorization invariants
```

## 15. Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

Try the deterministic demo path:

```bash
curl -X POST http://localhost:8080/v1/analyze \
  -H 'content-type: application/json' \
  -d '{"tenant_id":"acme","repository":"acme/payments","environment":"prod","objective":"Investigate failed release","context":{"pipeline_status":"failed","deployment_status":"degraded","service":"payments-api","cpu_percent":91,"replicas":4,"error_rate":0.12,"latency_p95_ms":1800,"changed_files":["Dockerfile","src/payment.py"]}}'
```

Notice that scaling/rollback proposals for production are **not auto-authorized**.

Docker:

```bash
docker compose up --build
# API :8080, Prometheus :9090, Grafana :3000
```

## 16. Production extensions

Replace the in-process orchestrator with durable workflows; add PostgreSQL for workflow/audit state, Redis for bounded caching, Kafka/SQS/PubSub for events, OpenTelemetry Collector, enterprise vector search, OPA/Cedar or equivalent policy, Vault/Secrets Manager, GitHub App authentication, Kubernetes controller adapters, AWS AssumeRole with session policies, approval integrations, signed action receipts, and service catalog/CMDB integration.

Implement real security scanners (CodeQL/Semgrep/Trivy/Grype/Checkov etc.) as independent deterministic tools and feed their results to the Code Analyzer. Do not ask an LLM to substitute for those scanners.

## 17. Principal/Staff interview discussion

Be prepared to defend: why LLMs are outside the authorization boundary; how you prevent prompt injection from repositories/logs; at-least-once semantics and idempotent mutations; how rollback verification works; agent conflict resolution; stale telemetry and retrieval freshness; tenant isolation; model/provider failure; fleet-wide incident load shedding; model/cost routing; auditability; regional cells; change-management integration; and how you prove a new model is safer before enabling actions.

The strongest design principle is simple: **reason probabilistically, authorize deterministically, execute narrowly, verify empirically, and audit everything.**

## 18. Safety note

This repository is a reference implementation. Do not point its demo action layer at production infrastructure without organization-specific IAM, policy, approval, testing, rollback and audit controls. The included policy intentionally blocks production mutations.
