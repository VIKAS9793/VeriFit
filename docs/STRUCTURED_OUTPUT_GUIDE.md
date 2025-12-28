# Structured Output Implementation Guide

**Purpose**: How to add LLM structured output for edge cases in VeriFit

**Compliance**: SYSTEM.md Section 0 (Refuse hallucination) + Section 1.1 (Research-first)

---

## Why Structured Output?

Per SYSTEM.md Section 0: **"Explicitly refuse hallucination"**

**Problem**: LLMs can generate invalid JSON or incorrect field types
**Solution**: Force LLM output to match our Pydantic schemas exactly

**Research Source** (Current as of Dec 2025):
- OpenAI "Structured Outputs" (Aug 2024, still current)
- Google Gemini "Controlled Generation" (Sept 2024, still current)
- Instructor library for production use (actively maintained)

---

## Current VeriFit Status

✅ **Already prepared**:
- All models use Pydantic V2 (`Resume`, `Experience`, `Education`, etc.)
- Parser has `use_llm_fallback` flag (currently defaults to `False`)
- Deterministic-first approach implemented

---

## Implementation Options

### Option 1: OpenAI Structured Outputs (Recommended for Production)

**Pros**: Guaranteed schema compliance, built-in validation
**Cons**: Proprietary API, costs money

```python
from openai import OpenAI
from src.models.resume import Resume, Experience

client = OpenAI(api_key="your-key")

# When use_llm_fallback=True and edge case detected
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract resume experience from this text. Be verbatim."},
        {"role": "user", "content": resume_text}
    ],
    response_format=Experience  # Our Pydantic model!
)

experience = response.choices[0].message.parsed  # Guaranteed to match Experience schema
```

**Key Point**: `response_format=Experience` forces output to match our schema

---

### Option 2: Google Gemini with response_schema

**Pros**: Free tier available, supports Pydantic
**Cons**: Requires schema conversion to JSON

```python
import google.generativeai as genai
from src.models.resume import Experience

genai.configure(api_key="your-key")

# Convert Pydantic to Gemini schema
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": Experience  # Pydantic model
    }
)

response = model.generate_content(
    f"Extract experience from: {resume_text}"
)

# Parse JSON response
import json
experience_data = json.loads(response.text)
experience = Experience(**experience_data)  # Validate with Pydantic
```

---

### Option 3: LangChain PydanticOutputParser (Framework Integration)

**Pros**: Works with multiple LLM providers, retry logic
**Cons**: More complex setup

```python
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.models.resume import Experience

# Setup parser
parser = PydanticOutputParser(pydantic_object=Experience)

# Create prompt with format instructions
prompt = PromptTemplate(
    template="Extract experience from resume.\n{format_instructions}\n{text}",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Chain it together
llm = ChatOpenAI(model="gpt-4")
chain = prompt | llm | parser

# Use it
experience = chain.invoke({"text": resume_text})  # Returns validated Experience object
```

---

### Option 4: Instructor Library (Production-Ready)

**Pros**: Automatic retries, works with OpenAI/Gemini, simple API
**Cons**: Additional dependency

```python
import instructor
from openai import OpenAI
from src.models.resume import Experience

# Patch OpenAI client
client = instructor.from_openai(OpenAI())

# Call with Pydantic model - automatic validation!
experience = client.chat.completions.create(
    model="gpt-4o",
    response_model=Experience,  # Our Pydantic model
    messages=[
        {"role": "user", "content": f"Extract experience from: {resume_text}"}
    ],
    max_retries=3  # Automatic retries if validation fails
)

# 'experience' is guaranteed to be a valid Experience object
```

---

## Recommended Implementation for VeriFit

**Step 1**: Add to `requirements.txt`
```
# LLM Structured Output (optional, for edge cases)
instructor>=1.0.0  # Structured output wrapper
openai>=1.0.0      # or google-generativeai>=0.3.0
```

**Step 2**: Update `resume_parser.py`

