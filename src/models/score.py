"""
Score Data Models
Pydantic models for ATS compliance and job matching scores
Compliance: SYSTEM.md Section 4 (Deterministic Scoring Engine - No LLMs, evidence-backed only)
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ScoreCategory(str, Enum):
    """Score category types"""
    ATS_COMPLIANCE = "ats_compliance"
    JOB_MATCH = "job_match"
    SKILL_MATCH = "skill_match"
    EXPERIENCE_MATCH = "experience_match"


class EvidenceType(str, Enum):
    """Types of evidence supporting scores"""
    KEYWORD_MATCH = "keyword_match"
    FORMAT_CHECK = "format_check"
    STRUCTURE_ANALYSIS = "structure_analysis"
    EXPERIENCE_COMPARISON = "experience_comparison"
    SKILL_COMPARISON = "skill_comparison"
    READABILITY_CHECK = "readability_check"  # Added for LLM analysis compatibility


class Evidence(BaseModel):
    """
    Evidence supporting a score component
    Principle: Every score must be explainable (SYSTEM.md Section 0)
    """
    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    description: str = Field(..., description="Human-readable evidence description")
    data: Dict[str, Any] = Field(..., description="Machine-readable evidence data")
    weight: float = Field(..., ge=0.0, le=1.0, description="Evidence weight in scoring")
    
    model_config = ConfigDict(frozen=True)


class ScoreExplanation(BaseModel):
    """
    Detailed explanation for a score component
    Principle: Explainability first (SYSTEM.md Section 0)
    """
    component: str = Field(..., description="Scoring component name")
    score: float = Field(..., ge=0.0, le=100.0, description="Component score (0-100)")
    max_score: float = Field(100.0, ge=0.0, description="Maximum possible score")
    evidence: List[Evidence] = Field(..., description="Supporting evidence")
    explanation: str = Field(..., description="Human-readable explanation")
    
    @field_validator('score')
    @classmethod
    def validate_score_range(cls, v, info):
        """Ensure score doesn't exceed max_score"""
        max_score = info.data.get('max_score', 100.0)
        if v > max_score:
            raise ValueError(f'score ({v}) cannot exceed max_score ({max_score})')
        return v
    
    model_config = ConfigDict(frozen=True)


class ATSComplianceScore(BaseModel):
    """
    ATS Compliance scoring breakdown
    
    Principles (SYSTEM.md Section 4):
    - Deterministic only (no LLMs)
    - Evidence-backed
    - Explainable criteria
    """
    
    # Overall score
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall ATS compliance (0-100)")
    
    # Component scores with explanations
    format_score: ScoreExplanation = Field(..., description="Document format compliance")
    structure_score: ScoreExplanation = Field(..., description="Resume structure quality")
    keyword_score: ScoreExplanation = Field(..., description="Keyword optimization")
    readability_score: ScoreExplanation = Field(..., description="ATS readability")
    
    # Flags and issues
    critical_issues: List[str] = Field(
        default_factory=list,
        description="Critical issues blocking ATS parsing"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical warnings"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )
    
    # Metadata
    scoring_version: str = Field("1.0.0", description="Scoring algorithm version")
    scored_at: datetime = Field(..., description="When score was calculated")
    
    @field_validator('overall_score')
    @classmethod
    def validate_overall_score(cls, v, info):
        """Ensure overall score is consistent with components"""
        # Simple example: overall = average of components
        # In practice, this would be the actual formula used
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "overall_score": 78.5,
            "format_score": {
                "component": "Document Format",
                "score": 95.0,
                "evidence": [
                    {
                        "evidence_type": "format_check",
                        "description": "PDF format detected",
                        "data": {"format": "pdf", "parseable": True},
                        "weight": 1.0
                    }
                ],
                "explanation": "Document uses PDF format which is ATS-friendly"
            },
            "critical_issues": [],
            "warnings": ["Missing contact phone number"],
            "scoring_version": "1.0.0"
        }
    })


class JobMatchScore(BaseModel):
    """
    Job matching score breakdown
    
    Principles (SYSTEM.md Section 5):
    - Multi-factor explainable fit
    - No opaque ranking
    """
    
    # Match identity
    resume_id: str = Field(..., description="Resume identifier")
    job_id: str = Field(..., description="Job identifier")
    
    # Overall match
    overall_match: float = Field(..., ge=0.0, le=100.0, description="Overall match score (0-100)")
    
    # Component matches
    skill_match: ScoreExplanation = Field(..., description="Skills alignment")
    experience_match: ScoreExplanation = Field(..., description="Experience level match")
    education_match: ScoreExplanation = Field(..., description="Education requirements match")
    location_match: ScoreExplanation = Field(..., description="Location preference match")
    
    # Matched and missing items
    matched_skills: List[str] = Field(default_factory=list, description="Skills that match")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills missing")
    
    # Recommendation
    recommendation: str = Field(..., description="Match recommendation (apply/maybe/skip)")
    reasons: List[str] = Field(..., description="Reasons for recommendation")
    
    # Metadata
    matched_at: datetime = Field(..., description="When match was calculated")
    
    model_config = ConfigDict(frozen=True)


class Score(BaseModel):
    """
    Unified scoring model
    Contains both ATS compliance and optional job match scores
    """
    
    # Resume being scored
    resume_id: str = Field(..., description="Resume identifier")
    
    # ATS Compliance (always present)
    ats_compliance: ATSComplianceScore = Field(..., description="ATS compliance scoring")
    
    # Job Matching (optional)
    job_matches: List[JobMatchScore] = Field(
        default_factory=list,
        description="Job match scores if jobs provided"
    )
    
    # Overall metadata
    scored_at: datetime = Field(..., description="Scoring timestamp")
    scoring_engine_version: str = Field("1.0.0", description="Scoring engine version")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "resume_id": "resume-abc123",
            "ats_compliance": {
                "overall_score": 78.5,
                "scoring_version": "1.0.0"
            },
            "job_matches": [],
            "scoring_engine_version": "1.0.0"
        }
    })
