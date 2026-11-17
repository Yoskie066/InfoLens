
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePasswordRequest

from app.services.password_history_service import (
    is_password_reused,
    archive_current_password,
)


def change_user_password(
    db: Session,
    current_user: User,
    password_data: ChangePasswordRequest,
) -> None:

    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise ValueError("Current password is incorrect")

    # Prevent reusing the current password
    if verify_password(
        password_data.new_password,
        current_user.hashed_password,
    ):
        raise ValueError(
            "New password must be different from current password"
        )

    # Prevent reusing previous passwords
    if is_password_reused(
        db=db,
        user_id=current_user.id,
        new_password=password_data.new_password,
    ):
        raise ValueError(
            "You cannot reuse a previously used password"
        )

    try:
        # Save current password to history before changing it
        archive_current_password(
            db=db,
            user_id=current_user.id,
            current_password_hash=current_user.hashed_password,
        )

        # Hash and update new password
        current_user.hashed_password = hash_password(
            password_data.new_password
        )

        # Save changes
        db.commit()
        db.refresh(current_user)

    except SQLAlchemyError:
        db.rollback()
        raise
