"""
GoldArmy — Network Ninja Agent (Workflow #3)
============================================
Scanne les 15 dernières candidatures APPLIED/FOLLOW_UP du CRM,
cherche les décideurs LinkedIn pour chaque entreprise unique,
génère un message d'approche personnalisé ≤ 180 chars par profil,
et persiste les résultats dans MongoDB (permanent, par user).
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger


# ---------------------------------------------------------------------------
# NetworkNinjaAgent
# ---------------------------------------------------------------------------
class NetworkNinjaAgent:
    """Agent qui chasse les décideurs LinkedIn à partir du CRM."""

    MAX_COMPANIES = 8      # max d'entreprises traitées en //
    MAX_APPS      = 15     # dernières candidatures analysées
    MSG_MAX_CHARS = 180    # limite message LinkedIn

    async def run(self, user_id: str) -> Dict[str, Any]:
        """
        Lance le workflow complet :
        1. Récupère les MAX_APPS dernières candidatures APPLIED/FOLLOW_UP
        2. Déduplique par company_name (garde le plus récent)
        3. Pour chaque entreprise unique → find_decision_makers (parallèle, max 8)
        4. Génère un message LinkedIn ≤ 180 chars par profil (batch LLM)
        5. Persiste dans db.ninja_results et retourne les données

        Returns:
            {
                "companies": [
                    {
                        "company_name": str,
                        "job_title": str,
                        "app_id": str,
                        "profiles": [
                            {
                                "name": str,
                                "role": str,
                                "linkedin_url": str,
                                "snippet": str,
                                "message": str,  # ≤ 180 chars
                            }
                        ]
                    }
                ],
                "total_profiles": int,
                "generated_at": str,
            }
        """
        from core.database import get_db
        db = get_db()

        # ── Profil utilisateur (pour personnaliser les messages) ─────────────
        user_data = await db.users.find_one({"id": user_id}, {"_id": 0}) or {}
        user_name = user_data.get("full_name") or user_data.get("email", "un candidat")
        cv_text   = user_data.get("cv_text", "")

        # ── Récupère les dernières candidatures éligibles ────────────────────
        cursor = db.applications.find(
            {
                "user_id": user_id,
                "status": {"$in": ["APPLIED", "FOLLOW_UP"]},
            },
            {"_id": 0},
        ).sort("created_at", -1).limit(self.MAX_APPS)

        apps: List[Dict] = await cursor.to_list(length=self.MAX_APPS)

        if not apps:
            logger.info(f"[NetworkNinja] Aucune candidature éligible pour user {user_id}")
            return {"companies": [], "total_profiles": 0, "generated_at": datetime.utcnow().isoformat()}

        # ── Déduplication par company_name (garde le plus récent) ───────────
        seen: Dict[str, Dict] = {}
        for app in apps:
            name = (app.get("company_name") or "").strip()
            if name and name not in seen:
                seen[name] = app

        unique_companies = list(seen.values())[: self.MAX_COMPANIES]
        logger.info(
            f"[NetworkNinja] {len(apps)} candidatures → "
            f"{len(unique_companies)} entreprises uniques à traiter"
        )

        # ── Recherche des décideurs en parallèle (max MAX_COMPANIES) ────────
        semaphore = asyncio.Semaphore(self.MAX_COMPANIES)

        async def _fetch_profiles(app: Dict) -> Dict:
            company = (app.get("company_name") or "").strip()
            job_title = app.get("job_title", "Poste")
            app_id    = app.get("id", "")
            async with semaphore:
                try:
                    from agents.headhunter import headhunter_agent
                    profiles_raw = await headhunter_agent.find_decision_makers(
                        {"company_name": company}
                    )
                except Exception as e:
                    logger.warning(f"[NetworkNinja] Headhunter error for {company}: {e}")
                    profiles_raw = []

            return {
                "company_name": company,
                "job_title": job_title,
                "app_id": app_id,
                "profiles_raw": profiles_raw or [],
            }

        company_data_list = await asyncio.gather(
            *[_fetch_profiles(app) for app in unique_companies]
        )

        # ── Génération des messages LinkedIn en batch ────────────────────────
        # On collecte tous les profils et on génère en // (max 20 LLM calls)
        all_profile_tasks = []
        for company_data in company_data_list:
            for profile in company_data["profiles_raw"]:
                all_profile_tasks.append((company_data, profile))

        msg_semaphore = asyncio.Semaphore(10)

        async def _generate_message(company_data: Dict, profile: Dict) -> Dict:
            async with msg_semaphore:
                msg = await self._generate_linkedin_message(
                    person_name=profile.get("name", ""),
                    person_role=profile.get("role", ""),
                    company_name=company_data["company_name"],
                    job_title=company_data["job_title"],
                    user_name=user_name,
                    cv_text=cv_text,
                )
            return {
                "name": profile.get("name", ""),
                "role": profile.get("role", ""),
                "linkedin_url": profile.get("linkedin_url", ""),
                "snippet": profile.get("snippet", ""),
                "message": msg,
            }

        enriched_profiles_all = await asyncio.gather(
            *[_generate_message(cd, p) for cd, p in all_profile_tasks]
        )

        # ── Reconstruction par entreprise ────────────────────────────────────
        profile_index = 0
        companies_result = []
        for company_data in company_data_list:
            count = len(company_data["profiles_raw"])
            enriched = list(enriched_profiles_all[profile_index: profile_index + count])
            profile_index += count

            if not enriched:
                continue  # Entreprise sans profil → on skip

            companies_result.append({
                "company_name": company_data["company_name"],
                "job_title":    company_data["job_title"],
                "app_id":       company_data["app_id"],
                "profiles":     enriched,
            })

        # ── Persistance MongoDB (upsert par user_id) ─────────────────────────
        now = datetime.utcnow()
        doc = await db.ninja_results.find_one({"user_id": user_id})
        
        final_companies = []
        if doc and "companies" in doc:
            # Garder les compagnies existantes (OSINT manuelles ou anciennes)
            final_companies = doc["companies"]
            # Mettre à jour ou ajouter les nouvelles (venant des applications)
            for new_c in companies_result:
                idx = next((i for i, c in enumerate(final_companies) if c["company_name"].lower() == new_c["company_name"].lower()), None)
                if idx is not None:
                    final_companies[idx] = new_c
                else:
                    final_companies.append(new_c)
        else:
            final_companies = companies_result

        await db.ninja_results.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id":      user_id,
                    "companies":    final_companies,
                    "total_profiles": sum(len(c.get("profiles", [])) for c in final_companies),
                    "generated_at": now,
                    "updated_at":   now,
                }
            },
            upsert=True,
        )

        companies_result = final_companies

        total = sum(len(c["profiles"]) for c in companies_result)
        logger.success(
            f"[NetworkNinja] Terminé pour user {user_id}: "
            f"{len(companies_result)} entreprises, {total} profils."
        )

        return {
            "companies":      companies_result,
            "total_profiles": total,
            "generated_at":   now.isoformat(),
        }

    async def get_results(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Lit les résultats persistés depuis MongoDB."""
        from core.database import get_db
        db = get_db()
        doc = await db.ninja_results.find_one({"user_id": user_id}, {"_id": 0})
        return doc

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    async def _generate_linkedin_message(
        self,
        person_name:  str,
        person_role:  str,
        company_name: str,
        job_title:    str,
        user_name:    str,
        cv_text:      str,
    ) -> str:
        """Génère un message d'approche LinkedIn ≤ 180 caractères via LLM."""
        from llm.unified_client import UnifiedLLMClient

        llm = UnifiedLLMClient()

        prompt = (
            f"Rédige un message LinkedIn professionnel de mise en relation de MAX 200 caractères en français.\n"
            f"RÈGLE ABSOLUE : Le message DOIT faire 200 caractères maximum.\n"
            f"INTERDICTION FORMELLE : Ne mentionne JAMAIS de recherche d'emploi, de candidature ou de poste ouvert. L'objectif est purement le NETWORKING et la mise en relation entre experts d'un même secteur.\n"
            f"Structure : [Prénom], [1 phrase sur une synergie entre mon domaine et ce que fait {company_name}], "
            f"[invitation à échanger sur nos enjeux communs]. Signature : {user_name.split()[0] if user_name else 'Moi'}.\n\n"
            f"Contexte :\n"
            f"- Destinataire : {person_name} ({person_role} chez {company_name})\n"
            f"- Mon profil (secteur/expertise) : {cv_text[:300] if cv_text else 'Professionnel du secteur'}\n\n"
            f"Réponds UNIQUEMENT par le texte du message. Maximum 200 caractères."
        )

        try:
            result = await llm.chat(
                [{"role": "user", "content": prompt}],
                model="gemini-2.0-flash",
                max_tokens=90,
                temperature=0.7,
                timeout=30,
            )
            msg = (result or "").strip()
            if len(msg) > 200:
                msg = msg[:197] + "..."
            return msg
        except Exception as e:
            logger.warning(f"[NetworkNinja] LLM message error: {e}")
            # Fallback
            fallback = (
                f"{person_name.split()[0] if person_name else 'Bonjour'}, "
                f"profil {job_title} chez {company_name} m'intéresse. "
                f"Échange possible ? — {user_name.split()[0] if user_name else ''}"
            )
            return fallback[:180]

    async def add_manual_search(self, user_id: str, company_name: str, profiles: list):
        """
        Appelé par Headhunter pour ajouter de façon permanente une recherche au graphe Network Ninja.
        """
        try:
            from core.database import get_db
            db = get_db()
            # 1. Infos utilisateur
            user = await db.users.find_one({"id": user_id}) or {}
            user_name = user.get("name", "") if user else ""
            cv_text = ""
            if user and user.get("parsed_resume"):
                cv_text = str(user.get("parsed_resume"))[:1000]

            # 2. Enrichir les profils avec un message
            enriched_profiles = []
            for profile in profiles:
                msg = await self._generate_linkedin_message(
                    person_name=profile.get("name", ""),
                    person_role=profile.get("role", ""),
                    company_name=company_name,
                    job_title="Recherche Libre",
                    user_name=user_name,
                    cv_text=cv_text,
                )
                enriched_profiles.append({
                    "name": profile.get("name", ""),
                    "role": profile.get("role", ""),
                    "linkedin_url": profile.get("linkedin_url", ""),
                    "snippet": profile.get("snippet", ""),
                    "message": msg,
                })

            if not enriched_profiles:
                return

            # 3. Met à jour ninja_results
            company_data = {
                "company_name": company_name,
                "job_title": "Recherche OSINT",
                "app_id": "osint_manual",
                "profiles": enriched_profiles
            }

            now = datetime.utcnow()
            doc = await db.ninja_results.find_one({"user_id": user_id})

            if not doc:
                # Créer le document
                await db.ninja_results.insert_one({
                    "user_id": user_id,
                    "companies": [company_data],
                    "total_profiles": len(enriched_profiles),
                    "generated_at": now,
                    "updated_at": now,
                })
            else:
                # Mettre à jour si la compagnie existe, sinon ajouter
                companies = doc.get("companies", [])
                existing_company = next((c for c in companies if c.get("company_name", "").lower() == company_name.lower()), None)

                if existing_company:
                    # Remplacer les profils de l'entreprise existante
                    existing_company["profiles"] = enriched_profiles
                else:
                    companies.append(company_data)

                await db.ninja_results.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "companies": companies,
                            "total_profiles": sum(len(c.get("profiles", [])) for c in companies),
                            "updated_at": now,
                        }
                    }
                )
            logger.success(f"[NetworkNinja] Recherche manuelle '{company_name}' ajoutée pour user {user_id}")
        except Exception as e:
            logger.error(f"[NetworkNinja] Erreur add_manual_search: {e}")


# Singleton
network_ninja_agent = NetworkNinjaAgent()
