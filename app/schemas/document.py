from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):

    success: bool
    filename: str
    chunks_created: int
    message: str


class DocumentDeleteResponse(BaseModel):

    success: bool
    filename: str
    chunks_deleted: int
    message: str


class DocumentInfo(BaseModel):

    filename: str
    size_bytes: int


class DocumentListResponse(BaseModel):

    documents: list[DocumentInfo]
    total: int
