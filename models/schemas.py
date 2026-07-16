"""
Schéma des données pour l'agent IA BeneIT.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FicheClient(BaseModel):
    """Représente une fiche client extraite de la conversation."""
    nom: Optional[str] = Field(default=None, description="Nom du client")
    email: Optional[str] = Field(default=None, description="Email du client")
    telephone: Optional[str] = Field(default=None, description="Téléphone du client")
    disponibilite: Optional[str] = Field(default=None, description="Disponibilité du client")
    type_demande: Optional[str] = Field(default=None, description="Type de demande (ex: dépannage, installation)")
    appareil: Optional[str] = Field(default=None, description="Appareil concerné (ex: PC Windows 11, MacBook Pro)")
    symptomes: Optional[str] = Field(default=None, description="Symptômes décrits par le client")
    urgence: Optional[str] = Field(default=None, description="Niveau d'urgence (basse, moyenne, haute)")
    description_libre: Optional[str] = Field(default="", description="Description libre du problème")
    details: Dict[str, Any] = Field(default_factory=dict, description="Champs spécifiques au domaine")
    domaine: str = Field(default="diagnostic", description="Domaine de la demande (virus, optimisation, etc.)")


class Service(BaseModel):
    """Représente un service dans un devis."""
    nom: str
    description: str
    prix: float
    quantite: int = 1


class Devis(BaseModel):
    """Représente un devis généré pour un client."""
    client: FicheClient
    services: list[Service]
    options: list[Service] = Field(default_factory=list)
    total: float
