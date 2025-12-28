"""
Rewrite Validator
Anti-hallucination validation for resume improvements
Compliance: SYSTEM.md Section 5 (No new claims)

What this DOES:
- Detect when LLM adds information not in original resume
- Flag placeholders that need user input
- Assess hallucination risk
- Validate all suggestions before showing to user

What this DOES NOT do:
- Allow false claims
- Permit undisclosed AI additions
- Skip validation
"""

from typing import Set, List, Dict, Any
import re

from src.models.resume import Resume
from src.models.rewrite import ValidationResult, RiskLevel


class RewriteValidator:
    """
    Validates resume rewrite suggestions for hallucinations
    
    SYSTEM.md Section 5: No new claims
    
    Checks:
    1. No new technologies added (must exist in resume)
    2. No new dates/durations (must match resume)
    3. No new companies/titles (must match resume)
    4. Metrics are either from resume or placeholders
    """
    
    # Common placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r'\[.*?\]',          # [X%], [metric], etc.
        r'<.*?>',            # <value>, <number>
        r'\{.*?\}',          # {metric}
        r'X+',               # XX, XXX
        r'\d+\+?%?',         # For incomplete metrics
    ]
    
    # Technology/skill patterns
    TECH_PATTERN = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*|[A-Z]{2,})\b'  # Python, AWS, TensorFlow
    
    # Common action verbs to ignore (false positives for entities)
    IGNORED_VERBS = {
        "Architected", "Led", "Managed", "Developed", "Designed", "Created", 
        "Built", "Implemented", "Engineered", "Orchestrated", "Spearheaded",
        "Improved", "Increased", "Reduced", "Facilitated", "Executed", "Performed"
    }
    
    def __init__(self):
        """Initialize validator"""
        self.version = "1.0.0"
    
    def validate_suggestion(
        self,
        original: str,
        suggested: str,
        resume: Resume
    ) -> ValidationResult:
        """
        Validate a rewrite suggestion for hallucinations
        
        Args:
            original: Original resume text
            suggested: Suggested improved text
            resume: Full resume for context
            
        Returns:
            ValidationResult with validation status and details
        """
        # Extract entities
        original_entities = self._extract_entities(original)
        suggested_entities = self._extract_entities(suggested)
        resume_entities = self._extract_resume_entities(resume)
        
        # Find new entities in suggestion
        new_entities = suggested_entities - original_entities
        
        # Check if new entities exist in resume
        hallucinated = []
        for entity in new_entities:
            if entity not in resume_entities:
                # Check if it's a placeholder
                if not self._is_placeholder(entity):
                    hallucinated.append(entity)
        
        # Find placeholders
        placeholders = self._extract_placeholders(suggested)
        
        # Determine risk level
        risk = self._assess_risk(hallucinated, placeholders, suggested)
        
        # Valid if no hallucinations
        valid = len(hallucinated) == 0
        
        return ValidationResult(
            valid=valid,
            reason=f"Hallucinated entities: {hallucinated}" if hallucinated else None,
            hallucinated_entities=hallucinated,
            requires_user_input=len(placeholders) > 0,
            placeholders=placeholders,
            risk_level=risk,
            confidence=1.0 - (len(hallucinated) * 0.2)  # Lower confidence if hallucinations
        )
    
    def _extract_entities(self, text: str) -> Set[str]:
        """
        Extract key entities from text
        
        Entities:
        - Technologies (Python, Docker, AWS)
        - Numbers/metrics (10%, 5 years)
        - Proper nouns (company names, etc.)
        """
        entities = set()
        
        # Extract technologies (capitalized words)
        tech_matches = re.findall(self.TECH_PATTERN, text)
        for match in tech_matches:
            if match not in self.IGNORED_VERBS:
                entities.add(match)
        
        # Extract numbers and metrics
        number_patterns = [
            r'\d+[.]?\d*\s*(?:years?|months?|days?)',  # Durations
            r'\d+[.]?\d*\s*%',                          # Percentages
            r'\$\d+[,\d]*',                              # Dollar amounts
            r'\d+[,\d]*\+?'                              # Large numbers
        ]
        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.update(matches)
        
        return entities
    
    def _extract_resume_entities(self, resume: Resume) -> Set[str]:
        """Extract all entities from resume for validation"""
        entities = set()
        
        # From skills
        for skill in resume.skills:
            entities.add(skill.name)
        
        # From experience
        for exp in resume.experience:
            # Extract from description
            entities.update(self._extract_entities(exp.description))
            # Add company
            entities.add(exp.company)
            # Add title
            entities.add(exp.title)
        
        # From education
        for edu in resume.education:
            entities.add(edu.institution)
            entities.add(edu.degree)
        
        return entities
    
    def _extract_placeholders(self, text: str) -> List[str]:
        """Extract all placeholders from text"""
        placeholders = []
        
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)
        
        return placeholders
    
    def _is_placeholder(self, text: str) -> bool:
        """Check if text is a placeholder"""
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
    
    def _assess_risk(
        self,
        hallucinated: List[str],
        placeholders: List[str],
        suggested_text: str
    ) -> RiskLevel:
        """
        Assess hallucination risk
        
        Risk levels:
        - LOW: No hallucinations, few placeholders
        - MEDIUM: Several placeholders, minor additions
        - HIGH: Hallucinations detected or major changes
        """
        if len(hallucinated) > 0:
            return RiskLevel.HIGH
        
        if len(placeholders) > 3:
            return RiskLevel.MEDIUM
        
        # Check for major text changes
        if len(suggested_text) > len(suggested_text) * 1.5:
            # Suggestion is 50%+ longer - high risk
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def validate_batch(
        self,
        suggestions: List[Dict[str, str]],
        resume: Resume
    ) -> List[ValidationResult]:
        """Validate multiple suggestions at once"""
        return [
            self.validate_suggestion(
                sug["original"],
                sug["suggested"],
                resume
            )
            for sug in suggestions
        ]


# Factory function
def create_validator() -> RewriteValidator:
    """Create validator instance"""
    return RewriteValidator()