```python
def _llm_fallback_experience(self, text: str) -> List[Experience]:
    """
    LLM fallback for ambiguous experience extraction
    
    Uses structured output to prevent hallucination (SYSTEM.md Section 0)
    """
    if not self.use_llm_fallback:
        return []
    
    try:
        import instructor
        from openai import OpenAI
        
        client = instructor.from_openai(OpenAI())
        
        # Schema-validated extraction
        result = client.chat.completions.create(
            model="gpt-4o",
            response_model=List[Experience],  # Our Pydantic model
            messages=[{
                "role": "system",
                "content": "Extract work experience VERBATIM. Do not invent or infer."
            }, {
                "role": "user",
                "content": f"Extract experience from:\n{text}"
            }],
            max_retries=2
        )
        
        return result
        
    except Exception as e:
        # LLM failure = return empty (honest)
        logger.warning(f"LLM fallback failed: {e}")
        return []
```

**Step 3**: Add audit logging

```python
from src.models.audit import AuditLog

# Log LLM usage for transparency
audit_log = AuditLog(
    event_type="llm_fallback_used",
    system_component="resume_parser",
    metadata={
        "model": "gpt-4o",
        "schema": "Experience",
        "reason": "Ambiguous date format"
    }
)
```

---

## Testing Structured Output

```python
def test_llm_structured_output_validation():
    """
    Test that LLM output matches Pydantic schema
    SYSTEM.md Section 0: Refuse hallucination
    """
    parser = ResumeParser(use_llm_fallback=True)
    
    # Call LLM fallback
    experiences = parser._llm_fallback_experience("Worked at Google 2020-2023")
    
    # Should be valid Experience objects
    assert all(isinstance(exp, Experience) for exp in experiences)
    
    # Should have required fields
    for exp in experiences:
        assert exp.company  # Required field
        # Pydantic validation ensures this!
```

---

## Best Practices (Research-Backed)

1. **Default to Deterministic** (SYSTEM.md Section 5)
   - LLM fallback should be `use_llm_fallback=False` by default
   - Only enable for known edge cases

2. **Always Validate** (SYSTEM.md Section 0)
   - Use structured output to force schema compliance
   - Log all LLM calls for audit trail

3. **Prefer Instructor Library**
   - Handles retries automatically
   - Works with multiple providers
   - Production-tested

4. **Cost Management**
   - Track LLM usage in audit logs
   - Set token limits
   - Consider free tier (Gemini) first

5. **Explainability**
   - Always explain WHY LLM was used
   - Show what deterministic method failed
   - Provide evidence for LLM-extracted data

---

## Migration Path

**Phase 1** (Current): Deterministic only ✅
- Parser works without any LLM
- `use_llm_fallback=False` by default

**Phase 2** (Future): Add LLM for edge cases
- Identify specific edge cases (e.g., complex date formats)
- Implement with structured output
- Add comprehensive audit logging

**Phase 3** (Optional): HITL for LLM outputs
- All LLM extractions require human approval
- Aligns with SYSTEM.md Section 6 (HITL gates)

---

## Documentation

**IMPORTANT**: When adding LLM fallback, update:
1. `README.md` - Note that LLM is optional
2. `.env.example` - Add `OPENAI_API_KEY` (optional)
3. `docs/ARCHITECTURE.md` - Document LLM usage
4. Audit logs - Track every LLM call

---

## References

**Research Sources**:
- [OpenAI Structured Outputs](https://openai.com/blog/structured-outputs) (Aug 2024)
- [Google Gemini Controlled Generation](https://ai.google.dev/gemini-api/docs/json-mode) (Sept 2024)
- [Instructor Library](https://useinstructor.com) - Production wrapper
- [LangChain Pydantic Parser](https://python.langchain.com/docs/modules/model_io/output_parsers/pydantic)

**VeriFit Principle**: Truth over convenience - we use LLMs only when deterministic methods fail, and ALWAYS with schema validation.
