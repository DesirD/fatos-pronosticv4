# ⚽ Fatos Pronostic — Enèji

Moteur de pronostics football multi-ligues avec combinés et scores exacts.

## 🚀 Déploiement sur Railway (gratuit)

### Étape 1 — Créer un compte
1. Va sur [railway.app](https://railway.app)
2. Clique **"Start a New Project"**
3. Connecte-toi avec ton compte **GitHub** (gratuit)

### Étape 2 — Uploader le code sur GitHub
1. Va sur [github.com](https://github.com) → crée un compte gratuit
2. Clique le **"+"** en haut → **"New repository"**
3. Nomme-le `fatos-pronostic` → clique **"Create repository"**
4. Sur la page du repo, clique **"uploading an existing file"**
5. **Glisse-dépose TOUS les fichiers** du dossier `fatos_pronostic/` :
   - `app.py`
   - `predictor.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `railway.json`
   - le dossier `templates/` avec `index.html`
6. Clique **"Commit changes"**

### Étape 3 — Déployer sur Railway
1. Sur [railway.app](https://railway.app), clique **"New Project"**
2. Choisis **"Deploy from GitHub repo"**
3. Sélectionne ton repo `fatos-pronostic`
4. Railway détecte automatiquement que c'est Python/Flask
5. Clique **"Deploy"** — attends 2-3 minutes
6. Clique sur **"Settings"** → **"Generate Domain"**
7. Tu obtiens une URL publique genre : `https://fatos-pronostic-production.up.railway.app`

### Étape 4 — Utiliser sur téléphone
1. Ouvre l'URL sur ton téléphone Android ou iPhone
2. Dans le navigateur, clique le menu (⋮ ou □↑)
3. Choisis **"Ajouter à l'écran d'accueil"**
4. L'app apparaît comme une vraie application !

## 🔑 Clé API
Obtiens ta clé gratuite sur [the-odds-api.com](https://the-odds-api.com) (500 requêtes/mois gratuit)

## 📁 Structure
```
fatos_pronostic/
├── app.py           # Serveur Flask
├── predictor.py     # Moteur de prédictions
├── requirements.txt # Dépendances Python
├── Procfile         # Config gunicorn pour Railway
├── runtime.txt      # Version Python
├── railway.json     # Config Railway
└── templates/
    └── index.html   # Interface utilisateur
```
