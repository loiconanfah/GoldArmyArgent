import asyncio
import time
from typing import Any, Dict, List

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="GoldArmy Agent - Demo",
    page_icon="🪖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700;800&display=swap');

    /* === GLOBAL DARK THEME === */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #e2e8f0;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}

    /* === TYPOGRAPHY === */
    html, body, [class*="css"] {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }

    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: #0f172a !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
        font-family: 'Poppins', sans-serif;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(251, 191, 36, 0.4);
    }

    /* === INPUTS === */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        padding: 12px 16px !important;
        backdrop-filter: blur(10px) !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: rgba(251, 191, 36, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1) !important;
    }

    /* === CUSTOM COMPONENTS === */
    .brand-logo {
        font-size: 1.8rem;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }

    .menu-section {
        margin: 1.5rem 0;
    }

    .menu-title {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        padding: 0 1rem;
    }

    .menu-item {
        color: #cbd5e1;
        padding: 12px 16px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 6px 12px;
        transition: all 0.3s ease;
    }
    .menu-item:hover {
        background: rgba(251, 191, 36, 0.1);
        color: #fbbf24;
        transform: translateX(4px);
    }
    .menu-item.active {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border-left: 3px solid #fbbf24;
    }

    .hero-container {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 800px;
        margin: 0 auto;
    }

    .hero-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(251, 191, 36, 0.3)); }
        to { filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.6)); }
    }

    .hero-title {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 3rem;
        line-height: 1.6;
    }

    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
    }

    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(251, 191, 36, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }

    .job-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
    }

    .job-card:hover {
        border-color: rgba(251, 191, 36, 0.4);
        transform: translateX(4px);
        box-shadow: -4px 0 15px rgba(251, 191, 36, 0.2);
    }

    .match-badge {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #0f172a;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .premium-card {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border: 1px solid rgba(251, 191, 36, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 2rem;
        backdrop-filter: blur(20px);
    }

    .premium-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #fbbf24;
        margin-bottom: 0.5rem;
    }

    .premium-desc {
        color: #cbd5e1;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        line-height: 1.4;
    }

    .search-container {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        margin: 2rem auto;
        max-width: 600px;
    }

    /* === CHAT === */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        margin-bottom: 1rem !important;
    }

    .stChatInputContainer > div {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(15px) !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(251, 191, 36, 0.3);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(251, 191, 36, 0.5);
    }
