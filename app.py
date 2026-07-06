"""
Application Flask pour exposer l'agent IA BeneIT via une API REST.
Compatibilité WSGI pour déploiement sur o2switch avec Phusion Passenger.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.qualifier import poser_question, extraire_fiche_client
from agents.estimator import generer_devis
from utils.helpers import formater_rapport
import json
import logging

# Initialiser l'application Flask
app = Flask(__name__)

# Activer CORS pour permettre les requêtes depuis d'autres sous-domaines
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/api/conversation', methods=['POST'])
def conversation():
    """
    Endpoint pour continuer une conversation avec l'agent.
    
    Reçoit l'historique de conversation et retourne la réponse de l'agent.
    
    Request JSON:
    {
        "conversation_history": [
            {"role": "user", "content": "message du client"},
            {"role": "assistant", "content": "réponse de l'agent"}
        ]
    }
    
    Response JSON:
    {
        "response": "réponse de l'agent (sans ###READY###)",
        "pret_pour_devis": true/false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'conversation_history' not in data:
            return jsonify({
                "error": "Le champ 'conversation_history' est requis.",
                "pret_pour_devis": False
            }), 400
        
        conversation_history = data['conversation_history']
        
        # Valider le format de l'historique
        if not isinstance(conversation_history, list):
            return jsonify({
                "error": "conversation_history doit être une liste.",
                "pret_pour_devis": False
            }), 400
        
        # Appeler l'agent pour poser une question
        reponse_agent = poser_question(conversation_history)
        
        # Vérifier si l'agent est prêt pour le devis
        pret_pour_devis = "###READY###" in reponse_agent
        
        # Nettoyer la réponse (retirer le marqueur ###READY###)
        reponse_nettoyee = reponse_agent.replace("###READY###", "").strip()
        
        logger.info(f"Conversation: pret_pour_devis={pret_pour_devis}")
        
        return jsonify({
            "response": reponse_nettoyee,
            "pret_pour_devis": pret_pour_devis
        })
        
    except Exception as e:
        logger.error(f"Erreur dans /api/conversation: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Erreur interne: {str(e)}",
            "pret_pour_devis": False
        }), 500


@app.route('/api/devis', methods=['POST'])
def generer_devis_api():
    """
    Endpoint pour générer un devis à partir de l'historique complet.
    
    Reçoit l'historique de conversation et retourne le rapport Markdown final.
    
    Request JSON:
    {
        "conversation_history": [
            {"role": "user", "content": "message du client"},
            {"role": "assistant", "content": "réponse de l'agent"}
        ]
    }
    
    Response JSON:
    {
        "rapport_markdown": "...",
        "fiche_client": {...},
        "devis": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'conversation_history' not in data:
            return jsonify({
                "error": "Le champ 'conversation_history' est requis."
            }), 400
        
        conversation_history = data['conversation_history']
        
        # Valider le format
        if not isinstance(conversation_history, list):
            return jsonify({
                "error": "conversation_history doit être une liste."
            }), 400
        
        logger.info("Extraction de la fiche client...")
        
        # Étape 1: Extraire la fiche client
        fiche_client = extraire_fiche_client(conversation_history)
        
        logger.info(f"Fiche client extraite: {fiche_client.nom}")
        
        # Étape 2: Générer le devis
        devis = generer_devis(fiche_client)
        
        logger.info(f"Devis généré: total={devis.total}€")
        
        # Étape 3: Formater le rapport Markdown
        rapport = formater_rapport(fiche_client, devis)
        
        # Convertir les objets en dict pour la sérialisation JSON
        fiche_client_dict = {
            "nom": fiche_client.nom,
            "email": fiche_client.email,
            "telephone": fiche_client.telephone,
            "disponibilite": fiche_client.disponibilite,
            "type_demande": fiche_client.type_demande,
            "appareil": fiche_client.appareil,
            "symptomes": fiche_client.symptomes,
            "urgence": fiche_client.urgence,
            "description_libre": fiche_client.description_libre,
            "details": fiche_client.details
        }
        
        devis_dict = {
            "client": fiche_client_dict,
            "services": devis.services,
            "options": devis.options,
            "total": devis.total
        }
        
        return jsonify({
            "rapport_markdown": rapport,
            "fiche_client": fiche_client_dict,
            "devis": devis_dict
        })
        
    except ValueError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        return jsonify({
            "error": f"Données invalides: {str(e)}"
        }), 400
        
    except Exception as e:
        logger.error(f"Erreur dans /api/devis: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Erreur interne: {str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé.
    """
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "service": "agent-IA BeneIT API"
    })


# Point d'entrée pour le développement local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
