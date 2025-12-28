# ADR-006: Anti-Hallucination & Evals Strategy

**Status**: Accepted  
**Date**: 2025-12-28  
**Deciders**: Product & Engineering Team  
**Consulted**: SYSTEM.md (Sections 5 & 0)

---

## Context

The **Rewrite Agent** (Phase 9) leverages LLMs to improve resume content. However, LLMs are prone to "hallucinations"—inventing skills, experiences, or metrics that the user never claimed. This violates our core principle of **"Truth over Hype"** and poses legal/reputational risks to the user.

We needed a strategy to:
1.  Guarantee **zero fabricated claims**.
2.  Adhere to **SYSTEM.md Section 5** (Diff-only, HITL mandatory).
3.  Establish an evaluation baseline without over-engineering the MVP.

## Decision

We decided to implement a **Multi-Layered Safety Architecture** primarily relying on deterministic validation and Human-in-the-Loop (HITL), rather than complex offline evaluation benchmarks for the MVP.

### Key Components

1.  **Dedicated `RewriteValidator`**:
    *   **Rule-Based Entity Extraction**: Deterministically extracts skills, companies, and metrics.
    *   **Strict Comparison**: Any new entity in the output that wasn't in the input is flagged as a potential hallucination (Risk Level: HIGH).
    *   **Placeholder Mandate**: New metrics must use specific placeholder formats (e.g., `[X%]`) to be valid.
    *   **Ignored Action Verbs**: A whitelist of verbs (e.g., "Architected", "Led") prevents false positives during entity extraction.

2.  **Mandatory HITL (Human-in-the-Loop)**:
    *   The `RewriteAgent` *cannot* apply changes automatically.
    *   All changes must pass through the `IApprovalGate` interface, requiring explicit user approval.

3.  **Modular `IEvaluator` Interface**:
    *   We defined a protocol `IEvaluator` for observability.
    *   **MVP**: `SimpleEvaluator` (in-memory logging) tests the pipelines.
    *   **Future**: Drop-in support for **LangSmith** or **LangFuse** without changing agent logic.

## Rationale

*   **Safety Over Speed**: We prioritize preventing false claims over generating "creative" (but risky) content. A rule-based validator is arguably safer than an LLM-based judge for detecting specific factual inconsistencies (like new company names).
*   **SYSTEM.md Compliance**: Section 5 explicitly forbids semantic edits that change the truth. Our validator enforces this via code.
*   **MVP Pragmatism**: Building a comprehensive "Golden Dataset" for resume rewriting is time-consuming. Validating against the *input resume itself* is an effective, self-contained ground truth for the MVP.
*   **Observability**: The `IEvaluator` pattern ensures we aren't flying blind, while avoiding vendor lock-in or heavy dependencies (like LangChain) in the core logic.

## Consequences

### Positive
*   **Guaranteed Honesty**: The system physically cannot "sneak in" a new skill like "Kubernetes" unless the validator logic fails (unlikely given the unit tests).
*   **Zero Regression**: We can swap LLM models (Gemini 1.5 -> 2.0) without fear of safety degradation, as the validator is model-agnostic.
*   **Clean Architecture**: Separation of concerns (Generation vs. Validation vs. Evaluation).

### Negative
*   **Conservatism**: The validator might flag legitimate synonyms or inferred skills as hallucinations (e.g., inferring "Git" from "GitHub"). We accept this trade-off: users can manually add missing skills, but the AI won't do it for them.
*   **Maintenance**: The `IGNORED_VERBS` and regex patterns in `RewriteValidator` may need updates as we encounter more creative resume language.

## Alternatives Considered

1.  **"LLM-as-a-Judge"**:
    *   *Idea*: Ask another LLM "Did the first LLM hallucinate?"
    *   *Rejection*: Still non-deterministic. Too expensive/slow for real-time interactive editing.

2.  **Full Evaluation Harness (DeepEval / RAGAS)**:
    *   *Idea*: Use a framework like RAGAS to score "faithfulness".
    *   *Rejection*: Overkill for MVP. We just need to know "did it add a word that wasn't there?". Regex is faster and 100% explainable.

3.  **Unconstrained Generation**:
    *   *Idea*: Let the LLM rewrite freely, trust the user to edit.
    *   *Rejection*: Violation of SYSTEM.md. Users are prone to "accepting" AI output without reading closely.

## References
*   [SYSTEM.md Section 5: Rewrite Agent](file:///c:/Users/vikas/Downloads/VerFit/SYSTEM.md)
*   [Common Hallucinations in LLMs](https://arxiv.org/abs/2309.01219)
