# FactLama Roadmap

Use [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for the cross-repository order, dependencies, handoffs and exit tests. This file alone owns EPIC status. ADR-010–015 are accepted architecture decisions; their implementation remains `NOT_STARTED`.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

Claude must update task status only after acceptance criteria and tests pass.

## Phase A — Foundation

### EPIC-01 Repository and engineering foundation — STATUS: COMPLETE
- [x] Establish source/test/example layouts in implementation repos. `factlama-reliability` done (see REL-01). `factlama-observability`: `sdk/`, `collector/{ingress,processing}/`, `storage/`, `query/`, `operations/` Python packages, a `dashboard/` Vite+React+TypeScript scaffold, `tests/`, `examples/` placeholder -- see OBS-01 (`COMPLETE`).
- [x] Add configuration conventions. `factlama-reliability`'s REL-12 API gave this a real home: `api/settings.py`'s env-driven `Settings` plus `GET /health/live`/`GET /health/ready` (REL-01, now `COMPLETE`). `factlama-observability`'s `operations/config.py` foundation (env-var resolution helpers) was already done for OBS-01's own scope.
- [x] Add lint/type/test/CI foundations. `factlama-reliability`: ruff/mypy/pytest/`import-linter`, `.github/workflows/ci.yml` across Python 3.10-3.12, confirmed green on GitHub Actions (run [34754686765](https://github.com/Factlama/factlama-reliability/actions/runs/34754686765)). `factlama-observability`: same Python toolchain (22 tests, 100% coverage on `operations/`) plus a dashboard toolchain (eslint/tsc/vitest/build, 0 audited npm vulnerabilities); `.github/workflows/ci.yml` confirmed green on GitHub Actions on first push (run [34756423331](https://github.com/Factlama/factlama-observability/actions/runs/34756423331), all 4 jobs).
- [x] Add API/schema versioning conventions. `factlama-reliability`: pre-existing (`schema_version="0.1"`). [`contracts/v0.1/`](../contracts/README.md) JSON Schemas make the rule (reject unknown major, accept unknown minor) machine-checked. `factlama-observability`'s `operations/versioning.py` enforces the identical rule for its own future wire types; nothing emits/accepts a real payload yet.
- [x] Add dependency boundary rules. `factlama-reliability`: `import-linter` contracts (`schemas` has no internal dependencies; `schemas`/`core` cannot reach a vendor model SDK, even transitively), enforced in CI. `factlama-observability`: `import-linter` contracts (`sdk` cannot depend on `collector`/`storage`/`query`; `storage` cannot depend on `collector`/`query`/`sdk`; `query` cannot depend on `collector`/`sdk`), all `KEPT`.

**Exit:** clean checkout builds/tests and architecture boundaries are documented/enforced. `factlama-observability`'s OBS-01 is `COMPLETE`, confirmed by an actual GitHub Actions run, not just local reproduction. `factlama-reliability`'s REL-01 is now also `COMPLETE`, once REL-12's API gave the deferred configuration-model/health item a real home. Both foundations closed.

### EPIC-02 Tenancy and security foundation — STATUS: IN_PROGRESS
- [x] Tenant/project/application identity model. `factlama-reliability`'s `schemas/tenancy.py` `TenantContext` (tenant_id + optional project/application scope, with a real `authorizes()` check, tested) -- see REL-02. `factlama-observability`'s `schemas/tenancy.py` has the identical model -- see OBS-02.
- [ ] Tenant context propagation. `factlama-reliability` closed for its own scope: `api/app.py`'s synchronous `POST /v0.1/verifications` authenticates to a `TenantContext` and calls `.authorizes()` before dispatch -- a real API now exists to construct one from. `factlama-observability` still has nowhere to propagate through: no ingress (OBS-04), and neither repo has async/persistence (G5/OBS-06) yet.
- [ ] Tenant-aware persistence/query interfaces. `factlama-reliability`'s `core/repository.py` `TenantAwareRepository` `Protocol` exists as a contract with zero implementations (no persistence exists to implement it against). `factlama-observability` has none yet.
- [ ] Cross-tenant negative tests. `factlama-reliability` closed for its own scope: `tests/test_api.py::TestCrossTenantIsolation` is a genuine forged-tenant-field/cross-tenant test against the live API (403 on a scoped credential's mismatched project, 400 on a body-supplied `tenant_id`), not just `TenantContext.authorizes()` unit tests. `factlama-observability` still needs OBS-04's ingress to exist to attack; neither repo can test the persistence half yet (G5/OBS-06).
- [x] Bounded payload validation (ingress-side). `factlama-observability`'s `operations/payload_bounds.py` (body size, attribute count, attribute value length), tested. No ingress calls it yet (OBS-04).
- [ ] Secret/provider credential boundaries. Nothing to bound yet -- no provider in either repo uses an external credential today.
- [ ] Capture/redaction configuration model.
- [ ] Separate provider registration, tenant approval, credential use and content-read permissions.
- [ ] Enforce judge-egress destination, secret-scope and adapter trust-tier boundaries before opening customer judges.

**Exit:** cross-tenant access fails safely; metadata-only operation works. Met for `factlama-reliability`'s synchronous API path. `factlama-observability` still has no live boundary to test against (OBS-04), and neither repo has persistence (G5/OBS-06) -- those remain the real gap, not an oversight.

## Phase B — Reliability Engine

### EPIC-03 Evaluation contracts and provenance — STATUS: IN_PROGRESS
- [x] Versioned VerificationRequest/VerificationResult. `factlama-reliability` done -- see REL-03 (`COMPLETE`), confirmed by CI running `contracts/v0.1`'s canonical fixtures through its own types.
- [x] Claim/Evidence/Violation/Score/Verdict types. `factlama-reliability` done, same evidence as above.
- [x] Evaluator/model/configuration provenance. `factlama-reliability` done (pre-existing `Attempt`/`Provenance`, now contract-aligned).
- [x] `calibration_class` and qualification status on scores/events. `factlama-reliability`'s scores done; `factlama-observability`'s `ReliabilityEvent` (OBS-03) carries the event side, including the `MIXED` -> `calibration_classes` rule, fixture-tested against all 3 canonical events.
- [x] Ordered `attempts[]` with usage, and claim `contributing_judgments[]`. `factlama-reliability` done.
- [x] Reserve `DISPUTED`, `JUDGE_DISAGREEMENT`, `EVIDENCE_INJECTION_SUSPECTED` and `BUDGET_EXHAUSTED` semantics. `factlama-reliability`'s types accept the full vocabulary (unreachable by its own pipeline until G5/G3/G10 respectively); the vocabulary itself was reserved in `CONTRACTS.md` at G0.
- [ ] Versioned routing profile, usage summary and `supersedes` lineage. `factlama-reliability` has all three fields; nothing sets `supersedes` yet (no result ever supersedes another until G5's retries exist).
- [x] Contract serialization tests. `factlama-reliability`'s `tests/test_contract_fixtures.py` and `factlama-observability`'s `tests/test_contract_fixtures.py`, both confirmed green in their own CI against a `factlama-architecture` sibling checkout.

**Exit:** the worked fixture and negative variants round-trip in both implementation repos; no scalar-only provider assumption remains. Met for `VerificationRequest`/`VerificationResult`/`ReliabilityEvent`. Stays `IN_PROGRESS`: `factlama-observability`'s `AITrace`/span/resource model has no executable `contracts/v0.1` schema to round-trip against yet -- only prose exists, and OBS-03's remaining scope is deliberately waiting on that rather than guessing a shape.

### EPIC-04 First groundedness evaluator — STATUS: IN_PROGRESS
- [x] Claim extraction/segmentation. `factlama-reliability`'s `EnhancedClaimExtractor` (clause-level splitting); explicit caller-supplied claims are now consumed unchanged when present (REL-04).
- [x] Evidence mapping. `SimpleEvidenceMapper` (word-overlap/negation heuristic).
- [x] JudgeProvider abstraction. `judges/port.py`'s bounded `JudgeProvider.evaluate()` port.
- [x] First provider adapter. T0 in-process (ADR-011): `EmbeddingProvider`/`NLIProvider`, real downloaded models, no vendor API key -- see REL-06.
- [x] Claim-level supported/contradicted/unsupported/insufficient findings. `judge-provider.md`'s response-validation chain (`validate_judge_result` -> `apply_citation_support_check` -> `detect_evidence_injection`).
- [x] Transparent scoring and overall verdict. `core/scoring.py`'s claim-ratio formulas and `determine_verdict()`.
- [x] Golden evaluation tests. `tests/test_verifier.py::TestGoldenCases` plus this pass's `tests/test_dispatch_gates.py`/`tests/test_api.py`.
- [x] Enforce one-claim-per-call, evidence instruction/data separation and deterministic response validation. Pre-existing (`JudgeRequest` carries exactly one claim; evidence is a separate typed field, never concatenated into instructions).
- [ ] Enforce per-request/per-tenant token/cost ceilings and claim/evidence fan-out caps before dispatch, including retry/fallback accounting. Per-request claim/evidence fan-out caps now enforced (`core/budgets.py`, REL-04/REL-07). Per-tenant token/cost ceilings and retry/fallback accounting remain G5's -- there is no retry/fallback to account for yet.
- [ ] Record judge attempt usage/cost; BYO-key is the default. `Attempt.usage`/`JudgeResult.usage` exist and are plumbed through, but no current T0 adapter reports a non-default `Usage` -- the in-process embedding/NLI models incur no per-call token/dollar cost to report. This item stays open until a metered adapter (a vendor LLM judge, or a T0 adapter with real compute accounting) exists.
- [x] Include adversarial-evidence fixtures. `tests/test_dispatch_gates.py::TestEvidenceInjectionDefense`: an injection-laden but genuinely irrelevant evidence fixture never becomes SUPPORTED, and a genuinely-supporting-but-injection-laden fixture is flagged `EVIDENCE_INJECTION_SUSPECTED`, not silently ignored.
- [ ] Injection-suspected policy routing. The violation is surfaced in the result, but `PolicyEngine.evaluate()` does not yet special-case `EVIDENCE_INJECTION_SUSPECTED` into a specific action (e.g. forcing `HUMAN_REVIEW`) the way it does for `TOOL_ERROR`. Open.

**Exit:** a T0 adapter produces valid supported/contradicted/unsupported/insufficient findings, while timeout, exhausted budget and suspected injection cannot silently produce PASS -- met. Not yet met: judge usage/cost recording (no metered adapter exists yet) and explicit injection-suspected policy routing.

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
