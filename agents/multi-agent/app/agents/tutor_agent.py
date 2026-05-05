from app.core.state import AgentState
from app.core.config import settings
import httpx
import time
import os

def load_system_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(__file__), 
        "../../prompts/tutor_prompt.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are StudyMate AI, an expert educational assistant."

async def tutor_agent(state: AgentState) -> AgentState:
    print(f"[Tutor Agent] Generating answer for: {state['question'][:50]}...")

    system_prompt = load_system_prompt()

    history_text = ""
    for msg in state.get("history", [])[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_text += f"{role.upper()}: {content}\n"

    prompt = f"""CONTEXT FROM STUDY MATERIALS:
{state['context']}

CONVERSATION HISTORY:
{history_text}

STUDENT QUESTION: {state['question']}

Please provide a clear, educational answer based on the context above.

ANSWER:"""

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False
                }
            )
            result = response.json()
            answer = result.get("response", "I could not generate an answer.")
            latency = time.time() - start_time
            prompt_tokens = result.get("prompt_eval_count", 0)
            completion_tokens = result.get("eval_count", 0)

            print(f"[Tutor Agent] Answer generated ({len(answer)} chars)")
            print(f"[Tutor Agent] Latency: {round(latency, 2)}s | Tokens: {completion_tokens}")

            try:
                from langfuse import Langfuse
                lf = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST
                )
                lf.generation(
                    name="tutor-agent-generation",
                    model=settings.OLLAMA_MODEL,
                    input=prompt,
                    output=answer,
                    usage={
                        "input": prompt_tokens,
                        "output": completion_tokens,
                        "total": prompt_tokens + completion_tokens
                    },
                    metadata={
                        "latency_seconds": round(latency, 2),
                        "tokens_per_second": round(completion_tokens / latency, 2) if latency > 0 else 0,
                        "model": settings.OLLAMA_MODEL
                    }
                )
                lf.flush()
            except Exception as e:
                print(f"[Tutor Agent] Langfuse error: {e}")

    except Exception as e:
        answer = f"I encountered an error generating the answer: {str(e)}"
        print(f"[Tutor Agent] Error: {e}")

    return {**state, "answer": answer}