"""
Routeur pour classer les demandes clients dans un domaine spécifique.
Utilise OpenRouter pour analyser le premier message et retourner le domaine.
"""
from utils.openrouter_client import call_openrouter
from typing import Literal

# Domaines possibles
DOMAINES = [
    "virus", "optimisation", "sauvegarde",
    "microsoft365", "reseau", "diagnostic"
]


def detecter_domaine(premier_message: str) -> str:
    """
    Détecte le domaine de la demande à partir du premier message du client.
    Retourne l'un des domaines dans DOMAINES, ou "diagnostic" par défaut.
    """
    prompt = f"""
    Classe le message suivant dans UNE SEULE des catégories suivantes : {DOMAINES}.
    Retourne UNIQUEMENT le nom de la catégorie en minuscules, sans explication ni justificatif.
    Si le message est ambigu ou ne correspond à aucune catégorie, retourne "diagnostic".

    Message du client :
    "{premier_message}"
    """

    try:
        response = call_openrouter(
            messages=[{"role": "user", "content": prompt}],
            model="google/gemini-3.1-flash-lite",
            temperature=0.0,  # Réponse déterministe
            max_tokens=10
        )
        domaine = response.strip().lower()

        # Valider que le domaine est dans la liste
        if domaine in DOMAINES:
            return domaine
        else:
            return "diagnostic"
    except Exception as e:
        print(f"⚠️ Erreur lors de la détection du domaine: {e}")
        return "diagnostic"
