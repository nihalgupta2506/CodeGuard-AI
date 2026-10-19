# CodeGuard AI 🛡️

**An AI-powered code review assistant that helps developers identify code-quality issues and understand potential improvements.**

CodeGuard AI combines Ruff static analysis with Gemini-powered explanations and recommendations to make code reviews more accessible and actionable.

## 🚀 Project Status

- **Milestone 1:** Project setup and frontend-to-backend connectivity.
- **Milestone 2:** Python static analysis using Ruff, with explicit handling for unsupported C++ analysis.
- **Milestone 3:** AI-powered code review with Gemini integration.

## ✨ Features

- Interactive code-review interface with a dark-mode editor.
- REST API built with FastAPI.
- Python static analysis using Ruff.
- AI-generated explanations and improvement suggestions powered by Gemini.
- Structured findings with rule IDs, severity, messages, and source locations.
- AI summary, explanation, impact, and recommendation for each finding.
- Request validation for empty code, unsupported languages, unexpected fields, and oversized input.
- Explicit response when C++ analysis is unavailable.
- Graceful degradation: AI failure never removes successful Ruff results.
- Submitted source code is analyzed, not executed.

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, TypeScript |
| Backend | Python, FastAPI |
| Validation | Pydantic |
| Static Analysis | Ruff |
| AI Integration | Google Gemini (google-genai SDK) |
| Version Control | Git, GitHub |

## 📁 Project Structure

```text
CodeGuard-AI/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── python_analyzer.py
│   │   │   └── ai_review.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── tests/
│   │   └── test_review.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

- Python
- Node.js and npm
- Git
- A Gemini API key (see [Google AI Studio](https://aistudio.google.com/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/nihalgupta2506/CodeGuard-AI.git
cd CodeGuard-AI
```

### 2. Configure Environment Variables

```powershell
cd backend
copy .env.example .env
```

Edit `backend/.env` and set your `GEMINI_API_KEY` and `GEMINI_MODEL`.

### 3. Start the Backend

From the project root, run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app
```

Backend URL: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

Keep the backend terminal running.

### 4. Start the Frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## 🔍 Review API

### Endpoint

`POST /review`

### Example Request

```json
{
  "language": "python",
  "code": "import os\nprint('hello')\n"
}
```

### Supported Languages

| Language | Behavior |
|---|---|
| Python | Analyzed using Ruff; AI explanations via Gemini |
| C++ | Reports that the analyzer is unavailable |

The API returns structured information about the analysis, including its status, analyzer details, findings, finding count, and AI review with summary and per-finding suggestions.

For complete request and response schemas, use the interactive API documentation at `/docs`.

## 🧪 Testing

From the backend directory, run:

```powershell
python -m pytest -v
```

This command runs the available automated tests. Confirm that the test suite exists and passes before reporting successful test coverage.

## 🔐 Security Considerations

- Submitted source code is analyzed, not executed.
- Ruff runs as a subprocess with a timeout.
- Automatic code fixes are disabled during analysis.
- Request validation restricts accepted languages and source-code size.
- Secret keys and environment-specific credentials are never committed to Git.
- The Gemini API key is loaded from `.env`, which is excluded via `.gitignore`.

## 🗺️ Roadmap

- [x] Project setup and frontend-backend connectivity
- [x] Python static analysis integration
- [x] Explicit handling for unavailable C++ analysis
- [x] AI-generated explanations and improvement suggestions
- [ ] Expanded automated testing and reliability
- [ ] C++ analyzer integration
- [ ] Review history and persistence
- [ ] Deployment and portfolio release

## 🎯 Vision

Build a practical code-review assistant that combines reliable static-analysis findings with clear, actionable explanations to help developers improve code quality and understand potential issues.

---

**Developer:** Nihal Gupta

**GitHub Repository:** [CodeGuard AI](https://github.com/nihalgupta2506/CodeGuard-AI)
