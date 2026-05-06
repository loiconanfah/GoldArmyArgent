"""
GoldArmy — Ghostbuster Scheduler (Background 48h)
==================================================
Lance automatiquement le scan Ghostbuster toutes les 48h
pour les utilisateurs ayant activé le mode auto.

Démarrage : appelé une seule fois dans le startup_event de api/main.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from loguru import logger


# Intervalle entre deux cycles : 48 heures
SCAN_INTERVAL_HOURS = 48
SCAN_INTERVAL_SECONDS = SCAN_INTERVAL_HOURS * 3600


async def _run_ghostbuster_for_user(user_id: str) -> None:
    """Lance un scan Ghostbuster pour un utilisateur donné."""
    try:
        from agents.ghostbuster_agent import ghostbuster_agent
        result = await ghostbuster_agent.scan_and_generate(user_id=user_id)
        eligible_count = len(result.get("eligible", []))
        logger.info(
            f"[GhostbusterScheduler] User {user_id}: "
            f"{eligible_count} relance(s) générée(s) sur {result.get('total_scanned', 0)} candidatures."
        )

        # Mettre à jour last_run_at dans la config
        from core.database import get_db
        db = get_db()
        await db.ghostbuster_config.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_run_at": datetime.utcnow(),
                    "next_run_at": datetime.utcnow() + timedelta(hours=SCAN_INTERVAL_HOURS),
                    "last_result_count": eligible_count,
                }
            },
            upsert=True,
        )

        # Si des relances ont été générées, créer une notification in-app
        if eligible_count > 0:
            try:
                from api.notifications import create_notification
                await create_notification(
                    user_id=user_id,
                    title="🚨 Ghostbuster — Relances détectées",
                    message=f"{eligible_count} candidature(s) sans réponse depuis +15 jours. Relances prêtes à envoyer.",
                    type="warning",
                    action_url="/dashboard",
                )
            except Exception as notif_err:
                logger.debug(f"[GhostbusterScheduler] Notification non envoyée: {notif_err}")

    except Exception as e:
        logger.error(f"[GhostbusterScheduler] Erreur pour user {user_id}: {e}")


async def ghostbuster_scheduler_loop() -> None:
    """
    Boucle infinie qui s'exécute en background.
    Toutes les SCAN_INTERVAL_SECONDS, elle cherche tous les users
    avec auto_enabled=True et lance un scan pour chacun.
    """
    logger.info(
        f"[GhostbusterScheduler] Démarré — cycle toutes les {SCAN_INTERVAL_HOURS}h"
    )

    # Attendre 60s au démarrage pour laisser le serveur se stabiliser
    await asyncio.sleep(60)

    while True:
        try:
            from core.database import get_db
            db = get_db()

            # Trouver tous les users avec mode auto activé dont le prochain run est passé
            now = datetime.utcnow()
            cursor = db.ghostbuster_config.find(
                {
                    "auto_enabled": True,
                    "$or": [
                        {"next_run_at": {"$lte": now}},
                        {"next_run_at": {"$exists": False}},
                    ],
                },
                {"user_id": 1, "_id": 0},
            )
            configs = await cursor.to_list(length=None)

            if configs:
                logger.info(
                    f"[GhostbusterScheduler] {len(configs)} utilisateur(s) à traiter..."
                )
                # Traiter les users en parallèle (max 5 simultanément)
                semaphore = asyncio.Semaphore(5)

                async def _safe_run(uid: str) -> None:
                    async with semaphore:
                        await _run_ghostbuster_for_user(uid)

                await asyncio.gather(*[_safe_run(c["user_id"]) for c in configs])
            else:
                logger.debug("[GhostbusterScheduler] Aucun utilisateur à traiter ce cycle.")

        except Exception as e:
            logger.error(f"[GhostbusterScheduler] Erreur cycle principal: {e}")

        await asyncio.sleep(SCAN_INTERVAL_SECONDS)


def start_ghostbuster_scheduler() -> None:
    """
    Lance la boucle scheduler en tâche asyncio background.
    À appeler dans le startup_event de FastAPI.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(ghostbuster_scheduler_loop())
    logger.info("[GhostbusterScheduler] Tâche background enregistrée.")
