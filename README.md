# VeriFit

**Evidence-Based ATS Compliance & Job Matching Intelligence**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg)](https://react.dev)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Truth over hype. Trust over vanity metrics.**

---

## 🖼️ Screenshots

<p align="center">
  <img src="assets/MAIN UI.png" alt="VeriFit Main Interface" width="600"/>
</p>

<details>
<summary><strong>View More Screenshots</strong></summary>

| Resume Analysis | Score Breakdown |
|----------------|-----------------|
| ![Resume Analysis](assets/RESUME%20ANALYSIS.png) | ![Resume Scoring](assets/RESUME%20SCORING.png) |

| AI Explainability | Skills Detection |
|-------------------|------------------|
| ![AI Explainability](assets/AI%20EXPLAINABILITY.png) | ![Skills Section](assets/DETAILED%20SKILLS%20SECTION.png) |

| HITL Rewrite |
|--------------|
| ![HITL Rewrite](assets/HITL%20REWRITE.png) |

</details>

---

## 🎯 Project Vision

VeriFit is a **governance-first, evidence-based system** designed to evaluate resumes for ATS compliance, role fit, and job alignment **without exaggeration, hallucination, or opaque scoring**.

Unlike traditional resume "optimizers," VeriFit operates as a **truth mirror**:

- ✅ Scores resumes using **deterministic, explainable criteria**
- ✅ Matches candidates only with **real, active job roles**
- ✅ Enforces **human-in-the-loop approvals** for any generative change
- ✅ Prioritizes **fairness, auditability, and regulatory compliance**

Built for candidates, recruiters, and enterprises that value **accuracy over hype**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Smart Parsing** | LLM-powered resume extraction with regex fallback |
| 📊 **Evidence-Based Scoring** | Every score backed by specific findings |
| 🧠 **AI Explainability (XAI)** | "Why this score?" with reasoning chains |
| ✍️ **HITL Rewrite** | AI suggestions with diff view, requires human approval |
| 🔒 **Privacy-First** | No data retention, no training on user data |
| 🎨 **Modern UI** | Material You design with interactive flashcards |

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend** | Flask + Python | 3.11+ |
| **Frontend** | React + Vite | 19.2 |
| **LLM** | Google Gemini | 2.5 Flash |
| **UI Framework** | Material UI | 7.x |
| **Animations** | Framer Motion | 12.x |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Google API Key](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone repository
git clone https://github.com/VIKAS9793/VeriFit.git
cd VeriFit

# Backend setup
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Frontend setup
cd client && npm install
```

### Run Application

```bash
# Terminal 1: Backend
python -m src.app

# Terminal 2: Frontend
cd client && npm run dev
```

Open http://localhost:5173

📖 See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SYSTEM.md](SYSTEM.md) | Non-negotiable system principles |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture with diagrams |
| [docs/SETUP.md](docs/SETUP.md) | Installation guide |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & solutions |
| [docs/adr/](docs/adr/) | Architecture Decision Records |

---

## 🔒 System Principles

From [SYSTEM.md](SYSTEM.md):

1. **Truth Over Optimization** — Refuses hallucination, exaggeration, or inference
2. **Explainability First** — Every score and decision is auditable
3. **Human-in-the-Loop** — Generative actions require approval with diffs
4. **Privacy-Preserving** — DPDP compliant, consent-first, no training on user data

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Run tests
python -m pytest tests/ -v

# Frontend lint
cd client && npm run lint
```

---

## � Author & Maintainer

<table>
  <tr>
    <td align="center">
      <strong>VIKAS SAHANI</strong><br>
      <sub>@VIKAS9793</sub><br>
      <sub>📧 vikassahani17@gmail.com</sub>
    </td>
  </tr>
</table>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vikas-sahani-727420358)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/vikassahani9793)
[![Google Dev](https://img.shields.io/badge/Google_Dev-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://g.dev/vikas9793)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VIKAS9793)

---

## 📄 License

[MIT License](LICENSE) © 2025 Vikas Sahani

---

*"If your resume needs lies to pass ATS, the problem isn't your resume—it's the role."*
