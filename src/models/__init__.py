"""
VeriFit Data Models Package
Type-safe Pydantic models for all data structures
Compliance: SYSTEM.md Section 9 (Type hints mandatory)
"""

from .resume import Resume, Experience, Education, Skill
from .job import Job, JobRequirement
from .score import Score, ATSComplianceScore, ScoreExplanation
from .audit import AuditLog, HITLDecision
from .rewrite import RewriteSuggestion, ValidationResult, RewriteOptions, RewriteSession, RiskLevel

__all__ = [
    "Resume",
    "Experience",
    "Education",
    "Skill",
    "Job",
    "JobRequirement",
    "Score",
    "ATSComplianceScore",
    "ScoreExplanation",
    "AuditLog",
    "HITLDecision",
    "RewriteSuggestion",
    "ValidationResult",
    "RewriteOptions",
    "RewriteSession",
    "RiskLevel",
]
