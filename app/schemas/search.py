from pydantic import BaseModel, Field


class SearchRequest(BaseModel):

    query: str = Field(..., min_length=1, description="The search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):

    text: str
    filename: str
    chunk_index: int
    score: float


class SearchResponse(BaseModel):

    query: str
    results: list[SearchResult]
    total: int
