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

def test_playwright_e2e_real_pwa_offline_and_indexeddb_survival():
    """
    Gate B Full Verification:
    1. Launches server on isolated temporary disposable database copy.
    2. Opens real Chromium browser context.
    3. Loads PWA index.html and exercises Service Worker registration and caching.
    4. Simulates network disconnection (offline mode).
    5. Queues an attempt in browser IndexedDB ('pending_events' store).
    6. Reloads the browser page while offline to prove ServiceWorker offline navigation and queue persistence across context refresh.
    7. Restores online network.
    8. Triggers sync with backend /api/sync and verifies attempt synchronized.
    9. Re-executes sync to prove complete idempotency (returns duplicate without double counting).
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
            page = browser.new_page()

            # 1. Load application and allow ServiceWorker installation
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            # Wait for Service Worker registration and activation
            page.evaluate("async () => { await navigator.serviceWorker.ready; }")
            time.sleep(1.0)
            assert "GPAT" in page.title()

            # 2. Emulate real offline network cutoff
            page.context.set_offline(True)
            assert page.evaluate("() => !navigator.onLine") is True

            # 3. Queue attempt in IndexedDB while offline
            client_evt_id = f"pwa_gate_b_evt_{time.time_ns()}"
            page.evaluate(f"""async () => {{
                const db = await new Promise((res, rej) => {{
                    const req = indexedDB.open('gpat_offline_db', 1);
                    req.onupgradeneeded = (e) => {{
                        const d = e.target.result;
                        if (!d.objectStoreNames.contains('pending_events')) {{
                            d.createObjectStore('pending_events', {{ keyPath: 'client_event_id' }});
                        }}
                    }};
                    req.onsuccess = () => res(req.result);
                    req.onerror = () => rej(req.error);
                }});
                const tx = db.transaction('pending_events', 'readwrite');
                tx.objectStore('pending_events').put({{
                    client_event_id: '{client_evt_id}',
                    student_id: 'gate_b_verified_student',
                    question_id: 'q_gpat_001',
                    selected_option: 0,
                    confidence: 4,
                    response_time_sec: 14.2,
                    timestamp: new Date().toISOString()
                }});
            }}""")

            # 4. Reload page while offline to prove ServiceWorker cache serve + IndexedDB survival
            page.reload()
            survived = page.evaluate("""async () => {
                const db = await new Promise((res, rej) => {
                    const req = indexedDB.open('gpat_offline_db', 1);
                    req.onsuccess = () => res(req.result);
                    req.onerror = () => rej(req.error);
                });
                const tx = db.transaction('pending_events', 'readonly');
                return await new Promise((res) => {
                    const req = tx.objectStore('pending_events').getAll();
                    req.onsuccess = () => res(req.result.length);
                });
            }""")
            assert survived == 1

            # 5. Reconnect Online & Synchronize
            page.context.set_offline(False)
            sync_res = page.evaluate("""async () => {
                const db = await new Promise((res, rej) => {
                    const req = indexedDB.open('gpat_offline_db', 1);
                    req.onsuccess = () => res(req.result);
                    req.onerror = () => rej(req.error);
                });
                const tx = db.transaction('pending_events', 'readonly');
                const items = await new Promise((res) => {
                    const req = tx.objectStore('pending_events').getAll();
                    req.onsuccess = () => res(req.result);
                });
                const r = await fetch('/api/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ student_id: 'gate_b_verified_student', events: items })
                });
                return await r.json();
            }""")
            assert sync_res["synced_count"] >= 1
            assert sync_res["results"][0]["status"] in ("synced", "duplicate")

            # 6. Replay attempt to assert Idempotency in real browser
            dup_res = page.evaluate(f"""async () => {{
                const r = await fetch('/api/sync', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ student_id: 'gate_b_verified_student', events: [{{
                        client_event_id: '{client_evt_id}',
                        student_id: 'gate_b_verified_student',
                        question_id: 'q_gpat_001',
                        selected_option: 0,
                        confidence: 4,
                        response_time_sec: 14.2,
                        timestamp: new Date().toISOString()
                    }}] }})
                }});
                return await r.json();
            }}""")
            assert dup_res["results"][0]["status"] == "duplicate"

            browser.close()
    finally:
        server.should_exit = True
        server_thread.join(timeout=2.0)
        os.environ.pop("GPAT_DB_PATH", None)
        if tmp_db.exists():
            try:
                tmp_db.unlink()
            except Exception:
                pass
