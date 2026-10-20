import unittest
import tempfile
import shutil
import sqlite3
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from learner_engine import LearnerEngine
from backend.main import app, DB_PATH
from fastapi.testclient import TestClient

BASELINE_DB = DB_PATH

class TestHypothesisOrchestrationInvariants(unittest.TestCase):
    """
    Hypothesis property-based invariant test suite for Phase 3 study orchestration.
    Asserts:
    1. Time budget monotonicity & bounds.
    2. Candidate diversity invariant (never > 2 consecutive items with same non-empty concept_id).
    3. Explainable reason codes and candidate types on every recommended task.
    4. Attempt synchronization idempotency under randomized inputs.
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_path = Path(self.tmp.name)
        shutil.copyfile(BASELINE_DB, self.tmp_path)
        self.engine = LearnerEngine(db_path=self.tmp_path)

    def tearDown(self):
        try:
            if self.tmp_path.exists():
                self.tmp_path.unlink()
        except Exception:
            pass

    @settings(max_examples=25, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        target_minutes=st.integers(min_value=5, max_value=60),
        mode=st.sampled_from(["balanced", "exam"])
    )
    def test_property_daily_mission_bounds_and_diversity(self, target_minutes, mode):
        session = self.engine.generate_daily_session(
            student_id="test_property_student",
            session_minutes=target_minutes,
            mode=mode
        )
        questions = session.get("questions", [])
        self.assertGreaterEqual(len(questions), 1)

        # Invariant 1: Total estimated seconds is bounded by session duration (with minimum 4 question baseline)
        total_estimated_sec = sum(q.get("estimated_seconds", 90) for q in questions)
        expected_q_count = max(4, int(target_minutes / 2.5))
        max_allowed_sec = max(expected_q_count * 150, (target_minutes * 60) + 180)
        self.assertLessEqual(total_estimated_sec, max_allowed_sec)

        # Invariant 2: Candidate diversity - no more than 2 consecutive questions with same concept_id
        for i in range(len(questions) - 2):
            c1 = questions[i].get("concept_id")
            c2 = questions[i + 1].get("concept_id")
            c3 = questions[i + 2].get("concept_id")
            if c1 and c1 == c2 and c2 == c3:
                self.fail(f"Diversity invariant violated: 3 consecutive questions with concept_id {c1}")

        # Invariant 3: All questions have valid candidate_type and non-empty reason_codes
        valid_candidate_types = {"DUE_REVIEW", "TARGETED_REPAIR", "NEW_LEARNING", "PYQ_PRACTICE"}
        for q in questions:
            self.assertIn(q.get("candidate_type"), valid_candidate_types)
            self.assertIsInstance(q.get("reason_codes"), list)
            self.assertGreaterEqual(len(q.get("reason_codes")), 1)

    @settings(max_examples=15, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        selected_option=st.integers(min_value=0, max_value=3),
        confidence=st.integers(min_value=1, max_value=5),
        response_time_sec=st.floats(min_value=5.0, max_value=120.0)
    )
    def test_property_offline_sync_idempotency(self, selected_option, confidence, response_time_sec):
        client = TestClient(app)
        event_id = f"hypo_sync_evt_{selected_option}_{confidence}"
        batch = {
            "student_id": "test_hypo_sync_user",
            "events": [
                {
                    "client_event_id": event_id,
                    "question_id": "q_gpat_001",
                    "selected_option": selected_option,
                    "confidence": confidence,
                    "response_time_sec": response_time_sec,
                    "timestamp": "2026-10-17T01:00:00Z"
                }
            ]
        }
        
        try:
            # First submission
            res1 = client.post("/api/sync", json=batch)
            self.assertEqual(res1.status_code, 200)
            data1 = res1.json()
            self.assertEqual(len(data1["results"]), 1)
            self.assertIn(data1["results"][0]["status"], ("synced", "duplicate"))

            # Second submission with same client_event_id must be detected as duplicate (idempotent)
            res2 = client.post("/api/sync", json=batch)
            self.assertEqual(res2.status_code, 200)
            data2 = res2.json()
            self.assertEqual(len(data2["results"]), 1)
            self.assertEqual(data2["results"][0]["status"], "duplicate")
        finally:
            conn = sqlite3.connect(BASELINE_DB)
            conn.execute("DELETE FROM synced_client_events WHERE student_id = 'test_hypo_sync_user'")
            conn.execute("DELETE FROM student_attempts WHERE student_id = 'test_hypo_sync_user'")
            conn.execute("DELETE FROM learning_events WHERE user_id = 'test_hypo_sync_user'")
            conn.execute("DELETE FROM fsrs_cards WHERE student_id = 'test_hypo_sync_user'")
            conn.commit()
            conn.close()

if __name__ == "__main__":
    unittest.main()
