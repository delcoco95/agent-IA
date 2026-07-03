"""
Générateur de devis pour BeneIT.
Calcule le devis à partir de la fiche client et de la grille tarifaire.
"""
from models.schemas import FicheClient, Devis
from utils.helpers import valider_fiche_client
import json
import os


def charger_grille_tarifaire():
    """
    Charge la grille tarifaire depuis le fichier JSON.
    
    Returns :
        dict : Grille tarifaire complète (services + options).
    """
    current_dir = os.path.dirname(__file__)
    pricing_path = os.path.join(current_dir, "..", "data", "pricing_grid.json")
    with open(pricing_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generer_devis(fiche_client: FicheClient) -> Devis:
    """
    Génère un devis à partir de la fiche client et de la grille tarifaire.
    
    Args :
        fiche_client : Fiche client qualifiée et validée.
    
    Returns :
        Devis : Objet contenant le devis généré.
    
    Raises :
        ValueError : Si la fiche client est invalide.
    """
    # Valider la fiche client
    is_valid, errors = valider_fiche_client(fiche_client)
    if not is_valid:
        raise ValueError(f"Fiche client invalide : {errors}")

    grille = charger_grille_tarifaire()
    services = []
    total = 0

    # Logique de sélection des services (basée sur le type de demande et les symptômes)
    if fiche_client.type_demande == "problème":
        # Toujours ajouter un diagnostic pour les problèmes
        diagnostic = grille["services"]["diagnostic"]
        services.append({
            "nom": diagnostic["nom"],
            "prix": diagnostic["prix"],
            "duree_minutes": diagnostic.get("duree_minutes", 0),
            "duree_minutes_min": diagnostic.get("duree_minutes_min", 0),
            "duree_minutes_max": diagnostic.get("duree_minutes_max", 0),
        })
        total += diagnostic["prix"]

        # Ajouter un nettoyage si symptômes de lenteur/plantages
        if any(s in ["lenteur", "plantages", "ralentissements", "bugs"] for s in fiche_client.symptomes):
            nettoyage = grille["services"]["nettoyage_logiciel"]
            services.append({
                "nom": nettoyage["nom"],
                "prix": nettoyage["prix"],
                "duree_minutes": nettoyage.get("duree_minutes", 0),
                "duree_minutes_min": nettoyage.get("duree_minutes_min", 0),
                "duree_minutes_max": nettoyage.get("duree_minutes_max", 0),
            })
            total += nettoyage["prix"]

        # Ajouter un dépannage urgent si urgence = haute
        if fiche_client.urgence == "haute":
            depannage = grille["services"]["depannage_urgent"]
            services.append({
                "nom": depannage["nom"],
                "prix": depannage["prix"],
                "duree_minutes": depannage.get("duree_minutes", 0),
                "duree_minutes_min": depannage.get("duree_minutes_min", 0),
                "duree_minutes_max": depannage.get("duree_minutes_max", 0),
            })
            total += depannage["prix"]

    elif fiche_client.type_demande == "service":
        # Logique pour les demandes de service (ex: sauvegarde, installation)
        if "sauvegarde" in fiche_client.description_libre.lower() or any(
            s in ["sauvegarde", "backup"] for s in fiche_client.symptomes
        ):
            sauvegarde = grille["services"]["sauvegarde_automatique"]
            services.append({
                "nom": sauvegarde["nom"],
                "prix": sauvegarde["prix"],
                "duree_minutes": sauvegarde.get("duree_minutes", 0),
                "duree_minutes_min": sauvegarde.get("duree_minutes_min", 0),
                "duree_minutes_max": sauvegarde.get("duree_minutes_max", 0),
            })
            total += sauvegarde["prix"]

        if "installation" in fiche_client.description_libre.lower() or any(
            s in ["installer", "logiciel"] for s in fiche_client.symptomes
        ):
            installation = grille["services"]["installation_logiciel"]
            services.append({
                "nom": installation["nom"],
                "prix": installation["prix"],
                "duree_minutes": installation.get("duree_minutes", 0),
                "duree_minutes_min": installation.get("duree_minutes_min", 0),
                "duree_minutes_max": installation.get("duree_minutes_max", 0),
            })
            total += installation["prix"]

    # Ajouter les options (TOUJOURS en suggestions, jamais automatiquement)
    options = []
    for nom, option in grille["options"].items():
        options.append({
            "nom": option["nom"],
            "prix": option["prix"],
            "duree_minutes": option.get("duree_minutes", 0),
        })

    return Devis(
        client=fiche_client,
        services=services,
        options=options,
        total=total,
    )
