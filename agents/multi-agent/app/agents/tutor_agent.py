from app.core.state import AgentState
from app.core.config import settings
import httpx
import time

SYSTEM_PROMPT = """You are StudyMate AI, an expert educational assistant.
Your role is to help students understand their study materials deeply.

Guidelines:
- Base answers primarily on the provided context
- Be clear, concise, and educational  
- Use examples to clarify complex concepts
- If context is insufficient, acknowledge it and provide general knowledge
- Encourage deeper learning"""

async def tutor_agent(state: AgentState) -> AgentState:
    print(f"[Tutor Agent] Generating answer for: {state['question'][:50]}...")

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
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
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

            # Langfuse'a gönder
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
                print(f"[Tutor Agent] Sent to Langfuse ✓")
            except Exception as e:
                print(f"[Tutor Agent] Langfuse error: {e}")

    except Exception as e:
        answer = f"I encountered an error generating the answer: {str(e)}"
        print(f"[Tutor Agent] Error: {e}")

    return {**state, "answer": answer}