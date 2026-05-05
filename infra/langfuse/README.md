# Langfuse — LLM Observability

## What is Langfuse?

Langfuse is an open-source LLM observability platform used in StudyMate AI
to monitor, evaluate, and compare language model performance.

## Why Langfuse?

Unlike general observability tools (Prometheus, Grafana), Langfuse is
specifically designed for LLM applications:

- **Token tracking**: Monitor input/output token usage per model
- **Latency**: Measure response time per generation
- **Model comparison**: Compare qwen2.5 vs qwen3.5:4b side by side
- **Evals**: Score and evaluate LLM responses automatically

## Model Comparison Results

| Model | Avg Latency | Tokens/sec | Quality |
|-------|-------------|------------|---------|
| qwen2.5:3b | 17.58s | 49.14 | Good |
| qwen2.5:7b | 20.32s | 33.02 | Good |
| qwen3:8b | 39.02s | 25.45 | Very Good |
| qwen3.5:4b | 111.09s | 32.56 | Best |
| deepseek-coder:6.7b | 41.79s | 11.06 | Poor |

## Decision

qwen3.5:4b was selected based on Langfuse observability data:
- Highest quality output (3,617 tokens average)
- Most detailed educational explanations
- Acceptable latency for educational platform use case

## Access

- URL: http://localhost:3001
- Username: halit@studymate.com
- Password: (set during first login)

## Integration

Langfuse is integrated in:
- `agents/multi-agent/app/agents/tutor_agent.py`
- `agents/multi-agent/app/core/langfuse_client.py`
- `agents/multi-agent/evals/model_comparison.py`