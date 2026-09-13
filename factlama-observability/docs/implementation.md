# Observability Implementation Plan

For concrete SDK, collector, processing, storage/query, dashboard and acceptance behavior, use [LOW_LEVEL_IMPLEMENTATION.md](LOW_LEVEL_IMPLEMENTATION.md). This file owns task status; a task is not complete solely because it appears in the specification.

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

A task is COMPLETE only when code, tests, failure handling, tenant isolation, telemetry, documentation, and acceptance criteria are satisfied.

## OBS-01 Foundation — STATUS: COMPLETE
- [x] Establish source/test/example layouts. `sdk/`, `collector/{ingress,processing}/`, `storage/`, `query/`, `operations/` Python packages plus a `dashboard/` Vite+React+TypeScript scaffold and an `examples/` placeholder (real examples wait on OBS-13/OBS-07).
- [x] Add configuration, health, logging, lint/type/test foundations. `operations/{config,health,logging_config}.py` (22 tests, 100% coverage); dashboard has `npm run lint/typecheck/test/build`, all passing with 0 audited vulnerabilities.
- [x] Define API/event/schema versioning. `operations/versioning.py`'s `check_schema_version()` enforces the same major-reject/minor-accept rule the [`contracts/v0.1/`](../../contracts/README.md) schemas already enforce for Reliability; nothing in this repository emits or accepts a real payload yet, so no wire type uses it beyond its own tests.
- [x] Define module dependency boundaries. `import-linter` (3 forbidden contracts, all `KEPT`): `sdk` cannot depend on `collector`/`storage`/`query`; `storage` cannot depend on `collector`/`query`/`sdk`; `query` cannot depend on `collector`/`sdk`.

Storage migrations exist only as Alembic wiring (`storage/migrations/`, zero revisions, verified as a no-op against SQLite) -- that is this task's full scope; the actual `spans`/`reliability_events`/`evaluation_links` schema is OBS-06, not re-scoped here. `operations/config.py`'s env helpers have no caller yet (first real one is OBS-04/OBS-07) -- foundation only, by design, not a configured service.

`.github/workflows/ci.yml` (Python 3.10-3.12 matrix: ruff/mypy/import-linter/pytest/alembic smoke test; Node 24: eslint/tsc/vitest/build) ran green on GitHub Actions from a clean checkout on first push (run [34756423331](https://github.com/Factlama/factlama-observability/actions/runs/34756423331), all 4 jobs passed).

**Acceptance:** clean checkout builds/tests; module dependency rules are documented and enforceable. Confirmed by an actual GitHub Actions run against a clean checkout, not merely reproduced locally. Marked COMPLETE for OBS-01's own scope; this does not make OBS-02 and later any less `NOT_STARTED`.

## OBS-02 Tenant-aware ingestion — STATUS: NOT_STARTED
- [ ] Tenant/project/application context.
- [ ] Validate tenant context at ingress.
- [ ] Cross-tenant isolation tests.
- [ ] Bounded payload validation.
- [ ] Non-blocking/best-effort SDK behavior.

## OBS-03 AI telemetry model — STATUS: NOT_STARTED
- [ ] Trace/span/event/resource model.
- [ ] Model/provider/version attributes.
- [ ] Token/cost/latency/error attributes.
- [ ] Retrieval/tool-call events.
- [ ] Reliability correlation attributes.
- [ ] Prompt/evaluator/policy version references.

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
