# Evaluation System — StudyMate AI

## How We Evaluate the LLM

### 1. Agent Internal Evaluation (Critic Agent)
Every response is automatically evaluated by the Critic Agent:
- Relevance to question (0-10)
- Context usage (0-10)
- Clarity and educational value (0-10)
- Accuracy (0-10)
- If score < 5, Tutor Agent retries automatically

### 2. External Evaluation Script (eval_system.py)
A test dataset with known questions and expected keywords:
- Keyword matching score (70% weight)
- Response length score (30% weight)
- Results saved to eval_results.json

## How We Evaluate the Agentic System

### Metrics We Track
- End-to-end latency (Planner → Retrieval → Tutor → Critic)
- Retry rate (how often Critic triggers retry)
- Context hit rate (how often Retrieval finds relevant chunks)
- Average evaluation score per user session

### Observability Tools
- Langfuse: LLM-specific traces, token usage, prompt tracking
- Prometheus: HTTP metrics, latency histograms
- Grafana: Visual dashboards for all metrics
- Loki: Structured logs from each agent node
- Tempo: Distributed traces across agent nodes

## Limitations & Future Improvements
- Current keyword matching is simple — upgrade to semantic similarity
- Add human evaluation feedback loop
- Implement A/B testing between different prompts
- Add RAGAS framework for RAG-specific evaluation