# Reliability Implementation Plan

For concrete modules, algorithms, persistence, HTTP behavior and acceptance fixtures, use [LOW_LEVEL_IMPLEMENTATION.md](LOW_LEVEL_IMPLEMENTATION.md). This file owns task status; a task is not complete solely because it appears in the specification.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

A task is COMPLETE only when code, tests, failure handling, tenant isolation, observability, documentation, and acceptance criteria are satisfied.

## REL-01 Foundation — STATUS: COMPLETE
- [x] Create source module boundaries matching architecture. `judges/providers.py` (mixed vendor-free + vendor-coupled code) is split into `judges/port.py` (the vendor-neutral `JudgeProvider` abstraction), `judges/providers.py` (`MockModelProvider`/`RuleBasedProvider`, no vendor SDK) and `judges/vendor_adapters.py` (`EmbeddingProvider`/`NLIProvider`, sentence-transformers/transformers/torch) -- the split is what makes the dependency rule below actually enforceable, not just true by lazy-import convention.
- [x] Add logging conventions (`core/logging_config.py`, tested).
- [x] Add a configuration model and health/readiness endpoints. REL-12's API is now that real home: `api/settings.py`'s env-driven `Settings` (tenant credentials, max body bytes) and `api/app.py`'s `GET /health/live`/`GET /health/ready`. `/health/ready` is equivalent to `/health/live` today since no durable dependency (DB, queue) exists yet to check -- honest, not a placeholder pretending otherwise.
- [x] Add lint/type/test foundations: `ruff check`/`ruff format` (full ruleset, zero violations), `mypy --strict`-adjacent config with the pydantic plugin (zero errors, no blanket `# type: ignore`), `pytest` (232 passed, 1 skipped), wired into `.github/workflows/ci.yml` across Python 3.10-3.12. Verified against a genuinely fresh checkout + fresh venv (Python 3.11), not just the working `.venv`.
- [x] Add schema/API version conventions. Pre-existing: `schema_version="0.1"` with `validate_schema_version()` rejecting unsupported versions; now also lint/type-checked.
- [x] Add dependency rules preventing core -> provider SDK coupling. `import-linter` contracts in `pyproject.toml` (`[tool.importlinter]`), run in CI: `schemas` cannot import `core`/`judges`/`api`; `schemas`/`core` cannot import `sentence_transformers`/`transformers`/`torch`/`openai`/`anthropic` even transitively; `schemas`/`core`/`judges` cannot import `api` (the new outermost layer) -- this is what forced the `judges/` split above -- the old single-module layout could not pass this contract.

**Acceptance:** clean checkout builds/tests; module dependency rules are documented and enforceable. Met, including the configuration-model/health item once REL-12 gave it a real home to live in.

## REL-02 Tenant and security context — STATUS: IN_PROGRESS
- [x] Tenant/project/application context model. `schemas/tenancy.py`'s `TenantContext` (tenant_id required, project_id/application_id optionally narrowing scope) plus `authorizes(project_id, application_id)`, tested (5 tests). Now called from a real boundary: `api/app.py`'s `authenticate()` dependency.
- [x] Propagate context through API/services. `api/app.py`'s synchronous `POST /v0.1/verifications` authenticates an `Authorization: Bearer <key>` header to a `TenantContext` (`api/auth.py`'s config-driven `TenantCredentialStore` -- no credential database exists yet, so this is env-var-configured, not a public signup flow), calls `.authorizes(project_id, application_id)` before the request ever reaches `Verifier.verify()`, and passes the authenticated `tenant_id` through unchanged. `Verifier.verify(request, tenant_id=...)`'s own trusted string argument is still unchanged -- the API is what now constructs that argument honestly, rather than a caller doing it by hand. Async/persistence propagation still doesn't exist to test until G5.
- [x] Tenant-aware repository interfaces. `core/repository.py`'s `TenantAwareRepository` `Protocol` -- every method takes an explicit `TenantContext`. No implementation exists yet (G5/OBS-06 own persistence); this is the contract a future one must satisfy.
- [x] Negative cross-tenant tests, API portion. `tests/test_api.py::TestCrossTenantIsolation` and `::TestRequestValidation::test_client_supplied_tenant_id_is_rejected` are genuine forged-tenant-field/cross-tenant tests against a running HTTP boundary (a scoped credential gets 403 on a different project; a body-supplied `tenant_id` gets 400), not typed-context logic against a Python argument. The data-store half ("...or data store") still needs G5/OBS-06's persistence to exist to attack.
- [ ] Secret/provider credential isolation. Nothing to isolate yet: every current provider (Mock, RuleBased, local Embedding/NLI models) uses no external credential. First real target is REL-13 (evaluator ecosystem), where a vendor API key first appears.

