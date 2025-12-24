from fastapi import APIRouter, FastAPI
from app.routers import documents, chat

app = FastAPI(
    title="Pinecone RAG API",
    description="A starter API for RAG (Retrieval Augmented Generation) with Pinecone and OpenAI",
    version="1.0.0"
)

v1 = APIRouter(prefix="/api/v1")
v1.include_router(documents.router)
v1.include_router(chat.router)

app.include_router(v1)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Pinecone RAG API is running!"
    }