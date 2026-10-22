
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.services.database import initialize_database
from app.services.cpp_analyzer import analyze_cpp

from app.schemas import (
    AIReview,
    AISuggestion,
    AnalyzerInfo,
    ReviewRequest,
    ReviewResponse,
)
from app.services.review_history import (
    get_review,
    list_reviews,
    save_review,
)
from app.services.ai_review import explain_code_findings
from app.services.python_analyzer import analyze_python

# Load backend/.env regardless of the terminal's working directory.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

APP_VERSION = "0.3.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="CodeGuard AI API",
    version=APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def enforce_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")

    if content_length is not None:
        try:
            if int(content_length) > 25_000:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body is too large."},
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid Content-Length header."},
            )

    return await call_next(request)


@app.get("/")
def root():
    return {
        "message": "Welcome to CodeGuard AI",
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeGuard AI API",
    }



@app.post("/review", response_model=ReviewResponse)
def review_code(payload: ReviewRequest):
    # Run the analyzer that matches the requested language.
    if payload.language == "python":
        analyzer, findings = analyze_python(payload.code)
    else:
        analyzer, findings = analyze_cpp(payload.code)

    if analyzer.status == "failed":
        raise HTTPException(
            status_code=503,
            detail=analyzer.message,
        )

    status = (
        "completed"
        if analyzer.status == "completed"
        else "analyzer_unavailable"
    )

    ai_review = None

    if analyzer.status == "completed":
        try:
            ai_result = explain_code_findings(
                code=payload.code,
                language=payload.language,
                findings=[
                    finding.model_dump()
                    for finding in findings
                ],
            )

            ai_review = AIReview(
                status="completed",
                summary=ai_result["summary"],
                suggestions=[
                    AISuggestion(**suggestion)
                    for suggestion in ai_result["suggestions"]
                ],
            )

        except Exception as exc:
            logger.warning(
                "AI review failed with exception type: %s",
                type(exc).__name__,
            )
            ai_review = AIReview(
                status="failed",
                message=(
                    "AI explanations could not be generated. "
                    "Static-analysis findings are still available."
                ),
            )
    else:
        ai_review = AIReview(
            status="unavailable",
            message=(
                "AI review requires successful static analysis."
            ),
        )

    response = ReviewResponse(
        language=payload.language,
        status=status,
        analyzer=analyzer,
        findings=findings,
        findings_count=len(findings),
        ai_review=ai_review,
    )

    try:
        save_review(
            language=payload.language,
            code=payload.code,
            status=response.status,
            findings=[
                finding.model_dump()
                for finding in findings
            ],
            ai_review=(
                response.ai_review.model_dump()
                if response.ai_review is not None
                else None
            ),
        )
    except Exception as exc:
        logger.error(
            "Failed to save review history: %s",
            type(exc).__name__,
        )

    return response



@app.get("/reviews")
def get_review_history(limit: int = 20):
    """List recent reviews without returning submitted source code."""
    limit = max(1, min(limit, 100))
    return {"reviews": list_reviews(limit=limit)}

@app.get("/reviews/{review_id}")
def get_review_details(review_id: int):
    """Retrieve a saved review by its ID."""
    review = get_review(review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found.",
        )

    return review