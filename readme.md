# Résumeur de Vidéos YouTube

![Couverture du projet](src/youtube/static/youtube/images/work.jpg)

Summary.MouhaTech est une application web Django qui permet aux utilisateurs de résumer des vidéos YouTube en extrayant les transcriptions et en générant des résumés alimentés par intelligence artificielle de Google Gemini.

## Fonctionnalités

- Extraction des transcriptions des vidéos YouTube utilisant `youtube_transcript_api` et `yt_dlp`
- Génération de résumés structurés dans plusieurs langues (Français, Anglais, Espagnol, Allemand, Arabe, Italien)
- Support pour différentes longueurs de résumé (court, moyen, détaillé)
- Interface web pour une utilisation accessible en ligne [Resume.MouhaTech](https://summary.mouhatech.com)
- Point de terminaison API pour un accès programmatique

## Installation

### Prérequis

- Python 3.8+
- pip
- Environnement virtuel (recommandé)

### Configuration

1. Cloner le dépôt :

   ```bash
   git clone <url-du-dépôt>
   cd summary
   ```

2. Créer et activer un environnement virtuel :

   ```bash
   python -m venv env
   env\Scripts\activate  # Sur Windows
   source env/bin/activate # Sur MacOS/Linux
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurez les variables d'environnement :**
   Créez un fichier `env` dans le dossier `src/youtube/` avec les variables suivantes :

   - Obtenir une clé API Google Gemini depuis [Google AI Studio](https://makersuite.google.com/app/apikey)

   ```bash
   SECRET_KEY=votre-cle-secrete-django
   GOOGLE_GENAI_API_KEY=votre-cle-api-google-genai
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Configurer la base de données :

   ```bash
   cd src
   python manage.py migrate
   ```

6. Configurer la clé API :

   - Obtenir une clé API Google Gemini depuis [Google AI Studio](https://makersuite.google.com/app/apikey)
   - L'ajouter à `summary/settings.py` :
     ```python
     GOOGLE_GENAI_API_KEY = 'votre-clé-api-ici'
     ```

7. (Optionnel) Configurer les cookies pour les vidéos restreintes :
   - Placer vos cookies YouTube dans `cookies/cookies_youtube.txt` (par défaut)
   - Ou définir `COOKIE_FILE_PATH` dans les variables d'environnement pour un chemin personnalisé
   - Pour exporter les cookies YouTube : voir https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies

## Utilisation

1. Lancer le serveur de développement :

   ```bash
   python manage.py runserver
   ```

2. Ouvrir votre navigateur et aller sur `http://127.0.0.1:8000/`

3. Entrer une URL YouTube et sélectionner votre langue préférée et la longueur du résumé.

4. Cliquer sur "Résumer la vidéo" pour obtenir le résumé généré par IA.

### Utilisation de l'API

Vous pouvez également utiliser le point de terminaison API directement :

```bash
curl -X POST http://127.0.0.1:8000/api/summarize/ \
  -d "url=https://www.youtube.com/watch?v=VIDEO_ID&langue=fr&taille=moyen"
```

## Structure du Projet

```
summary/
├── src/
│   ├── summary/         # Projet Django principal
│   │   ├── cookies/     # Fichiers de cookies (Si disponible)
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   ├── youtube/          # Application YouTube
│   │   ├── views.py
│   │   ├── models.py
│   │   ├── templates/
│   │   └── static/
│   └── manage.py
├── env/                  # Environnement virtuel
├── redame.md
└── requirements.txt
```

## Dépendances

- Django 5.2+
- google-genai
- youtube-transcript-api
- yt-dlp
- pytube
- requests
- Et autres (voir requirements.txt)

## Contribution

1. Forker le dépôt
2. Créer une branche de fonctionnalité
3. Faire vos changements
4. Tester thoroughly
5. Soumettre une pull request

## Déploiement

Pour déployer en production :

1. Configurer les variables d'environnement :

   - `GOOGLE_GENAI_API_KEY` : Votre clé API Google Gemini
   - `COOKIE_FILE_PATH` : Chemin vers le fichier de cookies YouTube (optionnel)
   - Autres variables Django standard (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, etc.)

2. Assurer que le fichier de cookies est présent sur le serveur si nécessaire pour les vidéos restreintes.

3. Utiliser un serveur WSGI comme Gunicorn pour Django en production.

## Auteur

Ce projet est développé par Mouhamed Mbaye, développeur web full-stack. Voir son portfolio sur [MouhaTech](https://mouhatech.com).

## Licence

Ce projet est distribué sous licence MIT.  
Vous êtes libre de l’utiliser, le modifier et le redistribuer.  
Voir le fichier [LICENSE](Licence) pour plus de détails.

## Soutenez le créateur ☕

Si ce dépôt vous a été utile, vous pouvez me soutenir avec un café afin de m’aider à couvrir les frais d’hébergement et à continuer à l'améliorer.

<p align="center">
  <a href="https://my.moneyfusion.net/694717a3e075f7af6c1695f9" target="_blank">
    <img src="https://img.shields.io/badge/☕%20Offrir%20un%20café-791f87?style=for-the-badge" />
  </a>
</p>
