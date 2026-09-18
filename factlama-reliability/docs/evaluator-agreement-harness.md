# Evaluator agreement and qualification harness (G4)

ADR-010: an evaluator's `qualification_status` is `QUALIFIED` only after a published agreement report against the golden evaluation set. This file defines that set, the runner, and the report schema. It does not define the registry that stores the resulting status -- see [evaluator-registry.md](evaluator-registry.md).

## Fixture sets

Two disjoint sets, versioned together as one dataset release (`dataset_version`, e.g. `harness-0.1`):

- **Public development set.** Checked into this repo (`tests/fixtures/agreement/dev/`). A provider author may self-test against it before submitting for qualification. Its answers are known and must never be reused as held-out.
- **FactLama-held-out set.** Not checked into a public repo path a provider author can read before submission -- kept outside `factlama-reliability`'s own tree (a private fixture store, path TBD at implementation time) so self-testing cannot become answer-key memorization. The report's `dataset_version` and a content hash of the held-out set are recorded so a later dataset change is detectable, not silently reused.

Both sets share the same fixture shape: a claim, its candidate evidence, and a hand-reviewed expected `ClaimVerdict` label, grouped into families:

| Family | What it exercises |
|---|---|
| Direct support | Claim text restated near-verbatim in evidence |
| Paraphrased support | Semantic match, low lexical overlap |
| Numerical/temporal contradiction | ADR-013-adjacent: values disagree, wording otherwise similar |
| Negation contradiction | Same entities, opposite polarity |
| Irrelevant evidence | High lexical overlap, no actual support (a "confident but wrong" trap) |
| Insufficient evidence | Evidence present but genuinely inconclusive |
| Adversarial/injection | Evidence containing judge-directive-style language (ADR-013); expected label is unaffected by the injected text |
| Ambiguous | Reasonable evaluators could disagree; used for calibration, not pass/fail scoring |

Leakage control: the held-out set's claims/evidence must not be paraphrases of dev-set items close enough that passing dev implies passing held-out. A dataset reviewer (human, not the harness itself) attests to this per release; the harness cannot verify it mechanically.

## Conformance vs. agreement

Two distinct checks, run in order:

1. **Conformance** (ADR-014's first lifecycle transition, `REGISTERED -> CONFORMANCE_PASSED`): the existing success/ambiguity/timeout/rate-limit/malformed-response fixture suite (REL-13's acceptance bar) against the `JudgeProvider` port itself -- does the adapter return well-formed `JudgeResult`s and typed errors under the documented failure modes. This is a pass/fail gate, not a quality measurement.
2. **Agreement** (`CONFORMANCE_PASSED -> AGREEMENT_REPORTED`): only a provider that already passed conformance runs against the dev + held-out fixture families above, scored against the hand-reviewed labels.

## Report schema

One JSON report per `(provider_id, pinned_model_id, configuration_version, dataset_version)` tuple -- the same tuple `derive_calibration_class()` already hashes, so a report is addressable by calibration class:

```json
{
  "report_version": "0.1",
  "calibration_class": "<derive_calibration_class(...) output>",
  "provider_id": "...",
  "pinned_model_id": "...",
  "configuration_version": "...",
  "dataset_version": "harness-0.1",
  "generated_at": "<RFC3339>",
  "per_label": {
    "SUPPORTED": {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0},
    "CONTRADICTED": {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0},
    "UNSUPPORTED": {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0},
    "INSUFFICIENT_EVIDENCE": {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n": 0}
  },
  "adversarial": {"total": 0, "flipped_to_supported": 0, "flagged_injection_suspected": 0},
  "calibration": {"claimed_probability_supported": null},
  "latency_ms": {"p50": 0.0, "p95": 0.0},
  "usage": {"total_tokens": null, "cost": {"status": "UNAVAILABLE"}}
}
```

A per-label metric is never pooled across labels into one aggregate accuracy number -- ADR-010: "a class-specific score is not pooled with another class." `calibration.claimed_probability_supported` is `null` unless the provider actually emits a calibrated probability (most do not); a `null` here is not filled with a guess. `adversarial.flipped_to_supported` must be `0` for a report to be eligible for `QUALIFIED` -- any nonzero value is an automatic disqualification, not a lower score, per ADR-013's "injection fixture cannot silently become PASS."

## Runner

One command produces one report for one calibration class: given a `JudgeProvider` instance, its pinned model/config identifiers, and a dataset version, run conformance, then (only if conformance passes) agreement, and write the JSON report above. The runner is a script in `factlama-reliability` (e.g. `scripts/run_agreement_harness.py`), not a service -- G4's exit evidence is "one command produces a versioned report," not a running system. It must not itself decide `qualification_status`; it only produces the report `evaluator-registry.md`'s transition rule reads.

## What this file does not define

Registry state transitions, tenant approval, and default-judge eligibility are [evaluator-registry.md](evaluator-registry.md)'s job. This file only produces the report that registry consumes.
