"""
Page de Consultation
Emplois du temps personnalisés pour étudiants et professeurs
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database, ExamQueries
from config import db_config

st.set_page_config(page_title="Consultation", page_icon="👥", layout="wide")

# ============================================
# HEADER
# ============================================

st.title("👥 Consultation des Emplois du Temps")
st.markdown("**Consultez votre planning d'examens personnalisé**")

st.markdown("---")

# ============================================
# TABS
# ============================================

tab1, tab2 = st.tabs(["👨‍🎓 Étudiants", "👨‍🏫 Professeurs"])

# ============================================
# TAB 1 : ÉTUDIANTS
# ============================================

with tab1:
    st.header("👨‍🎓 Emploi du Temps Étudiant")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recherche par matricule
        matricule_etudiant = st.text_input(
            "🔍 Entrez votre matricule",
            placeholder="Ex: E202400001",
            help="Votre numéro d'identification étudiant"
        )
    
    with col2:
        annee = st.selectbox(
            "Année académique",
            ["2024-2025", "2023-2024", "2025-2026"],
            key="annee_etudiant"
        )
    
    if st.button("🔎 Rechercher", type="primary", key="search_etudiant"):
        if not matricule_etudiant:
            st.warning("⚠️ Veuillez entrer votre matricule")
        else:
            try:
                db = Database(db_config.DB_CONFIG)
                db.connect()
                
                # Récupérer les infos de l'étudiant
                query_etudiant = """
                    SELECT e.id, e.nom, e.prenom, e.matricule, 
                           f.nom as formation, d.nom as departement
                    FROM etudiants e
                    JOIN formations f ON e.formation_id = f.id
                    JOIN departements d ON f.departement_id = d.id
                    WHERE e.matricule = %s
                """
                
                etudiant = db.execute_query(query_etudiant, (matricule_etudiant,))
                
                if not etudiant:
                    st.error("❌ Matricule non trouvé")
                else:
                    etudiant = etudiant[0]
                    
                    # Afficher les infos
                    st.success(f"✅ Étudiant trouvé : **{etudiant['prenom']} {etudiant['nom']}**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info(f"**Formation**\n\n{etudiant['formation']}")
                    
                    with col2:
                        st.info(f"**Département**\n\n{etudiant['departement']}")
                    
                    with col3:
                        st.info(f"**Matricule**\n\n{etudiant['matricule']}")
                    
                    st.markdown("---")
                    
                    # Récupérer les examens
                    examens = ExamQueries.get_examens_etudiant(db, etudiant['id'], annee)
                    
                    if examens:
                        st.subheader(f"📅 Vos Examens ({len(examens)})")
                        
                        df_examens = pd.DataFrame(examens)
                        
                        # Tri par date
                        df_examens = df_examens.sort_values(['date_examen', 'heure_debut'])
                        
                        # Calculer la fin de l'examen
                        df_examens['heure_fin'] = df_examens.apply(
                            lambda row: (
                                datetime.combine(datetime.today(), row['heure_debut']) + 
                                pd.Timedelta(minutes=row['duree_minutes'])
                            ).time(),
                            axis=1
                        )
                        
                        # Affichage en carte
                        for idx, exam in df_examens.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.markdown(f"### 📚 {exam['module_nom']}")
                                    st.caption(f"Code: {exam['module_code']}")
                                
                                with col2:
                                    st.markdown(f"**📅 {exam['date_examen'].strftime('%d/%m/%Y')}**")
                                    st.markdown(f"**🕐 {exam['heure_debut'].strftime('%H:%M')} - {exam['heure_fin'].strftime('%H:%M')}** ({exam['duree_minutes']} min)")
                                
                                with col3:
                                    st.markdown(f"**📍 {exam['lieu']}**")
                                    
                                    if exam['statut'] == 'Planifié':
                                        st.success("✅ Planifié")
                                    else:
                                        st.warning(f"⚠️ {exam['statut']}")
                                
                                st.markdown("---")
                        
                        # Bouton d'export
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            if st.button("📄 Télécharger mon EDT (PDF)", use_container_width=True):
                                st.info("📥 Téléchargement en cours...")
                        
                        # Statistiques
                        st.markdown("---")
                        st.subheader("📊 Statistiques")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Nombre d'examens", len(examens))
                        
                        with col2:
                            duree_totale = df_examens['duree_minutes'].sum()
                            st.metric("Durée totale", f"{duree_totale // 60}h {duree_totale % 60}min")
                        
                        with col3:
                            nb_jours = df_examens['date_examen'].nunique()
                            st.metric("Jours d'examens", nb_jours)
                        
                    else:
                        st.info("ℹ️ Aucun examen planifié pour le moment")
                
                db.disconnect()
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

# ============================================
# TAB 2 : PROFESSEURS
# ============================================

with tab2:
    st.header("👨‍🏫 Planning de Surveillance - Professeurs")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recherche par matricule
        matricule_prof = st.text_input(
            "🔍 Entrez votre matricule",
            placeholder="Ex: P10001",
            help="Votre numéro d'identification professeur"
        )
    
    with col2:
        annee_prof = st.selectbox(
            "Année académique",
            ["2024-2025", "2023-2024", "2025-2026"],
            key="annee_prof"
        )
    
    if st.button("🔎 Rechercher", type="primary", key="search_prof"):
        if not matricule_prof:
            st.warning("⚠️ Veuillez entrer votre matricule")
        else:
            try:
                db = Database(db_config.DB_CONFIG)
                db.connect()
                
                # Récupérer les infos du prof
                query_prof = """
                    SELECT p.id, p.nom, p.prenom, p.matricule, p.grade,
                           d.nom as departement
                    FROM professeurs p
                    JOIN departements d ON p.departement_id = d.id
                    WHERE p.matricule = %s
                """
                
                prof = db.execute_query(query_prof, (matricule_prof,))
                
                if not prof:
                    st.error("❌ Matricule non trouvé")
                else:
                    prof = prof[0]
                    
                    # Afficher les infos
                    st.success(f"✅ Professeur trouvé : **{prof['grade']} {prof['prenom']} {prof['nom']}**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info(f"**Département**\n\n{prof['departement']}")
                    
                    with col2:
                        st.info(f"**Grade**\n\n{prof['grade']}")
                    
                    with col3:
                        st.info(f"**Matricule**\n\n{prof['matricule']}")
                    
                    st.markdown("---")
                    
                    # Récupérer les surveillances
                    surveillances = ExamQueries.get_surveillances_prof(db, prof['id'], annee_prof)
                    
                    if surveillances:
                        st.subheader(f"🔍 Vos Surveillances ({len(surveillances)})")
                        
                        df_surv = pd.DataFrame(surveillances)
                        
                        # Tri par date
                        df_surv = df_surv.sort_values(['date_examen', 'heure_debut'])
                        
                        # Calculer la fin
                        df_surv['heure_fin'] = df_surv.apply(
                            lambda row: (
                                datetime.combine(datetime.today(), row['heure_debut']) + 
                                pd.Timedelta(minutes=row['duree_minutes'])
                            ).time(),
                            axis=1
                        )
                        
                        # Affichage en carte
                        for idx, surv in df_surv.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.markdown(f"### 📚 {surv['module_nom']}")
                                    st.caption(f"Code: {surv['module_code']}")
                                
                                with col2:
                                    st.markdown(f"**📅 {surv['date_examen'].strftime('%d/%m/%Y')}**")
                                    st.markdown(f"**🕐 {surv['heure_debut'].strftime('%H:%M')} - {surv['heure_fin'].strftime('%H:%M')}** ({surv['duree_minutes']} min)")
                                
                                with col3:
                                    st.markdown(f"**📍 {surv['lieu']}**")
                                    
                                    if surv['type_surveillance'] == 'Principal':
                                        st.info("👨‍🏫 Principal")
                                    else:
                                        st.info("👤 Secondaire")
                                
                                st.markdown("---")
                        
                        # Bouton d'export
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            if st.button("📄 Télécharger mon planning (PDF)", use_container_width=True):
                                st.info("📥 Téléchargement en cours...")
                        
                        # Statistiques
                        st.markdown("---")
                        st.subheader("📊 Statistiques de Surveillance")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total surveillances", len(surveillances))
                        
                        with col2:
                            nb_principal = len(df_surv[df_surv['type_surveillance'] == 'Principal'])
                            st.metric("Surveillances principales", nb_principal)
                        
                        with col3:
                            nb_secondaire = len(df_surv[df_surv['type_surveillance'] == 'Secondaire'])
                            st.metric("Surveillances secondaires", nb_secondaire)
                        
                        with col4:
                            nb_jours = df_surv['date_examen'].nunique()
                            st.metric("Jours de surveillance", nb_jours)
                        
                        # Répartition par jour
                        st.markdown("---")
                        st.subheader("📅 Répartition par Jour")
                        
                        surv_par_jour = df_surv.groupby('date_examen').size().reset_index(name='nb_surveillances')
                        
                        import plotly.express as px
                        
                        fig = px.bar(
                            surv_par_jour,
                            x='date_examen',
                            y='nb_surveillances',
                            title='Nombre de surveillances par jour',
                            labels={'date_examen': 'Date', 'nb_surveillances': 'Surveillances'}
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        st.info("ℹ️ Aucune surveillance planifiée pour le moment")
                
                db.disconnect()
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

st.markdown("---")

# ============================================
# INFORMATIONS GÉNÉRALES
# ============================================

with st.expander("ℹ️ Informations Importantes"):
    st.markdown("""
    ### 📖 Guide de Consultation
    
    **Pour les Étudiants :**
    - Votre matricule se trouve sur votre carte d'étudiant
    - Vérifiez régulièrement les mises à jour de votre emploi du temps
    - En cas d'erreur, contactez l'administration
    
    **Pour les Professeurs :**
    - Votre matricule commence par "P" suivi de chiffres
    - Vous pouvez avoir jusqu'à 3 surveillances par jour maximum
    - Les surveillances principales nécessitent votre présence durant tout l'examen
    
    **Contacts :**
    - 📧 examens@univ.dz
    - 📞 +213 XXX XXX XXX
    - 🏢 Bureau des Examens - Bâtiment Administratif
    """)

st.markdown("---")
st.caption("👥 Consultation | Service disponible 24/7")