from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for chat."""

    question: str = Field(..., min_length=1, description="The question to ask")
    max_sources: int = Field(default=10, ge=1, le=50, description="Max documents to search")


class Source(BaseModel):
    """A source document used to generate the answer."""

    filename: str
    chunk_index: int
    score: float
    text: str


class ChatResponse(BaseModel):
    """Response containing the answer and sources."""

    question: str
    answer: str
    sources: list[Source]
