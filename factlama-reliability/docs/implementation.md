# Reliability Implementation Plan

For concrete modules, algorithms, persistence, HTTP behavior and acceptance fixtures, use [LOW_LEVEL_IMPLEMENTATION.md](LOW_LEVEL_IMPLEMENTATION.md). This file owns task status; a task is not complete solely because it appears in the specification.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

A task is COMPLETE only when code, tests, failure handling, tenant isolation, observability, documentation, and acceptance criteria are satisfied.

## REL-01 Foundation — STATUS: IN_PROGRESS
- [x] Create source module boundaries matching architecture. `judges/providers.py` (mixed vendor-free + vendor-coupled code) is split into `judges/port.py` (the vendor-neutral `JudgeProvider` abstraction), `judges/providers.py` (`MockModelProvider`/`RuleBasedProvider`, no vendor SDK) and `judges/vendor_adapters.py` (`EmbeddingProvider`/`NLIProvider`, sentence-transformers/transformers/torch) -- the split is what makes the dependency rule below actually enforceable, not just true by lazy-import convention.
- [x] Add logging conventions (`core/logging_config.py`, tested).
- [ ] Add a configuration model and health/readiness endpoints. Deliberately deferred: no service exists yet to configure or serve health from -- REL-12 (API) is where these get a real home, not a placeholder module with nothing to configure.
- [x] Add lint/type/test foundations: `ruff check`/`ruff format` (full ruleset, zero violations), `mypy --strict`-adjacent config with the pydantic plugin (zero errors, no blanket `# type: ignore`), `pytest` (151 passed, 1 skipped), wired into `.github/workflows/ci.yml` across Python 3.10-3.12. Verified against a genuinely fresh checkout + fresh venv (Python 3.11), not just the working `.venv`.
- [x] Add schema/API version conventions. Pre-existing: `schema_version="0.1"` with `validate_schema_version()` rejecting unsupported versions; now also lint/type-checked.
- [x] Add dependency rules preventing core -> provider SDK coupling. `import-linter` contracts in `pyproject.toml` (`[tool.importlinter]`), run in CI: `schemas` cannot import `core`/`judges`; `schemas`/`core` cannot import `sentence_transformers`/`transformers`/`torch`/`openai`/`anthropic` even transitively (this is what forced the `judges/` split above -- the old single-module layout could not pass this contract).

**Acceptance:** clean checkout builds/tests; module dependency rules are documented and enforceable. Met for this repo alone. Not marked COMPLETE: the configuration-model/health item is genuinely unstarted (deferred, not forgotten), and G1 (the cross-repo gate this task belongs to) also requires OBS-01, which has not started -- `factlama-observability` has no code yet, only documentation.

## REL-02 Tenant and security context — STATUS: NOT_STARTED
- [ ] Tenant/project/application context model.
- [ ] Propagate context through API/services/async/persistence.
- [ ] Tenant-aware repository interfaces.
- [ ] Negative cross-tenant tests.
- [ ] Secret/provider credential isolation.

**Acceptance:** no persistence/query path is tenant-implicit; cross-tenant access fails safely.

## REL-03 Public contracts and provenance — STATUS: NOT_STARTED
- [ ] VerificationRequest and VerificationResult.
- [ ] Claim, Evidence, Citation, ToolExecution, Violation, Score models.
- [ ] Verdict/action enums.
- [ ] Evaluator/model/configuration/policy provenance.
- [ ] Serialization and compatibility tests.

## REL-04 Claim engine — STATUS: NOT_STARTED
- [ ] Accept explicit claims or extract claims from answer.
- [ ] Stable claim IDs.
- [ ] Preserve source offsets/references where practical.
- [ ] Unit and golden tests.

## REL-05 Evidence engine — STATUS: NOT_STARTED
- [ ] Direct supplied evidence support.
- [ ] EvidenceRetriever interface.
- [ ] Evidence normalization and mapping.
- [ ] Source metadata/provenance.
- [ ] Insufficient-evidence behavior.

