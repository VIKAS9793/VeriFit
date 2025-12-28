"""
Unit Tests for Score Explainer
Compliance: SYSTEM.md Section 5 (Read-only, evidence-citing)
"""

import pytest
from datetime import date, datetime

from src.services import ScoreExplainer, create_explainer
from src.models.score import (
    ATSComplianceScore,
    JobMatchScore,
    ScoreExplanation,
    Evidence,
    EvidenceType
)
from src.models.job import Job


class TestScoreExplainer:
    """Test suite for score explanation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.explainer = ScoreExplainer()
    
    def test_explainer_initialization(self):
        """Test explainer can be initialized"""
        explainer = create_explainer()
        assert explainer is not None
        assert explainer.version == "1.0.0"
    
    def test_ats_explanation_read_only(self):
        """
        CRITICAL: Test that explanation doesn't modify score
        SYSTEM.MD Section 5: Read-only agent
        """
        # Create score
        score = ATSComplianceScore(
            overall_score=85.0,
            format_score=ScoreExplanation(
                component="Format",
                score=95.0,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.FORMAT_CHECK,
                    description="PDF format detected",
                    data={"format": "pdf"},
                    weight=1.0
                )],
                explanation="PDF format is ATS-friendly"
            ),
            structure_score=ScoreExplanation(
                component="Structure",
                score=80.0,
                max_score=100.0,
                evidence=[],
                explanation="Standard sections found"
            ),
            keyword_score=ScoreExplanation(
                component="Keywords",
                score=75.0,
                max_score=100.0,
                evidence=[],
                explanation="Some keywords present"
            ),
            readability_score=ScoreExplanation(
                component="Readability",
                score=90.0,
                max_score=100.0,
                evidence=[],
                explanation="Good readability"
            ),
            critical_issues=[],
            warnings=[],
            recommendations=["Add more keywords"],
            scoring_version="1.0.0",
            scored_at=datetime.now()
        )
        
        # Store original score
        original_score = score.overall_score
        
        # Generate explanation
        explanation = self.explainer.explain_ats_compliance(score)
        
        # CRITICAL: Score must not be modified
        assert score.overall_score == original_score
        assert explanation is not None
        assert len(explanation) > 0
    
    def test_ats_explanation_completeness(self):
        """Test that all score components are explained"""
        score = ATSComplianceScore(
            overall_score=75.0,
            format_score=ScoreExplanation(
                component="Format",
                score=90.0,
                max_score=100.0,
                evidence=[],
                explanation="Format is good"
            ),
            structure_score=ScoreExplanation(
                component="Structure",
                score=70.0,
                max_score=100.0,
                evidence=[],
                explanation="Structure needs work"
            ),
            keyword_score=ScoreExplanation(
                component="Keywords",
                score=60.0,
                max_score=100.0,
                evidence=[],
                explanation="Few keywords"
            ),
            readability_score=ScoreExplanation(
                component="Readability",
                score=80.0,
                max_score=100.0,
                evidence=[],
                explanation="Readable"
            ),
            critical_issues=["Missing email"],
            warnings=["No phone number"],
            recommendations=["Add email address"],
            scoring_version="1.0.0",
            scored_at=datetime.now()
        )
        
        explanation = self.explainer.explain_ats_compliance(score)
        
        # All components should be mentioned
        assert "FORMAT" in explanation
        assert "STRUCTURE" in explanation
        assert "KEYWORDS" in explanation
        assert "READABILITY" in explanation
        
        # Issues and recommendations should be included
        assert "CRITICAL ISSUES" in explanation
        assert "Missing email" in explanation
        assert "WARNINGS" in explanation
        assert "No phone number" in explanation
        assert "RECOMMENDATIONS" in explanation
        assert "Add email address" in explanation
    
    def test_ats_explanation_evidence_citing(self):
        """
        CRITICAL: Test that evidence is cited
        SYSTEM.MD Section 5: Evidence-citing
        """
        score = ATSComplianceScore(
            overall_score=85.0,
            format_score=ScoreExplanation(
                component="Format",
                score=95.0,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.FORMAT_CHECK,
                    description="Document successfully parsed as PDF",
                    data={"format": "pdf", "size_bytes": 45000},
                    weight=1.0
                )],
                explanation="PDF format detected"
            ),
            structure_score=ScoreExplanation(
                component="Structure",
                score=80.0,
                max_score=100.0,
                evidence=[],
                explanation="Standard sections"
            ),
            keyword_score=ScoreExplanation(
                component="Keywords",
                score=75.0,
                max_score=100.0,
                evidence=[],
                explanation="Keywords present"
            ),
            readability_score=ScoreExplanation(
                component="Readability",
                score=90.0,
                max_score=100.0,
                evidence=[],
                explanation="Good"
            ),
            critical_issues=[],
            warnings=[],
            recommendations=[],
            scoring_version="1.0.0",
            scored_at=datetime.now()
        )
        
        explanation = self.explainer.explain_ats_compliance(score)
        
        # Evidence should be cited
        assert "Evidence:" in explanation
        assert "Document successfully parsed as PDF" in explanation
    
    def test_job_match_explanation_read_only(self):
        """Test that job match explanation doesn't modify score"""
        match_score = JobMatchScore(
            resume_id="test-resume",
            job_id="test-job",
            overall_match=82.0,
            skill_match=ScoreExplanation(
                component="Skills",
                score=75.0,
                max_score=100.0,
                evidence=[],
                explanation="Good skill match"
            ),
            experience_match=ScoreExplanation(
                component="Experience",
                score=90.0,
                max_score=100.0,
                evidence=[],
                explanation="Experience matches"
            ),
            education_match=ScoreExplanation(
                component="Education",
                score=100.0,
                max_score=100.0,
                evidence=[],
                explanation="Education requirement met"
            ),
            location_match=ScoreExplanation(
                component="Location",
                score=100.0,
                max_score=100.0,
                evidence=[],
                explanation="Remote position"
            ),
            matched_skills=["Python", "Docker"],
            missing_skills=["Kubernetes"],
            recommendation="apply",
            reasons=["Strong technical fit", "Good experience match"],
            matched_at=datetime.now()
        )
        
        job = Job(
            job_id="test-job",
            title="Software Engineer",
            company="Tech Corp",
            description="Python role",
            job_type="full_time",
            location="Remote",
            required_skills=["Python", "Docker", "Kubernetes"],
            posted_date=date.today(),
            source_url="https://example.com/job",
            source_platform="TestPlatform",
            scraped_at=datetime.now()
        )
        
        original_score = match_score.overall_match
        
        explanation = self.explainer.explain_job_match(match_score, job)
        
        # Score must not be modified
        assert match_score.overall_match == original_score
        assert explanation is not None
    
    def test_job_match_explanation_completeness(self):
        """Test that all match components are explained"""
        match_score = JobMatchScore(
            resume_id="test-resume",
            job_id="test-job",
            overall_match=70.0,
            skill_match=ScoreExplanation(
                component="Skills",
                score=66.7,
                max_score=100.0,
                evidence=[],
                explanation="Partial skill match"
            ),
            experience_match=ScoreExplanation(
                component="Experience",
                score=80.0,
                max_score=100.0,
                evidence=[],
                explanation="Experience acceptable"
            ),
            education_match=ScoreExplanation(
                component="Education",
                score=100.0,
                max_score=100.0,
                evidence=[],
                explanation="Education OK"
            ),
            location_match=ScoreExplanation(
                component="Location",
                score=0.0,
                max_score=100.0,
                evidence=[],
                explanation="Location mismatch"
            ),
            matched_skills=["Python"],
            missing_skills=["Docker", "Kubernetes"],
            recommendation="maybe",
            reasons=["Some skills missing", "Location mismatch"],
            matched_at=datetime.now()
        )
        
        job = Job(
            job_id="test-job",
            title="Engineer",
            company="Tech Corp",
            description="Job",
            job_type="full_time",
            location="San Francisco",
            required_skills=["Python", "Docker", "Kubernetes"],
            posted_date=date.today(),
            source_url="https://example.com/job",
            source_platform="TestPlatform",
            scraped_at=datetime.now()
        )
        
        explanation = self.explainer.explain_job_match(match_score, job)
        
        # All components should be present
        assert "SKILLS" in explanation
        assert "EXPERIENCE" in explanation
        assert "LOCATION" in explanation
        assert "EDUCATION" in explanation
        
        # Matched and missing skills should be listed
        assert "Python" in explanation
        assert "Docker" in explanation
        assert "Kubernetes" in explanation
        
        # Recommendation should be clear
        assert "RECOMMENDATION" in explanation
        assert "REASONING" in explanation
    
    def test_determinism(self):
        """
        CRITICAL: Test deterministic explanation
        SYSTEM.md Section 8: Same input = same output
        """
        score = ATSComplianceScore(
            overall_score=75.0,
            format_score=ScoreExplanation(
                component="Format",
                score=80.0,
                max_score=100.0,
                evidence=[],
                explanation="Format OK"
            ),
            structure_score=ScoreExplanation(
                component="Structure",
                score=70.0,
                max_score=100.0,
                evidence=[],
                explanation="Structure OK"
            ),
            keyword_score=ScoreExplanation(
                component="Keywords",
                score=75.0,
                max_score=100.0,
                evidence=[],
                explanation="Keywords OK"
            ),
            readability_score=ScoreExplanation(
                component="Readability",
                score=75.0,
                max_score=100.0,
                evidence=[],
                explanation="Readability OK"
            ),
            critical_issues=[],
            warnings=[],
            recommendations=[],
            scoring_version="1.0.0",
            scored_at=datetime.now()
        )
        
        explanation1 = self.explainer.explain_ats_compliance(score)
        explanation2 = self.explainer.explain_ats_compliance(score)
        
        # Should be identical
        assert explanation1 == explanation2


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
