"""
Unit Tests for Job Matcher
Compliance: SYSTEM.md Section 5 (Explainable fit, no opaque ranking)
"""

import pytest
from datetime import date, timedelta

from src.services import JobMatcher, create_matcher
from src.models import Resume, Job
from src.models.job import ExperienceLevel


class TestJobMatcher:
    """Test suite for job matching"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.matcher = JobMatcher()
    
    def test_matcher_initialization(self):
        """Test matcher can be initialized"""
        matcher = create_matcher()
        assert matcher is not None
        assert matcher.MAX_JOB_AGE_DAYS == 7
    
    def test_perfect_skill_match(self):
        """Test matching when all skills overlap"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[
                {"name": "Python"},
                {"name": "Docker"},
                {"name": "PostgreSQL"},
            ],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-123",
            title="Software Engineer",
            company="Tech Corp",
            description="Python developer role",
            job_type="full_time",
            location="Remote",
            required_skills=["Python", "Docker", "PostgreSQL"],
            posted_date=date.today(),
            source_url="https://example.com/job/123",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Perfect skill match = 100%
        assert result.skill_match.score == 100.0
        
        # All skills matched
        assert len(result.matched_skills) == 3
        assert len(result.missing_skills) == 0
        
        # High overall score
        assert result.overall_match > 80
    
    def test_partial_skill_match(self):
        """Test matching with some missing skills"""
        resume = Resume(
            full_name="Jane Doe",
            email="jane@example.com",
            skills=[
                {"name": "Python"},
                {"name": "Docker"},
            ],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-456",
            title="DevOps Engineer",
            company="Tech Corp",
            description="DevOps role",
            job_type="full_time",
            location="Remote",
            required_skills=["Python", "Docker", "Kubernetes", "Terraform"],
            posted_date=date.today(),
            source_url="https://example.com/job/456",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # 2/4 skills matched = 50%
        assert result.skill_match.score == 50.0
        
        # Check matched and missing
        assert len(result.matched_skills) == 2
        assert len(result.missing_skills) == 2
        assert "kubernetes" in result.missing_skills
        assert "terraform" in result.missing_skills
    
    def test_job_age_validation_accepted(self):
        """Test that recent jobs are accepted"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        # 6-day old job (within limit)
        job = Job(
            job_id="test-789",
            title="Engineer",
            company="Tech Corp",
            description="Job",
            job_type="full_time",
            location="Remote",
            required_skills=["Python"],
            posted_date=date.today() - timedelta(days=6),
            source_url="https://example.com/job/789",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Should not be None (accepted)
        assert result is not None
    
    def test_job_age_validation_rejected(self):
        """
        CRITICAL: Test that old jobs are rejected  
        SYSTEM.md Section 5: ≤7-day active roles only
        
        Note: Job model validates this at construction time
        """
        from pydantic import ValidationError
        
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        # Try to create 8-day old job (should fail at model level)
        with pytest.raises(ValidationError) as exc_info:
            job = Job(
                job_id="test-old",
                title="Engineer",
                company="Tech Corp",
                description="Job",
                job_type="full_time",
                location="Remote",
                required_skills=["Python"],
                posted_date=date.today() - timedelta(days=8),  # Too old!
                source_url="https://example.com/job/old",
                source_platform="TestPlatform",
                scraped_at=date.today()
            )
        
        # Should raise validation error mentioning 7-day limit
        assert "7-day limit" in str(exc_info.value)
    
    def test_experience_matching_sufficient(self):
        """Test experience matching when candidate meets requirements"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            experience=[
                {
                    "company": "Company A",
                    "title": "Engineer",
                    "start_date": date.today() - timedelta(days=365*3),  # 3 years
                    "end_date": date.today(),
                    "is_current": True
                }
            ],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-exp",
            title="Mid-Level Engineer",
            company="Tech Corp",
            description="Requires 2 years experience",
            job_type="full_time",
            location="Remote",
            required_skills=["Python"],
            experience_level=ExperienceLevel.MID_LEVEL,  # Correct enum value
            posted_date=date.today(),
            source_url="https://example.com/job/exp",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Should meet experience requirement (3 >= 2)
        assert result.experience_match.score == 100.0
    
    def test_experience_matching_insufficient(self):
        """Test experience matching when candidate below requirements"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            experience=[
                {
                    "company": "Company A",
                    "title": "Junior Engineer",
                    "start_date": date.today() - timedelta(days=365),  # 1 year
                    "end_date": date.today(),
                    "is_current": True
                }
            ],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-exp2",
            title="Senior Engineer",
            company="Tech Corp",
            description="Requires 5+ years experience",
            job_type="full_time",
            location="Remote",
            required_skills=["Python"],
            experience_level=ExperienceLevel.SENIOR,  # Correct enum value
            posted_date=date.today(),
            source_url="https://example.com/job/exp2",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Should have reduced score due to gap (1 < 5)
        assert result.experience_match.score < 100.0
    
    def test_location_match_remote(self):
        """Test location matching for remote jobs"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            location="New York",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-remote",
            title="Engineer",
            company="Tech Corp",
            description="Remote job",
            job_type="full_time",
            location="San Francisco",
            is_remote=True,  # Remote!
            required_skills=["Python"],
            posted_date=date.today(),
            source_url="https://example.com/job/remote",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Remote = location not a factor
        assert result.location_match.score == 100.0
    
    def test_explainability(self):
        """
        CRITICAL: Test that all scores have evidence
        SYSTEM.md Section 5: Multi-factor explainable fit, no opaque ranking
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-explain",
            title="Engineer",
            company="Tech Corp",
            description="Job",
            job_type="full_time",
            location="Remote",
            required_skills=["Python", "Docker"],
            posted_date=date.today(),
            source_url="https://example.com/job/explain",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # All score components must have evidence
        for component in [
            result.skill_match,
            result.experience_match,
            result.location_match,
            result.education_match
        ]:
            assert len(component.evidence) > 0, f"{component.component} has no evidence"
            assert component.explanation, f"{component.component} has no explanation"
    
    def test_determinism(self):
        """
        CRITICAL: Test deterministic matching
        SYSTEM.md Section 8: Same input = same output
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}, {"name": "Docker"}],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-determ",
            title="Engineer",
            company="Tech Corp",
            description="Job",
            job_type="full_time",
            location="Remote",
            required_skills=["Python", "Docker", "Kubernetes"],
            posted_date=date.today(),
            source_url="https://example.com/job/determ",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result1 = self.matcher.match(resume, job)
        result2 = self.matcher.match(resume, job)
        
        # Scores should be identical
        assert result1.overall_match == result2.overall_match
        assert result1.skill_match.score == result2.skill_match.score
        assert set(result1.matched_skills) == set(result2.matched_skills)
        assert set(result1.missing_skills) == set(result2.missing_skills)
    
    def test_no_opaque_ranking(self):
        """
        CRITICAL: Verify no opaque AI ranking
        SYSTEM.md Section 5: No opaque ranking
        """
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[{"name": "Python"}],
            parsed_at=date.today()
        )
        
        job = Job(
            job_id="test-opaque",
            title="Engineer",
            company="Tech Corp",
            description="Job",
            job_type="full_time",
            location="Remote",
            required_skills=["Python"],
            posted_date=date.today(),
            source_url="https://example.com/job/opaque",
            source_platform="TestPlatform",
            scraped_at=date.today()
        )
        
        result = self.matcher.match(resume, job)
        
        # Verify we can explain HOW score was calculated
        # All factors should be traceable
        assert result.matched_skills  # Exact list of matched skills
        assert result.missing_skills is not None  # Exact list of missing
        
        # Each score component should have clear evidence
        for component in [result.skill_match, result.experience_match]:
            for evidence in component.evidence:
                assert evidence.data  # Evidence has concrete data
                assert evidence.description  # Evidence has description


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
