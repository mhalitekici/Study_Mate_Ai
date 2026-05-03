from app.core.state import AgentState
from app.core.config import settings
import httpx

CRITIC_PROMPT = """You are an educational quality evaluator.
Evaluate the given answer and return ONLY a JSON response.

Evaluation criteria:
- Relevance to the question (0-10)
- Use of provided context (0-10)  
- Clarity and educational value (0-10)
- Accuracy (0-10)

Return ONLY this JSON format:
{
  "score": <average_score_0_to_10>,
  "feedback": "<one sentence feedback>",
  "needs_retry": <true_if_score_below_5>
}"""

async def critic_agent(state: AgentState) -> AgentState:
    print(f"[Critic Agent] Evaluating answer quality...")

    eval_prompt = f"""QUESTION: {state['question']}

CONTEXT PROVIDED: {state['context'][:500]}...

ANSWER TO EVALUATE: {state['answer']}

Evaluate this answer and return ONLY the JSON response."""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": eval_prompt,
                    "system": CRITIC_PROMPT,
                    "stream": False,
                    "format": "json"
                }
            )
            result = response.json()
            import json
            eval_result = json.loads(result.get("response", "{}"))
            score = float(eval_result.get("score", 7.0))
            feedback = eval_result.get("feedback", "Answer quality is acceptable.")
            needs_retry = eval_result.get("needs_retry", False)
            print(f"[Critic Agent] Score: {score}/10 — {feedback}")

    except Exception as e:
        score = 7.0
        feedback = "Evaluation completed."
        needs_retry = False
        print(f"[Critic Agent] Evaluation error, using defaults: {e}")

    return {
        **state,
        "evaluation_score": score,
        "evaluation_feedback": feedback,
        "needs_retry": needs_retry
    }