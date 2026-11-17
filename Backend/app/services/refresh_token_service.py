
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.utils.token_generator import (
    generate_refresh_token,
    hash_refresh_token,
)


def create_refresh_token(db: Session, user: User) -> str:
    """Generate and store a hashed refresh token."""

    raw_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_token)

    refresh_token = RefreshToken(
        user_id=user.id,
        token=token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ),
    )

    try:
        db.add(refresh_token)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return raw_token


def refresh_access_token(db: Session, raw_token: str) -> dict:
    """Validate and rotate a refresh token atomically."""

    token_hash = hash_refresh_token(raw_token)
    now = datetime.now(timezone.utc)

    try:
        # Lock the token row to prevent simultaneous token rotation.
        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
            .with_for_update()
        )

        stored_token = db.scalar(statement)

        if stored_token is None:
            raise ValueError("Invalid refresh token")

        expires_at = stored_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= now:
            stored_token.is_revoked = True
            db.commit()
            raise ValueError("Refresh token has expired")

        user = db.get(User, stored_token.user_id)

        if user is None or not user.is_active:
            stored_token.is_revoked = True
            db.commit()
            raise ValueError("User account is unavailable")

        # Generate the replacement refresh token.
        new_refresh_token = generate_refresh_token()

        new_token_record = RefreshToken(
            user_id=user.id,
            token=hash_refresh_token(new_refresh_token),
            expires_at=(
                now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            ),
        )

        # Revoke the old token and save its replacement together.
        stored_token.is_revoked = True
        db.add(new_token_record)

        # Generate a new access token.
        new_access_token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
            }
        )

        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except SQLAlchemyError:
        db.rollback()
        raise


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    """Revoke a refresh token during logout."""

    token_hash = hash_refresh_token(raw_token)

    try:
        statement = select(RefreshToken).where(
            RefreshToken.token == token_hash,
            RefreshToken.is_revoked.is_(False),
        )

        stored_token = db.scalar(statement)

        if stored_token is not None:
            stored_token.is_revoked = True
            db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise
