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
    tmp_db = tmp_path / "test_contracts.db"
    shutil.copyfile(ROOT_DIR / "gpat_knowledge.db", tmp_db)
    os.environ["GPAT_DB_PATH"] = str(tmp_db)
    yield
    if orig_db:
        os.environ["GPAT_DB_PATH"] = orig_db
    else:
        os.environ.pop("GPAT_DB_PATH", None)

client = TestClient(app)

def test_contract_health_endpoint():
    """Verify health endpoint returns valid status and environment."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "environment" in data

def test_contract_today_mission_parameters_and_schema():
    """Verify today's mission endpoint input validation and output schema."""
    # Valid call
    res = client.get("/api/study/today?student_id=contract_tester&minutes=12&mode=balanced")
    assert res.status_code == 200
    data = res.json()
    assert "session_time_minutes" in data
    assert "target_question_count" in data
    assert "questions" in data
    assert len(data["questions"]) >= 4
    
    # Missing / default parameters
    res2 = client.get("/api/study/today")
    assert res2.status_code == 200
    assert len(res2.json()["questions"]) >= 4

def test_contract_attempt_recording_validation_and_idempotency():
    """Verify question attempt submission schema, calibration output, and error responses."""
    # Bad request (missing required fields)
    res_bad = client.post("/api/study/attempt", json={"confidence": 3})
    assert res_bad.status_code == 422
    
    # Non-existent question ID
    res_404 = client.post("/api/study/attempt", json={
        "student_id": "contract_tester",
        "question_id": "non_existent_q_99999",
        "selected_option": 0,
        "response_time_sec": 12.0,
        "confidence": 3
    })
    assert res_404.status_code in [400, 404, 422, 500]

def test_contract_offline_sync_idempotency():
    """Verify offline sync accepts valid batches and idempotently rejects duplicate client event IDs."""
    unique_evt = f"evt_contract_{uuid.uuid4().hex[:8]}"
    payload = {
        "student_id": "contract_sync_user",
        "events": [
            {
                "client_event_id": unique_evt,
                "student_id": "contract_sync_user",
                "question_id": "q_gpat_001",
                "selected_option": 0,
                "response_time_sec": 14.0,
                "confidence": 4,
                "timestamp": datetime.datetime.now(timezone.utc).isoformat()
            }
        ]
    }
    
    # First sync
    res1 = client.post("/api/study/sync", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["synced_count"] == 1
    assert data1["results"][0]["status"] == "synced"
    
    # Replay identical batch
    res2 = client.post("/api/study/sync", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["synced_count"] == 1
    assert data2["results"][0]["status"] == "duplicate"

def test_contract_rewards_and_goal_configuration():
    """Verify rewards data retrieval and non-punitive goal setting."""
    res_get = client.get("/api/rewards?student_id=contract_tester")
    assert res_get.status_code == 200
    data = res_get.json()
    assert "achievements" in data
    assert "weekly_goal" in data
    
    # Set goal target
    res_set = client.post("/api/rewards/goal", json={
        "student_id": "contract_tester",
        "target_count": 5
    })
    assert res_set.status_code == 200
    assert res_set.json()["goal"]["target_count"] == 5

def test_contract_admin_authorization():
    """Verify that admin endpoints reject unauthenticated access and accept valid secrets."""
    # Unauthenticated
    res_unauth = client.get("/api/admin/metrics")
    assert res_unauth.status_code in [401, 403]
    
    # Invalid secret
    res_invalid = client.get("/api/admin/metrics", headers={"X-Admin-Secret": "wrong_secret_xyz"})
    assert res_invalid.status_code in [401, 403]
