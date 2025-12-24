"""
Dashboard Doyen - Vue stratégique globale
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration
st.set_page_config(
    page_title="Dashboard Doyen",
    page_icon="🏛️",
    layout="wide"
)

# CSS supplémentaire
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3498db;
        margin-bottom: 1rem;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .dept-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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

def main():
    """Fonction principale du dashboard doyen"""
    
    # Header du dashboard
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; font-size: 2.5rem;">Dashboard Doyen</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Vue stratégique globale - Suivi des examens universitaires
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        periode = st.selectbox(
            "Période",
            ["Semaine en cours", "Mois en cours", "Semestre", "Personnalisée"],
            index=0
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
    
    # Connexion à la base de données
    conn = get_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données")
        return
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Section 1: KPIs Principaux
    st.markdown("### Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cur.execute("""
            SELECT COUNT(DISTINCT e.id) as count
            FROM examens e
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
        """, (date_debut, date_fin))
        nb_examens = cur.fetchone()['count']
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{nb_examens}</div>
            <div class="kpi-label">Examens Planifiés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cur.execute("""
            SELECT COUNT(DISTINCT s.professeur_id) as count
            FROM surveillances s
            JOIN examens e ON s.examen_id = e.id
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
        """, (date_debut, date_fin))
        nb_profs = cur.fetchone()['count']
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{nb_profs}</div>
            <div class="kpi-label">Professeurs Mobilisés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cur.execute("""
            SELECT COUNT(DISTINCT e.lieu_id) as count
            FROM examens e
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
        """, (date_debut, date_fin))
        nb_salles = cur.fetchone()['count']
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{nb_salles}</div>
            <div class="kpi-label">Salles Utilisées</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        cur.execute("""
            SELECT COALESCE(SUM(e.nb_etudiants_inscrits), 0) as total
            FROM examens e
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
        """, (date_debut, date_fin))
        total_places = cur.fetchone()['total']
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_places:,}</div>
            <div class="kpi-label">Places d'Examen</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 2: Graphiques
    st.markdown("### Analyses Visuelles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### Répartition des Examens par Département")
        
        cur.execute("""
            SELECT 
                d.nom as departement,
                COUNT(e.id) as nb_examens,
                SUM(e.nb_etudiants_inscrits) as nb_etudiants
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.departement_id = d.id
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
            GROUP BY d.id, d.nom
            ORDER BY nb_examens DESC
        """, (date_debut, date_fin))
        
        dept_data = cur.fetchall()
        
        if dept_data:
            df_dept = pd.DataFrame(dept_data)
            
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
                margin=dict(t=30, b=30, l=30, r=30)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### Occupation des Salles par Jour")
        
        cur.execute("""
            SELECT 
                e.date_examen,
                COUNT(DISTINCT e.lieu_id) as salles_occupees,
                (SELECT COUNT(*) FROM lieux_examen WHERE est_disponible = TRUE) as salles_total
            FROM examens e
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
            GROUP BY e.date_examen
            ORDER BY e.date_examen
        """, (date_debut, date_fin))
        
        occupancy_data = cur.fetchall()
        
        if occupancy_data:
            df_occupancy = pd.DataFrame(occupancy_data)
            df_occupancy['taux_occupation'] = (df_occupancy['salles_occupees'] / df_occupancy['salles_total'] * 100).round(2)
            
            fig = px.line(
                df_occupancy,
                x='date_examen',
                y='taux_occupation',
                markers=True,
                labels={'date_examen': 'Date', 'taux_occupation': 'Taux d\'occupation (%)'}
            )
            
            fig.update_traces(line_color='#3498db', line_width=3)
            fig.update_layout(
                height=400,
                xaxis_title="",
                yaxis_title="Taux d'occupation (%)",
                margin=dict(t=30, b=30, l=30, r=30)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 3: Détails par Département
    st.markdown("### Détails par Département")
    
    cur.execute("""
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
    """)
    
    all_dept_data = cur.fetchall()
    
    if all_dept_data:
        cols = st.columns(2)
        for idx, dept in enumerate(all_dept_data):
            with cols[idx % 2]:
                color_map = {
                    0: '#3498db',
                    1: '#2ecc71',
                    2: '#e74c3c',
                    3: '#f39c12',
                    4: '#9b59b6',
                    5: '#1abc9c',
                    6: '#34495e'
                }
                
                st.markdown(f"""
                <div class="dept-card" style="border-left-color: {color_map.get(idx, '#3498db')};">
                    <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">{dept['departement']}</h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                        <div>
                            <div style="font-size: 0.8rem; color: #7f8c8d;">Formations</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{dept['nb_formations']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.8rem; color: #7f8c8d;">Modules</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{dept['nb_modules']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.8rem; color: #7f8c8d;">Étudiants</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{dept['nb_etudiants']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.8rem; color: #7f8c8d;">Examens</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{dept['nb_examens']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Section 4: Alertes et Conflits
    st.markdown("### Alertes et Conflits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### Conflits Étudiants")
        
        cur.execute("""
            SELECT COUNT(*) as count
            FROM (
                SELECT i.etudiant_id, e.date_examen
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN inscriptions i ON m.id = i.module_id
                WHERE e.date_examen BETWEEN %s AND %s
                AND e.statut = 'Planifie'
                GROUP BY i.etudiant_id, e.date_examen
                HAVING COUNT(*) > 1
            ) conflits
        """, (date_debut, date_fin))
        
        student_conflicts = cur.fetchone()['count']
        
        if student_conflicts > 0:
            st.error(f"**{student_conflicts}** étudiants ont des conflits d'horaires")
            
            cur.execute("""
                SELECT 
                    e.matricule,
                    e.nom,
                    e.prenom,
                    conflits.date_examen,
                    conflits.nb_examens
                FROM (
                    SELECT 
                        i.etudiant_id,
                        e.date_examen,
                        COUNT(*) as nb_examens
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN inscriptions i ON m.id = i.module_id
                    WHERE e.date_examen BETWEEN %s AND %s
                    AND e.statut = 'Planifie'
                    GROUP BY i.etudiant_id, e.date_examen
                    HAVING COUNT(*) > 1
                ) conflits
                JOIN etudiants e ON conflits.etudiant_id = e.id
                ORDER BY conflits.nb_examens DESC
                LIMIT 5
            """, (date_debut, date_fin))
            
            conflicts_list = cur.fetchall()
            
            for conflict in conflicts_list:
                st.markdown(f"- **{conflict['nom']} {conflict['prenom']}** ({conflict['matricule']}): {conflict['nb_examens']} examens le {conflict['date_examen']}")
        else:
            st.success("Aucun conflit étudiant détecté")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### Surcharge des Professeurs")
        
        cur.execute("""
            SELECT COUNT(*) as count
            FROM (
                SELECT s.professeur_id, e.date_examen
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                WHERE e.date_examen BETWEEN %s AND %s
                AND e.statut = 'Planifie'
                GROUP BY s.professeur_id, e.date_examen
                HAVING COUNT(*) > 3
            ) surcharges
        """, (date_debut, date_fin))
        
        prof_overload = cur.fetchone()['count']
        
        if prof_overload > 0:
            st.warning(f"**{prof_overload}** professeurs sont surchargés")
            
            cur.execute("""
                SELECT 
                    p.nom,
                    p.prenom,
                    surcharges.date_examen,
                    surcharges.nb_surveillances
                FROM (
                    SELECT 
                        s.professeur_id,
                        e.date_examen,
                        COUNT(*) as nb_surveillances
                    FROM surveillances s
                    JOIN examens e ON s.examen_id = e.id
                    WHERE e.date_examen BETWEEN %s AND %s
                    AND e.statut = 'Planifie'
                    GROUP BY s.professeur_id, e.date_examen
                    HAVING COUNT(*) > 3
                ) surcharges
                JOIN professeurs p ON surcharges.professeur_id = p.id
                ORDER BY surcharges.nb_surveillances DESC
                LIMIT 5
            """, (date_debut, date_fin))
            
            overload_list = cur.fetchall()
            
            for overload in overload_list:
                st.markdown(f"- **{overload['nom']} {overload['prenom']}**: {overload['nb_surveillances']} surveillances le {overload['date_examen']}")
        else:
            st.success("Aucune surcharge professeur détectée")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 5: Résumé de Validation
    st.markdown("### Résumé pour Validation")
    
    cur.execute("""
        SELECT 
            'Examens planifiés' as categorie,
            COUNT(*)::text as valeur
        FROM examens
        WHERE statut = 'Planifie'
        AND date_examen BETWEEN %s AND %s
        
        UNION ALL
        
        SELECT 
            'Modules sans examen' as categorie,
            COUNT(*)::text as valeur
        FROM modules m
        WHERE NOT EXISTS (
            SELECT 1 FROM examens e 
            WHERE e.module_id = m.id 
            AND e.statut = 'Planifie'
            AND e.date_examen BETWEEN %s AND %s
        )
        
        UNION ALL
        
        SELECT 
            'Conflits étudiants' as categorie,
            COUNT(DISTINCT etudiant_id || '-' || date_examen)::text as valeur
        FROM (
            SELECT i.etudiant_id, e.date_examen
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN inscriptions i ON m.id = i.module_id
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
            GROUP BY i.etudiant_id, e.date_examen
            HAVING COUNT(*) > 1
        ) conflits
        
        UNION ALL
        
        SELECT 
            'Professeurs mobilisés' as categorie,
            COUNT(DISTINCT professeur_id)::text as valeur
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        WHERE e.date_examen BETWEEN %s AND %s
        AND e.statut = 'Planifie'
    """, (date_debut, date_fin, date_debut, date_fin, date_debut, date_fin, date_debut, date_fin))
    
    summary_data = cur.fetchall()
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Bouton de validation finale
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Valider le Planning Général", type="primary", use_container_width=True):
            st.success("Planning validé avec succès !")
            st.balloons()
    
    # Nettoyage
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()