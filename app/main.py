from fastapi import APIRouter, FastAPI
from app.config import settings
from app.routers import chat

app = FastAPI(
    title="Pinecone RAG API",
    description="A starter API for RAG (Retrieval Augmented Generation) with Pinecone and OpenAI",
    version="1.0.0"
)

v1 = APIRouter(prefix="/api/v1")

if settings.use_r2_storage:
    from app.routers import documents_r2 as documents
else:
    from app.routers import documents_local as documents

v1.include_router(documents.router)
v1.include_router(chat.router)

app.include_router(v1)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "storage": settings.storage_type,
        "message": "Pinecone RAG API is running!"
    }
