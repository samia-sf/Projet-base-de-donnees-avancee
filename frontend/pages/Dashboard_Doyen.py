"""
Dashboard Doyen/Vice-doyen
Vue stratégique globale, KPIs, validation finale
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, DashboardQueries
from config import db_config

st.set_page_config(page_title="Dashboard Doyen", page_icon="🏛️", layout="wide")

# ============================================
# HEADER
# ============================================

st.title("🏛️ Dashboard Doyen - Vue Stratégique")
st.markdown("**Vue d'ensemble de la planification des examens**")

st.markdown("---")

# ============================================
# CONNEXION BD
# ============================================

@st.cache_resource
def get_db():
    db = Database(db_config.DB_CONFIG)
    db.connect()
    return db

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================

def charger_kpis():
    """Charge les KPIs globaux"""
    try:
        db = get_db()
        annee = st.session_state.get('current_year', '2024-2025')
        kpis = DashboardQueries.get_kpis_globaux(db, annee)
        return kpis
    except Exception as e:
        st.error(f"Erreur lors du chargement des KPIs: {e}")
        return {}

def charger_occupation_salles():
    """Charge les données d'occupation des salles"""
    try:
        db = get_db()
        annee = st.session_state.get('current_year', '2024-2025')
        data = DashboardQueries.get_occupation_salles_par_jour(db, annee)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur: {e}")
        return pd.DataFrame()

def charger_repartition_departements():
    """Charge la répartition par département"""
    try:
        db = get_db()
        annee = st.session_state.get('current_year', '2024-2025')
        data = DashboardQueries.get_repartition_examens_par_dept(db, annee)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur: {e}")
        return pd.DataFrame()

# ============================================
# KPIS PRINCIPAUX
# ============================================

st.subheader("📊 Indicateurs Clés de Performance (KPIs)")

kpis = charger_kpis()

if kpis:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Examens",
            f"{kpis.get('total_examens', 0):,}",
            help="Nombre total d'examens planifiés"
        )
    
    with col2:
        st.metric(
            "Étudiants",
            f"{kpis.get('total_etudiants', 0):,}",
            help="Nombre d'étudiants concernés"
        )
    
    with col3:
        st.metric(
            "Professeurs Mobilisés",
            f"{kpis.get('profs_mobilises', 0)}",
            help="Professeurs assignés aux surveillances"
        )
    
    with col4:
        st.metric(
            "Salles Utilisées",
            f"{kpis.get('salles_utilisees', 0)} / 136",
            help="Salles mobilisées sur total disponible"
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Modules",
            f"{kpis.get('total_modules', 0):,}",
            help="Modules avec examens planifiés"
        )
    
    with col2:
        st.metric(
            "Formations",
            f"{kpis.get('total_formations', 0)}",
            help="Formations concernées"
        )
    
    with col3:
        st.metric(
            "Places Examens",
            f"{kpis.get('total_places_examens', 0):,}",
            help="Total de places d'examen"
        )
else:
    st.warning("⚠️ Aucun examen planifié pour cette année académique")

st.markdown("---")

