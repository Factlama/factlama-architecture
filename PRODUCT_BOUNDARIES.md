# Product Boundaries

## Owns
FactLama owns AI reliability evaluation and AI-native observability.

### Reliability
Claims, evidence mapping, judge/evaluator abstractions, groundedness, hallucination, contradiction, citation support, instruction adherence, tool correctness, RAG evaluation, agent evaluation, scoring, policy and decisions.

### Observability
OTEL-compatible ingestion, AI telemetry, traces, metrics, token/cost/latency/error data, reliability-signal correlation, query APIs, alerts, exporters and the native dashboard.

## Does not own in MVP
- General-purpose RAG orchestration
- A custom vector database
- A custom time-series database
- A generic Grafana/Splunk replacement
- Mandatory Kafka or Kubernetes
- SLM training before contracts and benchmarks stabilize

## Architecture-ready but deferred
- Interaction content storage/replay
- Hybrid/vector evidence retrieval
- FactLama SLM
- Benchmark service
- Enterprise SSO/RBAC/data-residency controls

## Principle
Simple by default, interoperable by design.

## Judge-call economics

The economic model for future metered adapters is bring-your-own-key: tenants provide approved provider credentials and pay providers directly. MVP supports local, unmetered evaluators with resource limits and available usage reporting. Metered providers and BYO-key dispatch are post-MVP, gated on hard budget enforcement under [ADR-017](adr/ADR-017-mvp-unmetered-evaluators.md). FactLama does not broker or mark up model calls. A hosted/brokered tier would require a new ADR and abuse/billing model.
