"""
Client pour l'API OpenRouter.
Permet d'appeler les modèles de langage via OpenRouter avec gestion d'erreur.
"""
import os
from openai import OpenAI
from typing import List, Dict, Optional, Union
from config import OPENROUTER_API_KEY, MODEL_NAME, OPENROUTER_BASE_URL

# Initialiser le client OpenRouter
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def call_openrouter(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    response_format: Optional[Dict] = None,
) -> str:
    """
    Appelle l'API OpenRouter avec les messages donnes.
    
    Args :
        messages : Liste de messages au format {"role": "user"|"assistant"|"system", "content": str}.
        model : Nom du modele a utiliser (par defaut : MODEL_NAME depuis config.py).
        temperature : Temperature pour la generation (0.0 a 1.0).
        response_format : Format de reponse souhaite (ex: {"type": "json_object"}).
    
    Returns :
        str : Reponse du modele, ou message d'erreur si echec.
    """
    try:
        response = client.chat.completions.create(
            model=model or MODEL_NAME,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "timeout" in error_str.lower() or "TimeOut" in error_str:
            return "Erreur : Delai d'attente depasse. Veuillez reessayer."
        elif "rate limit" in error_str.lower() or "429" in error_str:
            return "Erreur : Trop de requetes. Attendez quelques secondes."
        elif "401" in error_str or "Authentication" in error_str:
            return "Erreur : Cle API OpenRouter invalide ou manquante."
        elif "404" in error_str:
            return "Erreur : Modele non trouve. Verifiez MODEL_NAME."
        else:
            return f"Erreur API OpenRouter : {error_str}"
