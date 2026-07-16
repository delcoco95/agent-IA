"""
Génération de devis à partir d'une fiche client et d'une grille tarifaire.
"""
import json
from typing import Dict, List
from models.schemas import FicheClient, Devis, Service
from pathlib import Path

# Charger la grille tarifaire
PRICING_GRID_PATH = Path(__file__).parent.parent / "data" / "pricing_grid.json"


def charger_grille_tarifaire() -> Dict:
    """Charge la grille tarifaire depuis le fichier JSON."""
    with open(PRICING_GRID_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generer_devis(fiche_client: FicheClient) -> Devis:
    """
    Génère un devis à partir d'une fiche client.
    Utilise le champ `domaine` pour sélectionner les services appropriés.
    """
    grille = charger_grille_tarifaire()

    # Récupérer les services par défaut pour le domaine
    domaine = fiche_client.domaine
    services_par_defaut = grille.get("domaines", {}).get(domaine, {}).get("services", [])
    options_par_defaut = grille.get("domaines", {}).get(domaine, {}).get("options", [])

    # Convertir en objets Service
    services = [
        Service(
            nom=s["nom"],
            description=s["description"],
            prix=s["prix"],
            quantite=s.get("quantite", 1)
        )
        for s in services_par_defaut
    ]

    options = [
        Service(
            nom=o["nom"],
            description=o["description"],
            prix=o["prix"],
            quantite=o.get("quantite", 1)
        )
        for o in options_par_defaut
    ]

    # Calculer le total
    total = sum(s.prix * s.quantite for s in services) + sum(o.prix * o.quantite for o in options)

    return Devis(
        client=fiche_client,
        services=services,
        options=options,
        total=total
    )
