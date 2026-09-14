# Observability Implementation Plan

For concrete SDK, collector, processing, storage/query, dashboard and acceptance behavior, use [LOW_LEVEL_IMPLEMENTATION.md](LOW_LEVEL_IMPLEMENTATION.md). This file owns task status; a task is not complete solely because it appears in the specification.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

A task is COMPLETE only when code, tests, failure handling, tenant isolation, telemetry, documentation, and acceptance criteria are satisfied.

## G2 session summary — 2026-09-14 (observability side)

**Implemented:** OBS-02 (tenant-aware ingestion) and OBS-03 (AI telemetry model) taken to `IN_PROGRESS`, both from a zero-code starting point (OBS-01 was this repo's only prior work).

**Architectural decisions:**
- `schemas/` added as a new pure-data package (`import-linter`-enforced, no internal deps), mirroring Reliability's `schemas/` layout for consistency across repos.
- `AITrace`/span/resource model deliberately NOT built: `contracts/v0.1` has no executable schema for it yet, only prose in `telemetry-model.md`. Guessing a shape now risks rework once OBS-04/05 need it for real — only `ReliabilityEvent` (which has a canonical schema) was implemented.
- `ReliabilityEvent` matches `contracts/v0.1` exactly, including the `calibration_class=MIXED` → `calibration_classes` validator.

**Files changed:** `schemas/{__init__,tenancy,reliability_event}.py` (all new), `operations/payload_bounds.py` (new), `tests/{test_tenancy,test_payload_bounds,test_contract_fixtures}.py` (all new), `pyproject.toml`, `.github/workflows/ci.yml`, `README.md`. Commit `4d6b8b9` on `main`.

**Outstanding issues:**
- OBS-02: ingress validation, cross-tenant isolation tests, and SDK best-effort behavior all block on OBS-04 (collector) not existing yet.
- OBS-03: trace/span/event/resource model, model/provider/version attributes, token/cost/latency/error attributes, and retrieval/tool-call events are all blocked on a canonical schema not existing yet — not overlooked, deliberately deferred.
- OBS-04 through OBS-16: `NOT_STARTED`, unchanged this session.

**Tests/status:** CI green on `main` on first push — run [34812358199](https://github.com/Factlama/factlama-observability/actions/runs/34812358199), all 4 jobs (Python 3.10/3.11/3.12 + dashboard).

**Next recommended steps:** OBS-04 (collector) is the unblocking gate for the rest of OBS-02's acceptance criteria and gives the trace/span model in OBS-03 a real reason to be defined against a live ingestion path. Coordinate with Reliability's G3 API work — a real trace/span schema likely needs to be settled in `contracts/v0.1` (architecture repo) before either repo builds against it.

## OBS-01 Foundation — STATUS: COMPLETE
- [x] Establish source/test/example layouts. `sdk/`, `collector/{ingress,processing}/`, `storage/`, `query/`, `operations/` Python packages plus a `dashboard/` Vite+React+TypeScript scaffold and an `examples/` placeholder (real examples wait on OBS-13/OBS-07).
- [x] Add configuration, health, logging, lint/type/test foundations. `operations/{config,health,logging_config}.py` (22 tests, 100% coverage); dashboard has `npm run lint/typecheck/test/build`, all passing with 0 audited vulnerabilities.
- [x] Define API/event/schema versioning. `operations/versioning.py`'s `check_schema_version()` enforces the same major-reject/minor-accept rule the [`contracts/v0.1/`](../../contracts/README.md) schemas already enforce for Reliability; nothing in this repository emits or accepts a real payload yet, so no wire type uses it beyond its own tests.
- [x] Define module dependency boundaries. `import-linter` (3 forbidden contracts, all `KEPT`): `sdk` cannot depend on `collector`/`storage`/`query`; `storage` cannot depend on `collector`/`query`/`sdk`; `query` cannot depend on `collector`/`sdk`.

Storage migrations exist only as Alembic wiring (`storage/migrations/`, zero revisions, verified as a no-op against SQLite) -- that is this task's full scope; the actual `spans`/`reliability_events`/`evaluation_links` schema is OBS-06, not re-scoped here. `operations/config.py`'s env helpers have no caller yet (first real one is OBS-04/OBS-07) -- foundation only, by design, not a configured service.

`.github/workflows/ci.yml` (Python 3.10-3.12 matrix: ruff/mypy/import-linter/pytest/alembic smoke test; Node 24: eslint/tsc/vitest/build) ran green on GitHub Actions from a clean checkout on first push (run [34756423331](https://github.com/Factlama/factlama-observability/actions/runs/34756423331), all 4 jobs passed).

**Acceptance:** clean checkout builds/tests; module dependency rules are documented and enforceable. Confirmed by an actual GitHub Actions run against a clean checkout, not merely reproduced locally. Marked COMPLETE for OBS-01's own scope; this does not make OBS-02 and later any less `NOT_STARTED`.

## OBS-02 Tenant-aware ingestion — STATUS: IN_PROGRESS
- [x] Tenant/project/application context. `schemas/tenancy.py`'s `TenantContext`, identical model to `factlama-reliability`'s (tenant_id + optional project/application scope, real `authorizes()` check, tested).
- [ ] Validate tenant context at ingress. No ingress exists yet (OBS-04) to validate at.
- [ ] Cross-tenant isolation tests. `TenantContext.authorizes()` has real negative tests; a test against a real ingress/data store needs OBS-04/OBS-06 to exist first.
- [x] Bounded payload validation. `operations/payload_bounds.py`'s `validate_payload_bounds()` (body size, attribute count, attribute value length -- the three limits LOW_LEVEL_IMPLEMENTATION.md names), tested (5 tests). No ingress calls it yet.
- [ ] Non-blocking/best-effort SDK behavior. This is OBS-13's SDK queue/export behavior, not built here; `sdk/` is still an empty package.

**Acceptance:** tenant context validated at ingress; cross-tenant isolation demonstrated; bounded payloads. Partially met: the two things testable without a live ingress (typed context authorization, payload-bound checking) are done and tested; the rest is a genuine gate dependency on OBS-04.

## OBS-03 AI telemetry model — STATUS: IN_PROGRESS
- [ ] Trace/span/event/resource model. Not started: `contracts/v0.1` has no executable schema for `AITrace`/span/resource yet, only prose (`CONTRACTS.md`/`telemetry-model.md`). Defining one now without a canonical fixture to validate against risks guessing wrong ahead of OBS-04/05 actually needing it -- deliberately deferred, not overlooked.
- [ ] Model/provider/version attributes. Part of the undefined trace/span model above.
- [ ] Token/cost/latency/error attributes. Part of the undefined trace/span model above; `ReliabilityEvent.usage_summary` (below) covers evaluation-side usage only, not AI-request-side.
- [ ] Retrieval/tool-call events. Part of the undefined trace/span model above.
- [x] Reliability correlation attributes -- for the event side. `schemas/reliability_event.py`'s `ReliabilityEvent` (contracts/v0.1's exact shape, including the `calibration_class=MIXED` -> `calibration_classes` validator) carries `evaluation_id`/`interaction_id`/`trace_id`/`span_id` for correlation; `tests/test_contract_fixtures.py` runs all 3 canonical fixtures (completed/abstained/disputed) through it, confirmed green in this repo's own CI (sibling `factlama-architecture` checkout, run [34812358199](https://github.com/Factlama/factlama-observability/actions/runs/34812358199)). The trace side of correlation (a span carrying an `evaluation_id` back-reference) waits on the trace/span model above.
- [x] Prompt/evaluator/policy version references. `ReliabilityEvent.evaluator_version` done; prompt/policy versions live on the (not yet built) trace/span side.

**Acceptance:** typed telemetry model matching CONTRACTS.md, its event side fixture-tested against `contracts/v0.1`. Met for `ReliabilityEvent` only -- the trace/span/resource side has no contract to implement against yet.

## OBS-04 Collector — STATUS: NOT_STARTED
- [ ] OTEL-compatible ingestion path.
- [ ] FactLama SDK ingestion path.
- [ ] Validation and normalization.
- [ ] Backpressure/queue strategy.
- [ ] Retry/drop metrics.

## OBS-05 Processing and enrichment — STATUS: NOT_STARTED
- [ ] Normalize semantic attributes.
- [ ] Calculate derived cost/latency metadata when configured.
- [ ] Correlate interaction, trace, span, and evaluation IDs.
- [ ] Preserve raw extension attributes safely.

## OBS-06 Storage abstraction — STATUS: NOT_STARTED
- [ ] TelemetryStore interfaces.
- [ ] Metrics/trace/event logical separation.
- [ ] Tenant-aware reads/writes.
- [ ] Retention hooks.
- [ ] Pagination and time-window query conventions.

## OBS-07 Query API — STATUS: NOT_STARTED
- [ ] AI request listing/filtering.
- [ ] Trace detail.
- [ ] Model/provider aggregates.
- [ ] Token/cost/latency/error aggregates.
- [ ] Reliability aggregates and evaluation links.
- [ ] Stable pagination/error contracts.

## OBS-08 Native dashboard — STATUS: NOT_STARTED
- [ ] AI overview.
- [ ] LLM requests.
- [ ] Models/providers.
- [ ] Cost/tokens/latency/errors.
- [ ] Reliability view.
- [ ] Trace explorer.
- [ ] RAG and agent/tool foundations.

## OBS-09 Alerts — STATUS: NOT_STARTED
- [ ] Threshold/rate alert model.
- [ ] Reliability regression conditions.
- [ ] Delivery abstraction.
- [ ] Alert provenance and deduplication.

## OBS-10 Exporters/integrations — STATUS: NOT_STARTED
- [ ] OTEL export.
- [ ] Prometheus-compatible metrics where appropriate.
- [ ] External integration interface.
- [ ] Document enterprise observability handoff.

## OBS-11 Self-observability — STATUS: NOT_STARTED
- [ ] Collector health/throughput/drop metrics.
- [ ] Processing/query latency.
- [ ] Storage dependency health.
- [ ] Queue depth/retry/error metrics.
- [ ] Version/build metadata.

## OBS-12 Docker MVP — STATUS: NOT_STARTED
- [ ] Compose topology.
- [ ] Seed/example application.
- [ ] Document startup and validation workflow.
- [ ] End-to-end smoke test.

## OBS-13 SDK instrumentation — STATUS: NOT_STARTED
- [ ] Minimal opt-in SDK with W3C context propagation and bounded best-effort export.
- [ ] Direct verification call and an instrumented LLM/RAG example.
- [ ] Metadata-only capture and network-outage tests.

**Acceptance:** example trace and evaluation correlate without persisting raw interaction content.

## OBS-14 Cost and usage provenance — STATUS: NOT_STARTED
- [ ] Versioned price source, currency and calculation method.
- [ ] Unknown token/price data reported as unavailable, not zero.
- [ ] Aggregate accuracy tests for duplicated and late events.

## OBS-15 Optional Interaction Store — STATUS: NOT_STARTED
- [ ] Implement only after ADR-008 privacy, retention, deletion and access requirements are funded and tested.
- [ ] Keep it outside the MVP runtime dependency graph.

## OBS-16 Enterprise hardening — STATUS: NOT_STARTED
- [ ] External identity/SSO/RBAC integration, managed storage and secrets.
- [ ] Kubernetes, data residency, exporters and upgrade/migration support.
- [ ] Production load, backup/restore and security verification.

## MVP end-product expectation

From a clean checkout, a developer can start the stack, send instrumented LLM/RAG traffic, query traces and AI metrics, correlate a reliability result to a trace, and inspect requests, models, latency, tokens, cost, errors, and reliability in the native dashboard.

## Required test scenarios

1. Valid OTEL/SDK telemetry ingestion.
2. Invalid/oversized telemetry rejected safely.
3. Cross-tenant query/read attempt.
4. Collector downstream storage interruption.
5. Queue/backpressure behavior.
6. Duplicate/replayed telemetry behavior where relevant.
7. Trace/evaluation correlation.
8. Query pagination/filtering.
9. Empty/no-data dashboard states.
10. High-cardinality attribute protection strategy.
11. Retention boundary behavior.
12. Clean Docker Compose smoke test.
