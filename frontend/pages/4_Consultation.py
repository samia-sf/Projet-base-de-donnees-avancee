"""
Interface de Consultation des Emplois du Temps
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, ExamQueries
from config import db_config

st.set_page_config(page_title="Consultation", page_icon="👥", layout="wide")

st.markdown("""
<style>
    .consult-header {
        background: linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .consult-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .consult-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .search-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .info-panel {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 3px solid #8e44ad;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db():
    db = Database(db_config.DB_CONFIG)
    db.connect()
    return db

def main():
    st.markdown("""
    <div class="consult-header">
        <h1>Consultation des Emplois du Temps</h1>
        <p>Recherche et consultation des plannings personnalisés</p>
    </div>
    """, unsafe_allow_html=True)
    
    consultation_type = st.radio(
        "Type de consultation",
        ["Étudiant", "Professeur"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Période", ["Mois en cours", "Semestre"], index=0)
    
    with col2:
        if period == "Mois en cours":
            today = datetime.now().date()
            date_debut = today.replace(day=1)
            date_fin = today + timedelta(days=30)
        else:
            date_debut = datetime.now().date()
            date_fin = date_debut + timedelta(days=180)
    
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown(f"### Recherche {consultation_type}")
    
    try:
        db = get_db()
        
        if consultation_type == "Étudiant":
            col1, col2 = st.columns([1, 2])
            
            with col1:
                search_type = st.radio("Type", ["Matricule", "Nom"], horizontal=True)
            
            with col2:
                if search_type == "Matricule":
                    search_value = st.text_input("Matricule", placeholder="Ex: E202400001")
                else:
                    search_value = st.text_input("Nom", placeholder="Ex: Dupont")
            
            if st.button("Rechercher", type="primary", use_container_width=True):
                if search_value:
                    if search_type == "Matricule":
                        query = "SELECT * FROM etudiants WHERE matricule = %s"
                    else:
                        query = "SELECT * FROM etudiants WHERE nom ILIKE %s LIMIT 10"
                        search_value = f"%{search_value}%"
                    
                    students = db.execute_query(query, (search_value,))
                    
                    if students:
                        student = students[0]
                        st.session_state.selected_student = student
                        st.success(f"Étudiant trouvé: {student['nom']} {student['prenom']}")
                    else:
                        st.warning("Aucun étudiant trouvé")
        
        else:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                search_type = st.radio("Type", ["Nom", "Département"], horizontal=True)
            
            with col2:
                if search_type == "Nom":
                    search_value = st.text_input("Nom", placeholder="Ex: Martin")
                else:
                    query_depts = "SELECT nom FROM departements ORDER BY nom"
                    departments = db.execute_query(query_depts)
                    dept_names = [d['nom'] for d in departments]
                    search_value = st.selectbox("Département", dept_names)
            
            if st.button("Rechercher", type="primary", use_container_width=True):
                if search_value:
                    if search_type == "Nom":
                        query = """
                            SELECT p.*, d.nom as departement 
                            FROM professeurs p
                            JOIN departements d ON p.departement_id = d.id
                            WHERE p.nom ILIKE %s LIMIT 10
                        """
                        search_value = f"%{search_value}%"
                    else:
                        query = """
                            SELECT p.*, d.nom as departement 
                            FROM professeurs p
                            JOIN departements d ON p.departement_id = d.id
                            WHERE d.nom = %s
                        """
                    
                    professors = db.execute_query(query, (search_value,))
                    
                    if professors:
                        professor = professors[0]
                        st.session_state.selected_professor = professor
                        st.success(f"Professeur trouvé: {professor['nom']} {professor['prenom']}")
                    else:
                        st.warning("Aucun professeur trouvé")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if consultation_type == "Étudiant" and 'selected_student' in st.session_state:
            student = st.session_state.selected_student
            
            st.markdown("### Informations de l'Étudiant")
            
            query_info = """
                SELECT e.*, f.nom as formation, d.nom as departement
                FROM etudiants e
                JOIN formations f ON e.formation_id = f.id
                JOIN departements d ON f.departement_id = d.id
                WHERE e.id = %s
            """
            
            student_info = db.execute_query(query_info, (student['id'],))
            
            if student_info:
                info = student_info[0]
                st.markdown(f"""
                <div class="info-panel">
                    <strong>Matricule:</strong> {info['matricule']}<br>
                    <strong>Nom:</strong> {info['nom']} {info['prenom']}<br>
                    <strong>Formation:</strong> {info['formation']}<br>
                    <strong>Département:</strong> {info['departement']}<br>
                    <strong>Promotion:</strong> {info['promotion']}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### Emploi du Temps")
            
            schedule = ExamQueries.get_examens_etudiant(db, student['id'], "2024-2025")
            
            if schedule:
                df_schedule = pd.DataFrame(schedule)
                st.dataframe(df_schedule, use_container_width=True, hide_index=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total examens", len(schedule))
                with col2:
                    st.metric("Jours d'examens", df_schedule['date_examen'].nunique())
                with col3:
                    total_h = df_schedule['duree_minutes'].sum() / 60
                    st.metric("Heures totales", f"{total_h:.1f}h")
            else:
                st.info("Aucun examen planifié")
        
        elif consultation_type == "Professeur" and 'selected_professor' in st.session_state:
            professor = st.session_state.selected_professor
            
            st.markdown("### Informations du Professeur")
            
            st.markdown(f"""
            <div class="info-panel">
                <strong>Matricule:</strong> {professor['matricule']}<br>
                <strong>Nom:</strong> {professor['nom']} {professor['prenom']}<br>
                <strong>Département:</strong> {professor['departement']}<br>
                <strong>Grade:</strong> {professor.get('grade', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Surveillances Assignées")
            
            surveillances = ExamQueries.get_surveillances_prof(db, professor['id'], "2024-2025")
            
            if surveillances:
                df_surv = pd.DataFrame(surveillances)
                st.dataframe(df_surv, use_container_width=True, hide_index=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total surveillances", len(surveillances))
                with col2:
                    st.metric("Jours", df_surv['date_examen'].nunique())
                with col3:
                    total_h = df_surv['duree_minutes'].sum() / 60
                    st.metric("Heures totales", f"{total_h:.1f}h")
            else:
                st.info("Aucune surveillance planifiée")
    
    except Exception as e:
        st.error(f"Erreur: {e}")

if __name__ == "__main__":
    main()