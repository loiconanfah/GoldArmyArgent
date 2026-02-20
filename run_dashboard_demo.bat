@echo off
echo ========================================
echo   🪖 GoldArmy Agent - Dashboard Demo
echo ========================================
echo.
echo Lancement du dashboard avec le nouveau design...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.11+ depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier si Streamlit est installé
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Streamlit n'est pas installé. Installation en cours...
    pip install streamlit
)

REM Lancer le dashboard demo
echo 🚀 Ouverture du dashboard dans votre navigateur...
echo.
echo 💡 Pour arrêter le serveur: Ctrl+C
echo 🌐 URL: http://localhost:8501
echo.

streamlit run dashboard_demo.py --server.port=8501 --server.headless=false

pause
