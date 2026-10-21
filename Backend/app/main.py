
from fastapi import FastAPI

app = FastAPI(
    title="InfoLens API",
    description="Backend API for the InfoLens application",
    version="1.0.0",
)


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

