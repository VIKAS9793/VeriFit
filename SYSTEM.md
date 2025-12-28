# VeriFit
**Evidence-Based ATS Compliance & Job Matching Intelligence**

## Project Description

VeriFit is a governance-first, evidence-based system designed to evaluate resumes for ATS compliance, role fit, and job alignment **without exaggeration, hallucination, or opaque scoring**.

Unlike traditional resume "optimizers," VeriFit operates as a **truth mirror**:

- It scores resumes using **deterministic, explainable criteria**
- It matches candidates only with **real, active job roles**
- It enforces **human-in-the-loop approvals** for any generative change
- It prioritizes **fairness, auditability, and regulatory compliance**

VeriFit is built for candidates, recruiters, and enterprises that value **accuracy over hype** and **trust over vanity metrics**.

---

## 0. SYSTEM INTENT (NON-NEGOTIABLE)

This system exists to:

- Perform **truthful, evidence-based resume analysis**
- Produce **deterministic ATS compliance scoring**
- Identify **real, active job matches** using verifiable criteria
- **Explicitly refuse hallucination, exaggeration, or inference**
- Be **auditable, fair, privacy-preserving, and compliant**
- Operate with **human-in-the-loop (HITL) gates** for any generative action

The system **must never**:

- Invent metrics, roles, skills, or experience
- Optimize resumes for deception
- Produce opaque or unexplainable scores
- Claim to replicate proprietary ATS systems

**Truth, restraint, and explainability override convenience.**

---

## 1. TECHNOLOGY SELECTION PRINCIPLE (MANDATORY)

### 1.1 Research-First Rule

Before selecting any framework, library, or version, the system builder **must**:

1. Visit the **official documentation**
2. Review:
   - Latest stable release
   - Deprecation notices
   - API guarantees
   - Backward compatibility
3. Compare **at least one alternative**
4. Document **tradeoffs and rationale**

**No implementation may proceed without this step.**

---

## 2. CHOSEN ARCHITECTURAL DIRECTION

### Core Orchestration
**LangGraph + LangChain (HITL)**
- Deterministic flow control
- Interruptible execution
- Explicit approval gates
- Audit-friendly state transitions

### UI
**React** (initial)
- Optional: A2UI after doc-verified maturity check

### Automation
**n8n** for ingestion, scheduling, notifications
- **Never** for scoring or reasoning

### Development Tooling
- **Cursor / Windsurf** for implementation
- **Antigravity** for agent-driven assembly
- **Jules** for optional repo hygiene

---

## 3. RESEARCH FOUNDATIONS (BRAIN)

Grounded in:

- Resume parsing & IE (ACL / EMNLP)
- Semantic similarity (Sentence-BERT, WMD)
- Fairness in ML (Barocas et al.)
- Explainability (LIME, Interpretability in ML)
- Governance (NIST AI RMF, OECD AI Principles, DPDP Act)

**Research constrains design; it does not decorate it.**

---

## 4. MODULAR SYSTEM ARCHITECTURE

```
[ UI ]
  |
[ UI ]
  |
[ Security Gateway (Sanitization) ]
  |
[ Ingestion Service ]
  |
[ Resume Parsing Service ]
  |
[ Resume Normalization Service ]
  |
[ Deterministic Scoring Engine ]
  |
[ Explanation Agent ]
  |
[ Job Matching Engine ]
  |
[ HITL Approval Gate ]
```

Each module:

- Single responsibility
- Independently deployable
- Versioned interfaces
- No hidden dependencies

---

## 5. AGENT PERSONAS (ANTIGRAVITY)

### System Architect Agent
- Builds only from this document
- Researches official docs before version choice
- Refactors if incompatibilities exist
- Refuses undocumented assumptions

### Resume Parser Agent
- Deterministic first
- LLM only for edge cases
- Verbatim extraction

### Resume Normalizer Agent
- Structural normalization only
- No semantic edits

### Deterministic Scoring Engine
- No LLMs
- Evidence-backed scoring only

### Explanation Agent
- Read-only
- Evidence-citing
- No score modification

### Job Ingestion Agent
- ≤7-day active roles only
- Verified sources only

### Job Matching Agent
- Multi-factor explainable fit
- No opaque ranking

### Rewrite Agent
- Diff-only suggestions
- HITL mandatory
- No new claims

### Governance & Audit Agent
- Bias checks
- Consent verification
- Full decision logs

---

## 6. HUMAN-IN-THE-LOOP

All generative or modifying actions:

- Must **pause**
- Must **show diff**
- Must **require approval**
- Must be **logged**

---

## 7. PRIVACY & COMPLIANCE

- **Consent-first** ingestion
- **Data minimization**
- **User-initiated deletion**
- **Encryption** at rest and transit
- **Input Sanitization** (polyglot/injection protection)
- **No training on user data**

**DPDP compliance is mandatory.**

---

## 8. EVALUATION & EVALS

- Parsing accuracy
- Score determinism
- Rewrite faithfulness
- Bias regression tests
- Trust audits

---

## 9. ENGINEERING STANDARDS

- Python 3.11+
- PEP8 + type hints
- Docstrings mandatory
- SOLID / DRY / KISS / YAGNI
- Dependency Injection
- No monoliths

---

## 10. SUCCESS CRITERIA

VeriFit is successful if:

- Users **trust it** even when feedback is negative
- It **refuses more often** than it hallucinates
- **Every decision is auditable**
- Recruiters find outputs **fair and grounded**

---

**END OF SYSTEM.md**
