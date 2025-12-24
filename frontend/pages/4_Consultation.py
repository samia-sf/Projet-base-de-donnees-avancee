"""
Interface de Consultation des Emplois du Temps
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta

# Configuration
st.set_page_config(
    page_title="Consultation des Emplois du Temps",
    page_icon="👥",
    layout="wide"
)

# CSS supplémentaire
st.markdown("""
<style>
    .consult-header {
        background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .search-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    .result-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    .info-panel {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #9b59b6;
    }
    
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .schedule-table th {
        background: #9b59b6;
        color: white;
        padding: 0.75rem;
        text-align: left;
    }
    
    .schedule-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .schedule-table tr:hover {
        background: #f8f9fa;
    }
    
    .export-options {
        background: #e8f4fc;
        border: 1px solid #3498db;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .no-results {
        background: #fff8e1;
        border: 1px solid #f1c40f;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='num_exam_db',
            user='postgres',
            password='123456'
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return None

def search_student(search_type, search_value):
    """Recherche un étudiant"""
    conn = get_connection()
    if not conn:
        return []
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if search_type == "matricule":
            cur.execute("""
                SELECT id, matricule, nom, prenom, email, formation_id, promotion
                FROM etudiants
                WHERE matricule = %s
            """, (search_value,))
        else:  # nom
            cur.execute("""
                SELECT id, matricule, nom, prenom, email, formation_id, promotion
                FROM etudiants
                WHERE nom ILIKE %s OR prenom ILIKE %s
                ORDER BY nom, prenom
                LIMIT 10
            """, (f"%{search_value}%", f"%{search_value}%"))
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def search_professor(search_type, search_value, department=None):
    """Recherche un professeur"""
    conn = get_connection()
    if not conn:
        return []
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if search_type == "nom":
            cur.execute("""
                SELECT p.id, p.matricule, p.nom, p.prenom, p.email, p.grade, d.nom as departement
                FROM professeurs p
                JOIN departements d ON p.departement_id = d.id
                WHERE p.nom ILIKE %s OR p.prenom ILIKE %s
                ORDER BY p.nom, p.prenom
                LIMIT 10
            """, (f"%{search_value}%", f"%{search_value}%"))
        else:  # département
            cur.execute("""
                SELECT p.id, p.matricule, p.nom, p.prenom, p.email, p.grade, d.nom as departement
                FROM professeurs p
                JOIN departements d ON p.departement_id = d.id
                WHERE d.nom = %s
                ORDER BY p.nom, p.prenom
            """, (search_value,))
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_student_schedule(student_id, date_debut, date_fin):
    """Récupère l'emploi du temps d'un étudiant"""
    conn = get_connection()
    if not conn:
        return []
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                l.nom as salle,
                l.batiment,
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
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_professor_schedule(prof_id, date_debut, date_fin):
    """Récupère l'emploi du temps d'un professeur"""
    conn = get_connection()
    if not conn:
        return []
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                l.nom as salle,
                l.batiment,
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
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_student_info(student_id):
    """Récupère les informations d'un étudiant"""
    conn = get_connection()
    if not conn:
        return None
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                e.matricule,
                e.nom,
                e.prenom,
                e.email,
                e.promotion,
                f.nom as formation,
                d.nom as departement
            FROM etudiants e
            JOIN formations f ON e.formation_id = f.id
            JOIN departements d ON f.departement_id = d.id
            WHERE e.id = %s
        """, (student_id,))
        
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def get_professor_info(prof_id):
    """Récupère les informations d'un professeur"""
    conn = get_connection()
    if not conn:
        return None
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                p.matricule,
                p.nom,
                p.prenom,
                p.email,
                p.grade,
                p.specialite,
                d.nom as departement
            FROM professeurs p
            JOIN departements d ON p.departement_id = d.id
            WHERE p.id = %s
        """, (prof_id,))
        
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def main():
    """Fonction principale de l'interface de consultation"""
    
    # Header
    st.markdown("""
    <div class="consult-header">
        <h1 style="margin: 0; font-size: 2.5rem;">Consultation des Emplois du Temps</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Recherche et consultation des plannings personnalisés
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection du type de consultation
    consultation_type = st.radio(
        "Type de consultation",
        ["Étudiant", "Professeur"],
        horizontal=True,
        index=0
    )
    
    # Filtres de période
    col_period1, col_period2 = st.columns(2)
    
    with col_period1:
        period = st.selectbox(
            "Période",
            ["Semaine en cours", "Mois en cours", "Semestre", "Personnalisée"],
            index=1
        )
    
    with col_period2:
        if period == "Personnalisée":
            date_debut = st.date_input("Date de début", datetime.now().date())
            date_fin = st.date_input("Date de fin", datetime.now().date() + timedelta(days=30))
        elif period == "Semaine en cours":
            today = datetime.now().date()
            date_debut = today - timedelta(days=today.weekday())
            date_fin = date_debut + timedelta(days=6)
        elif period == "Mois en cours":
            today = datetime.now().date()
            date_debut = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            date_fin = next_month - timedelta(days=next_month.day)
        else:  # Semestre
            date_debut = datetime.now().date()
            date_fin = date_debut + timedelta(days=180)
    
    # Section de recherche
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown(f"### Recherche {consultation_type}")
    
    if consultation_type == "Étudiant":
        col_search1, col_search2 = st.columns([1, 2])
        
        with col_search1:
            search_type = st.radio(
                "Type de recherche",
                ["Matricule", "Nom"],
                horizontal=True,
                key="student_search_type"
            )
        
        with col_search2:
            if search_type == "Matricule":
                search_value = st.text_input(
                    "Matricule de l'étudiant",
                    placeholder="Ex: E202400001",
                    key="student_matricule"
                )
            else:
                search_value = st.text_input(
                    "Nom de l'étudiant",
                    placeholder="Ex: Dupont",
                    key="student_name"
                )
        
        if st.button("Rechercher l'Étudiant", type="primary", use_container_width=True):
            if search_value:
                with st.spinner("Recherche en cours..."):
                    students = search_student(
                        "matricule" if search_type == "Matricule" else "nom",
                        search_value
                    )
                    
                    if students:
                        if len(students) == 1:
                            student = students[0]
                            st.session_state.selected_student = student
                            st.success(f"Étudiant trouvé: {student['nom']} {student['prenom']}")
                        else:
                            # Plusieurs résultats
                            student_options = {
                                f"{s['matricule']} - {s['nom']} {s['prenom']}": s for s in students
                            }
                            selected_option = st.selectbox(
                                "Sélectionner l'étudiant",
                                list(student_options.keys())
                            )
                            
                            if selected_option:
                                st.session_state.selected_student = student_options[selected_option]
                                st.success(f"Étudiant sélectionné: {student_options[selected_option]['nom']} {student_options[selected_option]['prenom']}")
                    else:
                        st.warning("Aucun étudiant trouvé avec ces critères")
                        if 'selected_student' in st.session_state:
                            del st.session_state.selected_student
            else:
                st.warning("Veuillez entrer une valeur de recherche")
    else:  # Professeur
        col_search1, col_search2 = st.columns([1, 2])
        
        with col_search1:
            search_type = st.radio(
                "Type de recherche",
                ["Nom", "Département"],
                horizontal=True,
                key="prof_search_type"
            )
        
        with col_search2:
            if search_type == "Nom":
                search_value = st.text_input(
                    "Nom du professeur",
                    placeholder="Ex: Martin",
                    key="prof_name"
                )
            else:
                # Récupération des départements
                conn = get_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute("SELECT nom FROM departements ORDER BY nom")
                    departments = [row[0] for row in cur.fetchall()]
                    cur.close()
                    conn.close()
                    
                    search_value = st.selectbox(
                        "Département",
                        departments,
                        key="prof_department"
                    )
        
        if st.button("Rechercher le Professeur", type="primary", use_container_width=True):
            if search_value:
                with st.spinner("Recherche en cours..."):
                    professors = search_professor(
                        "nom" if search_type == "Nom" else "departement",
                        search_value
                    )
                    
                    if professors:
                        if len(professors) == 1:
                            professor = professors[0]
                            st.session_state.selected_professor = professor
                            st.success(f"Professeur trouvé: {professor['nom']} {professor['prenom']}")
                        else:
                            # Plusieurs résultats
                            prof_options = {
                                f"{p['nom']} {p['prenom']} ({p['departement']})": p for p in professors
                            }
                            selected_option = st.selectbox(
                                "Sélectionner le professeur",
                                list(prof_options.keys())
                            )
                            
                            if selected_option:
                                st.session_state.selected_professor = prof_options[selected_option]
                                st.success(f"Professeur sélectionné: {prof_options[selected_option]['nom']} {prof_options[selected_option]['prenom']}")
                    else:
                        st.warning("Aucun professeur trouvé avec ces critères")
                        if 'selected_professor' in st.session_state:
                            del st.session_state.selected_professor
            else:
                st.warning("Veuillez entrer une valeur de recherche")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Affichage des résultats
    if consultation_type == "Étudiant" and 'selected_student' in st.session_state:
        student = st.session_state.selected_student
        display_student_results(student, date_debut, date_fin)
    
    elif consultation_type == "Professeur" and 'selected_professor' in st.session_state:
        professor = st.session_state.selected_professor
        display_professor_results(professor, date_debut, date_fin)

def display_student_results(student, date_debut, date_fin):
    """Affiche les résultats pour un étudiant"""
    
    # Informations de l'étudiant
    student_info = get_student_info(student['id'])
    
    if not student_info:
        st.error("Impossible de récupérer les informations de l'étudiant")
        return
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Informations de l'Étudiant")
    
    st.markdown(f"""
    <div class="info-panel">
        <table style="width: 100%;">
            <tr>
                <td style="width: 30%; font-weight: bold;">Matricule:</td>
                <td>{student_info['matricule']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Nom:</td>
                <td>{student_info['nom']} {student_info['prenom']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Formation:</td>
                <td>{student_info['formation']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Département:</td>
                <td>{student_info['departement']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Promotion:</td>
                <td>{student_info['promotion']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Email:</td>
                <td>{student_info['email']}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Emploi du temps
    st.markdown("### Emploi du Temps")
    st.markdown(f"Période: {date_debut} au {date_fin}")
    
    schedule = get_student_schedule(student['id'], date_debut, date_fin)
    
    if schedule:
        df_schedule = pd.DataFrame(schedule)
        
        # Calcul des statistiques
        total_exams = len(schedule)
        unique_days = df_schedule['date_examen'].nunique()
        total_duration = df_schedule['duree_minutes'].sum()
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total examens", total_exams)
        
        with col_stat2:
            st.metric("Jours d'examens", unique_days)
        
        with col_stat3:
            st.metric("Heures totales", f"{total_duration/60:.1f}h")
        
        # Affichage du planning
        st.markdown("##### Détail des Examens")
        
        # Formatage des données pour l'affichage
        display_df = df_schedule.copy()
        display_df['Heure'] = display_df['heure_debut'].apply(lambda x: x.strftime('%H:%M'))
        display_df['Durée (h)'] = (display_df['duree_minutes'] / 60).round(1)
        
        # Colonnes à afficher
        display_cols = ['date_examen', 'Heure', 'Durée (h)', 'module_code', 'module_nom', 'formation', 'salle', 'batiment']
        
        st.dataframe(
            display_df[display_cols],
            column_config={
                'date_examen': st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                'module_code': "Code",
                'module_nom': "Module",
                'formation': "Formation",
                'salle': "Salle",
                'batiment': "Bâtiment"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Détection de conflits
        st.markdown("##### Vérification des Conflits")
        
        # Vérifier les doublons de date
        date_counts = df_schedule['date_examen'].value_counts()
        conflict_dates = date_counts[date_counts > 1].index.tolist()
        
        if conflict_dates:
            st.error("⚠️ Conflits d'horaires détectés !")
            
            for conflict_date in conflict_dates:
                conflict_exams = df_schedule[df_schedule['date_examen'] == conflict_date]
                
                st.markdown(f"**Le {conflict_date.strftime('%d/%m/%Y')}:**")
                for _, exam in conflict_exams.iterrows():
                    st.markdown(f"- {exam['module_code']} ({exam['heure_debut'].strftime('%H:%M')})")
        else:
            st.success("✅ Aucun conflit d'horaire détecté")
        
        # Options d'export
        st.markdown("##### Export du Planning")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("Exporter en CSV", use_container_width=True):
                csv = df_schedule.to_csv(index=False)
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name=f"emploi_du_temps_{student_info['matricule']}.csv",
                    mime="text/csv"
                )
        
        with col_export2:
            if st.button("Exporter en PDF", use_container_width=True):
                st.info("La fonctionnalité d'export PDF sera bientôt disponible")
        
        with col_export3:
            if st.button("Exporter en iCal", use_container_width=True):
                st.info("La fonctionnalité d'export iCal sera bientôt disponible")
        
        # Vue calendrier
        with st.expander("Vue Calendrier"):
            # Création d'un calendrier simple
            import calendar
            
            # Mois en cours
            today = datetime.now()
            cal = calendar.monthcalendar(today.year, today.month)
            
            st.markdown(f"### Calendrier - {today.strftime('%B %Y')}")
            
            # En-têtes des jours
            days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            cols = st.columns(7)
            
            for i, day in enumerate(days):
                with cols[i]:
                    st.markdown(f"**{day}**")
            
            # Jours du mois
            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    with cols[i]:
                        if day != 0:
                            # Vérifier si l'étudiant a un examen ce jour-là
                            exam_date = datetime(today.year, today.month, day).date()
                            has_exam = any(exam['date_examen'] == exam_date for exam in schedule)
                            
                            if has_exam:
                                st.markdown(f"<div style='background: #e74c3c; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin: auto;'>{day}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin: auto;'>{day}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="no-results">
            <h3>Aucun examen planifié</h3>
            <p>Cet étudiant n'a pas d'examen planifié pour la période sélectionnée.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_professor_results(professor, date_debut, date_fin):
    """Affiche les résultats pour un professeur"""
    
    # Informations du professeur
    prof_info = get_professor_info(professor['id'])
    
    if not prof_info:
        st.error("Impossible de récupérer les informations du professeur")
        return
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("### Informations du Professeur")
    
    st.markdown(f"""
    <div class="info-panel">
        <table style="width: 100%;">
            <tr>
                <td style="width: 30%; font-weight: bold;">Matricule:</td>
                <td>{prof_info['matricule']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Nom:</td>
                <td>{prof_info['nom']} {prof_info['prenom']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Département:</td>
                <td>{prof_info['departement']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Grade:</td>
                <td>{prof_info['grade']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Spécialité:</td>
                <td>{prof_info['specialite']}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Email:</td>
                <td>{prof_info['email']}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Surveillances assignées
    st.markdown("### Surveillances Assignées")
    st.markdown(f"Période: {date_debut} au {date_fin}")
    
    surveillances = get_professor_schedule(professor['id'], date_debut, date_fin)
    
    if surveillances:
        df_surveillances = pd.DataFrame(surveillances)
        
        # Calcul des statistiques
        total_surveillances = len(surveillances)
        unique_days = df_surveillances['date_examen'].nunique()
        principal_count = sum(1 for s in surveillances if s['type_surveillance'] == 'Principal')
        total_duration = df_surveillances['duree_minutes'].sum()
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Total surveillances", total_surveillances)
        
        with col_stat2:
            st.metric("Jours de surveillance", unique_days)
        
        with col_stat3:
            st.metric("Surveillances principales", principal_count)
        
        with col_stat4:
            st.metric("Heures totales", f"{total_duration/60:.1f}h")
        
        # Affichage des surveillances
        st.markdown("##### Détail des Surveillances")
        
        # Formatage des données pour l'affichage
        display_df = df_surveillances.copy()
        display_df['Heure'] = display_df['heure_debut'].apply(lambda x: x.strftime('%H:%M'))
        display_df['Durée (h)'] = (display_df['duree_minutes'] / 60).round(1)
        
        # Colonnes à afficher
        display_cols = ['date_examen', 'Heure', 'Durée (h)', 'module_code', 'module_nom', 'salle', 'batiment', 'type_surveillance']
        
        st.dataframe(
            display_df[display_cols],
            column_config={
                'date_examen': st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                'module_code': "Code",
                'module_nom': "Module",
                'salle': "Salle",
                'batiment': "Bâtiment",
                'type_surveillance': "Type"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Vérification de la charge de travail
        st.markdown("##### Analyse de la Charge de Travail")
        
        # Vérifier les jours avec plus de 3 surveillances
        date_counts = df_surveillances['date_examen'].value_counts()
        overload_dates = date_counts[date_counts > 3].index.tolist()
        
        if overload_dates:
            st.error("⚠️ Surcharge de travail détectée !")
            
            for overload_date in overload_dates:
                overload_surveillances = df_surveillances[df_surveillances['date_examen'] == overload_date]
                
                st.markdown(f"**Le {overload_date.strftime('%d/%m/%Y')}:** {len(overload_surveillances)} surveillances")
                for _, surveillance in overload_surveillances.iterrows():
                    st.markdown(f"- {surveillance['module_code']} ({surveillance['heure_debut'].strftime('%H:%M')}) - {surveillance['type_surveillance']}")
        else:
            st.success("✅ Charge de travail acceptable")
        
        # Graphique: Répartition par type de surveillance
        st.markdown("##### Répartition par Type de Surveillance")
        
        if 'type_surveillance' in df_surveillances.columns:
            type_counts = df_surveillances['type_surveillance'].value_counts()
            
            import plotly.express as px
            
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Répartition des surveillances par type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Options d'export
        st.markdown("##### Export du Planning")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("Exporter en CSV", key="prof_csv", use_container_width=True):
                csv = df_surveillances.to_csv(index=False)
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name=f"surveillances_{prof_info['matricule']}.csv",
                    mime="text/csv",
                    key="prof_download_csv"
                )
        
        with col_export2:
            if st.button("Exporter en PDF", key="prof_pdf", use_container_width=True):
                st.info("La fonctionnalité d'export PDF sera bientôt disponible")
        
        with col_export3:
            if st.button("Exporter en iCal", key="prof_ical", use_container_width=True):
                st.info("La fonctionnalité d'export iCal sera bientôt disponible")
    else:
        st.markdown("""
        <div class="no-results">
            <h3>Aucune surveillance planifiée</h3>
            <p>Ce professeur n'a pas de surveillance planifiée pour la période sélectionnée.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()