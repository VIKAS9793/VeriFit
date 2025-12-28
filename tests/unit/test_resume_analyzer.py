"""
Unit Tests for Resume Analyzer
Compliance: SYSTEM.md Section 0 (No false claims about ATS prediction)
"""

import pytest
from datetime import date

from src.services import ResumeAnalyzer, create_analyzer
from src.models import Resume


class TestResumeAnalyzer:
    """Test suite for resume analyzer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = ResumeAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized"""
        analyzer = create_analyzer()
        assert analyzer is not None
        assert analyzer.scoring_version == "1.0.0"
    
    def test_complete_resume_analysis(self):
        """Test analysis of well-formed resume"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            phone="(555) 123-4567",
            linkedin_url="https://linkedin.com/in/johndoe",
            summary="Experienced software engineer with 5 years in Python development.",
            skills=[
                {"name": "Python"},
                {"name": "JavaScript"},
                {"name": "Docker"},
                {"name": "PostgreSQL"},
                {"name": "React"},
            ],
            experience=[{
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "responsibilities": [
                    "Led team of 5 engineers",
                    "Built microservices architecture"
                ],
                "is_current": True
            }],
            education=[{
                "institution": "MIT",
                "degree": "BS Computer Science"
            }],
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Should have good score
        assert result.overall_score > 80
        
        # Should have no critical issues
        assert len(result.critical_issues) == 0
        
        # Should have evidence for each component
        assert result.format_score.score > 0
        assert result.structure_score.score > 0
        assert result.keyword_score.score > 0
        assert result.readability_score.score > 0
        
        # Each component should have evidence
        assert len(result.format_score.evidence) > 0
        assert len(result.structure_score.evidence) > 0
        assert len(result.keyword_score.evidence) > 0
        assert len(result.readability_score.evidence) > 0
    
    def test_minimal_resume_analysis(self):
        """Test analysis of minimal resume"""
        resume = Resume(
            full_name="Jane Doe",
            email="jane@example.com",
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Score should be lower
        assert result.overall_score < 50
        
        # Should have warnings
        assert len(result.warnings) > 0 or len(result.recommendations) > 0
        
        # Still should have evidence
        assert all(
            len(component.evidence) > 0
            for component in [
                result.format_score,
                result.structure_score,
                result.keyword_score,
                result.readability_score
            ]
        )
    
    def test_missing_email_critical_issue(self):
        """Test that missing email is flagged as critical"""
        resume = Resume(
            full_name="John Doe",
            # No email!
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Should have critical issue
        assert any("email" in issue.lower() for issue in result.critical_issues)
    
    def test_missing_experience_critical_issue(self):
        """Test that missing experience is flagged"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            # No experience!
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Should have critical issue
        assert any("experience" in issue.lower() for issue in result.critical_issues)
    
    def test_determinism(self):
        """
        CRITICAL: Test deterministic analysis
        SYSTEM.md Section 8: Same input = same output
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        result1 = self.analyzer.analyze(resume)
        result2 = self.analyzer.analyze(resume)
        
        # Scores should be identical
        assert result1.overall_score == result2.overall_score
        assert result1.format_score.score == result2.format_score.score
        assert result1.structure_score.score == result2.structure_score.score
        assert result1.keyword_score.score == result2.keyword_score.score
        assert result1.readability_score.score == result2.readability_score.score
    
    def test_evidence_completeness(self):
        """
        CRITICAL: Test every score has evidence
        SYSTEM.md Section 0: Explainability
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}, {"name": "JavaScript"}],
            experience=[{"company": "Tech Corp", "title": "Engineer", "is_current": True}],
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Every component must have evidence
        for component in [result.format_score, result.structure_score, 
                          result.keyword_score, result.readability_score]:
            assert len(component.evidence) > 0, f"{component.component} has no evidence"
            assert component.explanation, f"{component.component} has no explanation"
            
            # Each evidence item should have data
            for evidence in component.evidence:
                assert evidence.description, "Evidence missing description"
                assert evidence.evidence_type, "Evidence missing type"
    
    def test_no_false_claims(self):
        """
        CRITICAL: Verify no false ATS prediction claims
        SYSTEM.md Section 0: Refuse exaggeration
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Check that nothing claims to be an "ATS score"
        # (the overall_score exists but should be documented as analysis, not prediction)
        
        # Ensure we don't claim specific ATS compatibility
        explanations = [
            result.format_score.explanation,
            result.structure_score.explanation,
            result.keyword_score.explanation,
            result.readability_score.explanation,
        ]
        
        for explanation in explanations:
            # Should not claim to predict ATS scores
            assert "ats score" not in explanation.lower()
            assert "guarantee" not in explanation.lower()
            assert "will pass" not in explanation.lower()
    
    def test_skills_keyword_analysis(self):
        """Test keyword analysis based on skills"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[
                {"name": "Python"},
                {"name": "JavaScript"},
                {"name": "Docker"},
            ],
            parsed_at=date.today()
        )
        
        result = self.analyzer.analyze(resume)
        
        # Should detect the skills
        keyword_evidence = result.keyword_score.evidence[0]
        assert keyword_evidence.data["skill_count"] == 3
        assert "Python" in keyword_evidence.data["skills"]
        assert "JavaScript" in keyword_evidence.data["skills"]
        assert "Docker" in keyword_evidence.data["skills"]
    
    def test_readability_components(self):
        """Test readability scoring components"""
        # Test with all readability components
        resume_complete = Resume(
            full_name="John Doe",
            email="john@example.com",
            phone="(555) 123-4567",
            linkedin_url="https://linkedin.com/in/johndoe",
            summary="Experienced engineer",
            experience=[{
                "company": "Tech Corp",
                "title": "Engineer",
                "responsibilities": ["Built features", "Led projects"],
                "is_current": True
            }],
            parsed_at=date.today()
        )
        
        result_complete = self.analyzer.analyze(resume_complete)
        
        # Should have max readability score
        assert result_complete.readability_score.score == 100.0
        
        # Test with minimal readability components
        resume_minimal = Resume(
            full_name="Jane Doe",
            email="jane@example.com",
            # No phone, no URL, no summary, no bullet points
            parsed_at=date.today()
        )
        
        result_minimal = self.analyzer.analyze(resume_minimal)
        
        # Should have low readability score
        assert result_minimal.readability_score.score == 0.0


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
