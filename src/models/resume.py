"""
Resume Data Models
Pydantic models for resume data structures
Compliance: SYSTEM.md Section 5 (Resume Parser Agent - Verbatim extraction)
"""

from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, ConfigDict


class SkillLevel(str, Enum):
    """Skill proficiency level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Individual skill with optional proficiency"""
    name: str = Field(..., description="Skill name (verbatim from resume)")
    level: Optional[SkillLevel] = Field(None, description="Proficiency level if stated")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience if stated")
    
    model_config = ConfigDict(frozen=True)


class Education(BaseModel):
    """Educational background"""
    institution: str = Field(..., description="School/University name (verbatim)")
    degree: str = Field(..., description="Degree/Certification (verbatim)")
    field_of_study: Optional[str] = Field(None, description="Major/Field (verbatim)")
    start_date: Optional[date] = Field(None, description="Start date if available")
    end_date: Optional[date] = Field(None, description="End/Expected end date")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA if stated")
    location: Optional[str] = Field(None, description="Location (verbatim)")
    is_current: bool = Field(False, description="Currently enrolled")
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Ensure end_date is after start_date"""
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    model_config = ConfigDict(frozen=True)


class Experience(BaseModel):
    """Work experience entry"""
    company: str = Field(..., description="Company name (verbatim)")
    title: str = Field(..., description="Job title (verbatim)")
    location: Optional[str] = Field(None, description="Job location (verbatim)")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date (None if current)")
    is_current: bool = Field(False, description="Currently employed here")
    description: Optional[str] = Field(None, description="Job description (verbatim)")
    responsibilities: List[str] = Field(default_factory=list, description="Bullet points (verbatim)")
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Ensure end_date is after start_date and not in future if not current"""
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        if v and not info.data.get('is_current') and v > date.today():
            raise ValueError('end_date cannot be in future for past positions')
        return v
    
    model_config = ConfigDict(frozen=True)


class Resume(BaseModel):
    """
    Complete resume data structure
    
    Principles (SYSTEM.md Section 5):
    - Verbatim extraction only
    - No inference or interpretation
    - Structured normalization permitted (dates, formats)
    - No semantic edits
    """
    
    # Personal Information (only what's on resume)
    full_name: str = Field(..., description="Full name (verbatim)")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number (verbatim format)")
    location: Optional[str] = Field(None, description="Location/Address (verbatim)")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[HttpUrl] = Field(None, description="Portfolio/Website URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    
    # Professional Summary
    summary: Optional[str] = Field(None, description="Professional summary (verbatim)")
    
    # Work Experience
    experience: List[Experience] = Field(
        default_factory=list,
        description="Work history in chronological order"
    )
    
    # Education
    education: List[Education] = Field(
        default_factory=list,
        description="Educational background in chronological order"
    )
    
    # Skills
    skills: List[Skill] = Field(
        default_factory=list,
        description="Technical and soft skills"
    )
    
    # Certifications
    certifications: List[str] = Field(
        default_factory=list,
        description="Professional certifications (verbatim)"
    )
    
    # Languages
    languages: List[str] = Field(
        default_factory=list,
        description="Languages spoken (verbatim)"
    )
    
    # Metadata (not from resume content)
    source_file: Optional[str] = Field(None, description="Original filename")
    parsed_at: Optional[date] = Field(None, description="Parsing timestamp")
    parser_version: str = Field("1.0.0", description="Parser version for auditability")
    
    @field_validator('experience')
    @classmethod
    def sort_experience_descending(cls, v):
        """Sort experience by start date (most recent first)"""
        return sorted(v, key=lambda x: x.start_date or date.min, reverse=True)
    
    @field_validator('education')
    @classmethod
    def sort_education_descending(cls, v):
        """Sort education by end date (most recent first)"""
        return sorted(v, key=lambda x: x.end_date or date.min, reverse=True)
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "full_name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "summary": "Experienced software engineer with 5+ years in Python and AI",
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Senior Software Engineer",
                        "start_date": "2020-01-01",
                        "is_current": True,
                        "responsibilities": ["Led team of 5 engineers", "Built ML pipeline"]
                    }
                ],
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 5},
                    {"name": "Machine Learning", "level": "advanced"}
                ]
            }
        })
