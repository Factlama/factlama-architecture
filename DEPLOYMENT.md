# Deployment Architecture

## Deployment modes

### Developer / startup default
A single `docker compose up` experience should start the minimum viable platform: Reliability API/runtime, Observability collector/processing/query, persistence dependencies, and dashboard.

### Enterprise self-hosted
Support containerized deployment behind enterprise ingress/load balancers with external identity, secrets management, managed databases, private networking, centralized logging/metrics, and horizontal scaling.

### Kubernetes
Future enterprise mode. Services remain independently scalable where workload patterns differ: collector/ingestion, evaluation workers, query API, dashboard, and supporting stores.

## Runtime characteristics
- APIs and collectors should be stateless where practical.
- Stateful concerns live behind storage interfaces.
- Expensive/slow evaluation supports asynchronous workers.
- Health/readiness endpoints distinguish process health from dependency readiness.
- Configuration is externalized and environment-specific.
- Secrets are injected through deployment secret facilities, never committed.

## Availability and failure isolation
- Telemetry instrumentation must be non-blocking/best-effort by default for customer request paths.
- Provider timeouts are bounded.
- Retry storms are prevented with bounded backoff/jitter and idempotency.
- Downstream failures are visible through platform telemetry.
- Dashboard unavailability does not affect ingestion/evaluation.

## Scale dimensions
Plan independently for requests/sec, spans/sec, evaluation jobs/sec, evidence payload size, telemetry retention, query concurrency, and dashboard users. Do not assume they scale together.

## Upgrade strategy
Public API/event/schema versions are explicit. Persistent schema changes require migrations. Rolling upgrades should preserve backward compatibility for supported versions. Breaking changes require deprecation and migration guidance.
