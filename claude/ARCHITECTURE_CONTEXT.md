# Architecture context

Read `EXECUTION_PLAN.md`, `SYSTEM_ARCHITECTURE.md`, `CONTRACTS.md`, `DECISION_REGISTER.md`, `SECURITY_MODEL.md`, `OPERATIONS.md` and the relevant implementation repository docs before changing code. FactLama has three initial repositories: architecture owns shared contracts and decisions, reliability owns factual evaluation, and observability owns ingestion/query/dashboard. The SLM is an optional judge under the provider-neutral ADR-010 qualification gate; supplied evidence is the MVP path. The Interaction Store and multi-judge ensembles are deferred.
