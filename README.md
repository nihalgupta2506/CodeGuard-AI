# CodeGuard AI 🛡️

**An AI-powered code review assistant that helps developers identify code-quality issues and understand potential improvements.**

CodeGuard AI combines **Ruff static analysis** with **Google Gemini-powered explanations and recommendations** to make code reviews more accessible and actionable.

## 🚀 Project Status

- **Milestone 1 — Project Setup:** Frontend and backend setup with connectivity checks.
- **Milestone 2 — Static Analysis:** Python code analysis using Ruff and explicit handling for unavailable C++ analysis.
- **Milestone 3 — AI Integration:** Gemini-powered explanations and improvement recommendations.
- **Milestone 4 — Review History:** SQLite persistence, review history API endpoints, and frontend history interface.
- **Milestone 5 — Reliability and Testing:** Automated tests, request validation, error handling, and logging improvements.
- **Milestone 6 — C++ Analysis:** Planned.
- **Milestone 7 — Deployment:** Planned.

> Current status: Core Python analysis, AI review, and review-history functionality have been implemented. Final verification of the latest changes and C++ analyzer integration remain separate tasks.

## ✨ Features

- Interactive code-review interface with a dark-mode editor.
- React frontend built with Vite and TypeScript.
- REST API powered by FastAPI.
- Python static analysis using Ruff.
- AI-generated explanations and improvement suggestions using Google Gemini.
- Structured findings with rule IDs, severity, messages, and source locations.
- AI summaries, explanations, impact descriptions, and recommendations.
- Request validation for empty code, unsupported languages, unexpected fields, and oversized input.
- Explicit response when C++ analysis is unavailable.
- Graceful degradation: AI failures do not discard successful Ruff results.
- Persistent review history stored in SQLite.
- API endpoints to list saved reviews and retrieve individual reviews.
- Frontend interface for browsing and reopening saved reviews.
- Automated backend tests using pytest.
- Submitted source code is analyzed, not executed.

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, TypeScript |
| Backend | Python, FastAPI |
| Validation | Pydantic |
| Static Analysis | Ruff |
| AI Integration | Google Gemini, `google-genai` |
| Database | SQLite |
| Testing | pytest, FastAPI TestClient |
| Version Control | Git, GitHub |

## 📁 Project Structure

```text
CodeGuard-AI/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── python_analyzer.py
│   │   │   ├── ai_review.py
│   │   │   ├── database.py
│   │   │   └── review_history.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── tests/
│   │   ├── test_review.py
│   │   └── test_review_history.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

The SQLite database is generated locally and should not be committed to Git. The actual project structure may contain additional configuration and test files.

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the dependencies.
- Node.js and npm.
- Git.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 1. Clone the Repository

```powershell
git clone https://github.com/nihalgupta2506/CodeGuard-AI.git
cd CodeGuard-AI
```

### 2. Configure Environment Variables

From the project root:

```powershell
cd backend
Copy-Item .env.example .env
```

Open `backend/.env` and configure your credentials:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_model
```

Use a model supported by your Gemini API configuration. Never commit your actual API key or `.env` file.

### 3. Set Up and Start the Backend

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend runs at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Keep this terminal running.

### 4. Start the Frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## 🔍 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API welcome information |
| `GET` | `/health` | Check backend health |
| `POST` | `/review` | Analyze submitted source code |
| `GET` | `/reviews` | List recent saved reviews |
| `GET` | `/reviews/{review_id}` | Retrieve a saved review |

### Example Review Request

`POST /review`

```json
{
  "language": "python",
  "code": "import os\nprint('hello')\n"
}
```

### Supported Languages

| Language | Behavior |
|---|---|
| Python | Ruff static analysis and Gemini-powered explanations when available |
| C++ | Returns an explicit unavailable status until a C++ analyzer is integrated |

### Review History

List recent reviews:

```http
GET /reviews?limit=20
```

Retrieve an individual review:

```http
GET /reviews/1
```

The history listing returns review metadata without including submitted source code. Individual review retrieval includes the saved code, static-analysis findings, and AI review data when available.

Review history is stored locally in SQLite. Do not submit confidential or sensitive source code unless you are comfortable with how it is processed and stored.

## 🧪 Testing

Run the backend tests from the `backend` directory:

```powershell
python -m pytest -v
```

Check Python syntax compilation:

```powershell
python -m compileall -q app tests
```

Check for whitespace errors in Git changes from the project root:

```powershell
git diff --check
```

Always use the actual test output to report test coverage. A successful frontend build can be checked from the `frontend` directory with:

```powershell
npm run build
```

## 🔐 Security Considerations

- Submitted source code is analyzed, not executed.
- Ruff runs as a subprocess with a timeout.
- Automatic code fixes are disabled during analysis.
- Request validation restricts accepted languages and source-code size.
- API keys are loaded from environment variables and must not be committed.
- `.env` and the local SQLite database are excluded through `.gitignore`.
- AI-generated suggestions are recommendations and should be reviewed before being applied.
- AI failures do not remove successfully generated static-analysis findings.
- Database operations use parameterized SQL queries.

## 🗺️ Roadmap

- [x] Project setup and frontend-backend connectivity.
- [x] Python static analysis using Ruff.
- [x] Explicit handling for unavailable C++ analysis.
- [x] Gemini-powered explanations and recommendations.
- [x] SQLite-based review persistence.
- [x] Review history API and frontend interface.
- [x] Initial automated backend testing.
- [ ] Complete reliability hardening and final regression testing.
- [ ] Integrate a C++ static analyzer such as `clang-tidy`.
- [ ] Add and verify further C++ analysis tests.
- [ ] Deploy the backend and frontend.
- [ ] Publish a live portfolio demonstration.

## 🎯 Vision

CodeGuard AI aims to make code reviews more understandable and actionable by combining reliable static-analysis findings with clear AI-generated explanations. The project is being developed incrementally, with an emphasis on maintainability, validation, testing, and responsible handling of submitted source code.

## 👨‍💻 Developer

**Nihal Gupta**

- GitHub: [nihalgupta2506](https://github.com/nihalgupta2506)
- Project Repository: [CodeGuard AI](https://github.com/nihalgupta2506/CodeGuard-AI)
