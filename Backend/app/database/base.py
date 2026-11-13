from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy can register their tables
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.models.email_verification import EmailVerificationToken
from app.models.search_history import SearchHistory
from app.models.article import Article
from app.models.summary import Summary
from app.models.saved_article import SavedArticle
from app.models.activity_log import ActivityLog