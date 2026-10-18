
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    AnalyzerInfo,
    ReviewRequest,
    ReviewResponse,
)
from app.services.python_analyzer import analyze_python

app = FastAPI(
    title="CodeGuard AI API",
    version="0.2.0",
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
        "version": "0.2.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeGuard AI API",
    }


@app.post("/review", response_model=ReviewResponse)
def review_code(payload: ReviewRequest):
    if payload.language == "cpp":
        return ReviewResponse(
            language="cpp",
            status="analyzer_unavailable",
            analyzer=AnalyzerInfo(
                name="clang-tidy",
                status="unavailable",
                message=(
                    "C++ static analysis is not configured yet. "
                    "No C++ findings were generated."
                ),
            ),
            findings=[],
            findings_count=0,
        )

    analyzer, findings = analyze_python(payload.code)

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

    return ReviewResponse(
        language=payload.language,
        status=status,
        analyzer=analyzer,
        findings=findings,
        findings_count=len(findings),
    )
