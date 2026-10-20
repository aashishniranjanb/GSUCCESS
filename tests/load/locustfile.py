import uuid
import random
from locust import HttpUser, task, between

class GPATLearnerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Each virtual user simulates an independent synthetic learner account."""
        self.student_id = f"synth_locust_{uuid.uuid4().hex[:8]}"

    @task(3)
    def load_today_mission(self):
        """Simulate learner loading or refreshing today's adaptive mission."""
        self.client.get(
            f"/api/study/today?student_id={self.student_id}&minutes=12&mode=balanced",
            name="/api/study/today"
        )

    @task(2)
    def submit_answer_attempt(self):
        """Simulate learner answering a question with calibrated confidence."""
        payload = {
            "student_id": self.student_id,
            "question_id": "q_gpat_001",
            "selected_option": random.choice([0, 1, 2, 3]),
            "response_time_sec": random.uniform(8.0, 25.0),
            "confidence": random.randint(1, 5)
        }
        self.client.post(
            "/api/study/attempt",
            json=payload,
            name="/api/study/attempt"
        )

    @task(1)
    def view_progress_and_rewards(self):
        """Simulate learner checking progress matrix and achievements."""
        self.client.get(
            f"/api/rewards?student_id={self.student_id}",
            name="/api/rewards"
        )

    @task(1)
    def health_check(self):
        """Periodic background connectivity check."""
        self.client.get("/api/health", name="/api/health")
