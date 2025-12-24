import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.services.document_service import process_document, delete_document_by_filename, ALLOWED_EXTENSIONS
from app.services import storage_service
from app.schemas.document import DocumentUploadResponse, DocumentDeleteResponse, DocumentListResponse, DocumentInfo


router = APIRouter(prefix="/documents", tags=["Documents"])


def _is_allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, DOCX, TXT or MD).

    The document will be:
    1. Saved to Cloudflare R2 storage
    2. Text extracted from document
    3. Split into chunks
    4. Each chunk saved to Pinecone for semantic search
    """
    if not _is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Only [{', '.join(ALLOWED_EXTENSIONS)}] files are allowed"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunks_created = process_document(file.filename, tmp_path)
        storage_service.upload_file(tmp_path, file.filename)

        return DocumentUploadResponse(
            success=True,
            filename=file.filename,
            chunks_created=chunks_created,
            message=f"Document processed successfully. Created {chunks_created} chunks."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents.
    """
    files = storage_service.list_files()

    docs = [
        DocumentInfo(filename=f["filename"], size_bytes=f["size_bytes"])
        for f in files
        if _is_allowed_file(f["filename"])
    ]

    return DocumentListResponse(documents=docs, total=len(docs))


@router.get("/{filename}")
async def get_document(filename: str):
    """
    Download a specific document.
    """
    if not storage_service.file_exists(filename):
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")

    file_stream = storage_service.get_file_stream(filename)

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.delete("/{filename}", response_model=DocumentDeleteResponse)
async def delete_document(filename: str):
    """
    Delete a document and all its chunks from Pinecone.
    """
    if not storage_service.file_exists(filename):
        raise HTTPException(
            status_code=404,
            detail=f"Document '{filename}' not found"
        )

    chunks_deleted = delete_document_by_filename(filename)
    storage_service.delete_file(filename)

    return DocumentDeleteResponse(
        success=True,
        filename=filename,
        chunks_deleted=chunks_deleted,
        message=f"Document deleted successfully. Removed {chunks_deleted} chunks."
    )
