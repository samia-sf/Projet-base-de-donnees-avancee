"""
Application Streamlit - Plateforme d'Optimisation des Emplois du Temps d'Examens
Page principale avec navigation
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from config import streamlit_config, db_config
from database import Database, test_connection

# ============================================
# CONFIGURATION DE LA PAGE
# ============================================

st.set_page_config(
    page_title=streamlit_config.PAGE_TITLE,
    page_icon=streamlit_config.PAGE_ICON,
    layout=streamlit_config.LAYOUT,
    initial_sidebar_state=streamlit_config.INITIAL_SIDEBAR_STATE
)

# ============================================
# STYLE CSS PERSONNALISÉ
# ============================================

st.markdown("""
<style>
    /* Style général */
    .main {
        padding: 2rem;
    }
    
    /* Cartes de statistiques */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Boutons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
    }
    
    /* Alertes */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ÉTAT DE SESSION
# ============================================

if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'current_year' not in st.session_state:
    st.session_state.current_year = "2024-2025"

# ============================================
# SIDEBAR - NAVIGATION
# ============================================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=Num_Exam", use_container_width=True)
    
    st.markdown("---")
    
    # Sélection du rôle (simulation authentification)
    st.subheader("👤 Authentification")
    
    role = st.selectbox(
        "Sélectionnez votre rôle",
        ["Doyen/Vice-doyen", "Administrateur Examens", "Chef de Département", "Étudiant", "Professeur"],
        key="user_role_select"
    )
    
    st.session_state.user_role = role
    
    st.markdown("---")
    
    # Année académique
    st.subheader("📅 Année Académique")
    annee = st.selectbox(
        "Année",
        ["2024-2025", "2023-2024", "2025-2026"],
        key="academic_year"
    )
    st.session_state.current_year = annee
    
    st.markdown("---")
    
    # Test de connexion BD
    st.subheader("🔌 Statut Base de Données")
    
    if st.button("Tester la connexion", key="test_db"):
        with st.spinner("Test en cours..."):
            if test_connection(db_config.DB_CONFIG):
                st.session_state.db_connected = True
                st.success("✅ Connecté")
            else:
                st.session_state.db_connected = False
                st.error("❌ Déconnecté")
    
    if st.session_state.db_connected:
        st.success("✅ Base de données connectée")
    else:
        st.warning("⚠️ Non connecté à la BD")
    
    st.markdown("---")
    
    # Informations
    st.caption("📚 Plateforme Num_Exam v1.0")
    st.caption("🏫 Faculté des Sciences")
    st.caption("📧 support@num-exam.dz")

# ============================================
# PAGE PRINCIPALE
# ============================================

# Header
st.markdown("""
<div class="app-header">
    <h1>📚 Num_Exam</h1>
    <p>Plateforme d'Optimisation des Emplois du Temps d'Examens</p>
</div>
""", unsafe_allow_html=True)

# Message de bienvenue personnalisé
st.markdown(f"### 👋 Bienvenue, **{role}**")
st.markdown(f"**Année académique :** {annee}")

st.markdown("---")

# ============================================
# CONTENU SELON LE RÔLE
# ============================================

if role == "Doyen/Vice-doyen":
    st.header("🏛️ Dashboard Doyen")
    st.info("👈 Accédez au dashboard complet via le menu latéral : **Pages** → **Dashboard Doyen**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>1,470</h3>
            <p>📖 Modules</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>13,000</h3>
            <p>👨‍🎓 Étudiants</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>310</h3>
            <p>👨‍🏫 Professeurs</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Accès Rapides")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**📈 Statistiques Globales**\n\nVue d'ensemble de tous les départements")
        if st.button("Voir les statistiques", key="stats_doyen"):
            st.info("Allez dans : Pages → Dashboard Doyen")
    
    with col2:
        st.info("**✅ Validation des Plannings**\n\nValidez les emplois du temps par département")
        if st.button("Valider les plannings", key="validate_doyen"):
            st.info("Allez dans : Pages → Dashboard Doyen")

