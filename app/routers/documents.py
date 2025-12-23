import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_service import process_document, delete_document_by_filename, UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.schemas.document import DocumentUploadResponse, DocumentDeleteResponse


router = APIRouter(prefix="/documents", tags=["Documents"])


def _is_allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or DOCX).

    The document will be:
    1. Saved to the uploads folder
    2. Text extracted from document
    3. Split into chunks
    4. Each chunk saved to Pinecone for semantic search
    """
    if not _is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Only [{', '.join(ALLOWED_EXTENSIONS)}] files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks_created = process_document(file.filename, file_path)

        return DocumentUploadResponse(
            success=True,
            filename=file.filename,
            chunks_created=chunks_created,
            message=f"Document processed successfully. Created {chunks_created} chunks."
        )

    except Exception as e:

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/list")
async def list_documents():
    """
    List all uploaded documents.
    """
    docs = []
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": [], "total": 0}

    for f in os.listdir(UPLOAD_DIR):
        if _is_allowed_file(f):
            path = os.path.join(UPLOAD_DIR, f)
            size = os.path.getsize(path)

            docs.append({
                "filename": f,
                "size_bytes": size,
            })


    return {
        "documents": docs,
        "total": len(docs)
    }


@router.delete("/{filename}", response_model=DocumentDeleteResponse)
async def delete_document(filename: str):
    """
    Delete a document and all its chunks from Pinecone.

    Args:
        filename: Name of the file to delete
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Document '{filename}' not found"
        )

    chunks_deleted = delete_document_by_filename(filename)

    os.remove(file_path)

    return DocumentDeleteResponse(
        success=True,
        filename=filename,
        chunks_deleted=chunks_deleted,
        message=f"Document deleted successfully. Removed {chunks_deleted} chunks."
    )
