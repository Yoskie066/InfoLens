
from pydantic import BaseModel, Field, HttpUrl


class ArticleExtractionRequest(BaseModel):
    url: HttpUrl = Field(
        description="HTTPS URL of the article to extract",
    )


class ArticleExtractionResponse(BaseModel):
    id: int
    url: str
    title: str | None = None
    author: str | None = None
    date: str | None = None
    content: str
