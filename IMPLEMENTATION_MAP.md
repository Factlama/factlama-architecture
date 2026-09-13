# What the MVP implements

This is the reviewer’s one-page map. It describes target code, not completed work. Each row links to the implementation specification and an observable check. The [shared contract](CONTRACTS.md) owns external field semantics; the local specs own code responsibilities.

| Component | Implement in MVP | Observable check |
|---|---|---|
| Reliability API | Authenticated sync verification, async submit/status/cancel, result read, stable errors | Submit the worked request and inspect the result/job through HTTP |
| Reliability core | Request validation, atomic claim segmentation, supplied-evidence mapping, provider adapter, normalized findings, deterministic scores/verdict, policy decision, provenance | Supported, unsupported, contradicted, ambiguous and provider-error fixtures produce specified results |
| Reliability worker | Durable jobs, idempotency, retry/lease/terminal state, result and outbox event | Repeated submit/delivery creates one logical evaluation; event eventually arrives |
| Evaluator agreement harness | Public dev and held-out fixtures, conformance/agreement report, calibration class | First T0 judge has a reproducible report before default routing |
| Evaluator registry | Pinned model/config, qualification/tenant approval, audited lifecycle, compliance-constrained selection | Unqualified, revoked or noncompliant judge cannot become default/fallback; T2 customer code is out of process |
| Python SDK | Explicit `verify`, context-managed LLM/retrieval/tool spans, W3C context, bounded best-effort export, metadata-only default | Instrumented example yields trace and linked evaluation; outage does not fail app |
| Collector | OTLP/HTTP trace ingress, authentication/scope validation, content filtering, normalization, bounded processing, reliability-event ingestion | Bad tenant/content is rejected; accepted spans survive restart and appear in query |
| Observability storage/query | Tenant-keyed spans/events/projections, reconciliation, time-window queries, pagination, aggregates, cost provenance | Late/duplicate events do not double count; cross-tenant query reveals nothing |
| Dashboard | Overview, Requests/Trace, Reliability and Models views, filters, explicit no-data/pending/error states | Reviewer can navigate from request to trace to claim result and explain each metric |
| Local stack | Compose services, persistent DB, migrations, sample app/tenant, smoke test | Fresh checkout runs a complete trace/evaluation/dashboard path |

Use [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for the dependency order and cross-repo exit tests. Existing component checklists are [Reliability](https://github.com/Factlama/factlama-reliability/blob/main/docs/LOW_LEVEL_IMPLEMENTATION.md) and [Observability](https://github.com/Factlama/factlama-observability/blob/main/docs/LOW_LEVEL_IMPLEMENTATION.md); they must be brought into alignment with ADR-010–015 as the owning implementation tasks start. Deferred features (own SLM, vector retrieval, interaction replay, enterprise SSO/Kubernetes, multi-judge ensembles) stay on the roadmap and are not part of this MVP acceptance path.

## Reference implementation decisions

The documentation assumes one Python SDK, Python Reliability/ingestion services, a TypeScript browser dashboard, PostgreSQL for MVP metadata, and a PostgreSQL-backed job/outbox queue. These are implementation baselines to make the checklist testable, not public contract requirements. Replace one through an ADR that names the migration and preserves behavior. Use maintained OpenTelemetry libraries for OTLP/W3C propagation rather than a custom trace protocol. Do not create empty folders merely to match a diagram.