## REL-06 Judge provider — STATUS: NOT_STARTED
- [ ] JudgeProvider interface.
- [ ] First working provider adapter.
- [ ] Bounded timeouts/cancellation.
- [ ] Normalize provider errors/timeouts.
- [ ] Provider version/config provenance.

## REL-07 Verification pipeline — STATUS: NOT_STARTED
- [ ] Claim/evidence evaluation orchestration.
- [ ] SUPPORTED/CONTRADICTED/UNSUPPORTED/INSUFFICIENT_EVIDENCE outcomes.
- [ ] Aggregate result.
- [ ] Synchronous API path.
- [ ] Deterministic golden tests.

## REL-08 Scoring — STATUS: NOT_STARTED
- [ ] Transparent score calculation.
- [ ] Groundedness, hallucination risk, contradiction risk.
- [ ] Explicit confidence/provenance.
- [ ] Calibration hook for future benchmark-driven scoring.

## REL-09 Policy engine — STATUS: NOT_STARTED
- [ ] Policy inputs and actions.
- [ ] Deterministic rule evaluation.
- [ ] PASS/FAIL/REGENERATE/RETRIEVE_AGAIN/SWITCH_MODEL/ASK_USER/BLOCK/HUMAN_REVIEW.
- [ ] Decision provenance.

## REL-10 Async evaluation — STATUS: NOT_STARTED
- [ ] Job lifecycle.
- [ ] Idempotency keys.
- [ ] Retry/backoff and terminal failure state.
- [ ] Duplicate-delivery tests.
- [ ] Worker telemetry.

## REL-11 Content governance — STATUS: NOT_STARTED
- [ ] Configurable capture modes.
- [ ] Redaction hook before persistence.
- [ ] Retention interfaces.
- [ ] Metadata-only operation tests.

## REL-12 API and examples — STATUS: NOT_STARTED
- [ ] Versioned sync API.
- [ ] Async submission/status API.
- [ ] Error contract.
- [ ] Example groundedness request.
- [ ] Example tenant-isolated usage.

## REL-13 Evaluator ecosystem — STATUS: NOT_STARTED
- [ ] Tenant-approved provider registry and second/custom adapter path.
- [ ] Evaluator/configuration versioning and contract fixture suite.
- [ ] Explicit fallback provenance, quota and cost controls.

**Acceptance:** two adapters pass the same normalized success, ambiguity, timeout and malformed-response fixtures.

## REL-14 RAG and agent evaluation — STATUS: NOT_STARTED
- [ ] Citation support and retrieval quality signals with evidence lineage.
- [ ] Instruction adherence and tool selection/argument/result checks.
- [ ] Explicit `UNAVAILABLE` dimensions where an evaluator is absent.

**Acceptance:** each new dimension has a versioned method, golden cases and provenance; it does not change MVP groundedness semantics implicitly.

## REL-15 Benchmark and SLM gate — STATUS: NOT_STARTED
- [ ] Hand-reviewed development/test sets and leakage controls.
- [ ] Human/strong-judge baseline, per-class precision/recall/F1, calibration, latency and cost.
- [ ] SLM adapter only after a documented benchmark decision.

**Acceptance:** routing preference is based on reproducible results and thresholds approved in an ADR, not model size or cost claims alone.

## MVP end-product expectation

From a clean checkout, a developer can start the service, submit answer + supplied evidence, receive claim-level findings, scores, verdict, and provenance, repeat the same logical async request safely, and observe evaluation telemetry. The implementation must work without storing raw prompts/responses.

## Required test scenarios

1. Fully supported answer.
2. Partially supported answer.
3. Contradicted claim.
4. Unsupported claim.
5. Insufficient evidence.
6. Invalid request/schema version.
7. Provider timeout/failure.
8. Duplicate async delivery.
9. Cross-tenant read/write attempt.
10. Content capture disabled.
11. Stable serialization across supported schema versions.
12. Provenance present for every externally evaluated result.
