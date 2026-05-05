from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
import httpx

qdrant = QdrantClient(url=settings.QDRANT_URL)

async def get_embeddings(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://host.docker.internal:11434/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text}
            )
            return response.json()["embedding"]
    except Exception:
        return [0.0] * 768

async def content_based_recommend(
    user_id: int,
    current_question: str,
    top_k: int = 5
) -> list[dict]:
    try:
        query_vector = await get_embeddings(current_question)

        results = qdrant.search(
            collection_name=settings.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=Filter(
                must_not=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=top_k
        )

        recommendations = []
        seen_texts = set()

        for r in results:
            text = r.payload.get("text", "")
            if text and text not in seen_texts:
                seen_texts.add(text)
                recommendations.append({
                    "type": "content_based",
                    "text": text[:200],
                    "score": round(r.score, 3),
                    "reason": "Similar to your current question"
                })

        return recommendations

    except Exception as e:
        print(f"[Content-Based] Error: {e}")
        return []