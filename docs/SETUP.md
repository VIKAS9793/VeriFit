# VeriFit Setup Guide

Complete setup instructions for running VeriFit locally.

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| Google API Key | [Get one here](https://aistudio.google.com/apikey) |

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/VIKAS9793/VeriFit.git
cd VeriFit
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Google API key
```

**.env contents:**
```env
GOOGLE_API_KEY=your_api_key_here
FLASK_DEBUG=true
```

### 4. Frontend Setup

```bash
cd client

# Install dependencies
npm install
```

### 5. Run the Application

**Terminal 1 — Backend:**
```bash
# From project root
python -m src.app
```
Backend runs at: http://127.0.0.1:5000

**Terminal 2 — Frontend:**
```bash
cd client
npm run dev
```
Frontend runs at: http://localhost:5173

## Project Structure

```
VeriFit/
├── src/                  # Python backend
│   ├── app.py           # Flask application
│   ├── models/          # Pydantic data models
│   └── services/        # Business logic
├── client/              # React frontend
│   └── src/
│       ├── components/  # UI components
│       └── api/         # API client
├── tests/               # Python tests
├── docs/                # Documentation
├── uploads/             # Temp file storage
└── logs/                # Application logs
```

## Verification

### Test Backend
```bash
python -m pytest tests/ -v
```

### Test Frontend Build
```bash
cd client && npm run build
```

### Health Check
1. Open http://localhost:5173
2. Upload a PDF or DOCX resume
3. Verify analysis appears with scores
4. Click "Why this score?" to test XAI

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key |
| `FLASK_DEBUG` | No | Enable debug mode (default: false) |
| `UPLOAD_FOLDER` | No | Custom upload path (default: ./uploads) |

## Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions to common problems.

## IDE Configuration

### VS Code Extensions
- Python
- Pylance
- ESLint
- Prettier

### Recommended Settings
```json
{
  "python.linting.enabled": true,
  "editor.formatOnSave": true,
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

---

**Need help?** Open an issue or check the [Troubleshooting Guide](TROUBLESHOOTING.md).
