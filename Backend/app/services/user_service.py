
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePasswordRequest


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

    # Hash new password
    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    # Save updated password
    db.commit()
    db.refresh(current_user)
