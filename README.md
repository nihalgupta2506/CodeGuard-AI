<div align="center">

# 🛡️ CodeGuard AI

### AI-Powered Code Review Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Tests-36%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](backend/tests)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Identify code-quality issues instantly. Understand *why* they matter. Get actionable fixes — powered by static analysis and AI.**

CodeGuard AI combines **dual-engine static analysis** (Ruff for Python, Clang-Tidy for C++) with **Google Gemini AI explanations** to make code reviews educational, reliable, and actionable.

---

[Features](#-features) · [Architecture](#-architecture) · [Getting Started](#-getting-started) · [API Reference](#-api-reference) · [Testing](#-testing) · [Roadmap](#-roadmap)

</div>

---

## 🚀 Project Status

| Milestone | Description | Status |
|:---------:|-------------|:------:|
| 1 | **Project Setup** — Frontend & backend scaffolding, connectivity checks | ✅ Done |
| 2 | **Static Analysis** — Python analysis via Ruff, explicit C++ unavailability handling | ✅ Done |
| 3 | **AI Integration** — Gemini-powered explanations, structured JSON responses, retry logic | ✅ Done |
| 4 | **Review History** — SQLite persistence, history API endpoints, frontend history UI | ✅ Done |
| 5 | **C++ Analyzer** — Integrated `clang-tidy` for C++ static analysis | ✅ Done |
| 6 | **Expanded Testing** — Automated backend tests, request validation, error handling, logging | ✅ Done |
| 7 | **Reliability & Security** — Error handling hardening, input validation, analyzer safety, expanded tests | ✅ Done |
| 8 | **Frontend Polish** — Improved review interface, loading states, findings display, error UX, history | 🔜 Next |
| 9 | **CI/CD & Documentation** — GitHub Actions, automated test pipeline, setup docs, architecture docs | 🔲 Planned |
| 10 | **Deployment & Portfolio** — Production deployment, env config, verification, portfolio demo | 🔲 Planned |

> **Current Progress:** Milestones 1–7 are complete. The core pipeline is fully hardened with 36 passing automated tests covering input validation edge cases, request body byte limits, analyzer timeouts and cleanup safety, failure isolation for AI and database operations, and data privacy protections. Milestone 8 (Frontend Polish) is up next.

---

## ✨ Features

### 🔬 Static Analysis Engine
- **Ruff-powered Python analysis** — Catches unused imports, syntax errors, and style issues with sub-second execution
- **Clang-Tidy C++ analysis** — Detects bugprone constructs, performance issues, and readability problems via LLVM `clang-tidy`
- **Structured findings** — Each issue includes rule ID, severity (`error` / `warning`), message, line & column location, and fix availability
- **Sandboxed execution & timeouts** — Analyzers run as non-shell subprocesses (`shell=False`, 10s for Python, 15s for C++) analyzing code without executing it
- **Deterministic resource cleanup** — Temporary source files are guaranteed to be unlinked in `finally` blocks, even upon subprocess timeouts or errors
- **Graceful environment fallback** — Returns clear `analyzer_unavailable` status when analyzer executables are not installed

### 🤖 AI-Powered Explanations
- **Google Gemini integration** — Generates human-readable explanations for every static-analysis finding
- **Structured AI responses** — Each suggestion includes: explanation, why it matters, and a concrete recommendation
- **JSON schema enforcement** — Gemini responses are constrained to a strict schema for reliable parsing
- **Retry with backoff** — Automatic retry (up to 3 attempts) on `503` / `429` transient errors
- **Graceful degradation** — AI failures or malformed AI responses never discard static findings; findings are always returned safely

### 💾 Review History & Persistence
- **SQLite storage** — Every review is automatically saved with code, findings, AI review, and timestamp
- **History browsing** — Frontend interface lists the 20 most recent reviews with metadata
- **Review reopening** — Click any saved review to reload the original code, findings, and AI suggestions
- **Paginated API & bounds clamping** — `GET /reviews?limit=N` clamped securely between 1–100
- **Data privacy protection** — Review history listing endpoint returns metadata only and never exposes source code
- **Parameterized queries** — All database operations use parameterized SQL (`?`) to prevent injection
- **Failure tolerance** — Database persistence failures are logged and do not block or crash the review response

### 🖥️ Frontend Experience
- **Dark-mode code editor** — Syntax-aware textarea with file-name indicator, character counter, and resize support
- **Real-time results** — Findings and AI suggestions render immediately after analysis completes
- **Backend health check** — One-click connectivity verification against the `/health` endpoint
- **Responsive design** — Mobile-friendly layout with stacked controls and full-width actions on small screens
- **Developer Footer** — Links to project GitHub repository and developer LinkedIn profile

### 🔒 Reliability & Security (Milestone 7)
- **Pydantic schema validation** — Strict language enum (`python` | `cpp`), whitespace rejection validator, and 20K character limit
- **Extra field rejection** — `model_config = ConfigDict(extra="forbid")` blocks unknown payload keys
- **Request body limit middleware** — Custom ASGI middleware rejects payloads >25KB (HTTP 413) and catches invalid/negative `Content-Length` headers (HTTP 400)
- **Subprocess execution safety** — Non-shell subprocess execution with explicit timeouts preventing hung processes or zombie files
- **Failure isolation** — Decoupled execution ensures static analysis, AI explanations, and database persistence operate independently without cascade failures
- **CORS restriction** — Restricted to `http://localhost:5173` only
- **Environment isolation** — Sensitive keys loaded from `.env`, excluded via `.gitignore`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite + TS)             │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐ │
│  │  Editor   │  │  Results     │  │  AI Review  │  │  History  │ │
│  │  Panel    │  │  Panel       │  │  Panel      │  │  Panel    │ │
│  └──────────┘  └──────────────┘  └────────────┘  └───────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP (REST API / CORS)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python)                 │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │     RequestBodyLimitMiddleware (25KB limit & header check)│  │
│  └─────────────────────────────┬─────────────────────────────┘  │
│                                │                                │
│  ┌─────────────────┐  ┌────────▼──────┐  ┌──────────────────┐  │
│  │  /review (POST)  │  │  /reviews     │  │  /health (GET)   │  │
│  │  /reviews/{id}   │  │  (GET)        │  │  / (GET)         │  │
│  └────────┬────────┘  └───────┬───────┘  └──────────────────┘  │
│           │                   │                                 │
│  ┌────────▼────────┐  ┌──────▼────────┐                        │
│  │ Static Analyzers│  │  SQLite DB    │                        │
│  │ Ruff (Python)   │  │  (history &   │                        │
│  │ Clang-Tidy (C++)│  │   isolation)  │                        │
│  └────────┬────────┘  └───────────────┘                        │
│           │                                                     │
│  ┌────────▼────────┐                                            │
│  │  Gemini AI       │                                            │
│  │  (google-genai)  │                                            │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
|:-----:|:------------:|---------|
| **Frontend** | React 19, Vite 8, TypeScript 6 | Interactive SPA with dark-mode UI |
| **Backend** | Python 3.10+, FastAPI | REST API with async lifespan events & security middleware |
| **Validation** | Pydantic v2 | Request/response schema enforcement & strict field validation |
| **Static Analysis** | Ruff, Clang-Tidy (LLVM) | Fast Python linting & C++ diagnostic analysis |
| **AI** | Google Gemini (`google-genai`) | Code explanation & recommendations |
| **Database** | SQLite | Local review history persistence |
| **Testing** | pytest, FastAPI TestClient, httpx | 36 automated unit & integration tests |
| **Linting (FE)** | oxlint | Frontend code quality |
| **Version Control** | Git, GitHub | Source control & collaboration |

