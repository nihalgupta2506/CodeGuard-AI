
import { useState } from "react";
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

function App() {
  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState('import os\n\nx = 1\nprint(x)\n');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState("");
  const [connection, setConnection] = useState<
    "idle" | "checking" | "connected" | "error"
  >("idle");

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
        CodeGuard AI · Static analysis and AI-assisted explanations.
      </footer>
    </main>
  );
}

export default App;
