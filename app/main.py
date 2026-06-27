from fastapi import FastAPI

from app.registry import registry
from app.routes import predict

app = FastAPI(
    title="Influenza Classification API",
    description="Sequence-based Influenza type classification",
    version="0.1.0"
)

app.include_router(predict.router)

@app.get("/heatlh")
def health():
    return {"status": "ok", "active_model": registry._active_name}
