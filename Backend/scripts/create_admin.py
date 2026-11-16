
from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def create_admin():
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    if len(password) < 8:
        print("Error: Password must be at least 8 characters.")
        return

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("Error: Email is already registered.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
            is_verified=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin account created successfully!")
        print(f"ID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
