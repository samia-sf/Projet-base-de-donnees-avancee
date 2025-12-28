"""
Dashboard Doyen - Vue stratégique globale
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, DashboardQueries
from config import db_config

st.set_page_config(
    page_title="Dashboard Doyen",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .kpi-card {
        background: white;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        border-left: 3px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3c72;
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .dept-card {
        background: white;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 3px solid;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    .dept-card h4 {
        margin: 0 0 1rem 0;
        color: #1e3c72;
        font-size: 1.1rem;
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
    <div class="dashboard-header">
        <h1>Dashboard Doyen</h1>
        <p>Vue stratégique globale - Suivi des examens universitaires</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        periode = st.selectbox(
            "Période",
            ["Semaine en cours", "Mois en cours", "Semestre", "Personnalisée"],
            index=1
        )
    
    with col2:
        if periode == "Personnalisée":
            date_debut = st.date_input("Date de début", datetime.now().date())
        else:
            date_debut = datetime.now().date()
    
    with col3:
        if periode == "Personnalisée":
            date_fin = st.date_input("Date de fin", datetime.now().date() + timedelta(days=30))
        else:
            date_fin = datetime.now().date() + timedelta(days=30)
    
    try:
        db = get_db()
        annee = st.session_state.get('current_year', '2024-2025')
        
        st.markdown("### Indicateurs Clés de Performance")
        
        kpis = DashboardQueries.get_kpis_globaux(db, annee)
        
        if kpis:
            col1, col2, col3, col4 = st.columns(4)
            
            total_examens = kpis.get('total_examens') or 0
            profs_mobilises = kpis.get('profs_mobilises') or 0
            salles_utilisees = kpis.get('salles_utilisees') or 0
            total_places = kpis.get('total_places_examens') or 0
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_examens:,}</div>
                    <div class="kpi-label">Examens Planifiés</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{profs_mobilises}</div>
                    <div class="kpi-label">Professeurs Mobilisés</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{salles_utilisees}</div>
                    <div class="kpi-label">Salles Utilisées</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_places:,}</div>
                    <div class="kpi-label">Places d'Examen</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### Analyses Visuelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### Répartition des Examens par Département")
            
            repartition = DashboardQueries.get_repartition_examens_par_dept(db, annee)
            
            if repartition:
                df_dept = pd.DataFrame(repartition)
                
                fig = px.bar(
                    df_dept,
                    x='departement',
                    y='nb_examens',
                    color='nb_examens',
                    color_continuous_scale='Blues',
                    labels={'departement': 'Département', 'nb_examens': "Nombre d'examens"}
                )
                
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="Nombre d'examens",
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### Occupation des Salles par Jour")
            
            occupation = DashboardQueries.get_occupation_salles_par_jour(db, annee)
            
            if occupation:
                df_occupancy = pd.DataFrame(occupation)
                
                fig = px.line(
                    df_occupancy,
                    x='date_examen',
                    y='taux_occupation',
                    markers=True,
                    labels={'date_examen': 'Date', 'taux_occupation': "Taux d'occupation (%)"}
                )
                
                fig.update_traces(line_color='#2a5298', line_width=3)
                fig.update_layout(
                    height=400,
                    xaxis_title="",
                    yaxis_title="Taux d'occupation (%)",
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### Détails par Département")
        
        query = """
            SELECT 
                d.nom as departement,
                COUNT(DISTINCT f.id) as nb_formations,
                COUNT(DISTINCT m.id) as nb_modules,
                COUNT(DISTINCT et.id) as nb_etudiants,
                COUNT(DISTINCT p.id) as nb_professeurs,
                COUNT(DISTINCT e.id) as nb_examens
            FROM departements d
            LEFT JOIN formations f ON d.id = f.departement_id
            LEFT JOIN modules m ON f.id = m.formation_id
            LEFT JOIN etudiants et ON f.id = et.formation_id
            LEFT JOIN professeurs p ON d.id = p.departement_id
            LEFT JOIN examens e ON m.id = e.module_id AND e.statut = 'Planifie'
            GROUP BY d.id, d.nom
            ORDER BY d.nom
        """
        
        all_dept_data = db.execute_query(query)
        
        if all_dept_data:
            cols = st.columns(2)
            color_map = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
            
            for idx, dept in enumerate(all_dept_data):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="dept-card" style="border-left-color: {color_map[idx % len(color_map)]};">
                        <h4>{dept['departement']}</h4>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                            <div>
                                <div style="font-size: 0.75rem; color: #6c757d;">Formations</div>
                                <div style="font-size: 1.1rem; font-weight: 600;">{dept['nb_formations']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #6c757d;">Modules</div>
                                <div style="font-size: 1.1rem; font-weight: 600;">{dept['nb_modules']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #6c757d;">Étudiants</div>
                                <div style="font-size: 1.1rem; font-weight: 600;">{dept['nb_etudiants']}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #6c757d;">Examens</div>
                                <div style="font-size: 1.1rem; font-weight: 600;">{dept['nb_examens']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("### Validation du Planning")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Valider le Planning Général", type="primary", use_container_width=True):
                st.success("Planning validé avec succès")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")

if __name__ == "__main__":
    main()