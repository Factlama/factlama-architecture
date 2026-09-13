# FactLama Architecture

Start with [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for build order and exit tests, then [IMPLEMENTATION_MAP.md](IMPLEMENTATION_MAP.md) for component ownership. Component documentation is centralized in [factlama-reliability](factlama-reliability/README.md) and [factlama-observability](factlama-observability/README.md), including each component's `docs/implementation.md` task ledger. [CONTRACTS.md](CONTRACTS.md) owns the shared wire contract in prose; [`contracts/v0.1/`](contracts/README.md) is its executable counterpart -- JSON Schemas, canonical examples and a standalone validator. [DECISION_REGISTER.md](DECISION_REGISTER.md) indexes ADRs and status sources. [SECURITY_MODEL.md](SECURITY_MODEL.md), [OPERATIONS.md](OPERATIONS.md), [INTERACTION_STORE.md](INTERACTION_STORE.md) and [VALIDATION.md](VALIDATION.md) define cross-cutting requirements.

FactLama is an open-source AI reliability and observability platform for LLM, RAG, and agentic applications.

Its purpose is to make AI systems measurable, evidence-aware, debuggable, and governable without forcing every verification decision through another expensive frontier-model call.

## North star

An open-source AI reliability and observability platform that instruments LLM applications, evaluates model outputs and agent behavior, and provides evidence-based reliability signals using enterprise-approved models or the optional FactLama SLM.

## Product thesis

- Expensive model = intelligence/generation.
- FactLama Reliability = evidence-based evaluation, scoring, policy, and decisions.
- FactLama SLM = optional low-cost verification model that must earn its role through benchmarks.
- FactLama Observability = AI-native telemetry, traces, metrics, costs, reliability signals, and dashboard.
- FactLama does not sell another model call; it aims to reduce the number of expensive calls required to make AI systems reliable.

## Repository strategy

| Repository | Responsibility |
|---|---|
| `factlama-architecture` | System-level source of truth: scope, target architecture, cross-repo contracts, ADRs, security, roadmap and implementation governance |
| `factlama-reliability` | Reliability engine: claims, evidence, judges, verification, scoring, policy, RAG/agent evaluation, reliability API/SDK |
| `factlama-observability` | AI observability: OTEL/SDK ingestion, collector, telemetry processing, storage/query, dashboard, alerts and integrations |

Do not create separate repositories for core, schemas, API, ingestion, evaluation, SDK, collector, dashboard, integrations, deployment or docs until independent release/versioning pressure proves that split is necessary.

Possible later repositories, only when justified:

- `factlama-models`
- `factlama-benchmarks`

## Target architecture

Logical interaction flow:

1. An AI application emits telemetry through FactLama SDK and/or OpenTelemetry.
2. The observability collector accepts telemetry and AI semantic events.
3. Telemetry processing normalizes requests, spans, model usage, costs, retrieval, tool events and reliability signals.
4. Storage/query abstractions persist and expose telemetry without coupling the product to one backend.
5. Reliability receives an evaluation request, identifies claims, maps evidence, calls one or more judge providers, computes normalized findings/scores and applies policy.
6. Reliability results and provenance are correlated back to the original interaction/trace.
7. The native dashboard shows operational and semantic reliability views.

### Reliability responsibilities

Reliability owns:

- claims and claim segmentation;
- evidence and evidence mapping;
- judge/evaluator providers;
- groundedness;
- hallucination risk;
- contradiction detection;
- citation support;
- instruction adherence;
- confidence alignment;
- RAG evaluation;
- agent trajectory/tool-use evaluation;
- scoring;
- policies;
- decisions;
- evaluator provenance.

Core reliability code must depend on a stable `JudgeProvider` abstraction and must not know which model vendor is used.

### Evidence architecture

FactLama is not a generic RAG platform. It verifies outputs regardless of where evidence came from.

Evidence retrieval should remain behind an `EvidenceRetriever` abstraction. MVP begins with direct supplied context/evidence. Keyword, structured data, internal knowledge, hybrid and vector retrieval can be added later when retrieval is actually required.

A vector database is not an MVP requirement. Semantic similarity is not equivalent to truth.

### Observability responsibilities

Observability owns:

- OpenTelemetry-compatible concepts;
- traces, spans, events, metrics and resource metadata;
- AI request/model metadata;
- token usage and estimated cost;
- latency and failures;
- retrieval events;
- tool calls;
- reliability signals;
- model/prompt version correlation;
- query APIs;
- alerts;
- exporters;
- native AI dashboard.

The dashboard must query FactLama's query API rather than directly depending on a specific telemetry backend.

### AI semantic attributes

Initial semantic model should support concepts such as:

- `llm.model`
- `llm.provider`
- `llm.prompt_tokens`
- `llm.completion_tokens`
- `llm.cost`
- `ai.operation`
- `ai.reliability.groundedness`
- `ai.reliability.hallucination_risk`
- `ai.reliability.citation_support`
- `ai.agent.tool.name`
- `ai.agent.tool.success`
- retrieval document/reference metadata

### Shared identifiers

Where applicable, events/contracts should support stable identifiers for:

- tenant
- project/application
- interaction
- trace
- span
- evaluation
- model version
- prompt version
- evaluator version
- policy version

## Public reliability contract

The normalized contract is evaluator-independent.

### Claim verdicts

- `SUPPORTED`
- `CONTRADICTED`
- `UNSUPPORTED`
- `INSUFFICIENT_EVIDENCE`
- `NOT_APPLICABLE`

### Overall verdicts

- `PASS`
- `PARTIAL`
- `FAIL`
- `ABSTAIN`

### Initial score dimensions

- groundedness
- hallucination risk
- contradiction risk
- scope breach
- citation support
- instruction adherence
- tool correctness
- confidence alignment

### Initial violation codes

- `UNSUPPORTED_CLAIM`
- `CONTRADICTED_CLAIM`
- `HALLUCINATION`
- `SCOPE_BREACH`
- `INSTRUCTION_VIOLATION`
- `CITATION_MISMATCH`
- `CITATION_MISSING`
- `TOOL_SELECTION_ERROR`
- `TOOL_ARGUMENT_ERROR`
- `TOOL_RESULT_CONTRADICTION`
- `TOOL_RESULT_FABRICATION`
- `CONFIDENCE_MISMATCH`
- `INSUFFICIENT_EVIDENCE`

### Policy actions

- `PASS`
- `FAIL`
- `REGENERATE`
- `RETRIEVE_AGAIN`
- `SWITCH_MODEL`
- `ASK_USER`
- `BLOCK`
- `HUMAN_REVIEW`

Initial scoring should be transparent and replaceable by calibrated logic after benchmarking. A first heuristic may weight groundedness most heavily, then citation support, instruction adherence, tool correctness and confidence alignment, with explicit risk penalties.

## Multi-tenancy and security requirements

Multi-tenancy is P0 architecture, not future hardening.

Requirements:

- tenant context at persistence/query boundaries;
- no cross-tenant reads or writes;
- evaluator/provider credentials remain outside user-visible data;
- public contracts never require raw secrets;
- content capture is configurable;
- metadata-only operation is supported;
- redaction hooks exist before persistence;
- retention is configurable;
- evaluator/model/policy provenance is stored without requiring raw prompt storage;
- APIs and schemas are versioned;
- async operations are idempotent and retry-safe;
- FactLama emits telemetry about its own processing and failures.

## Interaction Store - architecture-ready, not MVP-required

Some users will want to retain prompts, responses, evidence, tool calls/results, judge outputs and final decisions for replay, debugging and regression datasets. This is a valid product direction but should not be a mandatory MVP dependency.

Capture modes should eventually include:

- capture nothing;
- metadata only;
- redacted content;
- full content.

Retention, redaction, encryption, tenant isolation and data residency must be considered before implementing full content persistence.

## Scope

### MVP scope

The MVP must deliver a real end-to-end product, not isolated libraries.

Required:

1. versioned evaluation request/result contracts;
2. claim-level groundedness/hallucination verification against supplied evidence;
3. evidence abstraction;
4. judge-provider abstraction with at least one working provider;
5. normalized findings, score, verdict and provenance;
6. transparent initial scoring;
7. tenant-aware persistence/query model;
8. synchronous evaluation;
9. retry-safe asynchronous evaluation;
10. configurable content capture foundation;
11. OTEL-compatible telemetry ingestion;
12. correlation between interaction, trace and evaluation;
13. native dashboard with AI overview, requests, latency, tokens, cost, errors, reliability and trace detail;
14. basic SDK/collector integration;
15. Docker Compose developer deployment;
16. automated unit/integration/contract/security tests.

### MVP end product

A developer should be able to clone/install FactLama, start it locally with Docker Compose, instrument an LLM or RAG application, send traffic, and then:

- see AI requests and traces;
- inspect model/provider, latency, token usage and cost;
- inspect retrieval/tool events when emitted;
- evaluate an answer against supplied evidence;
- see claim-level supported/unsupported/contradicted findings;
- see groundedness/hallucination/other normalized scores;
- see the final reliability verdict;
- see evaluator/model/configuration provenance;
- correlate the evaluation to the originating trace;
- run the same workflow through documented API/SDK examples.

If this flow does not work from a clean checkout, MVP is not complete.

### Full product scope

- multiple evaluators/judges;
- custom/enterprise judge adapters;
- citation verification;
- instruction adherence;
- RAG retrieval/context evaluation;
- agent/tool evaluation;
- policy orchestration;
- risk/cost-aware verification routing;
- alerts and regression detection;
- model/prompt/retrieval comparisons;
- interaction storage/replay;
- evaluation datasets;
- external observability exporters;
- RBAC and SSO;
- enterprise deployment and data controls.

### Future scope

- FactLama SLM training/runtime;
- benchmark repository/service;
- reproducible public benchmark reports;
- confidence-aware SLM routing;
- multi-stage judge cascade;
- optional hybrid/vector evidence retrieval;
- large-scale distributed processing;
- advanced enterprise integrations and storage tiers.

## Explicit MVP non-goals

- general-purpose Grafana/Splunk replacement;
- custom time-series database;
- custom vector database;
- generic RAG orchestration;
- mandatory storage of prompts/responses;
- mandatory Kafka;
- mandatory Kubernetes;
- SLM training before evaluator contracts and benchmark harness are stable.

## Implementation roadmap and status

Status values: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`.

### EPIC-01 Foundation - STATUS: NOT_STARTED

- [ ] Establish code layout and module boundaries in implementation repos.
- [ ] Define configuration conventions.
- [ ] Define public schema/API versioning.
- [ ] Add lint/type/test/CI foundations.
- [ ] Add architecture conformance checks where practical.

Exit criteria: clean checkout builds/tests; boundaries are documented; no evaluator/vendor coupling is introduced.

### EPIC-02 Tenancy and Security - STATUS: NOT_STARTED

- [ ] Define tenant/project/application identity model.
- [ ] Propagate tenant context through API, service and persistence layers.
- [ ] Add tenant isolation tests.
- [ ] Define content-capture/redaction configuration.
- [ ] Establish secret/provider credential boundaries.

Exit criteria: cross-tenant access tests fail safely; metadata-only operation works.

### EPIC-03 Evaluation Contracts and Provenance - STATUS: NOT_STARTED

- [ ] Implement versioned verification request/result types.
- [ ] Implement claim, evidence, violation, score and verdict models.
- [ ] Implement evaluator provenance.
- [ ] Add JSON/schema contract tests.

Exit criteria: public result is evaluator-independent and round-trips through API/storage.

### EPIC-04 First Grounding Evaluator - STATUS: NOT_STARTED

- [ ] Implement claim segmentation.
- [ ] Implement evidence mapping.
- [ ] Implement `JudgeProvider` interface.
- [ ] Add first provider adapter.
- [ ] Implement groundedness/unsupported/contradiction findings.
- [ ] Implement transparent aggregate scoring.
- [ ] Add golden tests.

Exit criteria: supplied answer + evidence produces deterministic normalized result with provenance.

### EPIC-05 Content Governance - STATUS: NOT_STARTED

- [ ] Implement capture-mode configuration.
- [ ] Add redaction hooks.
- [ ] Separate telemetry metadata from optional interaction content.
- [ ] Add retention interfaces/configuration.

Exit criteria: the product works with content capture disabled.

### EPIC-06 Async Evaluation - STATUS: NOT_STARTED

- [ ] Define evaluation job states.
- [ ] Implement idempotency keys.
- [ ] Implement retry/backoff and terminal failure behavior.
- [ ] Add duplicate/retry tests.

Exit criteria: duplicate delivery does not create duplicate logical evaluations.

### EPIC-07 Evaluator Ecosystem - STATUS: NOT_STARTED

- [ ] Provider registry/configuration.
- [ ] Add second provider/custom adapter path.
- [ ] Version evaluators and configurations.
- [ ] Normalize failures/timeouts.

### EPIC-08 Policy and Verification Routing - STATUS: NOT_STARTED

- [ ] Implement policy inputs/actions.
- [ ] Implement deterministic rule evaluation.
- [ ] Add risk/cost routing interface.
- [ ] Preserve decision provenance.

### EPIC-09 Observability Core - STATUS: NOT_STARTED

- [ ] OTEL-compatible ingestion.
- [ ] AI semantic telemetry model.
- [ ] Storage abstraction.
- [ ] Query API.
- [ ] Reliability signal correlation.
- [ ] FactLama self-observability.

### EPIC-10 Native Dashboard - STATUS: NOT_STARTED

- [ ] AI overview.
- [ ] LLM requests/models/tokens/cost/latency/errors.
- [ ] Reliability view.
- [ ] RAG view foundation.
- [ ] Agent/tool view foundation.
- [ ] Trace explorer.

### EPIC-11 SDK, Collector and Integrations - STATUS: NOT_STARTED

- [ ] Minimal SDK instrumentation.
- [ ] Collector configuration.
- [ ] Integration examples.
- [ ] External export abstraction.

### EPIC-12 SLM and Benchmarking - STATUS: NOT_STARTED

- [ ] Build labeled benchmark datasets.
- [ ] Benchmark strong judge baselines and humans.
- [ ] Measure accuracy, precision, recall, F1, calibration, latency, tokens and cost.
- [ ] Train/select SLM only after benchmark criteria are explicit.

### EPIC-13 Interaction Store and Replay - STATUS: NOT_STARTED

- [ ] Define optional interaction-store interface.
- [ ] Implement configurable persistence modes.
- [ ] Add replay/dataset extraction path.
- [ ] Add retention and deletion behaviors.

### EPIC-14 Enterprise Hardening - STATUS: NOT_STARTED

- [ ] RBAC/SSO architecture and implementation.
- [ ] Enterprise deployment patterns.
- [ ] Advanced audit/data controls.
- [ ] Scale/performance validation.

## Claude implementation protocol

Claude must implement vertical slices, not "build FactLama" in one pass.

For every task, use this lifecycle:

`READ -> UNDERSTAND -> INSPECT EXISTING CODE -> PLAN -> IMPLEMENT -> TEST -> REVIEW -> DOCUMENT -> UPDATE STATUS`

Each task/epic must carry a status and checklist:

- `STATUS: NOT_STARTED` initially.
- Set `IN_PROGRESS` before implementation.
- Set `BLOCKED` only with a concrete blocker and evidence.
- Set `COMPLETE` only when every acceptance criterion and test passes.

Required completion checklist:

- [ ] Read architecture/source-of-truth sections relevant to the task.
- [ ] Inspect existing implementation before creating new abstractions.
- [ ] Confirm affected modules and dependency direction.
- [ ] Implement the smallest complete vertical slice.
- [ ] Add unit tests.
- [ ] Add integration/contract tests where applicable.
- [ ] Test failure/retry paths.
- [ ] Verify tenant isolation/security boundaries.
- [ ] Verify idempotency where asynchronous.
- [ ] Verify observability/telemetry.
- [ ] Run lint/type checks.
- [ ] Run repository test suite.
- [ ] Review for architectural drift.
- [ ] Update implementation documentation/status.
- [ ] Mark `COMPLETE` only after all checks pass.

Claude must not:

- create a new repository/module boundary without architectural justification;
- add a specific model vendor into reliability core;
- introduce Kafka/vector DB/Kubernetes because it is "enterprise-like";
- persist prompts/responses by default without capture configuration;
- bypass tenant context;
- invent a new public result contract for each evaluator;
- mark work complete when only happy-path unit tests pass.

## Test strategy

### Unit tests

Cover schema validation, scoring, policy rules, evidence mapping, redaction, adapters, telemetry normalization and query logic.

### Contract tests

Verify request/result schema compatibility, API version behavior, evaluator normalization and cross-repository identifier semantics.

### Integration tests

At minimum:

1. supported claim + supporting evidence -> supported finding;
2. contradicted claim + contradicting evidence -> contradicted finding;
3. unsupported claim -> unsupported/insufficient evidence without fabricated support;
4. evaluator timeout -> normalized failure and observable error;
5. duplicate async request -> one logical evaluation;
6. tenant A cannot retrieve tenant B data;
7. content capture disabled -> product still evaluates and observes metadata;
8. trace ID/evaluation ID correlation survives persistence/query;
9. clean Docker Compose startup -> API, collector, storage and dashboard become usable;
10. dashboard query -> returns the same normalized reliability data exposed by API.

### Golden evaluation tests

Maintain a small hand-reviewed dataset with supported, contradicted, unsupported, ambiguous and citation cases. Track regressions by evaluator/model/configuration version.

### Security tests

Test tenant isolation, authorization boundaries, redaction, provider credential handling, malformed inputs, oversized inputs/limits and unsafe persistence defaults.

### Performance tests

Measure evaluation latency, ingestion throughput, query latency and resource footprint. Establish numbers before introducing distributed infrastructure.

## Architecture decisions

### ADR-001 - Three initial repositories
Accepted. Keep architecture, reliability and observability as the only initial repositories. Split only when independent lifecycle/versioning/team ownership requires it.

### ADR-002 - Reliability Engine
Accepted. Claims, evidence, evaluation, scoring, policy and provenance belong to the first-class Reliability Engine.

### ADR-003 - OTEL first
Accepted. Use OpenTelemetry-compatible concepts and integration boundaries, while keeping the native FactLama query/dashboard model decoupled from any one backend.

### ADR-004 - Judge provider abstraction
Accepted. Reliability core must never depend directly on a specific model provider.

### ADR-005 - Evidence abstraction
Accepted. FactLama verifies against supplied evidence first; it is not a generic RAG system.

### ADR-006 - SLM is optional and benchmark-gated
Accepted, with its SLM-only qualification asymmetry superseded by ADR-010. The SLM is a potential low-cost evaluator, not the platform; it follows the same qualification rule as every judge.

### ADR-007 - Native AI dashboard
Accepted. Build a lightweight AI-specific dashboard for users without an existing observability stack, while retaining enterprise export/integration paths.

### ADR-008 - Interaction Store deferred
Accepted. Design for optional interaction persistence and replay now, but do not make it an MVP dependency.

### ADR-009 - MVP reference stack
Accepted. Use Python services and SDK, a TypeScript dashboard, PostgreSQL metadata/job outbox, and maintained OTLP/HTTP libraries for the first implementation; preserve language-independent public contracts.

### ADR-010 - Evaluator qualification and calibration classes
Accepted. Any evaluator, not only the FactLama SLM, must carry a calibration class and earn a benchmark-backed qualification status before becoming a tenant's default judge; scores are comparable only within a calibration class.

### ADR-011 - Judge adapter trust tiers
Accepted. Judge adapters split into first-party (in-process), certified partner (in-process, signed and conformance-tested), and customer (out-of-process only, over a published HTTP wire schema, with no access to FactLama's database or secrets beyond the call in flight).

### ADR-012 - Verification budgets and cost ownership
Accepted. Verification enforces per-request/per-tenant token and cost budgets and claim/evidence fan-out caps; bring-your-own-key is the default and only economic model for judge calls.

### ADR-013 - Evidence as adversarial input at the judge boundary
Accepted. Evidence is treated as untrusted, potentially adversarial input, with structural instruction/data separation, deterministic post-validation, detection (not silent dropping) of suspected injection, and adversarial fixtures run against every registered adapter.

### ADR-014 - Provider lifecycle, pinning and compliance constraints
Accepted. The evaluator registry has an explicit lifecycle and audit trail, model identifiers are pinned rather than floating aliases, and provider selection (including fallback) is constrained by tenant-declared compliance attributes.

### ADR-015 - Deferred multi-judge reconciliation
Accepted. Multi-judge ensembles stay out of MVP scope, but provenance and finding shapes are provisioned in v0.1 so that adding them later is additive rather than a breaking change.

See [ANY_JUDGE_ARCHITECTURE_REVIEW.md](ANY_JUDGE_ARCHITECTURE_REVIEW.md) for the analysis behind ADR-010 through ADR-015.

### ADR-016 - Centralized component documentation
Accepted. Reliability and Observability component specs and task ledgers live in this architecture repository; code repositories retain short README and agent entrypoints.

## Definition of MVP done

MVP is complete only when a fresh developer can:

1. clone the implementation repos;
2. start the documented local stack;
3. instrument a sample LLM/RAG app;
4. generate trace/usage telemetry;
5. submit or trigger an evaluation with evidence;
6. receive normalized claim-level results, scores, verdict and provenance;
7. inspect the same interaction and evaluation in the dashboard;
8. run the complete automated test suite successfully;
9. run with interaction content capture disabled;
10. demonstrate tenant isolation.

Anything short of this is an implementation milestone, not MVP completion.

## License

MIT. Keep third-party dependencies and model licenses independently reviewed; MIT licensing of FactLama code does not automatically make third-party model weights or datasets MIT-compatible.
