"""
Application Streamlit - Plateforme de Gestion des Emplois du Temps d'Examens
Version Professionnelle Sans Emojis
"""

import streamlit as st
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from config import streamlit_config, db_config
from database import Database, test_connection

st.set_page_config(
    page_title=streamlit_config.PAGE_TITLE,
    page_icon="📚",
    layout=streamlit_config.LAYOUT,
    initial_sidebar_state=streamlit_config.INITIAL_SIDEBAR_STATE
)

st.markdown("""
<style>
    .main {
        padding: 1.5rem;
    }
    
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem 2.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .info-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        border-left: 3px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    .info-card h3 {
        margin: 0 0 0.75rem 0;
        color: #1e3c72;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .info-card p {
        margin: 0;
        color: #5a6c7d;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .connection-status {
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin: 0.75rem 0;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .connection-success {
        background-color: #d4edda;
        border-left: 3px solid #28a745;
        color: #155724;
    }
    
    .connection-error {
        background-color: #f8d7da;
        border-left: 3px solid #dc3545;
        color: #721c24;
    }
    
    .sidebar .element-container {
        margin-bottom: 0.5rem;
    }
    
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'current_year' not in st.session_state:
    st.session_state.current_year = "2024-2025"

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 2px solid #e0e0e0; margin-bottom: 1.5rem;">
        <h2 style="margin: 0; color: #1e3c72; font-size: 1.5rem;">Num Exam</h2>
        <p style="margin: 0.25rem 0 0 0; color: #6c757d; font-size: 0.8rem;">Gestion des Examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Authentification")
    
    role = st.selectbox(
        "Sélectionnez votre rôle",
        ["Doyen/Vice-doyen", "Administrateur Examens", "Chef de Département", "Étudiant", "Professeur"],
        key="user_role_select"
    )
    
    st.session_state.user_role = role
    
    st.markdown("---")
    
    st.subheader("Année Académique")
    annee = st.selectbox(
        "Année",
        ["2024-2025", "2025-2026", "2023-2024"],
        key="academic_year"
    )
    st.session_state.current_year = annee
    
    st.markdown("---")
    
    st.subheader("Base de Données")
    
    if st.button("Tester la connexion", key="test_db", use_container_width=True):
        with st.spinner("Test en cours..."):
            if test_connection(db_config.DB_CONFIG):
                st.session_state.db_connected = True
                st.success("Connexion établie")
            else:
                st.session_state.db_connected = False
                st.error("Connexion échouée")
    
    if st.session_state.db_connected:
        st.markdown('<div class="connection-status connection-success">Statut : Connecté</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="connection-status connection-error">Statut : Déconnecté</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.caption("Version 1.0.0")
    st.caption("Faculté des Sciences")
    st.caption("Université M'Hamed Bougara")

st.markdown("""
<div class="app-header">
    <h1>Plateforme de Gestion des Emplois du Temps d'Examens</h1>
    <p>Système intelligent d'optimisation et de planification des examens universitaires</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"### Bienvenue, **{role}**")
st.markdown(f"**Année académique :** {annee}")

st.markdown("---")

if role == "Doyen/Vice-doyen":
    st.markdown("## Vue Stratégique Globale")
    
    st.info("Accédez au dashboard complet via le menu : **Pages** > **Dashboard Doyen**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">1,470</div>
            <div class="metric-label">Modules</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">13,000</div>
            <div class="metric-label">Étudiants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">310</div>
            <div class="metric-label">Professeurs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">136</div>
            <div class="metric-label">Salles</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Accès Rapides")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>Statistiques Globales</h3>
            <p>Consultez les indicateurs de performance et l'occupation des ressources</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accéder au Dashboard", key="go_doyen", use_container_width=True):
            st.info("Utilisez le menu : Pages > Dashboard Doyen")
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>Validation Finale</h3>
            <p>Validez les emplois du temps après vérification des départements</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Valider les Plannings", key="validate_doyen", use_container_width=True):
            st.info("Utilisez le menu : Pages > Dashboard Doyen")

elif role == "Administrateur Examens":
    st.markdown("## Administration des Examens")
    
    st.info("Accédez au panneau d'administration via : **Pages** > **Admin Examens**")
    
    st.markdown("### Actions Principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>Génération Automatique</h3>
            <p>Générez l'emploi du temps complet en moins de 45 secondes</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Générer l'EDT", key="generate_admin", type="primary", use_container_width=True):
            st.info("Accédez à : Pages > Admin Examens > Génération EDT")
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>Détection de Conflits</h3>
            <p>Analysez et résolvez les conflits dans le planning</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Détecter les Conflits", key="conflicts_admin", use_container_width=True):
            st.info("Accédez à : Pages > Admin Examens > Détection Conflits")
    
    st.markdown("---")
    
    st.markdown("### Statistiques Rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Examens planifiés", "0", "À générer")
    
    with col2:
        st.metric("Salles disponibles", "136")
    
    with col3:
        st.metric("Conflits détectés", "0")
    
    with col4:
        st.metric("Taux de réussite", "0%")

elif role == "Chef de Département":
    st.markdown("## Dashboard Chef de Département")
    
    st.info("Accédez à votre dashboard via : **Pages** > **Chef Département**")
    
    departement = st.selectbox(
        "Sélectionnez votre département",
        ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Génie Civil", "Électronique"]
    )
    
    st.markdown(f"### Vue d'ensemble - {departement}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Examens", "210")
    
    with col2:
        st.metric("Étudiants", "1,850")
    
    with col3:
        st.metric("Conflits", "0")
    
    st.markdown("---")
    
    if st.button("Voir le Dashboard Complet", type="primary", use_container_width=True):
        st.info("Accédez à : Pages > Chef Département")

elif role == "Étudiant":
    st.markdown("## Espace Étudiant")
    
    st.info("Consultez votre emploi du temps via : **Pages** > **Consultation**")
    
    matricule = st.text_input("Entrez votre matricule", placeholder="Ex: E202400001")
    
    if st.button("Voir mon Emploi du Temps", type="primary", use_container_width=True):
        if matricule:
            st.info("Accédez à : Pages > Consultation > Étudiants")
        else:
            st.warning("Veuillez entrer votre matricule")
    
    st.markdown("---")
    
    st.markdown("### Vos Prochains Examens")
    
    st.info("Aucun examen planifié pour le moment. L'emploi du temps sera disponible une fois généré par l'administration.")

elif role == "Professeur":
    st.markdown("## Espace Professeur")
    
    st.info("Consultez vos surveillances via : **Pages** > **Consultation**")
    
    matricule = st.text_input("Entrez votre matricule", placeholder="Ex: P10001")
    
    if st.button("Voir mes Surveillances", type="primary", use_container_width=True):
        if matricule:
            st.info("Accédez à : Pages > Consultation > Professeurs")
        else:
            st.warning("Veuillez entrer votre matricule")
    
    st.markdown("---")
    
    st.markdown("### Vos Prochaines Surveillances")
    
    st.info("Aucune surveillance planifiée pour le moment. Les surveillances seront assignées une fois l'emploi du temps généré.")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Documentation**")
    st.markdown("Guide utilisateur")
    st.markdown("FAQ")

with col2:
    st.markdown("**Support**")
    st.markdown("Signaler un problème")
    st.markdown("Demande d'aide")

with col3:
    st.markdown("**À propos**")
    st.markdown("Version 1.0.0")
    st.markdown("© 2025 Num Exam")

with st.expander("Comment utiliser la plateforme"):
    st.markdown("""
    ### Guide de Navigation
    
    **1. Sélectionnez votre rôle** dans la barre latérale
    
    **2. Choisissez l'année académique**
    
    **3. Accédez aux pages** via le menu **Pages** en haut à gauche
    
    ### Pages Disponibles
    
    - **Dashboard Doyen** : Vue stratégique globale, KPIs, validation finale
    - **Admin Examens** : Génération EDT, détection conflits, optimisation
    - **Chef Département** : Statistiques par département, validation locale
    - **Consultation** : Emplois du temps personnalisés
    - **Visualisation Planning** : Affichage professionnel type université
    
    ### Workflow
    
    1. **Admin** génère l'emploi du temps automatiquement
    2. **Admin** détecte et corrige les conflits
    3. **Chefs de département** valident leurs plannings
    4. **Doyen** valide le planning global
    5. **Étudiants/Profs** consultent leurs emplois du temps
    """)

st.markdown("---")
st.caption("Développé avec Streamlit | PostgreSQL | Python")