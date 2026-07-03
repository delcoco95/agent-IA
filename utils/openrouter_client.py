"""
Client pour l'API OpenRouter.
Permet d'appeler les modèles de langage via OpenRouter avec gestion d'erreur.
"""
import os
from openai import OpenAI, APIError, Timeout, RateLimitError
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
    Appelle l'API OpenRouter avec les messages donnés.
    
    Args :
        messages : Liste de messages au format {"role": "user"|"assistant"|"system", "content": str}.
        model : Nom du modèle à utiliser (par défaut : MODEL_NAME depuis config.py).
        temperature : Température pour la génération (0.0 à 1.0).
        response_format : Format de réponse souhaité (ex: {"type": "json_object"}).
    
    Returns :
        str : Réponse du modèle, ou message d'erreur si échec.
    """
    try:
        response = client.chat.completions.create(
            model=model or MODEL_NAME,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        return response.choices[0].message.content
    except Timeout:
        return "Erreur : Délai d'attente dépassé. Veuillez réessayer."
    except RateLimitError:
        return "Erreur : Trop de requêtes. Attendez quelques secondes."
    except APIError as e:
        return f"Erreur API OpenRouter : {str(e)}"
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"
