
from sqlalchemy.orm import Session

from app.integrations.trafilatura_client import extract_article

from app.services.article_service import save_article


def extract_article_service(
    db: Session,
    url: str,
) -> dict:
    """
    Extract article information and save it to the database.
    """

    article_data = extract_article(url=url)

    saved_article = save_article(
        db=db,
        article_data=article_data,
    )

    return {
        "id": saved_article.id,
        "url": saved_article.url,
        "title": saved_article.title,
        "author": saved_article.author,
        "date": (
            saved_article.published_at.isoformat()
            if saved_article.published_at
            else None
        ),
        "content": saved_article.content,
    }
