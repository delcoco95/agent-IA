"""
Package des agents spécialisés.
"""
from agents.specialists.virus import VirusAgent
from agents.specialists.optimisation import OptimisationAgent
from agents.specialists.sauvegarde import SauvegardeAgent
from agents.specialists.microsoft365 import Microsoft365Agent
from agents.specialists.reseau import ReseauAgent
from agents.specialists.diagnostic import DiagnosticAgent

# Dictionnaire pour récupérer un spécialiste par domaine
SPECIALISTS = {
    "virus": VirusAgent(),
    "optimisation": OptimisationAgent(),
    "sauvegarde": SauvegardeAgent(),
    "microsoft365": Microsoft365Agent(),
    "reseau": ReseauAgent(),
    "diagnostic": DiagnosticAgent()
}

def get_specialist(domaine: str):
    """
    Retourne l'agent spécialiste correspondant au domaine.
    Si le domaine est inconnu, retourne l'agent diagnostic.
    """
    return SPECIALISTS.get(domaine, SPECIALISTS["diagnostic"])
