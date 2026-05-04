from fastapi import FastAPI
from app.api.ai import router as ai_router
from app.core.kafka_consumer import start_kafka_consumer
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="AI Assistant Service", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(ai_router)

@app.on_event("startup")
async def startup_event():
    start_kafka_consumer()
    print("[AI Service] Kafka consumer started")

@app.get("/")
def root():
    return {"service": "ai-service", "status": "running"}