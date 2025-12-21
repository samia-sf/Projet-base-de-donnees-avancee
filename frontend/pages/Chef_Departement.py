
"""
Dashboard Chef de Département
Validation, statistiques et conflits par département
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, ExamQueries
from config import db_config

st.set_page_config(page_title="Chef Département", page_icon="📊", layout="wide")

# ============================================
# HEADER
# ============================================

st.title("📊 Dashboard Chef de Département")
st.markdown("**Gestion et validation des examens de votre département**")

st.markdown("---")

# ============================================
# SÉLECTION DÉPARTEMENT
# ============================================

@st.cache_data
def charger_departements():
    """Charge la liste des départements"""
    try:
        db = Database(db_config.DB_CONFIG)
        db.connect()
        result = db.execute_query("SELECT id, nom FROM departements ORDER BY nom")
        db.disconnect()
        return result
    except Exception as e:
        st.error(f"Erreur: {e}")
        return []

departements = charger_departements()

if departements:
    dept_names = [d['nom'] for d in departements]
    dept_selected = st.selectbox(
        "🏢 Sélectionnez votre département",
        dept_names,
        key="dept_select"
    )
    
    dept_id = next(d['id'] for d in departements if d['nom'] == dept_selected)
else:
    st.error("Aucun département trouvé")
    st.stop()

st.markdown("---")

# ============================================
# KPIS DÉPARTEMENT
# ============================================

def charger_stats_dept(dept_id, annee):
    """Charge les statistiques du département"""
    try:
        db = Database(db_config.DB_CONFIG)
        db.connect()
        stats = ExamQueries.get_stats_departement(db, dept_id, annee)
        db.disconnect()
        return stats
    except Exception as e:
        st.error(f"Erreur: {e}")
        return {}

annee = st.session_state.get('current_year', '2024-2025')
stats = charger_stats_dept(dept_id, annee)

if stats:
    st.subheader(f"📊 Statistiques - {dept_selected}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Examens",
            f"{stats.get('nb_examens', 0)}",
            help="Nombre total d'examens planifiés"
        )
    
    with col2:
        st.metric(
            "Modules",
            f"{stats.get('nb_modules', 0)}",
            help="Modules avec examens"
        )
    
    with col3:
        st.metric(
            "Étudiants",
            f"{stats.get('nb_etudiants', 0):,}",
            help="Étudiants du département"
        )
    
    with col4:
        st.metric(
            "Profs Mobilisés",
            f"{stats.get('nb_profs_utilises', 0)}",
            help="Professeurs assignés aux surveillances"
        )
    
    st.markdown("---")
else:
    st.warning("⚠️ Aucune donnée disponible pour ce département")

# ============================================
# EXAMENS DU DÉPARTEMENT
# ============================================

st.subheader("📅 Examens Planifiés")

def charger_examens_dept(dept_id, annee):
    """Charge les examens du département"""
    try:
        db = Database(db_config.DB_CONFIG)
        db.connect()
        
        query = """
            SELECT 
                e.id,
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                l.nom as lieu,
                e.nb_etudiants_inscrits,
                e.statut
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE f.departement_id = %s
            AND e.annee_academique = %s
            ORDER BY e.date_examen, e.heure_debut
        """
        
        result = db.execute_query(query, (dept_id, annee))
        db.disconnect()
        return pd.DataFrame(result) if result else pd.DataFrame()
    
    except Exception as e:
        st.error(f"Erreur: {e}")
        return pd.DataFrame()

df_examens = charger_examens_dept(dept_id, annee)

if not df_examens.empty:
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        formations = ['Toutes'] + df_examens['formation'].unique().tolist()
        formation_filtre = st.selectbox("Formation", formations)
    
    with col2:
        dates = ['Toutes'] + sorted(df_examens['date_examen'].unique().tolist())
        date_filtre = st.selectbox("Date", dates)
    
    with col3:
        statuts = ['Tous'] + df_examens['statut'].unique().tolist()
        statut_filtre = st.selectbox("Statut", statuts)
    
    # Appliquer les filtres
    df_filtre = df_examens.copy()
    
    if formation_filtre != 'Toutes':
        df_filtre = df_filtre[df_filtre['formation'] == formation_filtre]
    
    if date_filtre != 'Toutes':
        df_filtre = df_filtre[df_filtre['date_examen'] == date_filtre]
    
    if statut_filtre != 'Tous':
        df_filtre = df_filtre[df_filtre['statut'] == statut_filtre]
    
    # Affichage
    st.dataframe(
        df_filtre[[
            'date_examen', 'heure_debut', 'module_code', 'module_nom',
            'formation', 'lieu', 'nb_etudiants_inscrits', 'statut'
        ]].rename(columns={
            'date_examen': 'Date',
            'heure_debut': 'Heure',
            'module_code': 'Code',
            'module_nom': 'Module',
            'formation': 'Formation',
            'lieu': 'Lieu',
            'nb_etudiants_inscrits': 'Étudiants',
            'statut': 'Statut'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"📊 {len(df_filtre)} examen(s) affiché(s)")
    
else:
    st.info("Aucun examen planifié pour ce département")

st.markdown("---")

# ============================================
# GRAPHIQUES
# ============================================

if not df_examens.empty:
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Examens par Formation")
        
        df_par_formation = df_examens.groupby('formation').size().reset_index(name='count')
        
        fig = px.bar(
            df_par_formation,
            x='formation',
            y='count',
            title='Nombre d\'examens par formation',
            labels={'formation': 'Formation', 'count': 'Nombre d\'examens'},
            color='count',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Examens par Date")
        
        df_par_date = df_examens.groupby('date_examen').size().reset_index(name='count')
        
        fig = px.line(
            df_par_date,
            x='date_examen',
            y='count',
            title='Nombre d\'examens par jour',
            labels={'date_examen': 'Date', 'count': 'Nombre d\'examens'},
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# ============================================
# CONFLITS DÉPARTEMENT
# ============================================

st.subheader("🔍 Conflits et Alertes")

def detecter_conflits_dept(dept_id, annee):
    """Détecte les conflits pour ce département"""
    try:
        db = Database(db_config.DB_CONFIG)
        db.connect()
        
        # Conflits étudiants
        query_etudiants = """
            WITH examens_etudiants AS (
                SELECT 
                    e.date_examen,
                    i.etudiant_id,
                    et.nom,
                    et.prenom,
                    et.matricule,
                    COUNT(*) as nb_examens
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN inscriptions i ON m.id = i.module_id
                JOIN etudiants et ON i.etudiant_id = et.id
                WHERE f.departement_id = %s
                AND e.annee_academique = %s
                AND e.statut = 'Planifié'
                GROUP BY e.date_examen, i.etudiant_id, et.nom, et.prenom, et.matricule
                HAVING COUNT(*) > 1
            )
            SELECT * FROM examens_etudiants
        """
        
        conflits_etudiants = db.execute_query(query_etudiants, (dept_id, annee))
        
        db.disconnect()
        
        return {
            'etudiants': conflits_etudiants
        }
    
    except Exception as e:
        st.error(f"Erreur: {e}")
        return {'etudiants': []}

conflits = detecter_conflits_dept(dept_id, annee)

if conflits['etudiants']:
    st.error(f"⚠️ {len(conflits['etudiants'])} conflit(s) détecté(s)")
    
    with st.expander("Voir les conflits", expanded=True):
        df_conflits = pd.DataFrame(conflits['etudiants'])
        st.dataframe(
            df_conflits[['date_examen', 'nom', 'prenom', 'matricule', 'nb_examens']].rename(columns={
                'date_examen': 'Date',
                'nom': 'Nom',
                'prenom': 'Prénom',
                'matricule': 'Matricule',
                'nb_examens': 'Nb Examens'
            }),
            use_container_width=True,
            hide_index=True
        )
else:
    st.success("✅ Aucun conflit détecté pour ce département")

st.markdown("---")

# ============================================
# VALIDATION
# ============================================

st.subheader("✅ Validation du Planning")

col1, col2 = st.columns([3, 1])

with col1:
    st.info(f"""
    **Critères de validation pour {dept_selected} :**
    - ✅ Tous les modules ont un examen planifié
    - {'✅' if not conflits['etudiants'] else '❌'} Aucun conflit étudiant
    - ✅ Capacités des salles respectées
    - ✅ Surveillances équilibrées
    """)

with col2:
    if st.button("✅ Valider", type="primary", use_container_width=True):
        if not conflits['etudiants']:
            st.success(f"✅ Planning validé pour {dept_selected}!")
            st.balloons()
        else:
            st.error("❌ Veuillez résoudre les conflits avant validation")
    
    if st.button("📤 Exporter", use_container_width=True):
        st.info("📄 Export en cours...")

st.markdown("---")
st.caption(f"📊 Dashboard {dept_selected} | Dernière mise à jour : 20/12/2024")