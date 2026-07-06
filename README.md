# Agent IA BeneIT - Phase 1.5 : API Web & Déploiement o2switch

Un système d'agents IA simple pour automatiser le support informatique de BeneIT, maintenant disponible via une API web prête pour le déploiement sur o2switch.

## \ud83d\udccc À propos

Ce projet implémente un **agent conversationnel** qui :
1. Pose des questions pour qualifier une demande client (problème technique ou service).
2. Structure les réponses en une **fiche client JSON**. 
3. Génère un **devis automatique** basé sur une grille tarifaire.
4. Produit un **rapport Markdown** prêt à envoyer au client.

**Nouveauté Phase 1.5** : L'agent est maintenant exposé via une **API Flask** compatible WSGI, prête à être déployée sur o2switch avec Phusion Passenger.

## \ud83d\udee0 Prérequis

- Python 3.8+
- Une **clé API OpenRouter** (gratuit pour commencer) : [https://openrouter.ai/keys](https://openrouter.ai/keys)

## \ud83d\ude80 Installation (Développement Local)

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
   pip install -r requirements.txt
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

5. Lancer l'API en développement :
   ```bash
   python app.py
   ```
   L'API sera disponible sur `http://localhost:5000`

## \ud83d\udcc2 Structure du Projet

```
agent-IA/
├── .env.example              # Exemple de configuration
├── .gitignore
├── config.py                 # Configuration centrale
├── passenger_wsgi.py         # Entrée WSGI pour Phusion Passenger (o2switch)
├── app.py                    # Application Flask avec les endpoints API
├── requirements.txt          # Dépendances Python
├── README.md
├── static/
│   └── chat-widget.html      # Widget de chat HTML/JS prêt à l'emploi
├── data/
│   └── pricing_grid.json     # Grille tarifaire (modifiable)
├── agents/
│   ├── __init__.py
│   ├── qualifier.py          # Agent de qualification (conversation + extraction)
│   └── estimator.py          # Génération de devis
├── models/
│   ├── __init__.py
│   └── schemas.py            # Schémas de données (FicheClient, Devis)
└── utils/
    ├── __init__.py
    ├── openrouter_client.py # Client API OpenRouter
    └── helpers.py            # Fonctions utilitaires
```

## \ud83c\udfaf Utilisation

### Tester l'API localement

Lancez le serveur Flask :
```bash
python app.py
```

#### Endpoint 1: Conversation
```bash
curl -X POST http://localhost:5000/api/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_history": [
      {"role": "user", "content": "Mon PC est très lent depuis hier, il plante tout le temps."}
    ]
  }'
```

Réponse :
```json
{
  "response": "Bonjour ! Quel est votre nom et votre email ?",
  "pret_pour_devis": false
}
```

#### Endpoint 2: Génération de devis
```bash
curl -X POST http://localhost:5000/api/devis \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_history": [
      {"role": "user", "content": "Mon PC est très lent depuis hier, il plante tout le temps."},
      {"role": "assistant", "content": "Bonjour ! Quel est votre nom et votre email ?"},
      {"role": "user", "content": "Jean Dupont, jean@exemple.com"},
      {"role": "assistant", "content": "Merci Jean. Quel est votre numéro de téléphone ?"},
      {"role": "user", "content": "+33 1 23 45 67 89"},
      {"role": "assistant", "content": "Quand êtes-vous disponible ?"},
      {"role": "user", "content": "Lundi après-midi"},
      {"role": "assistant", "content": "Quel appareil est concerné ?"},
      {"role": "user", "content": "PC Windows 11"},
      {"role": "assistant", "content": "Quels sont les symptômes précis ?"},
      {"role": "user", "content": "Lenteur, plantages fréquents"},
      {"role": "assistant", "content": "Quel est le niveau d'urgence ? (basse, moyenne, haute)"},
      {"role": "user", "content": "haute"},
      {"role": "assistant", "content": "Merci pour ces précisions. J'ai tout ce qu'il faut pour établir un devis.###READY###"}
    ]
  }'
```

Réponse :
```json
{
  "rapport_markdown": "# 📋 Rapport Client - BeneIT\n\n## 👤 Informations Client\n...",
  "fiche_client": {...},
  "devis": {...}
}
```

#### Endpoint 3: Health Check
```bash
curl http://localhost:5000/api/health
```

### Utiliser le Widget de Chat

Ouvrez simplement `static/chat-widget.html` dans un navigateur. Le widget appelle automatiquement les endpoints API sur le même domaine.

Pour l'intégrer à votre site :
1. Copiez le contenu de `static/chat-widget.html`
2. Collez-le dans une page HTML de votre site
3. Assurez-vous que l'API est accessible depuis votre domaine

## \ud83d\udce1 Déploiement sur o2switch

### Prérequis
- Un hébergement **o2switch** avec accès cPanel
- Python 3.8+ disponible sur votre hébergement
- Accès SSH ou Terminal cPanel

### Étapes de déploiement

#### 1. Préparer les fichiers

Vos fichiers doivent être organisés comme suit sur votre hébergement :
```
/home/votrecompte/
├── votre-domaine.com/
│   └── public_html/          # Site principal (optionnel)
└── api.votre-domaine.com/   # ou un sous-dossier de votre choix
    ├── app.py
    ├── passenger_wsgi.py
    ├── requirements.txt
    ├── config.py
    ├── .env                  # À créer avec vos variables
    ├── agents/
    ├── models/
    ├── utils/
    ├── data/
    └── static/
```

#### 2. Créer l'application Python via cPanel

1. Connectez-vous à votre **cPanel**
2. Allez dans **"Setup Python App"** (sous la section "Software")
3. Cliquez sur **"Create Application"**
4. Configurez les paramètres :
   - **Python version** : Sélectionnez Python 3.8 ou supérieur
   - **Application root** : `/home/votrecompte/api.votre-domaine.com` (ou votre dossier)
   - **Application URL** : `https://api.votre-domaine.com` (ou l'URL souhaitée)
   - **Application startup file** : `passenger_wsgi.py`
   - **Application entry point** : `application`
   - **Passenger log level** : `3` (pour le débogage, réduisez à `0` en production)
5. Cliquez sur **"Create"**

#### 3. Configurer les variables d'environnement

Dans l'interface "Setup Python App" :
1. Trouvez votre application dans la liste
2. Cliquez sur l'icône **"Edit"** (stylo)
3. Allez dans l'onglet **"Environment variables"**
4. Ajoutez les variables suivantes :
   - **Nom** : `OPENROUTER_API_KEY` | **Valeur** : `sk-or-v1-votre-cle-api`
   - **Nom** : `MODEL_NAME` | **Valeur** : `google/gemini-3.1-flash-lite` (ou autre modèle compatible)
5. Sauvegardez les modifications

#### 4. Installer les dépendances

Vous avez deux options :

**Option A: Via le Terminal cPanel (recommandé)**
1. Allez dans **"Terminal"** dans cPanel
2. Naviguez vers votre dossier d'application :
   ```bash
   cd /home/votrecompte/api.votre-domaine.com
   ```
3. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   ```
4. Activez l'environnement :
   ```bash
   source venv/bin/activate
   ```
5. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
6. Désactivez l'environnement :
   ```bash
   deactivate
   ```

**Option B: Via SSH**
```bash
ssh votrecompte@votre-serveur.o2switch.fr
cd /home/votrecompte/api.votre-domaine.com
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

#### 5. Configurer Passenger pour utiliser l'environnement virtuel

Dans "Setup Python App" :
1. Éditez votre application
2. Dans l'onglet **"Application settings"**
3. Ajoutez le chemin vers Python de votre venv dans **"Python path"** :
   - `/home/votrecompte/api.votre-domaine.com/venv/bin/python`
4. Sauvegardez

#### 6. Redémarrer l'application

Dans "Setup Python App" :
1. Trouvez votre application
2. Cliquez sur **"Restart"** (icône de recyclage)

#### 7. Vérifier le déploiement

Ouvrez votre navigateur et accédez à :
```
https://api.votre-domaine.com/api/health
```

Vous devriez voir :
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "agent-IA BeneIT API"
}
```

### Dépannage

**Problème : Erreur 500**
- Vérifiez les logs Passenger : `/home/votrecompte/logs/error_log`
- Assurez-vous que le fichier `.env` existe avec les bonnes variables
- Vérifiez que l'environnement virtuel est correctement configuré

**Problème : Module not found**
- Assurez-vous d'avoir installé les dépendances : `pip install -r requirements.txt`
- Vérifiez que Passenger utilise le bon Python (celui du venv)

**Problème : Permission denied**
- Exécutez : `chmod -R 755 /home/votrecompte/api.votre-domaine.com`
- Assurez-vous que les fichiers appartiennent à votre utilisateur

**Problème : CORS bloqué**
- Le widget et l'API doivent être sur le même domaine (ou sous-domaines)
- Si vous utilisez des domaines différents, modifiez `API_BASE_URL` dans le widget

## \ud83d\udce1 Intégration avec GitHub Pages

Si vous souhaitez utiliser le widget sur un site GitHub Pages :

1. Déployez l'API sur o2switch comme décrit ci-dessus
2. Modifiez `API_BASE_URL` dans `static/chat-widget.html` :
   ```javascript
   const API_BASE_URL = 'https://api.votre-domaine.com';
   ```
3. Copiez le fichier `static/chat-widget.html` dans votre dépôt GitHub Pages
4. Ajoutez-le comme iframe ou intégrez directement le code HTML

## \ud83d\udce1 Prochaines Étapes

- [ ] Déployer l'API sur o2switch
- [ ] Intégrer le widget sur votre site principal
- [ ] Personnaliser la grille tarifaire (`data/pricing_grid.json`)
- [ ] Configurer un nom de domaine personnalisé pour l'API

## \ud83e\udd1d Contribuer

Les contributions sont les bienvenues ! Ouvrez une **issue** ou une **pull request** pour :
- Proposer des améliorations.
- Signaler des bugs.
- Ajouter des fonctionnalités.

## \ud83d\udcc4 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.
