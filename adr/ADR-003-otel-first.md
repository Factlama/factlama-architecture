# ADR-003: OpenTelemetry First

Status: Accepted

FactLama uses OpenTelemetry concepts as the interoperability boundary for traces, spans, events, metrics, and resources.

FactLama may add AI-specific semantic attributes, but must not require the native dashboard to read directly from an OTEL backend. The dashboard consumes FactLama query APIs.
