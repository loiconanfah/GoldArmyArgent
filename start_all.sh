#!/bin/bash

echo "=========================================="
echo "   🪖 GOLDARMY - START ALL SERVICES"
echo "=========================================="
echo ""

# Démarrer le Backend (FastAPI)
echo "[1/2] Démarrage du Backend (FastAPI) sur le port 8000..."
python3 -m uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Attendre un peu que le backend initialise
sleep 2

# Démarrer le Frontend (Vite)
echo "[2/2] Démarrage du Frontend (Vite) sur le port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Tous les services sont lancés !"
echo ""
echo "🌐 Frontend : http://localhost:5173"
echo "🔌 API      : http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour TOUT arrêter."

# Gérer l'arrêt propre
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait
