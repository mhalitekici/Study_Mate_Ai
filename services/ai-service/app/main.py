from fastapi import FastAPI
from app.api.ai import router as ai_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="AI Assistant Service", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(ai_router)

@app.get("/")
def root():
    return {"service": "ai-service", "status": "running"}