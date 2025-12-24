"""
Interface Chef de Département
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuration
st.set_page_config(
    page_title="Chef de Département",
    page_icon="📊",
    layout="wide"
)

# CSS supplémentaire
st.markdown("""
<style>
    .chef-header {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .dept-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    .dept-title {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2ecc71;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    @media (max-width: 1200px) {
        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .metric-grid {
            grid-template-columns: 1fr;
        }
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
        line-height: 1;
    }
    
    .grid-label {
        font-size: 0.85rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .validation-panel {
        background: #e8f6ef;
        border: 1px solid #2ecc71;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .warning-panel {
        background: #fff8e1;
        border: 1px solid #f39c12;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
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

def get_department_id(dept_name):
    """Récupère l'ID d'un département par son nom"""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM departements WHERE nom = %s", (dept_name,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    return None

def main():
    """Fonction principale de l'interface chef de département"""
    
    # Header
    st.markdown("""
    <div class="chef-header">
        <h1 style="margin: 0; font-size: 2.5rem;">Interface Chef de Département</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Gestion et suivi des examens de votre département
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection du département
    conn = get_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données")
        return
    
    cur = conn.cursor()
    cur.execute("SELECT nom FROM departements ORDER BY nom")
    departments = [row[0] for row in cur.fetchall()]
    cur.close()
    
    if not departments:
        st.error("Aucun département trouvé dans la base de données")
        conn.close()
        return
    
    # Sélection du département (avec session state pour persistance)
    if 'selected_department' not in st.session_state:
        st.session_state.selected_department = departments[0]
    
    selected_department = st.selectbox(
        "Sélectionnez votre département",
        departments,
        index=departments.index(st.session_state.selected_department)
        if st.session_state.selected_department in departments else 0
    )
    
    st.session_state.selected_department = selected_department
    
    # Récupération de l'ID du département
    dept_id = get_department_id(selected_department)
    
    if not dept_id:
        st.error(f"Département '{selected_department}' introuvable")
        conn.close()
        return
    
    # Filtres de période
    col1, col2 = st.columns(2)
    
    with col1:
        period = st.selectbox(
            "Période",
            ["Semaine en cours", "Mois en cours", "Semestre", "Personnalisée"],
            index=1
        )
    
    with col2:
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
    
    # Section 1: Vue d'ensemble du département
    st.markdown(f'<div class="dept-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="dept-title">Vue d\'Ensemble - {selected_department}</div>', unsafe_allow_html=True)
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Métriques du département
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    
    # Nombre de formations
    cur.execute("SELECT COUNT(*) as count FROM formations WHERE departement_id = %s", (dept_id,))
    nb_formations = cur.fetchone()['count']
    
    st.markdown(f"""
    <div class="grid-metric">
        <div class="grid-value">{nb_formations}</div>
        <div class="grid-label">Formations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nombre d'étudiants
    cur.execute("""
        SELECT COUNT(DISTINCT e.id) as count
        FROM etudiants e
        JOIN formations f ON e.formation_id = f.id
        WHERE f.departement_id = %s
    """, (dept_id,))
    nb_etudiants = cur.fetchone()['count']
    
    st.markdown(f"""
    <div class="grid-metric">
        <div class="grid-value">{nb_etudiants:,}</div>
        <div class="grid-label">Étudiants</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nombre de professeurs
    cur.execute("SELECT COUNT(*) as count FROM professeurs WHERE departement_id = %s", (dept_id,))
    nb_professeurs = cur.fetchone()['count']
    
    st.markdown(f"""
    <div class="grid-metric">
        <div class="grid-value">{nb_professeurs}</div>
        <div class="grid-label">Professeurs</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nombre d'examens planifiés
    cur.execute("""
        SELECT COUNT(DISTINCT e.id) as count
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.departement_id = %s
        AND e.date_examen BETWEEN %s AND %s
        AND e.statut = 'Planifie'
    """, (dept_id, date_debut, date_fin))
    nb_examens = cur.fetchone()['count']
    
    st.markdown(f"""
    <div class="grid-metric">
        <div class="grid-value">{nb_examens}</div>
        <div class="grid-label">Examens Planifiés</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs([
        "Examens du Département",
        "Surveillances",
        "Conflits et Alertes",
        "Validation Départementale"
    ])
    
    with tab1:
        st.markdown('<div class="dept-card">', unsafe_allow_html=True)
        st.markdown('<div class="dept-title">Examens du Département</div>', unsafe_allow_html=True)
        
        # Liste des examens
        cur.execute("""
            SELECT 
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                f.niveau,
                l.nom as salle,
                l.type as type_salle,
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
            df_exams = pd.DataFrame(dept_exams)
            
            # Filtres supplémentaires
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                filter_formation = st.selectbox(
                    "Filtrer par formation",
                    ["Toutes"] + sorted(df_exams['formation'].unique().tolist()),
                    key="filter_formation"
                )
            
            with col_filter2:
                filter_niveau = st.selectbox(
                    "Filtrer par niveau",
                    ["Tous"] + sorted(df_exams['niveau'].dropna().unique().tolist()),
                    key="filter_niveau"
                )
            
            with col_filter3:
                filter_statut = st.selectbox(
                    "Filtrer par statut",
                    ["Tous"] + sorted(df_exams['statut'].unique().tolist()),
                    key="filter_statut"
                )
            
            # Application des filtres
            filtered_exams = df_exams.copy()
            
            if filter_formation != "Toutes":
                filtered_exams = filtered_exams[filtered_exams['formation'] == filter_formation]
            
            if filter_niveau != "Tous":
                filtered_exams = filtered_exams[filtered_exams['niveau'] == filter_niveau]
            
            if filter_statut != "Tous":
                filtered_exams = filtered_exams[filtered_exams['statut'] == filter_statut]
            
            # Affichage du tableau
            st.dataframe(filtered_exams, use_container_width=True, hide_index=True)
            
            # Statistiques
            st.markdown("##### Statistiques des Examens")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_exams = len(filtered_exams)
                st.metric("Total examens", total_exams)
            
            with col_stat2:
                total_students = filtered_exams['nb_etudiants_inscrits'].sum()
                st.metric("Total étudiants", f"{total_students:,}")
            
            with col_stat3:
                unique_rooms = filtered_exams['salle'].nunique()
                st.metric("Salles utilisées", unique_rooms)
            
            with col_stat4:
                if not filtered_exams.empty:
                    avg_students = filtered_exams['nb_etudiants_inscrits'].mean().round(1)
                    st.metric("Moyenne étudiants", avg_students)
            
            # Graphique: Examens par jour
            st.markdown("##### Répartition des Examens par Jour")
            
            exams_per_day = filtered_exams.groupby('date_examen').size().reset_index(name='nb_examens')
            
            if not exams_per_day.empty:
                fig = px.bar(
                    exams_per_day,
                    x='date_examen',
                    y='nb_examens',
                    labels={'date_examen': 'Date', 'nb_examens': "Nombre d'examens"},
                    color='nb_examens',
                    color_continuous_scale='Greens'
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="",
                    yaxis_title="Nombre d'examens",
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Aucun examen planifié pour le département {selected_department} dans la période sélectionnée")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="dept-card">', unsafe_allow_html=True)
        st.markdown('<div class="dept-title">Gestion des Surveillances</div>', unsafe_allow_html=True)
        
        # Charge de travail des professeurs du département
        cur.execute("""
            SELECT 
                p.nom || ' ' || p.prenom as professeur,
                p.grade,
                COUNT(s.id) as nb_surveillances,
                COUNT(DISTINCT e.date_examen) as nb_jours,
                ROUND(AVG(e.duree_minutes)::numeric, 1) as duree_moyenne
            FROM professeurs p
            LEFT JOIN surveillances s ON p.id = s.professeur_id
            LEFT JOIN examens e ON s.examen_id = e.id AND e.statut = 'Planifie'
            WHERE p.departement_id = %s
            AND (e.date_examen BETWEEN %s AND %s OR e.date_examen IS NULL)
            GROUP BY p.id, p.nom, p.prenom, p.grade
            ORDER BY nb_surveillances DESC
        """, (dept_id, date_debut, date_fin))
        
        surveillances = cur.fetchall()
        
        if surveillances:
            df_surveillances = pd.DataFrame(surveillances)
            
            # Filtre par grade
            grades = ["Tous"] + sorted(df_surveillances['grade'].dropna().unique().tolist())
            selected_grade = st.selectbox("Filtrer par grade", grades, key="filter_grade_surv")
            
            if selected_grade != "Tous":
                df_surveillances = df_surveillances[df_surveillances['grade'] == selected_grade]
            
            st.dataframe(df_surveillances, use_container_width=True, hide_index=True)
            
            # Graphique: Répartition des surveillances
            st.markdown("##### Répartition des Surveillances")
            
            if len(df_surveillances) > 0:
                fig = px.bar(
                    df_surveillances.head(15),
                    x='professeur',
                    y='nb_surveillances',
                    color='nb_surveillances',
                    color_continuous_scale='Viridis',
                    labels={'professeur': 'Professeur', 'nb_surveillances': 'Nombre de surveillances'}
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="",
                    yaxis_title="Nombre de surveillances",
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Alertes de surcharge
            st.markdown("##### Alertes de Surcharge")
            
            overloaded_profs = df_surveillances[df_surveillances['nb_surveillances'] > 10]
            
            if not overloaded_profs.empty:
                st.warning("Certains professeurs ont une charge élevée de surveillances:")
                
                for _, prof in overloaded_profs.iterrows():
                    st.markdown(f"- **{prof['professeur']}**: {prof['nb_surveillances']} surveillances")
            else:
                st.success("Aucune surcharge détectée parmi les professeurs du département")
        else:
            st.info("Aucune donnée de surveillance disponible pour ce département")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="dept-card">', unsafe_allow_html=True)
        st.markdown('<div class="dept-title">Conflits et Alertes Départementaux</div>', unsafe_allow_html=True)
        
        # Conflits étudiants
        st.markdown("##### Conflits d'Horaires Étudiants")
        
        cur.execute("""
            SELECT 
                e.matricule,
                e.nom,
                e.prenom,
                f.nom as formation,
                conflits.date_examen,
                conflits.nb_examens,
                string_agg(m.code, ', ' ORDER BY ex.heure_debut) as modules
            FROM (
                SELECT 
                    i.etudiant_id,
                    e.date_examen,
                    COUNT(*) as nb_examens
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN inscriptions i ON m.id = i.module_id
                JOIN formations f ON m.formation_id = f.id
                WHERE f.departement_id = %s
                AND e.date_examen BETWEEN %s AND %s
                AND e.statut = 'Planifie'
                GROUP BY i.etudiant_id, e.date_examen
                HAVING COUNT(*) > 1
            ) conflits
            JOIN etudiants e ON conflits.etudiant_id = e.id
            JOIN formations f ON e.formation_id = f.id
            JOIN examens ex ON ex.date_examen = conflits.date_examen
            JOIN modules m ON ex.module_id = m.id
            JOIN inscriptions i2 ON m.id = i2.module_id AND i2.etudiant_id = e.id
            GROUP BY e.id, e.matricule, e.nom, e.prenom, f.nom, conflits.date_examen, conflits.nb_examens
            ORDER BY conflits.nb_examens DESC
            LIMIT 20
        """, (dept_id, date_debut, date_fin))
        
        student_conflicts = cur.fetchall()
        
        if student_conflicts:
            st.markdown('<div class="warning-panel">', unsafe_allow_html=True)
            st.warning(f"{len(student_conflicts)} étudiants ont des conflits d'horaires")
            
            df_conflicts = pd.DataFrame(student_conflicts)
            st.dataframe(df_conflicts, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("Aucun conflit étudiant détecté dans le département")
        
        # Surcharge professeurs
        st.markdown("##### Surcharge des Professeurs")
        
        cur.execute("""
            SELECT 
                p.nom || ' ' || p.prenom as professeur,
                surcharges.date_examen,
                surcharges.nb_surveillances
            FROM (
                SELECT 
                    s.professeur_id,
                    e.date_examen,
                    COUNT(*) as nb_surveillances
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                WHERE f.departement_id = %s
                AND e.date_examen BETWEEN %s AND %s
                AND e.statut = 'Planifie'
                GROUP BY s.professeur_id, e.date_examen
                HAVING COUNT(*) > 3
            ) surcharges
            JOIN professeurs p ON surcharges.professeur_id = p.id
            ORDER BY surcharges.nb_surveillances DESC
        """, (dept_id, date_debut, date_fin))
        
        prof_overload = cur.fetchall()
        
        if prof_overload:
            st.markdown('<div class="warning-panel">', unsafe_allow_html=True)
            st.warning(f"{len(prof_overload)} professeurs sont surchargés")
            
            for overload in prof_overload:
                st.markdown(f"- **{overload['professeur']}**: {overload['nb_surveillances']} surveillances le {overload['date_examen']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("Aucune surcharge professeur détectée dans le département")
        
        # Salles surchargées
        st.markdown("##### Capacité des Salles")
        
        cur.execute("""
            SELECT 
                l.nom as salle,
                e.nb_etudiants_inscrits,
                l.capacite_examen,
                (e.nb_etudiants_inscrits - l.capacite_examen) as depassement,
                m.code as module_code,
                e.date_examen
            FROM examens e
            JOIN lieux_examen l ON e.lieu_id = l.id
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.departement_id = %s
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut = 'Planifie'
            AND e.nb_etudiants_inscrits > l.capacite_examen
            ORDER BY depassement DESC
        """, (dept_id, date_debut, date_fin))
        
        room_overload = cur.fetchall()
        
        if room_overload:
            st.markdown('<div class="warning-panel">', unsafe_allow_html=True)
            st.error(f"{len(room_overload)} salles sont surchargées")
            
            df_room_overload = pd.DataFrame(room_overload)
            st.dataframe(df_room_overload, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("Aucune salle surchargée détectée dans le département")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="dept-card">', unsafe_allow_html=True)
        st.markdown('<div class="dept-title">Validation Départementale</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="validation-panel">
            <h4>Validation du Planning Départemental</h4>
            <p>Cette section vous permet de valider le planning des examens de votre département 
            avant la validation finale par le doyen.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Résumé pour validation
        col_val1, col_val2 = st.columns(2)
        
        with col_val1:
            st.markdown("##### État du Planning")
            
            validation_status = {
                "Examens planifiés": nb_examens,
                "Conflits étudiants": len(student_conflicts) if 'student_conflicts' in locals() else 0,
                "Surcharge professeurs": len(prof_overload) if 'prof_overload' in locals() else 0,
                "Salles surchargées": len(room_overload) if 'room_overload' in locals() else 0
            }
            
            for label, value in validation_status.items():
                if "Conflits" in label or "Surcharge" in label or "Salles" in label:
                    if value > 0:
                        st.error(f"{label}: {value}")
                    else:
                        st.success(f"{label}: {value}")
                else:
                    st.info(f"{label}: {value}")
        
        with col_val2:
            st.markdown("##### Actions de Validation")
            
            # Commentaires
            commentaires = st.text_area(
                "Commentaires pour la validation",
                placeholder="Ajoutez vos commentaires ou remarques sur le planning...",
                height=100
            )
            
            # Options de validation
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("✅ Valider", type="primary", use_container_width=True):
                    st.success(f"Planning du département {selected_department} validé avec succès !")
                    if commentaires:
                        st.info(f"Commentaires enregistrés: {commentaires}")
            
            with col_btn2:
                if st.button("⚠️ Valider avec Réserves", use_container_width=True):
                    st.warning(f"Planning validé avec réserves pour le département {selected_department}")
                    if commentaires:
                        st.info(f"Commentaires enregistrés: {commentaires}")
            
            with col_btn3:
                if st.button("❌ Rejeter", use_container_width=True):
                    st.error(f"Planning rejeté pour le département {selected_department}")
                    if commentaires:
                        st.info(f"Commentaires enregistrés: {commentaires}")
        
        # Rapport de validation
        st.markdown("##### Générer un Rapport")
        
        if st.button("Générer le Rapport de Validation", use_container_width=True):
            # Simulation de génération de rapport
            st.info("Génération du rapport en cours...")
            
            # Création d'un rapport fictif
            report_content = f"""
            RAPPORT DE VALIDATION - DÉPARTEMENT {selected_department.upper()}
            Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            Période: {date_debut} au {date_fin}
            
            1. STATISTIQUES GÉNÉRALES
            - Formations: {nb_formations}
            - Étudiants: {nb_etudiants:,}
            - Professeurs: {nb_professeurs}
            - Examens planifiés: {nb_examens}
            
            2. CONFLITS DÉTECTÉS
            - Conflits étudiants: {len(student_conflicts) if 'student_conflicts' in locals() else 0}
            - Surcharge professeurs: {len(prof_overload) if 'prof_overload' in locals() else 0}
            - Salles surchargées: {len(room_overload) if 'room_overload' in locals() else 0}
            
            3. COMMENTAIRES
            {commentaires if commentaires else "Aucun commentaire"}
            
            4. RECOMMANDATIONS
            - Vérifier les conflits étudiants identifiés
            - Rééquilibrer la charge des professeurs surchargés
            - S'assurer de la capacité des salles pour les prochains examens
            """
            
            st.download_button(
                label="Télécharger le Rapport (TXT)",
                data=report_content,
                file_name=f"validation_{selected_department}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Nettoyage
    conn.close()

if __name__ == "__main__":
    main()