#!/bin/bash

echo "🪖 Lancement de GoldArmy Agent Dashboard..."
echo

# Vérifier si Streamlit est installé
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit n'est pas installé. Installation en cours..."
    pip install streamlit
    echo "✅ Streamlit installé !"
fi

echo "🚀 Démarrage du dashboard..."
echo
echo "Le dashboard sera disponible à: http://localhost:8501"
echo "Appuyez sur Ctrl+C pour arrêter"
echo

streamlit run dashboard.py --server.port 8501 --server.headless false
