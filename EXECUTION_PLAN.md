# Cross-repository execution plan

This is the **build order and integration gate** for the three initial repositories. It is a target plan, not an assertion that code exists. [ROADMAP.md](ROADMAP.md) owns EPIC status; the Reliability and Observability `docs/implementation.md` files own REL/OBS task status. All implementation statuses remain `NOT_STARTED` until their own acceptance tests pass. [CONTRACTS.md](CONTRACTS.md) and ADR-001–015 are the architecture baseline. Implement a thin, tested vertical slice at each gate; avoid creating every future module up front.

ADR acceptance and the document contract are complete, but **G0 is not closed**: executable canonical fixtures and cross-repo compatibility tests still need implementation. No gate is marked complete by this plan.

The implementation-repo low-level checklists predate ADR-010–015. G0 includes updating Reliability's `domain-model.md`, `judge-provider.md`, `scoring.md`, `verification-pipeline.md`, `LOW_LEVEL_IMPLEMENTATION.md`, plus new `evaluator-agreement-harness.md` and `evaluator-registry.md`; Observability must update `telemetry-model.md`, `storage-query.md`, `dashboard.md` and `LOW_LEVEL_IMPLEMENTATION.md`. Those edits belong in their owning repos and are prerequisites for coding against this version of the shared contract.

## Dependency graph

```text
G0 architecture contract/fixture freeze (documentation gate)
  -> G1 repository/CI foundation
  -> G2 trusted tenancy + executable contracts
       ├─> G3 first T0 groundedness slice -> G4 evaluator agreement/qualification -> G5 async/content hardening
       └─> G6 observability ingress/store/query foundation ------------------------┘
                                                        G5 + G6 -> G7 SDK/correlation
                                                        G6 + G7 -> G8 dashboard
                                                   G4 + G5 + G7 + G8 -> G9 local MVP
                                                   G4 + G5 -> G10 evaluator ecosystem (post-MVP)
```

The observability lane may progress in parallel with Reliability after G2. G7 cannot be closed until a real Reliability result is linked to a persisted trace. G8 can start with fixtures but cannot close on mocked data alone. G10 is a deliberate ecosystem gate, not a prerequisite for the one-T0-judge MVP. `G9` is the only MVP completion gate.

## Gate-by-gate work and exit tests

| Gate | Dependencies and owners | Deliverables | Exit evidence |
|---|---|---|---|
| **G0: contract freeze** | Architecture plus Reliability/Observability contract owners; accepted ADR-010–015 | v0.1 types for calibration class, attempts/usage, contributing judgments, `DISPUTED`, budget and injection codes; reconcile owning low-level docs; canonical JSON fixtures and compatibility rules | JSON schemas/examples validate; both implementation repos pass the same versioned fixture suite; no unresolved enum or status meaning |
| **G1: engineering foundation** | G0; EPIC-01, REL-01, OBS-01 | Python package/service layouts, TS dashboard scaffold, config, migrations, lint/type/test/CI, dependency rules | Fresh checkout installs/builds/tests; CI rejects domain-to-vendor imports; no empty placeholder test is counted |
| **G2: trusted tenancy + executable contracts** | G1; EPIC-02/03, REL-02/03, OBS-02/03 | Authenticated tenant/project/application context at API/collector/worker boundaries; typed request/result/event models; per-tenant persistence and cursor keys | Worked request/result/event round-trip in both repos; forged tenant fields, cross-tenant IDs/jobs/cursors and unknown schema major fail safely; metadata-only mode persists no raw content |
| **G3: first factual vertical slice** | G2; EPIC-04/08, REL-04–09/12 | Explicit claims and supplied evidence first; one T0 working judge adapter; one-claim-per-call; structural evidence isolation; response validation; claim findings; deterministic scores/verdict and advisory policy; sync API; pre-dispatch claim/evidence/token/cost caps | Golden supported/contradicted/unsupported/insufficient fixtures pass; `SUPPORTED` without cited evidence is invalid; injection fixture cannot silently become PASS; timeout/budget exhaustion/no compliant provider abstain; judge cost/attempt is recorded; no default judge yet until G4 |
| **G4: first evaluator qualification** | G3; EPIC-04b, REL-15 harness subset, minimal ADR-014 registry | Public development and held-out fixture sets, conformance runner, agreement report, calibration-class derivation, registry state through tenant approval, pinned model/config | One command produces versioned conformance/agreement report for T0; report includes per-label quality, adversarial cases, latency and cost; provider cannot become tenant default without `QUALIFIED` plus tenant approval; changed model/config creates a new class |
| **G5: durable Reliability** | G4; EPIC-05/06, REL-10/11/12 | Async submit/status/cancel, PostgreSQL jobs/outbox, idempotency, bounded retries/fallback, capture/redaction/retention, revocation checks and sanitized result reads | Same key/body returns same job, conflicting body 409; duplicate worker/event yields one logical result; failed attempts remain in `attempts[]`; disagreement yields `DISPUTED`, not silent majority vote; raw content absent in metadata-only DB/queues/logs |
| **G6: Observability core** | G2; EPIC-09, OBS-04–07/11/14 | Authenticated OTLP/HTTP and ReliabilityEvent ingress, normalization/redaction, PostgreSQL span/event/link storage, dedup/reconciliation, query routes, generation and judge usage/cost provenance | Late event joins trace; duplicate event does not double-count; cross-tenant query returns no data; cost unknown stays unavailable; score aggregates group by calibration class; storage outage returns bounded failure and readiness changes |
| **G7: SDK and correlation** | G5 + G6; EPIC-11, OBS-13 | Python `verify`/async client and explicit LLM/retrieval/tool spans, W3C context, bounded best-effort export, sample app | Sample app emits one interaction/trace linked to one evaluation; SDK outage does not fail generation; prompts/evidence/credentials absent from default telemetry; direct and async API examples pass |
| **G8: dashboard** | G6 + G7; EPIC-10, OBS-08 | Overview, Requests/Trace, Reliability and Models views, URL filters, freshness/count/units, calibration and verification-cost views, inert rationale rendering | Reviewer navigates request → trace → evaluation/claim; `NOT_EVALUATED`, `PENDING`, `ABSTAINED`, `DISPUTED`, failed and unavailable are distinct; mixed classes/currencies are labeled; no cross-tenant leakage or unsafe rationale HTML |
| **G9: local MVP release gate** | G4–G8; EPIC-01–06/08–11, OBS-12 | Compose with migrations, sample tenant/app/provider, documented configuration and end-to-end smoke test | Fresh checkout runs the full [MVP validation](VALIDATION.md) with security, contract, golden, async, failure, privacy and dashboard tests; performance baseline recorded; all required owning tasks genuinely COMPLETE |
| **G10: open evaluator ecosystem** | G4 + G5; EPIC-07, REL-13 | Full registry lifecycle/audit, T1 signed/reviewed gate, T2 HTTP wire endpoint through mTLS/egress proxy, compliance-constrained primary/fallback, per-provider bulkheads/circuit breakers, scheduled agreement canary | T2 code never runs in-process; SSRF and secret-scope tests pass; revoked provider cannot dispatch or remain fallback; no compliant judge gives abstention + human review; drifting/aliased model loses default eligibility; two adapters pass same contract/conformance suite |

