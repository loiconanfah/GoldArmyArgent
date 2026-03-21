@echo off
setlocal
echo ==========================================
echo    🪖 GOLDARMY - START ALL SERVICES
echo ==========================================
echo.

:: Ouvrir le Backend (FastAPI) dans une nouvelle fenêtre
echo [1/2] Démarrage du Backend (FastAPI) sur le port 8000...
start "GoldArmy Backend" /min cmd /c "python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

:: Attendre un peu que le backend initialise
timeout /t 2 /nobreak > nul

:: Ouvrir le Frontend (Vite) dans une nouvelle fenêtre
echo [2/2] Démarrage du Frontend (Vite) sur le port 5173...
cd frontend
start "GoldArmy Frontend" /min cmd /c "npm run dev"

echo.
echo ✅ Tous les services sont lancés !
echo.
echo 🌐 Frontend : http://localhost:5173
echo 🔌 API      : http://localhost:8000/docs
echo.
echo Appuyez sur une touche pour voir les logs... (Note: les terminaux sont minimisés)
pause
