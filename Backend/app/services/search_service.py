
from sqlalchemy.orm import Session

from app.integrations.tavily_client import search_articles
from app.services.search_history_service import save_search_history


def search_article_service(
    db: Session,
    user_id: int,
    query: str,
    max_results: int = 10,
) -> dict:
    """
    Search for relevant articles using Tavily
    and save the user's search history.
    """

    results = search_articles(
        query=query,
        max_results=max_results,
    )

    save_search_history(
        db=db,
        user_id=user_id,
        query=query,
    )

    return results
