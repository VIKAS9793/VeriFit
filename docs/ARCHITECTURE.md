# VeriFit Architecture

Comprehensive architecture documentation for VeriFit.

---

## System Overview

```mermaid
flowchart TB
    subgraph CLIENT["🖥️ Frontend (React + Vite)"]
        UI[UploadZone]
        DASH[AnalysisDashboard]
        XAI[ExplanationPanel]
        SKILL[SkillFlashcard]
        HITL[RewritePanel]
    end

    subgraph API["🔌 Flask API"]
        UPLOAD[POST /api/resumes]
        ANALYZE[POST /api/analyze]
        EXPLAIN[POST /api/explain]
        MATCH[POST /api/match]
        REWRITE[POST /api/rewrite]
    end

    subgraph SERVICES["⚙️ Core Services"]
        PARSER[ResumeParser]
        NORMALIZER[ResumeNormalizer]
        ANALYZER[ResumeAnalyzer]
        EXPLAINER[ExplanationService]
        MATCHER[JobMatcher]
        REWRITER[RewriteAgent]
        VALIDATOR[RewriteValidator]
    end

    subgraph LLM["🧠 LLM Layer"]
        GEMINI[Gemini 2.5 Flash]
        FALLBACK[Regex Fallback]
    end

    subgraph SECURITY["🔒 Security Layer"]
        MAGIC[Magic Number Validation]
        SANITIZE[Input Sanitization]
        PROMPT[Prompt Injection Guard]
    end

    UI --> UPLOAD
    DASH --> ANALYZE
    XAI --> EXPLAIN
    
    UPLOAD --> SECURITY
    SECURITY --> PARSER
    PARSER --> LLM
    PARSER --> NORMALIZER
    NORMALIZER --> ANALYZER
    ANALYZER --> EXPLAINER
    
    ANALYZE --> ANALYZER
    EXPLAIN --> EXPLAINER
    MATCH --> MATCHER
    REWRITE --> REWRITER
    REWRITER --> VALIDATOR
```

---

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend
    participant API as Flask API
    participant Security
    participant Parser as ResumeParser
    participant LLM as Gemini
    participant Analyzer as Analyzer
    participant XAI as ExplanationService

    User->>UI: Upload Resume (PDF/DOCX)
    UI->>API: POST /api/resumes
    API->>Security: Validate file type
    Security-->>API: ✓ Valid
    API->>Parser: Parse resume
    Parser->>LLM: Extract structured data
    LLM-->>Parser: Parsed resume
    Parser-->>API: ResumeData
    API-->>UI: Resume parsed

    User->>UI: Request Analysis
    UI->>API: POST /api/analyze
    API->>Analyzer: Analyze resume
    Analyzer->>LLM: Score components
    LLM-->>Analyzer: Evidence-based scores
    Analyzer-->>API: AnalysisScore
    API-->>UI: Display scores

    User->>UI: Click "Why this score?"
    UI->>API: POST /api/explain
    API->>XAI: Generate explanation
    XAI-->>API: ScoreBreakdown
    API-->>UI: Display reasoning
```

---

## Service Architecture

```mermaid
flowchart LR
    subgraph MODELS["📦 Data Models (Pydantic V2)"]
        Resume
        Job
        Score
        Evidence
        AuditLog
    end

    subgraph SERVICES["⚙️ Services"]
        direction TB
        RP[ResumeParser]
        RN[ResumeNormalizer]
        RA[ResumeAnalyzer]
        ES[ExplanationService]
        JM[JobMatcher]
        JP[JobParser]
        RW[RewriteAgent]
        RV[RewriteValidator]
        AG[ApprovalGate]
        SEC[SecurityService]
        LLM[LLMService]
    end

    MODELS --> SERVICES
    
    RP --> RN
    RN --> RA
    RA --> ES
    JP --> JM
    RW --> RV
    RV --> AG
