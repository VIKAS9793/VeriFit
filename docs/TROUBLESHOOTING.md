# VeriFit Troubleshooting Guide

Solutions to common issues when running VeriFit.

---

## 🔴 Backend Issues

### 1. ModuleNotFoundError: No module named 'google.genai'
**Cause:** Using old `google-generativeai` instead of `google-genai`

**Solution:**
```bash
pip uninstall google-generativeai
pip install google-genai
```

---

### 2. GOOGLE_API_KEY not found
**Cause:** Environment variable not set

**Solution:**
1. Create `.env` file in project root:
   ```env
   GOOGLE_API_KEY=your_key_here
   ```
2. Or set in terminal:
   ```bash
   # Windows
   set GOOGLE_API_KEY=your_key_here
   
   # macOS/Linux
   export GOOGLE_API_KEY=your_key_here
   ```

---

### 3. ValidationError: confidence > 1.0
**Cause:** Bug in confidence calculation (fixed in Phase 16)

**Solution:** Pull latest code. The fix clamps confidence to [0.0, 1.0]:
```python
return min(1.0, max(0.0, calculated_value))
```

---

### 4. Port 5000 already in use
**Cause:** Another process using the port

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

### 5. File upload fails with "Invalid file type"
**Cause:** Security validation rejecting file

**Supported formats:**
- PDF (magic bytes: `%PDF`)
- DOCX (magic bytes: `PK`)

**Solution:** Ensure file is a valid PDF or DOCX, not renamed.

---

## 🟡 Frontend Issues

### 1. npm install fails
**Cause:** Node version incompatibility

**Solution:**
```bash
# Check Node version (requires 18+)
node --version

# Using nvm (Windows)
nvm install 18
nvm use 18
```

---

### 2. Vite proxy error: ECONNREFUSED
**Cause:** Backend not running

**Solution:** Start backend first:
```bash
python -m src.app
```

Then start frontend:
```bash
cd client && npm run dev
```

---

### 3. "Why this score?" shows nothing
**Cause:** Missing `rawScore` prop or API error

**Debug steps:**
1. Open browser DevTools (F12)
2. Check Network tab for `/api/explain` calls
3. Verify response exists and has `explanations` object

---

### 4. Skill cards not hovering
**Cause:** CSS not applying or Framer Motion issue

**Solution:** Hard refresh the page:
- Windows: `Ctrl + Shift + R`
- macOS: `Cmd + Shift + R`

---

### 5. TypeScript errors about 'Grid'
**Cause:** IDE cache not updated

**Solution:**
1. VS Code: `Ctrl+Shift+P` → "TypeScript: Restart TS Server"
2. Or reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

---

## 🟢 API Issues

### 1. Rate limit exceeded (429)
**Cause:** Too many requests to Gemini API

**Solution:** The app has built-in retry with exponential backoff. Wait 60 seconds and retry.

---

### 2. Parsing returns empty skills
**Cause:** Resume format not recognized

**Debug:**
1. Check Flask logs for parsing output
2. Verify resume has clearly labeled "Skills" section

---

### 3. Analysis scores all 75
**Cause:** LLM fallback to heuristics (on error)

**Solution:** Check backend logs for LLM errors, usually API key issue.

---

## 🔧 Development Issues

### 1. Tests failing after changes
```bash
# Run tests with verbose output
python -m pytest tests/ -v --tb=short
```

### 2. Pydantic validation errors
Ensure all models use Pydantic V2 syntax:
```python
# V2 syntax
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    field: str = Field(default="value")
```

### 3. Import errors in services
Check `src/services/__init__.py` exports the service.

---

## 📊 Performance Issues

### Slow resume parsing (>30s)
**Cause:** Large file or complex formatting

**Solutions:**
1. Reduce file size (compress images)
2. Use text-based PDF (not scanned)
3. Check Gemini API latency

---

## 🆘 Still Stuck?

1. Check [docs/adr/](adr/) for architectural decisions
2. Review [SYSTEM.md](../SYSTEM.md) for design constraints
3. Open an issue with:
   - Error message
   - Steps to reproduce
   - Python/Node versions
   - OS information
