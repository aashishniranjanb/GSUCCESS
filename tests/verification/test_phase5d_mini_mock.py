import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_mini_mock_coverage_calculation():
    """Verify that /api/mock/mini-mock-coverage reports true eligible counts, duration, and marking scheme."""
    payload = {
        "topic_ids": ["ans_anticholinesterases", "ans_antimuscarinics"],
        "requested_count": 10
    }
    res = client.post("/api/mock/mini-mock-coverage", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "requested_count" in data
    assert "eligible_count" in data
    assert "achievable_count" in data
    assert "marking_scheme" in data
    assert data["marking_scheme"]["correct_marks"] == 4.0
    assert data["marking_scheme"]["negative_marks"] == 1.0
    assert "concepts_breakdown" in data
    assert len(data["concepts_breakdown"]) > 0

def test_mini_mock_coverage_shortfall_warning():
    """Verify that requesting more questions than available triggers an explicit shortfall warning."""
    payload = {
        "topic_ids": ["ans_anticholinesterases"],
        "requested_count": 25
    }
    res = client.post("/api/mock/mini-mock-coverage", json=payload)
    assert res.status_code == 200
    data = res.json()
    # ans_anticholinesterases has 2 questions, requested 25
    assert data["eligible_count"] == 2
    assert data["achievable_count"] == 2
    assert data["is_achievable"] is False
    assert len(data["coverage_gaps"]) > 0
    assert "shortfall" in data["coverage_gaps"][0].lower()

def test_create_and_take_personalized_mini_mock():
    """Verify end-to-end flow: create mini mock, start session, answer, pause, resume, and submit for evaluation."""
    create_payload = {
        "user_id": "student_01",
        "blueprint_name": "mini_mock",
        "custom_title": "Test Autonomic Mini Mock",
        "question_count": 5,
        "topic_ids": ["ans_anticholinesterases", "ans_antimuscarinics", "ans_adrenergic_receptors"]
    }
    create_res = client.post("/api/mock/create", json=create_payload)
    assert create_res.status_code == 200
    exam_data = create_res.json()
    exam_id = exam_data["exam_id"]
    assert exam_id.startswith("mock_")
    assert exam_data["status"] == "CREATED"
    assert exam_data["total_questions"] <= 5

    # 1. Start exam
    start_res = client.post(f"/api/mock/{exam_id}/start?user_id=student_01")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "IN_PROGRESS"

    # 2. Fetch full exam session (deterministic ordering, questions array)
    get_res = client.get(f"/api/mock/{exam_id}?user_id=student_01")
    assert get_res.status_code == 200
    session_data = get_res.json()
    assert session_data["status"] == "IN_PROGRESS"
    questions = session_data["questions"]
    assert len(questions) == exam_data["total_questions"]
    
    # Check no duplicate question IDs
    q_ids = [q["question_id"] for q in questions]
    assert len(q_ids) == len(set(q_ids))

    # 3. Answer first question
    first_q = questions[0]
    ans_payload = {
        "user_id": "student_01",
        "question_id": first_q["question_id"],
        "selected_option": 0,
        "time_spent_ms": 15000,
        "confidence": 4
    }
    ans_res = client.post(f"/api/mock/{exam_id}/answer", json=ans_payload)
    assert ans_res.status_code == 200
    assert ans_res.json()["status"] == "saved"

    # 4. Reload / Resume verification: Answer should be preserved
    resume_res = client.get(f"/api/mock/{exam_id}?user_id=student_01")
    assert resume_res.status_code == 200
    resumed_first_q = resume_res.json()["questions"][0]
    assert resumed_first_q["selected_option"] == 0
    assert resumed_first_q["confidence"] == 4

    # 5. Submit for final evaluation
    submit_res = client.post(f"/api/mock/{exam_id}/submit?user_id=student_01")
    assert submit_res.status_code == 200
    result = submit_res.json()
    assert result["status"] == "EVALUATED"
    assert "summary" in result
    assert "timing_analysis" in result
    assert "concept_performance" in result
    assert result["summary"]["attempted"] >= 1
    assert "raw_score" in result["summary"]

def test_official_125_simulation_regression():
    """Verify that official full-length 125-question simulation remains separate and intact."""
    res = client.get("/api/mock/blueprints")
    assert res.status_code == 200
    blueprints = res.json()["blueprints"]
    bp_125 = next((b for b in blueprints if b["id"] == "official_125"), None)
    assert bp_125 is not None
    assert bp_125["total_questions"] == 125
    assert bp_125["duration_minutes"] == 180
    assert bp_125["exam_version"] == "OFFICIAL_EXAM_SIMULATION"
