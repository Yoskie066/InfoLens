
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    ArticleSearchResult,
    SearchHistoryResponse,
)

from app.services.search_service import search_article_service

from app.services.search_history_service import (
    get_search_history,
    delete_search_history,
)


router = APIRouter()


# ==========================================
# SEARCH ARTICLES
# ==========================================

@router.post(
    "/",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)
def search_articles_endpoint(
    request_data: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        response = search_article_service(
            db=db,
            user_id=current_user.id,
            query=request_data.query,
            max_results=request_data.max_results,
        )

        articles = [
            ArticleSearchResult(
                title=item.get("title") or "Untitled",
                url=item["url"],
                content=item.get("content"),
                score=item.get("score"),
            )
            for item in response.get("results", [])
            if item.get("url")
        ]

        return SearchResponse(
            query=request_data.query,
            total_results=len(articles),
            results=articles,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Article search service is temporarily unavailable",
        )


# ==========================================
# GET SEARCH HISTORY
# ==========================================

@router.get(
    "/history",
    response_model=SearchHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_search_history_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        history = get_search_history(
            db=db,
            user_id=current_user.id,
        )

        return SearchHistoryResponse(
            total=len(history),
            history=history,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve search history",
        )


# ==========================================
# DELETE SEARCH HISTORY
# ==========================================

@router.delete(
    "/history/{history_id}",
    status_code=status.HTTP_200_OK,
)
def delete_search_history_endpoint(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_search_history(
            db=db,
            user_id=current_user.id,
            history_id=history_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Search history not found",
            )

        return {
            "message": "Search history deleted successfully",
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete search history",
        )
