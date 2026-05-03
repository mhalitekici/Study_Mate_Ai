from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

qdrant = QdrantClient(url=settings.QDRANT_URL)

def ensure_collection():
    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]
    if settings.COLLECTION_NAME not in names:
        qdrant.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )