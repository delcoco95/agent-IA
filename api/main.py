"""
Application FastAPI pour l'agent IA BeneIT.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from config import ALLOWED_ORIGINS
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent IA BeneIT API",
    description="API pour le support informatique automatisé de BeneIT.",
    version="1.0.0"
)

# Configurer CORS avec une liste blanche
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"]
)

# Inclure le routeur API
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Agent IA BeneIT"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