```

---

## Security Architecture

```mermaid
flowchart TB
    subgraph INPUT["📥 File Upload"]
        FILE[User File]
    end

    subgraph VALIDATION["🛡️ Security Checks"]
        MAGIC[Magic Number Check<br/>PDF: %PDF<br/>DOCX: PK]
        SIZE[Size Limit<br/>Max 10MB]
        TYPE[Extension Check<br/>.pdf, .docx]
    end

    subgraph SANITIZATION["🧹 Input Sanitization"]
        PROMPT[Prompt Injection Guard]
        XSS[XSS Prevention]
    end

    subgraph PROCESSING["⚙️ Safe Processing"]
        PARSER[ResumeParser]
    end

    FILE --> MAGIC
    MAGIC -->|Valid| SIZE
    MAGIC -->|Invalid| REJECT[❌ Reject]
    SIZE -->|Valid| TYPE
    SIZE -->|Too Large| REJECT
    TYPE -->|Valid| SANITIZATION
    SANITIZATION --> PROCESSING
```

---

## XAI (Explainability) Architecture

```mermaid
flowchart TB
    subgraph SCORING["📊 Scoring Engine"]
        FORMAT[Format Score]
        STRUCTURE[Structure Score]
        KEYWORD[Keyword Score]
        READABILITY[Readability Score]
    end

    subgraph EVIDENCE["📋 Evidence Collection"]
        E1[Evidence 1]
        E2[Evidence 2]
        E3[Evidence N]
    end

    subgraph XAI["🧠 Explanation Service"]
        TRANSFORM[Evidence → Finding]
        CHAIN[Reasoning Chain]
        CONFIDENCE[Confidence Calc]
        SUMMARY[Summary Gen]
    end

    subgraph OUTPUT["📤 User Output"]
        PANEL[ExplanationPanel]
        FINDING[Finding Cards]
        TIPS[Recommendations]
    end

    FORMAT --> E1
    STRUCTURE --> E2
    KEYWORD --> E3

    E1 --> TRANSFORM
    E2 --> TRANSFORM
    E3 --> TRANSFORM

    TRANSFORM --> CHAIN
    CHAIN --> CONFIDENCE
    CONFIDENCE --> SUMMARY

    SUMMARY --> PANEL
    TRANSFORM --> FINDING
    FINDING --> TIPS
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 19 + Vite | UI rendering |
| **UI Framework** | Material UI 7 | Design system |
| **Animations** | Framer Motion | Micro-interactions |
| **Backend** | Flask | REST API |
| **Data Models** | Pydantic V2 | Validation |
| **LLM** | Gemini 2.5 Flash | AI processing |
| **Rate Limiting** | Tenacity | Retry logic |

---

## Directory Structure

```
VeriFit/
├── assets/                 # Screenshots & media
├── client/
│   └── src/
│       ├── api/
│       │   └── client.ts   # API client
│       └── components/
│           ├── AnalysisDashboard.tsx
│           ├── ExplanationPanel.tsx
│           ├── Footer.tsx
│           ├── RewritePanel.tsx
│           ├── SkillFlashcard.tsx
│           └── UploadZone.tsx
├── docs/
│   ├── adr/               # 8 Architecture Decision Records
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   └── TROUBLESHOOTING.md
├── src/
│   ├── app.py             # Flask application
│   ├── models/            # Pydantic data models
│   │   ├── audit.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   ├── rewrite.py
│   │   └── score.py
│   ├── services/          # Business logic (13 services)
│   │   ├── approval_gate.py
│   │   ├── explanation_service.py
│   │   ├── job_matcher.py
│   │   ├── job_parser.py
│   │   ├── llm.py
│   │   ├── resume_analyzer.py
│   │   ├── resume_normalizer.py
│   │   ├── resume_parser.py
│   │   ├── rewrite_agent.py
│   │   ├── rewrite_validator.py
│   │   ├── score_explainer.py
│   │   └── security.py
│   └── utils/
├── tests/                  # Python tests
├── uploads/                # Temporary file storage
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
└── SYSTEM.md
```

---

## SYSTEM.md Compliance

All architecture decisions follow [SYSTEM.md](../SYSTEM.md) principles:

| Principle | Implementation |
|-----------|----------------|
| Explainability First | XAI Layer with reasoning chains |
| No Hallucination | RewriteValidator + Evidence-based scoring |
| Privacy-Preserving | No data retention, file cleanup |
| Human-in-the-Loop | ApprovalGate for rewrites |
| Research-Driven | ADRs for all major decisions |
