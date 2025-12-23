from fastapi import APIRouter, HTTPException
from app.services.pinecone_service import search_documents
from app.schemas.search import SearchRequest, SearchResult, SearchResponse


router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search on documents.

    This searches by meaning, not exact words.
    For example, "payment deadline" will find "due date" or "vencimento".
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    try:
        results = search_documents(request.query, request.top_k)

        search_results = []
        for doc in results:
            metadata = doc.get("metadata", {})

            search_results.append(SearchResult(
                text=metadata.get("text", ""),
                filename=metadata.get("filename", "unknown"),
                chunk_index=metadata.get("chunk_index", 0),
                score=doc.get("score", 0.0)
            ))

        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during search: {str(e)}"
        )
