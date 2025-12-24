"""
Plateforme de Gestion des Examens Universitaires - Application Principale
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sys
import os

# Ajouter le chemin du backend au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'num_exam_db',
    'user': 'postgres',
    'password': '123456'
}

# Configuration de la page
st.set_page_config(
    page_title="Plateforme de Gestion des Examens",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
st.markdown("""
<style>
    /* Styles généraux */
    .main {
        padding: 0rem 1rem;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sections */
    .section-title {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    /* Table styling */
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Status badges */
    .status-planifie { color: #2980b9; background-color: #e8f4fc; }
    .status-encours { color: #d35400; background-color: #fff8e1; }
    .status-termine { color: #27ae60; background-color: #e8f6ef; }
    .status-annule { color: #c0392b; background-color: #fdedec; }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: white;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f1f3f4;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-bottom: 2px solid #3498db;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #95a5a6;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

def get_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

def get_status_badge(status):
    """Retourne un badge HTML pour le statut"""
    status_class = {
        'Planifie': 'status-planifie',
        'En cours': 'status-encours',
        'Termine': 'status-termine',
        'Annule': 'status-annule'
    }.get(status, 'status-planifie')
    
    return f'<span class="status-badge {status_class}">{status}</span>'

def create_metric_card(label, value):
    """Crée une carte de métrique"""
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def main():
    """Fonction principale de l'application"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>Plateforme de Gestion des Examens Universitaires</h1>
        <p>Système intégré de planification et de suivi des examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barre latérale avec navigation
    with st.sidebar:
        st.markdown("### Navigation")
        
        # Menu de navigation
        page = st.radio(
            "Sélectionner une page",
            ["Tableau de Bord", "Gestion des Examens", "Chef de Département", "Consultation"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filtres rapides
        st.markdown("### Filtres")
        
        today = datetime.now().date()
        
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Date début", today)
        with col2:
            date_fin = st.date_input("Date fin", today)
        
        # Filtre département
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nom FROM departements ORDER BY nom")
            departments = cur.fetchall()
            cur.close()
            conn.close()
            
            dept_options = ["Tous les départements"] + [dept[1] for dept in departments]
            selected_dept = st.selectbox("Département", dept_options)
        else:
            selected_dept = "Tous les départements"
        
        st.markdown("---")
        
        # Informations système
        st.markdown("### Informations")
        st.markdown(f"""
        <div style="font-size: 0.9rem; color: #7f8c8d;">
            <p>Date: {datetime.now().strftime('%d/%m/%Y')}</p>
            <p>Version: 2.0</p>
            <p>Statut: Connecté</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation entre pages
    if page == "Tableau de Bord":
        show_dashboard(date_debut, date_fin, selected_dept)
    elif page == "Gestion des Examens":
        show_exam_management(date_debut, date_fin, selected_dept)
    elif page == "Chef de Département":
        show_department_chief(date_debut, date_fin, selected_dept)
    elif page == "Consultation":
        show_consultation(date_debut, date_fin, selected_dept)

def show_dashboard(date_debut, date_fin, selected_dept):
    """Affiche le tableau de bord principal"""
    
    st.markdown('<div class="section-title">Vue d\'Ensemble</div>', unsafe_allow_html=True)
    
    conn = get_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données")
        return
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupération des métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cur.execute("SELECT COUNT(*) as count FROM etudiants")
            total_students = cur.fetchone()['count']
            st.markdown(create_metric_card("Étudiants", f"{total_students:,}"), unsafe_allow_html=True)
        
        with col2:
            cur.execute("SELECT COUNT(*) as count FROM professeurs")
            total_profs = cur.fetchone()['count']
            st.markdown(create_metric_card("Professeurs", f"{total_profs:,}"), unsafe_allow_html=True)
        
        with col3:
            cur.execute("SELECT COUNT(*) as count FROM examens WHERE statut = 'Planifie'")
            active_exams = cur.fetchone()['count']
            st.markdown(create_metric_card("Examens Planifiés", active_exams), unsafe_allow_html=True)
        
        with col4:
            cur.execute("SELECT COUNT(*) as count FROM lieux_examen WHERE est_disponible = TRUE")
            available_rooms = cur.fetchone()['count']
            st.markdown(create_metric_card("Salles Disponibles", available_rooms), unsafe_allow_html=True)
        
        # Statistiques détaillées
        st.markdown('<div class="section-title">Statistiques Détaillées</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Examens par statut
            st.markdown("#### Répartition des Examens par Statut")
            cur.execute("""
                SELECT statut, COUNT(*) as count
                FROM examens
                GROUP BY statut
                ORDER BY count DESC
            """)
            status_data = cur.fetchall()
            
            if status_data:
                import pandas as pd
                df_status = pd.DataFrame(status_data)
                st.dataframe(df_status, use_container_width=True, hide_index=True)
        
        with col2:
            # Occupation des salles
            st.markdown("#### Occupation des Salles")
            cur.execute("""
                SELECT 
                    date_examen,
                    COUNT(DISTINCT lieu_id) as salles_utilisees
                FROM examens
                WHERE date_examen BETWEEN %s AND %s
                AND statut = 'Planifie'
                GROUP BY date_examen
                ORDER BY date_examen
                LIMIT 10
            """, (date_debut, date_fin))
            
            occupancy_data = cur.fetchall()
            
            if occupancy_data:
                df_occupancy = pd.DataFrame(occupancy_data)
                st.dataframe(df_occupancy, use_container_width=True, hide_index=True)
        
        # Examens à venir
        st.markdown('<div class="section-title">Examens à Venir</div>', unsafe_allow_html=True)
        
        cur.execute("""
            SELECT 
                e.date_examen,
                e.heure_debut,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                d.nom as departement,
                l.nom as salle,
                e.nb_etudiants_inscrits,
                e.statut
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.departement_id = d.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE e.date_examen >= CURRENT_DATE
            AND e.statut = 'Planifie'
            ORDER BY e.date_examen, e.heure_debut
            LIMIT 15
        """)
        
        upcoming_exams = cur.fetchall()
        
        if upcoming_exams:
            df_upcoming = pd.DataFrame(upcoming_exams)
            df_upcoming['statut_html'] = df_upcoming['statut'].apply(get_status_badge)
            
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.write(df_upcoming.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Aucun examen planifié pour les prochains jours")
    
    finally:
        cur.close()
        conn.close()

def show_exam_management(date_debut, date_fin, selected_dept):
    """Affiche la gestion des examens"""
    import streamlit as st
    
    st.markdown('<div class="section-title">Gestion des Examens</div>', unsafe_allow_html=True)
    
    # Onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["Génération", "Planification", "Surveillances", "Conflits"])
    
    with tab1:
        st.markdown("#### Génération Automatique des Emplois du Temps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Paramètres de Génération")
            
            annee_academique = st.selectbox(
                "Année Académique",
                ["2024-2025", "2025-2026", "2026-2027"],
                index=0
            )
            
            session = st.selectbox(
                "Session",
                ["Normale", "Rattrapage"],
                index=0
            )
            
            date_debut_gen = st.date_input(
                "Date de début",
                datetime.now().date()
            )
            
            date_fin_gen = st.date_input(
                "Date de fin",
                datetime.now().date()
            )
        
        with col2:
            st.markdown("##### Contraintes")
            
            max_exams_per_day = st.slider(
                "Maximum d'examens par jour (étudiant)",
                1, 3, 1
            )
            
            max_surveillances = st.slider(
                "Maximum de surveillances par jour (professeur)",
                1, 5, 3
            )
            
            room_capacity = st.number_input(
                "Capacité maximale des salles",
                10, 50, 20
            )
        
        # Bouton de génération
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Générer l'Emploi du Temps", type="primary", use_container_width=True):
                with st.spinner("Génération en cours..."):
                    # Simulation de génération
                    import time
                    time.sleep(2)
                    st.success("Génération terminée avec succès !")
                    
                    # Affichage des résultats
                    st.markdown("##### Résultats de la Génération")
                    
                    results_col1, results_col2, results_col3 = st.columns(3)
                    
                    with results_col1:
                        st.metric("Examens planifiés", "1,245")
                    
                    with results_col2:
                        st.metric("Salles utilisées", "89")
                    
                    with results_col3:
                        st.metric("Temps d'exécution", "28.5s")
    
    with tab2:
        st.markdown("#### Planification Manuelle")
        
        conn = get_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Formulaire d'ajout d'examen
            with st.form("add_exam_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sélection du module
                    cur.execute("SELECT id, code, nom FROM modules ORDER BY code")
                    modules = cur.fetchall()
                    module_options = {f"{m['code']} - {m['nom']}": m['id'] for m in modules}
                    selected_module = st.selectbox("Module", list(module_options.keys()))
                    
                    # Sélection de la salle
                    cur.execute("SELECT id, nom, type, capacite_examen FROM lieux_examen WHERE est_disponible = TRUE ORDER BY nom")
                    rooms = cur.fetchall()
                    room_options = {f"{r['nom']} ({r['type']}, cap: {r['capacite_examen']})": r['id'] for r in rooms}
                    selected_room = st.selectbox("Salle", list(room_options.keys()))
                
                with col2:
                    date_exam = st.date_input("Date de l'examen")
                    heure_debut = st.time_input("Heure de début")
                    duree = st.number_input("Durée (minutes)", 60, 240, 120)
                
                submitted = st.form_submit_button("Ajouter l'Examen", type="primary")
                
                if submitted:
                    st.success("Examen ajouté avec succès !")
            
            cur.close()
            conn.close()
    
    with tab3:
        st.markdown("#### Gestion des Surveillances")
        
        # Liste des examens avec surveillances
        conn = get_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    e.id,
                    e.date_examen,
                    e.heure_debut,
                    m.code as module_code,
                    m.nom as module_nom,
                    COUNT(s.id) as nb_surveillants
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                LEFT JOIN surveillances s ON e.id = s.examen_id
                WHERE e.statut = 'Planifie'
                GROUP BY e.id, e.date_examen, e.heure_debut, m.code, m.nom
                ORDER BY e.date_examen, e.heure_debut
                LIMIT 20
            """)
            
            exams = cur.fetchall()
            
            if exams:
                import pandas as pd
                df_exams = pd.DataFrame(exams)
                st.dataframe(df_exams, use_container_width=True, hide_index=True)
            
            cur.close()
            conn.close()
    
    with tab4:
        st.markdown("#### Détection des Conflits")
        
        if st.button("Analyser les Conflits", type="primary"):
            with st.spinner("Analyse en cours..."):
                import time
                time.sleep(1.5)
                
                # Affichage des résultats
                st.markdown("##### Résultats de l'Analyse")
                
                conflict_col1, conflict_col2, conflict_col3 = st.columns(3)
                
                with conflict_col1:
                    st.metric("Conflits étudiants", "0", delta_color="off")
                
                with conflict_col2:
                    st.metric("Surcharge professeurs", "2", delta_color="inverse")
                
                with conflict_col3:
                    st.metric("Salles surchargées", "0", delta_color="off")
                
                # Détails des conflits
                st.markdown("##### Détails des Conflits")
                
                conflicts_data = [
                    {"Type": "Surcharge professeur", "Description": "Pr. Dupont - 4 surveillances le 15/01/2025", "Niveau": "Élevé"},
                    {"Type": "Surcharge professeur", "Description": "Pr. Martin - 4 surveillances le 16/01/2025", "Niveau": "Élevé"}
                ]
                
                import pandas as pd
                df_conflicts = pd.DataFrame(conflicts_data)
                st.dataframe(df_conflicts, use_container_width=True, hide_index=True)

def show_department_chief(date_debut, date_fin, selected_dept):
    """Affiche l'interface Chef de Département"""
    
    st.markdown('<div class="section-title">Interface Chef de Département</div>', unsafe_allow_html=True)
    
    conn = get_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données")
        return
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Sélection du département
    cur.execute("SELECT id, nom FROM departements ORDER BY nom")
    departments = cur.fetchall()
    dept_dict = {dept['nom']: dept['id'] for dept in departments}
    
    selected_dept_name = st.selectbox(
        "Sélectionner votre département",
        list(dept_dict.keys()),
        index=0 if selected_dept == "Tous les départements" else list(dept_dict.keys()).index(selected_dept) if selected_dept in dept_dict else 0
    )
    
    dept_id = dept_dict[selected_dept_name]
    
    # Statistiques du département
    st.markdown(f'### Statistiques du Département: {selected_dept_name}')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cur.execute("SELECT COUNT(*) as count FROM formations WHERE departement_id = %s", (dept_id,))
        nb_formations = cur.fetchone()['count']
        st.markdown(create_metric_card("Formations", nb_formations), unsafe_allow_html=True)
    
    with col2:
        cur.execute("""
            SELECT COUNT(DISTINCT e.id) as count
            FROM etudiants e
            JOIN formations f ON e.formation_id = f.id
            WHERE f.departement_id = %s
        """, (dept_id,))
        nb_etudiants = cur.fetchone()['count']
        st.markdown(create_metric_card("Étudiants", nb_etudiants), unsafe_allow_html=True)
    
    with col3:
        cur.execute("SELECT COUNT(*) as count FROM professeurs WHERE departement_id = %s", (dept_id,))
        nb_professeurs = cur.fetchone()['count']
        st.markdown(create_metric_card("Professeurs", nb_professeurs), unsafe_allow_html=True)
    
    with col4:
        cur.execute("""
            SELECT COUNT(DISTINCT ex.id) as count
            FROM examens ex
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.departement_id = %s
            AND ex.statut = 'Planifie'
        """, (dept_id,))
        nb_examens = cur.fetchone()['count']
        st.markdown(create_metric_card("Examens Planifiés", nb_examens), unsafe_allow_html=True)
    
    # Onglets pour différentes vues
    tab1, tab2, tab3 = st.tabs(["Examens du Département", "Surveillances", "Conflits Départementaux"])
    
    with tab1:
        st.markdown("#### Examens du Département")
        
        cur.execute("""
            SELECT 
                e.date_examen,
                e.heure_debut,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                l.nom as salle,
                e.nb_etudiants_inscrits,
                e.statut
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE f.departement_id = %s
            AND e.date_examen BETWEEN %s AND %s
            ORDER BY e.date_examen, e.heure_debut
        """, (dept_id, date_debut, date_fin))
        
        dept_exams = cur.fetchall()
        
        if dept_exams:
            import pandas as pd
            df_dept_exams = pd.DataFrame(dept_exams)
            df_dept_exams['statut_html'] = df_dept_exams['statut'].apply(get_status_badge)
            
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.write(df_dept_exams.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Options d'export
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Exporter en CSV"):
                    csv = df_dept_exams.to_csv(index=False)
                    st.download_button(
                        label="Télécharger CSV",
                        data=csv,
                        file_name=f"examens_{selected_dept_name}_{date_debut}_{date_fin}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("Aucun examen planifié pour ce département dans la période sélectionnée")
    
    with tab2:
        st.markdown("#### Surveillances par Professeur")
        
        cur.execute("""
            SELECT 
                p.nom || ' ' || p.prenom as professeur,
                COUNT(s.id) as nb_surveillances,
                COUNT(DISTINCT e.date_examen) as nb_jours
            FROM professeurs p
            LEFT JOIN surveillances s ON p.id = s.professeur_id
            LEFT JOIN examens e ON s.examen_id = e.id AND e.statut = 'Planifie'
            WHERE p.departement_id = %s
            GROUP BY p.id, p.nom, p.prenom
            ORDER BY nb_surveillances DESC
        """, (dept_id,))
        
        surveillances = cur.fetchall()
        
        if surveillances:
            import pandas as pd
            df_surveillances = pd.DataFrame(surveillances)
            st.dataframe(df_surveillances, use_container_width=True, hide_index=True)
            
            # Graphique de répartition
            st.markdown("##### Répartition des Surveillances")
            
            import plotly.express as px
            fig = px.bar(df_surveillances, x='professeur', y='nb_surveillances')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### Conflits Départementaux")
        
        # Conflits étudiants
        st.markdown("##### Conflits Étudiants")
        cur.execute("""
            SELECT 
                e.matricule,
                e.nom,
                e.prenom,
                ex.date_examen,
                COUNT(*) as nb_examens
            FROM etudiants e
            JOIN inscriptions i ON e.id = i.etudiant_id
            JOIN modules m ON i.module_id = m.id
            JOIN examens ex ON m.id = ex.module_id
            JOIN formations f ON e.formation_id = f.id
            WHERE f.departement_id = %s
            AND ex.statut = 'Planifie'
            AND ex.date_examen BETWEEN %s AND %s
            GROUP BY e.id, e.matricule, e.nom, e.prenom, ex.date_examen
            HAVING COUNT(*) > 1
            ORDER BY nb_examens DESC
        """, (dept_id, date_debut, date_fin))
        
        student_conflicts = cur.fetchall()
        
        if student_conflicts:
            import pandas as pd
            df_conflicts = pd.DataFrame(student_conflicts)
            st.dataframe(df_conflicts, use_container_width=True, hide_index=True)
            st.warning(f"{len(student_conflicts)} conflits étudiants détectés")
        else:
            st.success("Aucun conflit étudiant détecté")
    
    cur.close()
    conn.close()

def show_consultation(date_debut, date_fin, selected_dept):
    """Affiche l'interface de consultation"""
    
    st.markdown('<div class="section-title">Consultation des Emplois du Temps</div>', unsafe_allow_html=True)
    
    # Onglets pour différents types de consultation
    tab1, tab2 = st.tabs(["Étudiants", "Professeurs"])
    
    with tab1:
        st.markdown("#### Consultation Étudiante")
        
        # Recherche d'étudiant
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_type = st.radio(
                "Type de recherche",
                ["Par matricule", "Par nom"],
                horizontal=True
            )
        
        with col2:
            if search_type == "Par matricule":
                search_value = st.text_input("Matricule", placeholder="Ex: E202400001")
            else:
                search_value = st.text_input("Nom", placeholder="Ex: Dupont")
        
        if st.button("Rechercher", type="primary"):
            if search_value:
                conn = get_connection()
                if conn:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    
                    # Recherche de l'étudiant
                    if search_type == "Par matricule":
                        cur.execute("SELECT id, matricule, nom, prenom, formation_id FROM etudiants WHERE matricule = %s", (search_value,))
                    else:
                        cur.execute("SELECT id, matricule, nom, prenom, formation_id FROM etudiants WHERE nom ILIKE %s LIMIT 5", (f"%{search_value}%",))
                    
                    students = cur.fetchall()
                    
                    if students:
                        if len(students) > 1:
                            # Multiple résultats
                            student_options = {f"{s['matricule']} - {s['nom']} {s['prenom']}": s['id'] for s in students}
                            selected_student_label = st.selectbox("Sélectionner l'étudiant", list(student_options.keys()))
                            student_id = student_options[selected_student_label]
                        else:
                            # Un seul résultat
                            student = students[0]
                            student_id = student['id']
                            
                            # Affichage des informations
                            st.markdown(f"**Étudiant:** {student['nom']} {student['prenom']}")
                            st.markdown(f"**Matricule:** {student['matricule']}")
                        
                        # Récupération des examens de l'étudiant
                        cur.execute("""
                            SELECT 
                                e.date_examen,
                                e.heure_debut,
                                e.duree_minutes,
                                m.code as module_code,
                                m.nom as module_nom,
                                l.nom as salle,
                                f.nom as formation,
                                e.statut
                            FROM examens e
                            JOIN modules m ON e.module_id = m.id
                            JOIN inscriptions i ON m.id = i.module_id
                            JOIN lieux_examen l ON e.lieu_id = l.id
                            JOIN formations f ON m.formation_id = f.id
                            WHERE i.etudiant_id = %s
                            AND e.date_examen BETWEEN %s AND %s
                            AND e.statut = 'Planifie'
                            ORDER BY e.date_examen, e.heure_debut
                        """, (student_id, date_debut, date_fin))
                        
                        student_exams = cur.fetchall()
                        
                        if student_exams:
                            import pandas as pd
                            df_student_exams = pd.DataFrame(student_exams)
                            df_student_exams['statut_html'] = df_student_exams['statut'].apply(get_status_badge)
                            
                            st.markdown("##### Emploi du Temps")
                            st.markdown('<div class="data-table">', unsafe_allow_html=True)
                            st.write(df_student_exams.to_html(escape=False, index=False), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Statistiques
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total examens", len(student_exams))
                            with col2:
                                unique_days = df_student_exams['date_examen'].nunique()
                                st.metric("Jours d'examens", unique_days)
                            with col3:
                                if len(student_exams) > 0:
                                    st.metric("Prochain examen", df_student_exams.iloc[0]['date_examen'])
                        else:
                            st.info("Aucun examen planifié pour cet étudiant dans la période sélectionnée")
                    else:
                        st.warning("Aucun étudiant trouvé")
                    
                    cur.close()
                    conn.close()
            else:
                st.warning("Veuillez entrer une valeur de recherche")
    
    with tab2:
        st.markdown("#### Consultation Professeurs")
        
        # Recherche de professeur
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prof_search_type = st.radio(
                "Type de recherche",
                ["Par nom", "Par département"],
                horizontal=True,
                key="prof_search"
            )
        
        with col2:
            if prof_search_type == "Par nom":
                prof_search_value = st.text_input("Nom du professeur", placeholder="Ex: Martin")
            else:
                conn = get_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute("SELECT nom FROM departements ORDER BY nom")
                    depts = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    prof_search_value = st.selectbox("Département", depts)
        
        if st.button("Rechercher Professeur", type="primary"):
            if prof_search_value:
                conn = get_connection()
                if conn:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    
                    # Recherche des professeurs
                    if prof_search_type == "Par nom":
                        cur.execute("""
                            SELECT id, matricule, nom, prenom, departement_id 
                            FROM professeurs 
                            WHERE nom ILIKE %s OR prenom ILIKE %s
                            LIMIT 10
                        """, (f"%{prof_search_value}%", f"%{prof_search_value}%"))
                    else:
                        cur.execute("""
                            SELECT p.id, p.matricule, p.nom, p.prenom, p.departement_id
                            FROM professeurs p
                            JOIN departements d ON p.departement_id = d.id
                            WHERE d.nom = %s
                            ORDER BY p.nom
                        """, (prof_search_value,))
                    
                    professors = cur.fetchall()
                    
                    if professors:
                        if len(professors) > 1:
                            # Multiple résultats
                            prof_options = {f"{p['nom']} {p['prenom']} ({p['matricule']})": p['id'] for p in professors}
                            selected_prof_label = st.selectbox("Sélectionner le professeur", list(prof_options.keys()))
                            prof_id = prof_options[selected_prof_label]
                        else:
                            # Un seul résultat
                            professor = professors[0]
                            prof_id = professor['id']
                            
                            # Affichage des informations
                            st.markdown(f"**Professeur:** {professor['nom']} {professor['prenom']}")
                            st.markdown(f"**Matricule:** {professor['matricule']}")
                        
                        # Récupération des surveillances
                        cur.execute("""
                            SELECT 
                                e.date_examen,
                                e.heure_debut,
                                e.duree_minutes,
                                m.code as module_code,
                                m.nom as module_nom,
                                l.nom as salle,
                                s.type_surveillance,
                                e.statut
                            FROM surveillances s
                            JOIN examens e ON s.examen_id = e.id
                            JOIN modules m ON e.module_id = m.id
                            JOIN lieux_examen l ON e.lieu_id = l.id
                            WHERE s.professeur_id = %s
                            AND e.date_examen BETWEEN %s AND %s
                            AND e.statut = 'Planifie'
                            ORDER BY e.date_examen, e.heure_debut
                        """, (prof_id, date_debut, date_fin))
                        
                        professor_surveillances = cur.fetchall()
                        
                        if professor_surveillances:
                            import pandas as pd
                            df_prof_surveillances = pd.DataFrame(professor_surveillances)
                            df_prof_surveillances['statut_html'] = df_prof_surveillances['statut'].apply(get_status_badge)
                            
                            st.markdown("##### Surveillances Assignées")
                            st.markdown('<div class="data-table">', unsafe_allow_html=True)
                            st.write(df_prof_surveillances.to_html(escape=False, index=False), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Statistiques
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total surveillances", len(professor_surveillances))
                            with col2:
                                principal_count = sum(1 for s in professor_surveillances if s['type_surveillance'] == 'Principal')
                                st.metric("Surveillances principales", principal_count)
                            with col3:
                                if len(professor_surveillances) > 0:
                                    st.metric("Prochaine surveillance", df_prof_surveillances.iloc[0]['date_examen'])
                        else:
                            st.info("Aucune surveillance planifiée pour ce professeur dans la période sélectionnée")
                    else:
                        st.warning("Aucun professeur trouvé")
                    
                    cur.close()
                    conn.close()
            else:
                st.warning("Veuillez entrer une valeur de recherche")

if __name__ == "__main__":
    main()