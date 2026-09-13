# Repository Strategy

## Decision

FactLama starts with three repositories:

1. `factlama-architecture` — system-level source of truth
2. `factlama-reliability` — reliability/evaluation engine
3. `factlama-observability` — telemetry, query, dashboard, alerts, integrations

## Why not more repositories now

Splitting API, schemas, SDK, collector, dashboard, ingestion, evaluation, deployment, and docs into separate repositories would create premature release/versioning overhead, cross-repository coordination, duplicated CI/security policy, and contract drift before module boundaries are stable.

## Split criteria

A module becomes a separate repository only when at least one of these is true:
- independent release/version lifecycle is required;
- separate ownership and deployment lifecycle is stable;
- dependency boundaries are mature and enforced;
- consumers need the component independently;
- security/compliance isolation requires it;
- repository size/build performance creates measurable friction.

## Future candidates

- `factlama-models` when model artifacts/runtime have an independent lifecycle.
- `factlama-benchmarks` when benchmark datasets/harness/results need independent governance and releases.
- `factlama-schemas` only if contracts are consumed independently across languages and need dedicated versioning.

## Ownership rule

Architecture owns cross-repository contracts and the `factlama-reliability/` and `factlama-observability/` documentation folders, including their task ledgers. Implementation repositories contain source, tests, examples, a short README, and `CLAUDE.md`/`CODEX.md` entrypoints (with `AGENTS.md` for Codex discovery). They may propose ADRs but must not silently redefine system boundaries. A code change that affects documented behavior updates the corresponding architecture-owned component docs in the same review cycle.
