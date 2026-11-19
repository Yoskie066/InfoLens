
from tavily import TavilyClient

from app.core.config import settings


# Initialize Tavily client using API key from environment
tavily_client = TavilyClient(
    api_key=settings.TAVILY_API_KEY,
)


def search_articles(
    query: str,
    max_results: int = 10,
) -> dict:
    """
    Search for relevant articles using Tavily.
    """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        topic="general",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )

    return response
