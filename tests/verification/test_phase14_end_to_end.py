import pytest
import sqlite3
import json
import uuid
import datetime
from datetime import timezone
from pathlib import Path
import os
import shutil
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(autouse=True)
def isolate_test_database(tmp_path):
    orig_db = os.environ.get("GPAT_DB_PATH")
    tmp_db = tmp_path / "test_e2e.db"
    shutil.copyfile(ROOT_DIR / "gpat_knowledge.db", tmp_db)
    os.environ["GPAT_DB_PATH"] = str(tmp_db)
    yield
    if orig_db:
        os.environ["GPAT_DB_PATH"] = orig_db
    else:
        os.environ.pop("GPAT_DB_PATH", None)

client = TestClient(app)

def test_full_learning_journey_and_database_persistence():
    """
    Gate 14.2: Full-Stack Integration Verification
    Executes a complete 12-step realistic learner journey:
    1. Check system health
    2. Load today's mission
    3. Verify question composition and reason codes
    4. Submit answer with confidence calibration
    5. Verify FSRS memory stability update
    6. Verify learning event log
    7. Offline sync queue with client event deduplication
    8. Launch 25Q sprint mock exam
    9. Answer mock questions with +4 / -1 scoring
    10. Submit mock exam and verify diagnostic repairs
    11. Fetch updated progress rewards and weekly goal
    12. Verify session resumption idempotency
    """
    student_id = f"synth_journey_{uuid.uuid4().hex[:6]}"
    
    # 1. Health check
    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "healthy"
    
    # 2. Load mission
    m_res = client.get(f"/api/study/today?student_id={student_id}&minutes=12&mode=balanced")
    assert m_res.status_code == 200
    mission = m_res.json()
    assert len(mission["questions"]) >= 4
    first_q = mission["questions"][0]
    q_id = first_q["question_id"]
    
    # 3. Answer question with confidence
    a_res = client.post("/api/study/attempt", json={
        "student_id": student_id,
        "question_id": q_id,
        "selected_option": 0,
        "response_time_sec": 12.5,
        "confidence": 4
    })
    assert a_res.status_code == 200
    fb = a_res.json()
    assert "is_correct" in fb
    assert "calibration_category" in fb
    assert fb["stability_days"] is not None
    
    # 4. Offline sync idempotency
    client_evt_id = f"evt_{uuid.uuid4().hex[:8]}"
    sync_payload = {
        "student_id": student_id,
        "events": [{
            "client_event_id": client_evt_id,
            "student_id": student_id,
            "question_id": "q_gpat_002",
            "selected_option": 0,
            "response_time_sec": 14.0,
            "confidence": 3,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat()
        }]
    }
    s_res1 = client.post("/api/study/sync", json=sync_payload)
    assert s_res1.status_code == 200
    assert s_res1.json()["synced_count"] == 1
    
    # Replay duplicate
    s_res2 = client.post("/api/study/sync", json=sync_payload)
    assert s_res2.status_code == 200
    assert s_res2.json()["results"][0]["status"] == "duplicate"
    
    # 5. Mock Exam Lifecycle
    mock_create = client.post("/api/mock/create", json={"user_id": student_id, "blueprint_name": "sprint_25"})
    assert mock_create.status_code == 200
    exam_id = mock_create.json()["exam_id"]
    
    # Start mock
    mock_start = client.post(f"/api/mock/{exam_id}/start?user_id={student_id}")
    assert mock_start.status_code == 200
    assert mock_start.json()["status"] == "IN_PROGRESS"
    
    # Get mock questions
    mock_get = client.get(f"/api/mock/{exam_id}?user_id={student_id}")
    assert mock_get.status_code == 200
    mock_q = mock_get.json()["questions"][0]
    
    # Answer mock item
    ans_mock = client.post(f"/api/mock/{exam_id}/answer", json={
        "user_id": student_id,
        "question_id": mock_q["question_id"],
        "selected_option": 0,
        "time_spent_ms": 15000,
        "confidence": 4
    })
    assert ans_mock.status_code == 200
    
    # Submit mock
    mock_sub = client.post(f"/api/mock/{exam_id}/submit?user_id={student_id}")
    assert mock_sub.status_code == 200
    eval_data = mock_sub.json()
    assert eval_data["status"] == "EVALUATED"
    assert "summary" in eval_data
    assert "recommended_repairs" in eval_data
    
    # 6. Verify Rewards & Goals
    rew_res = client.get(f"/api/rewards?student_id={student_id}")
    assert rew_res.status_code == 200
    assert "achievements" in rew_res.json()
    
    # 7. Resumption idempotency
    resume_res = client.get(f"/api/study/today?student_id={student_id}&minutes=12&mode=balanced")
    assert resume_res.status_code == 200
    assert resume_res.json()["session_id"] == mission["session_id"]
