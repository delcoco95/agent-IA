"""
Schéma des données pour l'agent IA BeneIT.
Définit les structures de données principales : FicheClient et Devis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FicheClient:
    """
    Représente une fiche client qualifiée.
    
    Attributs :
        nom (str) : Nom complet du client.
        email (str) : Adresse email du client.
        telephone (str) : Numéro de téléphone du client.
        disponibilite (str) : Disponibilités du client (ex: "lundi 14h-16h").
        type_demande (str) : Type de demande, soit "problème" soit "service".
        appareil (str) : Type d'appareil concerné (ex: "PC Windows", "MacBook Pro").
        symptomes (List[str]) : Liste des symptômes ou besoins (ex: ["lenteur", "plantages"]).
        urgence (str) : Niveau d'urgence, doit être dans ["basse", "moyenne", "haute"].
        description_libre (str) : Message initial brut du client.
        details (Dict[str, str]) : Autres informations techniques (ex: {"os": "Windows 11"}).
    """
    nom: str
    email: str
    telephone: str
    disponibilite: str
    type_demande: str  # "problème" ou "service"
    appareil: str
    symptomes: List[str]
    urgence: str  # "basse", "moyenne", "haute"
    description_libre: str
    details: Dict[str, str] = field(default_factory=dict)


@dataclass
class Devis:
    """
    Représente un devis généré pour un client.
    
    Attributs :
        client (FicheClient) : Fiche client associée au devis.
        services (List[Dict]) : Liste des services inclus dans le devis.
        options (List[Dict]) : Liste des options suggérées (non incluses par défaut).
        total (float) : Montant total du devis (en euros).
    """
    client: FicheClient
    services: List[Dict]
    options: List[Dict]
    total: float
