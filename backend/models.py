"""
Pydantic data models and schemas for CogniStudy AI.
Ensures rigorous input validation, typing, and structured output formatting.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class SummaryStyle(str, Enum):
    CORNELL = "cornell"
    BULLET = "bullet"
    EXECUTIVE = "executive"
    EXAM_CUES = "exam_cues"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizType(str, Enum):
    MCQ = "mcq"
    FLASHCARD = "flashcard"
    MIXED = "mixed"


class AcademicLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"


class CognitiveLevel(str, Enum):
    ELI5 = "eli5"                     # Intuitive metaphor / Simple
    HIGH_YIELD_EXAM = "high_yield_exam" # Exam prep / Structured
    DEEP_DIVE = "deep_dive"           # Rigorous / Undergrad / First-principles


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=15,
        max_length=15000,
        description="Source notes or textbook material to summarize."
    )
    style: SummaryStyle = Field(
        default=SummaryStyle.CORNELL,
        description="Summarization pedagogical framework style."
    )
    focus_topic: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Specific focus or subtopic to highlight."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional runtime Google Gemini or provider API key."
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 15:
            raise ValueError("Input content must contain at least 15 non-whitespace characters.")
        return stripped


class QuizRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=15,
        max_length=15000,
        description="Study notes from which to generate quiz and flashcards."
    )
    num_questions: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of questions to synthesize (1 to 10)."
    )
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Difficulty level for question synthesis."
    )
    question_type: QuizType = Field(
        default=QuizType.MIXED,
        description="Type of questions: multiple-choice, flashcards, or mixed."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional runtime API key."
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 15:
            raise ValueError("Input content must contain at least 15 non-whitespace characters.")
        return stripped


class AnswerPolishRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="The exam prompt or homework question being answered."
    )
    student_draft: str = Field(
        ...,
        min_length=10,
        max_length=8000,
        description="Student's raw draft answer to be evaluated and polished."
    )
    target_level: AcademicLevel = Field(
        default=AcademicLevel.UNDERGRADUATE,
        description="Target academic standard for grading and refinement."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional runtime API key."
    )

    @field_validator("question", "student_draft")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or solely whitespace.")
        return stripped


class ExplainRequest(BaseModel):
    concept: str = Field(
        ...,
        min_length=2,
        max_length=300,
        description="Name of the concept, theorem, or mechanism to explain."
    )
    cognitive_level: CognitiveLevel = Field(
        default=CognitiveLevel.HIGH_YIELD_EXAM,
        description="Cognitive abstraction level (ELI5, Exam Ready, Deep Dive)."
    )
    subject_domain: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional subject discipline (e.g. Physics, Biology, CS)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional runtime API key."
    )

    @field_validator("concept")
    @classmethod
    def validate_concept(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError("Concept name must be at least 2 characters long.")
        return stripped


class ApiKeyUpdateRequest(BaseModel):
    api_key: str = Field(..., min_length=5, max_length=200)
    provider: str = Field(default="gemini")


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class QuizItem(BaseModel):
    id: int
    type: str  # "mcq" or "flashcard"
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    hint: Optional[str] = None


class QuizResponseData(BaseModel):
    title: str
    difficulty: str
    questions: List[QuizItem]


class SummarizeResponseData(BaseModel):
    title: str
    style: str
    cues_and_keywords: List[str]
    notes_summary: str
    core_takeaways: List[str]
    study_questions: List[str]
    action_items: List[str]


class AnswerPolishResponseData(BaseModel):
    original_score: int = Field(..., ge=1, le=10, description="Draft score out of 10")
    rubric_evaluation: Dict[str, str] = Field(..., description="Criteria-by-criteria breakdown")
    strengths: List[str]
    weaknesses: List[str]
    polished_version: str
    key_improvements_made: List[str]


class ExplainResponseData(BaseModel):
    concept: str
    level: str
    core_explanation: str
    intuitive_analogy: str
    common_misconceptions: List[str]
    memory_hook_or_mnemonic: str
    self_test_challenge: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    is_fallback: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
