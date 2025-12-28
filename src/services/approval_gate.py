"""
HITL Approval Gate
Human-in-the-Loop approval system with modular architecture
Compliance: SYSTEM.md Section 6 (Mandatory human approval, diff display, audit logging)

Architecture: Interface-based for plug-and-play implementations
- IApprovalGate: Abstract interface
- SimpleApprovalGate: In-memory implementation (MVP)
- LangGraphApprovalGate: Future slot for complex workflows

What this DOES:
- Request human approval for AI-proposed changes
- Display visual diffs of modifications
- Log all approval/rejection decisions
- Provide audit trail

What this DOES NOT do:
- Auto-approve (human approval is MANDATORY)
- Hide changes (full transparency)
- Skip audit logging
"""

from typing import Protocol, Optional, Dict, Any, List, runtime_checkable
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import uuid

from src.models.audit import HITLDecision


class ApprovalStatus(str, Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRequest(BaseModel):
    """
    Approval request model
    
    Represents a pending approval with all context
    """
    approval_id: str
    action_type: str  # "resume_update", "job_application", etc.
    original_content: str
    proposed_content: str
    diff_text: str  # Plain text diff
    diff_html: Optional[str] = None  # HTML diff (optional)
    user_id: str
    requested_at: datetime
    status: ApprovalStatus
    context: Optional[Dict[str, Any]] = None


@runtime_checkable
class IApprovalGate(Protocol):
    """
    Approval gate interface
    
    ANY implementation must provide these methods.
    Allows plug-and-play architecture:
    - SimpleApprovalGate (in-memory)
    - LangGraphApprovalGate (future)
    - DatabaseApprovalGate (custom)
    - MockApprovalGate (testing)
    """
    
    @abstractmethod
    def request_approval(
        self,
        action_type: str,
        original: str,
        proposed: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Request human approval for a proposed change
        
        Args:
            action_type: Type of action ("resume_update", etc.)
            original: Original content
            proposed: Proposed changes
            user_id: User who needs to approve
            context: Additional context
            
        Returns:
            Approval request with unique ID and diff
        """
        ...
    
    @abstractmethod
    def approve(
        self,
        approval_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> HITLDecision:
        """
        Approve a request
        
        Args:
            approval_id: Approval request ID
            user_id: User approving
            notes: Optional approval notes
            
        Returns:
            HITL decision audit log
        """
        ...
    
    @abstractmethod
    def reject(
        self,
        approval_id: str,
        user_id: str,
        reason: str
    ) -> HITLDecision:
        """
        Reject a request
        
        Args:
            approval_id: Approval request ID
            user_id: User rejecting
            reason: Rejection reason (required)
            
        Returns:
            HITL decision audit log
        """
        ...
    
    @abstractmethod
    def get_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        ...
    
    @abstractmethod
    def list_pending(self, user_id: str) -> List[ApprovalRequest]:
        """List pending approvals for user"""
        ...


class SimpleApprovalGate:
    """
    Simple in-memory approval gate
    
    Implementation: IApprovalGate
    Storage: In-memory dictionaries
    Use case: MVP, testing, single-user applications
    
    SYSTEM.md Section 6:
    - ✅ HITL mandatory
    - ✅ Show diffs
    - ✅ Log all decisions
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._requests: Dict[str, ApprovalRequest] = {}
        self._decisions: List[HITLDecision] = []
        self.version = "1.0.0"
    
    def request_approval(
        self,
        action_type: str,
        original: str,
        proposed: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Create approval request with diff
        
        SYSTEM.md Section 6: Show diffs for transparency
        """
        # Generate unique ID
        approval_id = f"approval_{uuid.uuid4().hex[:12]}"
        
        # Create diffs
        from src.utils.diff import create_text_diff
        diff_text = create_text_diff(original, proposed)
        
        # Create request
        request = ApprovalRequest(
            approval_id=approval_id,
            action_type=action_type,
            original_content=original,
            proposed_content=proposed,
            diff_text=diff_text,
            user_id=user_id,
            requested_at=datetime.now(),
            status=ApprovalStatus.PENDING,
            context=context
        )
        
        # Store request
        self._requests[approval_id] = request
        
        return request
    
    def approve(
        self,
        approval_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> HITLDecision:
        """
        Approve request and create audit log
        
        SYSTEM.md Section 6: Log all decisions
        """
        request = self._get_request_or_error(approval_id)
        
        # Verify ownership
        if request.user_id != user_id:
            raise PermissionError(
                f"User {user_id} cannot approve request owned by {request.user_id}"
            )
        
        # Check if already decided
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Request already {request.status.value}")
        
        # Update status
        request.status = ApprovalStatus.APPROVED
        self._requests[approval_id] = request
        
        # Create audit log
        from src.models.audit import HITLAction, HITLStatus
        
        decision = HITLDecision(
            decision_id=f"decision_{uuid.uuid4().hex[:12]}",
            action_type=HITLAction.RESUME_REWRITE,  # Use enum
            status=HITLStatus.APPROVED,
            user_id=user_id,
            entity_id=request.approval_id,
            proposed_content={"original": request.original_content[:200], "proposed": request.proposed_content[:200]},
            diff=request.diff_text[:500] if request.diff_text else "",
            reason=notes or f"Approved {request.action_type}",
            generated_by="approval_gate",
            requested_at=request.requested_at,
            decided_at=datetime.now(),
            decision_notes=notes
        )
        
        # Store decision
        self._decisions.append(decision)
        
        return decision
    
    def reject(
        self,
        approval_id: str,
        user_id: str,
        reason: str
    ) -> HITLDecision:
        """
        Reject request and create audit log
        
        SYSTEM.md Section 6: Log rejections
        """
        request = self._get_request_or_error(approval_id)
        
        # Verify ownership
        if request.user_id != user_id:
            raise PermissionError(
                f"User {user_id} cannot reject request owned by {request.user_id}"
            )
        
        # Check if already decided
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Request already {request.status.value}")
        
        # Update status
        request.status = ApprovalStatus.REJECTED
        self._requests[approval_id] = request
        
        # Create audit log with rejection reason
        from src.models.audit import HITLAction, HITLStatus
        
        decision = HITLDecision(
            decision_id=f"decision_{uuid.uuid4().hex[:12]}",
            action_type=HITLAction.RESUME_REWRITE,  # Use enum
            status=HITLStatus.REJECTED,
            user_id=user_id,
            entity_id=request.approval_id,
            proposed_content={"original": request.original_content[:200], "proposed": request.proposed_content[:200]},
            diff=request.diff_text[:500] if request.diff_text else "",
            reason=f"Rejected: {reason}",
            generated_by="approval_gate",
            requested_at=request.requested_at,
            decided_at=datetime.now(),
            decision_notes=reason
        )
        
        # Store decision
        self._decisions.append(decision)
        
        return decision
    
    def get_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        return self._requests.get(approval_id)
    
    def list_pending(self, user_id: str) -> List[ApprovalRequest]:
        """List pending approvals for user"""
        return [
            req for req in self._requests.values()
            if req.user_id == user_id and req.status == ApprovalStatus.PENDING
        ]
    
    def get_all_decisions(self) -> List[HITLDecision]:
        """Get all audit logs (for testing/review)"""
        return self._decisions.copy()
    
    def _get_request_or_error(self, approval_id: str) -> ApprovalRequest:
        """Get request or raise error"""
        request = self._requests.get(approval_id)
        if not request:
            raise ValueError(f"Approval request not found: {approval_id}")
        return request


# Approval gate errors
class ApprovalGateError(Exception):
    """Base approval gate error"""
    pass


# Factory function for plug-and-play
def create_approval_gate(
    implementation: str = "simple",
    **kwargs
) -> IApprovalGate:
    """
    Factory: Create approval gate instance
    
    Plug-and-play architecture:
    - Change implementation without code changes
    - Swap via configuration
    - Easy testing with mocks
    
    Args:
        implementation: "simple", "langgraph" (future), or "custom"
        **kwargs: Implementation-specific configuration
        
    Returns:
        Approval gate instance implementing IApprovalGate
        
    Examples:
        # Simple (default - MVP)
        gate = create_approval_gate()
        
        # LangGraph (future)
        gate = create_approval_gate("langgraph", graph=my_graph)
        
        # Custom user implementation
        gate = create_approval_gate("custom", cls=MyApprovalGate)
    """
    if implementation == "simple":
        return SimpleApprovalGate(**kwargs)
    elif implementation == "langgraph":
        # Future: Import and create LangGraphApprovalGate
        raise NotImplementedError(
            "LangGraph implementation not yet available. "
            "Coming in future release!"
        )
    elif implementation == "custom":
        cls = kwargs.pop("cls", None)
        if not cls:
            raise ValueError("Custom implementation requires 'cls' parameter")
        return cls(**kwargs)
    else:
        raise ValueError(
            f"Unknown implementation: {implementation}. "
            f"Use 'simple', 'langgraph', or 'custom'"
        )
