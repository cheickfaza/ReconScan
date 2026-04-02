# ReconScan
# ReconScan - Outil OSINT Complet de Recherche de Pseudo et Email

![Version](https://img.shields.io/badge/version-3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Description

**ReconScan** est une suite OSINT (Open Source Intelligence) complète et puissante conçue pour les investigations numériques. Elle intègre de multiples fonctionnalités avancées :

### 🔍 Recherche par pseudo
Trouver la présence d'un utilisateur sur plus de **94 plateformes** différentes avec analyse approfondie.

### 📧 Recherche par email
Analyser une adresse email pour découvrir :
- Fuites de données (HaveIBeenPwned)
- Profil Gravatar et comptes sociaux associés
- Informations sur le domaine

### 🔄 Recherche inversée de pseudo
- Analyse des patterns de noms d'utilisateur
- Génération de variations probables
- Corrélation entre différents comptes

### 🎯 Deep Scan (Mode approfondi)
- Extraction détaillée des profils (bio, followers, liens)
- Détection des technologies utilisées
- Analyse des métadonnées
- Vérification des fichiers spéciaux (robots.txt, sitemap.xml, etc.)

### 📊 Export avancé
- Rapports HTML interactifs avec graphiques
- Export CSV pour analyse Excel
- Export JSON pour intégration API

## ⚠️ Avertissement Important

Cet outil est destiné **uniquement** à des fins :
- Éducatives
- De recherche en sécurité légitime
- D'audit de votre propre empreinte numérique
- De tests d'intrusion autorisés

**L'utilisation de cet outil pour harceler, stalk ou nuire à autrui est strictement interdite et peut être illégale.**

## ✨ Fonctionnalités

- 🔍 **Recherche multi-plateformes** : Vérifie plus de 94 plateformes
- ⚡ **Recherche asynchrone** : Rapide et efficace
- 📊 **Rapports détaillés** : Export en JSON ou texte
- 🎨 **Interface colorée** : Affichage clair des résultats
- 🔧 **Personnalisable** : Timeout, concurrence, etc.
- 📝 **Mode silencieux** : Pour l'automatisation

## 📋 Plateformes Supportées

### 🔒 Cybersécurité & Hacking Éthique
- HackTheBox, TryHackMe, Bugcrowd, HackerOne, PentesterLab, Root-Me, CTFtime
- HackThisSite, WeChall, SecurityScorecard, VulnCon
- 0x00sec, KernelMode, Reverse Engineering Stack Exchange, Information Security Stack Exchange
- Guided Hacking, UnknownCheats, Elitepvpers, Hack Forums, Cracked.to, Nulled, BlackHatWorld

### 💻 Développement & DevOps
- GitHub, GitLab, Bitbucket, SourceForge
- Stack Overflow, Dev.to, CodePen
- Docker Hub, Ansible Galaxy
- npm, PyPI, RubyGems, Packagist, Maven, NuGet, Crates.io, Go Packages

### 📱 Réseaux Sociaux
- Twitter/X, Reddit, Instagram, Facebook, TikTok, LinkedIn, Mastodon
- Quora, Medium, Tumblr, VK, 4chan

### 🎮 Jeux Vidéo & Streaming
- Steam, Twitch, Xbox, PlayStation, Discord

### 🎨 Créatifs & Portfolio
- Pinterest, Behance, Dribbble, 500px, Flickr, Vimeo, YouTube
- About.me, Linktree, CodePen

### 📚 Recherche & Données
- Kaggle, Google Scholar, ResearchGate, Academia.edu, arXiv

### 💰 Finance & Business
- Patreon, Cash App, Venmo, AngelList, ProductHunt, Indie Hackers

### 📝 Blogging & Contenu
- Hashnode, Substack, Ghost, Medium

### 📡 Communication
- Telegram, Signal, WhatsApp, Skype, Gmail, ProtonMail

### 🎵 Divertissement
- SoundCloud, Spotify, TikTok, YouTube

### 🔐 Crypto & Sécurité
- Keybase

### 📌 Curation & Veille
- Pinboard, Pocket, Flipboard

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/cheickfaza/ReconScan.git
cd ReconScan
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Rendre le script exécutable** (optionnel)
```bash
chmod +x reconscan.py
chmod +x email_scanner.py
```

## 📖 Utilisation

### 🎯 Commandes principales

#### Recherche par pseudo
```bash
python reconscan.py pseudo_a_rechercher
```

#### Recherche par email
```bash
python reconscan.py --email cible@example.com
```

#### Deep Scan (analyse approfondie)
```bash
python deep_scanner.py https://github.com/username
```

#### Recherche inversée de pseudo
```bash
python username_correlator.py pseudo_a_analyser
```

### 📋 Exemples détaillés

**Recherche simple par pseudo :**
```bash
python reconscan.py john_doe
```

**Recherche avec export HTML :**
```bash
python reconscan.py test_user --format json
python -c "from advanced_exporter import AdvancedExporter; import json; data=json.load(open('report_username_*.json')); AdvancedExporter(data, 'username').export_html()"
```

**Analyse complète d'email :**
```bash
python reconscan.py --email target@gmail.com --format json
```

**Deep Scan d'une URL :**
```bash
python deep_scanner.py https://github.com/username https://reddit.com/user/username
```

**Corrélation de pseudos :**
```bash
python username_correlator.py john_doe_123
```

### Options disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `username` | Pseudo à rechercher (mode pseudo) | - |
| `-e, --email` | Email à analyser (mode email) | - |
| `-f, --format` | Format du rapport (text/json) | text |
| `-o, --output` | Nom du fichier de sortie | automatique |
| `-t, --timeout` | Délai d'attente en secondes | 10 |
| `-c, --concurrent` | Requêtes concurrentes max | 10 |
| `-q, --quiet` | Mode silencieux | false |
| `--no-save` | Ne pas sauvegarder le rapport | false |

### 📊 Modules avancés

| Module | Description |
|--------|-------------|
| `deep_scanner.py` | Analyse approfondie des profils et détection de technologies |
| `username_correlator.py` | Recherche inversée et corrélation de pseudos |
| `email_scanner.py` | Analyse d'emails (fuites, Gravatar, réseaux) |
| `advanced_exporter.py` | Export HTML/CSV avec graphiques interactifs |

## 📊 Structure des Rapports

### Rapport de recherche par pseudo (JSON)
```json
{
  "username": "pseudo_recherché",
  "timestamp": "2024-02-04 15:30:00",
  "summary": {
    "total_platforms": 94,
    "found": 12,
    "not_found": 30,
    "errors": 3
  },
  "results": {
    "found": [...],
    "not_found": [...],
    "errors": [...]
  }
}
```

### Rapport de recherche par email (JSON)
```json
{
  "email": "cible@example.com",
  "timestamp": "2024-02-04 15:30:00",
  "summary": {
    "total_breaches": 2,
    "gravatar_found": true,
    "social_accounts_found": 3,
    "errors": 0
  },
  "results": {
    "breaches": [...],
    "gravatar": {...},
    "social_accounts": [...],
    "domain_info": {...}
  }
}
```

### Rapport Deep Scan (JSON)
```json
{
  "timestamp": "2024-02-04 15:30:00",
  "total_urls": 1,
  "results": [{
    "url": "https://github.com/user",
    "status": 200,
    "profile_data": {
      "title": "User's Profile",
      "bio": "Developer...",
      "followers": "1.2k",
      "social_links": [...]
    },
    "technologies": [
      {"name": "React", "type": "framework"},
      {"name": "GitHub Pages", "type": "hosting"}
    ],
    "files_found": [
      {"file": "robots.txt", "exists": true}
    ]
  }]
}
```

## 🔧 Configuration Avancée

### Ajout de nouvelles plateformes

Pour ajouter une plateforme, modifiez le dictionnaire `PLATFORMS` dans `reconscan.py` :

```python
PLATFORMS = {
    "NomPlateforme": {
        "url": "https://exemple.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
}
```

### Configuration de l'API HaveIBeenPwned

Pour éviter les limitations de rate limiting, obtenez une clé API gratuite sur [HaveIBeenPwned](https://haveibeenpwned.com/API/Key) et configurez-la dans `email_scanner.py` :

```python
headers = {
    "user-agent": "ReconScan-OSINT-Tool",
    "hibp-api-key": "VOTRE_CLE_API"
}
```

### Personnalisation du Deep Scanner

Pour ajouter des technologies à détecter, modifiez `deep_scanner.py` :

```python
tech_patterns = {
    "VotreFramework": r'votre-pattern',
    "VotreCMS": r'votre-cms',
    # Ajoutez vos patterns ici
}
```

### Création de rapports personnalisés

Utilisez `advanced_exporter.py` pour générer des rapports dans différents formats :

```python
from advanced_exporter import AdvancedExporter

exporter = AdvancedExporter(data, "username")
exporter.export_html("rapport.html")
exporter.export_csv("rapport.csv")
exporter.export_json("rapport.json")
```

## ⚡ Performance

- **Vitesse** : Utilise l'asynchronisme pour des requêtes rapides
- **Contrôle** : Limite le nombre de requêtes concurrentes pour éviter le blocage
- **Respect** : Inclut des délais entre les requêtes pour ne pas surcharger les serveurs

## 🛡️ Limitations

### Recherche par pseudo
1. **Faux positifs** : Certaines plateformes peuvent retourner 200 même pour des comptes inexistants
2. **Rate limiting** : Les plateformes peuvent bloquer les requêtes trop nombreuses
3. **Comptes privés** : Certains comptes existent mais sont privés/inaccessibles
4. **Évolution des sites** : Les URLs et structures peuvent changer

### Recherche par email
1. **HaveIBeenPwned** : Limité sans clé API (rate limiting)
2. **Gravatar** : Nécessite que l'utilisateur ait un compte Gravatar
3. **Données partielles** : Certaines fuites ne sont pas publiques
4. **Emails jetables** : Les emails temporaires ne donnent pas de résultats

### Deep Scan
1. **Analyse statique** : L'analyse HTML ne capture pas le contenu dynamique (JavaScript)
2. **Anti-bot** : Certains sites bloquent les scanners automatiques
3. **Performance** : L'analyse approfondie est plus lente que le scan simple

## 🔒 Confidentialité et Éthique

Cet outil est conçu pour :
- L'audit de votre propre empreinte numérique
- La recherche en sécurité autorisée
- Les tests d'intrusion avec permission écrite
- L'éducation et la formation en cybersécurité

**Interdictions :**
- Harcèlement, stalking ou surveillance non consentie
- Collecte de données à des fins malveillantes
- Violation des conditions d'utilisation des services
- Toute activité illégale ou non éthique

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter de nouvelles plateformes
- Améliorer la détection
- Corriger des bugs
- Améliorer la documentation

## 🏗️ Architecture du projet

```
ReconScan/
├── reconscan.py           # Script principal (pseudo + email)
├── email_scanner.py       # Module d'analyse d'emails
├── deep_scanner.py        # Module de deep scan
├── username_correlator.py # Module de corrélation de pseudos
├── advanced_exporter.py   # Module d'export avancé
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
├── LICENCE.txt           # Licence MIT
├── install.sh            # Script d'installation
├── config.json           # Configuration
└── .gitignore            # Exclusions Git
```

## 📄 Licence

MIT License - Voir le fichier LICENCE.txt pour plus de détails.

## 🙏 Remerciements

- À la communauté OSINT pour l'inspiration
- Aux mainteneurs des différentes API utilisées
- À tous les contributeurs
- HaveIBeenPwned pour leur API de fuites de données
- Gravatar pour leur API de profils

---

**⚠️ RAPPEL** : Utilisez cet outil de manière responsable et éthique. Le respect de la vie privée d'autrui est primordial.

**🔗 Liens utiles :**
- [GitHub Repository](https://github.com/cheickfaza/ReconScan)
- [HaveIBeenPwned API](https://haveibeenpwned.com/API/Key)
- [Gravatar API](https://en.gravatar.com/site/implement/images/)
</content>
<task_progress>
- [x] Analyser le projet actuel
- [x] Configurer Git (nom et email)
- [x] Commit des modifications
- [x] Créer un dépôt sur GitHub et pousser le code
- [x] Vérifier le résultat
- [x] Supprimer .gitignore du suivi Git
- [x] Pousser les modifications vers GitHub
- [x] Analyser le code pour améliorer le projet
- [x] Choisir les améliorations à implémenter (Recherche par email)
- [x] Créer un fichier .gitignore approprié
- [x] Implémenter la recherche par email (module email_scanner.py)
- [x] Intégrer le module email au script principal
- [x] Mettre à jour le README
- [ ] Pousser les modifications vers GitHub
</task_progress>

## 🙏 Remerciements

- À la communauté OSINT pour l'inspiration
- Aux mainteneurs des différentes API utilisées
- À tous les contributeurs

---

**⚠️ RAPPEL** : Utilisez cet outil de manière responsable et éthique. Le respect de la vie privée d'autrui est primordial.
