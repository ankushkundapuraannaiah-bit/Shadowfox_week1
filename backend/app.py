"""
FastAPI application for CogniStudy AI.
Exposes REST endpoints with comprehensive validation, error trapping,
and static frontend dashboard serving.
"""
import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import ValidationError

from backend import config
from backend.models import (
    SummarizeRequest,
    QuizRequest,
    AnswerPolishRequest,
    ExplainRequest,
    ApiKeyUpdateRequest,
    ApiResponse
)
from backend import llm_service

app = FastAPI(
    title="CogniStudy AI - Intelligent Academic Utility Suite",
    description="AI-powered student assistant for Cornell notes, active-recall quizzes, answer rubric grading, and Feynman concept explanation.",
    version="1.0.0"
)

# CORS middleware for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc):
    """Formats validation errors into clean, student-friendly feedback."""
    error_details = []
    errors = exc.errors() if hasattr(exc, "errors") else []
    for err in errors:
        field_name = " -> ".join(str(loc) for loc in err.get("loc", []))
        message = err.get("msg", "Invalid input value.")
        error_details.append(f"{field_name}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse(
            success=False,
            error="; ".join(error_details) if error_details else "Invalid input data.",
            metadata={"validation_errors": errors}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catches unhandled internal server exceptions without crashing."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse(
            success=False,
            error=f"An unexpected internal error occurred: {str(exc)}",
            metadata={"type": type(exc).__name__}
        ).model_dump()
    )


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Health check endpoint indicating API readiness and configured key status."""
    has_env_key = bool(config.GEMINI_API_KEY)
    return {
        "status": "healthy",
        "service": "CogniStudy AI",
        "timestamp": time.time(),
        "api_key_configured": has_env_key,
        "default_model": config.DEFAULT_GEMINI_MODEL
    }


@app.post("/api/config/key")
async def update_api_key(req: ApiKeyUpdateRequest):
    """Allows client-side session key updates without editing server files."""
    stripped_key = req.api_key.strip()
    if len(stripped_key) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key must be at least 10 characters long."
        )
    # Update process memory key
    config.GEMINI_API_KEY = stripped_key
    return ApiResponse(
        success=True,
        data={"message": "API key successfully updated for this session."},
        metadata={"masked_key": f"{stripped_key[:4]}...{stripped_key[-4:]}"}
    )


@app.post("/api/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    """Synthesizes lecture notes into a structured Cornell summary."""
    try:
        data, is_fallback, notice = await llm_service.generate_summary(
            content=req.content,
            style=req.style.value,
            focus_topic=req.focus_topic,
            api_key=req.api_key
        )
        return ApiResponse(
            success=True,
            data=data,
            is_fallback=is_fallback,
            metadata={"notice": notice, "char_count": len(req.content)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(success=False, error=str(e)).model_dump()
        )


@app.post("/api/quiz")
async def quiz_endpoint(req: QuizRequest):
    """Generates an active-recall self-assessment quiz from study notes."""
    try:
        data, is_fallback, notice = await llm_service.generate_quiz(
            content=req.content,
            num_questions=req.num_questions,
            difficulty=req.difficulty.value,
            question_type=req.question_type.value,
            api_key=req.api_key
        )
        return ApiResponse(
            success=True,
            data=data,
            is_fallback=is_fallback,
            metadata={"notice": notice, "requested_questions": req.num_questions}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(success=False, error=str(e)).model_dump()
        )


@app.post("/api/polish")
async def polish_endpoint(req: AnswerPolishRequest):
    """Critiques and upgrades a student's answer using academic rubric grading."""
    try:
        data, is_fallback, notice = await llm_service.polish_answer(
            question=req.question,
            student_draft=req.student_draft,
            target_level=req.target_level.value,
            api_key=req.api_key
        )
        return ApiResponse(
            success=True,
            data=data,
            is_fallback=is_fallback,
            metadata={"notice": notice, "level": req.target_level.value}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(success=False, error=str(e)).model_dump()
        )


@app.post("/api/explain")
async def explain_endpoint(req: ExplainRequest):
    """Explains complex concepts across multiple cognitive tiers (Feynman method)."""
    try:
        data, is_fallback, notice = await llm_service.explain_concept(
            concept=req.concept,
            cognitive_level=req.cognitive_level.value,
            subject_domain=req.subject_domain,
            api_key=req.api_key
        )
        return ApiResponse(
            success=True,
            data=data,
            is_fallback=is_fallback,
            metadata={"notice": notice, "concept": req.concept}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(success=False, error=str(e)).model_dump()
        )


# ---------------------------------------------------------------------------
# Static Frontend Serving
# ---------------------------------------------------------------------------

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")
