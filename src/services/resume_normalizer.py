"""
Resume Normalization Service
Structural normalization only - NO semantic content modification
Compliance: SYSTEM.md Section 5 (No inference or interpretation)

Operations:
- Whitespace cleanup
- Date standardization (via Pydantic)
- Phone number formatting
- Duplicate removal
- Case consistency for headings

What it DOES NOT do:
- Rewrite content
- Fix grammar/spelling
- Add missing information
- Modify job descriptions or bullet points
"""

import re
from typing import List, Optional, Set
from datetime import date

from src.models.resume import Resume, Experience, Education, Skill


class ResumeNormalizer:
    """
    Structural resume normalizer
    
    Principle: Clean formatting, preserve semantic content
    SYSTEM.md Section 5: No semantic edits
    """
    
    def __init__(self):
        """Initialize normalizer"""
        pass
    
    def normalize(self, resume: Resume) -> Resume:
        """
        Normalize resume structure
        
        Args:
            resume: Parsed Resume object
            
        Returns:
            Normalized Resume with cleaned formatting
            
        Note: All semantic content preserved exactly
        """
        # Create normalized data dict
        normalized_data = resume.model_dump()
        
        # 1. Clean text fields (whitespace only)
        normalized_data = self._clean_text_fields(normalized_data)
        
        # 2. Standardize phone format
        if normalized_data.get('phone'):
            normalized_data['phone'] = self._standardize_phone(normalized_data['phone'])
        
        # 3. Deduplicate lists
        if normalized_data.get('skills'):
            normalized_data['skills'] = self._deduplicate_skills(normalized_data['skills'])
        
        if normalized_data.get('certifications'):
            normalized_data['certifications'] = self._deduplicate_list(normalized_data['certifications'])
        
        if normalized_data.get('languages'):
            normalized_data['languages'] = self._deduplicate_list(normalized_data['languages'])
        
        # 4. Clean experience and education (whitespace only)
        if normalized_data.get('experience'):
            normalized_data['experience'] = [
                self._clean_experience(exp) for exp in normalized_data['experience']
            ]
        
        if normalized_data.get('education'):
            normalized_data['education'] = [
                self._clean_education(edu) for edu in normalized_data['education']
            ]
        
        # Recreate Resume object (Pydantic will re-validate and re-sort)
        return Resume(**normalized_data)
    
    def _clean_text_fields(self, data: dict) -> dict:
        """
        Clean whitespace from text fields
        
        Preserves: All content, just removes extra whitespace
        """
        # Clean string fields
        for field in ['full_name', 'location', 'summary']:
            if data.get(field):
                data[field] = self._normalize_whitespace(data[field])
        
        return data
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text
        
        - Trim leading/trailing whitespace
        - Replace multiple spaces with single space
        - Remove extra newlines
        
        Preserves: Original wording exactly
        """
        # Replace multiple spaces/tabs with single space
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        return text
    
    def _standardize_phone(self, phone: str) -> str:
        """
        Standardize phone number format
        
        Target format: (XXX) XXX-XXXX or +CC (XXX) XXX-XXXX
        
        Research: Industry standard ATS-friendly format
        Source: https://stackoverflow.com/a/16699507
        """
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        # Check for country code
        if len(digits) == 11 and digits[0] == '1':
            # US number with country code: 1XXXXXXXXXX
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif len(digits) == 10:
            # Standard 10-digit US number
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
        else:
            # Non-standard format, return as-is (don't invent)
            return phone
    
    def _deduplicate_skills(self, skills: List[dict]) -> List[dict]:
        """
        Remove duplicate skills (case-insensitive)
        
        Preserves: First occurrence of each unique skill
        """
        seen: Set[str] = set()
        unique_skills = []
        
        for skill in skills:
            skill_name_lower = skill['name'].lower()
            if skill_name_lower not in seen:
                seen.add(skill_name_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _deduplicate_list(self, items: List[str]) -> List[str]:
        """
        Remove duplicates from string list (case-insensitive)
        
        Preserves: First occurrence, original case
        """
        seen: Set[str] = set()
        unique_items = []
        
        for item in items:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                unique_items.append(item)
        
        return unique_items
    
    def _clean_experience(self, exp: dict) -> dict:
        """Clean whitespace from experience entry"""
        if exp.get('company'):
            exp['company'] = self._normalize_whitespace(exp['company'])
        if exp.get('title'):
            exp['title'] = self._normalize_whitespace(exp['title'])
        if exp.get('location'):
            exp['location'] = self._normalize_whitespace(exp['location'])
        if exp.get('description'):
            exp['description'] = self._normalize_whitespace(exp['description'])
        
        # Clean each responsibility (preserve as separate items)
        if exp.get('responsibilities'):
            exp['responsibilities'] = [
                self._normalize_whitespace(resp) 
                for resp in exp['responsibilities']
                if resp.strip()  # Remove empty strings
            ]
        
        return exp
    
    def _clean_education(self, edu: dict) -> dict:
        """Clean whitespace from education entry"""
        if edu.get('institution'):
            edu['institution'] = self._normalize_whitespace(edu['institution'])
        if edu.get('degree'):
            edu['degree'] = self._normalize_whitespace(edu['degree'])
        if edu.get('field_of_study'):
            edu['field_of_study'] = self._normalize_whitespace(edu['field_of_study'])
        if edu.get('location'):
            edu['location'] = self._normalize_whitespace(edu['location'])
        
        return edu


# Factory function
def create_normalizer() -> ResumeNormalizer:
    """Create resume normalizer instance"""
    return ResumeNormalizer()
