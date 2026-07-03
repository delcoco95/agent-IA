"""
Point d'entrée principal pour tester l'agent IA BeneIT.
Simule une conversation complète avec un client.
"""
from agents.qualifier import poser_question, extraire_fiche_client
from agents.estimator import generer_devis
from utils.helpers import formater_rapport
import json


def simuler_conversation():
    """
    Simule une conversation complète avec un client.
    
    Ce flux suit les étapes :
    1. Conversation avec poser_question() jusqu'à ce que l'agent soit prêt (###READY###).
    2. Extraction de la fiche client avec extraire_fiche_client().
    3. Génération du devis avec generer_devis().
    4. Formatage du rapport final en Markdown.
    """
    print("🔹 Démarrage de la conversation avec le client...\n")
    print("Tapez vos réponses comme si vous étiez le client.\n")

    # Historique de conversation (commence avec le message initial du client)
    conversation = [
        {"role": "user", "content": "Mon PC est très lent depuis hier, il plante tout le temps."}
    ]

    # Étape 1 : Poser des questions jusqu'à ce que l'agent soit prêt
    while True:
        # L'agent pose une question ou signale qu'il a assez d'infos
        reponse_agent = poser_question(conversation)

        # Nettoyer le marqueur ###READY### avant affichage/stockage
        if "###READY###" in reponse_agent:
            reponse_agent_nettoyee = reponse_agent.replace("###READY###", "").strip()
            print(f"🤖 Agent: {reponse_agent_nettoyee}")
            conversation.append({"role": "assistant", "content": reponse_agent_nettoyee})
            break
        else:
            print(f"🤖 Agent: {reponse_agent}")
            conversation.append({"role": "assistant", "content": reponse_agent})

        # Simuler la réponse du client (en vrai, ce serait une entrée utilisateur)
        reponse_client = input("👤 Client: ")
        conversation.append({"role": "user", "content": reponse_client})

    print("\n✅ Agent prêt pour l'extraction !\n")

    # Étape 2 : Extraire la fiche client
    print("🔹 Extraction de la fiche client...")
    try:
        fiche_client = extraire_fiche_client(conversation)
        print(f"Fiche extraite : {json.dumps(fiche_client.__dict__, indent=2, ensure_ascii=False)}\n")
    except ValueError as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        return

    # Étape 3 : Générer le devis
    print("🔹 Génération du devis...")
    try:
        devis = generer_devis(fiche_client)
        print(f"Devis généré : {json.dumps(devis.__dict__, indent=2, ensure_ascii=False, default=str)}\n")
    except ValueError as e:
        print(f"❌ Erreur lors de la génération du devis : {e}")
        return

    # Étape 4 : Formater le rapport final
    rapport = formater_rapport(fiche_client, devis)
    print("📄 Rapport final (Markdown) :\n")
    print(rapport)

    return rapport


if __name__ == "__main__":
    simuler_conversation()
