
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.password_history import PasswordHistory


# ==========================================
# SAVE PASSWORD TO HISTORY
# ==========================================

def save_password_history(
    db: Session,
    user_id: int,
    password_hash: str,
) -> None:

    history_record = PasswordHistory(
        user_id=user_id,
        hashed_password=password_hash,
    )

    db.add(history_record)


# ==========================================
# CHECK PASSWORD HISTORY
# ==========================================

def is_password_reused(
    db: Session,
    user_id: int,
    new_password: str,
) -> bool:

    password_records = db.scalars(
        select(PasswordHistory).where(
            PasswordHistory.user_id == user_id
        )
    ).all()

    for record in password_records:
        if verify_password(
            new_password,
            record.hashed_password,
        ):
            return True

    return False


# ==========================================
# CHECK CURRENT PASSWORD
# ==========================================

def is_current_password(
    new_password: str,
    current_password_hash: str,
) -> bool:

    return verify_password(
        new_password,
        current_password_hash,
    )


# ==========================================
# ADD CURRENT PASSWORD TO HISTORY
# ==========================================

def archive_current_password(
    db: Session,
    user_id: int,
    current_password_hash: str,
) -> None:

    save_password_history(
        db=db,
        user_id=user_id,
        password_hash=current_password_hash,
    )


# ==========================================
# CREATE PASSWORD HASH
# ==========================================

def create_password_hash(password: str) -> str:

    return hash_password(password)
