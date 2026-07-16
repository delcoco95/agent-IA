"""
Tests pour l'API FastAPI.
Utilise TestClient pour tester les endpoints sans lancer le serveur.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch, MagicMock
from api.session_store import SessionStore

# Créer un client de test
client = TestClient(app)


@pytest.fixture
def mock_session_store():
    """Mock du SessionStore pour les tests."""
    store = SessionStore()
    store.create_session("test-session-123")
    return store


def test_health_check():
    """Test l'endpoint /api/health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('api.routes.session_store')
def test_create_session(mock_session_store):
    """Test la création d'une session."""
    mock_session_store.return_value = SessionStore()
    response = client.post("/api/session")
    assert response.status_code == 200
    assert "session_id" in response.json()


@patch('api.routes.session_store')
@patch('api.routes.detecter_domaine')
@patch('api.routes.get_specialist')
def test_conversation_premier_message(mock_get_specialist, mock_detecter_domaine, mock_session_store):
    """Test la conversation avec le premier message (détection du domaine)."""
    # Configurer les mocks
    mock_detecter_domaine.return_value = "virus"
    mock_specialist = MagicMock()
    mock_specialist.poser_question.return_value = "Quel est votre nom ?"
    mock_specialist.champs_specifices = []
    mock_get_specialist.return_value = mock_specialist

    store = SessionStore()
    store.create_session("test-session-123")
    mock_session_store.return_value = store

    # Appeler l'endpoint
    response = client.post(
        "/api/conversation",
        json={"session_id": "test-session-123", "message": "Mon PC a un virus !"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["domaine"] == "virus"
    assert data["pret_pour_devis"] == False
    assert "response" in data


@patch('api.routes.session_store')
def test_conversation_session_inconnue():
    """Test la gestion d'une session inconnue."""
    response = client.post(
        "/api/conversation",
        json={"session_id": "session-inconnue", "message": "Test"}
    )
    assert response.status_code == 404
    assert "Session non trouvée" in response.json()["detail"]


@patch('api.routes.session_store')
@patch('api.routes.extraire_fiche_client')
@patch('api.routes.generer_devis')
def test_generer_devis(mock_generer_devis, mock_extraire_fiche_client, mock_session_store):
    """Test la génération d'un devis."""
    # Configurer les mocks
    store = SessionStore()
    store.create_session("test-session-123")
    store.sessions["test-session-123"]["pret_pour_devis"] = True
    store.sessions["test-session-123"]["domaine"] = "virus"
    store.sessions["test-session-123"]["specialist"] = MagicMock(champs_specifices=[])
    mock_session_store.return_value = store

    mock_fiche_client = MagicMock()
    mock_fiche_client.domaine = "virus"
    mock_extraire_fiche_client.return_value = mock_fiche_client

    mock_devis = MagicMock()
    mock_devis.services = []
    mock_devis.options = []
    mock_devis.total = 100.0
    mock_generer_devis.return_value = mock_devis

    # Appeler l'endpoint
    response = client.post(
        "/api/devis",
        json={"session_id": "test-session-123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "rapport_markdown" in data
    assert "fiche_client" in data
    assert "devis" in data


def test_generer_devis_session_non_pret():
    """Test la génération d'un devis quand l'agent n'est pas prêt."""
    # Créer une session qui n'est pas prête
    store = SessionStore()
    store.create_session("test-session-123")
    store.sessions["test-session-123"]["pret_pour_devis"] = False

    with patch('api.routes.session_store', return_value=store):
        response = client.post(
            "/api/devis",
            json={"session_id": "test-session-123"}
        )
        assert response.status_code == 400
        assert "pas encore prêt" in response.json()["detail"]
