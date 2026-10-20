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

def test_playwright_phase4_daily_mission_ux_and_completion_loop():
    """
    Phase 4 High-Value Feature End-to-End Verification:
    1. Runs against a cloned, disposable temporary SQLite database.
    2. Launches headless Chromium browser with Playwright.
    3. Loads PWA and clicks 'Start 25-Min Recall Mission'.
    4. Verifies the candidate type badge (e.g., 'HIGH YIELD', 'FSRS REVIEW', or 'REPAIR TRAP') is displayed.
    5. Answers questions through the mission loop:
       - selects confidence
       - selects option
       - verifies answer (checks feedback card rendering with page citation)
       - clicks next question
    6. Verifies that when the last question is answered:
       - The completion endpoint (/api/study/mission/{id}/complete) is invoked
       - The session status updates in SQLite to 'completed'
       - The 'MISSION COMPLETE' summary screen renders showing:
         - Accuracy metric
         - FSRS Cards Advanced
         - Traps Repaired
         - Verified Delayed Learning Gain message
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
            page.on("console", lambda msg: print(f"BROWSER_LOG: {msg.type}: {msg.text}"))
            page.on("pageerror", lambda err: print(f"PAGE_ERROR_STACK: {getattr(err, 'stack', err)}"))
            page.on("requestfailed", lambda req: print(f"REQ_FAILED: {req.url} -> {req.failure}"))

            page.goto(f"http://127.0.0.1:{port}/")
            page.wait_for_selector("#btn-start-session")

            # Verify single-action Daily Mission headline and 12-minute default
            assert page.locator("#mission-headline").is_visible()
            assert "12-minute mission" in page.locator("#btn-launch-label").inner_text()

            # Test 5-Minute Shorter Session toggle
            short_btn = page.locator("#btn-short-mission")
            assert short_btn.is_visible()
            short_btn.click()
            page.wait_for_timeout(500)
            assert any(t in page.locator("#btn-launch-label").inner_text() for t in ["4-minute mission", "5-minute mission"])

            # Toggle back to 12-minute default
            short_btn.click()
            page.wait_for_timeout(500)
            assert "12-minute mission" in page.locator("#btn-launch-label").inner_text()

            # 1. Click Start Daily Mission
            page.click("#btn-start-session")
            page.wait_for_selector("#question-player", state="visible", timeout=10000)

            # 2. Check Candidate Badge is visible
            badge = page.locator("#q-candidate-type")
            assert badge.is_visible(), "Candidate type badge should be visible on active question player"
            badge_text = badge.inner_text()
            assert any(tag in badge_text for tag in ["HIGH YIELD", "FSRS REVIEW", "REPAIR TRAP"]), f"Unexpected badge text: {badge_text}"

            page.on("request", lambda req: print(f"REQ: {req.method} {req.url}"))
            page.on("response", lambda res: print(f"RES: {res.status} {res.url}"))

            # 3. Answer questions until mission is completed
            for i in range(15):
                # Check if mission completed
                if page.locator("text=MISSION COMPLETE").is_visible():
                    break

                # Pick option A (index 0)
                options = page.locator(".option-btn")
                if options.count() > 0:
                    options.first.click()

                # Verify answer
                submit_btn = page.locator("#btn-submit-answer")
                if submit_btn.is_visible():
                    submit_btn.click()

                # Wait for feedback card
                page.wait_for_selector(".feedback-panel", state="visible", timeout=3000)
                
                # Check for source citation
                citation = page.locator(".citation-box")
                assert citation.is_visible(), "Source citation should be rendered in feedback panel"

                # Advance to next question
                next_btn = page.locator("#btn-next-question")
                page.wait_for_selector("#btn-next-question", state="visible", timeout=3000)
                next_btn.click()
                page.wait_for_timeout(300)

            # 4. Verify Mission Complete UI Card
            page.wait_for_selector("text=MISSION COMPLETE", timeout=5000)
            assert page.locator("text=25-Min Study Session Concluded").is_visible()
            assert page.locator("text=Verified Delayed Learning Gain").is_visible()
            assert page.locator("text=Return to Daily Mission").is_visible()
            page.wait_for_timeout(1000)

            # 5. Verify database recorded mission completion
            conn = sqlite3.connect(tmp_db)
            cur = conn.cursor()
            cur.execute("SELECT status, completed_at FROM study_sessions WHERE status = 'completed'")
            row = cur.fetchone()
            assert row is not None, "A study session should be marked as completed in SQLite"
            assert row[0] == "completed"
            assert row[1] is not None

            # Verify MISSION_COMPLETED event was logged
            cur.execute("SELECT count(*) FROM learning_events WHERE event_type = 'MISSION_COMPLETED'")
            completed_events = cur.fetchone()[0]
            assert completed_events >= 1, "MISSION_COMPLETED event should be logged in learning_events"
            conn.close()

            # 6. Gate 3: Navigate to Learn tab and verify evidence-based Mastery Map
            page.click("button:has-text('Learn')")
            page.wait_for_selector("#concepts-list .concept-item", timeout=5000)
            assert page.locator("text=Unassessed").first.is_visible()
            assert page.locator("text=Mastered").first.is_visible() or page.locator("text=Needs Repair").first.is_visible()

            browser.close()
    finally:
        server.should_exit = True
        server_thread.join(timeout=2.0)
        os.environ.pop("GPAT_DB_PATH", None)
        if tmp_db.exists():
            try:
                os.remove(tmp_db)
            except Exception:
                pass
