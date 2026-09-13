# FactLama

FactLama is an open-source AI reliability and observability platform for LLM, RAG, and agentic applications.

Its purpose is to make AI systems measurable, evidence-aware, debuggable, and governable without forcing every verification decision through another expensive frontier-model call.

## Product thesis

- Expensive model = intelligence/generation.
- FactLama Reliability = evidence-based evaluation, scoring, policy, and decisions.
- FactLama SLM = optional low-cost verifier that must earn its role through benchmarks.
- FactLama Observability = AI-native telemetry, traces, metrics, costs, reliability signals, and dashboard.

## Repository boundaries

| Repository | Responsibility |
|---|---|
| `factlama-architecture` | System architecture, product scope, ADRs, contracts, security boundaries, roadmap, Claude implementation guidance |
| `factlama-reliability` | Claims, evidence, judges, verification, scoring, policies, RAG/agent evaluation, reliability API/SDK |
| `factlama-observability` | OTEL/SDK ingestion, collector, telemetry processing, storage, query API, dashboard, alerts, exporters |

Do not create separate repositories for API, core, schemas, ingestion, dashboard, SDK, collector, integrations, deployment, or docs until independent release/versioning pressure justifies it.

## Scope

### MVP

A locally deployable product that can:

1. accept an AI interaction/evaluation request;
2. evaluate groundedness/hallucination against supplied evidence;
3. return normalized claim-level and overall reliability results with provenance;
4. isolate tenants and enforce secure defaults;
5. run evaluations synchronously and asynchronously;
6. ingest AI telemetry using OTEL-compatible concepts;
7. correlate traces with reliability results;
8. show requests, latency, tokens, cost, reliability, and traces in a native dashboard;
9. run with a simple Docker Compose developer experience.

### Full product scope

- Multiple evaluator/judge providers.
- RAG retrieval and answer evaluation.
- Agent/tool-use evaluation.
- Policy orchestration and verification routing.
- Cost-aware judge routing.
- Alerts and regression detection.
- Native dashboard plus external exporters.
- Configurable interaction capture, replay, and evaluation datasets.
- RBAC, SSO, enterprise deployment and integrations.

### Future scope

- FactLama SLM training/runtime.
- Benchmark service and public benchmark reports.
- Confidence- and risk-aware verification cascade.
- Vector/hybrid evidence retrieval where justified.
- Large-scale distributed execution and advanced data residency controls.

## Non-goals for MVP

- Building a general-purpose Grafana/Splunk replacement.
- Building a custom time-series database.
- Building a general-purpose vector database.
- Building a generic RAG platform.
- Training the FactLama SLM before the evaluator contracts and benchmark harness are stable.

## Required reading order

1. `docs/vision.md`
2. `docs/architecture.md`
3. `docs/scope.md`
4. `docs/domain-model.md`
5. `docs/security.md`
6. `docs/testing-strategy.md`
7. `docs/claude-implementation-guide.md`
8. `roadmap.md`
9. ADRs under `docs/ADR/`

## Core principle

**Simple by default, interoperable by design.**

The startup path should be close to `docker compose up`. Enterprises should be able to integrate FactLama with existing OpenTelemetry, observability, identity, storage, and model platforms.