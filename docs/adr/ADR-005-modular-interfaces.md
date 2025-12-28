# ADR-005: Interface-Based Modular Architecture

**Status**: Accepted  
**Date**: 2025-12-28  
**Deciders**: Product & Engineering Team

---

## Context

Software architecture can be:
1. Monolithic (tightly coupled)
2. Service-oriented (interfaces)
3. Microservices (fully distributed)

**Product Question**: How do we structure code for long-term flexibility and maintainability?

---

## Decision

Use **interface-based modular architecture** with **dependency injection**.

Implementation:
- All services implement Protocol interfaces
- Factory functions for instantiation
- Plug-and-play implementations
- Single Responsibility Principle

---

## Rationale

### Why Interface-Based Design?

1. **Plug-and-Play Upgrades**
   ```python
   # Change implementation without code changes
   gate = create_approval_gate("simple")      # MVP
   gate = create_approval_gate("langgraph")   # Future
   ```

2. **Easy Testing**
   ```python
   # Mock implementations for unit tests
   mock_gate = MockApprovalGate()
   service = RewriteAgent(approval_gate=mock_gate)
   ```

3. **Independent Evolution**
   - Upgrade ApprovalGate without touching RewriteAgent
   - Swap LLM providers without rewriting services
   - Replace storage backends transparently

4. **SYSTEM.md Section 4 Compliance**
   - Single responsibility ✓
   - Independently deployable ✓
   - No hidden dependencies ✓
   - Versioned interfaces ✓

5. **Future-Proof**
   - Today: Simple in-memory implementations
   - Tomorrow: Database-backed, distributed, cloud-native
   - **Zero service code changes**

---

## Architecture Pattern

### Interface Definition

```python
from typing import Protocol

class IApprovalGate(Protocol):
    """Abstract interface - ANY implementation works"""
    
    def request_approval(...) -> ApprovalRequest: ...
    def approve(...) -> HITLDecision: ...
    def reject(...) -> HITLDecision: ...
```

### Multiple Implementations

```python
class SimpleApprovalGate(IApprovalGate):
    """MVP: In-memory storage"""
    
class DatabaseApprovalGate(IApprovalGate):
    """Production: PostgreSQL storage"""
    
class LangGraphApprovalGate(IApprovalGate):
    """Future: Multi-agent workflows"""
```

### Factory Pattern

```python
def create_approval_gate(impl="simple") -> IApprovalGate:
    """Configuration-based instantiation"""
    if impl == "simple":
        return SimpleApprovalGate()
    elif impl == "database":
        return DatabaseApprovalGate(db_url=DB_URL)
    elif impl == "langgraph":
        return LangGraphApprovalGate(graph=...)
```

### Dependency Injection

```python
class RewriteAgent:
    def __init__(self, approval_gate: IApprovalGate):
        self.approval_gate = approval_gate  # ANY implementation!
    
    def suggest_improvements(self, resume):
        # Works with SimpleGate, DatabaseGate, LangGraphGate...
        approval = self.approval_gate.request_approval(...)
```

---

## Consequences

### Positive

✅ **Flexibility**: Swap implementations via config  
✅ **Testability**: Mock interfaces for unit tests  
✅ **Maintainability**: Change one component independently  
✅ **Scalability**: Upgrade storage/logic without rewrites  
✅ **Team Productivity**: Multiple devs work on different implementations  

### Negative

⚠️ **Initial Overhead**: More files, more abstractions  
⚠️ **Learning Curve**: Team must understand interfaces  

### Mitigation

- Clear documentation and examples
- Factory functions hide complexity
- ADRs explain decisions

---

## Alternatives Considered

### Option 1: Monolithic Classes (Rejected)

**Example**:
```python
class ApprovalGate:
    def __init__(self):
        self.storage = {}  # Hardcoded
        self.workflow = "simple"  # Hardcoded
```

**Pros**:
- Simple to start

**Cons**:
- Cannot swap implementations
- Hard to test (no mocks)
- Tight coupling
- **Violates SYSTEM.md Section 4**

**Rejected**: Not maintainable long-term

---

### Option 2: Microservices (Rejected for MVP)

**Pros**:
- Ultimate decoupling
- Independent deployment

**Cons**:
- **Overkill for MVP**
- Network latency
- Deployment complexity
- Debugging harder

**Deferred**: Consider for v2.0 at scale

---

### Option 3: Interface-Based Modularity (CHOSEN)

**Pros**:
- Right-sized for current scale
- Plug-and-play upgrades
- Easy testing
- SYSTEM.md compliant
- Path to microservices if needed

**Cons**:
- Slightly more initial code

**Accepted**: Best balance for MVP with growth path

---

## Implementation Examples

### Services with Interfaces

All VeriFit services follow this pattern:

| Service | Interface | Implementations |
|---------|-----------|-----------------|
| Resume Parser | `IResumeParser` | `ResumeParser` (deterministic), future: `LLMResumeParser` |
| Job Parser | - (internal) | `JobParser` (deterministic + LLM fallback) |
| Approval Gate | `IApprovalGate` | `SimpleApprovalGate`, future: `LangGraphApprovalGate` |
| Job Matcher | - (internal) | `JobMatcher` (deterministic scoring) |

---

## Configuration Management

### Environment-Based

```.env
# Swap implementations via config
APPROVAL_GATE_IMPL=simple          # MVP
# APPROVAL_GATE_IMPL=langgraph     # Future
# APPROVAL_GATE_IMPL=database      # Production

STORAGE_BACKEND=memory             # MVP
# STORAGE_BACKEND=postgresql       # Production
```

### Code Usage

```python
# main.py
from config import APPROVAL_GATE_IMPL

gate = create_approval_gate(APPROVAL_GATE_IMPL)
rewriter = RewriteAgent(approval_gate=gate)

# Zero code changes to swap implementations!
```

---

## Product Impact

### Development Speed

**MVP**: Fast iteration with simple implementations  
**Growth**: Upgrade to production backends without rewrites  
**Scale**: Swap to distributed systems via config

### Team Scalability

- Frontend team: Mocks for testing
- Backend team: Swap storage independently
- ML team: Experiment with different LLMs

### Deployment Flexibility

- Local: In-memory implementations
- Staging: Simple database
- Production: Distributed, cached, optimized

**One codebase, multiple deployment modes**

---

## Success Metrics

- [x] All services use interface pattern
- [x] Factory functions for instantiation
- [x] Zero service-to-service tight coupling
- [x] Can swap implementations via config
- [x] Mock implementations for all tests

---

## Lessons Learned

1. **Interfaces Cost Time Upfront, Save Time Long-Term**
2. **Python Protocol is Perfect for This** (runtime checkable)
3. **Factory Pattern Hides Complexity** from users
4. **SYSTEM.md Section 4** provides excellent guidance

---

## References

- [SYSTEM.md Section 4](../../SYSTEM.md#section-4-modular-architecture)
- [Approval Gate Implementation](../../src/services/approval_gate.py)
- [Factory Pattern Examples](../../src/services/__init__.py)
- [Python Protocol Documentation](https://peps.python.org/pep-0544/)

---

**Review Date**: Quarterly - assess if microservices needed  
**Status**: Monitor coupling - refactor if interfaces violated