**First coding task:** G1's smallest foundation slice, followed immediately by G2's shared request/result/event fixture and tenant boundary. Do not begin SLM training, dashboard charts or a T2 extension point as the first implementation. Within G3, start with explicit claims and supplied evidence; add extraction once the direct path passes. The first production-like demonstration is the G3 sync API result, then the G7 trace correlation, then the G9 local stack.

## Cross-repository handoffs

| Producer → consumer | Contract and owning test | Failure behavior |
|---|---|---|
| Reliability API/worker → SDK client | `VerificationRequest/Result`, jobs, error shape; shared fixture in both repos | SDK distinguishes factual abstention, dispute and transport error |
| Reliability outbox → Observability ingress | `ReliabilityEvent` with stable event ID, calibration class and usage; at-least-once integration test | Delivery retries; duplicate does not double-count; trace remains visible if event delayed |
| SDK → Collector | W3C context and OTLP/HTTP spans; metadata-only fixture | Export is bounded/fail-open for customer inference; collector rejects bad auth/limits |
| Collector → Query API | Tenant-keyed spans/events/link projection and pricing provenance | Missing evaluation/cost is pending/unavailable, never PASS/zero |
| Query API → Dashboard | Versioned list/detail/aggregate envelopes and delegated sanitized Reliability detail | Empty, delayed, unavailable, denied and failed states are rendered separately |

Every handoff needs a producer fixture, a consumer contract test and one cross-repo integration test against compatible revisions. The architecture repo owns the fixture schema and compatibility policy; implementation repos own executable tests. A change to verdict, event, score or tenant semantics requires an ADR and coordinated release.

## Qualification and registry gates

The **first T0 adapter** may be used in development while `PROVISIONAL`, but cannot be selected as a tenant's default judge until G4 publishes its agreement report, assigns `QUALIFIED`, pins its model/configuration and records tenant approval. The report must state dataset versions, held-out isolation, per-class confusion matrix/precision/recall/F1, calibration if a probability is claimed, adversarial-evidence outcomes, latency, tokens and cost. A class-specific score is not pooled with another class. The harness is a runner/report, not a human certification bureaucracy; a tenant may explicitly choose an unqualified judge for nondefault use with that status visible.

The **customer-judge gate** is G10. T2 customer adapters are HTTP-only and out of process. Registry transitions are audited: `REGISTERED -> CONFORMANCE_PASSED -> AGREEMENT_REPORTED -> TENANT_APPROVED -> DEPRECATED|REVOKED`. Selection checks tenant approval, pinned model, qualification for default use, hosting/data-processing constraints, budget and breaker state on both primary and fallback. Revocation blocks new dispatch immediately and is rechecked before result commit; cancellation of an already-running external call is best effort and recorded. A compliant provider absence yields `ABSTAINED/ABSTAIN` plus `HUMAN_REVIEW`.

## Explicitly deferred after MVP

EPIC-12's FactLama SLM uses G4's provider-neutral harness and must pass the same qualification gate. EPIC-13 Interaction Store/replay enables cross-version re-evaluation only for tenants that opted into sufficient content retention. EPIC-14 covers enterprise SSO/Kubernetes/storage residency; judge-egress compliance is already enforced at G10. Multi-judge ensembles, majority voting and automatic reconciliation stay deferred under ADR-015; the contract can represent attempts and `DISPUTED` without implementing ensembles. Mode profiles permit one judgment per claim in MVP; a later ADR must define ensemble behavior. All these tasks remain `NOT_STARTED` until separately implemented and tested.
