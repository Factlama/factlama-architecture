# Privacy Architecture

FactLama must support organizations that cannot persist raw AI interaction content.

## Capture modes
- `NONE` — no interaction content; operational metadata only.
- `METADATA_ONLY` — telemetry and reliability metadata without raw prompt/response/evidence bodies.
- `REDACTED` — configured content is persisted only after redaction.
- `FULL` — explicit opt-in full interaction capture subject to retention/security policy.

## Privacy principles
1. Raw content persistence is never required for core observability.
2. Redaction happens before persistence, not only at presentation time.
3. Retention is configurable by data class and tenant.
4. Deletion/export workflows must be architecture-compatible even if implemented later.
5. Provider credentials, secrets, tokens, and authentication material are never captured as interaction content.
6. Interaction storage is logically separated from telemetry storage.
7. Data residency and customer-managed storage are future-compatible requirements.

## Interaction Store

The future Interaction Store may persist prompts, responses, evidence, tool calls/results, judge outputs, and decisions for replay/regression workflows. It is not an MVP dependency and must be explicitly enabled.

## Required metadata without raw content

FactLama should still retain, subject to tenant policy: correlation IDs, timestamps, model/provider/version, evaluator/version, prompt version identifier, token counts, latency, cost, reliability scores, verdict, violations, policy decision, and hashes/references where useful.
