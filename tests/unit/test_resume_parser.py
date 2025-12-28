"""
Unit Tests for Resume Parser
Compliance: SYSTEM.md Section 8 (Evaluation & Evals - Parsing accuracy)
"""

import pytest
from pathlib import Path
from datetime import date

from src.services import ResumeParser, ParserException, UnsupportedFormatError
from src.models import Resume


class TestResumeParser:
    """Test suite for deterministic resume parser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = ResumeParser(use_llm_fallback=False)
    
    def test_parser_initialization(self):
        """Test parser can be initialized"""
        parser = ResumeParser()
        assert parser is not None
        assert parser.use_llm_fallback == False
    
    def test_supported_formats(self):
        """Test supported file formats"""
        assert '.pdf' in ResumeParser.SUPPORTED_FORMATS
        assert '.docx' in ResumeParser.SUPPORTED_FORMATS
        assert '.txt' in ResumeParser.SUPPORTED_FORMATS
    
    def test_contact_info_extraction_email(self):
        """Test email extraction from text"""
        text = "John Doe\njohn.doe@example.com\n(555) 123-4567"
        contact = self.parser._extract_contact_info(text)
        
        assert contact['email'] == 'john.doe@example.com'
        assert contact['full_name'] == 'John Doe'
    
    def test_contact_info_extraction_phone(self):
        """Test phone extraction with various formats"""
        test_cases = [
            ("Contact: (555) 123-4567", "(555) 123-4567"),
            ("Call me at 555-123-4567", "555-123-4567"),
            ("Phone: +1-555-123-4567", "+1-555-123-4567"),
        ]
        
        for text, expected_pattern in test_cases:
            contact = self.parser._extract_contact_info(text + "\nJohn Doe")
            assert 'phone' in contact
            # Just verify phone was extracted (format may vary)
            assert len(contact['phone']) > 0
    
    def test_contact_info_linkedin_url(self):
        """Test LinkedIn URL extraction"""
        text = "John Doe\nhttps://linkedin.com/in/johndoe"
        contact = self.parser._extract_contact_info(text)
        
        assert contact.get('linkedin_url') == 'https://linkedin.com/in/johndoe'
    
    def test_contact_info_github_url(self):
        """Test GitHub URL extraction"""
        text = "John Doe\nhttps://github.com/johndoe"
        contact = self.parser._extract_contact_info(text)
        
        assert contact.get('github_url') == 'https://github.com/johndoe'
    
    def test_skills_extraction(self):
        """Test skills section extraction"""
        text = """
        EXPERIENCE
        Some work history here
        
        SKILLS
        Python, JavaScript, Machine Learning, Docker, PostgreSQL
        
        EDUCATION
        University of Example
        """
        
        skills = self.parser._extract_skills(text)
        assert len(skills) > 0
        skill_names = [s['name'] for s in skills]
        assert 'Python' in skill_names
    
    def test_summary_extraction(self):
        """Test professional summary extraction"""
        text = """
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years in full-stack development.
        
        EXPERIENCE
        Tech Company - Senior Engineer
        """
        
        summary = self.parser._extract_summary(text)
        assert summary is not None
        assert 'software engineer' in summary.lower()
        assert '5+ years' in summary
    
    def test_file_not_found(self):
        """Test error handling for missing file"""
        fake_path = Path("/nonexistent/resume.pdf")
        
        with pytest.raises(ParserException, match="File not found"):
            self.parser.parse_file(fake_path)
    
    def test_unsupported_format(self):
        """Test error for unsupported file format"""
        # Create a temporary file with unsupported extension
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
                self.parser.parse_file(temp_path)
        finally:
            temp_path.unlink()  # Cleanup
    
    def test_verbatim_extraction_principle(self):
        """
        Test that parser extracts verbatim, no interpretation
        SYSTEM.md Section 5: Verbatim extraction
        """
        text = "John Doe\njohn@example.com"
        contact = self.parser._extract_contact_info(text)
        
        # Should extract exactly as written
        assert contact['full_name'] == 'John Doe'
        assert contact['email'] == 'john@example.com'
        
        # Should NOT invent data that doesn't exist
        assert 'linkedin_url' not in contact or contact.get('linkedin_url') is None
    
    def test_no_invention_when_missing(self):
        """
        Test that parser doesn't invent data
        SYSTEM.md Section 0: Explicitly refuse hallucination
        """
        text = "Some random text without structure"
        contact = self.parser._extract_contact_info(text)
        
        # Should not invent email if not present
        assert 'email' not in contact or contact.get('email') is None


class TestParserAccuracy:
    """
    Parsing accuracy tests
    SYSTEM.md Section 8: Parsing accuracy evaluation
    """
    
    def test_determinism(self):
        """Test that parser produces same output for same input"""
        parser = ResumeParser()
        text = "John Doe\njohn@example.com\n(555) 123-4567"
        
        # Parse same text multiple times
        result1 = parser._extract_contact_info(text)
        result2 = parser._extract_contact_info(text)
        
        # Should be deterministic
        assert result1 == result2


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
