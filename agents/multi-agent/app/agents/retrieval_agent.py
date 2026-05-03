from app.core.state import AgentState
from app.core.config import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import httpx

qdrant = QdrantClient(url=settings.QDRANT_URL)

async def get_embeddings(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text}
            )
            return response.json()["embedding"]
    except Exception:
        return [0.0] * 768

async def retrieval_agent(state: AgentState) -> AgentState:
    print(f"[Retrieval Agent] Searching context for: {state['question'][:50]}...")
    
    try:
        query_vector = await get_embeddings(state["question"])
        
        results = qdrant.search(
            collection_name=settings.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=Filter(
                must=[FieldCondition(
                    key="user_id",
                    match=MatchValue(value=state["user_id"])
                )]
            ),
            limit=5
        )

        if results:
            context_parts = [r.payload.get("text", "") for r in results]
            context = "\n\n".join(context_parts)
            print(f"[Retrieval Agent] Found {len(results)} relevant chunks")
        else:
            context = "No relevant context found in uploaded materials."
            print("[Retrieval Agent] No context found")

    except Exception as e:
        context = "No relevant context found."
        print(f"[Retrieval Agent] Error: {e}")

    return {**state, "context": context}