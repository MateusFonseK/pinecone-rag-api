from fastapi import FastAPI
from app.routers import documents, chat

app = FastAPI(
    title="Pinecone RAG API",
    description="A starter API for RAG (Retrieval Augmented Generation) with Pinecone and OpenAI",
    version="1.0.0"
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Pinecone RAG API is running!"
    }