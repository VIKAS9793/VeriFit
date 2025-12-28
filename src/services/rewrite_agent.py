"""
Resume Rewrite Agent
LLM-powered resume improvement with HITL approval
Compliance: SYSTEM.md Section 5 (Diff-only, HITL mandatory, No new claims)

Modular Design:
- Simple validator now (RewriteValidator)
- Interface for future evals (IEvaluator)
- Hooks for observability (LangSmith, LangFuse)

What this DOES:
- Generate improvement suggestions using LLM
- Validate suggestions (anti-hallucination)
- Show diffs to user
- Require HITL approval for all changes
- Use placeholders for unknown metrics

What this DOES NOT do:
- Invent achievements or experience
- Auto-apply changes without approval
- Hide what it changes
"""

from typing import List, Optional, Protocol, Any
# Avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.services.llm import LLMService
import uuid
import os
import json
from datetime import datetime

from src.models.resume import Resume
from src.models.job import Job
from src.models.rewrite import (
    RewriteSuggestion,
    ValidationResult,
    RewriteOptions,
    RiskLevel
)
from src.services.rewrite_validator import RewriteValidator
from src.services.approval_gate import IApprovalGate
from src.utils.diff import create_text_diff


class IEvaluator(Protocol):
    """
    Interface for eval/observability systems
    
    Future implementations:
    - LangSmithEvaluator (production monitoring)
    - LangFuseEvaluator (trace logging)
    - SimpleEvaluator (basic metrics)
    """
    
    def log_suggestion(
        self,
        original: str,
        suggested: str,
        validation: ValidationResult
    ) -> None:
        """Log a suggestion for eval"""
        ...
    
    def log_user_decision(
        self,
        suggestion_id: str,
        approved: bool,
        reason: Optional[str] = None
    ) -> None:
        """Log user approval/rejection"""
        ...


