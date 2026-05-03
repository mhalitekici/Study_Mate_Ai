from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
import httpx
import json

qdrant = QdrantClient(url=settings.QDRANT_URL)

async def get_embeddings(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        return response.json()["embedding"]

async def retrieve_context(question: str, user_id: int, top_k: int = 5) -> str:
    try:
        query_vector = await get_embeddings(question)
        results = qdrant.search(
            collection_name=settings.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=Filter(
                must=[FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )]
            ),
            limit=top_k
        )
        if not results:
            return "No relevant context found in uploaded materials."
        
        context_parts = []
        for r in results:
            context_parts.append(r.payload.get("text", ""))
        return "\n\n".join(context_parts)
    except Exception:
        return "No relevant context found."

async def generate_answer(
    question: str,
    context: str,
    history: list[dict],
    trace=None
) -> str:
    system_prompt = """You are StudyMate AI, an intelligent study assistant.
You help students understand their study materials by answering questions based on the provided context.

Rules:
- Always base your answers on the provided context
- If the context doesn't contain relevant information, say so clearly
- Be concise, clear, and educational
- Use examples when helpful"""

    history_text = ""
    for msg in history[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_text += f"{role.upper()}: {content}\n"

    prompt = f"""CONTEXT FROM STUDY MATERIALS:
{context}

CONVERSATION HISTORY:
{history_text}

STUDENT QUESTION: {question}

ANSWER:"""

    async with httpx.AsyncClient(timeout=60) as client:
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
        
        if trace:
            trace.generation(
                name="ollama-generation",
                model=settings.OLLAMA_MODEL,
                input=prompt,
                output=answer
            )
        
        return answer