"""
Routes de l'API FastAPI pour l'agent IA BeneIT.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from pydantic import BaseModel
from agents.router import detecter_domaine
from agents.specialists import get_specialist
from agents.extractor import extraire_fiche_client
from agents.estimator import generer_devis
from utils.helpers import formater_rapport
from api.session_store import SessionStore
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# Store des sessions (en mémoire)
session_store = SessionStore()


class Message(BaseModel):
    """Modèle pour un message dans la conversation."""
    role: str  # "user" ou "assistant"
    content: str


class ConversationRequest(BaseModel):
    """Modèle pour une requête de conversation."""
    session_id: str
    message: str


class SessionResponse(BaseModel):
    """Modèle pour la réponse de création de session."""
    session_id: str


class ConversationResponse(BaseModel):
    """Modèle pour la réponse de conversation."""
    response: str
    pret_pour_devis: bool
    domaine: str


class DevisResponse(BaseModel):
    """Modèle pour la réponse de devis."""
    rapport_markdown: str
    fiche_client: Dict
    devis: Dict


@router.post("/session", response_model=SessionResponse)
async def create_session():
    """
    Crée une nouvelle session de conversation.
    Retourne un session_id unique.
    """
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)
    logger.info(f"Nouvelle session créée: {session_id}")
    return {"session_id": session_id}


@router.post("/conversation", response_model=ConversationResponse)
async def conversation(request: ConversationRequest):
    """
    Traite un message dans une conversation existante.
    - Au premier message, détecte le domaine et initialise l'agent spécialiste.
    - Pour les messages suivants, utilise l'agent spécialiste de la session.
    """
    session_id = request.session_id
    message = request.message

    # Vérifier que la session existe
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Ajouter le message à l'historique
    session["conversation_history"].append({"role": "user", "content": message})

    # Si c'est le premier message, détecter le domaine
    if len(session["conversation_history"]) == 1:
        premier_message = message
        domaine = detecter_domaine(premier_message)
        session["domaine"] = domaine
        session["specialist"] = get_specialist(domaine)
        logger.info(f"Domaine détecté pour la session {session_id}: {domaine}")

    # Récupérer l'agent spécialiste
    specialist = session["specialist"]

    # Poser une question avec l'agent
    reponse_agent = specialist.poser_question(session["conversation_history"])

    # Vérifier si l'agent est prêt pour le devis
    pret_pour_devis = "###READY###" in reponse_agent
    reponse_nettoyee = reponse_agent.replace("###READY###", "").strip()

    # Ajouter la réponse de l'agent à l'historique
    session["conversation_history"].append({"role": "assistant", "content": reponse_nettoyee})
    session["pret_pour_devis"] = pret_pour_devis

    logger.info(f"Réponse de l'agent [{session['domaine']}]: {reponse_nettoyee}")

    return {
        "response": reponse_nettoyee,
        "pret_pour_devis": pret_pour_devis,
        "domaine": session["domaine"]
    }


@router.post("/devis", response_model=DevisResponse)
async def generer_devis_api(request: ConversationRequest):
    """
    Génère un devis à partir de l'historique de conversation d'une session.
    """
    session_id = request.session_id

    # Vérifier que la session existe
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Vérifier que l'agent est prêt pour le devis
    if not session.get("pret_pour_devis", False):
        raise HTTPException(
            status_code=400,
            detail="L'agent n'est pas encore prêt pour générer un devis. Continuez la conversation."
        )

    # Extraire la fiche client
    try:
        fiche_client = extraire_fiche_client(
            session["conversation_history"],
            champs_specifices=session["specialist"].champs_specifices
        )
        fiche_client.domaine = session["domaine"]
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de la fiche client: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur d'extraction: {str(e)}")

    # Générer le devis
    try:
        devis = generer_devis(fiche_client)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du devis: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de génération: {str(e)}")

    # Formater le rapport
    rapport = formater_rapport(fiche_client, devis)

    # Convertir en dict pour la réponse JSON
    fiche_client_dict = fiche_client.model_dump()
    devis_dict = {
        "client": fiche_client_dict,
        "services": [s.model_dump() for s in devis.services],
        "options": [o.model_dump() for o in devis.options],
        "total": devis.total
    }

    return {
        "rapport_markdown": rapport,
        "fiche_client": fiche_client_dict,
        "devis": devis_dict
    }


@router.get("/health")
async def health_check():
    """
    Endpoint de vérification de santé.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "agent-IA BeneIT API"
    }