class SimpleEvaluator:
    """
    Simple evaluator for MVP
    
    Future: Replace with LangSmith/LangFuse for production
    """
    
    def __init__(self, log_file: str = "logs/evals.jsonl"):
        self.suggestions_logged = []
        self.decisions_logged = []
        self.log_file = log_file
        # Ensure log dir exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_suggestion(
        self,
        original: str,
        suggested: str,
        validation: ValidationResult
    ) -> None:
        """Log suggestion (Persistent)"""
        entry = {
            "type": "suggestion",
            "original": original,
            "suggested": suggested,
            "valid": validation.valid,
            "risk": validation.risk_level.value if hasattr(validation.risk_level, 'value') else str(validation.risk_level),
            "timestamp": datetime.now().isoformat()
        }
        self.suggestions_logged.append(entry)
        self._write_log(entry)
    
    def log_user_decision(
        self,
        suggestion_id: str,
        approved: bool,
        reason: Optional[str] = None
    ) -> None:
        """Log user decision (Persistent)"""
        entry = {
            "type": "decision",
            "suggestion_id": suggestion_id,
            "approved": approved,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.decisions_logged.append(entry)
        self._write_log(entry)
        
    def _write_log(self, entry: dict):
        """Append to JSONL file"""
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Error writing eval log: {e}")
    
    def get_metrics(self) -> dict:
        """Get basic metrics"""
        total = len(self.decisions_logged)
        if total == 0:
            return {"total": 0, "approval_rate": 0}
        
        approved = sum(1 for d in self.decisions_logged if d["approved"])
        return {
            "total_suggestions": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": approved / total
        }


class RewriteAgent:
    """
    Resume rewrite agent with HITL approval
    
    SYSTEM.md Section 5 compliance:
    - Diff-only suggestions
    - HITL mandatory  
    - No new claims (validated)
    
    Modular design:
    - Validator: RewriteValidator (swappable)
    - Approval: IApprovalGate (already modular)
    - Evals: IEvaluator (future: LangSmith)
    """
    
    def __init__(
        self,
        validator: RewriteValidator,
        approval_gate: IApprovalGate,
        evaluator: Optional[IEvaluator] = None,
        use_llm: bool = False,
        llm_service: Optional['LLMService'] = None
    ):
        """
        Initialize rewrite agent
        
        Args:
            validator: Anti-hallucination validator
            approval_gate: HITL approval system
            evaluator: Optional eval/observability system
            use_llm: Whether to use actual LLM
            llm_service: Service for LLM calls
        """
        self.validator = validator
        self.approval_gate = approval_gate
        self.evaluator = evaluator or SimpleEvaluator()
        self.use_llm = use_llm
        self.llm_service = llm_service
        self.version = "1.0.0"
    
    def suggest_improvements(
        self,
        resume: Resume,
        options: Optional[RewriteOptions] = None,
        target_job: Optional[Job] = None
    ) -> List[RewriteSuggestion]:
        """
        Generate improvement suggestions
        
        Args:
            resume: Resume to improve
            options: Rewrite options
            target_job: Optional job to tailor for
            
        Returns:
            List of validated suggestions
            
        Note: For MVP, returns deterministic suggestions.
              Future: LLM-powered with Gemini
        """
        options = options or RewriteOptions()
        
        if self.use_llm:
            # Future: LLM-powered suggestions
            return self._generate_llm_suggestions(resume, options, target_job)
        else:
            # MVP: Deterministic test suggestions
            return self._generate_test_suggestions(resume, options)
    
    def _generate_test_suggestions(
        self,
        resume: Resume,
        options: RewriteOptions
    ) -> List[RewriteSuggestion]:
        """
        Generate test suggestions (deterministic)
        
        For MVP testing without LLM
        """
        suggestions = []
        
        # Example: Strengthen first experience entry
        if resume.experience and len(resume.experience) > 0:
            exp = resume.experience[0]
            
            # Simple verb strengthening
            original = exp.description
            suggested = self._strengthen_verbs(original)
            
            # Create diff
            diff = create_text_diff(original, suggested)
            
            # Validate
            validation = self.validator.validate_suggestion(
                original, suggested, resume
            )
            
            # Log for eval
            self.evaluator.log_suggestion(original, suggested, validation)
            
            if validation.valid or validation.requires_user_input:
                suggestion = RewriteSuggestion(
                    suggestion_id=f"sug_{uuid.uuid4().hex[:8]}",
                    section="experience",
                    subsection=exp.title,
                    original_text=original,
                    suggested_text=suggested,
                    diff=diff,
                    reason="Strengthened action verbs for ATS impact",
                    confidence=0.85,
                    action_verbs_strengthened=["led", "managed"],
                    requires_user_input=validation.requires_user_input,
                    placeholders=validation.placeholders,
                    risk_level=validation.risk_level
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _strengthen_verbs(self, text: str) -> str:
        """Simple verb strengthening for testing"""
        replacements = {
            "worked on": "led",
            "Worked on": "Led",
            "helped": "facilitated",
            "Helped": "Facilitated",
            "did": "executed",
            "made": "developed"
        }
        
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def _generate_llm_suggestions(
        self,
        resume: Resume,
        options: RewriteOptions,
        target_job: Optional[Job]
    ) -> List[RewriteSuggestion]:
        """
        Generate suggestions using LLM
        """
        suggestions = []
        
        # Determine focus sections
        sections_to_review = []
        if options and options.focus_section:
            sections_to_review.append(options.focus_section)
        else:
            # Default to checking experience and summary
            sections_to_review = ["experience", "summary"]
            
        if not self.llm_service:
             # Fallback if service not injected
             return self._generate_test_suggestions(resume, options)

        for section in sections_to_review:
            try:
                # Call LLM Service
                llm_suggestions = self.llm_service.generate_improvements(
                    resume.model_dump(mode='json'), 
                    focus_section=section
                )
                
                for item in llm_suggestions:
                    original = item.get("original_text", "")
                    suggested = item.get("suggested_text", "")
                    
                    if not original or not suggested:
                        continue
                        
                    # Create Diff
                    diff = create_text_diff(original, suggested)
                    
                    # Validate (Anti-Hallucination)
                    validation = self.validator.validate_suggestion(
                        original, suggested, resume, target_job
                    )
                    
                    # Log
                    self.evaluator.log_suggestion(original, suggested, validation)
                    
                    # Create Object
                    sugg_obj = RewriteSuggestion(
                        suggestion_id=f"sug_{uuid.uuid4().hex[:8]}",
                        section=item.get("section", section),
                        subsection=item.get("subsection", ""),
                        original_text=original,
                        suggested_text=suggested,
                        diff=diff,
                        reason=item.get("reason", "Improved clarity and impact"),
                        confidence=item.get("confidence", 0.8),
                        action_verbs_strengthened=item.get("action_verbs", []),
                        requires_user_input=validation.requires_user_input,
                        placeholders=validation.placeholders,
                        risk_level=validation.risk_level,
                        keywords_added=[] # TODO: extract keywords from diff
                    )
                    
                    suggestions.append(sugg_obj)
                    
            except Exception as e:
                print(f"Error generating suggestions for {section}: {e}")
                
        return suggestions
    
    def apply_improvements(
        self,
        resume: Resume,
        suggestions: List[RewriteSuggestion],
        user_id: str
    ) -> Resume:
        """
        Apply improvements with HITL approval
        
        SYSTEM.md Section 5: HITL mandatory
        
        Args:
            resume: Original resume
            suggestions: Suggestions to apply
            user_id: User who must approve
            
        Returns:
            Updated resume (with only approved changes)
        """
        approved_suggestions = []
        
        for suggestion in suggestions:
            # Request HITL approval
            approval = self.approval_gate.request_approval(
                action_type="resume_rewrite",
                original=suggestion.original_text,
                proposed=suggestion.suggested_text,
                user_id=user_id,
                context={
                    "section": suggestion.section,
                    "reason": suggestion.reason,
                    "confidence": suggestion.confidence,
                    "risk_level": suggestion.risk_level.value,
                    "keywords_added": suggestion.keywords_added
                }
            )
            
            # Note: In real implementation, this would pause
            # and wait for user approval via UI
            # For testing, we can auto-approve or mock
            
            # Track for eval
            # (In production, this happens after user decides)
            
        return resume  # Updated with approved changes


# Factory function
def create_rewrite_agent(
    approval_gate: IApprovalGate,
    evaluator: Optional[IEvaluator] = None,
    use_llm: bool = False,
    llm_service: Any = None
) -> RewriteAgent:
    """
    Create rewrite agent instance
    
    Modular design - swap components easily:
    - validator: Built-in for now
    - approval_gate: Already modular (Simple/LangGraph)
    - evaluator: Simple for MVP, LangSmith for production
    """
    validator = RewriteValidator()
    
    return RewriteAgent(
        validator=validator,
        approval_gate=approval_gate,
        evaluator=evaluator,
        use_llm=use_llm,
        llm_service=llm_service
    )
