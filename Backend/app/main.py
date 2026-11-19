
from fastapi import FastAPI, Depends

from app.routers import auth, user, search, articles
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin
from app.models.user import User


app = FastAPI(
    title="InfoLens API",
    description="Backend API for the InfoLens application",
    version="1.0.0",
)


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
)


# ==========================================
# USER ROUTES
# ==========================================

app.include_router(
    user.router,
    prefix="/api/users",
    tags=["Users"],
)


# ==========================================
# ARTICLE SEARCH ROUTES
# ==========================================

app.include_router(
    search.router,
    prefix="/api/search",
    tags=["Article Search"],
)


# ==========================================
# ARTICLE EXTRACTION ROUTES
# ==========================================

app.include_router(
    articles.router,
    prefix="/api/articles",
    tags=["Articles"],
)


# ==========================================
# ROOT AND HEALTH CHECK
# ==========================================

@app.get("/")
def root():
    return {
        "message": "Welcome to InfoLens API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


# ==========================================
# CURRENT USER INFORMATION
# ==========================================

@app.get("/api/auth/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
    }


# ==========================================
# ADMIN TEST ENDPOINT
# ==========================================

@app.get("/api/admin/test")
def admin_test(
    current_admin: User = Depends(require_admin),
):
    return {
        "message": "Welcome, Admin!",
        "admin_email": current_admin.email,
        "role": current_admin.role,
    }
