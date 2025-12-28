# Contributing to VeriFit

Thank you for your interest in contributing to VeriFit! This document provides guidelines for contributing.

## 🎯 Core Principles

Before contributing, understand our non-negotiable principles from [SYSTEM.md](SYSTEM.md):

1. **Truth over Hype** — No hallucination, exaggeration, or opaque scoring
2. **Explainability First** — Every AI decision must be auditable
3. **Privacy-Preserving** — Consent-first, minimal data retention
4. **Human-in-the-Loop** — All generative actions require approval

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/VIKAS9793/VeriFit.git
   ```
3. Follow the [Setup Guide](docs/SETUP.md)

## 📋 Development Workflow

### Branch Naming
- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation updates
- `refactor/` — Code refactoring

### Commit Messages
Use conventional commits:
```
feat: add job matching endpoint
fix: resolve confidence overflow in XAI
docs: update setup instructions
refactor: extract parsing logic to service
```

### Pull Request Process
1. Create a feature branch from `main`
2. Make your changes with tests
3. Run verification:
   ```bash
   # Backend
   python -m pytest tests/ -v
   
   # Frontend
   cd client && npm run lint && npm run build
   ```
4. Submit PR with clear description
5. Address review feedback

## 🏗️ Architecture Guidelines

### Backend (Python)
- Python 3.11+
- Type hints required
- Docstrings mandatory
- Follow PEP 8
- Use Pydantic V2 for models

### Frontend (React)
- TypeScript required
- Material UI 7 components
- Framer Motion for animations
- No `any` types (strict mode)

### Adding New Services
1. Create service in `src/services/`
2. Add interface in `src/services/__init__.py`
3. Register in `src/app.py`
4. Add tests in `tests/`

## ⚠️ What NOT to Contribute

Per SYSTEM.md, we **do not accept**:
- Features that hallucinate or invent data
- Opaque scoring algorithms
- Proprietary ATS replication claims
- Resume "optimization" for deception

## 🧪 Testing

### Backend Tests
```bash
python -m pytest tests/ -v --cov=src
```

### Running the App
```bash
# Terminal 1: Backend
python -m src.app

# Terminal 2: Frontend
cd client && npm run dev
```

## 📝 Documentation

- Update `README.md` for user-facing changes
- Add ADRs for architectural decisions in `docs/adr/`
- Update `docs/SETUP.md` for environment changes

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## 📫 Questions?

Open an issue with the `question` label.

---

**Thank you for helping make VeriFit better!** 🚀
