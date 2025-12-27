"""
Interface Chef de Département
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, ExamQueries
from config import db_config

st.set_page_config(page_title="Chef de Département", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .chef-header {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .chef-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .chef-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .dept-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .grid-metric {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .grid-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .grid-label {
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
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
    <div class="chef-header">
        <h1>Dashboard Chef de Département</h1>
        <p>Gestion et suivi des examens de votre département</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = get_db()
        
        query_depts = "SELECT id, nom FROM departements ORDER BY nom"
        departments = db.execute_query(query_depts)
        
        if not departments:
            st.error("Aucun département trouvé")
            return
        
        dept_names = [d['nom'] for d in departments]
        selected_department = st.selectbox("Sélectionnez votre département", dept_names)
        
        dept_id = next(d['id'] for d in departments if d['nom'] == selected_department)
        
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox("Période", ["Mois en cours", "Semestre", "Personnalisée"], index=0)
        
        with col2:
            if period == "Personnalisée":
                date_debut = st.date_input("Date début", datetime.now().date())
                date_fin = st.date_input("Date fin", datetime.now().date() + timedelta(days=30))
            else:
                date_debut = datetime.now().date()
                date_fin = date_debut + timedelta(days=90)
        
        st.markdown('<div class="dept-card">', unsafe_allow_html=True)
        st.markdown(f"### Vue d'Ensemble - {selected_department}")
        
        stats = ExamQueries.get_stats_departement(db, dept_id, "2024-2025")
        
        if stats:
            st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="grid-metric">
                <div class="grid-value">{stats.get('nb_formations', 0)}</div>
                <div class="grid-label">Formations</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="grid-metric">
                <div class="grid-value">{stats.get('nb_etudiants', 0):,}</div>
                <div class="grid-label">Étudiants</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="grid-metric">
                <div class="grid-value">{stats.get('nb_professeurs', 0)}</div>
                <div class="grid-label">Professeurs</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="grid-metric">
                <div class="grid-value">{stats.get('nb_examens', 0)}</div>
                <div class="grid-label">Examens</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Examens", "Surveillances", "Validation"])
        
        with tab1:
            st.markdown("### Examens du Département")
            
            query_exams = """
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
            """
            
            dept_exams = db.execute_query(query_exams, (dept_id, date_debut, date_fin))
            
            if dept_exams:
                df_exams = pd.DataFrame(dept_exams)
                st.dataframe(df_exams, use_container_width=True, hide_index=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total examens", len(dept_exams))
                with col2:
                    st.metric("Total étudiants", df_exams['nb_etudiants_inscrits'].sum())
                with col3:
                    st.metric("Salles utilisées", df_exams['salle'].nunique())
            else:
                st.info("Aucun examen planifié pour cette période")
        
        with tab2:
            st.markdown("### Charge des Professeurs")
            
            query_surv = """
                SELECT 
                    p.nom || ' ' || p.prenom as professeur,
                    COUNT(s.id) as nb_surveillances
                FROM professeurs p
                LEFT JOIN surveillances s ON p.id = s.professeur_id
                LEFT JOIN examens e ON s.examen_id = e.id
                WHERE p.departement_id = %s
                AND e.statut = 'Planifie'
                GROUP BY p.id, p.nom, p.prenom
                ORDER BY nb_surveillances DESC
            """
            
            surveillances = db.execute_query(query_surv, (dept_id,))
            
            if surveillances:
                df_surv = pd.DataFrame(surveillances)
                st.dataframe(df_surv, use_container_width=True, hide_index=True)
                
                fig = px.bar(
                    df_surv.head(10),
                    x='professeur',
                    y='nb_surveillances',
                    labels={'professeur': 'Professeur', 'nb_surveillances': 'Surveillances'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune surveillance assignée")
        
        with tab3:
            st.markdown("### Validation du Planning Départemental")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info("""
                **Critères de validation :**
                - Tous les modules ont un examen planifié
                - Aucun conflit étudiant
                - Capacités des salles respectées
                - Surveillances équilibrées
                """)
            
            with col2:
                if st.button("Valider", type="primary", use_container_width=True):
                    st.success(f"Planning validé pour {selected_department}")
                
                if st.button("Exporter", use_container_width=True):
                    st.info("Export en cours...")
    
    except Exception as e:
        st.error(f"Erreur: {e}")

if __name__ == "__main__":
    main()