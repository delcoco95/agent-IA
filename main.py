"""
Point d'entrée principal pour tester l'agent IA BeneIT.
Simule une conversation complète avec un client.
"""
from agents.extractor import extraire_fiche_client
from agents.estimator import generer_devis
from agents.router import detecter_domaine
from agents.specialists import get_specialist
from utils.helpers import formater_rapport
import json


def simuler_conversation():
    """
    Simule une conversation complète avec un client.
    """
    print("🔹 Démarrage de la conversation avec le client...\n")
    print("Tapez vos réponses comme si vous étiez le client.\n")

    # Premier message du client
    premier_message = input("👤 Client: ")
    conversation = [{"role": "user", "content": premier_message}]

    # Étape 0 : Détecter le domaine
    domaine = detecter_domaine(premier_message)
    print(f"🔍 Domaine détecté: {domaine}\n")
    specialist = get_specialist(domaine)

    # Étape 1 : Poser des questions avec l'agent spécialisé
    while True:
        reponse_agent = specialist.poser_question(conversation)

        if "###READY###" in reponse_agent:
            reponse_agent_nettoyee = reponse_agent.replace("###READY###", "").strip()
            print(f"🤖 Agent [{domaine}]: {reponse_agent_nettoyee}")
            conversation.append({"role": "assistant", "content": reponse_agent_nettoyee})
            break
        else:
            print(f"🤖 Agent [{domaine}]: {reponse_agent}")
            conversation.append({"role": "assistant", "content": reponse_agent})

        reponse_client = input("👤 Client: ")
        conversation.append({"role": "user", "content": reponse_client})

    print("\n✅ Agent prêt pour l'extraction !\n")

    # Étape 2 : Extraire la fiche client (avec champs spécifiques au domaine)
    print("🔹 Extraction de la fiche client...")
    try:
        fiche_client = extraire_fiche_client(
            conversation,
            champs_specifices=specialist.champs_specifices
        )
        fiche_client.domaine = domaine  # Forcer le domaine détecté
        print(f"Fiche extraite : {json.dumps(fiche_client.model_dump(), indent=2, ensure_ascii=False)}\n")
    except ValueError as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        return

    # Étape 3 : Générer le devis
    print("🔹 Génération du devis...")
    try:
        devis = generer_devis(fiche_client)
        print(f"Devis généré : {json.dumps(devis.model_dump(), indent=2, ensure_ascii=False, default=str)}\n")
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
