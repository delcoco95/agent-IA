"""
Stockage des sessions de conversation en mémoire.
TODO: Remplacer par Redis en production.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Stocke les sessions de conversation en mémoire.
    Chaque session contient :
    - conversation_history: liste des messages
    - domaine: domaine détecté (ex: "virus")
    - specialist: instance de l'agent spécialiste
    - pret_pour_devis: booléen indiquant si l'agent est prêt
    """

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str) -> None:
        """Crée une nouvelle session."""
        self.sessions[session_id] = {
            "conversation_history": [],
            "domaine": None,
            "specialist": None,
            "pret_pour_devis": False
        }
        logger.info(f"Session créée: {session_id}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session par son ID."""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """Met à jour une session."""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            logger.info(f"Session mise à jour: {session_id}")

    def delete_session(self, session_id: str) -> None:
        """Supprime une session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session supprimée: {session_id}")

    def set_pret_pour_devis(self, session_id: str, pret: bool) -> None:
        """Met à jour l'état pret_pour_devis d'une session."""
        if session_id in self.sessions:
            self.sessions[session_id]["pret_pour_devis"] = pret
