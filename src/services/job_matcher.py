"""
Job Matching Engine
Deterministic, explainable job-resume matching
Compliance: SYSTEM.md Section 5 (Multi-factor explainable fit, no opaque ranking)

Matching Factors:
- Skill overlap (deterministic set intersection)
- Experience requirements
- Location match
- Education requirements
- Job age validation (≤7 days per SYSTEM.md)

What this DOES NOT do:
- Use opaque AI matching algorithms
- Claim to "predict perfect fit"
- Match to stale jobs (>7 days old)
"""

from typing import Optional, List, Set
from datetime import datetime, timedelta

from src.models.resume import Resume
from src.models.job import Job
from src.models.score import (
    JobMatchScore,
    ScoreExplanation,
    Evidence,
    EvidenceType,
    ScoreCategory
)


class JobMatcher:
    """
    Explainable job-resume matcher
    
    Principle: Deterministic matching with full evidence
    SYSTEM.md Section 5: Multi-factor, explainable, no opaque ranking
    """
    
    # Job age limit per SYSTEM.md Section 5
    MAX_JOB_AGE_DAYS = 7
    
    def __init__(self):
        """Initialize matcher"""
        self.matching_version = "1.0.0"
    
    def match(self, resume: Resume, job: Job) -> Optional[JobMatchScore]:
        """
        Match resume to job with explainable criteria
        
        Args:
            resume: Parsed and normalized Resume
            job: Job posting (must be ≤7 days old)
            
        Returns:
            JobMatchScore with evidence, or None if job too old
            
        Note: All scoring is deterministic and explainable
        """
        # CRITICAL: Validate job age (SYSTEM.md Section 5)
        if not self._validate_job_age(job):
            return None  # Reject stale jobs
        
        # Calculate each matching factor
        skill_score = self._match_skills(resume, job)
        experience_score = self._match_experience(resume, job)
        location_score = self._match_location(resume, job)
        education_score = self._match_education(resume, job)
        
        # Calculate weighted overall score
        overall_score = (
            skill_score.score * 0.40 +
            experience_score.score * 0.30 +
            location_score.score * 0.15 +
            education_score.score * 0.15
        )
        
        # Collect matched and missing skills for evidence
        resume_skill_names = {s.name.lower() for s in resume.skills}
        job_skill_names = {s.lower() for s in job.required_skills}  # Already strings
        
        matched_skills = list(resume_skill_names & job_skill_names)
        missing_skills = list(job_skill_names - resume_skill_names)
        
        # Generate recommendation based on overall score
        if overall_score >= 75:
            recommendation = "apply"
            reasons = [f"Strong match ({overall_score:.1f}%)", "Most requirements aligned"]
        elif overall_score >= 50:
            recommendation = "maybe"
            reasons = [f"Moderate match ({overall_score:.1f}%)", f"{len(missing_skills)} skills missing"]
        else:
            recommendation = "skip"
            reasons = [f"Weak match ({overall_score:.1f}%)", f"Only {len(matched_skills)} of {len(job_skill_names)} skills match"]
        
        return JobMatchScore(
            overall_match=round(overall_score, 1),
            skill_match=skill_score,
            experience_match=experience_score,
            location_match=location_score,
            education_match=education_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            job_id=job.job_id,
            resume_id=resume.source_file or "unknown",
            recommendation=recommendation,
            reasons=reasons,
            matched_at=datetime.utcnow()
        )
    
    def _validate_job_age(self, job: Job) -> bool:
        """
        Validate job posting age
        
        SYSTEM.md Section 5: ≤7-day active roles only
        """
        if not job.posted_date:
            # No posted date = cannot validate = reject
            return False
        
        age_days = (datetime.now().date() - job.posted_date).days
        return age_days <= self.MAX_JOB_AGE_DAYS
    
    def _match_skills(self, resume: Resume, job: Job) -> ScoreExplanation:
        """
        Match skills using deterministic set intersection
        
        Method: Exact skill name matching (case-insensitive)
        Weight: 40% of overall score
        """
        # Extract skill names (case-insensitive)
        resume_skills = {s.name.lower() for s in resume.skills}
        job_skills = {s.lower() for s in job.required_skills}  # Already strings
        
        if len(job_skills) == 0:
            # No required skills = perfect match
            return ScoreExplanation(
                component="Skill Match",
                score=100.0,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.KEYWORD_MATCH,
                    description="No specific skills required for this role",
                    data={"required_skills": 0},
                    weight=1.0
                )],
                explanation="Job has no specific skill requirements"
            )
        
        # Calculate overlap
        matched = resume_skills & job_skills
        match_percentage = (len(matched) / len(job_skills)) * 100
        
        evidence = Evidence(
            evidence_type=EvidenceType.KEYWORD_MATCH,
            description=f"Matched {len(matched)} of {len(job_skills)} required skills",
            data={
                "matched_skills": list(matched),
                "missing_skills": list(job_skills - resume_skills),
                "match_percentage": round(match_percentage, 1)
            },
            weight=1.0
        )
        
        explanation = (
            f"Skills matched: {len(matched)}/{len(job_skills)} "
            f"({round(match_percentage, 1)}%). "
            f"Missing: {', '.join(list(job_skills - resume_skills)[:5]) if (job_skills - resume_skills) else 'none'}."
        )
        
        return ScoreExplanation(
            component="Skill Match",
            score=round(match_percentage, 1),
            max_score=100.0,
            evidence=[evidence],
            explanation=explanation
        )
    
    def _match_experience(self, resume: Resume, job: Job) -> ScoreExplanation:
        """
        Match experience requirements
        
        Checks: Years of experience vs experience_level
        Weight: 30% of overall score
        """
        evidence_list = []
        score = 100.0
        
        # Calculate total years of experience
        total_years = self._calculate_years_experience(resume.experience)
        
        # Simple mapping: entry=0-2, mid=2-5, senior=5+, lead=8+
        required_years_map = {
            "entry_level": 0,
            "mid_level": 2,
            "senior": 5,
            "lead": 8,
            "executive": 10
        }
        
        # Check experience level match (if specified)
        if job.experience_level:
            required_years = required_years_map.get(job.experience_level.value, 0)
            
            if total_years >= required_years:
                evidence_list.append(Evidence(
                    evidence_type=EvidenceType.EXPERIENCE_COMPARISON,
                    description=f"Meets experience requirement: {total_years} years >= {required_years} years ({job.experience_level.value})",
                    data={
                        "candidate_years": total_years,
                        "required_level": job.experience_level.value,
                        "required_years": required_years,
                        "meets_requirement": True
                    },
                    weight=1.0
                ))
            else:
                # Penalize for insufficient experience
                gap = required_years - total_years
                penalty = min(gap * 10, 50)  # Max 50% penalty
                score -= penalty
                
                evidence_list.append(Evidence(
                    evidence_type=EvidenceType.EXPERIENCE_COMPARISON,
                    description=f"Below experience requirement: {total_years} years < {required_years} years ({job.experience_level.value})",
                    data={
                        "candidate_years": total_years,
                        "required_level": job.experience_level.value,
                        "required_years": required_years,
                        "gap_years": gap,
                        "meets_requirement": False
                    },
                    weight=1.0
                ))
                
            explanation = f"Candidate has {total_years} years. {'Meets' if total_years >= required_years else 'Below'} {job.experience_level.value} requirement ({required_years}+ years)."
        else:
            evidence_list.append(Evidence(
                evidence_type=EvidenceType.EXPERIENCE_COMPARISON,
                description="No specific experience level requirement",
                data={"candidate_years": total_years},
                weight=1.0
            ))
            explanation = f"Candidate has {total_years} years total experience. No specific requirement."
        
        return ScoreExplanation(
            component="Experience Match",
            score=max(0, score),
            max_score=100.0,
            evidence=evidence_list,
            explanation=explanation
        )
    
    def _match_location(self, resume: Resume, job: Job) -> ScoreExplanation:
        """
        Match location requirements
        
        Method: Exact location match or remote flag
        Weight: 15% of overall score
        """
        # Check if job is remote
        if job.is_remote:
            return ScoreExplanation(
                component="Location Match",
                score=100.0,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                    description="Job is remote - location not a factor",
                    data={"is_remote": True},
                    weight=1.0
                )],
                explanation="Remote position - location match not applicable"
            )
        
        # Check location match
        if job.location and resume.location:
            match = job.location.lower() == resume.location.lower()
            score = 100.0 if match else 0.0
            
            return ScoreExplanation(
                component="Location Match",
                score=score,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                    description=f"Location {'matches' if match else 'does not match'}",
                    data={
                        "job_location": job.location,
                        "resume_location": resume.location,
                        "match": match
                    },
                    weight=1.0
                )],
                explanation=f"Job location: {job.location}, Resume location: {resume.location}"
            )
        else:
            # No location specified = neutral
            return ScoreExplanation(
                component="Location Match",
                score=100.0,
                max_score=100.0,
                evidence=[Evidence(
                    evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                    description="Location requirements not specified",
                    data={"job_location": job.location, "resume_location": resume.location},
                    weight=1.0
                )],
                explanation="Location not a matching factor"
            )
    
    def _match_education(self, resume: Resume, job: Job) -> ScoreExplanation:
        """
        Match education requirements
        
        Method: Simple check (future: can extract from requirements)
        Weight: 15% of overall score
        """
        # For now, give full score if candidate has education
        # Future: Extract education requirements from job.requirements list
        has_education = len(resume.education) > 0
        
        score = 100.0 if has_education else 50.0  # Partial credit for no education listed
        
        return ScoreExplanation(
            component="Education Match",
            score=score,
            max_score=100.0,
            evidence=[Evidence(
                evidence_type=EvidenceType.STRUCTURE_ANALYSIS,
                description=f"Candidate {'has' if has_education else 'has no'} education listed",
                data={
                    "has_education": has_education,
                    "education_count": len(resume.education)
                },
                weight=1.0
            )],
            explanation=f"Candidate has {len(resume.education)} education entries listed"
        )
    
    def _calculate_years_experience(self, experiences: List) -> float:
        """
        Calculate total years of experience
        
        Note: Simplified calculation, assumes non-overlapping roles
        """
        from datetime import date
        
        total_days = 0
        for exp in experiences:
            if not exp.start_date:
                continue
            
            end = exp.end_date if exp.end_date else date.today()
            start = exp.start_date
            
            duration = (end - start).days
            total_days += duration
        
        return round(total_days / 365.25, 1)  # Account for leap years


# Factory function
def create_matcher() -> JobMatcher:
    """Create job matcher instance"""
    return JobMatcher()
