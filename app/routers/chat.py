from fastapi import APIRouter, HTTPException
from app.services.llm_service import generate_answer
from app.schemas.chat import ChatRequest, ChatResponse, Source


# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about your documents.

    This uses RAG (Retrieval Augmented Generation):
    1. Searches for relevant document chunks
    2. Sends them to the LLM as context
    3. LLM generates a natural language answer

    The answer is based ONLY on your documents, not on general knowledge.
    """
    # Validate question
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Generate answer using RAG
        result = generate_answer(request.question, request.max_sources)

        # Format sources
        sources = [
            Source(
                filename=s["filename"],
                chunk_index=s["chunk_index"],
                score=s["score"],
                text=s["text"]
            )
            for s in result["sources"]
        ]

        return ChatResponse(
            question=request.question,
            answer=result["answer"],
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )
