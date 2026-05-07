# StudyMate AI 🎓

> AI-powered study assistant platform — Distributed microservices with multi-agent system, RAG, Kafka, Redis, Kubernetes, and full observability.

**Kazan Federal University | Group 11-314a | Mehmet Halit Ekici**

---

## 🏗️ Architecture Overview

StudyMate AI is built as a **distributed microservices platform** where students upload study materials, ask questions, and receive AI-generated answers grounded in their own documents.

```
Student → API Gateway (Nginx) → Microservices → Multi-Agent Pipeline → LLM (qwen3.5:4b)
                                      ↕
                              Kafka Event Streaming
                                      ↕
                           AI Service (RAG + Qdrant)
```

---

## 🧩 Services

| Service | Port | Technology | Database | Responsibility |
|---------|------|-----------|----------|----------------|
| Auth Service | 8101 | Python/FastAPI | PostgreSQL | JWT authentication, user registration |
| Material Service | 8102 | Python/FastAPI | PostgreSQL + MinIO | File upload, hot/cold storage |
| AI Service | 8103 | Python/FastAPI | Qdrant + Redis | RAG pipeline, semantic search, caching |
| Memory Service | 8104 | Python/FastAPI | MongoDB | Conversation history, context |
| RecSys Service | 8105 | Python/FastAPI | MongoDB | Recommendations (3 approaches) |
| Multi-Agent | 8110 | LangGraph | Redis (cache) | Planner→Retrieval→Tutor→Critic |

---

## 🤖 Multi-Agent System

LangGraph-based pipeline with 4 specialized agents:

```
Planner Agent → Retrieval Agent → Tutor Agent → Critic Agent
     ↑                                               |
     └───────────── retry if score < 5 ─────────────┘
```

- **Planner**: Fetches last 6 conversation turns from Memory Service
- **Retrieval**: Semantic search in Qdrant (nomic-embed-text embeddings)
- **Tutor**: Generates answer using **qwen3.5:4b** via Ollama
- **Critic**: Scores answer 0-10. Auto-retry if score < 5

### LLM Model Selection (via Langfuse)

| Model | Latency | Tokens/sec | Quality |
|-------|---------|------------|---------|
| qwen2.5:3b | 17.58s | 49.14 | Good |
| qwen2.5:7b | 20.32s | 33.02 | Good |
| qwen3:8b | 39.02s | 25.45 | Very Good |
| deepseek-coder:6.7b | 41.79s | 11.06 | Poor |
| **qwen3.5:4b** | **111.09s** | **32.56** | **Best ✅** |

---

## ⚡ Tech Stack

### Backend
- Python 3.11 + FastAPI + Uvicorn
- LangGraph (multi-agent orchestration)
- Ollama (local LLM runtime)

### Databases
- **PostgreSQL** — Auth, Material (RDBMS, ACID)
- **MongoDB** — Memory, RecSys (flexible schema)
- **Qdrant** — AI Service (vector embeddings)
- **Redis** — Caching (5,000x speedup)
- **MinIO** — Object storage (hot/cold buckets)

### Messaging
- **Apache Kafka** — Event streaming (vs RabbitMQ: no replay; vs NATS: weak persistence)
- Topics: `material.uploaded`, `answer.generated`

### Infrastructure
- **Docker** + Docker Compose
- **Kubernetes** (Docker Desktop)
- **Helm** — Package management
- **ArgoCD** — GitOps CD
- **Terraform** — IaC
- **Ansible** — Kafka deployment (Strimzi operator)
- **Istio** — Service mesh (mTLS, circuit breaker)

### Observability
- **Prometheus** — Metrics (pull-based, Kubernetes-native)
- **Grafana** — Visualization
- **Loki** — Log aggregation (vs ELK: lighter, Grafana-native)
- **Tempo** — Distributed tracing (vs Jaeger: simpler setup)
- **Langfuse** — LLM-specific observability (token usage, model comparison)

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop with Kubernetes enabled
- Ollama installed (`ollama serve`)
- Models pulled:
```bash
ollama pull qwen3.5:4b
ollama pull nomic-embed-text
```

### Run with Docker Compose
```bash
# Clone repository
git clone https://github.com/mhalitekici/Study_Mate_Ai
cd Study_Mate_Ai

# Start all services
docker-compose up -d

# Start infrastructure (Kafka, Redis, DBs, Observability)
docker-compose -f docker-compose.infra.yml up -d
```

### Access Services
| Service | URL |
|---------|-----|
| Auth Service | http://localhost:8101/docs |
| Material Service | http://localhost:8102/docs |
| AI Service | http://localhost:8103/docs |
| Memory Service | http://localhost:8104/docs |
| RecSys Service | http://localhost:8105/docs |
| Multi-Agent | http://localhost:8110/docs |
| Grafana | http://localhost:3000 (admin/admin) |
| Langfuse | http://localhost:3001 |
| API Gateway | http://localhost:8000 |

