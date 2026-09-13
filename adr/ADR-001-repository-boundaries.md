# ADR-001: Repository Boundaries

Status: Accepted

FactLama starts with three repositories: factlama-architecture, factlama-reliability, and factlama-observability.

API, schemas, SDK, collector, dashboard, deployment, and integrations remain modules until independent lifecycle or ownership requirements justify separation.

Cross-repository contracts are governed by the architecture repository.
