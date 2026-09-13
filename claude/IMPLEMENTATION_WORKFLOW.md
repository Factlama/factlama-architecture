# Implementation workflow

For each slice: read the owning contract and ADR; inspect current code; write a concrete request/result or event fixture; implement the path; test success, abstention/failure, duplicate/retry and cross-tenant cases; verify telemetry and content capture mode; run repository checks; update docs and task status. For a cross-repository slice, run a contract fixture through Reliability output, Observability ingestion/query and dashboard projection before closing the epic.
