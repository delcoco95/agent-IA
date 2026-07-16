"""
Tests pour l'estimateur de devis.
"""
import pytest
from models.schemas import FicheClient
from agents.estimator import generer_devis


@pytest.fixture
def fiche_client_virus():
    """Fiche client pour un problème de virus."""
    return FicheClient(
        nom="Jean Dupont",
        email="jean@exemple.com",
        telephone="+33123456789",
        disponibilite="Lundi après-midi",
        type_demande="Dépannage",
        appareil="PC Windows 10",
        symptomes="Fichiers chiffrés, demande de rançon",
        urgence="haute",
        domaine="virus",
        details={
            "antivirus_installe": "Aucun",
            "fichiers_impactes": "Tous les documents",
            "lien_ou_telechargement_suspect": "Oui, email suspect"
        }
    )


@pytest.fixture
def fiche_client_optimisation():
    """Fiche client pour un problème d'optimisation."""
    return FicheClient(
        nom="Marie Martin",
        email="marie@exemple.com",
        telephone="+33198765432",
        disponibilite="Mardi matin",
        type_demande="Optimisation",
        appareil="PC Windows 11",
        symptomes="Lenteur générale",
        urgence="moyenne",
        domaine="optimisation",
        details={
            "duree_probleme": "2 semaines",
            "applications_concernees": "Toutes",
            "espace_disque_disponible": "10 Go",
            "ram_installee": "8 Go"
        }
    )


def test_generer_devis_virus(fiche_client_virus):
    """Test la génération d'un devis pour un problème de virus."""
    devis = generer_devis(fiche_client_virus)
    assert devis.client.domaine == "virus"
    assert len(devis.services) > 0
    assert devis.total > 0
    assert any(s.nom == "Diagnostic virus/malware" for s in devis.services)


def test_generer_devis_optimisation(fiche_client_optimisation):
    """Test la génération d'un devis pour un problème d'optimisation."""
    devis = generer_devis(fiche_client_optimisation)
    assert devis.client.domaine == "optimisation"
    assert len(devis.services) > 0
    assert devis.total > 0
    assert any(s.nom == "Diagnostic de performance" for s in devis.services)
