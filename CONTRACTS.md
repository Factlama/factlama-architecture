# Cross-repository contracts (design baseline v0.1)

This document owns the wire-level agreement between Reliability and Observability. It is a design specification, not a claim that an API or SDK exists. `schema_version` is `0.1`; breaking changes require an ADR and a new major version. Implementations MUST reject unknown major versions, MAY ignore unknown additive fields within a supported major version, and MUST preserve unknown telemetry extension attributes only within configured size/cardinality limits. JSON uses UTF-8, RFC 3339 UTC timestamps, finite numbers, and opaque IDs. `null` means known absent; omitted means not supplied. No score may be inferred from an omitted field.

## Identity and authorization

`tenant_id` is established from authenticated identity at ingress, never trusted from an unverified payload. A client-supplied `project_id` and `application_id` are authorized within that tenant. APIs MAY echo these IDs but MUST reject a payload/query that disagrees with authenticated scope. Internal jobs carry a signed or otherwise trusted tenant context. Every stored row, index key, job, cache key, and query predicate is tenant-scoped. IDs are opaque strings (1–128 characters); `trace_id` and `span_id` follow OpenTelemetry encoding when supplied. `interaction_id` links a user-visible AI operation across traces; `evaluation_id` links Reliability results and telemetry. IDs alone never grant access.

## VerificationRequest

Required: `schema_version`, `request_id`, `project_id`, `application_id`, `answer`, and `evidence` (an array, possibly empty). `answer` is nonempty UTF-8 text. Optional: `question`, `instructions`, `claims`, `citations`, `tool_executions`, `interaction_id`, `trace_id`, `span_id`, `model`, `prompt_version`, `mode` (`FAST|STANDARD|DEEP`), `policy_id`, and `metadata`. `claims`, when supplied, are nonempty objects with unique `claim_id` and `text`; the engine must not silently re-extract them. `evidence` entries require unique `evidence_id` and exactly one of `content` or `reference`; optional source URI, title, retrieval rank/score, timestamp and trust label are descriptive metadata, never proof of truth. `citations` link a claim or answer span to evidence IDs. `tool_executions` contain tool name, status, timing and optional governed content. Payload and field limits are deployment configuration, documented by the API, and enforced before external judge calls.

## VerificationResult

Required: `schema_version`, `evaluation_id`, `request_id`, `tenant_id`, `project_id`, `application_id`, `created_at`, `status` (`COMPLETED|ABSTAINED|FAILED|DISPUTED`), `verdict` (`PASS|PARTIAL|FAIL|ABSTAIN|DISPUTED`), `claims`, `scores`, `violations`, and `provenance`. An abstained result requires `abstention_reason` (`NO_CHECKABLE_CLAIMS|INSUFFICIENT_EVIDENCE|PROVIDER_FAILURE|BUDGET_EXHAUSTED|NO_COMPLIANT_PROVIDER|REVOKED|CANCELLED`); a disputed result requires `dispute_reason=JUDGE_DISAGREEMENT`. Optional correlation IDs echo the request. Each claim requires `claim_id`, `verdict` (`SUPPORTED|CONTRADICTED|UNSUPPORTED|INSUFFICIENT_EVIDENCE|NOT_APPLICABLE|DISPUTED`), `evidence_ids`, `rationale_code`, `text_status` (`AVAILABLE|REDACTED|NOT_STORED`), and `contributing_judgments` (an array, empty when no valid judgment was returned, including provider failure). A contributing judgment identifies `attempt_id`, claim verdict, cited evidence IDs and rationale code; it does not replace the final claim verdict. `text` is present only when authorized and available. The immediate response may contain claim text even when persistence is metadata-only; later reads return `text_status=NOT_STORED` and omit `text`. Free-text rationale is optional and content-governed. Evidence IDs must resolve to request evidence; an empty link set is legitimate except for `SUPPORTED`, which requires at least one cited evidence ID. `scores` is a map of named dimensions to `{value?, status, method_version, calibration_class}` where status is `MEASURED|NOT_APPLICABLE|UNAVAILABLE`; `value` is a finite number in [0,1] only for `MEASURED`. A violation requires a stable code, severity, affected claim IDs, and evidence IDs. Reserved codes include `JUDGE_DISAGREEMENT` and `EVIDENCE_INJECTION_SUSPECTED`. A result records `policy_decision` separately from factual verdict. `provenance` includes evaluator ID/version, policy version if applied, started/completed timestamps, evaluation mode/routing-profile version, and nonempty `attempts[]` when a judge was called. Each attempt records `attempt_id`, provider/model/pinned model version, configuration version, qualification status, calibration class, outcome/error, timing and usage. It never includes credentials.

