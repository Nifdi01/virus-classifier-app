from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict, batch


app = FastAPI(
    title="Influenza Classification API",
    description="Sequence-based Influenza type classification",
    version="0.1.0",
)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(batch.router)
