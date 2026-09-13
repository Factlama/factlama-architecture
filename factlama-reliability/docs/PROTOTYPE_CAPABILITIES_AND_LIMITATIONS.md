# FactLama — Capabilities and Limitations (as of Phase 1)

> Historical prototype snapshot, not the current FactLama architecture or implementation status. See [CURRENT_IMPLEMENTATION.md](../CURRENT_IMPLEMENTATION.md) and the accepted [shared contract](../../CONTRACTS.md) before using these examples as acceptance criteria.

**Status**: Phase 0 and Phase 1 (verification-engine scope) complete. Phase 1.5
(`factlama-extract`) and Phase 2 (benchmark harness) intentionally deferred —
see `CLAUDE.md` for the full roadmap and what's pending in each.

This document is a plain-language snapshot of what the system can and can't
do today, backed by real output from running it. Written so it can be
revisited without re-deriving context from the code.

## What FactLama is

You give it three things — a **question**, an AI's **answer**, and **evidence**
(source text the answer is supposed to be based on). It does not generate
answers; it's a checker that sits after your AI and verifies what it said.

It:
1. Splits the answer into individual factual claims (e.g. "Company X was
   founded in 2018" and "It has 5000 employees" are checked separately, even
   if they're in the same sentence).
2. Checks each claim against your evidence.
3. Produces a verdict (`PASS` / `PARTIAL` / `FAIL` / `ABSTAIN`), a 0–1
   reliability score, and a plain-English reason per claim — not a black-box
   number.
4. Optionally enforces rules you configure (policies) — e.g. "never fail to
   cite sources," "never discuss investment advice," "any tool failure is
   unacceptable."

## Capabilities (demonstrated, with real output)

All examples below were run against the actual code, not hypothetical.

### 1. Correct claims score high

```python
verify(
    question="When was Company X founded?",
    answer="Company X was founded in 2018.",
    context=[Evidence(id="doc_001", extracted_text="Company X was founded in 2018.")],
)
```
→ `PASS`, reliability `1.00`, claim `SUPPORTED`.

### 2. Numeric contradictions are caught

```python
verify(
    question="What does Product X weigh?",
    answer="Product X weighs 3.4 kg.",
    context=[Evidence(id="doc_001", extracted_text="Product X weighs 2.4 kg.")],
)
```
→ `FAIL`, reliability `0.00`, claim `CONTRADICTED` ("Numerical values in claim
contradict evidence"), violation `CONTRADICTED_CLAIM`.

### 3. Partial hallucination (one true claim, one made-up) is caught

```python
verify(
    question="Tell me about Company X.",
    answer="Company X was founded in 2018. It has 5000 employees.",
    context=[Evidence(id="doc_001", extracted_text="Company X was founded in 2018.")],
)
```
→ `PARTIAL`, reliability `0.59`. First claim `SUPPORTED`, second claim
`UNSUPPORTED` ("No relevant evidence found"), violation `UNSUPPORTED_CLAIM`.

### 4. Scope/topic policies are enforced

```python
verify(
    question="What should I do with my savings?",
    answer="You should invest in Company X stock.",
    policy=Policy(id="p1", scope=ScopePolicy(enabled=True, forbidden=["invest"])),
)
```
→ `PARTIAL`, reliability `0.83`, violation `SCOPE_BREACH`.

### 5. Failed agent tool calls are enforced, with configurable strictness

```python
verify(
    question="What is the weather in Paris?",
    answer="The weather in Paris is sunny.",
    tools=[ToolExecution(id="t1", tool_name="weather_api", status=ToolStatus.ERROR,
                          error_message="API timeout")],
)
```
→ `FAIL` by default (reliability `0.78`, violation `TOOL_ERROR`). This is a
**deliberate fail-safe default** (`ToolPolicy.fail_on_error=True`) — pass
`policy=Policy(id="p2", tools=ToolPolicy(fail_on_error=False))` to downgrade
the same failure to `PARTIAL` instead.

### 6. Citation validity is checked (structural, no model needed)

A citation pointing at a source id that doesn't exist in the evidence, or at
a real source that wasn't actually the claim's supporting evidence, is
flagged as `CITATION_MISMATCH` and lowers `citation_support`. Policies can
also require citations to be present at all (`CitationPolicy.required`) or
enforce a minimum support score (`CitationPolicy.minimum_support`).

### 7. Meaning-based ("semantic") matching, when explicitly enabled

The **default** checker only understands shared words. A heavily reworded
but true claim:

```python
question = "When did Company X launch?"
answer = "Company X came into existence during 2018."
evidence = [Evidence(id="doc_001", extracted_text="Company X was founded in 2018.")]
```

- **Default (rule-based) checker** → `PARTIAL`, reliability `0.17`, claim
  `UNSUPPORTED` ("No relevant evidence found"). **False alarm** — the
  statement is true, but the words don't overlap enough.
- **Optional embeddings-based checker** (`EmbeddingProvider`, needs
  `pip install factlama[embeddings]`) on the *same* input → `PASS`,
  reliability `0.98`, claim `SUPPORTED` ("similarity: 0.89"). It understands
  meaning, not just shared vocabulary.

An `NLIProvider` (entailment/contradiction classification via a small
MNLI-finetuned model, `pip install factlama[nli]`) is also available as a
third option, verified to correctly distinguish entailment / contradiction /
neutral cases against real evidence in testing.

## Limitations (be deliberate about these)

1. **No evidence supplied → no ability to catch fabrication.** Without
   evidence, groundedness defaults to a perfect score and hallucination
   detection is switched off entirely:
   ```python
   verify(
       question="What is the company's future revenue?",
       answer="Revenue will be $10 billion next year.",
       context=[],
   )
   ```
   → `PASS`, reliability `0.93` — a completely made-up number sails through.
   FactLama can only check claims against evidence you actually give it; it
   is not a general-knowledge fact-checker.

2. **The default checker only understands shared words, not meaning.** It
   will raise false alarms on true, reworded statements (see Capability #7
   above) unless you explicitly enable a semantic provider. That provider
   requires an extra install and is slower (it loads a real ML model on
   first use).

3. **The "smarter" checkers aren't perfect either.** The NLI-based checker
   sometimes misclassifies clearly-unrelated (not contradicting) text as
   "contradiction" rather than "neutral" — a known miscalibration of small
   MNLI-style models on out-of-domain input, not something FactLama's code
   controls. Worth using a stronger/larger NLI checkpoint if this matters for
   a given deployment.

4. **No accuracy benchmark exists yet.** Nobody has measured "how often is
   FactLama actually right" against a standard test set. That's explicitly
   Phase 2 (deferred — a different approach is planned and needs separate
   scoping before starting).

5. **It doesn't fetch documents for you.** Evidence must be handed to it as
   plain text already. Pulling from PDFs, Confluence, SharePoint, APIs, etc.
   is a planned-but-unbuilt separate layer (`factlama-extract`, Phase 1.5,
   deferred).

6. **A recent default-behavior change is easy to be surprised by.** As of
   this session, `ToolPolicy.fail_on_error` defaults to `True`: *any* single
   failed tool call now fails the whole request unless you explicitly set
   `fail_on_error=False`. Previously tool failures only ever reached
   `PARTIAL`. This is a deliberate fail-safe choice, but changes default
   verdicts for any tool-using request that has ever had a failure.

## Where to look for more detail

- `CLAUDE.md` — full phase-by-phase roadmap and what's done/pending in each,
  including the specific bugs found and fixed in `NLIProvider` this session
  (wrong default model, hardcoded label ordering, a `TypeError` in the
  confidence calculation).
- `tests/core/test_verifier.py`, `test_policy.py`, `test_scoring.py`,
  `test_semantic_providers.py` — the tests referenced above are runnable
  proof of every capability and limitation described here; run
  `python -m pytest tests/ -v` to see them all pass live.
- `architecture docs/FactLama_Schemas_and_Core_Specification.md` — the full
  schema/scoring contract this is built against.
