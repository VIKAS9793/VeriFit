"""
Audit and HITL Data Models
Pydantic models for audit logging and human-in-the-loop decisions
Compliance: SYSTEM.md Section 6 (Human-in-the-Loop - Must pause, show diff, require approval, be logged)
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class HITLAction(str, Enum):
    """Types of actions requiring human approval"""
    RESUME_REWRITE = "resume_rewrite"
    SKILL_ADDITION = "skill_addition"
    EXPERIENCE_MODIFICATION = "experience_modification"
    CONTENT_GENERATION = "content_generation"


class HITLStatus(str, Enum):
    """Status of HITL decision"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AuditEventType(str, Enum):
    """Types of auditable events"""
    RESUME_UPLOADED = "resume_uploaded"
    RESUME_PARSED = "resume_parsed"
    SCORE_CALCULATED = "score_calculated"
    JOB_MATCHED = "job_matched"
    HITL_REQUESTED = "hitl_requested"
    HITL_DECIDED = "hitl_decided"
    DATA_DELETED = "data_deleted"
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"


class HITLDecision(BaseModel):
    """
    Human-in-the-loop decision record
    
    Principles (SYSTEM.md Section 6):
    - Must pause workflow
    - Must show diff
    - Must require explicit approval
    - Must be logged
    """
    
    # Decision identity
    decision_id: str = Field(..., description="Unique decision identifier")
    action_type: HITLAction = Field(..., description="Type of action requiring approval")
    status: HITLStatus = Field(HITLStatus.PENDING, description="Decision status")
    
    # Context
    user_id: str = Field(..., description="User who needs to approve")
    entity_id: str = Field(..., description="ID of entity being modified (resume, etc.)")
    
    # The change being proposed
    original_content: Optional[Dict[str, Any]] = Field(None, description="Original content")
    proposed_content: Dict[str, Any] = Field(..., description="Proposed changes")
    diff: str = Field(..., description="Human-readable diff")
    
    # Justification
    reason: str = Field(..., description="Why this change is proposed")
    generated_by: str = Field(..., description="System/agent that generated proposal")
    
    # Decision details
    decided_at: Optional[datetime] = Field(None, description="When decision was made")
    decision_notes: Optional[str] = Field(None, description="User's notes on decision")
    
    # Timestamps (for audit)
    requested_at: datetime = Field(..., description="When approval was requested")
    expires_at: Optional[datetime] = Field(None, description="When request expires")
    
    def approve(self, notes: Optional[str] = None) -> "HITLDecision":
        """Approve the proposed change"""
        self.status = HITLStatus.APPROVED
        self.decided_at = datetime.utcnow()
        self.decision_notes = notes
        return self
    
    def reject(self, notes: Optional[str] = None) -> "HITLDecision":
        """Reject the proposed change"""
        self.status = HITLStatus.REJECTED
        self.decided_at = datetime.utcnow()
        self.decision_notes = notes
        return self
    
    def is_expired(self) -> bool:
        """Check if decision request has expired"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = HITLStatus.EXPIRED
            return True
        return False
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "decision_id": "hitl-abc123",
            "action_type": "resume_rewrite",
            "status": "pending",
            "user_id": "user-xyz789",
            "entity_id": "resume-abc123",
            "proposed_content": {
                "section": "experience",
                "new_text": "Led development of ML pipeline"
            },
            "diff": "- Led ML pipeline project\\n+ Led development of ML pipeline",
            "reason": "Improved clarity and ATS keyword matching",
            "generated_by": "rewrite_agent_v1",
            "requested_at": "2025-12-28T10:00:00Z"
        }
    })


class AuditLog(BaseModel):
    """
    Complete audit log entry
    
    Principles (SYSTEM.md Section 0):
    - Every decision is auditable
    - Full decision logs (Section 5: Governance & Audit Agent)
    """
    
    # Log entry identity
    log_id: str = Field(..., description="Unique log entry identifier")
    event_type: AuditEventType = Field(..., description="Type of auditable event")
    timestamp: datetime = Field(..., description="When event occurred")
    
    # Actor (who performed action)
    user_id: Optional[str] = Field(None, description="User ID if user-initiated")
    agent_id: Optional[str] = Field(None, description="Agent ID if agent-initiated")
    system_component: str = Field(..., description="System component that logged event")
    
    # Event details
    entity_type: str = Field(..., description="Type of entity (resume, job, score)")
    entity_id: str = Field(..., description="Entity identifier")
    action: str = Field(..., description="Action performed")
    
    # Data (what changed)
    before_state: Optional[Dict[str, Any]] = Field(None, description="State before action")
    after_state: Optional[Dict[str, Any]] = Field(None, description="State after action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    # Privacy and compliance (SYSTEM.md Section 7)
    contains_pii: bool = Field(False, description="Whether log contains PII")
    consent_verified: bool = Field(True, description="User consent verified")
    
    # HITL reference (if applicable)
    hitl_decision_id: Optional[str] = Field(None, description="Related HITL decision ID")
    
    model_config = ConfigDict(frozen=True, json_schema_extra={
        "example": {
            "log_id": "log-xyz789",
            "event_type": "resume_parsed",
            "timestamp": "2025-12-28T10:00:00Z",
            "user_id": "user-abc123",
            "system_component": "resume_parser_v1",
            "entity_type": "resume",
            "entity_id": "resume-abc123",
            "action": "parsed_resume",
            "metadata": {
                "parser_version": "1.0.0",
                "file_format": "pdf",
                "confidence": 0.95
            },
            "contains_pii": True,
            "consent_verified": True
        }
    })


class BiasCheckResult(BaseModel):
    """
    Bias detection result
    Compliance: SYSTEM.md Section 5 (Governance & Audit Agent - Bias checks)
    """
    
    check_id: str = Field(..., description="Unique check identifier")
    checked_at: datetime = Field(..., description="When bias check was performed")
    entity_type: str = Field(..., description="What was checked (resume, job, score)")
    entity_id: str = Field(..., description="Entity identifier")
    
    # Bias detection results
    bias_detected: bool = Field(False, description="Whether bias was detected")
    bias_categories: List[str] = Field(
        default_factory=list,
        description="Categories of bias detected (age, gender, race, etc.)"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    
    # Details
    flagged_content: List[str] = Field(
        default_factory=list,
        description="Specific content flagged"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations to mitigate bias"
    )
    
    # Compliance
    checker_version: str = Field("1.0.0", description="Bias checker version")
    
    model_config = ConfigDict(frozen=True)
