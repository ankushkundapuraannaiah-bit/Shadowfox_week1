"""
Comprehensive test suite for CogniStudy AI.
Verifies API endpoints, Pydantic validation rules, error handling,
JSON sanitization, and deterministic fallback responses.
"""
import pytest
from starlette.testclient import TestClient
from backend.app import app
from backend import llm_service

client = TestClient(app)

SAMPLE_BIOLOGY_NOTE = """
Cellular respiration is the biochemical pathway through which cells break down glucose 
to generate adenosine triphosphate (ATP). The main stages are Glycolysis in the cytosol, 
the Krebs citric acid cycle in the mitochondrial matrix, and Oxidative Phosphorylation 
along the electron transport chain where ATP synthase operates.
"""


def test_health_endpoint():
    """Verify health endpoint returns healthy status and metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CogniStudy AI"
    assert "timestamp" in data


# ---------------------------------------------------------------------------
# Input Validation & Defensive Tests
# ---------------------------------------------------------------------------

def test_summarize_validation_empty_content():
    """Verify that empty or whitespace input is rejected with 422."""
    response = client.post("/api/summarize", json={"content": "   "})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_summarize_validation_short_content():
    """Verify that inputs below the 15-character threshold are rejected."""
    response = client.post("/api/summarize", json={"content": "too short"})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_quiz_validation_invalid_question_count():
    """Verify bounds validation on question counts (e.g., > 10)."""
    response = client.post("/api/quiz", json={
        "content": SAMPLE_BIOLOGY_NOTE,
        "num_questions": 99  # Exceeds max 10
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_polish_validation_missing_fields():
    """Verify answer polish requires both exam question and student draft."""
    response = client.post("/api/polish", json={
        "question": "",
        "student_draft": "Draft answer here."
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_explain_validation_empty_concept():
    """Verify explain requires a valid concept string."""
    response = client.post("/api/explain", json={
        "concept": " ",
        "cognitive_level": "eli5"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


# ---------------------------------------------------------------------------
# Functional Endpoint & Fallback Tests
# ---------------------------------------------------------------------------

def test_summarize_success():
    """Test Cornell note synthesis returns complete structured schema."""
    response = client.post("/api/summarize", json={
        "content": SAMPLE_BIOLOGY_NOTE,
        "style": "cornell",
        "focus_topic": "ATP Synthase"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert "title" in res_data
    assert "cues_and_keywords" in res_data
    assert len(res_data["cues_and_keywords"]) > 0
    assert "notes_summary" in res_data
    assert "core_takeaways" in res_data
    assert "study_questions" in res_data
    assert "action_items" in res_data


def test_quiz_generation_success():
    """Test quiz endpoint returns structured questions with correct answers."""
    response = client.post("/api/quiz", json={
        "content": SAMPLE_BIOLOGY_NOTE,
        "num_questions": 3,
        "difficulty": "medium",
        "question_type": "mixed"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert "questions" in res_data
    assert len(res_data["questions"]) == 3
    q1 = res_data["questions"][0]
    assert "question" in q1
    assert "correct_answer" in q1
    assert "explanation" in q1


def test_answer_polish_success():
    """Test answer polisher provides score, rubric breakdown, and upgrade."""
    response = client.post("/api/polish", json={
        "question": "How does ATP synthase produce ATP?",
        "student_draft": "Protons go through the enzyme and it spins to make ATP.",
        "target_level": "undergraduate"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert 1 <= res_data["original_score"] <= 10
    assert "rubric_evaluation" in res_data
    assert "polished_version" in res_data
    assert "key_improvements_made" in res_data


def test_feynman_explain_success():
    """Test multi-tier Feynman explanation endpoint."""
    response = client.post("/api/explain", json={
        "concept": "Proton-Motive Force",
        "cognitive_level": "eli5",
        "subject_domain": "Biochemistry"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert res_data["concept"] == "Proton-Motive Force"
    assert "intuitive_analogy" in res_data
    assert "core_explanation" in res_data
    assert "common_misconceptions" in res_data
    assert "memory_hook_or_mnemonic" in res_data


# ---------------------------------------------------------------------------
# Utility & JSON Sanitization Tests
# ---------------------------------------------------------------------------

def test_clean_and_parse_json_markdown_fences():
    """Test JSON parser handles markdown enclosing code blocks cleanly."""
    raw = '```json\n{"test_key": "success", "value": 42}\n```'
    parsed = llm_service.clean_and_parse_json(raw)
    assert parsed["test_key"] == "success"
    assert parsed["value"] == 42


def test_clean_and_parse_json_raw():
    """Test JSON parser handles raw JSON with leading/trailing text."""
    raw = 'Here is the JSON output:\n{"score": 9}\nHope this helps!'
    parsed = llm_service.clean_and_parse_json(raw)
    assert parsed["score"] == 9


def test_api_key_update_endpoint():
    """Test session API key configuration endpoint."""
    response = client.post("/api/config/key", json={
        "api_key": "AIzaSyTestMockKeyForSession12345"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "masked_key" in data["metadata"]
