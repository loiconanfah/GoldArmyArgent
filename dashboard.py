import asyncio
import time
import textwrap

import streamlit as st
import streamlit.components.v1 as components
from loguru import logger

# Imports directs
try:
    import docx
    import pypdf
except ImportError:
    import subprocess

    subprocess.check_call(["pip", "install", "pypdf", "python-docx"])
    import docx
    import pypdf

from agents.job_searcher import JobSearchAgent
from core.orchestrator import Orchestrator

# --- Config ---
st.set_page_config(
    page_title="GoldArmy Agent",
    page_icon="🪖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Complete CSS Design ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* === GLOBAL RESET & VARIABLES === */
    :root {
        --primary: #f59e0b;
        --primary-gradient: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.5);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        --text-main: #0f172a;
        --text-secondary: #64748b;
    }

    html, body, [class*="css"], .stChatMessage, .stMarkdown {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        background-color: #f0f4f8 !important; /* Slightly darker for contrast */
        color: var(--text-main) !important;
    }

    /* Remove Streamlit branding */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}

    /* === ANIMATED BACKGROUND === */
    .stApp {
        background-image: 
            radial-gradient(at 0% 0%, rgba(251, 191, 36, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(244, 63, 94, 0.1) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* === GLASSMORPHISM JOBS === */
    .job-card-glass {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.05),
            0 2px 4px -1px rgba(0, 0, 0, 0.03),
            inset 0 0 0 1px rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .job-card-glass:hover {
        transform: translateY(-4px) scale(1.005);
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
        background: rgba(255, 255, 255, 0.95);
        border-color: rgba(251, 191, 36, 0.3);
    }

    .job-card-glass::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .job-card-glass:hover::before {
        opacity: 1;
    }

    /* === TYPOGRAPHY & ELEMENTS === */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }

    .job-role {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 8px 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .job-meta {
        display: flex;
        gap: 16px;
        font-size: 0.95rem;
        color: #64748b;
        align-items: center;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* === MATCH SCORE === */
    .match-ring {
        position: relative;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: conic-gradient(var(--score-color) var(--score-percent), #e2e8f0 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    .match-ring::after {
        content: attr(data-score);
        position: absolute;
        width: 38px;
        height: 38px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.85rem;
        color: #334155;
    }

    /* === JUSTIFICATION BOX === */
    .ai-insight {
        background: linear-gradient(to right, #fffbeb, #fef3c7);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        border-left: 4px solid #f59e0b;
        font-size: 0.95rem;
        color: #4b5563;
        line-height: 1.6;
    }

    .ai-insight strong {
        color: #d97706;
        display: block;
        margin-bottom: 4px;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* === TAGS === */
    .skill-tag {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #e2e8f0;
    }

    /* === BUTTONS === */
    .action-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #0f172a;
        color: white !important;
        padding: 10px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .action-btn:hover {
        background: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-decoration: none;
    }

    .details-btn {
        background: white;
        border: 1px solid #e2e8f0;
        color: #64748b !important;
    }

    .details-btn:hover {
        background: #f8fafc;
        color: #334155 !important;
        border-color: #cbd5e1;
    }

    /* === HERO SECTION === */
    .hero-container {
        text-align: center;
        padding: 5rem 2rem;
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 32px;
        margin-bottom: 3rem;
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.05);
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        letter-spacing: -0.05em;
    }

    /* === SIDEBAR & INPUTS (Retained & Refined) === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        transition: all 0.2s !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #fbbf24 !important;
        box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.15) !important;
    }

    .css-1d391kg {background: #f8fafc;} /* Sidebar bg */
</style>
""",
    unsafe_allow_html=True,
)

# --- State ---
if "history" not in st.session_state:
    st.session_state.history = []
if "agent" not in st.session_state:
    st.session_state.agent = None


async def init_agent():
    if not st.session_state.agent:
        orchestrator = Orchestrator()
        agent = await orchestrator._get_or_create_agent("job_searcher")
        await agent.initialize()
        st.session_state.agent = agent

# --- SEARCH FUNCTION DEFINED EARLY ---
async def run_job_search(query, cv_file, num_results=10):
    await init_agent()

    # 1. Parse Query
    keywords = query
    loc = "Québec, QC"  # Default
    if " à " in query:
        parts = query.split(" à ")
        keywords = parts[0]
        loc = parts[1]

    # 2. Extract CV
    cv_text = ""
    if cv_file:
        try:
            if cv_file.name.endswith(".pdf"):
                pdf = pypdf.PdfReader(cv_file)
                cv_text = "\n".join([p.extract_text() for p in pdf.pages])
            elif cv_file.name.endswith(".docx"):
                doc = docx.Document(cv_file)
                cv_text = "\n".join([p.text for p in doc.paragraphs])
            else:
                cv_text = cv_file.getvalue().decode()
        except:
            pass

    # 3. Add User Message to History
    st.session_state.history.append({"role": "user", "content": query})

    # 4. Processing
    with st.chat_message("assistant", avatar="🪖"):
        status_ph = st.empty()
        status_ph.markdown(
            f"🔍 **Analyse en cours ({num_results} résultats demandés)...**"
        )

        task = {
            "id": f"search_{int(time.time())}",
            "description": f"{keywords} à {loc}",
            "filters": {"keywords": keywords.split(), "location": loc, "limit": num_results},
            "cv_text": cv_text,
        }

        # Execute Real Search
        res = await st.session_state.agent.execute_task(task)

        if res.get("success"):
            jobs = res.get("matched_jobs", [])[:num_results] # Limit results

            status_ph.empty()

            # --- HEADER ---
            st.markdown(textwrap.dedent(f"""
            <div style='margin: 10px 0 24px 0;'>
                <h2 style='margin: 0 0 6px 0; color: #0f172a;'>🎯 {len(jobs)} opportunités trouvées</h2>
                <div style='color: #64748b; font-weight: 500;'>
                    <span style='color: #f59e0b; font-weight: 700;'>{keywords}</span>
                    <span style='opacity: 0.6;'>•</span>
                    <span>{loc}</span>
                </div>
            </div>
            """), unsafe_allow_html=True)

            # --- RESULTS LOOP (NATIVE STREAMLIT) ---
            # This replaces the iframe method to allow native buttons
            
            for i, job in enumerate(jobs):
                # Data Prep
                score = int(job.get("match_score", 0) or 0)
                if score >= 80:
                    score_color = "#10b981"; score_text = "Excellent"
                elif score >= 60:
                    score_color = "#f59e0b"; score_text = "Bon"
                else:
                    score_color = "#ef4444"; score_text = "Moyen"

                matched_skills = job.get("matched_skills", []) or []
                skills_html = "".join([f"<span class='skill-tag'>{s}</span>" for s in matched_skills[:5]]) if matched_skills else "<span class='skill-tag' style='opacity:0.6'>N/A</span>"

                title = job.get("title") or "Titre non disponible"
                company = job.get("company") or "Entreprise confidentielle"
                source = job.get("source") or "Web"
                url = job.get("url") or "#"
                desc = job.get("description", "")
                
                # --- CARD CONTAINER ---
                with st.container():
                    # Card styling wrapper (visual only)
                    # Card styling wrapper (visual only)
                    # Removing blank lines to prevent Markdown block breakage
                    st.markdown(textwrap.dedent(f"""
                    <div class='job-card-glass' style='border-left: 4px solid {score_color};'>
                        <div class='card-header'>
                            <div>
                                <h3 class='job-role' style='margin:0;'>{title}</h3>
                                <div class='job-meta' style='margin-top:5px;'>
                                    <span class='meta-item'>🏢 {company}</span>
                                    <span class='meta-item'>📍 {job.get('location', 'Localisation non spécifiée')}</span>
                                    <span class='meta-item'>🌍 {source}</span>
                                </div>
                            </div>
                            <div class='score-badge' style='background: {score_color}15; color: {score_color}; border-color: {score_color}; min-width: 60px; text-align: center;'>
                                {score}%
                            </div>
                        </div>
                        <div class='ai-insight' style='margin-top:15px;'>
                            <strong>🤖 {score_text} Match</strong><br>
                            {job.get("match_justification", "Analyse en cours...")}
                        </div>
                        <div style='margin: 15px 0;'>
                            <div style='font-size: 0.8rem; color: #64748b; font-weight: 700; margin-bottom: 5px; text-transform: uppercase;'>Compétences Clés</div>
                            {skills_html}
                        </div>
                    </div>
                    """), unsafe_allow_html=True)
                    
                    with st.expander("📄 Voir la description complète"):
                        st.markdown(desc if desc else "_Aucune description détaillée disponible._")
                    
                    # --- ACTION BUTTONS (NATIVE) ---
                    # Placed nicely below the card content
                    col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
                    
                    with col_act1:
                        # Link to Job
                        st.link_button("🚀 Voir l'offre", url)
                        
                    with col_act2:
                        # ADAPT CV ACTION
                        # Using a callback with args to handle the state update
                        def adapt_cv_action(j=job, c=cv_text):
                            if not c:
                                st.error("Veuillez d'abord importer un CV !")
                                return
                            
                            # Show spinner toast
                            with st.spinner(f"Adaptation du CV pour {j['company']}..."):
                                # Call Agent Logic (Synchronously for now, or via async helper)
                                try:
                                    import asyncio
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    new_cv = loop.run_until_complete(st.session_state.agent.adapt_cv(c, j.get("description", "") or j.get("snippet", "")))
                                    loop.close()
                                    
                                    # Save to Session State
                                    st.session_state.adapted_cvs.append({
                                        "company": j.get("company"),
                                        "job_title": j.get("title"),
                                        "cv_content": new_cv,
                                        "date": time.strftime("%Y-%m-%d %H:%M")
                                    })
                                    st.toast(f"✅ CV adapté pour {j['company']} créé!", icon="🎉")
                                except Exception as e:
                                    st.error(f"Erreur: {e}")

                        st.button(f"⚡ Adapter CV", key=f"btn_adapt_{i}", on_click=adapt_cv_action, help="Génère une version de ton CV optimisée pour cette offre spécifique")
                        
                    with col_act3:
                        # WRITE EMAIL ACTION
                        def write_email_action(j=job):
                            st.session_state.email_job = j
                            # Note: Switching tabs programmatically in vanilla Streamlit is tricky without reruns or extra components.
                            # We rely on the user clicking the tab, but we set the state so it's ready.
                            st.toast(f"✅ Offre '{j['title']}' sélectionnée pour rédaction! Va dans l'onglet '📧 Envoi d'Emails'", icon="📨")
                            
                        st.button(f"✉️ Rédiger", key=f"btn_email_{i}", on_click=write_email_action)

            st.session_state.history.append(
                {"role": "assistant", "content": f"✅ {len(jobs)} résultats affichés.", "format": "text"}
            )
            # No rerun needed here, we just rendered the UI
            
        else:
            status_ph.error(f"❌ Erreur: {res.get('error')}")


# --- Sidebar ---
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
        st.session_state.history = []
        st.session_state.trigger_search = None
        st.rerun()

    # Persistent CV Upload
    st.markdown("### 📁 Votre Profil")
    cv_file = st.file_uploader(
        "Importer votre CV (PDF/DOCX)",
        type=["pdf", "docx", "txt"],
        key="sidebar_cv_uploader"
    )
    if cv_file:
        st.success("✅ CV chargé")

    # --- Configuration Avancée ---
    with st.expander("⚙️ Configuration", expanded=True):
        nb_results = st.slider("Nombre de résultats", min_value=5, max_value=50, value=20, step=5)
        
    # Navigation Menu
    st.markdown(
        """
    <div class="menu-section">
        <div class="menu-title">🎛️ Agents</div>
        <div class="menu-item active">🪖 Job Searcher</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --- PDF Generation Helper ---
def create_pdf(text):
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            # Logo or Title
            self.set_font('Helvetica', 'B', 12)
            self.cell(0, 10, 'GoldArmy Agent - CV Adapté', 0, 1, 'R')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Robust Encoding Helper
    def safe_encode(s):
        return s.encode('latin-1', 'replace').decode('latin-1')
    
    # Simple Markdown-ish parsing
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        # Use multi_cell for everything to prevent "Not enough space" error on long lines
        if line.startswith('# '):
            pdf.set_font("Helvetica", 'B', 16)
            pdf.multi_cell(0, 10, safe_encode(line[2:]))
            pdf.ln(2)
        elif line.startswith('## '):
            pdf.set_font("Helvetica", 'B', 14)
            pdf.multi_cell(0, 10, safe_encode(line[3:]))
            pdf.ln(1)
        elif line.startswith('### '):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.multi_cell(0, 8, safe_encode(line[4:]))
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font("Helvetica", '', 11)
            pdf.set_x(15) # Indent
            # Bullet point simulation
            pdf.multi_cell(0, 6, chr(149) + " " + safe_encode(line[2:]))
        else:
            pdf.set_font("Helvetica", '', 11)
            pdf.multi_cell(0, 6, safe_encode(line))
            
    return pdf.output(dest='S').encode('latin-1', errors='replace') # basic encoding for now

# --- EMAIL GENERATION HELPER ---
def generate_mailto_link(to, subject, body):
    import urllib.parse
    subject_enc = urllib.parse.quote(subject)
    body_enc = urllib.parse.quote(body)
    return f"mailto:{to}?subject={subject_enc}&body={body_enc}"

# --- Main Content ---

tab_search, tab_cvs, tab_emails = st.tabs(["🔍 Recherche d'Emploi", "📝 Mes CVs Adaptés", "📧 Envoi d'Emails"])

with tab_search:
    # Handle auto-trigger from suggestions
    if st.session_state.get("trigger_search"):
        query = st.session_state.trigger_search
        st.session_state.trigger_search = None # Reset
        asyncio.run(run_job_search(query, cv_file, nb_results))

    if st.session_state.history:
        # Display chat history
        for idx, msg in enumerate(st.session_state.history):
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            elif msg["role"] == "assistant":
                if msg.get("format") == "html_component":
                    # Use unique key for iframe to avoid reload issues
                    components.html(msg["content"], height=1400, scrolling=True)
                else:
                    with st.chat_message("assistant", avatar="🪖"):
                        st.markdown(msg["content"])
    else:
        # WELCOME SCREEN (When history is empty)
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

        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, rgba(251, 191, 36, 0.05), rgba(245, 158, 11, 0.02)); border-radius: 16px; border: 1px solid rgba(251, 191, 36, 0.1);">
            <h3 style="color: #0f172a; font-weight: 700; font-size: 1.3rem;">💡 Suggestions</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Template Grid
        col1, col2, col3 = st.columns(3)
        
        # Callback safe function
        def set_search(q):
            st.session_state.trigger_search = q
        
        with col1:
             st.button("🎯 Compétences", on_click=set_search, args=("Analyser mes compétences CV",), use_container_width=True)
        with col2:
             st.button("🎓 Stage Informatique", on_click=set_search, args=("Stage en informatique (Développement, IA, Data)",), use_container_width=True)
        with col3:
             st.button("🏢 Emploi Junior", on_click=set_search, args=("Emploi Junior Informatique",), use_container_width=True)

    # Chat input (Always visible at bottom)
    if prompt := st.chat_input("Ex: Développeur Python à Québec..."):
        # Run search asynchronously
        asyncio.run(run_job_search(prompt, cv_file, nb_results))

with tab_cvs:
    st.header("📝 Mes CVs et Candidatures")
    
    # Placeholder for CV Management Logic
    if "adapted_cvs" not in st.session_state:
        st.session_state.adapted_cvs = []
        
    if not st.session_state.adapted_cvs:
        st.info("Aucun CV adapté pour le moment. Lancez une recherche et cliquez sur '⚡ Adapter CV' !")
    else:
        for idx, item in enumerate(st.session_state.adapted_cvs):
            with st.expander(f"📄 {item['job_title']} - {item['company']} ({item['date']})"):
                st.markdown(item['cv_content'])
                
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "📄 Télécharger (.md)", 
                        item['cv_content'], 
                        file_name=f"CV_{item['company']}.md",
                        key=f"dl_md_{idx}"
                    )
                with col_dl2:
                    try:
                        pdf_bytes = create_pdf(item['cv_content'])
                        st.download_button(
                            "📕 Télécharger (.pdf)", 
                            pdf_bytes, 
                            file_name=f"CV_{item['company']}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{idx}"
                        )
                    except Exception as e:
                        st.error(f"Erreur PDF: {e}")

with tab_emails:
    st.header("📧 Envoi d'Emails")
    
    # State for selected job to email
    if "email_job" not in st.session_state:
        st.session_state.email_job = None
        
    if st.session_state.email_job:
        job = st.session_state.email_job
        st.success(f"📮 Rédaction pour : **{job.get('title')}** chez *{job.get('company')}*")
        
        col_type, col_recipient = st.columns([1, 2])
        with col_type:
            app_type = st.radio("Type de candidature", ["Stage", "Emploi"], index=1 if "senior" in job.get('title', '').lower() else 0)
        
        with col_recipient:
            # Try to pre-fill from contact extraction
            contact_info = st.session_state.agent._extract_contact_info(job.get('description', ''))
            recipient_email = st.text_input("Destinataire (Email)", value=contact_info.get("email", ""))
        
        if st.button("✨ Générer le brouillon", disabled=False):
            if not cv_text:
                st.warning("⚠️ Attention: Aucun CV chargé, la signature sera générique.")
                
            with st.spinner("Rédaction de l'email en cours..."):
                # Run sync for now
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Parse CV profile lightly or use stored one
                cv_profile = {"skills": [], "experience_years": 0} # Default dummy
                if cv_text:
                     cv_profile = loop.run_until_complete(st.session_state.agent._analyze_cv(cv_text))
                
                email_draft = loop.run_until_complete(st.session_state.agent.generate_application_email(job, cv_profile, app_type.lower()))
                loop.close()
                
                st.session_state.current_email_draft = email_draft
                st.rerun()
                
        if "current_email_draft" in st.session_state:
            draft = st.session_state.current_email_draft
            
            st.markdown("---")
            subject = st.text_input("Sujet", value=draft.get("subject", ""))
            body = st.text_area("Corps du message", value=draft.get("body", ""), height=300)
            
            # MAILTO LINK
            if recipient_email:
                link = generate_mailto_link(recipient_email, subject, body)
                st.markdown(f"""
                <a href="{link}" target="_blank" class="action-btn" style="background: #ef4444; text-decoration: none; display: inline-block; text-align: center;">
                    📧 Ouvrir dans mon client Mail
                </a>
                """, unsafe_allow_html=True)
            else:
                st.warning("Veuillez entrer une adresse email destinataire pour générer le lien d'envoi.")
                
    else:
        st.info("👈 Sélectionnez une offre dans l'onglet 'Recherche' et cliquez sur '✉️ Rédiger' pour commencer.")
