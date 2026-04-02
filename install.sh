#!/bin/bash
# Script d'installation de ReconScan

echo "🔍 Installation de ReconScan - Outil OSINT"
echo "=========================================="

# Vérifier si Python3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python3 détecté: $(python3 --version)"

# Créer un environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Rendre le script exécutable
chmod +x reconscan.py

echo ""
echo "✅ Installation terminée avec succès!"
echo ""
echo "🚀 Pour utiliser ReconScan:"
echo "   source venv/bin/activate"
echo "   python reconscan.py <pseudo>"
echo ""
echo "📖 Pour plus d'informations, consultez le README.md"