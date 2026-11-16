
from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User


# Check if the authenticated user is an admin
def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user
