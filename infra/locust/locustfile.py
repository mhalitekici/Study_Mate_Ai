from locust import HttpUser, task, between, events
import random
import json

# Test data
TEST_QUESTIONS = [
    "What is Kafka and why was it chosen over RabbitMQ?",
    "How does RAG work in AI systems?",
    "What is microservices architecture?",
    "Explain Redis caching and its benefits",
    "What is the difference between SQL and NoSQL?",
    "How does Docker containerization work?",
    "What is Kubernetes and why use it?",
    "Explain the concept of event-driven architecture",
    "What is a load balancer and how does it work?",
    "How does JWT authentication work?"
]

class StudyMateUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        self.register_and_login()

    def register_and_login(self):
        user_id = random.randint(1000, 9999)
        email = f"loadtest_{user_id}@test.com"

        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "test123",
                "full_name": f"Load Test User {user_id}"
            },
            name="/api/auth/register"
        )

        if register_response.status_code == 201:
            self.token = register_response.json().get("access_token")
        else:
            login_response = self.client.post(
                "/api/auth/login",
                json={"email": email, "password": "test123"},
                name="/api/auth/login"
            )
            if login_response.status_code == 200:
                self.token = login_response.json().get("access_token")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(3)
    def ask_agent(self):
        if not self.token:
            return
        question = random.choice(TEST_QUESTIONS)
        self.client.post(
            "/api/agent/ask",
            json={"question": question, "user_id": 1},
            headers=self.get_headers(),
            name="/api/agent/ask",
            timeout=300
        )

    @task(2)
    def get_recommendations(self):
        if not self.token:
            return
        self.client.post(
            "/api/recsys/recommend",
            json={
                "user_id": random.randint(1, 10),
                "current_question": random.choice(TEST_QUESTIONS),
                "top_k": 5
            },
            name="/api/recsys/recommend"
        )

    @task(2)
    def log_interaction(self):
        if not self.token:
            return
        self.client.post(
            "/api/recsys/log",
            json={
                "user_id": random.randint(1, 10),
                "question": random.choice(TEST_QUESTIONS)
            },
            name="/api/recsys/log"
        )

    @task(1)
    def get_popular_topics(self):
        self.client.get(
            "/api/recsys/popular",
            name="/api/recsys/popular"
        )

    @task(1)
    def health_check(self):
        self.client.get("/api/auth/health", name="/health-check")


class AdminUser(HttpUser):
    wait_time = between(5, 10)
    weight = 1

    @task
    def check_metrics(self):
        self.client.get("/metrics", name="/metrics")