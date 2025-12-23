from pinecone import Pinecone
from app.config import settings
from app.services.embedding_service import generate_embedding


_client = Pinecone(api_key=settings.pinecone_api_key)

_index = _client.Index(settings.pinecone_index_name)


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


def list_ids_by_filename(filename: str) -> list[str]:
    """
    List all vector IDs that belong to a specific filename.
    """
    results = _index.list(prefix=f"{filename}_")
    ids = []
    for id_list in results:
        ids.extend(id_list)
    return ids


def delete_by_ids(ids: list[str]) -> bool:
    """
    Delete multiple vectors by their IDs.
    """
    if ids:
        _index.delete(ids=ids)
    return True

