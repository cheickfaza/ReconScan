# ReconScan
# ReconScan - Outil OSINT de Recherche de Pseudo et Email

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Description

**ReconScan** est un outil OSINT (Open Source Intelligence) complet conçu pour :

1. **Recherche par pseudo** : Trouver la présence d'un utilisateur à travers internet en utilisant son pseudo/surnom. Il vérifie automatiquement la disponibilité d'un pseudo sur plus de **94 plateformes différentes**.

2. **Recherche par email** : Analyser une adresse email pour trouver :
   - Les fuites de données associées (via HaveIBeenPwned)
   - Le profil Gravatar et les comptes sociaux liés
   - Les informations sur le domaine de l'email

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

### Recherche par pseudo

**Commande de base :**
```bash
python reconscan.py pseudo_a_rechercher
```

**Exemples d'utilisation :**

Recherche simple :
```bash
python reconscan.py john_doe
```

Export en JSON avec nom de fichier personnalisé :
```bash
python reconscan.py test_user --format json --output rapport_test.json
```

Recherche avec paramètres avancés :
```bash
python reconscan.py username --timeout 15 --concurrent 5
```

Mode silencieux (pour scripts) :
```bash
python reconscan.py pseudo --quiet --no-save
```

### Recherche par email

**Commande de base :**
```bash
python reconscan.py --email cible@example.com
```

**Exemples d'utilisation :**

Analyse complète d'un email :
```bash
python reconscan.py --email target@gmail.com
```

Export en JSON :
```bash
python reconscan.py --email user@domain.com --format json
```

Avec timeout personnalisé :
```bash
python reconscan.py --email test@yahoo.com --timeout 15
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

## 📊 Structure du Rapport

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

### Ajout de nouvelles sources pour l'email scanner

Pour ajouter de nouvelles sources d'analyse email, modifiez `email_scanner.py` :

```python
async def check_nouvelle_source(self, session):
    """Vérifie une nouvelle source de données"""
    print(f"\n{Fore.CYAN}🔍 Vérification nouvelle source...{Style.RESET_ALL}")
    # Votre code ici
```

### Utilisation avec une clé API HaveIBeenPwned

Pour éviter les limitations de rate limiting, vous pouvez obtenir une clé API gratuite sur [HaveIBeenPwned](https://haveibeenpwned.com/API/Key) et la configurer dans `email_scanner.py` :

```python
headers = {
    "user-agent": "ReconScan-OSINT-Tool",
    "hibp-api-key": "VOTRE_CLE_API"
}
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
