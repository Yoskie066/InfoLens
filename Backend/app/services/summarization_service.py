
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.summary import Summary

from app.integrations.gemini_client import (
    generate_article_summary,
    generate_article_key_points,
)


def generate_summary_service(
    db: Session,
    user_id: int,
    article_id: int,
) -> Summary:
    """
    Generate an article summary and key points using Gemini AI
    and save both to the database.
    """

    article = (
        db.query(Article)
        .filter(Article.id == article_id)
        .first()
    )

    if not article:
        raise ValueError("Article not found")

    if not article.content:
        raise ValueError("Article content is not available")

    summary_text = generate_article_summary(
        content=article.content,
    )

    key_points = generate_article_key_points(
        content=article.content,
    )

    summary = Summary(
        user_id=user_id,
        article_id=article.id,
        summary_text=summary_text,
        key_points=key_points,
    )

    try:
        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    except Exception:
        db.rollback()
        raise
