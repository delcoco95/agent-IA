"""
Classe de base pour les agents spécialisés.
Chaque spécialiste doit définir :
- system_prompt : le prompt système spécifique à son domaine
- champs_specifices : liste des champs à extraire en plus des champs communs
"""
from typing import List, Dict
from agents.extractor import poser_question


class SpecialistAgent:
    """
    Classe abstraite pour un agent spécialisé dans un domaine.
    """
    system_prompt: str = ""
    champs_specifices: List[str] = []
    domaine: str = "diagnostic"  # À redéfinir dans chaque sous-classe

    def poser_question(self, conversation: List[Dict[str, str]]) -> str:
        """
        Pose une question au client en utilisant le prompt système du spécialiste.
        """
        return poser_question(conversation, self.system_prompt)
