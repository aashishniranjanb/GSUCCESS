import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_syllabus_topic_detail_endpoint_returns_success():
    """Verify that /api/syllabus/topic/{topic_id} returns multimodal topic data and question list."""
    topic_id = "pharmaceutics__pharmaceutics__pharmacy_profession"
    res = client.get(f"/api/syllabus/topic/{topic_id}")
    assert res.status_code == 200
    data = res.json()
    
    assert "topic" in data
    assert data["topic"]["topic_id"] == topic_id
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert "learning_objectives" in data
    assert "content_chunks" in data

def test_question_attempt_submission_with_confidence_calibration():
    """Verify that /api/study/attempt processes confidence and returns educational calibration."""
    payload = {
        "student_id": "student_01",
        "question_id": "q_gpat_001",
        "selected_option": 0,
        "response_time_sec": 12.5,
        "confidence": 5, # Certain
        "hint_used": 0
    }
    res = client.post("/api/study/attempt", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert "is_correct" in data
    assert "calibration_category" in data
    assert "fsrs_rating" in data
    assert "explanation" in data
    assert data["correct_option"] == 0
    assert data["is_correct"] is True
    # Confidence 5 + response_time 12.5s (<15s) -> Easy rating & Solid mastery calibration
    assert data["calibration_category"] == "SOLID_MASTERY"
    assert data["fsrs_rating"] == "Easy"
