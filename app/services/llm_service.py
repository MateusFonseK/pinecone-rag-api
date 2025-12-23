from openai import OpenAI
from app.config import settings
from app.services.pinecone_service import search_documents


# OpenAI client instance
_client = OpenAI(api_key=settings.openai_api_key)


def build_context(documents: list[dict]) -> str:
    """
    Build a context string from retrieved documents.

    Args:
        documents: List of documents from Pinecone search

    Returns:
        Formatted context string
    """
    context_parts = []

    for i, doc in enumerate(documents, 1):
        metadata = doc.get("metadata", {})
        text = metadata.get("text", "")
        filename = metadata.get("filename", "unknown")

        context_parts.append(
            f"[Document {i} - {filename}]\n{text}"
        )

    return "\n\n".join(context_parts)


def generate_answer(question: str, max_results: int = 10) -> dict:
    """
    Generate an answer using RAG (Retrieval Augmented Generation).

    1. Search for relevant documents
    2. Build context from documents
    3. Send to LLM to generate answer

    Args:
        question: The user's question
        max_results: Number of documents to retrieve

    Returns:
        Dictionary with answer and sources
    """

    documents = search_documents(question, max_results)

    if not documents:
        return {
            "answer": "I couldn't find any relevant information in the documents.",
            "sources": []
        }

    context = build_context(documents)

    system_prompt = """You are a helpful assistant that answers questions based on the provided documents.

Rules:
1. Only answer based on the information in the documents
2. If the information is not in the documents, say "I don't have this information in the documents"
3. Be specific and cite which document the information comes from
4. Be concise but complete
5. If there are monetary values, dates, or names, include them exactly as they appear"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {question}"}
    ]

    try:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3
        )
    except Exception as e:
        if "temperature" in str(e):
            response = _client.chat.completions.create(
                model=settings.openai_model,
                messages=messages
            )
        else:
            raise e

    answer = response.choices[0].message.content

    sources = []
    for doc in documents:
        metadata = doc.get("metadata", {})
        sources.append({
            "filename": metadata.get("filename", "unknown"),
            "chunk_index": metadata.get("chunk_index", 0),
            "score": doc.get("score", 0.0),
            "text": metadata.get("text", "")[:200] + "..."  
        })

    return {
        "answer": answer,
        "sources": sources
    }
