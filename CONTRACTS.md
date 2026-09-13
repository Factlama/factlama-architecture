# Cross-repository contracts (design baseline v0.1)

This document owns the wire-level agreement between Reliability and Observability. It is a design specification, not a claim that an API or SDK exists. `schema_version` is `0.1`; breaking changes require an ADR and a new major version. Implementations MUST reject unknown major versions, MAY ignore unknown additive fields within a supported major version, and MUST preserve unknown telemetry extension attributes only within configured size/cardinality limits. JSON uses UTF-8, RFC 3339 UTC timestamps, finite numbers, and opaque IDs. `null` means known absent; omitted means not supplied. No score may be inferred from an omitted field.

## Identity and authorization

`tenant_id` is established from authenticated identity at ingress, never trusted from an unverified payload. A client-supplied `project_id` and `application_id` are authorized within that tenant. APIs MAY echo these IDs but MUST reject a payload/query that disagrees with authenticated scope. Internal jobs carry a signed or otherwise trusted tenant context. Every stored row, index key, job, cache key, and query predicate is tenant-scoped. IDs are opaque strings (1–128 characters); `trace_id` and `span_id` follow OpenTelemetry encoding when supplied. `interaction_id` links a user-visible AI operation across traces; `evaluation_id` links Reliability results and telemetry. IDs alone never grant access.

## VerificationRequest

Required: `schema_version`, `request_id`, `project_id`, `application_id`, `answer`, and `evidence` (an array, possibly empty). `answer` is nonempty UTF-8 text. Optional: `question`, `instructions`, `claims`, `citations`, `tool_executions`, `interaction_id`, `trace_id`, `span_id`, `model`, `prompt_version`, `mode` (`FAST|STANDARD|DEEP`), `policy_id`, and `metadata`. `claims`, when supplied, are nonempty objects with unique `claim_id` and `text`; the engine must not silently re-extract them. `evidence` entries require unique `evidence_id` and exactly one of `content` or `reference`; optional source URI, title, retrieval rank/score, timestamp and trust label are descriptive metadata, never proof of truth. `citations` link a claim or answer span to evidence IDs. `tool_executions` contain tool name, status, timing and optional governed content. Payload and field limits are deployment configuration, documented by the API, and enforced before external judge calls.

## VerificationResult

Required: `schema_version`, `evaluation_id`, `request_id`, `tenant_id`, `project_id`, `application_id`, `created_at`, `status` (`COMPLETED|ABSTAINED|FAILED`), `verdict` (`PASS|PARTIAL|FAIL|ABSTAIN`), `claims`, `scores`, `violations`, and `provenance`. Optional correlation IDs echo the request. Each claim requires `claim_id`, `verdict` (`SUPPORTED|CONTRADICTED|UNSUPPORTED|INSUFFICIENT_EVIDENCE|NOT_APPLICABLE`), `evidence_ids`, `rationale_code`, and `text_status` (`AVAILABLE|REDACTED|NOT_STORED`); `text` is present only when authorized and available. The immediate response may contain claim text even when persistence is metadata-only; later reads return `text_status=NOT_STORED` and omit `text`. Free-text rationale is optional and content-governed. Evidence IDs must resolve to request evidence; empty evidence links are legitimate. `scores` is a map of named dimensions to `{value, status, method_version}` where status is `MEASURED|NOT_APPLICABLE|UNAVAILABLE`; `value` is a finite number in [0,1] only for `MEASURED`. A violation requires a stable code, severity, affected claim IDs, and evidence IDs. A result records `policy_decision` separately from factual verdict. `provenance` includes evaluator/provider ID, evaluator version, model identifier/version when applicable, configuration/prompt version, policy version if applied, started/completed timestamps, and evaluation mode; unavailable fields are explicitly marked absent. It never includes credentials.

`FAILED` and `ABSTAINED` MUST have `verdict=ABSTAIN`; provider timeout or transport failure is never `UNSUPPORTED` or `FAIL`. Factual verdict is computed independently of policy action. `PASS` requires all applicable factual claims supported. `PARTIAL` covers a mixture of supported and unresolved claims. `FAIL` requires a contradicted claim. Empty/wholly unevaluable claims produce `ABSTAINED/ABSTAIN`. The exact aggregate and score rules are versioned in Reliability's scoring specification.

