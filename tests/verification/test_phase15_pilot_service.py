import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import sqlite3
import shutil
import tempfile
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

@pytest.fixture(autouse=True)
def isolate_pilot_test_db(monkeypatch):
    """
    Ensures pilot contract tests operate on an isolated temporary copy
    of gpat_knowledge.db, strictly preserving the baseline database.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    real_db = root_dir / "gpat_knowledge.db"
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name
    
    shutil.copy2(real_db, temp_db_path)
    monkeypatch.setenv("GPAT_DB_PATH", temp_db_path)
    
    yield temp_db_path
    
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

@pytest.fixture
def client():
    return TestClient(app)

def test_pilot_status_endpoint(client):
    res = client.get("/api/pilot/status")
    assert res.status_code == 200
    data = res.json()
    assert "pilot_enabled" in data
    assert "real_learners_count" in data
    assert "synthetic_learners_count" in data
    assert "max_pilot_learners" in data

def test_pilot_toggle_requires_admin(client):
    # Unauthenticated attempt should fail
    res = client.post("/api/admin/pilot/toggle", json={"enabled": True})
    assert res.status_code == 401

    # Authenticated attempt with active secret
    secret = os.environ.get("ADMIN_SECRET", "dev_secret") or "dev_secret"
    res_auth = client.post(
        "/api/admin/pilot/toggle",
        json={"enabled": True},
        headers={"X-Admin-Secret": secret}
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["pilot_enabled"] is True

def test_pilot_learner_registration_consent_enforcement(client):
    # Registration without consent must be rejected
    res_no_consent = client.post(
        "/api/pilot/register",
        json={"is_synthetic": False, "consent_given": False}
    )
    assert res_no_consent.status_code == 400

    # Registration with consent succeeds
    res_consent = client.post(
        "/api/pilot/register",
        json={"is_synthetic": False, "consent_given": True}
    )
    assert res_consent.status_code == 200
    data = res_consent.json()
    assert data["student_id"].startswith("plt_learner_")
    assert "access_token" in data
    assert data["consent_given"] is True

def test_pilot_feedback_submission(client):
    # Register synthetic user for test
    reg = client.post(
        "/api/pilot/register",
        json={"is_synthetic": True, "consent_given": True}
    ).json()
    sid = reg["student_id"]

    fb_res = client.post(
        "/api/pilot/feedback",
        json={
            "student_id": sid,
            "feedback_type": "EXPLANATION_CLARITY",
            "rating": 5,
            "question_id": "test_q_01",
            "comment": "Clear distinction of mechanisms."
        }
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["status"] == "recorded"

def test_pilot_aggregated_metrics_protected(client):
    res_unauth = client.get("/api/admin/pilot/metrics")
    assert res_unauth.status_code == 401

    secret = os.environ.get("ADMIN_SECRET", "dev_secret") or "dev_secret"
    res_auth = client.get(
        "/api/admin/pilot/metrics",
        headers={"X-Admin-Secret": secret}
    )
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert "status" in data
    assert "enrolled_learners" in data
    assert "attempt_metrics" in data
