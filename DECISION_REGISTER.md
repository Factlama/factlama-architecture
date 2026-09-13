# Decision register and source of truth

The numbered files in `adr/` are authoritative; summary prose elsewhere is descriptive. Current accepted decisions:

| ADR | Decision |
|---|---|
| 001 | Three initial repository boundaries |
| 002 | Reliability Engine as a first-class component |
| 003 | OpenTelemetry-first interoperability |
| 004 | JudgeProvider abstraction |
| 005 | Evidence abstraction; supplied evidence first |
| 006 | Optional, benchmark-gated FactLama SLM |
| 007 | Native AI dashboard through query APIs |
| 008 | Optional Interaction Store, deferred from MVP |
| 009 | MVP reference implementation stack (Python, TypeScript, PostgreSQL, OTLP/HTTP) |

Proposed decisions, arising from the [any-judge architecture review](ANY_JUDGE_ARCHITECTURE_REVIEW.md) and pending acceptance:

| ADR | Decision |
|---|---|
| 010 | Evaluator qualification and calibration classes; supersedes the SLM-only benchmark gate in 006 |
| 011 | Judge adapter trust tiers (T0/T1/T2); customer judges run out-of-process only |
| 012 | Verification budgets, fan-out caps, and bring-your-own-key as the default economic model |
| 013 | Evidence treated as adversarial input at the judge boundary |
| 014 | Evaluator registry lifecycle, model pinning, and compliance-constrained provider selection |
| 015 | Multi-judge reconciliation deferred, but provenance/finding shapes provisioned in v0.1 |

Architecture owns [cross-repository contracts](CONTRACTS.md), repository boundaries and MVP gates. Reliability owns detailed evaluator, scoring and policy behavior; Observability owns telemetry, collector, query and dashboard behavior. A change to a shared field, verdict meaning, tenant boundary or correlation key requires an architecture ADR and coordinated compatibility tests. A local implementation detail requires a local ADR only when it changes a stable dependency or operational boundary.

Status tracking has one source per level: [ROADMAP.md](ROADMAP.md) owns EPIC-01–14; `factlama-reliability/docs/implementation.md` owns REL-01–15; `factlama-observability/docs/implementation.md` owns OBS-01–16. README summaries are navigation, not separate task ledgers. All remain `NOT_STARTED` until code and acceptance checks exist.