elif role == "Administrateur Examens":
    st.header("👨‍💼 Administration des Examens")
    st.info("👈 Accédez au panneau d'administration via : **Pages** → **Admin Examens**")
    
    st.markdown("### ⚡ Actions Rapides")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**🚀 Génération Automatique**\n\nGénérez l'emploi du temps complet en < 45 secondes")
        if st.button("Générer l'EDT", key="generate_admin", type="primary"):
            st.info("Allez dans : Pages → Admin Examens → Génération EDT")
    
    with col2:
        st.warning("**🔍 Détection de Conflits**\n\nAnalysez et résolvez les conflits du planning")
        if st.button("Détecter les conflits", key="conflicts_admin"):
            st.info("Allez dans : Pages → Admin Examens → Détection Conflits")
    
    st.markdown("---")
    
    st.markdown("### 📊 Statistiques Rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Examens planifiés", "0", "À générer")
    
    with col2:
        st.metric("Salles disponibles", "136", "")
    
    with col3:
        st.metric("Conflits détectés", "0", "")
    
    with col4:
        st.metric("Taux de réussite", "0%", "")

elif role == "Chef de Département":
    st.header("📊 Dashboard Chef de Département")
    st.info("👈 Accédez à votre dashboard via : **Pages** → **Chef Département**")
    
    # Sélection du département
    departement = st.selectbox(
        "Sélectionnez votre département",
        ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Génie Civil", "Électronique"]
    )
    
    st.markdown(f"### 📈 Vue d'ensemble - {departement}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Examens", "210", "+5")
    
    with col2:
        st.metric("Étudiants", "1,850", "")
    
    with col3:
        st.metric("Conflits", "0", "✅")
    
    st.markdown("---")
    
    if st.button("Voir le dashboard complet", type="primary"):
        st.info("Allez dans : Pages → Chef Département")

elif role == "Étudiant":
    st.header("👨‍🎓 Espace Étudiant")
    st.info("👈 Consultez votre emploi du temps via : **Pages** → **Consultation**")
    
    # Simulation recherche
    matricule = st.text_input("Entrez votre matricule", "E202400001")
    
    if st.button("Voir mon emploi du temps", type="primary"):
        st.info("Allez dans : Pages → Consultation → Onglet Étudiants")
    
    st.markdown("---")
    
    st.markdown("### 📅 Vos prochains examens")
    
    st.info("**Aucun examen planifié pour le moment**\n\nL'emploi du temps sera disponible une fois généré par l'administration.")

elif role == "Professeur":
    st.header("👨‍🏫 Espace Professeur")
    st.info("👈 Consultez vos surveillances via : **Pages** → **Consultation**")
    
    # Simulation recherche
    matricule = st.text_input("Entrez votre matricule", "P10001")
    
    if st.button("Voir mes surveillances", type="primary"):
        st.info("Allez dans : Pages → Consultation → Onglet Professeurs")
    
    st.markdown("---")
    
    st.markdown("### 📅 Vos prochaines surveillances")
    
    st.info("**Aucune surveillance planifiée pour le moment**\n\nLes surveillances seront assignées une fois l'emploi du temps généré.")

# ============================================
# FOOTER
# ============================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📚 Documentation**")
    st.markdown("- [Guide utilisateur](#)")
    st.markdown("- [FAQ](#)")

with col2:
    st.markdown("**🔧 Support**")
    st.markdown("- [Signaler un bug](#)")
    st.markdown("- [Demande de fonctionnalité](#)")

with col3:
    st.markdown("**ℹ️ À propos**")
    st.markdown("- Version 1.0.0")
    st.markdown("- © 2025 Num_Exam")

# ============================================
# INSTRUCTIONS DE NAVIGATION
# ============================================

with st.expander("ℹ️ Comment utiliser la plateforme"):
    st.markdown("""
    ### 📖 Guide de Navigation
    
    1. **Sélectionnez votre rôle** dans la barre latérale (Sidebar)
    2. **Choisissez l'année académique** que vous souhaitez consulter
    3. **Accédez aux pages** via le menu **Pages** en haut de la barre latérale
    
    ### 🎯 Pages Disponibles
    
    - **🏛️ Dashboard Doyen** : Vue stratégique globale, KPIs, validation finale
    - **👨‍💼 Admin Examens** : Génération EDT, détection conflits, optimisation
    - **📊 Chef Département** : Statistiques par département, validation
    - **👥 Consultation** : Emplois du temps personnalisés (étudiants/profs)
    
    ### ⚡ Workflow Typique
    
    1. **Admin** génère l'emploi du temps automatiquement
    2. **Admin** détecte et corrige les conflits éventuels
    3. **Chefs de département** valident leurs plannings
    4. **Doyen** valide le planning global
    5. **Étudiants/Profs** consultent leurs emplois du temps
    """)

st.markdown("---")
st.caption("🚀 Développé avec Streamlit | 🐘 PostgreSQL | 🐍 Python")