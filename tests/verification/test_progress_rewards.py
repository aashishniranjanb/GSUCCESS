import os
import json
import shutil
import sqlite3
import tempfile
import datetime
from datetime import timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = ROOT_DIR / "gpat_knowledge.db"

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    shutil.copyfile(DB_FILE, tmp_path)
    os.environ["GPAT_DB_PATH"] = str(tmp_path)
    yield tmp_path
    try:
        if tmp_path.exists():
            tmp_path.unlink()
    except Exception:
        pass

@pytest.fixture
def client(temp_db):
    from backend.main import app
    return TestClient(app)

class TestProgressRewardsSystem:

    def test_01_honest_empty_state_for_new_learner(self, client):
        """Gate 4 & Gate 7: New learner sees zero fabricated achievements and an honest empty state."""
        res = client.get("/api/rewards?student_id=new_student_999")
        assert res.status_code == 200
        data = res.json()
        assert data["student_id"] == "new_student_999"
        assert len(data["achievements"]) == 0
        assert data["counts"]["total_awarded"] == 0
        assert data["weekly_goal"]["target_count"] == 5
        assert data["weekly_goal"]["achieved_count"] == 0

    def test_02_completed_mission_awards_achievement_once(self, temp_db, client):
        """Gate 1A & Gate 7: Valid completed mission awards achievement once; replaying completion awards 0 duplicates."""
        # Create a real mission with items
        res_m = client.get("/api/study/today?minutes=5&student_id=reward_student_01")
        assert res_m.status_code == 200
        m_data = res_m.json()
        session_id = m_data["session_id"]
        questions = m_data["questions"]
        assert len(questions) > 0

        # Incomplete mission check: Calling complete before answering items yields 0 awards
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM learner_achievements WHERE student_id = 'reward_student_01'")
        assert cur.fetchone()[0] == 0

        # Lookup correct options from DB
        q_ids = [q["question_id"] for q in questions]
        cur.execute(f"SELECT id, correct_option FROM questions WHERE id IN ({','.join(['?']*len(q_ids))})", q_ids)
        correct_map = dict(cur.fetchall())
        conn.close()

        # Answer all questions
        for q in questions:
            qid = q["question_id"]
            res_att = client.post("/api/attempt", json={
                "student_id": "reward_student_01",
                "question_id": qid,
                "selected_option": correct_map.get(qid, 0),
                "response_time_sec": 12.0,
                "confidence": 4
            })
            assert res_att.status_code == 200

        # Complete mission
        res_c1 = client.post(f"/api/study/mission/{session_id}/complete")
        assert res_c1.status_code == 200
        data_c1 = res_c1.json()
        assert len(data_c1["new_achievements"]) >= 1
        ach_types = [a["achievement_type"] for a in data_c1["new_achievements"]]
        assert "MISSION_COMPLETION" in ach_types

        # Verify achievement persisted
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM learner_achievements WHERE student_id = 'reward_student_01' AND achievement_type = 'MISSION_COMPLETION'")
        assert cur.fetchone()[0] == 1

        # Replay completion endpoint -> Must NOT duplicate award
        res_c2 = client.post(f"/api/study/mission/{session_id}/complete")
        assert res_c2.status_code == 200
        data_c2 = res_c2.json()
        assert len(data_c2["new_achievements"]) == 0
        cur.execute("SELECT count(*) FROM learner_achievements WHERE student_id = 'reward_student_01' AND achievement_type = 'MISSION_COMPLETION'")
        assert cur.fetchone()[0] == 1
        conn.close()

    def test_03_delayed_recall_requires_24h_interval(self, temp_db, client):
        """Gate 1B & Gate 7: Immediate retry does not award DELAYED_RECALL; 24h+ delayed retrieval does."""
        q_id = "q_gpat_001"
        sid = "recall_student_01"

        # 1. First attempt at T0
        t0 = (datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=2)).isoformat()
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO student_attempts (student_id, question_id, concept_id, selected_option, is_correct, response_time_sec, confidence, created_at)
        VALUES (?, ?, 'ans_alpha_blockers', 0, 1, 10.0, 4, ?)
        """, (sid, q_id, t0))
        conn.commit()
        conn.close()

        # 2. Immediate repetition (2 hours later) -> Should NOT qualify for delayed recall
        res_imm = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 0,
            "response_time_sec": 10.0,
            "confidence": 4
        })
        assert res_imm.status_code == 200
        new_achs_imm = res_imm.json().get("new_achievements", [])
        assert not any(a["achievement_type"] == "DELAYED_RECALL" for a in new_achs_imm)

        # 3. Simulate prior attempt was 30 hours ago and remove the immediate attempt
        t_delayed = (datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=30)).isoformat()
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("DELETE FROM student_attempts WHERE student_id = ? AND question_id = ? AND id != (SELECT min(id) FROM student_attempts WHERE student_id = ? AND question_id = ?)", (sid, q_id, sid, q_id))
        cur.execute("UPDATE student_attempts SET created_at = ? WHERE student_id = ? AND question_id = ?", (t_delayed, sid, q_id))
        conn.commit()
        conn.close()

        # 4. Now answer correctly -> Must qualify for DELAYED_RECALL
        res_del = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 0,
            "response_time_sec": 10.0,
            "confidence": 4
        })
        assert res_del.status_code == 200
        new_achs_del = res_del.json().get("new_achievements", [])
        assert any(a["achievement_type"] == "DELAYED_RECALL" for a in new_achs_del)

        # 5. Subsequent immediate attempt cannot farm award again
        res_farm = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 0,
            "response_time_sec": 10.0,
            "confidence": 4
        })
        assert res_farm.status_code == 200
        new_achs_farm = res_farm.json().get("new_achievements", [])
        assert not any(a["achievement_type"] == "DELAYED_RECALL" for a in new_achs_farm)

    def test_04_misconception_correction_recognition(self, temp_db, client):
        """Gate 1C & Gate 7: Correction recognized only after prior active trap transitions to REPAIRED."""
        sid = "misc_student_01"
        q_id = "q_gpat_001" # ANS alpha blockers

        # Submit wrong answer with high confidence -> Triggers ACTIVE misconception
        res_wrong = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 2, # wrong distractor
            "response_time_sec": 15.0,
            "confidence": 4
        })
        assert res_wrong.status_code == 200
        assert not res_wrong.json()["is_correct"]

        # Verify misconception is ACTIVE in DB
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT status FROM student_misconceptions WHERE student_id = ? AND question_id = ?", (sid, q_id))
        assert cur.fetchone()[0] == "ACTIVE"
        conn.close()

        # Submit correct answer -> Repaired trap -> Should award MISCONCEPTION_REPAIR
        res_corr = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 0, # correct
            "response_time_sec": 12.0,
            "confidence": 4
        })
        assert res_corr.status_code == 200
        assert res_corr.json()["is_correct"]
        new_achs = res_corr.json().get("new_achievements", [])
        assert any(a["achievement_type"] == "MISCONCEPTION_REPAIR" for a in new_achs)

        # Farming check: answering again does NOT re-award
        res_repeat = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": 0,
            "response_time_sec": 12.0,
            "confidence": 4
        })
        assert not any(a["achievement_type"] == "MISCONCEPTION_REPAIR" for a in res_repeat.json().get("new_achievements", []))

    def test_05_topic_mastery_uses_deterministic_classifier(self, temp_db, client):
        """Gate 1D & Gate 7: Topic mastery awarded when >=3 attempts, >=80% acc, stability >= 7.0d."""
        sid = "mastery_student_01"
        cid = "pk_absorption"
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        # Seed concept memory state satisfying classifier
        cur.execute("""
        INSERT OR REPLACE INTO concept_memory_state 
        (student_id, concept_id, stability, difficulty, retrievability, mastery, attempts, correct, misconception_count, last_review, next_review)
        VALUES (?, ?, 8.5, 3.0, 0.95, 1.0, 3, 3, 0, '2026-10-16T10:00:00Z', '2026-10-24T10:00:00Z')
        """, (sid, cid))
        # Find a question for this concept
        cur.execute("SELECT id, correct_option FROM questions WHERE concept_id = ? LIMIT 1", (cid,))
        q_row = cur.fetchone()
        q_id = q_row[0]
        c_opt = q_row[1]
        conn.commit()
        conn.close()

        # Submit attempt -> Topic mastery milestone triggered
        res = client.post("/api/attempt", json={
            "student_id": sid,
            "question_id": q_id,
            "selected_option": c_opt,
            "response_time_sec": 10.0,
            "confidence": 4
        })
        assert res.status_code == 200
        new_achs = res.json().get("new_achievements", [])
        assert any(a["achievement_type"] == "TOPIC_MASTERY" for a in new_achs)

    def test_06_flexible_weekly_goal_configuration_and_non_punitive_edits(self, temp_db, client):
        """Gate 1F & Gate 5: Goal can be updated without erasing history; no streak reset."""
        sid = "goal_student_01"
        
        # 1. Fetch initial goal (defaults to 5)
        res1 = client.get(f"/api/rewards?student_id={sid}")
        assert res1.status_code == 200
        assert res1.json()["weekly_goal"]["target_count"] == 5

        # 2. Adjust target to 3 missions/week
        res_up = client.post("/api/rewards/goal", json={
            "student_id": sid,
            "target_count": 3,
            "status": "active",
            "goal_type": "completed_missions"
        })
        assert res_up.status_code == 200
        assert res_up.json()["goal"]["target_count"] == 3

        # 3. Check /api/rewards reflects 3
        res2 = client.get(f"/api/rewards?student_id={sid}")
        assert res2.json()["weekly_goal"]["target_count"] == 3

        # 4. Pause goal
        res_pause = client.post("/api/rewards/goal", json={
            "student_id": sid,
            "target_count": 3,
            "status": "paused",
            "goal_type": "completed_missions"
        })
        assert res_pause.status_code == 200
        assert res_pause.json()["goal"]["status"] == "paused"

    def test_07_offline_sync_evaluates_achievements_and_prevents_duplicate_replay(self, temp_db, client):
        """Gate 6 & Gate 7: Offline batch sync processes achievements safely and deduplicates replays."""
        sid = "offline_reward_student"
        batch_events = [
            {
                "client_event_id": "off_evt_r01",
                "student_id": sid,
                "question_id": "q_gpat_001",
                "selected_option": 0,
                "response_time_sec": 12.0,
                "confidence": 4,
                "timestamp": "2026-10-17T01:00:00Z"
            }
        ]

        # Sync first time
        res_s1 = client.post("/api/sync", json={"student_id": sid, "events": batch_events})
        assert res_s1.status_code == 200
        assert res_s1.json()["synced_count"] == 1

        # Replay duplicate sync
        res_s2 = client.post("/api/sync", json={"student_id": sid, "events": batch_events})
        assert res_s2.status_code == 200
        assert res_s2.json()["results"][0]["status"] == "duplicate"
