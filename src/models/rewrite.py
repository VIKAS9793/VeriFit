"""
Rewrite Models
Data models for resume improvement suggestions
Compliance: SYSTEM.md Section 5 (Diff-only suggestions, HITL mandatory, No new claims)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level for hallucination"""
    LOW = "low"          # Safe improvements (verb strengthening)
    MEDIUM = "medium"    # Needs review (keyword additions)
    HIGH = "high"        # High risk (major rewriting)


class RewriteSuggestion(BaseModel):
    """
    Single resume improvement suggestion
    
    SYSTEM.md Section 5 compliance:
    - Diff-only (shows original vs suggested)
    - No new claims (validated)
    - HITL mandatory (requires approval)
    """
    suggestion_id: str = Field(..., description="Unique suggestion ID")
    section: str = Field(..., description="Resume section (experience, skills, etc.)")
    subsection: Optional[str] = Field(None, description="Specific subsection (job title, etc.)")
    
    # The change
    original_text: str = Field(..., description="Original text")
    suggested_text: str = Field(..., description="Improved text")
    diff: str = Field(..., description="Visual diff")
    
    # Context
    reason: str = Field(..., description="Why this improvement helps")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM confidence (0-1)")
    
    # Transparency
    keywords_added: List[str] = Field(default_factory=list, description="Keywords added for ATS")
    action_verbs_strengthened: List[str] = Field(default_factory=list, description="Verbs improved")
    metrics_added: Dict[str, str] = Field(default_factory=dict, description="Metrics (may be placeholders)")
    
    # Safety flags
    requires_user_input: bool = Field(False, description="Has placeholders needing input")
    placeholders: List[str] = Field(default_factory=list, description="Placeholders like [X%]")
    risk_level: RiskLevel = Field(RiskLevel.LOW, description="Hallucination risk")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    applied: bool = Field(False, description="Whether user approved and applied")


class ValidationResult(BaseModel):
    """
    Result of hallucination validation
    
    SYSTEM.md Section 5: No new claims
    """
    valid: bool = Field(..., description="Whether suggestion is valid")
    reason: Optional[str] = Field(None, description="Why invalid (if not valid)")
    
    # Detected issues
    hallucinated_entities: List[str] = Field(default_factory=list, description="New entities not in resume")
    requires_user_input: bool = Field(False, description="Has placeholders")
    placeholders: List[str] = Field(default_factory=list, description="Found placeholders")
    
    # Risk assessment
    risk_level: RiskLevel = Field(RiskLevel.LOW, description="Overall risk")
    confidence: float = Field(1.0, description="Validation confidence")


class RewriteOptions(BaseModel):
    """
    Options for resume rewriting
    """
    target_job: Optional[str] = Field(None, description="Job title to target")
    job_keywords: List[str] = Field(default_factory=list, description="Keywords from job description")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to improve (experience, skills)")
    max_suggestions: int = Field(5, description="Maximum suggestions to generate")
    min_confidence: float = Field(0.6, ge=0.0, le=1.0, description="Min confidence threshold")
    include_placeholders: bool = Field(True, description="Allow placeholders for unknown metrics")


class RewriteSession(BaseModel):
    """
    Resume rewrite session tracking
    """
    session_id: str
    user_id: str
    resume_id: str
    suggestions: List[RewriteSuggestion]
    options: RewriteOptions
    started_at: datetime
    completed_at: Optional[datetime] = None
    approved_count: int = 0
    rejected_count: int = 0
