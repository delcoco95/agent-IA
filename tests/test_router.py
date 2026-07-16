"""
Tests pour le routeur de domaines.
"""
import pytest
from agents.router import detecter_domaine


def test_detecter_domaine_virus():
    """Test la détection du domaine 'virus'."""
    message = "Mon PC a un virus, tous mes fichiers sont chiffrés !"
    assert detecter_domaine(message) == "virus"


def test_detecter_domaine_optimisation():
    """Test la détection du domaine 'optimisation'."""
    message = "Mon ordinateur est très lent, il met 10 minutes à démarrer."
    assert detecter_domaine(message) == "optimisation"


def test_detecter_domaine_sauvegarde():
    """Test la détection du domaine 'sauvegarde'."""
    message = "Je veux sauvegarder mes photos sur un disque dur externe."
    assert detecter_domaine(message) == "sauvegarde"


def test_detecter_domaine_microsoft365():
    """Test la détection du domaine 'microsoft365'."""
    message = "Je n'arrive pas à envoyer d'emails avec Outlook."
    assert detecter_domaine(message) == "microsoft365"


def test_detecter_domaine_reseau():
    """Test la détection du domaine 'reseau'."""
    message = "Ma connexion Wi-Fi est très instable, ça coupe tout le temps."
    assert detecter_domaine(message) == "reseau"


def test_detecter_domaine_diagnostic():
    """Test la détection du domaine 'diagnostic' (repli par défaut)."""
    message = "J'ai un problème avec mon ordinateur."
    assert detecter_domaine(message) == "diagnostic"
