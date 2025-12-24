import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.document_service import process_document, delete_document_by_filename, UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.schemas.document import DocumentUploadResponse, DocumentDeleteResponse, DocumentListResponse, DocumentInfo


router = APIRouter(prefix="/documents", tags=["Documents"])


def _is_allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


@router.post("", response_model=DocumentUploadResponse, status_code=201)
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


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents.
    """
    if not os.path.exists(UPLOAD_DIR):
        return DocumentListResponse(documents=[], total=0)

    docs = [
        DocumentInfo(filename=f, size_bytes=os.path.getsize(os.path.join(UPLOAD_DIR, f)))
        for f in os.listdir(UPLOAD_DIR)
        if _is_allowed_file(f)
    ]

    return DocumentListResponse(documents=docs, total=len(docs))


@router.get("/{filename}")
async def get_document(filename: str):
    """
    Download a specific document.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")

    return FileResponse(file_path, filename=filename, media_type="application/octet-stream")


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
