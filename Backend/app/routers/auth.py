
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)

from app.schemas.user import UserResponse

from app.services.auth_service import (
    register_user,
    login_user,
    forgot_password,
    reset_password,
    verify_email,
)

from app.services.refresh_token_service import (
    refresh_access_token,
    revoke_refresh_token,
)


router = APIRouter()


# ==========================================
# USER REGISTRATION
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        new_user = register_user(db, user_data)
        return new_user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


# ==========================================
# USER LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    user_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        result = login_user(db, user_data)
        return result

    except ValueError as error:
        error_message = str(error)

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if error_message == "Account is inactive"
                else status.HTTP_401_UNAUTHORIZED
            ),
            detail=error_message,
        )


# ==========================================
# REFRESH ACCESS TOKEN
# ==========================================

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
def refresh_token_endpoint(
    request_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        result = refresh_access_token(
            db=db,
            raw_token=request_data.refresh_token,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )


# ==========================================
# USER LOGOUT
# ==========================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    request_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        revoke_refresh_token(
            db=db,
            raw_token=request_data.refresh_token,
        )

        return {
            "message": "Logged out successfully"
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process logout request",
        )


# ==========================================
# FORGOT PASSWORD
# ==========================================

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
def forgot_password_endpoint(
    request_data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        forgot_password(
            db,
            str(request_data.email),
        )

        return {
            "message": (
                "If an account exists with that email, "
                "a password reset link has been sent."
            )
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process password reset request",
        )


# ==========================================
# RESET PASSWORD
# ==========================================

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password_endpoint(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        reset_password(db, reset_data)

        return {
            "message": "Password has been reset successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ==========================================
# VERIFY EMAIL
# ==========================================

@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
)
def verify_email_endpoint(
    request_data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    try:
        user = verify_email(
            db,
            request_data.token,
        )

        return {
            "message": "Email verified successfully",
            "user": UserResponse.model_validate(user),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
