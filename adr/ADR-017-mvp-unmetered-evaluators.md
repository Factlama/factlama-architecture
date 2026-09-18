# ADR-017: Local Unmetered Evaluators for MVP; Hard Spending Limits Post-MVP

Status: Accepted

Date: 2026-09-18

Supersedes: ADR-012's delivery timing for hard per-request and per-tenant-window token/cost enforcement. Other ADR-012 requirements remain applicable.

## Decision

The MVP supports only local, unmetered evaluators. T0 is a trust classification, not an exemption from this restriction: a metered T0 adapter is also outside MVP scope. Local evaluation still consumes compute; unmetered does not mean free operation or zero measured cost.

G3 retains pre-dispatch claim/evidence limits, payload limits, execution safeguards, normalized abstention and available usage recording. G5 retains durable jobs, bounded retries/fallback, deadlines, cancellation, and preservation of every attempt's available usage. G9 must demonstrate that metered dispatch is unavailable in the supported MVP configuration. These are acceptance requirements, not assertions that all safeguards are already implemented.

Hard per-request and tenant-window token/cost enforcement moves to the post-MVP REL-13/EPIC-07 workstream, before enabling the first metered adapter. This prerequisite applies regardless of which gate or trust tier introduces that adapter. Qualification alone does not authorize metered dispatch.

Current fixed reservations are estimates, not verified worst-case bounds or hard spending guarantees. Post-call checks can stop later calls but cannot prevent overspending by the call already in progress. Unknown usage/cost must remain explicit. This scope decision does not defer accounting correctness: preserve known subtotals per currency, identify missing usage, and never hide a known USD overrun because another attempt reports a different currency.

## Post-MVP implementation

1. Define a versioned JudgeRequest/JudgeProvider extension for input estimation, maximum output tokens, enforceable provider limits, and reservation identity. Update prose contracts, executable schemas, fixtures, adapters and compatibility tests together before enabling metered dispatch. This ADR does not add fields to v0.1 today.
2. Estimate input tokens from the actual rendered request, including instructions, claims and evidence. Reserve a defensible upper bound for input plus capped output using pinned provider/model pricing, currency and pricing version. Include other billable units if the provider charges for them. Reject dispatch when the bound cannot be established under a hard-budget policy.
3. Atomically reserve against both the request and the durable tenant-window allowance before every attempt, including retries and fallback. Concurrent workers must not reserve the same remaining allowance twice.
4. Pass limits the provider actually honors. A provider without enforceable bounds, or without usable pricing for a hard monetary ceiling, cannot be selected under that policy. Cancellation alone is not a monetary cap.
5. Reconcile actual usage after success or failure and release unused reservations. Keep uncertain charges reserved until reconciled or conservatively accounted for; a timeout must not release funds that may already have been spent. Persist reservations and recovery state across restarts without double charging retries.
6. Report usage by currency, unknown-attempt counts and reservation outcomes. Never infer free execution from missing usage. Keep BYO-key ownership and credential isolation from ADR-012.

## Acceptance tests before metered enablement

- An over-budget first request is rejected before any provider call.
- Near-limit requests respect the enforceable per-call cap and cannot exceed the reserved bound.
- Missing pricing or an adapter that cannot enforce required limits prevents dispatch.
- Concurrent requests, retries, fallback and worker restarts cannot oversubscribe tenant/request budgets or double count reservations.
- Failures retain billed usage; uncertain charges are not prematurely released.
- Known USD spending remains enforceable alongside other currencies; missing usage is visible and mixed token-reporting formats accumulate correctly.
- Successful reconciliation releases unused capacity and preserves pricing/model provenance.
- A real metered adapter demonstrates the provider-limit behavior; mock-only tests do not establish the hard-cap guarantee.

## Consequences

MVP delivery does not depend on building a metered provider integration. The platform must describe its current budget protection accurately. Enabling any paid judge service requires the above implementation and tests first. This decision changes scope and acceptance criteria; it does not mark G3, G5, G9 or REL-13 complete and does not waive unrelated outstanding findings.
