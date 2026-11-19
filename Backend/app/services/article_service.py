
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.article import Article


def get_article_by_url(
    db: Session,
    url: str,
) -> Article | None:
    """
    Retrieve an article using its URL.
    """

    return (
        db.query(Article)
        .filter(Article.url == url)
        .first()
    )


def save_article(
    db: Session,
    article_data: dict,
) -> Article:
    """
    Save an extracted article.
    Avoid duplicate article URLs.
    """

    url = article_data["url"]

    existing_article = get_article_by_url(
        db=db,
        url=url,
    )

    if existing_article:
        return existing_article

    published_at = None
    date_value = article_data.get("date")

    if date_value:
        try:
            published_at = datetime.fromisoformat(
                date_value.replace("Z", "+00:00")
            )

            if published_at.tzinfo is None:
                published_at = published_at.replace(
                    tzinfo=timezone.utc,
                )

        except ValueError:
            published_at = None

    source = urlparse(url).hostname

    article = Article(
        title=article_data.get("title") or "Untitled",
        url=url,
        source=source,
        author=article_data.get("author"),
        content=article_data.get("content"),
        published_at=published_at,
    )

    try:
        db.add(article)
        db.commit()
        db.refresh(article)

        return article

    except Exception:
        db.rollback()
        raise


def get_article_by_id(
    db: Session,
    article_id: int,
) -> Article | None:
    """
    Retrieve an article using its ID.
    """

    return (
        db.query(Article)
        .filter(Article.id == article_id)
        .first()
    )
