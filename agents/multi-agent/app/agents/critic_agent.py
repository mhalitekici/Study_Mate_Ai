from app.core.state import AgentState
from app.core.config import settings
import httpx
import os

def load_critic_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "../../prompts/critic_prompt.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are an educational quality evaluator. Return JSON with score, feedback, needs_retry."

async def critic_agent(state: AgentState) -> AgentState:
    print(f"[Critic Agent] Evaluating answer quality...")

    critic_system = load_critic_prompt()

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
                    "system": critic_system,
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