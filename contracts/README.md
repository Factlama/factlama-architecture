# Canonical v0.1 contract fixtures

This directory is [EXECUTION_PLAN.md](../EXECUTION_PLAN.md)'s G0 exit evidence: JSON Schemas and examples for the wire types [CONTRACTS.md](../CONTRACTS.md) describes in prose, plus a standalone validator that checks them independently of either implementation repo's own test/CI foundation (that foundation is G1's job; G2 additionally runs this same fixture set inside each repo's own test framework).

`CONTRACTS.md` is authoritative on meaning. This directory is authoritative on exact shape. If they ever disagree, that is a bug to fix here or there, not a license to pick whichever is convenient.

## Layout

```
contracts/
  validate.py            standalone validator (no factlama-reliability/factlama-observability dependency)
  requirements.txt        its only dependency: jsonschema
  v0.1/
    schemas/
      common.schema.json                 shared $defs (Evidence, ClaimResult, Attempt, Violation, ...)
      verification_request.schema.json
      verification_result.schema.json
      judge_request.schema.json
      judge_result.schema.json
      reliability_event.schema.json
    examples/
      valid/<type>/*.json      must validate cleanly
      invalid/<type>_*.json    must be rejected (unknown major version, missing required field, forged tenant_id, invalid SUPPORTED-without-evidence, verdict+error both set)
```

## Settled in this pass

Two contract details that were previously ambiguous or inconsistent between `CONTRACTS.md`'s prose and its own worked example are now settled and encoded in the schemas:

1. **Evidence and claim-result shape.** `Evidence` carries `evidence_id` plus exactly one of `content` or `reference`. `ClaimResult` and `ContributingJudgment` both cite evidence as a plain `evidence_ids` array -- never an evidence-reference object with support/relevance scores; that kind of scoring is an internal judge-adapter concern, not a public field. A `rationale_code` vocabulary is now enumerated in `CONTRACTS.md` and `common.schema.json#/$defs/RationaleCode`.
2. **One judge attempt per claim.** `JudgeProvider.evaluate()` takes exactly one claim per call, so `provenance.attempts[]` carries one `Attempt` per claim, never one attempt spanning multiple claims. `CONTRACTS.md`'s worked example now shows two attempts for its two claims.

While building the fixtures, two more prototype-vs-contract naming gaps surfaced (`Violation.claim_id`/`evidence_id` singular vs. the contract's `claim_ids`/`evidence_ids` arrays, and lowercase vs. uppercase `severity`) -- see the note added to `factlama-reliability/CURRENT_IMPLEMENTATION.md`. Fixing the Python prototype itself is G2/G3 work, not this pass.

## Running the validator

```bash
cd contracts
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # first time only
.venv/bin/python validate.py
```

Exit code 0 iff every `examples/valid/**` fixture validates against its schema and every `examples/invalid/**` fixture is rejected. A schema or example change that breaks this must be fixed before merge -- this is the "no unresolved enum or status meaning" check G0 promises.
