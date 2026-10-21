
from fastapi import FastAPI

app = FastAPI(title="InfoLens API")


@app.get("/")
def home():
    return {
        "message": "InfoLens API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
