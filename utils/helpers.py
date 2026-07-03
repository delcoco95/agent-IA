"""
Fonctions utilitaires pour l'agent IA BeneIT.
Inclut la validation, le formatage et la conversion des données.
"""
import re
from typing import Tuple
from models.schemas import FicheClient, Devis


def convertir_minutes_en_heures(minutes: int) -> str:
    """
    Convertit un nombre de minutes en format lisible (ex: 90 -> "1h30").
    
    Args :
        minutes : Nombre de minutes à convertir.
    
    Returns :
        str : Chaîne au format "Xh Ymin" ou "Xh" ou "Ymin".
    """
    heures = minutes // 60
    restes_minutes = minutes % 60
    if heures == 0:
        return f"{restes_minutes}min"
    elif restes_minutes == 0:
        return f"{heures}h"
    else:
        return f"{heures}h {restes_minutes}min"


def valider_fiche_client(fiche: FicheClient) -> Tuple[bool, str]:
    """
    Valide les champs critiques de la fiche client.
    
    Args :
        fiche : Objet FicheClient à valider.
    
    Returns :
        Tuple[bool, str] : (True, "") si valide, (False, "erreur1\nerreur2") sinon.
    """
    errors = []

    # Validation email (format basique)
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, fiche.email):
        errors.append(f"Email invalide : {fiche.email}")

    # Validation urgence
    urgences_valides = ["basse", "moyenne", "haute"]
    if fiche.urgence not in urgences_valides:
        errors.append(
            f"Urgence invalide : '{fiche.urgence}'. "
            f"Doit être dans {urgences_valides}"
        )

    # Validation type_demande
    types_valides = ["problème", "service"]
    if fiche.type_demande not in types_valides:
        errors.append(
            f"Type de demande invalide : '{fiche.type_demande}'. "
            f"Doit être dans {types_valides}"
        )

    # Validation nom (non vide)
    if not fiche.nom.strip():
        errors.append("Le nom du client ne peut pas être vide.")

    return (len(errors) == 0, "\n".join(errors))


def formater_rapport(fiche_client: FicheClient, devis: Devis) -> str:
    """
    Génère un rapport Markdown à partir de la fiche client et du devis.
    
    Args :
        fiche_client : Fiche client qualifiée.
        devis : Devis généré.
    
    Returns :
        str : Rapport au format Markdown.
    """
    # Formater les services
    lignes_services = []
    for service in devis.services:
        duree_min = service.get("duree_minutes_min", service.get("duree_minutes", 0))
        duree_max = service.get("duree_minutes_max", service.get("duree_minutes", 0))
        
        if duree_min == duree_max:
            duree_str = convertir_minutes_en_heures(duree_min)
        else:
            duree_str = f"{convertir_minutes_en_heures(duree_min)} - {convertir_minutes_en_heures(duree_max)}"
        
        lignes_services.append(
            f"| {service['nom']} | {service['prix']}€ | {duree_str} |"
        )

    # Formater les options
    lignes_options = []
    for option in devis.options:
        duree_str = convertir_minutes_en_heures(option.get("duree_minutes", 0))
        prix_str = f"{option['prix']}€" if option["prix"] > 0 else "Gratuit"
        lignes_options.append(
            f"| {option['nom']} | {prix_str} | {duree_str} |"
        )

    # Calculer la durée totale (min/max si variable)
    duree_totale_min = sum(
        s.get("duree_minutes_min", s.get("duree_minutes", 0)) 
        for s in devis.services
    )
    duree_totale_max = sum(
        s.get("duree_minutes_max", s.get("duree_minutes", 0)) 
        for s in devis.services
    )
    
    if duree_totale_min == duree_totale_max:
        duree_totale_str = convertir_minutes_en_heures(duree_totale_min)
    else:
        duree_totale_str = (
            f"{convertir_minutes_en_heures(duree_totale_min)} - "
            f"{convertir_minutes_en_heures(duree_totale_max)}"
        )

    # Construire le rapport Markdown
    return f"""# 📋 Rapport Client - BeneIT

## 👤 Informations Client
- **Nom** : {fiche_client.nom}
- **Email** : {fiche_client.email}
- **Téléphone** : {fiche_client.telephone}
- **Disponibilité** : {fiche_client.disponibilite}

## 🔍 Demande
- **Type** : {fiche_client.type_demande}
- **Appareil** : {fiche_client.appareil}
- **Symptômes** : {", ".join(fiche_client.symptomes)}
- **Urgence** : {fiche_client.urgence}
- **Description** : {fiche_client.description_libre}

## 💰 Devis
| Service               | Prix   | Durée estimée |
|-----------------------|--------|---------------|
{"\n".join(lignes_services)}
| **Total**             | **{devis.total}€** | **{duree_totale_str}** |

## ⚡ Options Supplémentaires (à valider avec le client)
| Option               | Prix   | Durée       |
|----------------------|--------|-------------|
{"\n".join(lignes_options)}

---
*Ce devis est valable 30 jours. Contactez-nous pour validation.*
"""
