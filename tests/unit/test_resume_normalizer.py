"""
Unit Tests for Resume Normalizer
Compliance: SYSTEM.md Section 5 (No semantic edits)
"""

import pytest
from datetime import date

from src.services import ResumeNormalizer, create_normalizer
from src.models import Resume, Skill


class TestResumeNormalizer:
    """Test suite for resume normalization"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.normalizer = ResumeNormalizer()
    
    def test_normalizer_initialization(self):
        """Test normalizer can be initialized"""
        normalizer = create_normalizer()
        assert normalizer is not None
    
    def test_whitespace_normalization(self):
        """Test whitespace cleanup preserves content"""
        resume = Resume(
            full_name="  John   Doe  ",
            email="john@example.com",
            summary="  Software engineer   with   experience  ",
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        # Whitespace cleaned
        assert normalized.full_name == "John Doe"
        assert normalized.summary == "Software engineer with experience"
        
        # Content preserved exactly
        assert "John Doe" in normalized.full_name
        assert "Software engineer with experience" == normalized.summary
    
    def test_phone_standardization(self):
        """Test phone number formatting"""
        test_cases = [
            ("555-123-4567", "(555) 123-4567"),
            ("(555) 123-4567", "(555) 123-4567"),
            ("5551234567", "(555) 123-4567"),
            ("+1-555-123-4567", "+1 (555) 123-4567"),
        ]
        
        for input_phone, expected_output in test_cases:
            resume = Resume(
                full_name="John Doe",
                email="john@example.com",
                phone=input_phone,
                parsed_at=date.today()
            )
            
            normalized = self.normalizer.normalize(resume)
            assert normalized.phone == expected_output, f"Failed for {input_phone}"
    
    def test_skill_deduplication(self):
        """Test duplicate skills removed (case-insensitive)"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            skills=[
                {"name": "Python"},
                {"name": "python"},  # Duplicate (different case)
                {"name": "JavaScript"},
                {"name": "Python"},  # Duplicate
                {"name": "Docker"},
            ],
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        # Only unique skills
        skill_names = [s.name for s in normalized.skills]
        assert len(skill_names) == 3
        assert "Python" in skill_names
        assert "JavaScript" in skill_names
        assert "Docker" in skill_names
        
        # First occurrence preserved (original case)
        assert skill_names[0] == "Python"  # Not "python"
    
    def test_certification_deduplication(self):
        """Test duplicate certifications removed"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            certifications=[
                "AWS Certified",
                "PMP",
                "aws certified",  # Duplicate (different case)
                "PMP",  # Duplicate
            ],
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        assert len(normalized.certifications) == 2
        assert "AWS Certified" in normalized.certifications
        assert "PMP" in normalized.certifications
    
    def test_no_semantic_content_modification(self):
        """
        CRITICAL TEST: Verify NO semantic content changed
        SYSTEM.md Section 5: No inference or interpretation
        """
        original_text = "Led team of 5 engineers building ML pipeline"
        
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            experience=[{
                "company": "  Tech Corp  ",
                "title": "  Senior Engineer  ",
                "responsibilities": [
                    f"  {original_text}  ",
                    "  Designed scalable architecture  "
                ],
                "is_current": True
            }],
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        # Whitespace cleaned
        assert normalized.experience[0].company == "Tech Corp"
        assert normalized.experience[0].title == "Senior Engineer"
        
        # Content EXACTLY preserved (no rewording)
        assert normalized.experience[0].responsibilities[0] == original_text
        assert "Led team of 5 engineers" in normalized.experience[0].responsibilities[0]
        assert "building ML pipeline" in normalized.experience[0].responsibilities[0]
    
    def test_empty_responsibilities_removed(self):
        """Test empty strings removed from lists"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            experience=[{
                "company": "Tech Corp",
                "title": "Engineer",
                "responsibilities": [
                    "Built features",
                    "",  # Empty
                    "   ",  # Whitespace only
                    "Led projects"
                ],
                "is_current": True
            }],
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        # Only non-empty items
        assert len(normalized.experience[0].responsibilities) == 2
        assert "Built features" in normalized.experience[0].responsibilities
        assert "Led projects" in normalized.experience[0].responsibilities
    
    def test_education_whitespace_cleanup(self):
        """Test education fields cleaned"""
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            education=[{
                "institution": "  MIT  ",
                "degree": "  BS Computer Science  ",
                "field_of_study": "  Machine Learning  "
            }],
            parsed_at=date.today()
        )
        
        normalized = self.normalizer.normalize(resume)
        
        assert normalized.education[0].institution == "MIT"
        assert normalized.education[0].degree == "BS Computer Science"
        assert normalized.education[0].field_of_study == "Machine Learning"
    
    def test_idempotency(self):
        """Test normalizing twice produces same result"""
        resume = Resume(
            full_name="  John Doe  ",
            email="john@example.com",
            phone="555-123-4567",
            skills=[
                {"name": "Python"},
                {"name": "python"}
            ],
            parsed_at=date.today()
        )
        
        normalized_once = self.normalizer.normalize(resume)
        normalized_twice = self.normalizer.normalize(normalized_once)
        
        # Should be identical
        assert normalized_once.full_name == normalized_twice.full_name
        assert normalized_once.phone == normalized_twice.phone
        assert len(normalized_once.skills) == len(normalized_twice.skills)


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
