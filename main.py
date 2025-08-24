from fastapi import FastAPI
from app.api.v1.endpoints import journeys

app = FastAPI(title="Flight API", version="1.0.0")

app.include_router(journeys.router, prefix="/v1")
