"""
Extraction des données client à partir d'une conversation.
Contient la logique commune pour extraire les champs (communs + spécifiques).
"""
from typing import List, Dict, Any
from models.schemas import FicheClient
from utils.openrouter_client import call_openrouter
import json
import logging

logger = logging.getLogger(__name__)

# Champs communs à tous les domaines
CHAMPS_COMMUNS = [
    "nom", "email", "telephone", "disponibilite",
    "type_demande", "appareil", "symptomes", "urgence"
]


def extraire_champs(conversation: List[Dict[str, str]], champs: List[str]) -> Dict[str, Any]:
    """
    Extrait les champs spécifiés depuis l'historique de conversation.
    Utilise OpenRouter pour analyser la conversation et retourner un JSON avec les champs demandés.
    """
    prompt = f"""
    Analyse la conversation suivante et extrais UNIQUEMENT les informations demandées.
    Retourne UNIQUEMENT un objet JSON avec les clés suivantes : {champs}.
    Si une information est manquante, utilise null pour sa valeur.
    Ne pose PAS de question, ne fais PAS de commentaire, retourne UNIQUEMENT le JSON.

    Conversation :
    {json.dumps(conversation, ensure_ascii=False)}
    """

    try:
        response = call_openrouter(
            messages=[{"role": "user", "content": prompt}],
            model="google/gemini-3.1-flash-lite",  # Modèle léger pour l'extraction
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(response)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des champs: {e}")
        return {champ: None for champ in champs}


def extraire_fiche_client(conversation: List[Dict[str, str]], champs_specifices: List[str] = None) -> FicheClient:
    """
    Extrait une FicheClient depuis l'historique de conversation.
    Combine les champs communs et les champs spécifiques au domaine.
    """
    champs = CHAMPS_COMMUNS.copy()
    if champs_specifices:
        champs.extend(champs_specifices)

    data = extraire_champs(conversation, champs)

    # Remplir les champs obligatoires (même si None)
    fiche_data = {
        "nom": data.get("nom"),
        "email": data.get("email"),
        "telephone": data.get("telephone"),
        "disponibilite": data.get("disponibilite"),
        "type_demande": data.get("type_demande"),
        "appareil": data.get("appareil"),
        "symptomes": data.get("symptomes"),
        "urgence": data.get("urgence"),
        "description_libre": data.get("description_libre", ""),
        "details": data.get("details", {}),
        "domaine": data.get("domaine", "diagnostic")  # Par défaut
    }

    # Ajouter les champs spécifiques
    if champs_specifices:
        for champ in champs_specifices:
            fiche_data["details"][champ] = data.get(champ)

    return FicheClient(**fiche_data)


def poser_question(conversation: List[Dict[str, str]], system_prompt: str) -> str:
    """
    Pose une question au client en utilisant le prompt système fourni.
    Retourne la réponse de l'agent, avec ###READY### si toutes les infos sont collectées.
    """
    messages = [{"role": "system", "content": system_prompt}] + conversation
    response = call_openrouter(
        messages=messages,
        model="google/gemini-3.1-flash-lite",
        temperature=0.3
    )
    return response
