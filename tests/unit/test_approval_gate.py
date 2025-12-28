"""
Unit Tests for HITL Approval Gate
Compliance: SYSTEM.md Section 6 (HITL mandatory, diff display, audit logging)
"""

import pytest
from datetime import datetime

from src.services import (
    IApprovalGate,
    SimpleApprovalGate,
    create_approval_gate,
    ApprovalRequest,
    ApprovalStatus,
    ApprovalGateError
)
from src.models.audit import HITLDecision


class TestApprovalGateInterface:
    """Test approval gate interface compliance"""
    
    def test_simple_gate_implements_interface(self):
        """Test that SimpleApprovalGate implements IApprovalGate"""
        gate = SimpleApprovalGate()
        assert isinstance(gate, IApprovalGate)
    
    def test_factory_creates_simple_gate(self):
        """Test factory creates simple gate by default"""
        gate = create_approval_gate()
        assert isinstance(gate, SimpleApprovalGate)
    
    def test_factory_custom_implementation(self):
        """Test factory with custom implementation"""
        class CustomGate:
            def request_approval(self, *args, **kwargs):
                pass
            def approve(self, *args, **kwargs):
                pass
            def reject(self, *args, **kwargs):
                pass
            def get_request(self, *args, **kwargs):
                pass
            def list_pending(self, *args, **kwargs):
                pass
        
        gate = create_approval_gate("custom", cls=CustomGate)
        assert isinstance(gate, CustomGate)


class TestSimpleApprovalGate:
    """Test suite for SimpleApprovalGate"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.gate = SimpleApprovalGate()
        self.user_id = "user_123"
    
    def test_gate_initialization(self):
        """Test gate can be initialized"""
        gate = create_approval_gate()
        assert gate is not None
        assert gate.version == "1.0.0"
    
    def test_request_approval_creates_request(self):
        """Test creating approval request"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old resume text",
            proposed="New resume text",
            user_id=self.user_id
        )
        
        # Should create valid request
        assert isinstance(request, ApprovalRequest)
        assert request.approval_id.startswith("approval_")
        assert request.action_type == "resume_update"
        assert request.status == ApprovalStatus.PENDING
        assert request.user_id == self.user_id
    
    def test_request_approval_creates_diff(self):
        """
        CRITICAL: Test diff generation
        SYSTEM.md Section 6: Show diffs for transparency
        """
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Line 1\nLine 2\nLine 3",
            proposed="Line 1\nModified Line 2\nLine 3",
            user_id=self.user_id
        )
        
        # Should have diff
        assert request.diff_text
        assert len(request.diff_text) > 0
        # Diff should show the change
        assert "Modified" in request.diff_text or "-Line 2" in request.diff_text
    
    def test_approve_creates_audit_log(self):
        """
        CRITICAL: Test audit logging
        SYSTEM.md Section 6: Log all decisions
        """
        # Create request
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old text",
            proposed="New text",
            user_id=self.user_id
        )
        
        # Approve
        decision = self.gate.approve(
            approval_id=request.approval_id,
            user_id=self.user_id,
            notes="Looks good!"
        )
        
        # Should create HITL decision audit log
        assert isinstance(decision, HITLDecision)
        assert decision.user_id == self.user_id
        assert decision.status.value == "approved"  # Use .value for enum
        assert decision.action_type.value == "resume_rewrite"
        assert "Old text" in str(decision.proposed_content)
        assert "New text" in str(decision.proposed_content)
        assert "Looks good!" == decision.decision_notes
    
    def test_reject_creates_audit_log(self):
        """
        CRITICAL: Test rejection logging
        SYSTEM.md Section 6: Log rejections
        """
        # Create request
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old text",
            proposed="New text",
            user_id=self.user_id
        )
        
        # Reject
        decision = self.gate.reject(
            approval_id=request.approval_id,
            user_id=self.user_id,
            reason="Changes too aggressive"
        )
        
        # Should create audit log
        assert isinstance(decision, HITLDecision)
        assert decision.status.value == "rejected"
        assert "Changes too aggressive" in decision.decision_notes
    
    def test_approve_updates_status(self):
        """Test that approval updates request status"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old",
            proposed="New",
            user_id=self.user_id
        )
        
        # Approve
        self.gate.approve(request.approval_id, self.user_id)
        
        # Status should be updated
        updated_request = self.gate.get_request(request.approval_id)
        assert updated_request.status == ApprovalStatus.APPROVED
    
    def test_reject_updates_status(self):
        """Test that rejection updates request status"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old",
            proposed="New",
            user_id=self.user_id
        )
        
        # Reject
        self.gate.reject(request.approval_id, self.user_id, "Not good")
        
        # Status should be updated
        updated_request = self.gate.get_request(request.approval_id)
        assert updated_request.status == ApprovalStatus.REJECTED
    
    def test_cannot_approve_twice(self):
        """Test that can't approve already-approved request"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old",
            proposed="New",
            user_id=self.user_id
        )
        
        # Approve once
        self.gate.approve(request.approval_id, self.user_id)
        
        # Try to approve again - should fail
        with pytest.raises(ValueError) as exc_info:
            self.gate.approve(request.approval_id, self.user_id)
        
        assert "already approved" in str(exc_info.value)
    
    def test_only_owner_can_approve(self):
        """Test authorization - only requester can approve"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old",
            proposed="New",
            user_id="user_123"
        )
        
        # Try to approve as different user - should fail
        with pytest.raises(PermissionError):
            self.gate.approve(request.approval_id, user_id="user_456")
    
    def test_list_pending_approvals(self):
        """Test listing pending approvals for user"""
        # Create multiple requests
        req1 = self.gate.request_approval(
            "resume_update", "Old1", "New1", "user_123"
        )
        req2 = self.gate.request_approval(
            "job_application", "Old2", "New2", "user_123"
        )
        req3 = self.gate.request_approval(
            "resume_update", "Old3", "New3", "user_456"  # Different user
        )
        
        # Approve one
        self.gate.approve(req1.approval_id, "user_123")
        
        # List pending for user_123
        pending = self.gate.list_pending("user_123")
        
        # Should only have req2 (req1 approved, req3 different user)
        assert len(pending) == 1
        assert pending[0].approval_id == req2.approval_id
    
    def test_get_all_decisions(self):
        """Test retrieving all audit logs"""
        # Create and approve request
        request = self.gate.request_approval(
            "resume_update", "Old", "New", "user_123"
        )
        self.gate.approve(request.approval_id, "user_123")
        
        # Get all decisions
        decisions = self.gate.get_all_decisions()
        
        # Should have audit log
        assert len(decisions) == 1
        assert decisions[0].status.value == "approved"
    
    def test_request_with_context(self):
        """Test approval request with additional context"""
        request = self.gate.request_approval(
            action_type="resume_update",
            original="Old",
            proposed="New",
            user_id="user_123",
            context={
                "ai_model": "gemini-2.0",
                "confidence": 0.95,
                "suggestion_type": "title_enhancement"
            }
        )
        
        # Context should be stored
        assert request.context is not None
        assert request.context["ai_model"] == "gemini-2.0"
        assert request.context["confidence"] == 0.95


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