**Acceptance:** no persistence/query path is tenant-implicit; cross-tenant access fails safely. Met for every path that exists today (the synchronous API); the remaining gap is a genuine gate dependency (G5 persistence, REL-13 credentials), not an oversight.

## REL-03 Public contracts and provenance — STATUS: COMPLETE
- [x] VerificationRequest and VerificationResult. Aligned to `contracts/v0.1` exactly: `VerificationRequest` gained a `claims` field (unconsumed, wire-compat only) and now rejects a client-supplied `tenant_id` outright (`model_validator(mode="before")`) instead of silently dropping it. `VerificationResult` gained `dispute_reason`/`supersedes` and the full `DISPUTED`/`BUDGET_EXHAUSTED`/`NO_COMPLIANT_PROVIDER`/`REVOKED` vocabulary (unreachable by this pipeline today, but required so every valid canonical fixture still parses).
- [x] Claim, Evidence, Citation, ToolExecution, Violation, Score models. `Claim.id`→`claim_id`; `Evidence.id`/`extracted_text`→`evidence_id`/`content`+`reference` (mutually exclusive, validated); `ClaimVerification` rebuilt as contracts/v0.1's `ClaimResult` shape (`evidence_ids`, `rationale_code`, `text_status`, `contributing_judgments`, SUPPORTED-requires-evidence validated); `Violation.claim_id`/`evidence_id`→plural `claim_ids`/`evidence_ids` arrays, `severity` uppercase `Severity` enum; `Citation.id`/`source_id`→`citation_id`/`evidence_id`; `ToolExecution.id`→`tool_execution_id`, `status` narrowed to the contract's 3 uppercase values; `Instruction.id`→`instruction_id`, `priority` uppercase. `JudgeRequest`/`JudgeResult` (the judge-boundary port) followed: `JudgeResult.evidence`→`evidence_ids: list[str]`, added `rationale_code`/`usage`.
- [x] Verdict/action enums. Pre-existing, now extended with the full v0.1 vocabulary (see VerificationResult above).
- [x] Evaluator/model/configuration/policy provenance. Pre-existing (`Attempt`/`Provenance`/`Usage`/`Cost`) -- already matched contracts/v0.1 before this pass; `Cost` gained `pricing_version`.
- [x] Serialization and compatibility tests. `tests/test_contract_fixtures.py`: every canonical `contracts/v0.1` example (success/partial/fail/abstained x2/failed-internal-error/disputed for VerificationResult; both VerificationRequest examples; JudgeRequest/JudgeResult examples) parses through this repo's own pydantic types, and every relevant invalid fixture is rejected by the specific rule it demonstrates. Wired into CI via a `factlama-architecture` sibling checkout (`FACTLAMA_CONTRACTS_DIR`). `ReliabilityEvent` fixtures are out of scope here -- this repo has no `ReliabilityEvent` model yet (G5's outbox); that belongs to Observability's OBS-03.