`FAILED` and `ABSTAINED` MUST have `verdict=ABSTAIN`; `DISPUTED` status MUST have `verdict=DISPUTED` and a `JUDGE_DISAGREEMENT` violation. A disagreement between valid attempts is not insufficient evidence or a provider failure. Provider timeout, transport failure, budget exhaustion or absence of a compliant provider is never `UNSUPPORTED` or `FAIL`. Factual verdict is computed independently of policy action. `PASS` requires all applicable factual claims supported. `PARTIAL` covers a mixture of supported and unresolved claims. `FAIL` requires a contradicted claim. Empty/wholly unevaluable claims produce `ABSTAINED/ABSTAIN`. A disputed claim prevents an aggregate PASS/FAIL until an explicit, versioned reconciliation policy exists; MVP does not perform majority voting. The exact aggregate and score rules are versioned in Reliability's scoring specification.

## Evaluator identity, attempts and budgets

`qualification_status` is `QUALIFIED|PROVISIONAL|UNQUALIFIED`. `calibration_class` is an opaque stable identifier derived from `(evaluator_id,evaluator_version,provider_id,pinned_model_id,configuration_version,qualification_status)` and its derivation version. It changes when any component changes, including qualification. A measured score is comparable only within one class. Cross-class score aggregates MUST group by class or be labeled `MIXED` and MUST NOT report a pooled mean/percentile as if calibrated. An unqualified/provisional provider may be explicitly selected, but cannot become a tenant's default judge. The SLM follows the same rule under ADR-010, which supersedes the SLM-only qualification gate in ADR-006.

For a score with no judge attempt, `calibration_class=NONE`; for a disputed score involving multiple valid classes, `calibration_class=MIXED` and status is `UNAVAILABLE`. Neither sentinel participates in class-specific score averages. They avoid inventing an evaluator identity for abstentions.

`provenance.attempts[]` is ordered and append-only. A normal MVP evaluation has one attempt; retries and sequential fallback add entries, including failed attempts. Each `usage` has input/output/total tokens when known, provider-reported cost or a derived cost with currency/pricing version, and latency; unknown cost is `UNAVAILABLE`, never zero. A result-level `usage_summary` sums known usage only within one currency, carries unknown counts and never conceals failed attempts. Historical results are immutable; re-evaluation creates a new `evaluation_id` and optional `supersedes` link. `mode` selects a versioned routing profile with claim/evidence caps, total deadline, token/cost ceilings, provider set and judgments-per-claim (one in MVP). `BUDGET_EXHAUSTED` is a normalized abstention reason and typed provider/dispatch error, not a factual verdict. Per-request and per-tenant-window budgets count retries and fallback; dispatch must reserve/check budget before every attempt. BYO-key is the default; tenant-approved provider credentials are resolved per call and billed by the provider to that tenant.

## Provider and retrieval ports

`JudgeProvider.evaluate(JudgeRequest, deadline, cancellation) -> JudgeResult` receives exactly one claim and bounded evidence references/content under capture policy. Evidence is untrusted data, structurally separated from versioned judge instructions. `JudgeResult` returns one normalized claim verdict, cited evidence IDs, provider confidence if available, rationale code, token/cost/latency metadata, and provenance. `SUPPORTED` without a cited evidence ID is `INVALID_RESPONSE`. A versioned, conservative non-model overlap/support check MUST run on cited evidence; clear unsupported-by-citation findings downgrade to `INSUFFICIENT_EVIDENCE` with a reason and violation. Lexical overlap alone is never proof, and legitimate paraphrase is not rejected solely for lacking shared words. Provider/dispatch errors are typed `TIMEOUT|RATE_LIMIT|UNAVAILABLE|INVALID_RESPONSE|CANCELLED|CONFIGURATION|BUDGET_EXHAUSTED|NO_COMPLIANT_PROVIDER|REVOKED`; adapters MUST NOT invent a factual verdict. Customer-supplied T2 judges implement a versioned HTTP `JudgeRequest`/`JudgeResult` wire schema out of process; the platform uses mTLS, allowed destinations, payload/deadline bounds and per-call scoped credential resolution. T0 first-party adapters may run in process; T1 partner adapters require signed, pinned, reviewed code and conformance. `EvidenceRetriever.retrieve(tenant_context, query, limits) -> Evidence[]` is optional; the MVP accepts supplied evidence and MUST NOT invoke retrieval without explicit configuration and authorization.

## ReliabilityEvent and AITrace

`ReliabilityEvent` requires `schema_version`, `event_id`, `tenant_id`, `evaluation_id`, `occurred_at`, `status`, `verdict`, score summaries with calibration class, evaluator version, `calibration_class`, `qualification_status`, `usage_summary`, and applicable `interaction_id`, `trace_id`, `span_id`, `project_id`, `application_id`. When multiple valid attempts from different classes contribute, event `calibration_class=MIXED`, `calibration_classes[]` lists each class, and `qualification_status=MIXED` when qualification differs; disputed scores are `UNAVAILABLE`. Failed attempts still contribute to usage but not to the valid-judgment class. It contains references and metadata, not prompt/response/evidence bodies or secrets. Event identity is stable across retries, and consumers deduplicate on `(tenant_id,event_id)`. Observability groups score distributions by calibration class and verification cost by currency/pricing version; mixed groups are labeled, not silently pooled. `AITrace` is an Observability read projection identified by tenant and trace/interaction ID; it contains spans, model/provider, latency, tokens, cost with currency and pricing-version provenance, errors, retrieval/tool metadata, and linked evaluation IDs. A missing evaluation is represented as pending/absent, never as PASS.

