# 🚀 AI Code Analyzer

> Complete setup guide for getting the project running end-to-end on your local machine.

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| **Python** | 3.10+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Ollama** *(optional)* | latest | `ollama --version` |

> **Without Ollama:** The app still works — you'll get heuristic-based insights instead of AI-generated ones.

---

## Step 1 — Backend Setup (FastAPI)

### 1a. Create a Python virtual environment

Open a terminal inside the `backend/` folder:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1        # PowerShell
# or
venv\Scripts\activate.bat          # CMD
```

### 1b. Install dependencies

```bash
pip install -r requirements.txt
```

### 1c. Create your `.env` file

```bash
copy .env.example .env
```

Edit `.env` and fill in:

```env
# GitHub Personal Access Token — optional but strongly recommended
# Without it: 60 API requests/hour
# With it:  5,000 API requests/hour
# Get one at: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here

# Ollama (leave defaults if using local Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Server
API_PORT=8000
DEBUG=True
```

### 1d. Start the backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or use the included script (Windows):
```cmd
run_dev.bat
```

**Verify:** Open http://127.0.0.1:8000 — you should see the welcome JSON.  
**API Docs:** http://127.0.0.1:8000/docs

---

## Step 2 — Frontend Setup (React + Vite)

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Step 3 — Ollama Setup (AI Insights)

Ollama runs a local LLM to generate the AI-powered parts of the report.

### 3a. Install Ollama

Download from **https://ollama.com/download** and install.

### 3b. Pull the model

```bash
ollama pull llama3.2:3b
```

> Downloads ~2 GB. Runs on CPU — no GPU required.  
> For better quality (needs GPU): `ollama pull mistral:7b`

### 3c. Start Ollama

```bash
ollama serve
```

Runs on `http://localhost:11434`. The backend auto-detects it.

---

## Step 4 — Run Your First Analysis

1. Open **http://localhost:5173**
2. Paste any public GitHub URL:
   - `https://github.com/facebook/react`
   - `https://github.com/tiangolo/fastapi`
   - `microsoft/vscode`
3. Click **Analyze**
4. Wait ~10–60 seconds (GitHub fetch + LLM inference)
5. View the full intelligence report!

---

## Report Sections Explained

| Section | What it shows |
|---------|--------------|
| **Overview** | AI-generated project explanation & team behavior |
| **Health Stats** | Stars, forks, commits, last activity, issue ratio |
| **Language Bar** | Visual language breakdown |
| **Project Composition** | File types and folder structure |
| **Contributors** | Per-contributor cards — personality, quality score, risk level, AI likelihood |
| **Insights** | AI-identified strengths, weaknesses, and risks |
| **Patterns** | Hourly and daily commit activity charts |
| **Recommendations** | Actionable suggestions for each contributor or the whole team |

---

## Troubleshooting

### ❌ "Backend is not reachable"
- Start the backend: `uvicorn app.main:app --port 8000 --reload`
- Make sure port 8000 is not blocked

### ❌ "Failed to fetch repository metadata"
- The repo may be **private** — only public repos are supported
- You may have hit the GitHub **rate limit** (60 req/hr unauthenticated) — add `GITHUB_TOKEN` to `.env`
- Check URL format: `owner/repo` or `https://github.com/owner/repo`

### ❌ Report shows "AI insights unavailable"
- This is **non-fatal** — the report still works with heuristic fallback
- Fix: start Ollama with `ollama serve`, then re-analyze
- Check model is ready: `ollama list`

### ❌ Analysis is slow
- First analysis fetches 100+ commits from GitHub — normal
- LLM inference on CPU takes 30–90 seconds
- **Cached for 15 minutes** after first run — re-analyzing same repo is instant

### ❌ Python import errors
```bash
pip install -r requirements.txt --upgrade
```

### ❌ npm errors
```bash
cd frontend
rmdir /s /q node_modules       # Windows
npm install
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/api/health` | Backend + Ollama status |
| `POST` | `/api/analyze` | Analyze a repository |

### POST /api/analyze

**Request:**
```json
{ "repo_url": "https://github.com/owner/repo" }
```

**Response:** Full `FinalReport` JSON with repository metadata, contributor stats, AI insights, patterns, recommendations, and project structure.

### GET /api/health

```json
{
  "status": "ok",
  "server": "RepoIntel Backend",
  "timestamp": "2026-06-27T16:00:00",
  "ollama": {
    "available": true,
    "url": "http://localhost:11434",
    "model": "llama3.2:3b"
  }
}
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | *(empty)* | GitHub PAT — 5000 req/hr vs 60 without |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local Ollama URL |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model name for analysis |
| `API_PORT` | `8000` | Backend port |
| `DEBUG` | `False` | Verbose logging |

---

## Project File Structure

```
Code-Analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI app entry point
│   │   ├── api/
│   │   │   ├── routes.py              ← All API endpoints
│   │   │   └── schemas.py             ← Pydantic request/response models
│   │   ├── fetcher/
│   │   │   └── github_client.py       ← GitHub REST API calls
│   │   ├── analytics/
│   │   │   ├── contributor_analyzer.py  ← Main analytics orchestrator
│   │   │   ├── commit_analyzer.py       ← Commit message quality scoring
│   │   │   ├── ai_code_estimator.py     ← Heuristic AI-vs-human detection
│   │   │   ├── personality_labeler.py   ← Contributor personality archetypes
│   │   │   ├── pattern_detector.py      ← Hourly/daily activity patterns
│   │   │   └── file_analyzer.py         ← File tree & structure analysis
│   │   ├── llm/
│   │   │   ├── ollama_client.py  ← HTTP client for Ollama
│   │   │   ├── prompt_builder.py ← Prompt engineering + fallback
│   │   │   ├── response_parser.py← Parse & validate LLM output
│   │   │   └── models.py         ← LLMInsights Pydantic model
│   │   ├── report/
│   │   │   └── report_builder.py ← Assembles the FinalReport
│   │   └── utils/
│   │       ├── cache.py          ← In-memory TTL cache (15 min)
│   │       ├── config.py         ← Settings from .env
│   │       ├── logger.py         ← Logging setup
│   │       └── exceptions.py     ← Custom HTTP exception classes
│   ├── requirements.txt
│   ├── .env.example
│   └── run_dev.bat               ← Windows quick-start script
│
└── frontend/
    └── src/
        ├── App.jsx               ← Root component, view switching
        ├── components/           ← Header, Footer, LoadingState, ErrorDisplay, RepoInput
        ├── pages/                ← HomePage, ReportPage
        ├── sections/             ← OverviewSection, ContributorSection, etc.
        ├── hooks/useAnalyze.js   ← API call + state management hook
        ├── services/api.js       ← fetch() wrapper for backend
        └── utils/
            ├── constants.js      ← Personality map, colors, labels
            ├── formatters.js     ← Date/number formatters
            └── mockData.js       ← Dev mock (not used in production)
```

---

## Quick-Start Summary (TL;DR)

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env          # then edit .env with your GitHub token
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev

# Terminal 3 — Ollama (optional, for AI insights)
ollama pull llama3.2:3b
ollama serve
```

Then open **http://localhost:5173** and paste any public GitHub URL!