---

## 📁 Project Structure

```
CodeGuard-AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, routes, RequestBodyLimitMiddleware, lifespan
│   │   ├── schemas.py              # Pydantic models (ReviewRequest, Finding, AIReview, etc.)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── python_analyzer.py  # Ruff subprocess runner, timeouts & cleanup
│   │       ├── cpp_analyzer.py     # Clang-tidy runner, timeouts & diagnostic regex
│   │       ├── ai_review.py        # Gemini client, prompt, retry, validation
│   │       ├── database.py         # SQLite connection & schema initialization
│   │       └── review_history.py   # CRUD operations for review persistence
│   ├── tests/
│   │   ├── test_analyzer_reliability.py # 9 tests: timeouts, safety, cleanup, error recovery
│   │   ├── test_review.py               # 19 tests: endpoints, validation, failure degradation
│   │   └── test_review_history.py       # 8 tests: history CRUD, privacy, limits, isolation
│   ├── .env.example                # Environment variable template
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main application component with footer & history
│   │   ├── App.css                 # Complete design system with animations
│   │   ├── main.tsx                # React entry point
│   │   └── index.css               # Global styles & CSS variables
│   ├── index.html                  # HTML entry point
│   ├── package.json                # Node dependencies & scripts
│   ├── tsconfig.json               # TypeScript configuration
│   └── vite.config.ts              # Vite build configuration
├── .gitignore                      # Excludes .env, .db, node_modules, caches
└── README.md
```

