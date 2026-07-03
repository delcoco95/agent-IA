"""
Agent de qualification pour BeneIT.
Gère la conversation avec le client et l'extraction des données structurées.
"""
from utils.openrouter_client import call_openrouter
from models.schemas import FicheClient
import json


SYSTEM_PROMPT_CONVERSATION = """
Tu es un assistant technique pour BeneIT. Ton rôle est de poser des questions pour qualifier la demande du client.
Pose UNE question à la fois, et attends la réponse. Sois clair et concis.

Quand tu as assez d'informations pour remplir tous les champs suivants, ajoute le marqueur ###READY### 
SEUL SUR UNE LIGNE à la fin de ta dernière réponse (sans autre texte après) :

Champs à remplir :
- nom (str)
- email (str)
- telephone (str)
- disponibilite (str)
- type_demande (str: "problème" ou "service")
- appareil (str)
- symptomes (list[str])
- urgence (str: "basse", "moyenne", "haute")
- description_libre (str: message initial du client)
- details (dict: autres infos techniques)

Exemple de fin de conversation :
"Merci pour ces précisions. J'ai tout ce qu'il faut pour établir un devis.
###READY###"
"""

SYSTEM_PROMPT_EXTRACTION = """
Tu es un extracteur de données pour BeneIT. Analyse la conversation suivante et extrais UNIQUEMENT les informations
dans un JSON valide avec EXACTEMENT les champs suivants (ne pas ajouter d'autres champs) :

{
  "nom": str,
  "email": str,
  "telephone": str,
  "disponibilite": str,
  "type_demande": "problème" ou "service",
  "appareil": str,
  "symptomes": [str],
  "urgence": "basse" ou "moyenne" ou "haute",
  "description_libre": str,
  "details": {}
}

Règles :
- "description_libre" doit être le message initial brut du client (la première phrase qu'il a écrite).
- "symptomes" doit être une liste de chaînes de caractères.
- "details" peut être vide si aucune info supplémentaire.
- Ne pas inclure le marqueur ###READY### dans le JSON.
"""


def poser_question(conversation_history: list) -> str:
    """
    Pose une question au client dans le cadre de la conversation.
    
    Args :
        conversation_history : Historique des messages (liste de dicts {"role": ..., "content": ...}).
    
    Returns :
        str : Réponse de l'agent (peut contenir ###READY### si prêt pour l'extraction).
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT_CONVERSATION}]
    messages.extend(conversation_history)
    return call_openrouter(messages=messages, temperature=0.7)


def extraire_fiche_client(conversation_history: list) -> FicheClient:
    """
    Extrait une fiche client structurée depuis l'historique de conversation.
    Utilise le mode JSON forcé de l'API OpenRouter.
    
    Args :
        conversation_history : Historique des messages.
    
    Returns :
        FicheClient : Objet contenant les données structurées du client.
    
    Raises :
        ValueError : Si l'extraction JSON échoue.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT_EXTRACTION}]
    messages.extend(conversation_history)

    # Utilisation du mode JSON forcé
    response = call_openrouter(
        messages=messages,
        temperature=0.0,  # Déterministe pour l'extraction
        response_format={"type": "json_object"},
    )

    # Parsing du JSON
    try:
        data = json.loads(response)
        return FicheClient(**data)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Erreur lors de l'extraction JSON : {e}. "
            f"Réponse brute : {response}"
        )
