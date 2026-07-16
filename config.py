"""
Configuration centrale pour l'application.
"""
import os
from typing import List

# Clé API OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# URL de base pour OpenRouter (optionnelle, par défaut celle d'OpenRouter)
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Modèle par défaut pour les appels OpenRouter
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemini-3.1-flash-lite")

# Origines autorisées pour CORS (séparées par des virgules)
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "https://delcoco95.github.io,http://localhost:8000")
ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]

# Validation
if not OPENROUTER_API_KEY:
    raise ValueError("La variable d'environnement OPENROUTER_API_KEY est requise.")
