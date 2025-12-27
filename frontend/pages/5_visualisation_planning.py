"""
Visualisation Professionnelle des Emplois du Temps
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database
from config import db_config

st.set_page_config(page_title="Visualisation Planning", page_icon="📅", layout="wide")

st.markdown("""
<style>
    .university-header {
        text-align: center;
        background: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .university-header h2 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.5rem;
    }
    
    .university-header h3 {
        color: #34495e;
        margin: 0.5rem 0;
        font-size: 1.2rem;
    }
    
    .university-header h1 {
        color: #2c3e50;
        margin: 1rem 0;
        font-size: 1.75rem;
    }
    
    .university-header p {
        color: #7f8c8d;
        font-size: 1rem;
    }
    
    .planning-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        margin: 2rem 0;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .planning-table th {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 0.85rem;
        text-align: center;
        border: 2px solid #2c3e50;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .planning-table td {
        padding: 0.65rem;
        text-align: center;
        border: 1px solid #bdc3c7;
        font-size: 0.8rem;
    }
    
    .group-header {
        background: #ecf0f1;
        font-weight: 600;
        border: 2px solid #95a5a6;
    }
    
    .time-row {
        background: #ebf5fb;
        color: #1976d2;
        font-weight: 600;
    }
    
    .matiere-row {
        background: #fef9e7;
        font-weight: 600;
    }
    
    .salle-cell {
        background: #fff3cd;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db():
    db = Database(db_config.DB_CONFIG)
    db.connect()
    return db

def main():
    st.title("Visualisation des Emplois du Temps")
    
    try:
        db = get_db()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            query_depts = "SELECT DISTINCT d.id, d.nom FROM departements d ORDER BY d.nom"
            departments = db.execute_query(query_depts)
            
            if not departments:
                st.error("Aucun département trouvé dans la base de données")
                return
                
            dept_names = [d['nom'] for d in departments]
            selected_dept = st.selectbox("Département", dept_names)
            dept_id = next(d['id'] for d in departments if d['nom'] == selected_dept)
        
        with col2:
            query_formations = """
                SELECT f.id, f.nom, f.niveau
                FROM formations f
                WHERE f.departement_id = %s
                ORDER BY f.niveau, f.nom
            """
            formations = db.execute_query(query_formations, (dept_id,))
            
            if not formations:
                st.warning("Aucune formation trouvée pour ce département")
                return
                
            formation_labels = [f"{f['niveau']} - {f['nom']}" for f in formations]
            selected_formation_label = st.selectbox("Formation", formation_labels)
            formation_id = formations[formation_labels.index(selected_formation_label)]['id']
        
        with col3:
            date_debut = st.date_input("Date début", datetime(2026, 1, 5).date())
        
        if st.button("Afficher le Planning", type="primary", use_container_width=True):
            query_exams = """
                SELECT 
                    e.id,
                    e.date_examen,
                    e.heure_debut,
                    e.duree_minutes,
                    m.code as module_code,
                    m.nom as module_nom,
                    l.nom as salle,
                    l.type as type_lieu,
                    f.nom as formation,
                    f.niveau,
                    e.nb_etudiants_inscrits,
                    EXTRACT(DOW FROM e.date_examen) as day_of_week
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN lieux_examen l ON e.lieu_id = l.id
                WHERE f.id = %s
                AND e.date_examen >= %s
                AND e.statut = 'Planifie'
                ORDER BY e.date_examen, e.heure_debut
                LIMIT 15
            """
            
            exams = db.execute_query(query_exams, (formation_id, str(date_debut)))
            
            if exams:
                df = pd.DataFrame(exams)
                
                st.markdown(f"""
                <div class="university-header">
                    <h2>Université M'Hamed Bougara</h2>
                    <h3>Faculté des Sciences</h3>
                    <h1>PLANNING DES EXAMENS</h1>
                    <h2 style="color: #3498db; margin: 0.5rem 0;">{selected_formation_label}</h2>
                    <p>Année Universitaire: 2025/2026</p>
                </div>
                """, unsafe_allow_html=True)
                
                days_map = {0: 'Dimanche', 1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 
                           4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi'}
                
                unique_dates = df.drop_duplicates(subset=['date_examen']).sort_values('date_examen')
                
                html_table = '<table class="planning-table">'
                
                html_table += '<thead><tr><th>Info</th>'
                for _, exam in unique_dates.iterrows():
                    day = days_map.get(int(exam['day_of_week']), 'N/A')
                    html_table += f'<th>{day}<br>{exam["date_examen"].strftime("%d/%m/%Y")}</th>'
                html_table += '</tr></thead><tbody>'
                
                html_table += '<tr><td class="group-header">Séance</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    heure = exams_this_date.iloc[0]['heure_debut'].strftime('%H:%M')
                    html_table += f'<td class="time-row">{heure}</td>'
                html_table += '</tr>'
                
                html_table += '<tr><td class="group-header">Matière</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    module = exams_this_date.iloc[0]['module_code']
                    html_table += f'<td class="matiere-row" title="{exams_this_date.iloc[0]["module_nom"]}">{module}</td>'
                html_table += '</tr>'
                
                html_table += '<tr><td class="group-header">Module</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    module_nom = exams_this_date.iloc[0]['module_nom'][:30]
                    html_table += f'<td style="font-size: 0.7rem;">{module_nom}...</td>'
                html_table += '</tr>'
                
                html_table += '<tr><td class="group-header">Salle</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    salle = exams_this_date.iloc[0]['salle']
                    html_table += f'<td class="salle-cell">{salle}</td>'
                html_table += '</tr>'
                
                html_table += '<tr><td class="group-header">Étudiants</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    nb = exams_this_date.iloc[0]['nb_etudiants_inscrits']
                    html_table += f'<td>{nb}</td>'
                html_table += '</tr>'
                
                html_table += '<tr><td class="group-header">Durée</td>'
                for _, exam in unique_dates.iterrows():
                    exams_this_date = df[df['date_examen'] == exam['date_examen']]
                    duree = exams_this_date.iloc[0]['duree_minutes']
                    html_table += f'<td>{duree} min</td>'
                html_table += '</tr>'
                
                html_table += '</tbody></table>'
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown("### Liste Complète des Examens")
                
                display_df = df[[
                    'date_examen', 'heure_debut', 'duree_minutes', 
                    'module_code', 'module_nom', 'salle', 'nb_etudiants_inscrits'
                ]].copy()
                
                display_df.columns = [
                    'Date', 'Heure', 'Durée (min)', 
                    'Code', 'Module', 'Salle', 'Étudiants'
                ]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("### Statistiques du Planning")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Examens", len(exams))
                
                with col2:
                    st.metric("Salles Utilisées", df['salle'].nunique())
                
                with col3:
                    st.metric("Durée Totale", f"{df['duree_minutes'].sum() / 60:.1f}h")
                
                with col4:
                    st.metric("Jours", df['date_examen'].nunique())
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Exporter en PDF", use_container_width=True):
                        st.info("Fonctionnalité en développement")
                
                with col2:
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Télécharger CSV",
                        data=csv,
                        file_name=f"planning_{selected_formation_label.replace(' ', '_')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("Envoyer par Email", use_container_width=True):
                        st.info("Fonctionnalité en développement")
            
            else:
                st.warning("Aucun examen planifié pour cette formation à cette date")
                st.info("Essayez de changer la date ou vérifiez que des examens sont bien planifiés dans la base de données")
    
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.exception(e)
        st.info("Vérifiez que votre base de données contient les données nécessaires")

if __name__ == "__main__":
    main()