from kafka import KafkaConsumer
from app.core.config import settings
from app.core.qdrant_client import qdrant, ensure_collection
from qdrant_client.models import PointStruct
import json
import httpx
import asyncio
import threading
import uuid

async def get_embeddings(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text}
            )
            return response.json()["embedding"]
    except Exception as e:
        print(f"[Kafka Consumer] Embedding error: {e}")
        return [0.0] * 768

async def process_material_event(event: dict):
    print(f"[Kafka Consumer] Processing material: {event}")
    ensure_collection()

    material_id = event.get("material_id")
    user_id = event.get("user_id")
    minio_path = event.get("minio_path")

    sample_text = f"Study material uploaded by user {user_id}. Path: {minio_path}"

    chunks = [
        sample_text,
        f"Material ID: {material_id} contains study content for user {user_id}."
    ]

    points = []
    for chunk in chunks:
        embedding = await get_embeddings(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "material_id": material_id,
                "user_id": user_id,
                "text": chunk,
                "minio_path": minio_path
            }
        ))

    qdrant.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=points
    )
    print(f"[Kafka Consumer] Indexed {len(points)} chunks for material {material_id}")

def start_kafka_consumer():
    def consume():
        try:
            consumer = KafkaConsumer(
                "material.uploaded",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id="ai-service-group",
                auto_offset_reset="earliest"
            )
            print("[Kafka Consumer] Started listening to material.uploaded")

            for message in consumer:
                event = message.value
                print(f"[Kafka Consumer] Received event: {event}")
                asyncio.run(process_material_event(event))

        except Exception as e:
            print(f"[Kafka Consumer] Error: {e}")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    print("[Kafka Consumer] Consumer thread started")