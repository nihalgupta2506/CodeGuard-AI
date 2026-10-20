
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type Language = "python" | "cpp";
type Severity = "error" | "warning" | "info";

type Finding = {
  source: "static_analysis";
  rule_id: string;
  severity: Severity;
  message: string;
  line: number;
  column: number;
  end_line: number | null;
  end_column: number | null;
  fix_available: boolean;
};

type AISuggestion = {
  rule: string;
  explanation: string;
  why_it_matters: string;
  recommendation: string;
};

type AIReview = {
  status: "completed" | "failed" | "unavailable";
  summary?: string | null;
  suggestions: AISuggestion[];
  message?: string | null;
};

type ReviewResult = {
  language: Language;
  status: "completed" | "analyzer_unavailable" | "failed";
  analyzer: {
    name: string;
    status: "completed" | "unavailable" | "failed";
    message: string;
  };
  findings: Finding[];
  findings_count: number;
  ai_review?: AIReview | null;
};
type ReviewHistoryItem = {
  id: number;
  language: Language;
  status: string;
  created_at: string;
};

type SavedReview = {
  id: number;
  language: Language;
  code: string;
  status: string;
  created_at: string;
  findings: Finding[];
  ai_review: AIReview | null;
};

function App() {
  const [history, setHistory] = useState<ReviewHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null);
  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState('import os\n\nx = 1\nprint(x)\n');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState("");
  const [connection, setConnection] = useState<
    "idle" | "checking" | "connected" | "error"
  >("idle");
async function loadHistory() {
  setHistoryLoading(true);
  setHistoryError("");

  try {
    const response = await fetch(`${API_URL}/reviews?limit=20`);

    if (!response.ok) {
      throw new Error(`Unable to load history: HTTP ${response.status}`);
    }

    const data = await response.json();
    setHistory(data.reviews as ReviewHistoryItem[]);
  } catch (err) {
    setHistoryError(
      err instanceof Error ? err.message : "Unable to load review history."
    );
  } finally {
    setHistoryLoading(false);
  }
}

async function openSavedReview(reviewId: number) {
  setHistoryError("");

  try {
    const response = await fetch(`${API_URL}/reviews/${reviewId}`);

    if (!response.ok) {
      throw new Error(`Unable to open review: HTTP ${response.status}`);
    }

    const saved = (await response.json()) as SavedReview;

    setLanguage(saved.language);
    setCode(saved.code);
    setSelectedReviewId(saved.id);

    setResult({
      language: saved.language,
      status: saved.status as ReviewResult["status"],
      analyzer: {
        name: saved.language === "python" ? "ruff" : "clang-tidy",
        status: saved.status === "completed" ? "completed" : "unavailable",
        message: "Loaded from saved review history.",
      },
      findings: saved.findings,
      findings_count: saved.findings.length,
      ai_review: saved.ai_review,
    });

    setError("");
  } catch (err) {
    setHistoryError(
      err instanceof Error ? err.message : "Unable to open saved review."
    );
  }
}

useEffect(() => {
  void loadHistory();
}, []);
  async function checkConnection() {
    setConnection("checking");

    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.status !== "healthy") {
        throw new Error("Unexpected health response");
      }

      setConnection("connected");
    } catch {
      setConnection("error");
    }
  }

  async function reviewCode() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, code }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Request failed with HTTP ${response.status}`
        );
      }

      setResult(data as ReviewResult);
setSelectedReviewId(null);
void loadHistory();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to complete the review."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">&lt;/&gt;</span>
          <span>CodeGuard <strong>AI</strong></span>
        </a>
        <span className="version-label">DEVELOPER PREVIEW</span>
      </header>

      <section className="hero">
        <p className="eyebrow">AI-ASSISTED CODE REVIEW</p>
        <h1>Write better code.</h1>
        <p className="hero-description">
          Find code-quality issues, inspect verified analyzer findings,
          and get AI-powered explanations and improvement suggestions.
        </p>
      </section>

      <section className="workspace">
        <div className="workspace-header">
          <div>
            <h2>Code workspace</h2>
            <p>Submit source code for static analysis and AI review.</p>
          </div>

          <label className="language-control">
            <span>Language</span>
            <select
              value={language}
              onChange={(event) => {
                setSelectedReviewId(null);
                setLanguage(event.target.value as Language);
                setResult(null);
                setError("");
              }}
            >
              <option value="python">Python</option>
              <option value="cpp">C++</option>
            </select>
          </label>
        </div>

        <div className="editor">
          <div className="editor-toolbar">
            <span className="editor-dot" />
            <span className="editor-dot" />
            <span className="editor-dot" />
            <span className="file-name">
              {language === "python" ? "main.py" : "main.cpp"}
            </span>
          </div>

          <textarea
            aria-label="Source code"
            spellCheck={false}
            value={code}
            onChange={(event) => {
              setSelectedReviewId(null);
              setCode(event.target.value);
              setResult(null);
            }}
            placeholder="Paste your code here..."
          />

          <div className="editor-footer">
            <span>{language === "python" ? "Python" : "C++"}</span>
            <span>{code.length.toLocaleString()} / 20,000 characters</span>
          </div>
        </div>

        <div className="workspace-actions">
          <p>Source code is analyzed, not executed.</p>
          <button
            type="button"
            onClick={reviewCode}
            disabled={loading || !code.trim() || code.length > 20_000}
          >
            {loading ? "Reviewing..." : "Review code"}
          </button>
        </div>

        {error && (
          <div className="message-panel error-panel" role="alert">
            <strong>Review failed</strong>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <section className="results" aria-live="polite">
            <div className="results-heading">
              <div>
                <h2>Static analysis results</h2>
                <p>Analyzer: {result.analyzer.name}</p>
              </div>
              <span
                className={`status-pill ${
                  result.status === "completed" ? "connected" : "error"
                }`}
              >
                {result.status === "completed"
                  ? "Completed"
                  : "Analyzer unavailable"}
              </span>
            </div>

            <div className="message-panel">
              <p>{result.analyzer.message}</p>
              <strong>
                {result.findings_count} finding
                {result.findings_count === 1 ? "" : "s"}
              </strong>
            </div>

            {result.status === "completed" &&
              result.findings.length === 0 && (
                <div className="empty-results">
                  No findings were reported by this analyzer. This does not
                  guarantee that the code is bug-free or secure.
                </div>
              )}

            {result.findings.map((finding, index) => (
              <article
                className="finding"
                key={`${finding.rule_id}-${finding.line}-${index}`}
              >
                <div className="finding-heading">
                  <strong>{finding.rule_id}</strong>
                  <span className={`severity ${finding.severity}`}>
                    {finding.severity}
                  </span>
                </div>
                <p>{finding.message}</p>
                <div className="finding-meta">
                  <span>
                    Line {finding.line}, column {finding.column}
                  </span>
                  <span>
                    {finding.fix_available
                      ? "Fix available from analyzer"
                      : "No automatic fix reported"}
                  </span>
                </div>
              </article>
            ))}

            {result.ai_review && (
              <section className="ai-review">
                <div className="results-heading">
                  <div>
                    <h2>AI code review</h2>
                    <p>Explanations and recommendations from Gemini</p>
                  </div>
                  <span
                    className={`status-pill ${
                      result.ai_review.status === "completed"
                        ? "connected"
                        : result.ai_review.status === "failed"
                          ? "error"
                          : ""
                    }`}
                  >
                    {result.ai_review.status === "completed"
                      ? "Completed"
                      : result.ai_review.status === "failed"
                        ? "Unavailable"
                        : "Not available"}
                  </span>
                </div>

                {result.ai_review.summary && (
                  <div className="message-panel">
                    <strong>Summary</strong>
                    <p>{result.ai_review.summary}</p>
                  </div>
                )}

                {result.ai_review.message && (
                  <div className="message-panel">
                    <p>{result.ai_review.message}</p>
                  </div>
                )}

                {result.ai_review.status === "completed" &&
                  result.ai_review.suggestions.length === 0 && (
                    <div className="empty-results">
                      No AI suggestions were returned for this review.
                    </div>
                  )}

                {result.ai_review.suggestions.map((suggestion, index) => (
                  <article
                    className="finding ai-suggestion"
                    key={`${suggestion.rule}-${index}`}
                  >
                    <div className="finding-heading">
                      <strong>{suggestion.rule || "General suggestion"}</strong>
                      <span className="severity info">AI suggestion</span>
                    </div>

                    <p>{suggestion.explanation}</p>

                    <div className="ai-detail">
                      <strong>Why it matters</strong>
                      <p>{suggestion.why_it_matters}</p>
                    </div>

                    <div className="ai-detail">
                      <strong>Recommendation</strong>
                      <p>{suggestion.recommendation}</p>
                    </div>
                  </article>
                ))}
              </section>
            )}
          </section>
        )}
      </section>
            <section className="history-card">
        <div className="history-heading">
          <div>
            <h2>Review history</h2>
            <p>Your 20 most recent saved code reviews.</p>
          </div>

          <button
            type="button"
            className="history-refresh"
            onClick={() => void loadHistory()}
            disabled={historyLoading}
          >
            {historyLoading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {historyError && (
          <div className="message-panel error-panel" role="alert">
            <p>{historyError}</p>
          </div>
        )}

        {!historyLoading && history.length === 0 && !historyError && (
          <div className="empty-results">
            No saved reviews yet. Submit code to create your first history item.
          </div>
        )}

        <div className="history-list">
          {history.map((item) => (
            <article className="history-item" key={item.id}>
              <div className="history-item-details">
                <strong>Review #{item.id}</strong>
                <span>{item.language.toUpperCase()}</span>
                <span>{item.status.replaceAll("_", " ")}</span>
                <time dateTime={item.created_at}>
                  {new Date(`${item.created_at.replace(" ", "T")}Z`).toLocaleString()}
                </time>
              </div>

              <button
                type="button"
                className="history-open"
                onClick={() => void openSavedReview(item.id)}
              >
                {selectedReviewId === item.id ? "Opened" : "Open review"}
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="connection-card">
        <div className="connection-heading">
          <div>
            <h2>Backend connection</h2>
            <p>Check the availability of the API.</p>
          </div>
          <span className={`status-pill ${connection}`}>
            {connection === "connected"
              ? "Connected"
              : connection === "checking"
                ? "Checking..."
                : connection === "error"
                  ? "Connection failed"
                  : "Not checked"}
          </span>
        </div>

        <div className="connection-details">
          <span className="api-address">{API_URL}/health</span>
        </div>

        <button
          type="button"
          className="connection-button"
          onClick={checkConnection}
          disabled={connection === "checking"}
        >
          Check connection
        </button>
      </section>

      <footer className="footer">
        <span className="footer-left">© 2026 Nihal Gupta — CodeGuard AI</span>
        <div className="footer-links">
          <a
            href="https://github.com/nihalgupta2506"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
            className="footer-social"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub
          </a>
          <a
            href="https://linkedin.com/in/nihal-gupta-g2506/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            className="footer-social"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
            </svg>
            LinkedIn
          </a>
        </div>
      </footer>
    </main>
  );
}

export default App;
