from fastapi import FastAPI
from app.api.agent import router as agent_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Multi-Agent System", version="1.0.0")

Instrumentator().instrument(app).expose(app)

app.include_router(agent_router)

@app.get("/")
def root():
    return {"service": "multi-agent-system", "status": "running"}