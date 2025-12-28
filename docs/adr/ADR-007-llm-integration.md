# ADR-007: LLM Integration Strategy (Gemini 2.5 Flash Lite)

## Status
ACCEPTED

## Context
VeriFit requires intelligent Resume Parsing and Analysis capabilities.
Initial attempts with Regex (Parsing) and Heuristics (Analysis) failed on complex/polished resumes, leading to "Empty Skills" and "Generic Scoring".
We needed an LLM solution that balances:
1.  **Intelligence**: Ability to understand layout and context.
2.  **Cost**: Free/Low cost for MVP.
3.  **Speed**: Low latency for user experience.

## Decision
We selected **Google Gemini 2.5 Flash Lite** as the core intelligence engine.

### Implementation Details:
1.  **Model**: `gemini-2.5-flash-lite` (Chosen for speed/cost balance).
2.  **Library**: `google-genai>=1.0.0` (New SDK, migrated Dec 2025).
3.  **Rate Limiting Strategy**:
    -   Constraint: Free Tier limit is 15 RPM (Requests Per Minute).
    -   Implementation: Proactive `sleep(7.0)` delay before each request.
    -   Safety: Enforces ~8.5 RPM, providing a safe buffer against bursts.
    -   Retry Logic: `tenacity` library used for exponential backoff on 429/500 errors.

4.  **Parsing Strategy**:
    -   **LLM-First**: Parser attempts to use LLM to extract JSON.
    -   **Fallback**: If LLM fails (API error, rate limit), falls back to Regex.

5.  **Analysis Strategy**:
    -   **Evidence-Based**: LLM Prompt requires strict `Evidence` object structure.
    -   **Truth-Over-Hype**: Prompt engineered to penalize vague claims.

## Consequences
### Positive
-   **High Accuracy**: "Polished" resumes now yield full skill lists.
-   **Real Feedback**: Users get specific, content-aware advice.
-   **Zero Cost**: Runs entirely on Free Tier.

### Negative
-   **Latency**: The 7s delay per request adds friction (Total analysis time ~15s).
-   **Dependency**: Strict reliance on Google API availability.
-   **Schema Fragility**: LLM JSON output must perfectly match Pydantic models (required strict prompting).
