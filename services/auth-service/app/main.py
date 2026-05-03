from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.auth import router as auth_router
from prometheus_fastapi_instrumentator import Instrumentator

# Database tablolarını oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service", version="1.0.0")

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Router
app.include_router(auth_router)

@app.get("/")
def root():
    return {"service": "auth-service", "status": "running"}