**Acceptance:** typed request/result round-trip against `contracts/v0.1`'s canonical fixtures, in this repo's own CI, both valid and invalid cases. Confirmed by an actual GitHub Actions run (run [34811808714](https://github.com/Factlama/factlama-reliability/actions/runs/34811808714), all 3 Python versions green, sibling `factlama-architecture` checkout included) after two real CI-only bugs the local venv couldn't surface: `actions/checkout` cannot place a repo outside `$GITHUB_WORKSPACE`, and `ruff check .` swept the checked-out sibling repo's own code before it was excluded. Marked COMPLETE for REL-03's own scope.

## REL-04 Claim engine — STATUS: IN_PROGRESS
- [x] Accept explicit claims or extract claims from answer. `VerificationRequest.claims`, when non-empty, is now used unchanged instead of extraction (`Verifier.verify()`); a duplicate `claim_id` is rejected at request-validation time (`validate_unique_claim_ids`). Extraction still defaults to the pre-existing `EnhancedClaimExtractor` (clause-level splitting).
- [ ] Stable claim IDs. Explicit-claims mode: stable by construction (caller-assigned, uniqueness enforced). Extraction mode: IDs are extraction-order-based (`claim_NNN`) -- deterministic for one answer against one extractor version, but not stable across an edited answer, and there is no extractor-version field yet to detect a version change.
- [ ] Preserve source offsets/references where practical. `Claim.start_char`/`end_char` exist on the schema but neither extractor populates them.
- [x] Unit and golden tests. Pre-existing `tests/test_verifier.py::TestGoldenCases` (supported/partial/contradiction/insufficient-evidence/mixed), plus new `tests/test_dispatch_gates.py::TestExplicitClaimsMode` and the budget/injection fixtures below.

**Acceptance:** not yet met -- claim ID stability across an edited answer and source-offset preservation remain open; everything else is done and tested.

**Also closed this pass, pre-dispatch (ADR-012, shared by REL-04/REL-07):** `core/budgets.py`'s `MAX_CLAIMS_PER_REQUEST`/`MAX_EVIDENCE_PER_CLAIM`, checked once before any claim reaches a judge; exceeding either abstains `BUDGET_EXHAUSTED` with zero judge dispatch (`tests/test_dispatch_gates.py::TestVerifierBudgetGate`). Durable per-tenant-window token/cost ceilings across retries/fallback remain G5's, per EXECUTION_PLAN.md's gate mapping.

## REL-05 Evidence engine — STATUS: NOT_STARTED
- [ ] Direct supplied evidence support.
- [ ] EvidenceRetriever interface.
- [ ] Evidence normalization and mapping.
- [ ] Source metadata/provenance.
- [ ] Insufficient-evidence behavior.

## REL-06 Judge provider — STATUS: IN_PROGRESS
- [x] JudgeProvider interface. `judges/port.py`'s bounded `JudgeProvider.evaluate(JudgeRequest, deadline, cancellation) -> JudgeResult` (pre-existing).
- [x] First working provider adapter. ADR-011 T0, in-process: `judges/vendor_adapters.py`'s `EmbeddingProvider` (sentence-transformers cosine similarity) and `NLIProvider` (entailment/contradiction classification), both against real downloaded models (pre-existing, `tests/test_semantic_providers.py`, 13 tests, run separately from the base test suite since they need the `embeddings`/`nli` extras).
- [x] Bounded timeouts/cancellation. `judges/port.py`'s `bounded_check()`, called by every adapter before dispatch (pre-existing).
- [x] Normalize provider errors/timeouts. `JudgeErrorCode` (pre-existing `TIMEOUT|RATE_LIMIT|UNAVAILABLE|INVALID_RESPONSE|CANCELLED|CONFIGURATION`; this pass added `BUDGET_EXHAUSTED`/`NO_COMPLIANT_PROVIDER`/`REVOKED` to match CONTRACTS.md's full provider/dispatch-error vocabulary -- only the first two are produced by this pipeline yet, `REVOKED` needs G10's registry).
- [x] Provider version/config provenance. `Attempt.provider_id`/`configuration_version`/`calibration_class` (pre-existing).

**Acceptance:** met for a T0 in-process adapter. This pass added two things beyond field-completeness: (1) `JudgeProvider.compliance_tags` (default `frozenset()`, overridden `{"IN_PROCESS", "NO_EXTERNAL_EGRESS"}` by every current adapter) feeding a baseline `NO_COMPLIANT_PROVIDER` pre-dispatch check (`core/compliance.py`, `Policy.required_provider_compliance`) -- a static tag comparison, not G10's registry, per EXECUTION_PLAN.md's gate-mapping note. (2) `judges/port.py`'s `detect_evidence_injection()`: defense-in-depth flagging (not blocking -- the citation-overlap check already blocks) of cited evidence containing judge-directive-style language, surfaced as CONTRACTS.md's reserved `EVIDENCE_INJECTION_SUSPECTED` violation code (`tests/test_dispatch_gates.py::TestEvidenceInjectionDefense`).

## REL-07 Verification pipeline — STATUS: IN_PROGRESS
- [x] Claim/evidence evaluation orchestration. `core/verifier.py`'s `Verifier.verify()` (pre-existing); this pass added the pre-dispatch budget/compliance gates ahead of the per-claim loop (see REL-04/REL-06).
- [x] SUPPORTED/CONTRADICTED/UNSUPPORTED/INSUFFICIENT_EVIDENCE outcomes. Pre-existing, per `judge-provider.md`'s response-validation chain (`validate_judge_result` -> `apply_citation_support_check` -> now also `detect_evidence_injection`).
- [x] Aggregate result. `core/scoring.py`'s `determine_verdict()` (pre-existing), matching LOW_LEVEL_IMPLEMENTATION.md's verdict/score table.
- [x] Synchronous API path. New this pass: `api/app.py`'s `POST /v0.1/verifications` (REL-12).
- [x] Deterministic golden tests. Pre-existing `tests/test_verifier.py::TestGoldenCases`; this pass added `tests/test_dispatch_gates.py` (19 tests: budget/compliance gates, explicit-claims mode, injection fixtures) and `tests/test_api.py` (21 tests, full HTTP path).

**Acceptance:** met for the synchronous path with a T0 provider. Async orchestration (durable jobs, idempotency, retries/fallback) is REL-10/G5, not this task.

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

## REL-12 API and examples — STATUS: IN_PROGRESS
- [x] Versioned sync API. New `api/` package: `POST /v0.1/verifications` (API.md), `GET /health/live`, `GET /health/ready`. `api/auth.py`'s config-driven `TenantCredentialStore` (API-key -> `TenantContext`, env-var `FACTLAMA_TENANT_CREDENTIALS` JSON) is the real authenticated boundary `TenantContext`'s own docstring said was still missing -- there is no credential database yet (G5), so this is deliberately minimal, not a public signup flow. Confirmed against a real running `uvicorn` process with `curl`, not only `TestClient`: health check, 401 with no/bad key, a genuine 200 verification result, and a forged `tenant_id` rejected 400 -- not just asserted in-process.
- [ ] Async submission/status API. Deliberately out of scope for this pass: `POST /v0.1/verification-jobs` and its idempotency/outbox mechanics need G5's durable persistence, which does not exist in this repo. This is REL-10's job, not REL-12's, once G5 exists.
- [x] Error contract. `api/errors.py`: `{schema_version, error:{code, message, request_id, retryable, details?}}` with CONTRACTS.md's exact code vocabulary and status mapping (400/401/403/404/409/413/429/503/500); `retryable=true` only for `RATE_LIMITED`/`DEPENDENCY_UNAVAILABLE`.
- [x] Example groundedness request. Smoke-tested against a live server (see above); a runnable example script is not yet checked in.
- [x] Example tenant-isolated usage. `tests/test_api.py::TestCrossTenantIsolation` is exactly this, executable.

**Acceptance:** met for the synchronous surface. The full API.md route set (async jobs, cancellation) needs G5; a checked-in example script/README snippet (as opposed to a passing test demonstrating the same request) is a small remaining polish item, not a functional gap.

**Post-review fixes (2026-09-16):** an independent review of this pass's own diff found three real gaps, all fixed and each confirmed by a test that fails against the pre-fix code and passes against the fix (not just added and assumed correct):
- Evidence IDs had no uniqueness validator (`Claim.claim_id` did, `Evidence.evidence_id` didn't) -- the API accepted two evidence entries sharing one ID, silently ambiguous for every downstream ID-indexed lookup. Fixed: `VerificationRequest.validate_unique_evidence_ids` (`schemas/verification.py`), mirroring the existing claim-ID check.
- A malformed `Content-Length` header (`int()` on a non-numeric value) crashed into an uncontracted plain-text 500 instead of the documented JSON error envelope. Fixed: `api/app.py::_enforce_content_length_limit` now catches the parse failure and raises a typed `INVALID_ARGUMENT` 400. (A real HTTP client's malformed header is separately rejected by uvicorn/h11 at the transport layer before reaching the app at all -- the bug was only reachable via an in-process ASGI caller, e.g. `TestClient`, which is presumably how it was found; the fix is still correct defense-in-depth at the layer this code owns.)
- The API accepted a JSON body sent with any `Content-Type` (e.g. `text/plain`), contradicting API.md's "JSON content type ... required." Fixed: `api/app.py::_require_json_content_type`, checked before the body is even read.
- Separately flagged (not a correctness bug, a scalability one): the route awaited `Verifier.verify()` directly, and a model-heavy provider's blocking call would freeze the whole event loop for every concurrent request on that worker. Fixed: dispatched through `starlette.concurrency.run_in_threadpool`. `tests/test_api.py::TestAsyncDispatchDoesNotBlockEventLoop` is a genuine regression test -- verified failing (health check delayed ~0.32s behind a 0.3s blocking call) before the fix and passing (~0.05s) after.

14 new tests (`tests/test_dispatch_gates.py::TestUniqueEvidenceIds`; `tests/test_api.py::TestContentLengthGuard`/`TestJsonContentTypeGuard`/`TestAsyncDispatchDoesNotBlockEventLoop` plus three inline `TestRequestValidation` cases). 246 tests pass locally (1 skipped without `embeddings`/`nli` extras); `mypy`/`ruff`/`lint-imports` clean.

## G3 session summary — 2026-09-15 (reliability side)

**Implemented:** REL-04 (explicit claims + pre-dispatch caps), REL-06 (baseline provider-compliance gate + evidence-injection defense), REL-07 (pipeline wiring for both gates + the sync API path), REL-12 (new synchronous API) all taken to `IN_PROGRESS`; REL-02's API/negative-cross-tenant-test items closed for the paths that exist today.

**Architectural decisions:**
- Budget/compliance are checked once per request, before the per-claim judge-dispatch loop -- not per claim -- since both are request/provider-level properties (ADR-012; EXECUTION_PLAN.md's gate-mapping note on baseline `NO_COMPLIANT_PROVIDER`). A single synthetic failed `Attempt` records the reason; zero real judge calls happen.
- `JudgeProvider.compliance_tags` is a static tag set, not a registry lookup -- deliberately not G10-shaped. Every current adapter (Mock, RuleBased, Embedding, NLI) declares `{"IN_PROCESS", "NO_EXTERNAL_EGRESS"}` since none makes a network call inside `evaluate()`.
- Evidence-injection detection is defense-in-depth, layered after the existing citation-overlap check, not a replacement for it -- a judge that ignores an injection attempt entirely (the expected case, since evidence is untrusted data, never concatenated into instructions) still gets a correct verdict; the new signal only surfaces that an attempt existed in evidence the judge actually cited.
- `api/auth.py`'s `TenantCredentialStore` is config-driven (one JSON env var), not a database -- there is no credential store to build against yet (G5). This keeps the API a real authenticated boundary today without pretending a persistence layer exists.
- The API reads the request body manually (`await request.body()`) rather than a FastAPI-typed body parameter, so error responses match CONTRACTS.md's exact shape/codes instead of FastAPI's default 422 envelope.

**Files changed:** `core/budgets.py`, `core/compliance.py` (new); `core/verifier.py` (pre-dispatch gates, explicit-claims consumption, `_abstained_result` helper); `judges/port.py` (`compliance_tags`, `detect_evidence_injection`, `BUDGET_EXHAUSTED`/`NO_COMPLIANT_PROVIDER`/`REVOKED` error codes); `judges/providers.py`, `judges/vendor_adapters.py` (`compliance_tags` overrides); `schemas/policy.py` (`required_provider_compliance`); `schemas/verification.py` (`claims` now consumed, `validate_unique_claim_ids`); new `api/` package (`app.py`, `auth.py`, `errors.py`, `settings.py`); `tests/test_dispatch_gates.py`, `tests/test_api.py` (new, 40 tests total); `pyproject.toml` (`api` package/extra, import-linter contract); `.github/workflows/ci.yml`.

**Outstanding issues:**
- REL-04: claim-ID stability across an edited answer, and source-offset preservation, remain open (see REL-04 above).
- REL-02: secret/provider credential isolation and the data-store half of negative cross-tenant tests remain G5/REL-13.
- REL-12: async submission/status API is G5-blocked; a checked-in runnable example script is a small polish item.
- REL-05, REL-08, REL-09 status is unchanged this pass -- not audited, not touched. A future pass should reconcile their ledger status against the pre-existing prototype the same way REL-04/06/07 were reconciled here, rather than assume NOT_STARTED is still accurate.

**Tests/status:** 232 tests pass locally (1 skipped in a bare-`[dev]` venv without the `embeddings`/`nli` extras; 13 semantic-provider tests pass separately against real downloaded models) across `mypy`/`ruff check`/`ruff format --check`/`lint-imports`, all clean, verified in both the working `.venv` and a fresh CI-equivalent venv built from `[dev]` extras only. The live API was also smoke-tested against a real `uvicorn` process with `curl`, not only `TestClient`.

**Next recommended steps:** G3's own remaining acceptance gap is narrow: claim-ID stability/offsets (REL-04) and a checked-in example script (REL-12) are the two small items; everything else G3 names (golden fixtures, injection resistance, timeout/budget/no-compliant-provider abstention, judge cost/attempt recording, sync API) now has passing evidence. REL-05/08/09's ledger status should be reconciled against the existing prototype before claiming G3 fully closed. G6 (Observability core) may now start in parallel per ROADMAP.md ("observability lane may progress in parallel with Reliability after G2"); it does not block on this pass's remaining REL-04/12 polish items.

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
