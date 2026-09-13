# Data Flow

## Primary runtime flow

```text
AI App
 -> SDK/OTEL/API
 -> Ingress/Collector
 -> normalize tenant + correlation IDs
 -> Observability processing
 -> TelemetryStore
 -> Query API
 -> Dashboard

AI App or platform
 -> Verification API
 -> Reliability pipeline
 -> Claims
 -> Evidence mapping
 -> JudgeProvider
 -> Scoring
 -> Policy
 -> VerificationResult + Provenance
 -> Reliability telemetry
 -> Query API / Dashboard
```

## Data classes

### Control-plane metadata
Tenant, project, configuration, evaluator registration, policy versions, retention settings, provider references. Must be auditable.

### Telemetry metadata
Trace/span IDs, model/provider, latency, token usage, cost, operation type, error state, retrieval/tool metadata, reliability scores. This should be sufficient for metadata-only operation.

### Reliability data
Verification request metadata, claims, evidence references, findings, scores, violations, verdict, policy action, evaluator provenance.

### Sensitive interaction content
Prompts, responses, evidence payloads, tool arguments/results, judge raw outputs. Storage is optional and governed separately.

## Flow invariants

- Tenant context is established before persistence or query.
- Correlation identifiers are preserved across async boundaries.
- Sensitive content is redacted before persistence when capture is enabled.
- Provider credentials never enter telemetry or evaluation payload persistence.
- Public results contain evaluator provenance without exposing secrets.
- Retries preserve logical evaluation identity.

## Failure behavior

- Telemetry ingestion failure should not normally fail customer inference.
- Judge/provider failure returns normalized evaluator failure/abstention according to policy; it must not be misreported as a factual verdict.
- Storage/query failure is surfaced with bounded retries and health telemetry.
- Async terminal failures remain inspectable and recoverable.