</style>
""",
    unsafe_allow_html=True,
)

# État de l'application
if "demo_history" not in st.session_state:
    st.session_state.demo_history = []
if "demo_results" not in st.session_state:
    st.session_state.demo_results = []

# Données de démonstration
DEMO_JOBS = [
    {
        "title": "Développeur Python Junior",
        "company": "TechCorp Inc.",
        "location": "Montréal, QC",
        "match_score": 92,
        "matched_skills": ["Python", "Django", "PostgreSQL", "Git"],
        "match_justification": "Excellente correspondance avec votre profil Python et expérience en développement web. L'entreprise recherche spécifiquement des juniors motivés.",
        "url": "https://example.com/job1",
    },
    {
        "title": "Stage en Intelligence Artificielle",
        "company": "AI Solutions Ltd",
        "location": "Québec, QC",
        "match_score": 87,
        "matched_skills": ["Machine Learning", "Python", "TensorFlow"],
        "match_justification": "Parfait pour approfondir vos connaissances en IA. Stage de 4 mois avec possibilité d'embauche.",
        "url": "https://example.com/job2",
    },
    {
        "title": "Développeur Full Stack React/Node",
        "company": "StartupXYZ",
        "location": "Gatineau, QC",
        "match_score": 78,
        "matched_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "match_justification": "Bonne opportunité pour développer vos compétences full-stack dans un environnement startup dynamique.",
        "url": "https://example.com/job3",
    },
    {
        "title": "Analyste Data Junior",
        "company": "DataViz Pro",
        "location": "Ottawa, ON",
        "match_score": 71,
        "matched_skills": ["SQL", "Python", "Pandas", "Tableau"],
        "match_justification": "Position intéressante pour débuter en analyse de données, formation fournie sur les outils avancés.",
        "url": "https://example.com/job4",
    },
]


def simulate_search(query: str) -> List[Dict[str, Any]]:
    """Simule une recherche et retourne des résultats de démo"""
    # Simulation d'un délai de recherche
    time.sleep(2)
    return DEMO_JOBS


def display_job_results(jobs: List[Dict[str, Any]]):
    """Affiche les résultats de recherche d'emploi"""
    st.markdown(
        f"""
    <div style="margin-bottom: 2rem;">
        <h2 style="color: #e2e8f0; font-weight: 700; margin-bottom: 0.5rem;">
            🎯 {len(jobs)} opportunités trouvées
        </h2>
        <p style="color: #94a3b8; font-size: 1rem;">
            Résultats triés par pertinence • Mis à jour il y a quelques minutes
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    for i, job in enumerate(jobs, 1):
        score = job["match_score"]
        score_color = (
            "#22c55e" if score >= 80 else "#fbbf24" if score >= 60 else "#ef4444"
        )

        st.markdown(
            f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <h3 style="font-weight: 700; font-size: 1.2rem; color: #e2e8f0; margin: 0;">
                    {job["title"]}
                </h3>
                <div class="match-badge" style="background: linear-gradient(135deg, {score_color}, {score_color}dd);">
                    ⭐ {score}% Match
                </div>
            </div>

            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                🏢 {job["company"]} • 📍 {job["location"]}
            </div>

            <div style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem;">
                {job["match_justification"]}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: #64748b; font-size: 0.8rem;">
                    🛠️ {", ".join(job["matched_skills"][:4])}
                </div>
                <a href="{job["url"]}" target="_blank" style="color: #fbbf24; text-decoration: none; font-weight: 600; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.5rem; transition: all 0.3s ease;">
                    Voir l'offre →
                </a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# === SIDEBAR ===
with st.sidebar:
    # Brand Header
    st.markdown(
        """
    <div class="brand-logo">
        🪖 GoldArmy Agent
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Primary Actions
    if st.button("🆕 Nouvelle Recherche", use_container_width=True):
        st.session_state.demo_history = []
        st.session_state.demo_results = []
        st.rerun()

    # Navigation Menu
    st.markdown(
        """
    <div class="menu-section">
        <div class="menu-title">🎛️ Agents</div>
        <div class="menu-item active">🪖 Job Searcher</div>
        <div class="menu-item">🔍 Researcher</div>
        <div class="menu-item">💻 Coder</div>
        <div class="menu-item">📋 Planner</div>
    </div>

    <div class="menu-section">
        <div class="menu-title">📊 Analytics</div>
        <div class="menu-item">📈 Performance</div>
        <div class="menu-item">🎯 Taux de Succès</div>
        <div class="menu-item">📝 Historique</div>
    </div>

    <div class="menu-section">
        <div class="menu-title">⚙️ Configuration</div>
        <div class="menu-item">🔧 Paramètres</div>
        <div class="menu-item">🤖 Modèles IA</div>
        <div class="menu-item">🔑 API Keys</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Premium Card
    st.markdown(
        """
    <div class="premium-card">
        <div class="premium-title">⚡ GoldArmy Pro</div>
        <div class="premium-desc">Débloquez des agents avancés, recherches illimitées et support prioritaire</div>
        <button class="stButton" style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #0f172a; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 700; font-size: 0.85rem; cursor: pointer; width: 100%; transition: all 0.3s ease;">
            Passer à Pro →
        </button>
    </div>
    """,
        unsafe_allow_html=True,
    )

# === MAIN CONTENT ===

# Chat History ou Welcome
if st.session_state.demo_history:
    # Afficher l'historique des conversations
    for msg in st.session_state.demo_history:
        with st.chat_message(
            msg["role"], avatar="🪖" if msg["role"] == "assistant" else "👤"
        ):
            if msg["role"] == "assistant" and msg.get("type") == "results":
                display_job_results(msg["content"])
            else:
                st.markdown(msg["content"])

    # Input de chat en bas
    user_input = st.chat_input("Décrivez votre recherche d'emploi idéale...")
    if user_input:
        # Ajouter le message utilisateur
        st.session_state.demo_history.append({"role": "user", "content": user_input})

        # Simuler la réponse de l'assistant
        with st.chat_message("assistant", avatar="🪖"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "🔍 **Recherche en cours...** Analyse des offres et calcul de compatibilité"
            )

            # Simuler la recherche
            results = simulate_search(user_input)

            status_placeholder.empty()
            st.session_state.demo_history.append(
                {"role": "assistant", "type": "results", "content": results}
            )

        st.rerun()

else:
    # Écran d'accueil
    st.markdown(
        """
    <div class="hero-container">
        <div class="hero-icon">🪖</div>
        <h1 class="hero-title">GoldArmy Agent</h1>
        <p class="hero-subtitle">
            Votre assistant IA spécialisé dans la recherche d'emploi.<br>
            Analysez votre CV, trouvez des opportunités et postulez intelligemment.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Container de recherche principal
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="search-container">', unsafe_allow_html=True)

            with st.form("demo_search"):
                query = st.text_input(
                    "",
                    placeholder="Ex: Développeur Python à Montréal, Stage informatique...",
                    label_visibility="collapsed",
                )

                # Upload de fichier et bouton submit
                subcol1, subcol2 = st.columns([3, 1])
                with subcol1:
                    uploaded_file = st.file_uploader(
                        "📎 Joindre votre CV (Démo)",
                        type=["pdf", "docx", "txt"],
                        label_visibility="visible",
                    )
                with subcol2:
                    submitted = st.form_submit_button(
                        "🚀 Rechercher", use_container_width=True
                    )

                if submitted and query:
                    # Ajouter à l'historique et déclencher la recherche
                    st.session_state.demo_history.append(
                        {"role": "user", "content": query}
                    )

                    with st.spinner("Recherche en cours..."):
                        results = simulate_search(query)
                        st.session_state.demo_history.append(
                            {"role": "assistant", "type": "results", "content": results}
                        )

                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # Exemples de templates
    st.markdown(
        """
    <div style="text-align: center; margin: 4rem 0 2rem 0;">
        <h3 style="color: #cbd5e1; font-weight: 600;">💡 Exemples de recherches</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Grille de templates
    col1, col2, col3 = st.columns(3)

    templates = [
        {
            "title": "🎓 Stage étudiant",
            "desc": "Recherche de stages pour étudiants en informatique, ingénierie, marketing...",
            "query": "stage informatique Québec",
        },
        {
            "title": "💼 Premier emploi",
            "desc": "Opportunités pour jeunes diplômés dans différents domaines",
            "query": "développeur junior Montréal",
        },
        {
            "title": "🚀 Emploi senior",
            "desc": "Postes à responsabilités pour profils expérimentés",
            "query": "chef de projet senior Toronto",
        },
    ]

    for i, (col, template) in enumerate(zip([col1, col2, col3], templates)):
        with col:
            with st.container():
                st.markdown(
                    f"""
                <div class="glass-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <h4 style="color: #e2e8f0; font-weight: 600; margin-bottom: 0.5rem;">{template["title"]}</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.4; margin: 0;">{template["desc"]}</p>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    f"Essayer →", key=f"template_{i}", use_container_width=True
                ):
                    st.session_state.demo_history.append(
                        {"role": "user", "content": template["query"]}
                    )

                    with st.spinner("Recherche en cours..."):
                        results = simulate_search(template["query"])
                        st.session_state.demo_history.append(
                            {"role": "assistant", "type": "results", "content": results}
                        )

                    st.rerun()

# Footer
st.markdown(
    """
<div style="text-align: center; padding: 2rem; color: #64748b; font-size: 0.8rem;">
    🪖 GoldArmy Agent • Powered by AI • Version Démo
</div>
""",
    unsafe_allow_html=True,
)