## Errors and pagination

HTTP errors use `{schema_version,error:{code,message,request_id,retryable,details?}}`. Stable codes: `INVALID_ARGUMENT`, `UNSUPPORTED_VERSION`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `PAYLOAD_TOO_LARGE`, `RATE_LIMITED`, `DEPENDENCY_UNAVAILABLE`, `INTERNAL`. Messages must not expose cross-tenant existence or secrets. `NOT_FOUND` is used for inaccessible tenant-scoped resources. List APIs use bounded `limit`, opaque `next_cursor`, and a required time window; cursors bind tenant, filters, sort order and expiry. Retries may return the same logical evaluation/job, but must not create a second result.

## Worked example

The authenticated tenant is `t-acme`; it is intentionally absent from the client request.

```json
{"schema_version":"0.1","request_id":"req-1","project_id":"p-demo","application_id":"a-rag","question":"When was Acme founded and by whom?","answer":"Acme was founded in 2018 by Jane Doe.","evidence":[{"evidence_id":"doc-1","content":"Acme was founded in 2018.","source_uri":"https://example.test/acme"}],"interaction_id":"int-1","mode":"STANDARD"}
```

```json
{
  "schema_version": "0.1",
  "evaluation_id": "eval-1",
  "request_id": "req-1",
  "tenant_id": "t-acme",
  "project_id": "p-demo",
  "application_id": "a-rag",
  "interaction_id": "int-1",
  "created_at": "2026-09-13T00:00:00Z",
  "status": "COMPLETED",
  "verdict": "PARTIAL",
  "claims": [
    {
      "claim_id": "c1",
      "text": "Acme was founded in 2018",
      "text_status": "AVAILABLE",
      "verdict": "SUPPORTED",
      "evidence_ids": [
        "doc-1"
      ],
      "rationale_code": "DIRECT_SUPPORT",
      "contributing_judgments": [
        {
          "attempt_id": "attempt-1",
          "verdict": "SUPPORTED",
          "evidence_ids": [
            "doc-1"
          ],
          "rationale_code": "DIRECT_SUPPORT"
        }
      ]
    },
    {
      "claim_id": "c2",
      "text": "Acme was founded by Jane Doe",
      "text_status": "AVAILABLE",
      "verdict": "UNSUPPORTED",
      "evidence_ids": [],
      "rationale_code": "NO_SUPPORT",
      "contributing_judgments": [
        {
          "attempt_id": "attempt-1",
          "verdict": "UNSUPPORTED",
          "evidence_ids": [],
          "rationale_code": "NO_SUPPORT"
        }
      ]
    }
  ],
  "scores": {
    "groundedness": {
      "value": 0.5,
      "status": "MEASURED",
      "method_version": "groundedness-0.1",
      "calibration_class": "class-1"
    }
  },
  "violations": [
    {
      "code": "UNSUPPORTED_CLAIM",
      "severity": "MEDIUM",
      "claim_ids": [
        "c2"
      ],
      "evidence_ids": []
    }
  ],
  "provenance": {
    "evaluator_id": "groundedness",
    "evaluator_version": "0.1",
    "policy_version": null,
    "mode": "STANDARD",
    "routing_profile_version": "standard-0.1",
    "started_at": "2026-09-13T00:00:00Z",
    "completed_at": "2026-09-13T00:00:00Z",
    "attempts": [
      {
        "attempt_id": "attempt-1",
        "provider_id": "example-judge",
        "model_id": "example-model",
        "pinned_model_version": "example-model-1",
        "configuration_version": "0.1",
        "qualification_status": "QUALIFIED",
        "calibration_class": "class-1",
        "outcome": "COMPLETED",
        "started_at": "2026-09-13T00:00:00Z",
        "completed_at": "2026-09-13T00:00:00Z",
        "usage": {
          "input_tokens": 180,
          "output_tokens": 42,
          "total_tokens": 222,
          "cost": {
            "status": "UNAVAILABLE"
          },
          "latency_ms": 240
        }
      }
    ]
  },
  "usage_summary": {
    "input_tokens": 180,
    "output_tokens": 42,
    "total_tokens": 222,
    "cost": {
      "status": "UNAVAILABLE"
    }
  }
}
```

This is illustrative fixture data, not a claim of calibrated confidence. The example's 0.5 score follows the MVP equal-weight claim rule in Reliability's scoring document.
