# Security Architecture

FactLama is designed as a multi-tenant enterprise platform. Security requirements apply from the first implementation phase.

## Trust boundaries
- External client to public API
- API to internal services
- Reliability engine to external model providers
- Collector to telemetry storage
- Query API to dashboard
- Platform services to persistence layers

## Required controls
- Tenant identity propagated through every request and persistence operation
- No cross-tenant reads or writes
- Secrets never stored in user-visible payloads
- Provider credentials isolated from evaluation content
- Authentication and authorization enforced at API boundaries
- Sensitive content capture is configurable and disabled by default where practical
- Redaction occurs before persistence
- Encryption in transit and at rest is supported by deployment design
- Audit-relevant actions retain actor, tenant, version and timestamp metadata
- Async processing is idempotent and retry safe

## Enterprise design requirements
Security controls must remain compatible with future RBAC, SSO, workload identity, private networking, enterprise key management, data residency and customer-managed storage.
