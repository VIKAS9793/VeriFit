# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records documenting key technical and product decisions made during VeriFit development.

## Format

Each ADR follows this structure:
- **Title**: Short descriptive name
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What problem are we solving?
- **Decision**: What did we decide?
- **Rationale**: Why this choice?
- **Consequences**: What are the trade-offs?
- **Alternatives Considered**: What else did we explore?

## Index

1. [ADR-001: Deterministic Resume Parsing Over Pure AI](ADR-001-deterministic-parsing.md)
2. [ADR-002: No False ATS Score Claims](ADR-002-no-ats-claims.md)
3. [ADR-003: Manual Job Copy-Paste Over Web Scraping](ADR-003-manual-job-input.md)
4. [ADR-004: Simple Approval Gates Over LangGraph](ADR-004-simple-hitl.md)
5. [ADR-005: Interface-Based Modular Architecture](ADR-005-modular-interfaces.md)
6. [ADR-006: Anti-Hallucination & Evals Strategy](ADR-006-anti-hallucination-strategy.md)

## Quick Reference

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Deterministic parsing first | Explainability, debugging | Higher accuracy on standard cases |
| No ATS score prediction | Honesty (no standard exists) | Trust, legal safety |
| Manual job input | Legal compliance | User friction, but legal |
| Simple HITL gates | Right-sized solution | Faster delivery, upgradeable |
| Interface-based design | Plug-and-play future | Easy to swap implementations |
| Anti-hallucination strategy | Safety first, prevent false claims | Zero fabricated skills |
