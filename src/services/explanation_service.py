"""
Explanation Service
Transforms raw Evidence objects into human-readable explanations.

SYSTEM.md Compliance:
- Section 0: Explainability first
- Section 3: LIME, NIST AI RMF, OECD AI Principles

Principles:
- No technical jargon
- Cite specific resume content
- Actionable recommendations
- Confidence scores for transparency
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.models.score import ScoreExplanation, Evidence, EvidenceType


class FindingExplanation(BaseModel):
    """A single finding with human-readable explanation"""
    finding: str = Field(..., description="What was found")
    location: str = Field(..., description="Where in resume (e.g., 'Experience > Product Manager')")
    impact: str = Field(..., description="How this affects the score")
    recommendation: str = Field(..., description="Actionable improvement suggestion")
    severity: str = Field(default="info", description="info/warning/critical")


class ScoreBreakdown(BaseModel):
    """Complete breakdown for a single score component"""
    component: str = Field(..., description="Score component name")
    score: float = Field(..., description="Numeric score 0-100")
    summary: str = Field(..., description="One-line human-readable summary")
    reasoning_chain: List[str] = Field(default_factory=list, description="Step-by-step logic")
    findings: List[FindingExplanation] = Field(default_factory=list, description="Detailed findings")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="AI confidence")
    generated_at: datetime = Field(default_factory=datetime.now)


class ExplanationService:
    """
    Service for generating human-readable explanations
    from Evidence-based scoring data.
    
    'Truth over Hype' - Every score must be explainable.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        
    def explain_score(self, score_explanation: ScoreExplanation) -> ScoreBreakdown:
        """
        Transform a ScoreExplanation into a human-readable breakdown.
        
        Args:
            score_explanation: Raw score with evidence
            
        Returns:
            ScoreBreakdown with user-friendly explanations
        """
        findings = []
        reasoning_chain = []
        
        # Process each piece of evidence
        for evidence in score_explanation.evidence:
            finding = self._evidence_to_finding(evidence, score_explanation.component)
            if finding:
                findings.append(finding)
                reasoning_chain.append(f"Found: {finding.finding}")
        
        # Generate summary based on score
        summary = self._generate_summary(
            score_explanation.component,
            score_explanation.score,
            len(findings)
        )
        
        # Calculate confidence based on evidence strength
        confidence = self._calculate_confidence(score_explanation.evidence)
        
        return ScoreBreakdown(
            component=score_explanation.component,
            score=score_explanation.score,
            summary=summary,
            reasoning_chain=reasoning_chain,
            findings=findings,
            confidence=confidence
        )
    
    def _evidence_to_finding(
        self, 
        evidence: Evidence, 
        component: str
    ) -> Optional[FindingExplanation]:
        """Convert Evidence object to human-readable finding"""
        
        # Map evidence types to user-friendly descriptions
        type_descriptions = {
            EvidenceType.KEYWORD_MATCH: "Keyword Analysis",
            EvidenceType.FORMAT_CHECK: "Format Check",
            EvidenceType.STRUCTURE_ANALYSIS: "Structure Review",
            EvidenceType.EXPERIENCE_COMPARISON: "Experience Analysis",
            EvidenceType.SKILL_COMPARISON: "Skills Assessment",
            EvidenceType.READABILITY_CHECK: "Readability Check",
        }
        
        # Determine severity based on weight
        if evidence.weight >= 0.8:
            severity = "critical"
        elif evidence.weight >= 0.5:
            severity = "warning"
        else:
            severity = "info"
            
        # Generate recommendation based on evidence type
        recommendation = self._generate_recommendation(evidence)
        
        return FindingExplanation(
            finding=evidence.description,
            location=type_descriptions.get(evidence.evidence_type, component),
            impact=f"Weight: {evidence.weight:.0%} impact on {component}",
            recommendation=recommendation,
            severity=severity
        )
    
    def _generate_summary(
        self, 
        component: str, 
        score: float, 
        finding_count: int
    ) -> str:
        """Generate a one-line summary based on score"""
        
        if score >= 90:
            return f"Excellent {component.lower()}! Your profile demonstrates strong performance in this area."
        elif score >= 75:
            return f"Good {component.lower()} with minor areas for improvement."
        elif score >= 60:
            return f"Average {component.lower()}. {finding_count} areas identified for enhancement."
        elif score >= 40:
            return f"Below average {component.lower()}. Focus on the {finding_count} recommendations below."
        else:
            return f"Significant improvements needed in {component.lower()}. Review all {finding_count} findings."
    
    def _generate_recommendation(self, evidence: Evidence) -> str:
        """Generate actionable recommendation from evidence"""
        
        # Type-specific recommendations
        recommendations = {
            EvidenceType.KEYWORD_MATCH: "Add relevant keywords from the job description to improve ATS matching.",
            EvidenceType.FORMAT_CHECK: "Ensure consistent formatting throughout your resume.",
            EvidenceType.STRUCTURE_ANALYSIS: "Organize sections clearly with proper headings.",
            EvidenceType.EXPERIENCE_COMPARISON: "Add quantifiable metrics to demonstrate impact (e.g., 'increased by 20%').",
            EvidenceType.SKILL_COMPARISON: "List specific technical skills relevant to your target role.",
            EvidenceType.READABILITY_CHECK: "Use clear, concise language and avoid jargon.",
        }
        
        return recommendations.get(
            evidence.evidence_type, 
            "Review this area for potential improvements."
        )
    
    def _calculate_confidence(self, evidence_list: List[Evidence]) -> float:
        """Calculate overall confidence based on evidence quality"""
        if not evidence_list:
            return 0.5
            
        # Higher confidence with more evidence
        base_confidence = min(0.9, 0.5 + (len(evidence_list) * 0.1))
        
        # Weight by evidence weights
        avg_weight = sum(e.weight for e in evidence_list) / len(evidence_list)
        
        # Clamp to valid range [0.0, 1.0]
        return min(1.0, max(0.0, round(base_confidence * avg_weight + 0.3, 2)))
    
    def explain_full_analysis(
        self, 
        format_score: ScoreExplanation,
        structure_score: ScoreExplanation,
        keyword_score: ScoreExplanation,
        readability_score: ScoreExplanation
    ) -> Dict[str, ScoreBreakdown]:
        """
        Generate explanations for all score components.
        
        Returns dict keyed by component name.
        """
        return {
            "format": self.explain_score(format_score),
            "structure": self.explain_score(structure_score),
            "keywords": self.explain_score(keyword_score),
            "readability": self.explain_score(readability_score),
        }


# Factory function
def create_explanation_service() -> ExplanationService:
    """Create ExplanationService instance"""
    return ExplanationService()
