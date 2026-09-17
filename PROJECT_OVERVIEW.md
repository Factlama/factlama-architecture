# FactLama: Project Overview

## What we are building

FactLama is an open-source platform that helps organizations understand whether their AI systems are working correctly in the real world.

Modern AI applications can produce fluent, confident answers while still being wrong, unsupported, outdated, or inconsistent with the information they were given. When these applications use retrieval, tools, or multiple agents, it also becomes difficult to understand what happened during a request and where a failure began.

FactLama addresses both problems together:

- **Reliability** evaluates an AI response against available evidence and produces clear, structured findings.
- **Observability** records how the AI application behaved, connects operational telemetry to reliability results, and makes that information available through queries, dashboards, and alerts.

The goal is to give product teams, engineers, security teams, and business owners a shared view of AI quality. Instead of relying on a model's confidence or manually inspecting scattered logs, they can see what the system said, whether the important claims were supported, which evidence was used, what the request cost, how long it took, and what should happen next.

FactLama is designed for large language model applications, retrieval-augmented generation systems, copilots, and agentic workflows. It is not tied to one AI provider, one model, or one telemetry database.

## The problem FactLama solves

Traditional software usually fails in visible and repeatable ways. A request returns an error, a database query fails, or a test produces the wrong value. AI systems often fail differently. They can return a technically successful response that sounds reasonable but contains a false claim. A retrieval system can provide the wrong documents. An answer can include citations that do not support its statements. An agent can call the wrong tool or use a correct tool result incorrectly.

Existing monitoring products are useful for infrastructure health, latency, and errors, but they usually cannot answer questions such as:

- Was this answer grounded in the documents supplied to the model?
- Which individual statements were supported or contradicted?
- Did the citations actually support the claims they were attached to?
- Did a prompt, model, or retrieval change reduce answer quality?
- Did the agent choose the correct tool and use its result faithfully?
- Was a failed evaluation caused by bad evidence, an unavailable evaluator, or an exhausted budget?
- Can the organization investigate the issue without storing sensitive prompts and responses?

Teams often compensate with manual reviews, application-specific scripts, more calls to expensive general-purpose models, and dashboards assembled from unrelated systems. These approaches are costly, difficult to compare across applications, and hard to govern consistently.

FactLama provides a common reliability contract and a common observability layer. This allows different applications and evaluators to produce comparable results while preserving the details needed to explain each decision.

## How it works

Consider an enterprise assistant answering a question from internal documents. The application sends FactLama the answer and the evidence that was available when the answer was generated.

FactLama then follows a controlled evaluation process:

1. It authenticates the request and establishes the tenant, project, and application scope.
2. It accepts explicit claims from the application or separates the answer into claims that can be checked individually.
3. It maps the supplied evidence to those claims.
4. It sends one claim at a time, with bounded evidence, to an approved evaluator.
5. It validates the evaluator's response and verifies that cited evidence IDs belong to the request.
6. It classifies each claim as supported, contradicted, unsupported, or lacking sufficient evidence.
7. It calculates transparent reliability scores and an overall verdict.
8. It applies an optional policy, such as allowing the response, retrieving again, regenerating it, asking the user for clarification, blocking it, or sending it for human review.
9. It records which evaluator, model, configuration, policy, and evidence references contributed to the result.
10. It connects the evaluation to the original application trace so the result can be investigated alongside latency, token use, cost, retrieval activity, and tool calls.

A result is therefore more useful than a single score. It can say that an answer was partially reliable because two claims were supported, one contradicted the evidence, and another could not be evaluated. It can also explain which evidence and evaluator produced those findings.

When an evaluator times out or no approved provider is available, FactLama does not pretend the answer is false. It reports an abstention or operational failure. This distinction is important: “the claim is unsupported” and “the system could not complete the evaluation” mean very different things to users and operators.

## The two parts of the platform

### Reliability Engine

The Reliability Engine evaluates the meaning and support behind AI output. Its responsibilities include:

- claim identification;
- evidence mapping;
- groundedness and contradiction checks;
- citation validation;
- instruction and policy checks;
- agent and tool-use evaluation;
- normalized scores and verdicts;
- recommended policy actions;
- evaluator and decision provenance.

The engine uses a provider-independent evaluator interface. An organization can use an approved commercial model, an internal model, a local open model, or eventually the optional FactLama small language model. Changing the evaluator should not require changing the public API or the meaning of results.

Evaluators must be qualified before they are treated as trusted defaults. FactLama's direction is to measure evaluator agreement, accuracy, latency, and cost against versioned benchmarks rather than assuming that a model is suitable because it is popular or powerful.

### Observability Platform

The Observability Platform explains what happened across the AI application. It collects and connects information such as:

- requests, traces, and spans;
- model and provider versions;
- prompt versions;
- latency, failures, and retries;
- input and output token usage;
- estimated or provider-reported cost;
- retrieval operations and document references;
- agent and tool activity;
- reliability verdicts and scores;
- evaluator and policy versions.

The native dashboard will let teams move from a high-level reliability trend to a specific trace, evaluation, claim, or failure. For example, a team could identify that groundedness declined after a retrieval configuration change, isolate the affected model and prompt version, and inspect representative evaluations.

FactLama uses OpenTelemetry-compatible concepts so it can fit into existing monitoring environments. It also provides its own query and dashboard boundary, allowing a smaller team to run it without first adopting a large observability stack.

## A practical example

Suppose a financial-services assistant answers:

> The customer is eligible for the premium product because their annual income exceeds the required threshold and their account has been active for more than two years.

