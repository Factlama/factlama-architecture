# Evaluator registry (G4/G10)

ADR-014's control-plane object for judge providers. G4 implements the state machine and the minimal in-repo entry needed to gate default-judge selection; the full audited, persisted, multi-tier version (T1 signed/reviewed, T2 HTTP-only customer adapters, revocation propagation to in-flight evaluations) is G10's -- see EXECUTION_PLAN.md's gate-mapping note. This file specifies the shape both gates share so G10 extends it rather than replacing it.

## Lifecycle

```text
REGISTERED -> CONFORMANCE_PASSED -> AGREEMENT_REPORTED -> TENANT_APPROVED -> {DEPRECATED, REVOKED}
```

- `REGISTERED`: a `(provider_id, pinned_model_id, configuration_version)` tuple exists in the registry. Pinning is required -- a floating alias is never permitted for a tenant's default judge (ADR-014).
- `CONFORMANCE_PASSED`: the provider's adapter passed [evaluator-agreement-harness.md](evaluator-agreement-harness.md)'s conformance suite. A pass/fail gate, not a quality measurement.
- `AGREEMENT_REPORTED`: a versioned agreement report (same file, report schema) exists for this exact tuple plus a `dataset_version`. Reaching this state sets `qualification_status=QUALIFIED` *only if* the report's adversarial section shows zero flips to `SUPPORTED`; otherwise the transition is refused and the entry stays `CONFORMANCE_PASSED`.
- `TENANT_APPROVED`: a tenant has explicitly approved this exact calibration class for use. Approval is per tenant, not global -- one tenant approving a provider does not approve it for another.
- `DEPRECATED` / `REVOKED`: terminal states. `DEPRECATED` is a voluntary sunset (new dispatch discouraged, existing approvals honored until a stated date); `REVOKED` blocks new dispatch immediately and is rechecked before result commit (G5, once there is a result-commit step to recheck against). Both propagate to any policy naming the provider as fallback.

Every transition is audited: who/what triggered it, when, and the report or approval record it cites. G4's own scope stores this as a typed in-repo record (below); G10 replaces the storage, not the state machine.

## Default-judge eligibility

A provider/configuration may be used non-default (development, explicit tenant opt-in with status visible) at any lifecycle state from `REGISTERED` onward -- ADR-010: "any judge must not become any judge we've certified." It may be selected as a **tenant's default judge** only when all of:

1. State is `TENANT_APPROVED` (implies `AGREEMENT_REPORTED` implies `QUALIFIED`).
2. The model identifier is pinned, not a floating alias.
3. The tenant's policy compliance constraints (`hosting_region`, `data_processing_terms_ref`, `trains_on_submitted_data`, `retention_at_provider`, `subprocessors`, `certifications[]` -- ADR-014) are satisfied by this registry entry's declared attributes.

No compliant default-eligible provider yields `ABSTAIN` plus `HUMAN_REVIEW` -- never a silent non-compliant call (ADR-014), the same fail-closed rule `core.compliance`'s baseline `NO_COMPLIANT_PROVIDER` check already applies at G3 for a narrower, static tag comparison. This file's eligibility check is that same rule's successor once qualification/tenant-approval data exists to check against, not a separate mechanism.

## G4's own minimal scope

G4 does not build G10's persisted, audited registry. It builds:

- A typed `QualificationRecord` (provider/model/config tuple, lifecycle state, report reference, tenant-approval set) and a pure state-transition function enforcing the rule order above -- no illegal transition (e.g. `REGISTERED -> TENANT_APPROVED` skipping conformance/agreement) is representable.
- An eligibility check, `is_default_eligible(record, tenant_id) -> bool`, implementing the three conditions above.
- No wiring into `Verifier`'s dispatch path yet: there is no concept of "a tenant's configured default provider" anywhere in this codebase today (the `Verifier` is constructed with one `model_provider` directly), and inventing tenant-scoped provider selection is G5/G10 territory (it needs persistence to store which provider a tenant selected). Building the eligibility *rule* now, unwired, avoids redoing the state machine later while not pretending selection infrastructure exists.
- Every current T0 adapter (Mock, RuleBased, Embedding, NLI) starts and stays `REGISTERED` (or, once a real report exists, whatever state its own report earns) -- none is granted `QUALIFIED` by fiat. "Passing implementation tests does not establish evaluator accuracy": a green `pytest` run proves the adapter's *code* behaves as its own tests expect, never that its *judgments* agree with a held-out label set. Only a real agreement report can move a class past `CONFORMANCE_PASSED`.

## Re-scoring and drift

A provider-side model change (detected by ADR-014's periodic agreement-drift canary, G10) is a new calibration class, never a silent mutation of an existing one's status. Re-scoring against a changed provider/configuration creates a new `evaluation_id` with a `supersedes` link (`VerificationResult.supersedes`, already typed, unset until G5's retry/re-evaluation machinery exists to set it) -- historical results are never mutated in place.
