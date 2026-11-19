
from sqlalchemy.orm import Session

from app.models.search_history import SearchHistory
from app.models.user import User


def save_search_history(
    db: Session,
    user_id: int,
    query: str,
) -> SearchHistory:
    """
    Save a user's search query to the database.
    """

    search_history = SearchHistory(
        user_id=user_id,
        query=query,
    )

    try:
        db.add(search_history)
        db.commit()
        db.refresh(search_history)

        return search_history

    except Exception:
        db.rollback()
        raise


def get_search_history(
    db: Session,
    user_id: int,
) -> list[SearchHistory]:
    """
    Retrieve a user's search history, newest first.
    """

    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.created_at.desc())
        .all()
    )


def delete_search_history(
    db: Session,
    user_id: int,
    history_id: int,
) -> bool:
    """
    Delete a specific search history owned by the user.
    """

    search_history = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.id == history_id,
            SearchHistory.user_id == user_id,
        )
        .first()
    )

    if search_history is None:
        return False

    try:
        db.delete(search_history)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

