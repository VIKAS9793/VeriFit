# ADR-004: Simple Approval Gates Over LangGraph

**Status**: Accepted  
**Date**: 2025-12-28  
**Deciders**: Product & Engineering Team

---

## Context

We need Human-in-the-Loop (HITL) approval gates per SYSTEM.md Section 6. Research showed LangGraph provides powerful HITL capabilities with `interrupt()`, state persistence, and multi-agent workflows.

**Product Question**: Should we use LangGraph for approval gates or build a simpler solution?

---

## Decision

Use **simple approval gates** for MVP, with LangGraph as a future upgrade path.

Implementation:
- Interface-based design (`IApprovalGate`)
- Simple in-memory implementation (`SimpleApprovalGate`)
- Plug-and-play architecture for future LangGraph integration

---

## Rationale

### Why Simple Gates?

1. **Right-Sized Solution**
   - Current needs: Simple approve/reject for proposed changes
   - No multi-agent workflows yet
   - No dynamic graph modification needed
   - YAGNI principle (You Aren't Gonna Need It)

2. **Faster Delivery**
   - Simple: 8-12 hours implementation
   - LangGraph: 20-30 hours implementation
   - MVP can ship sooner

3. **Easier Testing**
   - Simpler code = easier unit tests
   - No complex graph state management
   - Deterministic behavior

4. **Lower Complexity**
   - 1/3rd the code
   - Fewer dependencies
   - Easier to debug

5. **Still Compliant**
   - Meets all SYSTEM.md Section 6 requirements:
     ✅ Requires human approval
     ✅ Shows diffs
     ✅ Logs all decisions
     ✅ Audit trail

### Why Interface-Based?

Enables future upgrade to LangGraph **without code changes**:
```python
# Today
gate = create_approval_gate("simple")

# Future (just change config!)
gate = create_approval_gate("langgraph")
```

---

## Consequences

### Positive

✅ **Faster MVP**: Ship approval gates in days, not weeks  
✅ **Simpler Codebase**: Easier maintenance  
✅ **Testable**: High test coverage (15/15 tests)  
✅ **Upgradeable**: Can add LangGraph when needed  
✅ **SYSTEM.md Compliant**: Meets all requirements  

### Negative

⚠️ **Limited to Simple Workflows**: No multi-step approvals (yet)  
⚠️ **In-Memory Storage**: Need database for production (planned)  
⚠️ **Manual Scaling**: LangGraph handles complex flows better  

### Neutral

🔄 **Future Work**: Will need LangGraph for:
- Multi-agent resume rewriting with iterations
- Complex application workflows
- Dynamic approval routing

---

## Alternatives Considered

### Option 1: Full LangGraph Implementation

**Pros**:
- Future-proof for complex workflows
- Built-in state management
- Powerful interrupt/resume capabilities

**Cons**:
- Overkill for current needs (simple approve/reject)
- 3x implementation time
- Additional dependency weight
- Harder to test and debug
- **Product Impact**: Delays MVP by 2+ weeks

**Rejected**: Too complex for current requirements

---

### Option 2: No Approval Gates (Auto-Apply)

**Pros**:
- Zero user friction
- Instant changes

**Cons**:
- **Violates SYSTEM.md Section 6**
- No human oversight
- Trust issues
- Legal/ethical concerns

**Rejected**: Non-compliant with requirements

---

### Option 3: Simple Gates (CHOSEN)

**Pros**:
- Right-sized for current needs
- Fast to implement
- Easy to test
- SYSTEM.md compliant
- Upgradeable to LangGraph

**Cons**:
- Limited to simple workflows
- Will need upgrade for complex cases

**Accepted**: Best balance of speed, complexity, and future flexibility

---

## Implementation Details

### Current Architecture

```python
# Interface (stable)
class IApprovalGate(Protocol):
    def request_approval(...) -> ApprovalRequest
    def approve(...) -> HITLDecision
    def reject(...) -> HITLDecision

# Simple Implementation (MVP)
class SimpleApprovalGate(IApprovalGate):
    # In-memory storage
    # Diff generation
    # Audit logging

# Factory (plug-and-play)
def create_approval_gate(implementation="simple"):
    if implementation == "simple":
        return SimpleApprovalGate()
    elif implementation == "langgraph":
        return LangGraphApprovalGate()  # Future
```

### Migration Path

When we need LangGraph:

1. Implement `LangGraphApprovalGate(IApprovalGate)`
2. Change config: `APPROVAL_GATE=langgraph`
3. **Zero service code changes** (interface stays same)

---

## Success Metrics

### MVP Success (Achieved ✅)

- [x] Approval requests created with diffs
- [x] Human approve/reject functionality
- [x] Audit logs for all decisions
- [x] 15/15 unit tests passing
- [x] Interface-based for future upgrades

### Future Success (When Needed)

- [ ] Multi-step approval workflows
- [ ] Complex agent pipelines
- [ ] Dynamic approval routing
- [ ] Parallel approval tracks

---

## Product Impact

### User Experience

**Today**:
1. User sees proposed change
2. User sees visual diff
3. User approves or rejects
4. System applies or discards change

**Complexity**: Low (good for MVP)  
**User Friction**: Minimal (one-click approve/reject)

### Time to Market

- **Simple Gates**: 8-12 hours → Ship in days
- **LangGraph**: 20-30 hours → Ship in weeks

**Decision**: Ship faster with simple gates, upgrade later if needed

---

## Lessons Learned

1. **YAGNI is Real**: Build what you need now, not what you might need
2. **Interfaces Enable Evolution**: Abstract early, swap implementations later
3. **Research Everything**: LangGraph is powerful, but not always necessary
4. **Product > Tech**: Choose solutions based on business needs, not tech coolness

---

## References

- [LangGraph HITL Documentation](https://langchain.com/docs/langgraph)
- [SYSTEM.md Section 6](../../SYSTEM.md#section-6-human-in-the-loop)
- [Implementation Plan](../implementation_plan.md)
- [Test Suite](../../tests/unit/test_approval_gate.py)

---

**Review Date**: When implementing Rewrite Agent (Phase 9)  
**Status**: Monitor complexity - upgrade to LangGraph if simple gates become limiting
