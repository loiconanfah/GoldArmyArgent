#!/bin/bash

echo "========================================"
echo "   🪖 GoldArmy Agent - Dashboard Demo"
echo "========================================"
echo ""
echo "Lancement du dashboard avec le nouveau design..."
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    echo "Veuillez installer Python 3.11+ depuis votre gestionnaire de paquets"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "⚠️ pip3 n'est pas installé. Installation..."
    python3 -m ensurepip --default-pip
fi

# Vérifier si Streamlit est installé
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Streamlit n'est pas installé. Installation en cours..."
    pip3 install streamlit
fi

# Lancer le dashboard demo
echo "🚀 Ouverture du dashboard dans votre navigateur..."
echo ""
echo "💡 Pour arrêter le serveur: Ctrl+C"
echo "🌐 URL: http://localhost:8501"
echo ""

# Rendre le script exécutable s'il ne l'est pas déjà
chmod +x "$0" 2>/dev/null || true

# Lancer streamlit
python3 -m streamlit run dashboard_demo.py --server.port=8501 --server.headless=false

echo ""
echo "👋 Dashboard fermé. Au revoir!"
