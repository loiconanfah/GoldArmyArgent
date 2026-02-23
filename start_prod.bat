@echo off
echo =======================================================
echo     Demarrage de GoldArmy Agent SaaS - PRODUCTION
echo =======================================================
echo.
echo Mode: Multi-Worker (Optimise pour ++ de 10 000 utilisateurs)
echo CPU Cores alloues: 4
echo.

:: Vérifier si le port est libre (Optionnel, utile en débug)
:: Lancer Uvicorn avec 4 workers pour profiter du multi-cœur
:: Remplacer 'api.main:app' par le chemin de votre instance FastAPI si différent
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info

echo.
pause
