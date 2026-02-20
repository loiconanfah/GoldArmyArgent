@echo off
echo 🪖 Lancement de GoldArmy Agent Dashboard...
echo.

REM Vérifier si Streamlit est installé
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit n'est pas installé. Installation en cours...
    pip install streamlit
    echo ✅ Streamlit installé !
)

echo 🚀 Démarrage du dashboard...
echo.
echo Le dashboard sera disponible à: http://localhost:8501
echo Appuyez sur Ctrl+C pour arrêter
echo.

streamlit run dashboard.py --server.port 8501 --server.headless false

pause
