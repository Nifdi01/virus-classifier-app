from fastapi import FastAPI


from app.routes import predict, batch

app = FastAPI(
    title="Influenza Classification API",
    description="Sequence-based Influenza type classification",
    version="0.1.0"
)

app.include_router(predict.router)
app.include_router(batch.router)

