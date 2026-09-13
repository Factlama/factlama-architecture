# FactLama Roadmap

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

Claude must update task status only after acceptance criteria and tests pass.

## Phase A — Foundation

### EPIC-01 Repository and engineering foundation — STATUS: NOT_STARTED
- [ ] Establish source/test/example layouts in implementation repos.
- [ ] Add configuration conventions.
- [ ] Add lint/type/test/CI foundations.
- [ ] Add API/schema versioning conventions.
- [ ] Add dependency boundary rules.

**Exit:** clean checkout builds/tests and architecture boundaries are documented/enforced.

### EPIC-02 Tenancy and security foundation — STATUS: NOT_STARTED
- [ ] Tenant/project/application identity model.
- [ ] Tenant context propagation.
- [ ] Tenant-aware persistence/query interfaces.
- [ ] Cross-tenant negative tests.
- [ ] Secret/provider credential boundaries.
- [ ] Capture/redaction configuration model.

**Exit:** cross-tenant access fails safely; metadata-only operation works.

## Phase B — Reliability Engine

### EPIC-03 Evaluation contracts and provenance — STATUS: NOT_STARTED
- [ ] Versioned VerificationRequest/VerificationResult.
- [ ] Claim/Evidence/Violation/Score/Verdict types.
- [ ] Evaluator/model/configuration provenance.
- [ ] Contract serialization tests.

### EPIC-04 First groundedness evaluator — STATUS: NOT_STARTED
- [ ] Claim extraction/segmentation.
- [ ] Evidence mapping.
- [ ] JudgeProvider abstraction.
- [ ] First provider adapter.
- [ ] Claim-level supported/contradicted/unsupported/insufficient findings.
- [ ] Transparent scoring and overall verdict.
- [ ] Golden evaluation tests.

### EPIC-05 Content governance — STATUS: NOT_STARTED
- [ ] NONE/METADATA_ONLY/REDACTED/FULL capture modes.
- [ ] Redaction hooks before persistence.
- [ ] Retention abstraction.
- [ ] Separate telemetry metadata from optional interaction content.

### EPIC-06 Async evaluation — STATUS: NOT_STARTED
- [ ] Job lifecycle.
- [ ] Idempotency keys.
- [ ] Retry/backoff/terminal failures.
- [ ] Duplicate delivery tests.

### EPIC-07 Evaluator ecosystem — STATUS: NOT_STARTED
- [ ] Provider registry.
- [ ] Second/custom provider path.
- [ ] Evaluator/config versioning.
- [ ] Normalized timeout/error handling.

### EPIC-08 Policy and routing — STATUS: NOT_STARTED
- [ ] Policy input/action model.
- [ ] Deterministic rule engine.
- [ ] Decision provenance.
- [ ] Risk/cost routing interface.

## Phase C — Observability

### EPIC-09 OTEL/telemetry core — STATUS: NOT_STARTED
- [ ] OTEL-compatible ingestion.
- [ ] AI semantic attributes/events.
- [ ] TelemetryStore abstraction.
- [ ] Query API.
- [ ] Trace/evaluation correlation.
- [ ] FactLama self-observability.

## Phase D — Native Dashboard

### EPIC-10 Dashboard — STATUS: NOT_STARTED
- [ ] AI overview.
- [ ] LLM requests/models/latency/tokens/cost/errors.
- [ ] Reliability view.
- [ ] Trace explorer.
- [ ] RAG/agent foundations.

## Phase E — SDK/Collector/Integrations

### EPIC-11 Instrumentation — STATUS: NOT_STARTED
- [ ] Minimal SDK.
- [ ] Collector configuration.
- [ ] End-to-end example app.
- [ ] Exporter abstraction.

## Phase F — FactLama SLM and Benchmarks

### EPIC-12 SLM/benchmark foundation — STATUS: NOT_STARTED
- [ ] Benchmark datasets/harness.
- [ ] Baseline strong judges/human labels.
- [ ] Accuracy/precision/recall/F1/calibration/latency/token/cost reporting.
- [ ] SLM adapter/runtime only after benchmarks justify it.

## Phase G — Interaction Store and Enterprise

### EPIC-13 Interaction Store/replay — STATUS: NOT_STARTED
- [ ] Explicit opt-in interaction persistence.
- [ ] Retention/redaction/encryption integration.
- [ ] Replay/evaluation dataset flow.

### EPIC-14 Enterprise hardening — STATUS: NOT_STARTED
- [ ] RBAC/SSO integration points.
- [ ] Kubernetes deployment.
- [ ] Data residency/customer-managed storage patterns.
- [ ] Enterprise exporters/integrations.
- [ ] Upgrade/deprecation/support policies.

## MVP completion gate

MVP is complete only when a developer can start FactLama locally, instrument an LLM/RAG request, ingest telemetry, run groundedness evaluation against evidence, see claim-level results and provenance, correlate the evaluation to the trace, inspect it in the dashboard, and run documented API/SDK examples with automated security/contract/integration tests passing.
