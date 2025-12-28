"""
Resume Analysis Engine
Evidence-based ATS-friendly characteristic analysis
Compliance: SYSTEM.md Section 0 (Truth over Hype - NO false claims)

What this does:
- Analyzes format compliance
- Checks contact information completeness
- Validates content structure
- Identifies keywords present

What this DOES NOT do:
- Predict ATS scores (no standard exists)
- Claim to replicate any specific ATS (Workday, Greenhouse, etc.)
- Guarantee "ATS pass rates"
"""

from typing import Dict, List, Any
from datetime import datetime

from src.models.resume import Resume
from src.models.score import (
    ATSComplianceScore,
    ScoreExplanation,
    Evidence,
    EvidenceType,
    ScoreCategory
)
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.services.llm import LLMService


class ResumeAnalyzer:
    """
    ATS-Friendly Resume Analyzer
    
    Provides evidence-based analysis WITHOUT claiming to predict ATS scores
    
    Research finding (Dec 2024): No industry-standard ATS scoring exists
    - Greenhouse/Lever: NO automated scoring
    - Taleo/Workday/iCIMS: Proprietary algorithms
    
    Therefore: We analyze common factors, we DON'T predict scores
    """
    
    def __init__(self, llm_service: Optional['LLMService'] = None):
        """Initialize analyzer"""
        self.scoring_version = "2.0.0-llm"
        self.llm_service = llm_service
    
    def analyze(self, resume: Resume) -> ATSComplianceScore:
        """
        Analyze resume for ATS-friendly characteristics
        
        Args:
            resume: Parsed and normalized Resume object
            
        Returns:
            ATSComplianceScore with evidence for each factor
            
        Note: This is NOT an ATS score prediction
        """
        if self.llm_service:
            try:
                print("DEBUG: Using LLM for analysis")
                analysis_dict = self.llm_service.analyze_resume(resume.model_dump(mode='json'))
                
                # Convert LLM dict to ATSComplianceScore
                # Ensure fields match Pydantic model
                return ATSComplianceScore(
                    overall_score=analysis_dict.get('veriscore', 0),
                    format_score=ScoreExplanation(**analysis_dict.get('format_score', {})),
                    structure_score=ScoreExplanation(**analysis_dict.get('structure_score', {})),
                    keyword_score=ScoreExplanation(**analysis_dict.get('keyword_score', {})),
                    readability_score=ScoreExplanation(**analysis_dict.get('readability_score', {})),
                    critical_issues=analysis_dict.get('critical_issues', []),
                    warnings=analysis_dict.get('warnings', []),
                    recommendations=analysis_dict.get('recommendations', []),
                    scoring_version=self.scoring_version,
                    scored_at=datetime.utcnow()
                )
            except Exception as e:
                print(f"ERROR: LLM Analysis failed: {e}. Falling back to heuristic.")
                # Fallthrough to heuristic

        # Analyze each component (Heuristic Fallback)
        format_analysis = self._analyze_format(resume)
        structure_analysis = self._analyze_structure(resume)
        keyword_analysis = self._analyze_keywords(resume)
        readability_analysis = self._analyze_readability(resume)
        
        # Calculate overall (weighted average)
        # Weights based on common ATS factors (research-backed)
        overall_score = (
            format_analysis.score * 0.25 +
            structure_analysis.score * 0.35 +
            keyword_analysis.score * 0.25 +
            readability_analysis.score * 0.15
        )
        
        # Collect issues
        critical_issues = []
        warnings = []
        recommendations = []
        
        # Check for critical issues
        if not resume.email:
            critical_issues.append("Missing email address (required for contact)")
        
        if len(resume.experience) == 0:
            critical_issues.append("No work experience listed")
        
        if len(resume.skills) == 0:
            warnings.append("No skills section found")
        
        if not resume.phone:
            recommendations.append("Consider adding phone number for easier contact")
        
        if not resume.summary:
            recommendations.append("Consider adding professional summary for context")
        
        # Create compliance score
        return ATSComplianceScore(
            overall_score=round(overall_score, 1),
            format_score=format_analysis,
            structure_score=structure_analysis,
            keyword_score=keyword_analysis,
            readability_score=readability_analysis,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            scoring_version=self.scoring_version,
            scored_at=datetime.utcnow()
        )
    
    def _analyze_format(self, resume: Resume) -> ScoreExplanation:
        """
        Analyze format compliance
        
        Checks: File parseable, has content
        """
        score = 100.0
        evidence_list = []
        issues = []
        
        # Check if we got any content
        if resume.source_file:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.FORMAT_CHECK,
                description=f"File format: {resume.source_file.split('.')[-1] if '.' in resume.source_file else 'unknown'}",
                data={"source_file": resume.source_file},
                weight=1.0
            ))
        
        # Check content presence (basic validation)
        content_length = len(resume.full_name or "") + len(resume.summary or "")
        if content_length < 10:
            score -= 50
            issues.append("Very little content extracted")
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.FORMAT_CHECK,
                description="Minimal content detected",
                data={"content_length": content_length},
                weight=1.0
            ))
        else:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.FORMAT_CHECK,
                description="Content successfully extracted",
                data={"content_length": content_length},
                weight=1.0
            ))
        
        explanation = "Format analysis: " + (
            "Parseable format with extractable content." if score == 100
            else f"Issues found: {', '.join(issues)}"
        )
        
        return ScoreExplanation(
            component="Format Compliance",
            score=max(0, score),
            max_score=100.0,
            evidence=evidence_list,
            explanation=explanation
        )
    
    def _analyze_structure(self, resume: Resume) -> ScoreExplanation:
        """
        Analyze resume structure completeness
        
        Checks: Standard sections present
        """
        score = 100.0
        evidence_list = []
        missing_sections = []
        
        # Check contact info
        if resume.email:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Email address present",
                data={"has_email": True},
                weight=1.0
            ))
        else:
            score -= 30
            missing_sections.append("email")
        
        # Check experience
        if len(resume.experience) > 0:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description=f"Experience section: {len(resume.experience)} entries",
                data={"experience_count": len(resume.experience)},
                weight=1.0
            ))
        else:
            score -= 30
            missing_sections.append("experience")
        
        # Check education
        if len(resume.education) > 0:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description=f"Education section: {len(resume.education)} entries",
                data={"education_count": len(resume.education)},
                weight=1.0
            ))
        else:
            score -= 20
            missing_sections.append("education")
        
        # Check skills
        if len(resume.skills) > 0:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description=f"Skills section: {len(resume.skills)} skills",
                data={"skills_count": len(resume.skills)},
                weight=1.0
            ))
        else:
            score -= 20
            missing_sections.append("skills")
        
        explanation = (
            "All standard sections present." if score == 100
            else f"Missing sections: {', '.join(missing_sections)}"
        )
        
        return ScoreExplanation(
            component="Content Structure",
            score=max(0, score),
            max_score=100.0,
            evidence=evidence_list,
            explanation=explanation
        )
    
    def _analyze_keywords(self, resume: Resume) -> ScoreExplanation:
        """
        Analyze keyword presence
        
        Note: This does NOT score relevance (that's job-specific)
        """
        score = 100.0
        evidence_list = []
        
        # Count skills (keywords)
        skill_count = len(resume.skills)
        
        if skill_count == 0:
            score = 0
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.KEYWORD_MATCH,
                description="No skills/keywords identified",
                data={"skill_count": 0},
                weight=1.0
            ))
        elif skill_count < 5:
            score = 50
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.KEYWORD_MATCH,
                description=f"Limited skills identified: {skill_count}",
                data={"skill_count": skill_count, "skills": [s.name for s in resume.skills]},
                weight=1.0
            ))
        else:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.KEYWORD_MATCH,
                description=f"Good skill coverage: {skill_count} skills",
                data={"skill_count": skill_count, "skills": [s.name for s in resume.skills[:10]]},  # First 10
                weight=1.0
            ))
        
        explanation = f"Identified {skill_count} skills/keywords. Note: Relevance depends on specific job requirements."
        
        return ScoreExplanation(
            component="Keyword Presence",
            score=score,
            max_score=100.0,
            evidence=evidence_list,
            explanation=explanation
        )
    
    def _analyze_readability(self, resume: Resume) -> ScoreExplanation:
        """
        Analyze contact information and professional presentation
        """
        score = 0
        evidence_list = []
        present_items = []
        missing_items = []
        
        # Phone present? (+25)
        if resume.phone:
            score += 25
            present_items.append("phone")
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Phone number present",
                data={"has_phone": True},
                weight=0.25
            ))
        else:
            missing_items.append("phone")
        
        # LinkedIn/Portfolio? (+25)
        if resume.linkedin_url or resume.portfolio_url:
            score += 25
            present_items.append("professional URL")
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Professional URL present",
                data={
                    "has_linkedin": bool(resume.linkedin_url),
                    "has_portfolio": bool(resume.portfolio_url)
                },
                weight=0.25
            ))
        else:
            missing_items.append("professional URL")
        
        # Summary? (+25)
        if resume.summary:
            score += 25
            present_items.append("summary")
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Professional summary present",
                data={"summary_length": len(resume.summary)},
                weight=0.25
            ))
        else:
            missing_items.append("summary")
        
        # Bullet points in experience? (+25)
        has_bullets = any(
            len(exp.responsibilities) > 0 
            for exp in resume.experience
        )
        if has_bullets:
            score += 25
            present_items.append("bullet points")
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Bullet points used in experience",
                data={"has_bullet_points": True},
                weight=0.25
            ))
        else:
            missing_items.append("bullet points")
        
        # Always add evidence summary (even if nothing present)
        if not evidence_list:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description="Missing readability elements",
                data={"missing": missing_items},
                weight=1.0
            ))
        
        explanation = (
            f"Professional presentation elements: {', '.join(present_items)}" 
            if present_items 
            else f"Missing all readability elements: {', '.join(missing_items)}"
        )
        
        return ScoreExplanation(
            component="Readability & Contact",
            score=score,
            max_score=100.0,
            evidence=evidence_list,
            explanation=explanation
        )


# Factory function
def create_analyzer(llm_service: Any = None) -> ResumeAnalyzer:
    """Create resume analyzer instance"""
    return ResumeAnalyzer(llm_service=llm_service)