## Provider and retrieval ports

`JudgeProvider.evaluate(JudgeRequest, deadline, cancellation) -> JudgeResult` receives one claim and bounded evidence references/content under capture policy. `JudgeResult` returns one normalized claim verdict, cited evidence IDs, provider confidence if available, rationale code, token/cost/latency metadata, and provenance. Provider errors are typed `TIMEOUT|RATE_LIMIT|UNAVAILABLE|INVALID_RESPONSE|CANCELLED|CONFIGURATION`; adapters MUST NOT invent a factual verdict. `EvidenceRetriever.retrieve(tenant_context, query, limits) -> Evidence[]` is optional; the MVP accepts supplied evidence and MUST NOT invoke retrieval without explicit configuration and authorization.

## ReliabilityEvent and AITrace

`ReliabilityEvent` requires `schema_version`, `event_id`, `tenant_id`, `evaluation_id`, `occurred_at`, `status`, `verdict`, score summaries, evaluator version, and applicable `interaction_id`, `trace_id`, `span_id`, `project_id`, `application_id`. It contains references, not prompt/response/evidence bodies. Event identity is stable across retries, and consumers deduplicate on `(tenant_id,event_id)`. `AITrace` is an Observability read projection identified by tenant and trace/interaction ID; it contains spans, model/provider, latency, tokens, cost with currency and pricing-version provenance, errors, retrieval/tool metadata, and linked evaluation IDs. A missing evaluation is represented as pending/absent, never as PASS.

## Errors and pagination

HTTP errors use `{schema_version,error:{code,message,request_id,retryable,details?}}`. Stable codes: `INVALID_ARGUMENT`, `UNSUPPORTED_VERSION`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `PAYLOAD_TOO_LARGE`, `RATE_LIMITED`, `DEPENDENCY_UNAVAILABLE`, `INTERNAL`. Messages must not expose cross-tenant existence or secrets. `NOT_FOUND` is used for inaccessible tenant-scoped resources. List APIs use bounded `limit`, opaque `next_cursor`, and a required time window; cursors bind tenant, filters, sort order and expiry. Retries may return the same logical evaluation/job, but must not create a second result.

## Worked example

The authenticated tenant is `t-acme`; it is intentionally absent from the client request.

```json
{"schema_version":"0.1","request_id":"req-1","project_id":"p-demo","application_id":"a-rag","question":"When was Acme founded and by whom?","answer":"Acme was founded in 2018 by Jane Doe.","evidence":[{"evidence_id":"doc-1","content":"Acme was founded in 2018.","source_uri":"https://example.test/acme"}],"interaction_id":"int-1","mode":"STANDARD"}
```

```json
{"schema_version":"0.1","evaluation_id":"eval-1","request_id":"req-1","tenant_id":"t-acme","project_id":"p-demo","application_id":"a-rag","interaction_id":"int-1","created_at":"2026-09-13T00:00:00Z","status":"COMPLETED","verdict":"PARTIAL","claims":[{"claim_id":"c1","text":"Acme was founded in 2018","text_status":"AVAILABLE","verdict":"SUPPORTED","evidence_ids":["doc-1"],"rationale_code":"DIRECT_SUPPORT"},{"claim_id":"c2","text":"Acme was founded by Jane Doe","text_status":"AVAILABLE","verdict":"UNSUPPORTED","evidence_ids":[],"rationale_code":"NO_SUPPORT"}],"scores":{"groundedness":{"value":0.5,"status":"MEASURED","method_version":"groundedness-0.1"}},"violations":[{"code":"UNSUPPORTED_CLAIM","severity":"MEDIUM","claim_ids":["c2"],"evidence_ids":[]}],"provenance":{"evaluator_id":"groundedness","evaluator_version":"0.1","provider_id":"example-judge","model_id":"example-model","configuration_version":"0.1","mode":"STANDARD","started_at":"2026-09-13T00:00:00Z","completed_at":"2026-09-13T00:00:00Z"}}
```

This is illustrative fixture data, not a claim of calibrated confidence. The example's 0.5 score follows the MVP equal-weight claim rule in Reliability's scoring document.
