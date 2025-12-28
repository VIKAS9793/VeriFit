"""
Resume Parser Service
Deterministic resume parsing with LLM fallback for edge cases
Compliance: SYSTEM.md Section 5 (Resume Parser Agent)

Principles:
- Deterministic first
- LLM only for edge cases
- Verbatim extraction (no interpretation)
"""

import re
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from pydantic import ValidationError
import pypdf
import pdfplumber
from docx import Document as DocxDocument

from src.models.resume import Resume, Experience, Education, Skill
# Import LLMService type hint only to avoid circular imports if needed, or just type as Any
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.services.llm import LLMService


class ParserException(Exception):
    """Base exception for parsing errors"""
    pass


class UnsupportedFormatError(ParserException):
    """Raised when file format is not supported"""
    pass


class ResumeParser:
    """
    Deterministic resume parser
    
    Strategy:
    1. Extract raw text (PDF/DOCX/TXT)
    2. Apply deterministic rules (regex, structure analysis)
    3. Fall back to LLM only for ambiguous cases
    4. Return structured Resume model
    """
    
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt'}
    
    def __init__(self, use_llm_fallback: bool = False, llm_service: Optional['LLMService'] = None):
        """
        Initialize parser
        
        Args:
            use_llm_fallback: Enable LLM for extraction (default: False)
            llm_service: Instance of LLMService
        """
        self.use_llm_fallback = use_llm_fallback
        self.llm_service = llm_service
        
    def parse_file(self, file_path: Path) -> Resume:
        """
        Parse resume from file
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Structured Resume object
            
        Raises:
            UnsupportedFormatError: If file format not supported
            ParserException: If parsing fails
        """
        if not file_path.exists():
            raise ParserException(f"File not found: {file_path}")
            
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported format: {suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Extract raw text
        raw_text = self._extract_text(file_path, suffix)
        
        # Intelligent Parsing via LLM (if enabled and available)
        if self.use_llm_fallback and self.llm_service:
            try:
                print("DEBUG: Using LLM for parsing")
                resume_dict = self.llm_service.parse_resume_text(raw_text)
                resume_dict['source_file'] = file_path.name
                resume_dict['parsed_at'] = date.today()
                resume_dict['parser_version'] = "2.0.0-llm"
                
                # Create Resume model
                return Resume(**resume_dict)
            except Exception as e:
                print(f"ERROR: LLM Parsing failed: {e}. Falling back to regex.")
                # Fallthrough to regex
        
        # Parse structured data (Regex/Deterministic)
        resume_data = self._parse_resume_data(raw_text, file_path.name)
        
        # Create Resume model (validates data)
        try:
            resume = Resume(**resume_data)
            return resume
        except ValidationError as e:
            raise ParserException(f"Validation failed: {e}")
    
    def _extract_text(self, file_path: Path, suffix: str) -> str:
        """Extract raw text from file based on format"""
        if suffix == '.pdf':
            return self._extract_pdf_text(file_path)
        elif suffix == '.docx':
            return self._extract_docx_text(file_path)
        elif suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        else:
            raise UnsupportedFormatError(f"Unknown format: {suffix}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF with fallback strategy"""
        text = ""
        
        # Try pdfplumber first (better layout preservation)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception:
            pass  # Fallback to pypdf
        
        # Fallback to pypdf
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise ParserException(f"PDF extraction failed: {e}")
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ParserException(f"DOCX extraction failed: {e}")
    
    def _parse_resume_data(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Parse structured data from raw text
        
        Strategy: Deterministic pattern matching
        """
        data = {
            "source_file": filename,
            "parsed_at": date.today(),
            "parser_version": "1.0.0"
        }
        
        # Extract contact information (deterministic)
        data.update(self._extract_contact_info(text))
        
        # Extract sections
        data["experience"] = self._extract_experience(text)
        data["education"] = self._extract_education(text)
        data["skills"] = self._extract_skills(text)
        data["certifications"] = self._extract_certifications(text)
        
        # Extract summary if present
        summary = self._extract_summary(text)
        if summary:
            data["summary"] = summary
        
        return data
    
    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information using regex patterns"""
        contact = {}
        
        # Extract email (deterministic regex)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact["email"] = emails[0]  # Take first email found
        
        # Extract phone (various formats)
        # Source: https://stackoverflow.com/a/16699507 (700+ upvotes, battle-tested)
        # Matches: (123) 456-7890, 123-456-7890, 123.456.7890, +1 (123) 456-7890, etc.
        # Using non-capturing group (?:...) to avoid tuple returns
        phone_pattern = r'(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact["phone"] = phones[0].strip()
        
        # Extract LinkedIn URL
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
        linkedin_urls = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_urls:
            contact["linkedin_url"] = linkedin_urls[0]
        
        # Extract GitHub URL
        github_pattern = r'https?://(?:www\.)?github\.com/[\w-]+'
        github_urls = re.findall(github_pattern, text, re.IGNORECASE)
        if github_urls:
            contact["github_url"] = github_urls[0]
        
        # Extract name (first non-empty line, heuristic)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Assume first line is name (common resume convention)
            potential_name = lines[0]
            # Validate it looks like a name (not an email, URL, etc.)
            if not re.search(r'[@:/]', potential_name):
                contact["full_name"] = potential_name
            else:
                # Fallback: use "Unknown" (SYSTEM.md: refuse to invent)
                contact["full_name"] = "Unknown"
        else:
            contact["full_name"] = "Unknown"
        
        return contact
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience
        
        Note: This is a simplified deterministic parser
        Real implementation would use more sophisticated patterns
        """
        # TODO: Implement deterministic experience extraction
        # For now, return empty list (honest: we don't have data)
        return []
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        # TODO: Implement deterministic education extraction
        return []
    
    def _extract_skills(self, text: str) -> List[Dict[str, str]]:
        """Extract skills section"""
        skills = []
        
        # Look for skills section
        skills_pattern = r'(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES)(.*?)(?=\n[A-Z]{2,}|\Z)'
        match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            skills_text = match.group(1)
            # Split by common delimiters
            skill_items = re.split(r'[,•\n]', skills_text)
            for item in skill_items:
                skill_name = item.strip()
                if skill_name and len(skill_name) > 1:
                    skills.append({"name": skill_name})
        
        return skills
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        # TODO: Implement deterministic certification extraction
        return []
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        # Look for summary section
        summary_pattern = r'(?:SUMMARY|PROFESSIONAL SUMMARY|PROFILE)(.*?)(?=\n[A-Z]{2,}|\Z)'
        match = re.search(summary_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            summary = match.group(1).strip()
            if summary:
                return summary
        
        return None


# Factory function
def create_parser(use_llm: bool = False, llm_service: Any = None) -> ResumeParser:
    """
    Create resume parser instance
    
    Args:
        use_llm: Enable LLM fallback
        llm_service: LLM Service instance
        
    Returns:
        ResumeParser instance
    """
    return ResumeParser(use_llm_fallback=use_llm, llm_service=llm_service)
