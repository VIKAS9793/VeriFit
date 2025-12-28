"""
Unit Tests for Rewrite Validator
Compliance: SYSTEM.md Section 5 (No new claims)
"""

import pytest
from datetime import date

from src.services.rewrite_validator import RewriteValidator, create_validator
from src.models.resume import Resume, Experience, Education, Skill
from src.models.rewrite import ValidationResult, RiskLevel


class TestRewriteValidator:
    """Test suite for anti-hallucination validator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = create_validator()
        
        # Create sample resume
        self.resume = Resume(
            user_id="test_user",
            full_name="Test User",
            raw_text="Sample resume",
            contact_info={"email": "test@example.com"},
            summary="Software Engineer",
            skills=[Skill(name="Python"), Skill(name="Docker"), Skill(name="AWS")],
            experience=[
                Experience(
                    title="Software Engineer",
                    company="Google",
                    location="Mountain View",
                    start_date=date(2020, 1, 1),
                    end_date=date(2023, 1, 1),
                    current=False,
                    description="Led development of ML pipeline using Python and TensorFlow"
                )
            ],
            education=[
                Education(
                    institution="MIT",
                    degree="BS Computer Science",
                    graduation_date=date(2019, 5, 1)
                )
            ]
        )
    
    def test_validator_initialization(self):
        """Test validator can be initialized"""
        validator = create_validator()
        assert validator is not None
        assert validator.version == "1.0.0"
    
    def test_valid_improvement_passes(self):
        """Test that valid improvements pass validation"""
        original = "Led development of ML pipeline"
        suggested = "Architected and led development of ML pipeline"
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        assert result.valid
        assert len(result.hallucinated_entities) == 0
        assert result.risk_level == RiskLevel.LOW
    
    def test_hallucinated_technology_detected(self):
        """
        CRITICAL: Test hallucination detection
        SYSTEM.md Section 5: No new claims
        """
        original = "Led development using Python"
        suggested = "Led development using Python, Kubernetes, and Rust"
        # Kubernetes and Rust not in resume!
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        # Should detect hallucination
        assert not result.valid
        assert len(result.hallucinated_entities) > 0
        assert result.risk_level == RiskLevel.HIGH
    
    def test_placeholder_detection(self):
        """Test that placeholders are detected and flagged"""
        original = "Improved performance"
        suggested = "Improved API performance by [X%]"
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        # Should be valid but require user input
        assert result.valid or result.requires_user_input
        assert len(result.placeholders) > 0
        assert "[X%]" in result.placeholders[0]
    
    def test_existing_technology_allowed(self):
        """Test that existing resume technologies can be added"""
        original = "Led development"
        suggested = "Led development using Python and Docker"
        # Python and Docker are in resume.skills
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        # Should pass - technologies exist in resume
        assert result.valid
        assert len(result.hallucinated_entities) == 0
    
    def test_risk_assessment(self):
        """Test risk level assessment"""
        # Low risk: Minor improvement
        original = "Worked on project"
        suggested = "Led project"
        result1 = self.validator.validate_suggestion(original, suggested, self.resume)
        assert result1.risk_level == RiskLevel.LOW
        
        # Medium risk: Multiple placeholders
        original2 = "Improved system"
        suggested2 = "Improved system performance by [X%], reduced latency by [Y%], increased throughput by [Z%]"
        result2 = self.validator.validate_suggestion(original2, suggested2, self.resume)
        assert result2.risk_level == RiskLevel.MEDIUM
        
        # High risk: Hallucination
        original3 = "Engineer at Company"
        suggested3 = "Senior Lead Architect at MegaCorp using Haskell and Scala"
        result3 = self.validator.validate_suggestion(original3, suggested3, self.resume)
        assert result3.risk_level == RiskLevel.HIGH
    
    def test_metric_validation(self):
        """Test that metrics are validated"""
        original = "Managed team"
        
        # With placeholder - OK
        suggested1 = "Managed team of [X] engineers"
        result1 = self.validator.validate_suggestion(original, suggested1, self.resume)
        assert result1.valid or result1.requires_user_input
        
        # With specific metric - check if it's a hallucination
        suggested2 = "Managed team of 50 engineers"
        result2 = self.validator.validate_suggestion(original, suggested2, self.resume)
        # Should flag as needs validation (number not in original)
    
    def test_company_name_validation(self):
        """Test that company names can't be fabricated"""
        original = "Software Engineer"
        suggested = "Software Engineer at Facebook"
        # Facebook not in resume
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        # Should detect as hallucination
        assert not result.valid or "Facebook" not in self.resume.raw_text
    
    def test_date_fabrication_detection(self):
        """Test that dates can't be invented"""
        original = "Worked on project"
        suggested = "Worked on project from 2015-2018"
        # These dates don't exist in resume
        
        result = self.validator.validate_suggestion(
            original, suggested, self.resume
        )
        
        # Should be flagged (dates not in context)
    
    def test_batch_validation(self):
        """Test validating multiple suggestions"""
        suggestions = [
            {
                "original": "Led team",
                "suggested": "Led cross-functional team"
            },
            {
                "original": "Used Python",
                "suggested": "Used Python and Go"  # Go not in resume
            }
        ]
        
        results = self.validator.validate_batch(suggestions, self.resume)
        
        assert len(results) == 2
        assert results[0].valid  # First is OK
        assert not results[1].valid  # Second has hallucination
    
    def test_entity_extraction(self):
        """Test entity extraction from text"""
        text = "Led development using Python, Docker, and AWS for 3 years, improving performance by 40%"
        
        entities = self.validator._extract_entities(text)
        
        # Should extract technologies
        assert "Python" in entities or "Docker" in entities or "AWS" in entities
        
        # Should extract metrics
        assert any("40" in str(e) or "%" in str(e) for e in entities)
    
    def test_placeholder_patterns(self):
        """Test various placeholder patterns are detected"""
        placeholders = [
            "[X%]",
            "[metric]",
            "<value>",
            "{number}",
            "XX engineers"
        ]
        
        for placeholder in placeholders:
            assert self.validator._is_placeholder(placeholder), \
                f"Failed to detect placeholder: {placeholder}"


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
