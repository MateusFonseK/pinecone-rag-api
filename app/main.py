from fastapi import FastAPI
from app.routers import documents

app = FastAPI(
    title="RAG Docs API",
    description="API for semantic search and Q&A on documents",
    version="1.0.0"
)

app.include_router(documents.router)


@app.get("/")
def health_check():
    return {
        "status": "online", 
        "message": "Ask Your Docs API is running!"
    }