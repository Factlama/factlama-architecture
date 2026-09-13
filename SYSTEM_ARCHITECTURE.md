# FactLama System Architecture

## 1. Purpose

FactLama is an open-source AI reliability and observability platform for LLM, RAG, and agentic systems. It separates generation from verification and separates reliability decisions from telemetry transport/storage so enterprises can evolve models, storage engines, and deployment topology without breaking public contracts.

## 2. Architectural principles

1. **Contracts before implementations.** Public request/result, telemetry, provenance, and policy contracts are versioned and provider-independent.
2. **Multi-tenancy is P0.** Tenant identity is mandatory at ingress, service, persistence, query, and async boundaries.
3. **Evidence over opinion.** Reliability decisions must retain evidence references and evaluator provenance.
4. **Provider independence.** Core logic depends on `JudgeProvider`, `EvidenceRetriever`, and storage abstractions, never directly on a vendor SDK.
5. **OTEL first, not OTEL only.** OpenTelemetry concepts are the interoperability boundary; FactLama may enrich them with AI-specific semantics.
6. **Simple startup path, enterprise deployment path.** Local Docker Compose first; enterprise deployment must support external identity, storage, observability, networking, and orchestration.
7. **Privacy by configuration.** Metadata-only operation must remain possible. Raw prompts/responses are never required for core telemetry.
8. **Failure isolation.** Evaluator, collector, storage, and dashboard failures must not unnecessarily fail the customer application.
9. **Idempotent asynchronous work.** Retries and duplicate delivery must not create duplicate logical evaluations.
10. **Observable platform.** FactLama emits telemetry about its own health, latency, queues, provider calls, failures, and policy decisions.

## 3. System context

```text
AI Application / Agent / RAG
        |
        | SDK / OTEL / API
        v
+------------------------------+
| FactLama Ingress Layer       |
| API + Collector              |
+---------------+--------------+
                |
        +-------+--------+
        |                |
        v                v
+---------------+  +-------------------+
| Reliability   |  | Observability     |
| Engine        |  | Processing        |
+-------+-------+  +---------+---------+
        |                    |
        v                    v
+---------------+  +-------------------+
| Judge/Evidence|  | Telemetry Stores  |
| Providers     |  | + Query API       |
+-------+-------+  +---------+---------+
        |                    |
        +---------+----------+
                  v
         +------------------+
         | Native Dashboard |
         +------------------+
```

## 4. Repository responsibilities

### factlama-architecture
System-level source of truth. Owns product boundaries, cross-repository contracts, architecture decisions, security/privacy principles, deployment modes, roadmap, and Claude implementation governance.

### factlama-reliability
Owns claims, evidence, judge abstraction, evaluation pipeline, scoring, policy decisions, provenance, RAG evaluation, and agent/tool evaluation.

### factlama-observability
Owns SDK/OTEL ingestion, collector behavior, telemetry normalization, storage/query abstractions, AI semantic telemetry, dashboard, alerts, exporters, and trace/reliability correlation.

## 5. Reliability path

```text
VerificationRequest
  -> validate tenant/schema
  -> extract or accept claims
  -> map supplied evidence
  -> select JudgeProvider
  -> evaluate claim/evidence pairs
  -> normalize findings
  -> calculate transparent scores
  -> apply policy
  -> attach provenance
  -> persist metadata/result
  -> emit reliability telemetry
  -> return VerificationResult
```

The core must not know whether the judge is FactLama SLM, OpenAI, Anthropic, Azure, an enterprise-internal model, or a custom adapter.

## 6. Observability path

```text
Application
  -> FactLama SDK / OTEL
  -> Collector
  -> validation + tenant context
  -> telemetry normalization
  -> processing/enrichment
  -> TelemetryStore
  -> Query API
  -> Dashboard / Alerts / Exporters
```

The dashboard depends on the Query API, not directly on a database implementation.

## 7. Shared correlation model

Every applicable record should support stable IDs for:
- tenant
- project/application
- interaction
- trace
- span
- evaluation
- model/provider/version
- prompt version
- evaluator/version
- policy/version

These IDs allow a user to move from a production trace to the reliability decision that evaluated it.

## 8. Core enterprise cross-cutting requirements

### Security
Authentication, authorization, tenant isolation, secret isolation, least privilege, secure defaults, auditable control-plane changes, encryption-compatible deployment.

### Privacy
Configurable content capture, pre-persistence redaction, retention controls, metadata-only mode, future data residency support, explicit interaction-store enablement.

### Reliability
Timeouts, cancellation, retries with bounded backoff, circuit breaking where external dependencies justify it, deterministic idempotency behavior, dead-letter/recovery strategy for async work.

### Scalability
Stateless APIs where possible, horizontal scale at ingestion/evaluation/query boundaries, storage abstraction, bounded payloads, pagination, backpressure, async execution for expensive work.

### Operability
Structured logs, metrics, traces, health/readiness endpoints, dependency status, version/build metadata, SLO-ready metrics, support bundle strategy in future.

### Compatibility
Versioned APIs/schemas/events, additive evolution by default, explicit deprecation policy, evaluator/version provenance, migration strategy for persistent schemas.

## 9. MVP architecture

MVP must prove a complete vertical slice:
1. instrument an LLM/RAG app;
2. ingest telemetry;
3. evaluate an answer against supplied evidence;
4. return claim-level normalized results with provenance;
5. correlate evaluation with trace;
6. query telemetry/reliability data;
7. render AI overview and trace/reliability detail in the native dashboard;
8. run locally using Docker Compose;
9. preserve tenant isolation and metadata-only operation.

## 10. Full-scope architecture

Adds multiple judge providers, citation and instruction evaluation, RAG quality metrics, agent/tool evaluation, policy routing, alerts, replay datasets, enterprise identity, pluggable storage/exporters, Kubernetes, and broader integrations.

## 11. Future architecture

Adds FactLama SLM training/runtime, benchmark platform, confidence-aware verification cascade, hybrid/vector evidence retrieval when justified, large-scale distributed execution, advanced data residency, customer-managed storage/key patterns, and deeper enterprise governance.
