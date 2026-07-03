"""
Configuration centrale pour l'agent IA BeneIT.
Charge les variables d'environnement et expose les paramètres globaux.
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Clé API OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "La variable d'environnement OPENROUTER_API_KEY n'est pas définie. "
        "Veuillez créer un fichier .env avec votre clé API OpenRouter."
    )

# Nom du modèle à utiliser (par défaut : google/gemini-3.1-flash-lite)
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemini-3.1-flash-lite")

# Base URL de l'API OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