> **Note:** The SQLite database (`codeguard.db`) is generated locally at runtime and is excluded from version control.

---

## ⚙️ Getting Started

### Prerequisites

| Requirement | Version | Notes |
|:-----------:|:-------:|-------|
| Python | 3.10+ | Compatible with dependency requirements |
| Node.js | 18+ | With npm |
| Git | Latest | For cloning the repository |
| Gemini API Key | — | Free tier available at [Google AI Studio](https://aistudio.google.com/apikey) |

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/nihalgupta2506/CodeGuard-AI.git
cd CodeGuard-AI
```

### 2️⃣ Configure Environment Variables

```bash
cd backend
cp .env.example .env     # On Windows: Copy-Item .env.example .env
```

Edit `backend/.env`:

```dotenv
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

> ⚠️ **Never commit your `.env` file.** It is already excluded via `.gitignore`.

### 3️⃣ Set Up & Start the Backend

```bash
cd backend
python -m venv .venv

# Activate the virtual environment:
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will be available at:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000 | API root |
| http://127.0.0.1:8000/docs | Interactive Swagger UI |
| http://127.0.0.1:8000/health | Health check endpoint |

### 4️⃣ Start the Frontend

Open a **new terminal** from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (usually **http://localhost:5173**).

---

## 🔍 API Reference

### Endpoints

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/` | API welcome message and version |
| `GET` | `/health` | Service health check |
| `POST` | `/review` | Submit code for analysis |
| `GET` | `/reviews` | List recent saved reviews |
| `GET` | `/reviews/{id}` | Retrieve a specific saved review |

### `POST /review` — Code Review

**Request:**

```json
{
  "language": "python",
  "code": "import os\nprint('hello')\n"
}
```

**Response (200):**

```json
{
  "language": "python",
  "status": "completed",
  "analyzer": {
    "name": "Ruff",
    "status": "completed",
    "message": "Static analysis completed successfully."
  },
  "findings": [
    {
      "source": "static_analysis",
      "rule_id": "F401",
      "severity": "error",
      "message": "`os` imported but unused",
      "line": 1,
      "column": 8,
      "end_line": 1,
      "end_column": 10,
      "fix_available": true
    }
  ],
  "findings_count": 1,
  "ai_review": {
    "status": "completed",
    "summary": "The code has one issue: an unused import.",
    "suggestions": [
      {
        "rule": "F401",
        "explanation": "The `os` module is imported but never used.",
        "why_it_matters": "Unused imports increase load time and reduce readability.",
        "recommendation": "Remove the `import os` statement."
      }
    ]
  }
}
```

### Supported Languages

| Language | Static Analysis | AI Review | Status |
|:--------:|:---------------:|:---------:|:------:|
| Python | ✅ Ruff | ✅ Gemini | Active |
| C++ | 🔲 clang-tidy | 🔲 Planned | Unavailable |

### `GET /reviews` — Review History

```http
GET /reviews?limit=20
```

Returns review metadata (ID, language, status, timestamp) without the submitted source code. Limit is clamped to **1–100**.

### `GET /reviews/{id}` — Saved Review Detail

```http
GET /reviews/1
```

Returns the full saved review including submitted code, all findings, and AI review data.

---

## 🧪 Testing

### Backend Test Suite

The project includes **36 automated tests** across three test modules, thoroughly covering endpoint behavior, strict validation, failure recovery, privacy, and subprocess safety:

| Module | Tests | Coverage |
|--------|:-----:|----------|
| `test_analyzer_reliability.py` | 9 | Python & C++ analyzer timeouts, unavailable tools, malformed JSON, OS errors, non-zero exits, guaranteed temporary file cleanup |
| `test_review.py` | 19 | Health check, Python & C++ structured reviews, clean code, empty/whitespace/null code rejection, unsupported language rejection, unexpected field rejection (`extra="forbid"`), max length verification, `RequestBodyLimitMiddleware` 413/400 validation, AI failure/malformed response graceful degradation, database failure graceful degradation, review list privacy (no source code leak) |
| `test_review_history.py` | 8 | Empty history, save-on-review, retrieve by ID, 404 handling, limit bounds clamping (1–100), DB isolation via `tmp_path` fixture |

**Run all tests:**

```bash
cd backend
python -m pytest -v
```

> **Note:** If running within a virtual environment, ensure the Python path includes the backend directory:
> ```powershell
> $env:PYTHONPATH="." ; .\.venv\Scripts\python -m pytest -v
> ```

**Verify Python syntax:**

```bash
python -m compileall -q app tests
```

**Check frontend build:**

```bash
cd frontend
npm run build
```

**Lint frontend code:**

```bash
cd frontend
npm run lint
```

---

## 🔐 Security Considerations

| Concern | Mitigation |
|---------|------------|
| Code execution risk | Submitted code is **analyzed only**, never executed |
| Subprocess safety | Analyzers run with `shell=False`, strict timeouts (10s Ruff, 15s Clang-Tidy), and deterministic temp file deletion in `finally` blocks |
| Input validation | Pydantic enforces language enum, non-blank validator, 20K char limit |
| Payload injection | `extra="forbid"` rejects unexpected JSON fields |
| Request size DOS | Custom ASGI middleware rejects bodies >25KB (413) and malformed headers (400) |
| Data privacy | History listing endpoint omits source code; code is only retrieved by specific ID |
| Secret management | API keys in `.env`, excluded via `.gitignore` |
| SQL injection | All queries use parameterized placeholders (`?`) |
| AI hallucination | Prompt instructs Gemini to treat code as untrusted, not invent findings |
| Failure isolation | AI and database failures degrade gracefully without disrupting static findings |
| CORS | Restricted to `http://localhost:5173` only |

---

## 🗺️ Roadmap

### ✅ Completed (Milestones 1–7)
- [x] Project setup and frontend–backend connectivity
- [x] Python static analysis using Ruff
- [x] C++ static analysis using `clang-tidy`
- [x] Gemini-powered explanations and recommendations
- [x] Structured JSON schema enforcement for AI responses
- [x] Retry logic with exponential backoff for transient AI failures
- [x] SQLite-based review persistence
- [x] Review history API and frontend interface
- [x] Pydantic request validation and extra-field rejection
- [x] HTTP request size middleware (25KB limit & malformed header defense)
- [x] Subprocess timeout guards & guaranteed temporary file cleanup
- [x] Failure isolation & graceful degradation for AI and database operations
- [x] Review history privacy protection (source code exclusion in listing)
- [x] CORS configuration
- [x] Comprehensive automated backend test suite (36 tests across 3 modules)
- [x] Database isolation in tests using `tmp_path`

### 🔜 Up Next (Milestone 8 — Frontend Polish)
- [ ] Improved review interface & code editor experience
- [ ] Enhanced loading states and progress indicators
- [ ] Rich findings display with collapsible severity badges
- [ ] Robust error UX and friendly alert messages
- [ ] Interactive review history navigation & inspection

### 🔲 Planned (Milestones 9–10)
- [ ] **Milestone 9** — CI/CD: GitHub Actions pipeline, automated tests on push, architecture docs
- [ ] **Milestone 10** — Deployment: production deploy, env configuration, verification, portfolio demo
- [ ] Add code syntax highlighting in the editor
- [ ] Support additional languages (JavaScript, Go, Rust)

---

## 🎯 Vision

CodeGuard AI aims to make code reviews **understandable and actionable** by combining reliable static-analysis findings with clear AI-generated explanations. Rather than simply flagging issues, it teaches developers *why* something matters and *how* to fix it.

The project is built incrementally with an emphasis on:
- **Maintainability** — Clean service architecture with separation of concerns
- **Validation** — Strict input validation at every layer
- **Testing** — Automated tests with database isolation
- **Security** — Defense-in-depth approach to handling untrusted input
- **Graceful degradation** — No single failure should break the entire review pipeline

---

## 👨‍💻 Developer

<div align="center">

**Nihal Gupta**

[![GitHub](https://img.shields.io/badge/GitHub-nihalgupta2506-181717?style=for-the-badge&logo=github)](https://github.com/nihalgupta2506)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Nihal_Gupta-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/nihal-gupta-g2506/)
[![Project](https://img.shields.io/badge/Repo-CodeGuard_AI-blue?style=for-the-badge&logo=github)](https://github.com/nihalgupta2506/CodeGuard-AI)

</div>

---

<div align="center">
  <sub>Built with ❤️ using FastAPI, React, Ruff, and Google Gemini</sub>
</div>
