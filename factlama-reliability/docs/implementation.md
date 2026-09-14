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

**Acceptance:** clean checkout builds/tests; module dependency rules are documented and enforceable. Met for this repo alone. Not marked COMPLETE: the configuration-model/health item is genuinely unstarted (deferred, not forgotten, to REL-12). `factlama-observability`'s OBS-01 is now `COMPLETE`, so it no longer blocks G1 on this task's behalf -- REL-01 stays `IN_PROGRESS` solely on its own remaining item.

## REL-02 Tenant and security context — STATUS: IN_PROGRESS
- [x] Tenant/project/application context model. `schemas/tenancy.py`'s `TenantContext` (tenant_id required, project_id/application_id optionally narrowing scope) plus `authorizes(project_id, application_id)`, tested (5 tests). Nothing calls `authorizes()` from a real boundary yet -- there is no authenticated ingress until G3's sync API.
- [ ] Propagate context through API/services/async/persistence. "Services" only, today: `Verifier.verify(request, tenant_id=...)`'s trusted string argument is unchanged, deliberately not yet rewired to require a `TenantContext` -- doing that before G3's API exists to construct one from real auth would be premature plumbing with no real caller. API/async/persistence propagation doesn't exist to test until G3/G5.
- [x] Tenant-aware repository interfaces. `core/repository.py`'s `TenantAwareRepository` `Protocol` -- every method takes an explicit `TenantContext`. No implementation exists yet (G5/OBS-06 own persistence); this is the contract a future one must satisfy.
- [ ] Negative cross-tenant tests. `TenantContext.authorizes()` has real negative tests (mismatched project/application scope correctly rejected), but a genuine "forged tenant field against a real API/data store" test needs G3's authenticated boundary and G5/OBS-06's persistence -- neither exists to attack yet.
- [ ] Secret/provider credential isolation. Nothing to isolate yet: every current provider (Mock, RuleBased, local Embedding/NLI models) uses no external credential. First real target is REL-13 (evaluator ecosystem), where a vendor API key first appears.

**Acceptance:** no persistence/query path is tenant-implicit; cross-tenant access fails safely. Partially met: the one thing testable without an API or persistence (typed-context authorization logic) is done and tested; the rest is a genuine gate dependency, not an oversight.

## REL-03 Public contracts and provenance — STATUS: COMPLETE
- [x] VerificationRequest and VerificationResult. Aligned to `contracts/v0.1` exactly: `VerificationRequest` gained a `claims` field (unconsumed, wire-compat only) and now rejects a client-supplied `tenant_id` outright (`model_validator(mode="before")`) instead of silently dropping it. `VerificationResult` gained `dispute_reason`/`supersedes` and the full `DISPUTED`/`BUDGET_EXHAUSTED`/`NO_COMPLIANT_PROVIDER`/`REVOKED` vocabulary (unreachable by this pipeline today, but required so every valid canonical fixture still parses).
- [x] Claim, Evidence, Citation, ToolExecution, Violation, Score models. `Claim.id`→`claim_id`; `Evidence.id`/`extracted_text`→`evidence_id`/`content`+`reference` (mutually exclusive, validated); `ClaimVerification` rebuilt as contracts/v0.1's `ClaimResult` shape (`evidence_ids`, `rationale_code`, `text_status`, `contributing_judgments`, SUPPORTED-requires-evidence validated); `Violation.claim_id`/`evidence_id`→plural `claim_ids`/`evidence_ids` arrays, `severity` uppercase `Severity` enum; `Citation.id`/`source_id`→`citation_id`/`evidence_id`; `ToolExecution.id`→`tool_execution_id`, `status` narrowed to the contract's 3 uppercase values; `Instruction.id`→`instruction_id`, `priority` uppercase. `JudgeRequest`/`JudgeResult` (the judge-boundary port) followed: `JudgeResult.evidence`→`evidence_ids: list[str]`, added `rationale_code`/`usage`.
- [x] Verdict/action enums. Pre-existing, now extended with the full v0.1 vocabulary (see VerificationResult above).
- [x] Evaluator/model/configuration/policy provenance. Pre-existing (`Attempt`/`Provenance`/`Usage`/`Cost`) -- already matched contracts/v0.1 before this pass; `Cost` gained `pricing_version`.
- [x] Serialization and compatibility tests. `tests/test_contract_fixtures.py`: every canonical `contracts/v0.1` example (success/partial/fail/abstained x2/failed-internal-error/disputed for VerificationResult; both VerificationRequest examples; JudgeRequest/JudgeResult examples) parses through this repo's own pydantic types, and every relevant invalid fixture is rejected by the specific rule it demonstrates. Wired into CI via a `factlama-architecture` sibling checkout (`FACTLAMA_CONTRACTS_DIR`). `ReliabilityEvent` fixtures are out of scope here -- this repo has no `ReliabilityEvent` model yet (G5's outbox); that belongs to Observability's OBS-03.

**Acceptance:** typed request/result round-trip against `contracts/v0.1`'s canonical fixtures, in this repo's own CI, both valid and invalid cases. Confirmed by an actual GitHub Actions run (run [34811808714](https://github.com/Factlama/factlama-reliability/actions/runs/34811808714), all 3 Python versions green, sibling `factlama-architecture` checkout included) after two real CI-only bugs the local venv couldn't surface: `actions/checkout` cannot place a repo outside `$GITHUB_WORKSPACE`, and `ruff check .` swept the checked-out sibling repo's own code before it was excluded. Marked COMPLETE for REL-03's own scope.

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