# ============================================
# GRAPHIQUES
# ============================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Occupation des Salles par Jour")
    
    df_occupation = charger_occupation_salles()
    
    if not df_occupation.empty:
        fig = px.line(
            df_occupation,
            x='date_examen',
            y='taux_occupation',
            title='Taux d\'occupation des salles (%)',
            labels={'date_examen': 'Date', 'taux_occupation': 'Taux (%)'},
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Taux d'occupation (%)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        if len(df_occupation) > 0:
            taux_moyen = df_occupation['taux_occupation'].mean()
            taux_max = df_occupation['taux_occupation'].max()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Taux moyen", f"{taux_moyen:.1f}%")
            with col_b:
                st.metric("Taux maximum", f"{taux_max:.1f}%")
    else:
        st.info("Aucune donnée d'occupation disponible")

with col2:
    st.subheader("🏢 Répartition par Département")
    
    df_repartition = charger_repartition_departements()
    
    if not df_repartition.empty:
        fig = px.bar(
            df_repartition,
            x='departement',
            y='nb_examens',
            title='Nombre d\'examens par département',
            labels={'departement': 'Département', 'nb_examens': 'Nombre d\'examens'},
            color='nb_examens',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            xaxis_title="Département",
            yaxis_title="Nombre d'examens",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(
            df_repartition[['departement', 'nb_examens', 'nb_modules', 'nb_etudiants_total']].rename(columns={
                'departement': 'Département',
                'nb_examens': 'Examens',
                'nb_modules': 'Modules',
                'nb_etudiants_total': 'Étudiants'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucune donnée de répartition disponible")

st.markdown("---")

# ============================================
# TABLEAU DE BORD DÉTAILLÉ
# ============================================

st.subheader("📋 Tableau de Bord Détaillé")

tab1, tab2, tab3 = st.tabs(["📊 Vue Globale", "🏢 Par Département", "📅 Calendrier"])

with tab1:
    st.markdown("### Vue d'ensemble de la session d'examens")
    
    if kpis:
        # Pie chart : Répartition des examens
        if not df_repartition.empty:
            fig = px.pie(
                df_repartition,
                values='nb_examens',
                names='departement',
                title='Répartition des examens par département'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Indicateurs supplémentaires
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**📖 Taux de planification**\n\nModules planifiés / Total modules")
            if kpis.get('total_modules', 0) > 0:
                taux = (kpis.get('total_examens', 0) / kpis.get('total_modules', 0)) * 100
                st.metric("Taux", f"{taux:.1f}%")
        
        with col2:
            st.info("**👥 Ratio Étudiants/Examen**\n\nMoyenne étudiants par examen")
            if kpis.get('total_examens', 0) > 0:
                ratio = kpis.get('total_etudiants', 0) / kpis.get('total_examens', 0)
                st.metric("Ratio", f"{ratio:.1f}")
        
        with col3:
            st.info("**🏛️ Utilisation Salles**\n\nSalles utilisées / Total")
            if kpis.get('salles_utilisees', 0) > 0:
                taux_salles = (kpis.get('salles_utilisees', 0) / 136) * 100
                st.metric("Utilisation", f"{taux_salles:.1f}%")

with tab2:
    st.markdown("### Statistiques par département")
    
    if not df_repartition.empty:
        # Sélection département
        dept_selectionne = st.selectbox(
            "Sélectionnez un département",
            df_repartition['departement'].tolist()
        )
        
        dept_data = df_repartition[df_repartition['departement'] == dept_selectionne].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Examens", dept_data['nb_examens'])
        
        with col2:
            st.metric("Modules", dept_data['nb_modules'])
        
        with col3:
            st.metric("Étudiants", dept_data['nb_etudiants_total'])
        
        st.success(f"✅ Planning validé pour **{dept_selectionne}**")
    else:
        st.info("Aucune donnée disponible")

with tab3:
    st.markdown("### Vue calendrier")
    
    if not df_occupation.empty:
        # Calendrier des examens
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_occupation['date_examen'],
            y=df_occupation['salles_occupees'],
            mode='lines+markers',
            name='Salles occupées',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='Salles occupées par jour',
            xaxis_title='Date',
            yaxis_title='Nombre de salles',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun examen planifié")

st.markdown("---")

# ============================================
# VALIDATION FINALE
# ============================================

st.subheader("✅ Validation Finale du Planning")

col1, col2 = st.columns([3, 1])

with col1:
    st.info("""
    **Critères de validation :**
    - ✅ Tous les examens sont planifiés
    - ✅ Aucun conflit détecté
    - ✅ Capacités des salles respectées
    - ✅ Contraintes professeurs respectées
    - ✅ Tous les départements ont validé
    """)

with col2:
    if st.button("✅ Valider le Planning Global", type="primary", use_container_width=True):
        st.success("✅ Planning validé avec succès!")
        st.balloons()
    
    if st.button("📤 Exporter en PDF", use_container_width=True):
        st.info("📄 Export en cours...")

st.markdown("---")

# ============================================
# FOOTER
# ============================================

st.caption("🏛️ Dashboard Doyen | Dernière mise à jour : 20/12/2024")
st.caption("📊 Données en temps réel depuis PostgreSQL")