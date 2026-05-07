from fastapi import FastAPI
from app.api.material import router as material_router
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.security import HTTPBearer

security = HTTPBearer()

app = FastAPI(
    title="Material Service",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

Instrumentator().instrument(app).expose(app)

app.include_router(material_router)

@app.get("/")
def root():
    return {"service": "material-service", "status": "running"}