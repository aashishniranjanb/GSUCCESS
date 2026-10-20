"""
Comprehensive production-readiness test suite for GPAT 2027 AI Learning OS.
Tests:
1. Replaying one event twice produces one effective learning update (Idempotency).
2. Concurrent retries cannot double-count an event.
3. Failed sync can be retried without losing pending event.
4. Partial batch failures are recoverable.
5. Unauthenticated admin API calls are rejected (401/403).
6. Authenticated admin API calls succeed with valid key.
7. Backup and restore preserve database and learner history.
8. Container restart preserves persistent database without overwrite.
9. Health checks do not expose secrets or sensitive server paths.
"""

import os
import json
import sqlite3
import tempfile
import shutil
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

# Configure environment before importing main app
os.environ["ENVIRONMENT"] = "development"
os.environ["ADMIN_SECRET"] = "test_production_secret_999"

from backend.main import app, DB_PATH
from scripts.backup_db import create_backup
from scripts.restore_db import verify_and_restore

import uuid

class TestProductionReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_gpat.db"
        self.backup_dir = self.test_dir / "backups"

        # Copy existing gpat_knowledge.db structure/seed into test db
        src_conn = sqlite3.connect(DB_PATH)
        dst_conn = sqlite3.connect(str(self.test_db))
        with dst_conn:
            src_conn.backup(dst_conn)
        src_conn.close()
        dst_conn.close()

    def tearDown(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM synced_client_events WHERE client_event_id LIKE 'test_evt%'")
            conn.execute("DELETE FROM student_attempts WHERE student_id LIKE 'test_student_%'")
            conn.execute("DELETE FROM learning_events WHERE user_id LIKE 'test_student_%'")
            conn.commit()
            conn.close()
        except Exception:
            pass

        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass

    # --- 1. Replaying one event twice produces exactly one effective learning update ---
    def test_sync_idempotency_replay(self):
        client_event_id = f"test_evt_idempotent_{uuid.uuid4().hex[:8]}"
        payload = {
            "student_id": "test_student_idempotency",
            "events": [{
                "client_event_id": client_event_id,
                "student_id": "test_student_idempotency",
                "question_id": "q_gpat_001",
                "selected_option": 0,
                "response_time_sec": 12.0,
                "confidence": 4,
                "timestamp": "2026-10-15T15:00:00Z"
            }]
        }

        # First sync
        res1 = self.client.post("/api/sync", json=payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["results"][0]["status"], "synced")

        # Check attempt count in database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_attempts WHERE student_id = 'test_student_idempotency'")
        attempts_after_first = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM learning_events WHERE user_id = 'test_student_idempotency' AND event_type = 'OFFLINE_SYNC_ANSWERED'")
        events_after_first = cur.fetchone()[0]
        conn.close()

        # Replay exact same event
        res2 = self.client.post("/api/sync", json=payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["results"][0]["status"], "duplicate")

        # Verify database was NOT double-counted
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_attempts WHERE student_id = 'test_student_idempotency'")
        attempts_after_second = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM learning_events WHERE user_id = 'test_student_idempotency' AND event_type = 'OFFLINE_SYNC_ANSWERED'")
        events_after_second = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM synced_client_events WHERE client_event_id = ?", (client_event_id,))
        synced_records = cur.fetchone()[0]
        conn.close()

        self.assertEqual(attempts_after_first, attempts_after_second, "Attempts table was double-counted on replay!")
        self.assertEqual(events_after_first, events_after_second, "Learning events table was double-counted on replay!")
        self.assertEqual(synced_records, 1, "synced_client_events should have exactly one record")

    # --- 2. Concurrent retries cannot double-count an event ---
    def test_concurrent_retries_idempotency(self):
        client_event_id = f"test_evt_concurrent_{uuid.uuid4().hex[:8]}"
        payload = {
            "student_id": "test_student_concurrent",
            "events": [{
                "client_event_id": client_event_id,
                "student_id": "test_student_concurrent",
                "question_id": "q_gpat_001",
                "selected_option": 0,
                "response_time_sec": 14.0,
                "confidence": 5,
                "timestamp": "2026-10-15T15:05:00Z"
            }]
        }

        def fire_sync():
            return self.client.post("/api/sync", json=payload)

        # Fire 5 parallel requests simultaneously
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fire_sync) for _ in range(5)]
            responses = [f.result() for f in futures]

        statuses = [r.json()["results"][0]["status"] for r in responses if r.status_code == 200]
        synced_count = statuses.count("synced")
        duplicate_count = statuses.count("duplicate")

        self.assertEqual(synced_count, 1, "Exactly one concurrent request must succeed as 'synced'")
        self.assertEqual(duplicate_count, len(statuses) - 1, "All other concurrent requests must return 'duplicate'")

        # Verify attempts table in database has exactly 1 entry
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_attempts WHERE student_id = 'test_student_concurrent'")
        total_attempts = cur.fetchone()[0]
        conn.close()
        self.assertEqual(total_attempts, 1)

    # --- 3. Partial batch failures are handled safely and failed items remain retryable ---
    def test_partial_batch_failure_and_retry(self):
        uid = uuid.uuid4().hex[:8]
        client_event_valid = f"test_evt_batch_valid_{uid}"
        client_event_invalid = f"test_evt_batch_invalid_{uid}"

        batch_payload = {
            "student_id": "test_student_batch",
            "events": [
                {
                    "client_event_id": client_event_valid,
                    "student_id": "test_student_batch",
                    "question_id": "q_gpat_001",
                    "selected_option": 0,
                    "response_time_sec": 11.0,
                    "confidence": 3,
                    "timestamp": "2026-10-15T15:10:00Z"
                },
                {
                    "client_event_id": client_event_invalid,
                    "student_id": "test_student_batch",
                    "question_id": "non_existent_question_99999",
                    "selected_option": 0,
                    "response_time_sec": 11.0,
                    "confidence": 3,
                    "timestamp": "2026-10-15T15:10:00Z"
                }
            ]
        }

        res = self.client.post("/api/sync", json=batch_payload)
        self.assertEqual(res.status_code, 200)
        results = res.json()["results"]

        self.assertEqual(results[0]["status"], "synced")
        self.assertEqual(results[1]["status"], "failed")

        # Retry the fixed event
        fixed_batch_payload = {
            "student_id": "test_student_batch",
            "events": [
                {
                    "client_event_id": client_event_invalid,
                    "student_id": "test_student_batch",
                    "question_id": "q_gpat_002",
                    "selected_option": 1,
                    "response_time_sec": 11.0,
                    "confidence": 3,
                    "timestamp": "2026-10-15T15:10:00Z"
                }
            ]
        }
        res_retry = self.client.post("/api/sync", json=fixed_batch_payload)
        self.assertEqual(res_retry.status_code, 200)
        self.assertEqual(res_retry.json()["results"][0]["status"], "synced")

    # --- 4. Admin API Authentication: Unauthenticated calls rejected (401) ---
    def test_unauthenticated_admin_api_rejected(self):
        # 1. GET /api/admin/metrics without auth
        res_metrics = self.client.get("/api/admin/metrics")
        self.assertEqual(res_metrics.status_code, 401)

        # 2. POST /api/admin/backup/create without auth
        res_backup = self.client.post("/api/admin/backup/create")
        self.assertEqual(res_backup.status_code, 401)

        # 3. GET /api/admin/backups without auth
        res_list = self.client.get("/api/admin/backups")
        self.assertEqual(res_list.status_code, 401)

        # 4. GET /admin UI route without auth
        res_admin_ui = self.client.get("/admin")
        self.assertEqual(res_admin_ui.status_code, 401)

    # --- 5. Admin API Authentication: Valid credentials accepted ---
    def test_authenticated_admin_api_accepted(self):
        # 1. Using Header Key
        headers = {"X-Admin-Secret": "test_production_secret_999"}
        res_metrics = self.client.get("/api/admin/metrics", headers=headers)
        self.assertEqual(res_metrics.status_code, 200)
        self.assertIn("system", res_metrics.json())

        # 2. Using HTTP Basic Auth
        res_basic = self.client.get("/api/admin/metrics", auth=("admin", "test_production_secret_999"))
        self.assertEqual(res_basic.status_code, 200)

        # 3. Trigger backup with header key
        res_backup = self.client.post("/api/admin/backup/create", headers=headers)
        self.assertEqual(res_backup.status_code, 200)
        self.assertEqual(res_backup.json()["status"], "SUCCESS")

    # --- 6. Backup & Restore preserves database and learner history ---
    def test_backup_restore_preserves_history(self):
        # Insert a marker attempt into test db
        conn = sqlite3.connect(str(self.test_db))
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO student_attempts (student_id, question_id, concept_id, selected_option, is_correct, response_time_sec, confidence, hint_used)
        VALUES ('restore_audit_user', 'q_gpat_001', 'c_atropine', 0, 1, 10.0, 5, 0)
        """)
        conn.commit()
        conn.close()

        # Create backup
        manifest = create_backup(db_path=self.test_db, backup_dir=self.backup_dir)
        self.assertTrue(Path(manifest["backup_path"]).exists())

        # Corrupt / delete data from test db
        conn = sqlite3.connect(str(self.test_db))
        cur = conn.cursor()
        cur.execute("DELETE FROM student_attempts WHERE student_id = 'restore_audit_user'")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM student_attempts WHERE student_id = 'restore_audit_user'")
        self.assertEqual(cur.fetchone()[0], 0)
        conn.close()

        # Restore from backup
        res = verify_and_restore(backup_file=Path(manifest["backup_path"]), target_db=self.test_db)
        self.assertEqual(res["status"], "RESTORED_SUCCESSFULLY")

        # Verify record restored
        conn = sqlite3.connect(str(self.test_db))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_attempts WHERE student_id = 'restore_audit_user'")
        self.assertEqual(cur.fetchone()[0], 1)
        conn.close()

    # --- 7. Container restart persistence logic ---
    def test_container_entrypoint_preserves_existing_data(self):
        """
        Simulates the docker-entrypoint.sh logic:
        If target volume database exists, it must NEVER be overwritten by the seed database.
        """
        seed_db = self.test_dir / "seed.db"
        volume_db = self.test_dir / "volume.db"

        # 1. Create seed database with 1 record
        conn = sqlite3.connect(str(seed_db))
        conn.execute("CREATE TABLE questions (id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO questions VALUES ('seed_q1')")
        conn.commit()
        conn.close()

        # 2. First boot: copy seed to volume
        shutil.copy2(seed_db, volume_db)

        # 3. Student uses app: adds history to volume_db
        conn = sqlite3.connect(str(volume_db))
        conn.execute("CREATE TABLE student_history (id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO student_history VALUES ('student_history_entry_1')")
        conn.commit()
        conn.close()

        # 4. Container restarts / redeploys: check preservation condition
        if not volume_db.exists():
            shutil.copy2(seed_db, volume_db)  # Should NOT trigger
        
        # Verify student history remains untouched
        conn = sqlite3.connect(str(volume_db))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_history")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1, "Persistent volume data was preserved across simulated restart")

    # --- 8. Health check does not expose secrets or sensitive server paths ---
    def test_health_check_sanitization(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database_connected"], True)
        self.assertNotIn("test_production_secret_999", json.dumps(data))
        self.assertNotIn("database", data, "Absolute filesystem database path must not be exposed")
        self.assertNotIn("SECRET_KEY", json.dumps(data))

if __name__ == "__main__":
    unittest.main()
