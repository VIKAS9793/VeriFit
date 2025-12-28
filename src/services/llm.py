import time
import os
import json
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_fixed

# New SDK: google-genai (replaces deprecated google.generativeai)
from google import genai
from google.genai import types

# Rate Limit for Gemini 2.5 Flash Lite (10 RPM -> 1 req / 6 sec)
# We enforce a safer delay to allow for latency
RATE_LIMIT_DELAY = 7.0

class LLMService:
    """
    Service for interacting with Google Gemini Models (2.5 Flash Lite)
    for intelligent resume parsing and analysis.
    
    Uses the new google-genai SDK (post Nov 2025).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            print("WARNING: No GOOGLE_API_KEY found. LLM features will fail.")
            self.client = None
        else:
            # Initialize the new SDK client
            self.client = genai.Client(api_key=self.api_key)
            
        self.model_name = "gemini-2.5-flash-lite"

    def _wait_for_rate_limit(self):
        """Simple sleep to respect 10 RPM"""
        time.sleep(RATE_LIMIT_DELAY)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def parse_resume_text(self, text: str) -> Dict[str, Any]:
        """
        Extract structured resume data using LLM
        """
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is not set. Please provide a key.")
            
        self._wait_for_rate_limit()
        
        prompt = """
        You are an expert Resume Parser. 
        Extract the following information from the resume text below and return it as a valid JSON object.
        Do not invent information. If a field is missing, omit it or use null/empty list.
        Ensure dates are in YYYY-MM-DD format where possible.
        
        Output Schema:
        {
            "full_name": "string",
            "email": "string",
            "phone": "string",
            "location": "string",
            "linkedin_url": "string",
            "portfolio_url": "string",
            "summary": "string",
            "experience": [
                {
                    "company": "string",
                    "title": "string",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD or null",
                    "is_current": boolean,
                    "location": "string",
                    "description": "string",
                    "responsibilities": ["string"]
                }
            ],
            "education": [
                {
                    "institution": "string",
                    "degree": "string",
                    "field_of_study": "string",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "is_current": boolean,
                    "location": "string"
                }
            ],
            "skills": [
                {"name": "string", "level": "string or null"}
            ],
            "certifications": ["string"],
            "languages": ["string"]
        }

        Resume Text:
        """ + text
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.95,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"LLM Parsing failed: {e}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def analyze_resume(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume quality and generate veriscore
        """
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is not set. Please provide a key.")
            
        self._wait_for_rate_limit()
        
        prompt = """
        You are an Expert Resume Auditor acting on the principle of "Truth over Hype".
        Analyze the following parsed resume JSON and provide an assessment.
        
        Return a JSON object with:
        1. veriscore (0-100): Overall quality based on clarity, impact, and evidence.
        2. overall_score: Same as veriscore.
        3. format_score: ScoreExplanation object
        4. structure_score: ScoreExplanation object
        5. keyword_score: ScoreExplanation object
        6. readability_score: ScoreExplanation object
        7. critical_issues: [string]
        8. warnings: [string]
        9. recommendations: [string]

        Schema Definitions:
        
        Evidence Object:
        {
            "evidence_type": "keyword_match" | "format_check" | "structure_analysis" | "experience_comparison" | "skill_comparison" | "readability_check",
            "description": "string (Human readable proof)",
            "data": {},
            "weight": 1.0
        }

        ScoreExplanation Object:
        { 
            "component": "string (Name of this score category)",
            "score": 0-100, 
            "explanation": "string", 
            "evidence": [Evidence Object] 
        }

        Rubric:
        - High Score: Quantifiable achievements, clear timeline, consistent formatting, relevant skills.
        - Low Score: Vague descriptions, buzzwords without evidence, typos, gaps.
        - Truth over Hype: Penalize fluff (e.g. "Visionary Leader") if unsupported by data.

        Resume JSON:
        """ + json.dumps(resume_json)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.95,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"LLM Analysis failed: {e}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def generate_improvements(self, resume_json: Dict[str, Any], focus_section: str = "experience") -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions for specific sections
        """
        if not self.client:
            return []
            
        self._wait_for_rate_limit()
        
        prompt = f"""
        You are an Expert Resume Writer and Editor.
        Review the '{focus_section}' section of the following resume data.
        Identify 3-5 weak points (passive voice, vague descriptions, lack of metrics) and suggest concrete rewrite improvements.
        
        Return a JSON object with a list of suggestions under key "suggestions":
        {{
            "suggestions": [
                {{
                    "section": "{focus_section}",
                    "subsection": "string (e.g. Job Title or Skill Name)",
                    "original_text": "string (exact match from input)",
                    "suggested_text": "string (improved version)",
                    "reason": "string (why this is better)",
                    "confidence": float (0.0-1.0),
                    "action_verbs": ["list", "of", "strong", "verbs", "used"]
                }}
            ]
        }}
        
        Do NOT invent experience. Only improve phrasing, impact, and clarity.
        
        Resume JSON:
        """ + json.dumps(resume_json)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.95,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                )
            )
            result = json.loads(response.text)
            return result.get("suggestions", [])
        except Exception as e:
            print(f"LLM Rewrite failed: {e}")
            return []

# Factory
def create_llm_service(api_key: Optional[str] = None) -> LLMService:
    return LLMService(api_key)
