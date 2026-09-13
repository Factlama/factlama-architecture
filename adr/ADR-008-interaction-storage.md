# ADR-008: Optional Interaction Store

Status: Accepted (design only; implementation deferred)

Decision: Telemetry and reliability metadata remain usable without persisting raw prompts, answers, evidence, tool payloads or judge outputs. A future `InteractionStore` is a separate, tenant-scoped port with per-data-class capture controls, pre-write redaction, encryption, retention/deletion and audit access. `NONE` and `METADATA_ONLY` never write raw content. `REDACTED` writes only after configured redaction. `FULL` requires explicit tenant opt-in and authorized access. A reference in a telemetry or verification record does not imply content is stored.

Rationale: Some organizations need replay and investigations; others cannot retain content. Coupling content to telemetry would exclude the latter and enlarge the default security boundary.

Consequences: Replay and production-to-dataset conversion are deferred. Interfaces and IDs must permit later linkage, while MVP deployment must not require an Interaction Store. Retention and deletion must cover replicas, indexes and derived datasets when implemented.
