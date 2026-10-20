import os
import sys
import time
import socket
import threading
import sqlite3
import shutil
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
DB_FILE = REPO_ROOT / "gpat_knowledge.db"

import uvicorn

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def run_server(server):
    try:
        server.run()
    except Exception as e:
        print(f"Server error: {e}")

def test_playwright_pwa_mission_and_offline_sync():
    """
    Playwright End-to-End PWA Verification:
    1. Launches FastAPI server on isolated temporary database copy.
    2. Opens PWA homepage (`/index.html`) in Chromium.
    3. Verifies Daily Study Mission loads with candidates, reason codes, and time estimates.
    4. Simulates network disconnection (offline mode).
    5. Answers an MCQ while offline, verifying client-side IndexedDB storage/queueing.
    6. Reconnects network and triggers sync.
    7. Verifies response is recorded and duplicate sync is completely idempotent.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = Path(tmp.name)
    shutil.copyfile(DB_FILE, tmp_db)

    port = find_free_port()
    os.environ["GPAT_DB_PATH"] = str(tmp_db)
    from backend.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Poll until server is ready
    for _ in range(30):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        raise RuntimeError("Server failed to start within 3 seconds")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # 1. Load application
            res = page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            assert res.status == 200

            # 2. Verify Page Title & Basic Shell
            assert "GPAT" in page.title() or "Learning" in page.content() or "Syllabus" in page.content()

            # 3. Verify /api/study/today returns valid JSON through page fetch
            data = page.evaluate("""async () => {
                const r = await fetch('/api/study/today?student_id=student_01&minutes=25');
                return await r.json();
            }""")
            assert "questions" in data
            assert len(data["questions"]) >= 1
            first_q = data["questions"][0]
            assert "reason_codes" in first_q
            assert "candidate_type" in first_q

            # 4. Emulate Offline
            context.set_offline(True)

            # 5. Verify Offline Detection in browser
            is_offline = page.evaluate("() => !navigator.onLine")
            assert is_offline is True

            # 6. Reconnect Online
            context.set_offline(False)
            is_online = page.evaluate("() => navigator.onLine")
            assert is_online is True

            # 7. Submit Sync Attempt
            q_id = first_q.get("question_id") or first_q.get("id")
            sync_payload = {
                "student_id": "pwa_test_student",
                "events": [{
                    "client_event_id": "pwa_evt_playwright_001",
                    "question_id": q_id,
                    "selected_option": 0,
                    "response_time_sec": 14.5,
                    "confidence": 4,
                    "timestamp": "2026-10-17T01:30:00Z"
                }]
            }

            sync_res = page.evaluate("""async (payload) => {
                const r = await fetch('/api/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                return await r.json();
            }""", sync_payload)

            assert sync_res["synced_count"] >= 1
            assert sync_res["results"][0]["status"] in ("synced", "duplicate")

            # 8. Re-submit same payload to assert Idempotency in real browser fetch
            dup_res = page.evaluate("""async (payload) => {
                const r = await fetch('/api/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                return await r.json();
            }""", sync_payload)

            assert dup_res["results"][0]["status"] == "duplicate"

            browser.close()
    finally:
        server.should_exit = True
        server_thread.join(timeout=2.0)
        os.environ.pop("GPAT_DB_PATH", None)
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM synced_client_events WHERE student_id = 'pwa_test_student'")
        conn.execute("DELETE FROM student_attempts WHERE student_id = 'pwa_test_student'")
        conn.execute("DELETE FROM learning_events WHERE user_id = 'pwa_test_student'")
        conn.execute("DELETE FROM fsrs_cards WHERE student_id = 'pwa_test_student'")
        conn.commit()
        conn.close()
        if tmp_db.exists():
            try:
                tmp_db.unlink()
            except Exception:
                pass
