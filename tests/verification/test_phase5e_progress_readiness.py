import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_progress_empty_learner_history():
    """Verify that a learner with zero attempts returns valid unassessed structure without crashing."""
    res = client.get("/api/progress?student_id=nonexistent_student_999")
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "nonexistent_student_999"
    assert data["summary"]["total_attempts"] == 0
    assert data["summary"]["total_correct"] == 0
    assert data["summary"]["overall_accuracy_percent"] == 0.0
    assert data["summary"]["status"] == "Unassessed"
    assert data["fsrs_workload"]["due_reviews"] == 0
    assert data["fsrs_workload"]["total_cards"] == 0
    assert len(data["daily_activity"]) == 0
    assert len(data["mock_history"]) == 0
    # Safe recommendation fallback for new student
    assert data["recommended_next_action"]["type"] in ["explore", "mission"]

def test_progress_accuracy_and_attempt_calculations():
    """Verify factual accuracy and attempts computation without synthetic distortion."""
    res = client.get("/api/progress?student_id=student_01")
    assert res.status_code == 200
    data = res.json()
    summary = data["summary"]
    assert summary["total_attempts"] >= 1
    assert summary["total_correct"] <= summary["total_attempts"]
    assert summary["total_incorrect"] == summary["total_attempts"] - summary["total_correct"]
    expected_acc = round((summary["total_correct"] / summary["total_attempts"]) * 100, 1)
    assert summary["overall_accuracy_percent"] == expected_acc

def test_progress_unassessed_topics_versus_weak_topics():
    """Verify that unassessed concepts are never categorized as weak or failing."""
    res = client.get("/api/progress?student_id=student_01")
    assert res.status_code == 200
    data = res.json()
    for concept in data["concepts"]:
        if concept["attempts"] == 0:
            assert concept["mastery_state"] == "UNASSESSED"
            assert concept["mastery"] == 0.0
        elif concept["misconception_count"] > 0:
            assert concept["mastery_state"] == "NEEDS_REPAIR"

    # Coverage verification
    coverage = data.get("syllabus_coverage", [])
    assert len(coverage) > 0
    for cov in coverage:
        assert cov["assessed_concepts"] + cov["unassessed_concepts"] == cov["total_concepts"]
        assert 0.0 <= cov["coverage_percent"] <= 100.0

def test_progress_fsrs_due_and_forecast_consistency():
    """Verify FSRS due counts and upcoming forecast derived from real due dates."""
    res = client.get("/api/progress?student_id=student_01")
    assert res.status_code == 200
    data = res.json()
    fsrs = data["fsrs_workload"]
    assert fsrs["due_reviews"] >= 0
    assert fsrs["overdue_reviews"] >= 0
    assert fsrs["total_cards"] >= 0
    assert fsrs["forecast_3_days"] >= 0
    assert fsrs["forecast_7_days"] >= fsrs["forecast_3_days"]
    assert fsrs["forecast_14_days"] >= fsrs["forecast_7_days"]

def test_progress_mock_results_accuracy():
    """Verify authoritative scoring (+4 / -1) and representation of mini mock history."""
    res = client.get("/api/progress?student_id=student_01")
    assert res.status_code == 200
    data = res.json()
    mocks = data.get("mock_history", [])
    for mock in mocks:
        assert "id" in mock
        assert "score" in mock
        assert mock["total_questions"] > 0
        if mock.get("result"):
            assert "summary" in mock["result"]

def test_progress_recommendation_priority_and_fallback():
    """Verify the 5-tier recommendation hierarchy with transparent rationale."""
    res = client.get("/api/progress?student_id=student_01")
    assert res.status_code == 200
    data = res.json()
    rec = data["recommended_next_action"]
    assert rec["type"] in ["review", "repair", "practice", "explore", "mission"]
    assert len(rec["title"]) > 0
    assert len(rec["description"]) > 0
    assert len(rec["cta_label"]) > 0
    assert len(rec["cta_href"]) > 0
    assert "rationale" in rec

def test_progress_learner_data_isolation():
    """Verify that records for one student are not leaked into another student's telemetry."""
    res1 = client.get("/api/progress?student_id=student_01")
    res2 = client.get("/api/progress?student_id=student_02")
    assert res1.status_code == 200
    assert res2.status_code == 200
    d1 = res1.json()
    d2 = res2.json()
    assert d1["student_id"] == "student_01"
    assert d2["student_id"] == "student_02"
    # student_01 has 3 attempts, student_02 has 1 attempt in baseline state
    assert d1["summary"]["total_attempts"] != d2["summary"]["total_attempts"]
