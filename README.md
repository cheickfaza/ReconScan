# ReconScan - Outil OSINT de Recherche de Pseudo

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Description

**ReconScan** est un outil OSINT (Open Source Intelligence) conçu pour rechercher la présence d'un utilisateur à travers internet en utilisant son pseudo/surnom. Il vérifie automatiquement la disponibilité d'un pseudo sur plus de **80 plateformes différentes**, incluant les réseaux sociaux, les plateformes de hacking éthique, de développement, et bien plus encore.

## ⚠️ Avertissement Important

Cet outil est destiné **uniquement** à des fins :
- Éducatives
- De recherche en sécurité légitime
- D'audit de votre propre empreinte numérique
- De tests d'intrusion autorisés

**L'utilisation de cet outil pour harceler, stalk ou nuire à autrui est strictement interdite et peut être illégale.**

## ✨ Fonctionnalités

- 🔍 **Recherche multi-plateformes** : Vérifie plus de 80 plateformes
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

1. **Cloner le repository** (si applicable) ou télécharger les fichiers
```bash
cd /chemin/vers/ReconScan
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Rendre le script exécutable** (optionnel)
```bash
chmod +x reconscan.py
```

## 📖 Utilisation

### Commande de base
```bash
python reconscan.py pseudo_a_rechercher
```

### Exemples d'utilisation

**Recherche simple :**
```bash
python reconscan.py john_doe
```

**Export en JSON avec nom de fichier personnalisé :**
```bash
python reconscan.py test_user --format json --output rapport_test.json
```

**Recherche avec paramètres avancés :**
```bash
python reconscan.py username --timeout 15 --concurrent 5
```

**Mode silencieux (pour scripts) :**
```bash
python reconscan.py pseudo --quiet --no-save
```

### Options disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `username` | Pseudo à rechercher (obligatoire) | - |
| `-f, --format` | Format du rapport (text/json) | text |
| `-o, --output` | Nom du fichier de sortie | automatique |
| `-t, --timeout` | Délai d'attente en secondes | 10 |
| `-c, --concurrent` | Requêtes concurrentes max | 10 |
| `-q, --quiet` | Mode silencieux | false |
| `--no-save` | Ne pas sauvegarder le rapport | false |

## 📊 Structure du Rapport

### Format JSON
```json
{
  "username": "pseudo_recherché",
  "timestamp": "2024-02-04 15:30:00",
  "summary": {
    "total_platforms": 45,
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

### Format Texte
Rapport lisible avec résumé et liste des plateformes trouvées.

## 🔧 Configuration Avancée

### Ajout de nouvelles plateformes

Pour ajouter une plateforme, modifiez le dictionnaire `PLATFORMS` dans `reconscan.py` :

```python
PLATFORMS = {
    "NomPlateforme": {
        "url": "https://exemple.com/{}",  # {} sera remplacé par le pseudo
        "type": "web",  # ou "api" ou "special"
        "method": "GET",
        "status_code": 200  # Code HTTP indiquant que le compte existe
    },
    # ... autres plateformes
}
```

### Types de plateformes

- **web** : Site web standard (détection par code HTTP)
- **api** : API avec réponse structurée
- **special** : Nécessite une vérification manuelle

## ⚡ Performance

- **Vitesse** : Utilise l'asynchronisme pour des requêtes rapides
- **Contrôle** : Limite le nombre de requêtes concurrentes pour éviter le blocage
- **Respect** : Inclut des délais entre les requêtes pour ne pas surcharger les serveurs

## 🛡️ Limitations et Considérations

1. **Faux positifs** : Certaines plateformes peuvent retourner 200 même pour des comptes inexistants
2. **Rate limiting** : Les plateformes peuvent bloquer les requêtes trop nombreuses
3. **Comptes privés** : Certains comptes existent mais sont privés/inaccessibles
4. **Évolution des sites** : Les URLs et structures peuvent changer

## 🔄 Mises à jour

Pour mettre à jour la liste des plateformes, modifiez simplement le dictionnaire `PLATFORMS` dans le fichier `reconscan.py`.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter de nouvelles plateformes
- Améliorer la détection
- Corriger des bugs
- Améliorer la documentation

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- À la communauté OSINT pour l'inspiration
- Aux mainteneurs des différentes API utilisées
- À tous les contributeurs

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur le repository.

---

**⚠️ RAPPEL** : Utilisez cet outil de manière responsable et éthique. Le respect de la vie privée d'autrui est primordial.