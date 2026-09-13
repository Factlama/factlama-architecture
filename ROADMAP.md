# FactLama Roadmap

Use [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for the cross-repository order, dependencies, handoffs and exit tests. This file alone owns EPIC status. ADR-010–015 are accepted architecture decisions; their implementation remains `NOT_STARTED`.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

Claude must update task status only after acceptance criteria and tests pass.

## Phase A — Foundation

### EPIC-01 Repository and engineering foundation — STATUS: IN_PROGRESS
- [x] Establish source/test/example layouts in implementation repos. `factlama-reliability` done (see REL-01). `factlama-observability`: `sdk/`, `collector/{ingress,processing}/`, `storage/`, `query/`, `operations/` Python packages, a `dashboard/` Vite+React+TypeScript scaffold, `tests/`, `examples/` placeholder -- see OBS-01.
- [ ] Add configuration conventions. Deferred in `factlama-reliability` until REL-12's API exists to configure. `factlama-observability`'s `operations/config.py` adds env-var resolution helpers, but no component reads them yet (first real caller is OBS-04/OBS-07) -- foundation only, not a configured service.
- [x] Add lint/type/test/CI foundations. `factlama-reliability`: ruff/mypy/pytest/`import-linter`, `.github/workflows/ci.yml` across Python 3.10-3.12, confirmed green on GitHub Actions (run `34754686765`). `factlama-observability`: same Python toolchain (22 tests, 100% coverage on `operations/`) plus a dashboard toolchain (eslint/tsc/vitest/build, 0 audited npm vulnerabilities); `.github/workflows/ci.yml` authored and every step reproduced locally, not yet confirmed green on GitHub Actions itself (this push will be the first run).
- [x] Add API/schema versioning conventions. `factlama-reliability`: pre-existing (`schema_version="0.1"`). [`contracts/v0.1/`](../contracts/README.md) JSON Schemas make the rule (reject unknown major, accept unknown minor) machine-checked. `factlama-observability`'s `operations/versioning.py` enforces the identical rule for its own future wire types; nothing emits/accepts a real payload yet.
- [x] Add dependency boundary rules. `factlama-reliability`: `import-linter` contracts (`schemas` has no internal dependencies; `schemas`/`core` cannot reach a vendor model SDK, even transitively), enforced in CI. `factlama-observability`: `import-linter` contracts (`sdk` cannot depend on `collector`/`storage`/`query`; `storage` cannot depend on `collector`/`query`/`sdk`; `query` cannot depend on `collector`/`sdk`), all `KEPT`.

**Exit:** clean checkout builds/tests and architecture boundaries are documented/enforced. Met locally in both repos. Stays `IN_PROGRESS`: `factlama-observability`'s configuration item is foundation-only by design (see OBS-01), and neither repo's CI workflow has been confirmed green by an actual GitHub Actions run yet -- both were reproduced step-by-step locally instead.

### EPIC-02 Tenancy and security foundation — STATUS: NOT_STARTED
- [ ] Tenant/project/application identity model.
- [ ] Tenant context propagation.
- [ ] Tenant-aware persistence/query interfaces.
- [ ] Cross-tenant negative tests.
- [ ] Secret/provider credential boundaries.
- [ ] Capture/redaction configuration model.
- [ ] Separate provider registration, tenant approval, credential use and content-read permissions.
- [ ] Enforce judge-egress destination, secret-scope and adapter trust-tier boundaries before opening customer judges.

**Exit:** cross-tenant access fails safely; metadata-only operation works.

## Phase B — Reliability Engine

### EPIC-03 Evaluation contracts and provenance — STATUS: NOT_STARTED
- [ ] Versioned VerificationRequest/VerificationResult.
- [ ] Claim/Evidence/Violation/Score/Verdict types.
- [ ] Evaluator/model/configuration provenance.
- [ ] `calibration_class` and qualification status on scores/events.
- [ ] Ordered `attempts[]` with usage, and claim `contributing_judgments[]`.
- [ ] Reserve `DISPUTED`, `JUDGE_DISAGREEMENT`, `EVIDENCE_INJECTION_SUSPECTED` and `BUDGET_EXHAUSTED` semantics.
- [ ] Versioned routing profile, usage summary and `supersedes` lineage.
- [ ] Contract serialization tests.

**Exit:** the worked fixture and negative variants round-trip in both implementation repos; no scalar-only provider assumption remains.

### EPIC-04 First groundedness evaluator — STATUS: NOT_STARTED
- [ ] Claim extraction/segmentation.
- [ ] Evidence mapping.
- [ ] JudgeProvider abstraction.
- [ ] First provider adapter.
- [ ] Claim-level supported/contradicted/unsupported/insufficient findings.
- [ ] Transparent scoring and overall verdict.
- [ ] Golden evaluation tests.
- [ ] Enforce one-claim-per-call, evidence instruction/data separation and deterministic response validation.
- [ ] Enforce per-request/per-tenant token/cost ceilings and claim/evidence fan-out caps before dispatch, including retry/fallback accounting.
- [ ] Record judge attempt usage/cost; BYO-key is the default.
- [ ] Include adversarial-evidence fixtures and injection-suspected policy routing.

**Exit:** a T0 adapter produces valid supported/contradicted/unsupported/insufficient findings, while timeout, exhausted budget and suspected injection cannot silently produce PASS.

### EPIC-04b Evaluator agreement and qualification harness — STATUS: NOT_STARTED
- [ ] Public development and FactLama-held-out fixture sets with leakage controls.
- [ ] One-command conformance and agreement runner for every adapter.
- [ ] Versioned report with per-label quality, adversarial cases, latency, tokens and cost.
- [ ] Calibration-class derivation and a minimal pinned/approved default-judge gate.

**Exit:** the first T0 adapter has a reproducible agreement report and cannot become a tenant's default judge without `QUALIFIED` and tenant approval. EPIC-12 reuses this harness for the SLM.

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
- [ ] Ordered attempt provenance, dispute representation and budget accounting across retries/fallback.

### EPIC-07 Evaluator ecosystem — STATUS: NOT_STARTED
- [ ] Full audited registry lifecycle, conformance and agreement gates, pinned non-aliased model versions.
- [ ] T1 signed/reviewed adapter gate and T2 customer HTTP wire schema with mTLS, egress allowlist and per-call secret scope.
- [ ] Tenant compliance constraints on primary and fallback provider selection, including judge-egress residency.
- [ ] Revocation propagation, scheduled agreement canary, per-provider bulkheads and circuit breakers.
- [ ] Second/custom provider path only after those gates pass.
- [ ] Evaluator/config versioning.
- [ ] Normalized timeout/error handling.

**Exit:** two adapters pass the same conformance suite; T2 code is out of process; revoked, drifting or noncompliant providers cannot be selected by default or fallback.

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
- [ ] Judge usage/cost event ingestion and calibration-class-aware score aggregation.

## Phase D — Native Dashboard

### EPIC-10 Dashboard — STATUS: NOT_STARTED
- [ ] AI overview.
- [ ] LLM requests/models/latency/tokens/cost/errors.
- [ ] Reliability view.
- [ ] Trace explorer.
- [ ] RAG/agent foundations.
- [ ] Show qualification/calibration class, judge attempt/cost provenance, and mixed-class trend markers.
- [ ] Render judge rationale as inert text; distinguish disputed, abstained and failed results.

## Phase E — SDK/Collector/Integrations

### EPIC-11 Instrumentation — STATUS: NOT_STARTED
- [ ] Minimal SDK.
- [ ] Collector configuration.
- [ ] End-to-end example app.
- [ ] Exporter abstraction.

## Phase F — FactLama SLM and Benchmarks

### EPIC-12 SLM/benchmark foundation — STATUS: NOT_STARTED
- [ ] Reuse EPIC-04b's provider-neutral harness; add SLM-specific datasets/training workflow only where needed.
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
