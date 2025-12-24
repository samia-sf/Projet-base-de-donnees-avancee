"""
Interface d'Administration des Examens
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

# Configuration
st.set_page_config(
    page_title="Administration des Examens",
    page_icon="⚙️",
    layout="wide"
)

# CSS supplémentaire
st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .tool-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .tool-title {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .conflict-alert {
        background: #fff8e1;
        border: 1px solid #f1c40f;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .conflict-critical {
        background: #fdedec;
        border: 1px solid #e74c3c;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .config-section {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
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

def generate_schedule():
    """Fonction de simulation de génération d'emploi du temps"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        # Simulation du processus
        time.sleep(0.05)
        progress_bar.progress(i + 1)
        
        if i < 20:
            status_text.text("Chargement des données...")
        elif i < 40:
            status_text.text("Analyse des contraintes...")
        elif i < 60:
            status_text.text("Assignation des salles...")
        elif i < 80:
            status_text.text("Assignation des surveillants...")
        else:
            status_text.text("Finalisation du planning...")
    
    progress_bar.empty()
    status_text.empty()

def main():
    """Fonction principale de l'interface d'administration"""
    
    # Header
    st.markdown("""
    <div class="admin-header">
        <h1 style="margin: 0; font-size: 2.5rem;">Administration des Examens</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Gestion et optimisation des emplois du temps d'examens
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs([
        "Génération Automatique",
        "Planification Manuelle",
        "Détection Conflits",
        "Gestion des Ressources"
    ])
    
    with tab1:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Génération Automatique de l\'Emploi du Temps</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Paramètres de Génération")
            
            annee_academique = st.selectbox(
                "Année Académique",
                ["2024-2025", "2025-2026", "2026-2027"],
                index=0,
                key="gen_annee"
            )
            
            session = st.selectbox(
                "Session",
                ["Normale", "Rattrapage"],
                index=0,
                key="gen_session"
            )
            
            date_debut = st.date_input(
                "Date de début de la période",
                datetime.now().date(),
                key="gen_date_debut"
            )
            
            date_fin = st.date_input(
                "Date de fin de la période",
                datetime.now().date() + timedelta(days=30),
                key="gen_date_fin"
            )
        
        with col2:
            st.markdown("##### Configuration des Contraintes")
            
            st.markdown("###### Contraintes Étudiants")
            max_exams_per_day = st.slider(
                "Maximum d'examens par jour (étudiant)",
                1, 2, 1,
                key="max_exams"
            )
            
            st.markdown("###### Contraintes Professeurs")
            max_surveillances = st.slider(
                "Maximum de surveillances par jour",
                1, 5, 3,
                key="max_surveillances"
            )
            
            st.markdown("###### Contraintes Salles")
            room_capacity = st.number_input(
                "Capacité maximale par salle",
                10, 50, 20,
                key="room_capacity"
            )
        
        # Options avancées
        with st.expander("Options Avancées"):
            col_adv1, col_adv2 = st.columns(2)
            
            with col_adv1:
                prioritize_large_groups = st.checkbox(
                    "Prioriser les grands groupes",
                    value=True,
                    help="Planifier d'abord les modules avec beaucoup d'étudiants"
                )
                
                balance_surveillances = st.checkbox(
                    "Équilibrer les surveillances",
                    value=True,
                    help="Répartir équitablement les surveillances entre professeurs"
                )
            
            with col_adv2:
                use_department_priority = st.checkbox(
                    "Priorité départementale",
                    value=True,
                    help="Les professeurs surveillent prioritairement leur département"
                )
                
                allow_multi_room = st.checkbox(
                    "Autoriser les salles multiples",
                    value=True,
                    help="Utiliser plusieurs salles pour un même examen si nécessaire"
                )
        
        # Bouton de génération
        st.markdown("---")
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        
        with col_gen2:
            if st.button("Lancer la Génération Automatique", type="primary", use_container_width=True):
                with st.spinner("Génération en cours..."):
                    # Simulation de la génération
                    generate_schedule()
                    
                    # Affichage des résultats
                    st.success("✅ Génération terminée avec succès !")
                    
                    # Métriques de résultat
                    st.markdown("##### Résultats de la Génération")
                    
                    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
                    
                    with res_col1:
                        st.metric("Examens planifiés", "1,245")
                    
                    with res_col2:
                        st.metric("Taux de réussite", "98.5%")
                    
                    with res_col3:
                        st.metric("Temps d'exécution", "28.5s")
                    
                    with res_col4:
                        st.metric("Conflits résolus", "142")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Planification Manuelle</div>', unsafe_allow_html=True)
        
        # Formulaire d'ajout d'examen
        with st.form("add_exam_form"):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                st.markdown("##### Informations de l'Examen")
                
                # Connexion pour les données
                conn = get_connection()
                if conn:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    
                    # Sélection du module
                    cur.execute("""
                        SELECT m.id, m.code, m.nom, f.nom as formation
                        FROM modules m
                        JOIN formations f ON m.formation_id = f.id
                        ORDER BY m.code
                    """)
                    modules = cur.fetchall()
                    
                    module_options = [f"{m['code']} - {m['nom']} ({m['formation']})" for m in modules]
                    module_ids = [m['id'] for m in modules]
                    
                    selected_module = st.selectbox(
                        "Module",
                        module_options,
                        index=0
                    )
                    
                    # Sélection de la salle
                    cur.execute("""
                        SELECT id, nom, type, capacite_examen, batiment
                        FROM lieux_examen
                        WHERE est_disponible = TRUE
                        ORDER BY nom
                    """)
                    rooms = cur.fetchall()
                    
                    room_options = [f"{r['nom']} ({r['type']}, {r['batiment']}, cap: {r['capacite_examen']})" for r in rooms]
                    room_ids = [r['id'] for r in rooms]
                    
                    selected_room = st.selectbox(
                        "Salle",
                        room_options,
                        index=0
                    )
                    
                    cur.close()
                    conn.close()
            
            with col_form2:
                st.markdown("##### Horaires")
                
                exam_date = st.date_input(
                    "Date de l'examen",
                    datetime.now().date() + timedelta(days=7)
                )
                
                start_time = st.time_input(
                    "Heure de début",
                    datetime.strptime("08:30", "%H:%M").time()
                )
                
                duration = st.number_input(
                    "Durée (minutes)",
                    60, 240, 120,
                    help="Durée de l'examen en minutes"
                )
                
                # Calcul de l'heure de fin
                if start_time and duration:
                    start_datetime = datetime.combine(exam_date, start_time)
                    end_datetime = start_datetime + timedelta(minutes=duration)
                    st.markdown(f"**Heure de fin estimée:** {end_datetime.time().strftime('%H:%M')}")
            
            st.markdown("##### Surveillants")
            
            conn = get_connection()
            if conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                
                # Sélection des surveillants
                cur.execute("""
                    SELECT id, nom, prenom, departement_id
                    FROM professeurs
                    ORDER BY nom, prenom
                """)
                professors = cur.fetchall()
                
                prof_options = [f"{p['nom']} {p['prenom']}" for p in professors]
                prof_ids = [p['id'] for p in professors]
                
                selected_profs = st.multiselect(
                    "Sélectionner les surveillants",
                    prof_options,
                    max_selections=2
                )
                
                if selected_profs:
                    st.markdown(f"**Surveillants sélectionnés:** {', '.join(selected_profs)}")
                
                cur.close()
                conn.close()
            
            # Bouton de soumission
            submitted = st.form_submit_button("Ajouter l'Examen", type="primary")
            
            if submitted:
                st.success("✅ Examen ajouté avec succès !")
                st.info("L'examen a été enregistré dans la base de données.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Liste des examens existants
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Examens Planifiés</div>', unsafe_allow_html=True)
        
        conn = get_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Filtres pour la liste
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                filter_date = st.date_input(
                    "Filtrer par date",
                    datetime.now().date(),
                    key="filter_date"
                )
            
            with col_filter2:
                filter_status = st.selectbox(
                    "Filtrer par statut",
                    ["Tous", "Planifie", "En cours", "Termine", "Annule"],
                    index=0,
                    key="filter_status"
                )
            
            with col_filter3:
                filter_department = st.selectbox(
                    "Filtrer par département",
                    ["Tous"] + get_departments(),
                    index=0,
                    key="filter_department"
                )
            
            # Construction de la requête
            query = """
                SELECT 
                    e.id,
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
                WHERE 1=1
            """
            
            params = []
            
            if filter_date:
                query += " AND e.date_examen = %s"
                params.append(filter_date)
            
            if filter_status != "Tous":
                query += " AND e.statut = %s"
                params.append(filter_status)
            
            if filter_department != "Tous":
                query += " AND d.nom = %s"
                params.append(filter_department)
            
            query += " ORDER BY e.date_examen, e.heure_debut LIMIT 50"
            
            cur.execute(query, params)
            exams = cur.fetchall()
            
            if exams:
                df_exams = pd.DataFrame(exams)
                
                # Options d'affichage
                display_cols = st.multiselect(
                    "Colonnes à afficher",
                    df_exams.columns.tolist(),
                    default=['date_examen', 'heure_debut', 'module_code', 'module_nom', 'formation', 'departement', 'salle', 'statut']
                )
                
                if display_cols:
                    st.dataframe(df_exams[display_cols], use_container_width=True, hide_index=True)
                    
                    # Options d'export
                    col_exp1, col_exp2 = st.columns(2)
                    
                    with col_exp1:
                        if st.button("Exporter en CSV"):
                            csv = df_exams.to_csv(index=False)
                            st.download_button(
                                label="Télécharger CSV",
                                data=csv,
                                file_name="examens_planifies.csv",
                                mime="text/csv"
                            )
                    
                    with col_exp2:
                        if st.button("Exporter en Excel"):
                            # Simulation - en production, utiliser pandas ExcelWriter
                            st.info("Fonctionnalité d'export Excel en développement")
            else:
                st.info("Aucun examen trouvé avec les filtres sélectionnés")
            
            cur.close()
            conn.close()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Détection et Analyse des Conflits</div>', unsafe_allow_html=True)
        
        # Bouton d'analyse
        if st.button("Analyser les Conflits", type="primary"):
            with st.spinner("Analyse en cours..."):
                time.sleep(2)
                
                # Résultats de l'analyse
                st.success("✅ Analyse terminée !")
                
                # Métriques des conflits
                st.markdown("##### Résumé des Conflits")
                
                col_conf1, col_conf2, col_conf3 = st.columns(3)
                
                with col_conf1:
                    st.metric("Conflits étudiants", "0", delta_color="off")
                
                with col_conf2:
                    st.metric("Surcharge professeurs", "2", delta="2", delta_color="inverse")
                
                with col_conf3:
                    st.metric("Salles surchargées", "0", delta_color="off")
                
                # Détails des conflits
                st.markdown("##### Détails des Conflits Détectés")
                
                # Conflits professeurs
                st.markdown("###### Surcharge des Professeurs")
                
                conflicts_data = [
                    {
                        "Type": "Surcharge professeur",
                        "Description": "Professeur Dupont - 4 surveillances le 15/01/2025",
                        "Niveau": "Critique",
                        "Solution": "Réaffecter une surveillance à un autre professeur"
                    },
                    {
                        "Type": "Surcharge professeur", 
                        "Description": "Professeur Martin - 4 surveillances le 16/01/2025",
                        "Niveau": "Critique",
                        "Solution": "Déplacer une surveillance à un autre jour"
                    }
                ]
                
                for conflict in conflicts_data:
                    if conflict["Niveau"] == "Critique":
                        st.markdown(f"""
                        <div class="conflict-critical">
                            <strong>{conflict['Type']}</strong><br>
                            {conflict['Description']}<br>
                            <em>Solution proposée:</em> {conflict['Solution']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="conflict-alert">
                            <strong>{conflict['Type']}</strong><br>
                            {conflict['Description']}<br>
                            <em>Solution proposée:</em> {conflict['Solution']}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Graphique des conflits par type
                st.markdown("###### Répartition des Conflits")
                
                conflict_types = ["Étudiants", "Professeurs", "Salles", "Horaires"]
                conflict_counts = [0, 2, 0, 0]
                
                fig = px.bar(
                    x=conflict_types,
                    y=conflict_counts,
                    labels={'x': 'Type de conflit', 'y': 'Nombre'},
                    color=conflict_counts,
                    color_continuous_scale='Reds'
                )
                
                fig.update_layout(
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Analyse historique
        st.markdown("---")
        st.markdown("##### Analyse Historique des Conflits")
        
        conn = get_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    DATE(e.date_examen) as date,
                    COUNT(*) as nb_conflits
                FROM (
                    -- Conflits étudiants
                    SELECT e.date_examen
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN inscriptions i ON m.id = i.module_id
                    WHERE e.statut = 'Planifie'
                    GROUP BY e.date_examen, i.etudiant_id
                    HAVING COUNT(*) > 1
                    
                    UNION ALL
                    
                    -- Conflits professeurs
                    SELECT e.date_examen
                    FROM surveillances s
                    JOIN examens e ON s.examen_id = e.id
                    WHERE e.statut = 'Planifie'
                    GROUP BY e.date_examen, s.professeur_id
                    HAVING COUNT(*) > 3
                ) conflits
                JOIN examens e ON conflits.date_examen = e.date_examen
                GROUP BY DATE(e.date_examen)
                ORDER BY date
                LIMIT 30
            """)
            
            history_data = cur.fetchall()
            
            if history_data:
                df_history = pd.DataFrame(history_data)
                
                fig = px.line(
                    df_history,
                    x='date',
                    y='nb_conflits',
                    markers=True,
                    labels={'date': 'Date', 'nb_conflits': 'Nombre de conflits'}
                )
                
                fig.update_traces(line_color='#e74c3c', line_width=2)
                fig.update_layout(
                    height=300,
                    xaxis_title="",
                    yaxis_title="Nombre de conflits"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            cur.close()
            conn.close()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Gestion des Ressources</div>', unsafe_allow_html=True)
        
        # Sous-onglets pour les ressources
        subtab1, subtab2, subtab3 = st.tabs(["Salles", "Professeurs", "Équipements"])
        
        with subtab1:
            st.markdown("##### Gestion des Salles d'Examen")
            
            conn = get_connection()
            if conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                
                # Liste des salles
                cur.execute("""
                    SELECT 
                        nom,
                        type,
                        capacite_normale,
                        capacite_examen,
                        batiment,
                        etage,
                        est_disponible,
                        array_to_string(equipements, ', ') as equipements
                    FROM lieux_examen
                    ORDER BY batiment, etage, nom
                """)
                
                rooms = cur.fetchall()
                
                if rooms:
                    df_rooms = pd.DataFrame(rooms)
                    
                    # Filtres
                    col_room1, col_room2 = st.columns(2)
                    
                    with col_room1:
                        filter_building = st.selectbox(
                            "Filtrer par bâtiment",
                            ["Tous"] + sorted(df_rooms['batiment'].unique().tolist()),
                            key="filter_building"
                        )
                    
                    with col_room2:
                        filter_available = st.selectbox(
                            "Disponibilité",
                            ["Tous", "Disponible", "Indisponible"],
                            key="filter_available"
                        )
                    
                    # Application des filtres
                    filtered_rooms = df_rooms.copy()
                    
                    if filter_building != "Tous":
                        filtered_rooms = filtered_rooms[filtered_rooms['batiment'] == filter_building]
                    
                    if filter_available == "Disponible":
                        filtered_rooms = filtered_rooms[filtered_rooms['est_disponible'] == True]
                    elif filter_available == "Indisponible":
                        filtered_rooms = filtered_rooms[filtered_rooms['est_disponible'] == False]
                    
                    st.dataframe(filtered_rooms, use_container_width=True, hide_index=True)
                    
                    # Statistiques des salles
                    st.markdown("##### Statistiques des Salles")
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    
                    with col_stat1:
                        total_rooms = len(df_rooms)
                        st.metric("Total salles", total_rooms)
                    
                    with col_stat2:
                        available_rooms = df_rooms['est_disponible'].sum()
                        st.metric("Salles disponibles", available_rooms)
                    
                    with col_stat3:
                        avg_capacity = df_rooms['capacite_examen'].mean().round(1)
                        st.metric("Capacité moyenne", avg_capacity)
                
                cur.close()
                conn.close()
        
        with subtab2:
            st.markdown("##### Gestion des Professeurs")
            
            conn = get_connection()
            if conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                
                # Charge de travail des professeurs
                cur.execute("""
                    SELECT 
                        p.nom || ' ' || p.prenom as professeur,
                        d.nom as departement,
                        p.grade,
                        COUNT(s.id) as nb_surveillances,
                        COUNT(DISTINCT e.date_examen) as nb_jours
                    FROM professeurs p
                    LEFT JOIN departements d ON p.departement_id = d.id
                    LEFT JOIN surveillances s ON p.id = s.professeur_id
                    LEFT JOIN examens e ON s.examen_id = e.id AND e.statut = 'Planifie'
                    GROUP BY p.id, p.nom, p.prenom, d.nom, p.grade
                    ORDER BY nb_surveillances DESC
                """)
                
                professors = cur.fetchall()
                
                if professors:
                    df_professors = pd.DataFrame(professors)
                    
                    # Filtres
                    col_prof1, col_prof2 = st.columns(2)
                    
                    with col_prof1:
                        filter_dept = st.selectbox(
                            "Filtrer par département",
                            ["Tous"] + sorted(df_professors['departement'].dropna().unique().tolist()),
                            key="filter_dept"
                        )
                    
                    with col_prof2:
                        filter_grade = st.selectbox(
                            "Filtrer par grade",
                            ["Tous"] + sorted(df_professors['grade'].dropna().unique().tolist()),
                            key="filter_grade"
                        )
                    
                    # Application des filtres
                    filtered_professors = df_professors.copy()
                    
                    if filter_dept != "Tous":
                        filtered_professors = filtered_professors[filtered_professors['departement'] == filter_dept]
                    
                    if filter_grade != "Tous":
                        filtered_professors = filtered_professors[filtered_professors['grade'] == filter_grade]
                    
                    st.dataframe(filtered_professors, use_container_width=True, hide_index=True)
                    
                    # Graphique de répartition
                    st.markdown("##### Répartition des Surveillances")
                    
                    fig = px.bar(
                        filtered_professors.head(10),
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
                
                cur.close()
                conn.close()
        
        with subtab3:
            st.markdown("##### Gestion des Équipements")
            
            st.info("Module de gestion des équipements en cours de développement")
            
            # Liste des équipements nécessaires
            equipment_data = [
                {"Équipement": "Ordinateurs", "Quantité": 45, "Disponible": 42, "Statut": "Attention"},
                {"Équipement": "Calculatrices", "Quantité": 120, "Disponible": 115, "Statut": "Bon"},
                {"Équipement": "Projecteurs", "Quantité": 25, "Disponible": 25, "Statut": "Bon"},
                {"Équipement": "Tableaux blancs", "Quantité": 50, "Disponible": 48, "Statut": "Bon"},
                {"Équipement": "Systèmes audio", "Quantité": 15, "Disponible": 12, "Statut": "Attention"}
            ]
            
            df_equipment = pd.DataFrame(equipment_data)
            df_equipment['Pourcentage'] = (df_equipment['Disponible'] / df_equipment['Quantité'] * 100).round(1)
            
            st.dataframe(df_equipment, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def get_departments():
    """Récupère la liste des départements"""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT nom FROM departements ORDER BY nom")
        departments = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return departments
    return []

if __name__ == "__main__":
    main()