"""
Score Explanation Agent
Read-only natural language explanation generator
Compliance: SYSTEM.md Section 5 (Read-only, Evidence-citing, No score modification)

What this DOES:
- Generates human-readable explanations from scores
- Cites actual Evidence objects
- Provides actionable recommendations

What this DOES NOT do:
- Modify scores (read-only!)
- Invent evidence (no hallucination)
- Exaggerate or minimize issues
"""

from typing import List
from src.models.score import (
    ATSComplianceScore,
    JobMatchScore,
    ScoreExplanation,
    Evidence
)
from src.models.job import Job


class ScoreExplainer:
    """
    Read-only score explanation generator
    
    Principle: Evidence-backed natural language summaries
    SYSTEM.md Section 5: Read-only, evidence-citing, no score modification
    """
    
    def __init__(self):
        """Initialize explainer"""
        self.version = "1.0.0"
    
    def explain_ats_compliance(self, score: ATSComplianceScore) -> str:
        """
        Generate natural language explanation of ATS compliance score
        
        Args:
            score: ATS compliance score object (NOT modified)
            
        Returns:
            Multi-paragraph explanation with evidence citations
            
        Note: This is READ-ONLY - score object is never modified
        """
        sections = []
        
        # Overall summary
        sections.append(self._explain_overall_ats(score.overall_score))
        sections.append("")  # Blank line
        
        # Component breakdowns
        sections.append(self._explain_component(score.format_score, "FORMAT"))
        sections.append("")
        sections.append(self._explain_component(score.structure_score, "STRUCTURE"))
        sections.append("")
        sections.append(self._explain_component(score.keyword_score, "KEYWORDS"))
        sections.append("")
        sections.append(self._explain_component(score.readability_score, "READABILITY"))
        
        # Critical issues
        if score.critical_issues:
            sections.append("")
            sections.append("CRITICAL ISSUES:")
            for issue in score.critical_issues:
                sections.append(f"• {issue}")
        
        # Warnings
        if score.warnings:
            sections.append("")
            sections.append("WARNINGS:")
            for warning in score.warnings:
                sections.append(f"• {warning}")
        
        # Recommendations
        if score.recommendations:
            sections.append("")
            sections.append("RECOMMENDATIONS:")
            for rec in score.recommendations:
                sections.append(f"• {rec}")
        
        return "\n".join(sections)
    
    def explain_job_match(self, match_score: JobMatchScore, job: Job) -> str:
        """
        Generate natural language explanation of job match
        
        Args:
            match_score: Job match score object (NOT modified)
            job: Job being matched against
            
        Returns:
            Multi-paragraph explanation with match verdict
            
        Note: This is READ-ONLY - match_score object is never modified
        """
        sections = []
        
        # Overall recommendation
        sections.append(self._explain_match_verdict(
            match_score.overall_match,
            match_score.recommendation
        ))
        sections.append("")
        
        # Skill breakdown
        sections.append(self._explain_skills_match(
            match_score.skill_match,
            match_score.matched_skills,
            match_score.missing_skills
        ))
        sections.append("")
        
        # Experience
        sections.append(self._explain_component(match_score.experience_match, "EXPERIENCE"))
        sections.append("")
        
        # Location
        sections.append(self._explain_component(match_score.location_match, "LOCATION"))
        sections.append("")
        
        # Education
        sections.append(self._explain_component(match_score.education_match, "EDUCATION"))
        
        # Why apply/skip
        if match_score.reasons:
            sections.append("")
            sections.append("REASONING:")
            for reason in match_score.reasons:
                sections.append(f"• {reason}")
        
        return "\n".join(sections)
    
    def _explain_overall_ats(self, overall_score: float) -> str:
        """Explain overall ATS score"""
        # Determine rating
        if overall_score >= 80:
            rating = "excellent"
        elif overall_score >= 70:
            rating = "good"
        elif overall_score >= 60:
            rating = "fair"
        else:
            rating = "needs improvement"
        
        return f"Your resume received an overall ATS compliance score of {overall_score}/100 ({rating})."
    
    def _explain_component(self, component: ScoreExplanation, label: str) -> str:
        """
        Explain a score component with evidence
        
        Cites actual Evidence objects - no hallucination
        """
        lines = []
        
        # Component header with score
        lines.append(f"{label} ({component.score}/{component.max_score}):")
        
        # Main explanation
        lines.append(f"  {component.explanation}")
        
        # Evidence details (if available)
        if component.evidence:
            for evidence in component.evidence:
                if evidence.description:
                    lines.append(f"  Evidence: {evidence.description}")
        
        return "\n".join(lines)
    
    def _explain_match_verdict(self, score: float, recommendation: str) -> str:
        """Explain match recommendation"""
        verdict_text = {
            "apply": "STRONG MATCH - RECOMMENDED TO APPLY",
            "maybe": "MODERATE MATCH - CONSIDER APPLYING",
            "skip": "WEAK MATCH - NOT RECOMMENDED"
        }
        
        verdict = verdict_text.get(recommendation, "MATCH ANALYSIS")
        return f"RECOMMENDATION: {verdict} ({score}/100)"
    
    def _explain_skills_match(
        self,
        skill_component: ScoreExplanation,
        matched: List[str],
        missing: List[str]
    ) -> str:
        """Explain skill matching with specific lists"""
        lines = []
        
        lines.append(f"SKILLS ({skill_component.score}/100):")
        
        if matched:
            lines.append(f"  Matched {len(matched)} skills:")
            for skill in matched[:10]:  # Limit to first 10
                lines.append(f"    ✓ {skill}")
        
        if missing:
            lines.append(f"  Missing {len(missing)} required skills:")
            for skill in missing[:10]:  # Limit to first 10
                lines.append(f"    ✗ {skill}")
        
        if not matched and not missing:
            lines.append("  No specific skills required")
        
        return "\n".join(lines)


# Factory function
def create_explainer() -> ScoreExplainer:
    """Create score explainer instance"""
    return ScoreExplainer()