The application supplies the relevant policy and customer-record evidence. FactLama separates the answer into two claims and checks each one.

- The income claim is supported by the customer record.
- The account-age claim is contradicted because the account was opened eight months ago.
- The overall result is a failure or partial result according to the configured policy.
- The policy recommends blocking the response and sending it for review.
- The result records the supporting and contradicting evidence references, evaluator version, policy version, timing, and cost.
- The dashboard links this decision to the original application trace, including the retrieval step and the model request.

This gives the organization an actionable explanation. It can correct the response, investigate why the wrong account information was used, measure how often similar failures occur, and show how the automated control reached its decision.

## How FactLama helps enterprises

### Safer adoption of AI

Enterprises need more than successful API calls before they can trust AI in customer support, finance, healthcare, legal operations, internal knowledge systems, and automated workflows. FactLama adds a measurable control layer between model output and business action. Policies can route uncertain or high-risk results to a safer response, another retrieval attempt, or human review.

### Evidence and accountability

FactLama keeps reliability decisions connected to evidence references and evaluator provenance. Teams can determine which claims were checked, which evidence was used, which evaluator made the judgment, and which configuration was active. This supports investigation, audit preparation, incident review, and responsible model governance.

FactLama does not claim that an automated evaluator is infallible. Provenance and qualification data make the evaluator's limits visible rather than hiding them behind a score.

### Vendor and model independence

AI providers, models, and enterprise standards will continue to change. FactLama separates its public result format and policy logic from provider-specific code. Organizations can replace or combine evaluators without rewriting every application or losing the ability to compare historical results.

### Lower and controlled evaluation cost

Calling a large frontier model to judge every output can become expensive. FactLama supports bounded evaluation, approved provider selection, bring-your-own provider credentials, and explicit usage provenance. Its long-term model is to use the least expensive qualified evaluator appropriate for the task, including local models and the optional FactLama small language model where benchmark results justify it.

FactLama does not broker or mark up judge calls in its initial model. Enterprises use their own approved provider relationships and remain in control of cost and credentials.

### Faster debugging and improvement

Reliability results become much more useful when connected to traces, model versions, prompt versions, retrieval behavior, and tool activity. Product and engineering teams can answer questions such as:

- Did the latest prompt release increase unsupported claims?
- Is one model producing more contradictions than another?
- Are slow responses associated with repeated retrieval or tool failures?
- Did a reliability regression begin after a document-index update?
- Which applications account for the largest evaluation cost?

This turns AI quality from an occasional manual review into an operational signal that teams can track over time.

### Privacy and deployment control

Many organizations cannot send sensitive content to an unapproved service or retain raw prompts indefinitely. FactLama is being designed to support several capture modes:

- no interaction content;
- metadata only;
- redacted content;
- full content through explicit opt-in.

Core observability does not require raw prompts or responses. Redaction and retention controls apply before persistence, and provider credentials are kept outside evaluation payloads and telemetry. Tenant context is required throughout ingestion, evaluation, persistence, and query paths.

FactLama is intended to run locally or inside an enterprise-controlled environment. The initial experience targets a simple Docker Compose deployment, while the architecture leaves room for approved identity systems, storage services, exporters, networking controls, Kubernetes, data-residency requirements, and customer-managed infrastructure.

### A shared language across teams

AI incidents often involve several groups that use different tools and terminology. FactLama provides stable concepts—claims, evidence, verdicts, violations, policies, traces, and provenance—that product, engineering, security, risk, and compliance teams can discuss together.

## What FactLama is not

FactLama is not an AI model provider, a general-purpose retrieval platform, or a replacement for an organization's entire monitoring stack.

It does not require a custom vector database, custom time-series database, Kafka, or Kubernetes for its first usable deployment. It does not treat semantic similarity as proof of truth. It also does not require organizations to store all prompts, responses, or evidence.

The platform focuses on the layer between an AI application's output and the organization's decision to trust, deliver, retry, block, or investigate that output.

## Architecture and deployment at a glance

FactLama is divided into three repositories:

- **Architecture** defines shared contracts, security and privacy rules, system decisions, and the delivery plan.
- **Reliability** implements evaluation, scoring, policy, and provenance.
- **Observability** implements telemetry ingestion, processing, queries, dashboards, alerts, and integrations.

At runtime, an application can use the Reliability API directly, emit telemetry to the Observability collector, or do both. Stable identifiers connect an application interaction, trace, model call, and evaluation without forcing all data into one service or database.

The first complete product will support an end-to-end path in which a developer can instrument an application, evaluate an answer against supplied evidence, receive claim-level findings, correlate the evaluation with a trace, and inspect the result in a native dashboard.

## Current stage and direction

FactLama is under active development. The shared contracts and core architecture are defined, and the Reliability component has a working synchronous evaluation path with tenant-aware authentication, explicit claim and evidence handling, bounded pre-dispatch checks, provider-independent evaluation, normalized results, and automated contract and security tests.

The Observability component has its engineering foundation and initial tenant and reliability-event models. Collector, storage/query, dashboard, asynchronous evaluation, full content governance, evaluator qualification, and enterprise deployment features remain part of the planned delivery sequence.

This distinction matters: the document describes the product being built and the architectural commitments guiding it. It should not be read as a claim that every capability described here is already production-ready.

## The intended outcome

FactLama aims to make AI systems easier to trust for the same reason mature software systems became easier to trust: their behavior can be measured, failures can be explained, controls can be applied consistently, and improvements can be verified.

For an enterprise, that means moving from “the model usually seems right” to a system that can show what happened, what evidence supports the answer, where uncertainty remains, how much the decision cost, and what action should follow.
