from pinecone import Pinecone
from app.config import settings
from app.services.embedding_service import generate_embedding


_client = Pinecone(api_key=settings.pinecone_api_key)

_index = _client.Index(settings.pinecone_index_name)


def get_index_stats() -> dict:
    
    return _index.describe_index_stats()


def upsert_document(doc_id: str, text: str, metadata: dict) -> bool:
    
    embedding = generate_embedding(text)
    
    metadata["text"] = text

    _index.upsert(vectors=[(doc_id, embedding, metadata)])

    return True


def search_documents(query: str, top_k: int = 5) -> list[dict]:
    
    query_embedding = generate_embedding(query)
    
    results = _index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    documents = []

    for match in results.matches:
        documents.append({
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        })

    return documents


def delete_document(doc_id: str) -> bool:

    _index.delete(ids=[doc_id])

    return True


