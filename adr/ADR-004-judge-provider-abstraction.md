# ADR-004: Judge Provider Abstraction

Status: Accepted

Reliability code depends on a stable JudgeProvider contract, not directly on provider SDKs. Adapters translate provider-specific requests, errors, and responses into FactLama contracts and preserve evaluator provenance.
