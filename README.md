# Agent IA BeneIT - Phase 1 : Qualification et Devis Automatique

Un système d'agents IA simple pour automatiser le support informatique de BeneIT.

## 📌 À propos

Ce projet implémente un **agent conversationnel** qui :
1. Pose des questions pour qualifier une demande client (problème technique ou service).
2. Structure les réponses en une **fiche client JSON**. 
3. Génère un **devis automatique** basé sur une grille tarifaire.
4. Produit un **rapport Markdown** prêt à envoyer au client.

## 🛠 Prérequis

- Python 3.8+
- Une **clé API OpenRouter** (gratuit pour commencer) : [https://openrouter.ai/keys](https://openrouter.ai/keys)

## 🚀 Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/delcoco95/agent-IA.git
   cd agent-IA
   ```

2. Créer un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install openai python-dotenv
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   ```
   Puis éditez `.env` pour ajouter votre **clé API OpenRouter** et le **modèle souhaité** :
   ```ini
   OPENROUTER_API_KEY=sk-or-v1-...
   MODEL_NAME=google/gemini-3.1-flash-lite
   ```

## 📂 Structure du Projet

```
agent-IA/
├── .env.example              # Exemple de configuration
├── config.py                 # Configuration centrale
├── data/
│   └── pricing_grid.json     # Grille tarifaire (modifiable)
├── agents/
│   ├── __init__.py
│   ├── qualifier.py          # Agent de qualification (conversation + extraction)
│   └── estimator.py          # Génération de devis
├── models/
│   ├── __init__.py
│   └── schemas.py            # Schémas de données (FicheClient, Devis)
├── utils/
│   ├── __init__.py
│   ├── openrouter_client.py # Client API OpenRouter
│   └── helpers.py            # Fonctions utilitaires
├── main.py                   # Point d'entrée (test en local)
└── README.md
```

## 🎯 Utilisation

### Tester en local

Lancez une conversation simulée :
```bash
python main.py
```

Suivez les instructions pour simuler une conversation avec l'agent. Exemple :
```
🔹 Démarrage de la conversation avec le client...

🤖 Agent: Bonjour ! Quel est votre nom et votre email ?
👤 Client: Jean Dupont, jean@exemple.com
🤖 Agent: Merci Jean. Quel est votre numéro de téléphone ?
👤 Client: +33 1 23 45 67 89
... (suite de la conversation)
```

À la fin, l'agent générera un **rapport Markdown** complet avec :
- Les informations du client
- La demande qualifiée
- Le devis détaillé
- Les options supplémentaires

### Personnaliser la grille tarifaire

Éditez `data/pricing_grid.json` pour adapter les tarifs à votre activité. Exemple :
```json
{
  "services": {
    "diagnostic": {
      "nom": "Diagnostic complet",
      "prix": 50,
      "duree_minutes": 60
    },
    ...
  },
  "options": {
    "deplacement": {
      "nom": "Déplacement sur site",
      "prix": 40,
      "duree_minutes": 30
    }
  }
}
```

### Changer de modèle

Modifiez `MODEL_NAME` dans `.env` pour utiliser un autre modèle compatible OpenRouter :
```ini
MODEL_NAME=anthropic/claude-haiku-4-5
```

## 🔧 Fonctionnalités Clés

| Fonctionnalité | Description |
|----------------|-------------|
| **Conversation** | L'agent pose des questions pour qualifier la demande. |
| **Extraction** | Structure les réponses en JSON avec `response_format={"type": "json_object"}`. |
| **Devis** | Génère un devis basé sur la grille tarifaire. |
| **Rapport** | Produit un rapport Markdown prêt à envoyer. |
| **Validation** | Vérifie l'email, l'urgence, et le type de demande. |
| **Gestion d'erreur** | Capture les erreurs API et propose des messages clairs. |

## 📡 Prochaine Étape : API Web (FastAPI)

Pour déployer l'agent sur **Render** et le brancher à un widget de chat (GitHub Pages), la prochaine étape consiste à :

1. Créer une **API FastAPI** exposant :
   - `POST /poser-question` : Pour continuer une conversation.
   - `POST /extraire-fiche` : Pour extraire la fiche client.
   - `POST /generer-devis` : Pour générer le devis final.

2. Déployer l'API sur **Render** (gratuit).

3. Intégrer un **widget JavaScript** sur votre site GitHub Pages qui appelle l'API.

**Prêt à commencer cette partie ?** Dites-le-moi, et je vous guiderai !

## 🤝 Contribuer

Les contributions sont les bienvenues ! Ouvrez une **issue** ou une **pull request** pour :
- Proposer des améliorations.
- Signaler des bugs.
- Ajouter des fonctionnalités.

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.
