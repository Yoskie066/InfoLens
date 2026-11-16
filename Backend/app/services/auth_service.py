
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.models.email_verification import EmailVerificationToken

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ResetPasswordRequest,
)

from app.utils.token_generator import (
    generate_reset_token,
    hash_reset_token,
    generate_verification_token,
    hash_verification_token,
)

from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
)


# ==========================================
# USER REGISTRATION
# ==========================================

def register_user(db: Session, user_data: RegisterRequest) -> User:

    # Check if email already exists
    existing_user = db.scalar(
        select(User).where(User.email == str(user_data.email))
    )

    if existing_user:
        raise ValueError("Email is already registered")

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=str(user_data.email),
        hashed_password=hashed_password,
        role="user",
    )

    try:
        db.add(new_user)
        db.flush()

        # Generate email verification token
        raw_token = generate_verification_token()
        hashed_token = hash_verification_token(raw_token)

        verification_record = EmailVerificationToken(
            user_id=new_user.id,
            token=hashed_token,
            expires_at=(
                datetime.now(timezone.utc) + timedelta(minutes=30)
            ),
        )

        db.add(verification_record)

        # Save user and verification token
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise ValueError("Email is already registered")

    except SQLAlchemyError:
        db.rollback()
        raise

    # Send verification email
    try:
        send_verification_email(
            recipient=new_user.email,
            verification_token=raw_token,
        )

    except Exception:
        # Invalidate token if email delivery fails
        verification_record.is_used = True

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()

        raise

    return new_user


# ==========================================
# USER LOGIN
# ==========================================

def login_user(db: Session, user_data: LoginRequest) -> dict:

    # Find user by email
    user = db.scalar(
        select(User).where(User.email == str(user_data.email))
    )

    # Check credentials
    if not user or not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise ValueError("Invalid email or password")

    # Check account status
    if not user.is_active:
        raise ValueError("Account is inactive")

    # Generate JWT access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# ==========================================
# FORGOT PASSWORD
# ==========================================

def forgot_password(db: Session, email: str) -> None:

    # Find user by email
    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Do not reveal whether the email exists
    if not user or not user.is_active:
        return

    # Invalidate previous unused reset tokens
    previous_tokens = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used.is_(False),
        )
    ).all()

    for previous_token in previous_tokens:
        previous_token.is_used = True

    # Generate a new secure reset token
    raw_token = generate_reset_token()

    # Store only the hashed token
    hashed_token = hash_reset_token(raw_token)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=hashed_token,
        expires_at=(
            datetime.now(timezone.utc) + timedelta(minutes=15)
        ),
    )

    try:
        db.add(reset_token)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    # Send the raw token through email
    try:
        send_password_reset_email(
            recipient=user.email,
            reset_token=raw_token,
        )

    except Exception:
        # Invalidate the token if email delivery fails
        reset_token.is_used = True

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()

        raise


# ==========================================
# RESET PASSWORD
# ==========================================

def reset_password(
    db: Session,
    reset_data: ResetPasswordRequest,
) -> None:

    # Hash the submitted reset token
    hashed_token = hash_reset_token(reset_data.token)

    # Find an unused reset token
    reset_record = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token == hashed_token,
            PasswordResetToken.is_used.is_(False),
        )
    )

    # Validate token
    if not reset_record:
        raise ValueError("Invalid or expired reset token")

    # Check token expiration
    current_time = datetime.now(timezone.utc)

    if reset_record.expires_at <= current_time:
        reset_record.is_used = True
        db.commit()
        raise ValueError("Invalid or expired reset token")

    # Find associated user
    user = db.get(User, reset_record.user_id)

    if not user or not user.is_active:
        raise ValueError("Invalid or expired reset token")

    # Prevent reusing the current password
    if verify_password(
        reset_data.new_password,
        user.hashed_password,
    ):
        raise ValueError(
            "New password must be different from current password"
        )

    try:
        # Update password
        user.hashed_password = hash_password(
            reset_data.new_password
        )

        # Mark current token as used
        reset_record.is_used = True

        # Invalidate other unused reset tokens
        other_tokens = db.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.is_used.is_(False),
            )
        ).all()

        for token_record in other_tokens:
            token_record.is_used = True

        db.commit()
        db.refresh(user)

    except SQLAlchemyError:
        db.rollback()
        raise


# ==========================================
# EMAIL VERIFICATION
# ==========================================

def verify_email(db: Session, token: str) -> User:

    # Hash the submitted verification token
    hashed_token = hash_verification_token(token)

    # Find an unused verification token
    verification_record = db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == hashed_token,
            EmailVerificationToken.is_used.is_(False),
        )
    )

    # Validate token
    if not verification_record:
        raise ValueError("Invalid or expired verification token")

    # Check token expiration
    current_time = datetime.now(timezone.utc)

    if verification_record.expires_at <= current_time:
        verification_record.is_used = True
        db.commit()
        raise ValueError("Invalid or expired verification token")

    # Find associated user
    user = db.get(User, verification_record.user_id)

    if not user or not user.is_active:
        raise ValueError("Invalid or expired verification token")

    try:
        # Mark email as verified
        user.is_verified = True

        # Mark verification token as used
        verification_record.is_used = True

        # Invalidate other unused verification tokens
        other_tokens = db.scalars(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.is_used.is_(False),
            )
        ).all()

        for token_record in other_tokens:
            token_record.is_used = True

        db.commit()
        db.refresh(user)

    except SQLAlchemyError:
        db.rollback()
        raise

    return user
