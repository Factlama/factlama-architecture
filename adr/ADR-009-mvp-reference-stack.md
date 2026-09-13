# ADR-009: MVP reference stack

Status: Accepted implementation baseline

Decision: use Python for the first SDK and Reliability/Observability services, TypeScript for the native browser dashboard, PostgreSQL for tenant-scoped metadata, and a PostgreSQL job/outbox pattern for async work. Use maintained OpenTelemetry libraries and OTLP/HTTP transport. The source-of-truth wire contract remains language and backend independent.

Rationale: this gives the MVP a concrete build and test path with one operational database while preserving ports for later alternatives. A single DB-backed queue is adequate until measured evaluation/ingestion load says otherwise.

Consequences: migrations, indexing, queue leases, backup/restore and retention jobs must be implemented and tested. A later stack change requires a replacement ADR and updated low-level specs. No implementation is claimed by this decision.