---

## 📁 Project Structure

```
Study_Mate_Ai/
├── services/
│   ├── auth-service/          # JWT authentication
│   ├── material-service/      # File upload + hot/cold storage
│   ├── ai-service/            # RAG pipeline + Redis cache
│   ├── memory-service/        # Conversation history
│   └── recsys-service/        # Recommender system
├── agents/
│   └── multi-agent/           # LangGraph pipeline
│       ├── prompts/           # System prompts (.md)
│       ├── skills/            # Agent skills (.md)
│       ├── memory/            # Memory management docs
│       └── evals/             # Evaluation scripts
├── infra/
│   ├── kubernetes/manifests/  # K8s deployments
│   ├── helm/studymate-ai/     # Helm charts
│   ├── argocd/                # GitOps config
│   ├── terraform/             # IaC
│   ├── ansible/               # Kafka deployment
│   ├── istio/                 # Service mesh config
│   └── locust/                # Load testing
├── gateway/                   # Nginx config
├── .github/workflows/         # CI/CD pipeline
├── docker-compose.yml
└── run_tests.py
```

---

## 🧪 Testing

```bash
# Run all tests (39 tests across 6 services)
python run_tests.py
```

| Service | Tests | Status |
|---------|-------|--------|
| Auth Service | 7 | ✅ PASSED |
| Material Service | 6 | ✅ PASSED |
| AI Service | 6 | ✅ PASSED |
| Memory Service | 7 | ✅ PASSED |
| RecSys Service | 8 | ✅ PASSED |
| Multi-Agent | 5 | ✅ PASSED |
| **Total** | **39** | **✅ ALL PASSED** |

---

## 🎯 API Usage Example

### 1. Register and Login
```bash
# Register
POST http://localhost:8101/auth/register
{"email": "student@test.com", "password": "test123", "full_name": "Test User"}

# Login → get JWT token
POST http://localhost:8101/auth/login
{"email": "student@test.com", "password": "test123"}
```

### 2. Upload Study Material
```bash
POST http://localhost:8102/materials/upload
Authorization: Bearer <token>
# Upload PDF, TXT, or DOCX (max 50MB)
# → Kafka event: material.uploaded
# → AI Service auto-indexes into Qdrant
```

### 3. Ask AI Agent
```bash
POST http://localhost:8110/agent/ask
{"question": "What is Kafka?", "user_id": 1}

# Response:
# {
#   "answer": "...",        # Generated by qwen3.5:4b
#   "evaluation_score": 8,  # Critic Agent score
#   "cached": false         # Redis cache status
# }
```

### 4. Get Recommendations
```bash
POST http://localhost:8105/recsys/recommend
{"user_id": 1, "current_question": "What is microservices?", "top_k": 5}
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Redis cache speedup | ~5,000x (151s → 0.03s) |
| Load test (20 users) | 0% failure rate |
| /api/agent/ask (cached) | 4.62ms median |
| /api/auth/register | 270ms median |
| Kafka indexing | ~2 chunks per material |

---

## 🏛️ Infrastructure

### Kubernetes
```bash
kubectl get pods -n studymate
# 12 pods: auth x2, ai x2, material x2, memory x2, recsys x2, postgres-auth x1, postgres-material x1
```

### CI/CD (GitHub Actions)
```
Push to main → Run Tests → Build 6 Docker Images → Security Scan (Trivy) → Notify
```

Docker images: `ghcr.io/mhalitekici/studymate-{service-name}:latest`

### Hot/Cold Storage
```bash
# Check storage stats
GET http://localhost:8102/materials/storage/stats

# Archive material to cold storage
POST http://localhost:8102/materials/archive/{material_id}
```

---

## 🔍 Observability

- **Metrics**: `http://localhost:3000` (Grafana dashboard)
- **LLM Traces**: `http://localhost:3001` (Langfuse)
- **Kubernetes**: `kubectl get pods -n studymate`
- **ArgoCD**: `https://localhost:8080` (GitOps dashboard)

---

## 📋 System Prompts & Skills

```
agents/multi-agent/prompts/
├── tutor_prompt.md    # Tutor Agent identity and response guidelines
└── critic_prompt.md   # Evaluation criteria and scoring rubric

agents/multi-agent/skills/
├── search_skill.md    # Semantic search strategy
└── answer_skill.md    # Response structure guidelines

agents/multi-agent/memory/
└── memory_management.md  # Memory architecture decisions
```

---

## 🤝 RecSys — Recommender System

Three approaches implemented:

1. **Content-Based**: Qdrant semantic search for similar content
2. **Collaborative**: User-based filtering from MongoDB interaction history
3. **Heuristic**: 7-day rolling popularity from MongoDB aggregation
4. **Cold Start**: 5 curated defaults for new users

---

## 📄 License

Open-source academic project. Built with open-source technologies only.

---

*Built with ❤️ by Mehmet Halit Ekici | Kazan Federal University | 2026*
