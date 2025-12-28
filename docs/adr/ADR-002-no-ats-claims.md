# ADR-002: No False ATS Score Claims

**Status**: Accepted  
**Date**: 2025-12-28  
**Deciders**: Product & Engineering Team

---

## Context

Many resume tools claim to predict "ATS scores" or "ATS pass rates":
- "Your resume scores 87/100 on ATS systems"
- "92% chance of passing ATS screening"

**Problem**: There is **NO industry standard** for ATS scoring.

**Product Question**: Should we claim to predict ATS scores?

---

## Decision

**NO** - We will NOT claim to predict ATS scores.

Instead:
- Analyze **evidence-based ATS-friendly factors**
- Provide **honest assessment** of compliance
- **Never claim** a numeric score or pass/fail prediction

---

## Rationale

### Why NO ATS Score Prediction?

1. **Truth Over Hype (SYSTEM.md Section 0)**
   - No verifiable ATS scoring standard exists
   - Each ATS uses different algorithms
   - Claiming accuracy is misleading

2. **Legal Risk**
   - False advertising if claims are unverifiable
   - User reliance on false scores = legal liability
   - Competitors sued for false ATS claims

3. **Ethical Concerns**
   - Users make career decisions based on scores
   - False confidence harms job seekers
   - Honest assessment builds trust

4. **Technical Reality**
   - We can't access real ATS systems
   - Can't validate our predictions
   - Would be pure speculation

### What We CAN Do Honestly

✅ **Format Analysis**: "Uses ATS-friendly format (no tables)"  
✅ **Keyword Detection**: "Contains 8/10 key terms from job description"  
✅ **Readability**: "Clear section headers detected"  
✅ **Evidence-Based**: Every claim backed by research

❌ **NO**: "ATS Score: 87/100"  
❌ **NO**: "92% pass rate"  
❌ **NO**: "Guaranteed to pass screening"

---

## Consequences

### Positive

✅ **Honest**: No false claims (SYSTEM.md compliance)  
✅ **Legal Safety**: No false advertising risk  
✅ **User Trust**: Transparency builds long-term trust  
✅ **Differentiation**: Honesty in dishonest market  

### Negative

⚠️ **Marketing Challenge**: "ATS score" sells better than "ATS analysis"  
⚠️ **User Expectation**: Users want simple numeric scores  

### Mitigation

- Educate users on ATS reality
- Provide actionable feedback instead of scores
- Position as "honest alternative"

---

## Alternatives Considered

### Option 1: Claim ATS Score (Rejected)

**Pros**:
- Marketing appeal
- Competitive parity

**Cons**:
- **Violates SYSTEM.md Section 0** (Truth over Hype)
- Legal risk
- Unverifiable claims
- Erodes trust when users discover truth

**Rejected**: Fundamentally dishonest

---

### Option 2: "Estimated" ATS Score (Rejected)

**Pros**:
- Caveat disclosure ("estimated")
- User wants numbers

**Cons**:
- Still misleading (no estimation basis)
- Caveat ignored by users
- Legal risk remains

**Rejected**: Lipstick on a pig

---

### Option 3: Evidence-Based Analysis (CHOSEN)

**Pros**:
- Honest and verifiable
- Legally defensible
- Builds trust
- Actionable feedback

**Cons**:
- Less marketable initially
- Requires user education

**Accepted**: Aligns with core values

---

## Implementation

### What We Show Users

```
ATS-Friendly Analysis:
✓ Format: Plain text (good)
✓ Sections: Clear headers detected
✓ Keywords: 8/10 job terms found
⚠ Contact: Missing LinkedIn URL

Evidence:
- Format check: No tables or images detected
- Keyword analysis: Matched "Python", "Docker", "AWS"...
- Missing: "Kubernetes" mentioned in job description
```

### What We DON'T Show

```
❌ ATS Score: 87/100
❌ Pass Probability: 92%
❌ Guaranteed to pass ATS
```

---

## Product Impact

### User Experience

**Short-term**:
- Confusion: "Where's my score?"
- Education needed

**Long-term**:
- Trust: "They don't BS me"
- Loyalty: Honest brand
- Word-of-mouth: "Actually honest resume tool"

### Market Position

**Differentiation**:
- Only honest ATS tool
- Truth-focused brand
- Appeals to skeptical users

**Risk**:
- Lower initial conversion (mitigated by education)

---

## Success Metrics

- [x] Zero false ATS score claims
- [x] All analysis backed by evidence
- [x] User feedback mentions "honest" / "trustworthy"
- [x] Critical test: `test_no_false_claims` passing

---

## References

- [Research: No ATS Standard Exists](https://www.jobscan.co/blog/ats-myths/)
- [Resume Analyzer Implementation](../../src/services/resume_analyzer.py)
- [Critical Test](../../tests/unit/test_resume_analyzer.py#L142)
- [SYSTEM.md Section 0](../../SYSTEM.md#section-0-core-principles)

---

**Review Date**: Quarterly - monitor competitor claims and legal landscape  
**Status**: Non-negotiable - honesty is core value
