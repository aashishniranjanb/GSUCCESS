import time
import uuid
import random
import concurrent.futures
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

def simulate_single_user(user_idx):
    client = TestClient(app)
    student_id = f"synth_concurrency_u{user_idx}_{uuid.uuid4().hex[:6]}"
    latencies = []
    
    # 1. Load mission
    t0 = time.time()
    r1 = client.get(f"/api/study/today?student_id={student_id}&minutes=12&mode=balanced")
    latencies.append(("today_mission", time.time() - t0, r1.status_code))
    
    # 2. Submit answer
    t0 = time.time()
    r2 = client.post("/api/study/attempt", json={
        "student_id": student_id,
        "question_id": "q_gpat_001",
        "selected_option": random.choice([0, 1, 2, 3]),
        "response_time_sec": 12.0,
        "confidence": 4
    })
    latencies.append(("attempt", time.time() - t0, r2.status_code))
    
    # 3. View rewards
    t0 = time.time()
    r3 = client.get(f"/api/rewards?student_id={student_id}")
    latencies.append(("rewards", time.time() - t0, r3.status_code))
    
    return latencies

def run_concurrency_benchmark(num_users=20):
    print(f"Running concurrency benchmark with {num_users} simultaneous virtual users...")
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(simulate_single_user, i) for i in range(num_users)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    duration = time.time() - start_total
    
    all_latencies = []
    errors = 0
    for user_res in results:
        for ep, lat, status in user_res:
            all_latencies.append(lat)
            if status >= 400:
                errors += 1
                
    all_latencies.sort()
    n = len(all_latencies)
    p50 = all_latencies[int(n * 0.50)] * 1000
    p95 = all_latencies[int(n * 0.95)] * 1000
    p99 = all_latencies[int(n * 0.99)] * 1000
    
    print(f"Completed in {duration:.2f}s | Total Requests: {n} | Errors: {errors}")
    print(f"Latency: p50={p50:.1f}ms, p95={p95:.1f}ms, p99={p99:.1f}ms")
    return {"users": num_users, "requests": n, "errors": errors, "p50": p50, "p95": p95, "p99": p99}

if __name__ == '__main__':
    run_concurrency_benchmark(5)
    run_concurrency_benchmark(20)
