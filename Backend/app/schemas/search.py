
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=200,
        description="Search keyword or topic",
    )

    max_results: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum number of articles to return",
    )


class ArticleSearchResult(BaseModel):
    title: str
    url: str
    content: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[ArticleSearchResult]


# ==========================================
# SEARCH HISTORY
# ==========================================

class SearchHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    created_at: datetime


class SearchHistoryResponse(BaseModel):
    total: int
    history: list[SearchHistoryItem]

