# ADR-016: Centralize Component Documentation

Status: Accepted

Decision: `factlama-architecture` owns `factlama-reliability/` and `factlama-observability/` documentation folders. Each contains the moved component README, detailed specs and task ledger. Implementation repositories keep code, tests, examples, a short package README, `CLAUDE.md`, `CODEX.md`, and `AGENTS.md` for Codex discovery. Agent entrypoints direct readers to the sibling architecture checkout or its GitHub URL.

Rationale: Architecture decisions, shared contracts and component plans can be reviewed together while implementation repositories remain focused on code. This avoids duplicate task ledgers and conflicting copies of the same specification.

Consequences: A change to component behavior or task status updates the architecture repository in the same review cycle as implementation. A standalone implementation checkout needs the architecture repo or network access to read detailed docs. The short implementation README remains for package metadata and onboarding; no runtime import or build path may depend on a sibling checkout.
