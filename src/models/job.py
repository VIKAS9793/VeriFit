"""
Job Data Models
Pydantic models for job posting data structures
Compliance: SYSTEM.md Section 5 (Job Ingestion Agent - ≤7-day active roles only)
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class JobType(str, Enum):
    """Employment type"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class ExperienceLevel(str, Enum):
    """Required experience level"""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class JobRequirement(BaseModel):
    """Individual job requirement"""
    category: str = Field(..., description="Requirement category (e.g., 'Education', 'Experience')")
    description: str = Field(..., description="Requirement description (verbatim)")
    is_required: bool = Field(True, description="Required vs. preferred")
    
    model_config = ConfigDict(frozen=True)


class Job(BaseModel):
    """
    Job posting data structure
    
    Principles (SYSTEM.md Section 5):
    - Only active jobs ≤7 days old
    - Verified sources only
    - Verbatim extraction from job postings
    """
    
    # Job Identity
    job_id: str = Field(..., description="Unique identifier from source")
    title: str = Field(..., description="Job title (verbatim)")
    company: str = Field(..., description="Company name (verbatim)")
    
    # Job Details
    description: str = Field(..., description="Full job description (verbatim)")
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities (verbatim bullet points)"
    )
    requirements: List[JobRequirement] = Field(
        default_factory=list,
        description="Structured requirements"
    )
    
    # Job Metadata
    job_type: JobType = Field(..., description="Employment type")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Required experience level")
    location: str = Field(..., description="Job location (verbatim)")
    is_remote: bool = Field(False, description="Remote work option")
    is_hybrid: bool = Field(False, description="Hybrid work option")
    
    # Compensation (if stated)
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary if stated")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary if stated")
    salary_currency: str = Field("USD", description="Salary currency")
    
    # Skills
    required_skills: List[str] = Field(
        default_factory=list,
        description="Required skills (extracted/verbatim)"
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have skills"
    )
    
    # Source Information (for auditability per SYSTEM.md Section 0)
    source_url: HttpUrl = Field(..., description="Original job posting URL")
    source_platform: str = Field(..., description="Platform (e.g., 'LinkedIn', 'Indeed')")
    posted_date: date = Field(..., description="Job posting date")
    scraped_at: datetime = Field(..., description="When we scraped this job")
    expires_at: Optional[date] = Field(None, description="Application deadline if stated")
    
    # Verification flags (SYSTEM.md Section 5: Verified sources only)
    is_verified: bool = Field(False, description="Source verification status")
    is_active: bool = Field(True, description="Job still active")
    
    @field_validator('posted_date')
    @classmethod
    def validate_age(cls, v):
        """Enforce ≤7-day age requirement (SYSTEM.md Section 5)"""
        age_days = (date.today() - v).days
        if age_days > 7:
            raise ValueError(
                f"Job posted {age_days} days ago exceeds 7-day limit "
                f"(SYSTEM.md Section 5: ≤7-day active roles only)"
            )
        return v
    
    @field_validator('salary_max')
    @classmethod
    def validate_salary_range(cls, v, info):
        """Ensure salary_max ≥ salary_min"""
        salary_min = info.data.get('salary_min')
        if v and salary_min and v < salary_min:
            raise ValueError('salary_max must be >= salary_min')
        return v
    
    def is_within_age_limit(self) -> bool:
        """Check if job is still within 7-day age limit"""
        age_days = (date.today() - self.posted_date).days
        return age_days <= 7
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "job_id": "linkedin-123456",
                "title": "Senior Python Engineer",
                "company": "Tech Innovations Inc.",
                "description": "We are seeking a Senior Python Engineer...",
                "job_type": "full_time",
                "experience_level": "senior",
                "location": "San Francisco, CA",
                "is_remote": True,
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "source_url": "https://linkedin.com/jobs/123456",
                "source_platform": "LinkedIn",
                "posted_date": "2025-12-27",
                "scraped_at": "2025-12-28T10:00:00",
                "is_verified": True
            }
        })
