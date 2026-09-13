# Dependency boundaries

Core Reliability domain code cannot import vendor SDKs, storage clients or Observability internals. Provider, retrieval, persistence and event transport are adapters behind ports. Observability cannot recalculate factual verdicts; it projects versioned Reliability events. Dashboard uses query APIs, not database access. Tenant context is established at trusted ingress and carried through async work. New repositories, mandatory services or cross-repository schema changes require an ADR.
