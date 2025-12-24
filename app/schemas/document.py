from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""

    success: bool
    filename: str
    chunks_created: int
    message: str


class DocumentDeleteResponse(BaseModel):
    """Response after deleting a document."""

    success: bool
    filename: str
    chunks_deleted: int
    message: str


class DocumentInfo(BaseModel):
    """Document metadata."""

    filename: str
    size_bytes: int


class DocumentListResponse(BaseModel):
    """Response containing list of documents."""

    documents: list[DocumentInfo]
    total: int
