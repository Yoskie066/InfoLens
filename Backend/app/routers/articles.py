
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User

from app.schemas.article import (
    ArticleExtractionRequest,
    ArticleExtractionResponse,
)

from app.services.extraction_service import extract_article_service


router = APIRouter()


# ==========================================
# EXTRACT ARTICLE
# ==========================================

@router.post(
    "/extract",
    response_model=ArticleExtractionResponse,
    status_code=status.HTTP_200_OK,
)
def extract_article_endpoint(
    request_data: ArticleExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        article = extract_article_service(
            db=db,
            url=str(request_data.url),
        )

        return ArticleExtractionResponse(**article)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Article extraction service is temporarily unavailable",
        )
