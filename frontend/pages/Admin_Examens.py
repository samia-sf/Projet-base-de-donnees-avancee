"""
Page Admin Examens
Génération automatique EDT, détection conflits, optimisation
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import time

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database
from config import db_config
from optimizer import ExamScheduleOptimizer
from conflict_detector import ConflictDetector

st.set_page_config(page_title="Admin Examens", page_icon="👨‍💼", layout="wide")

# ============================================
# HEADER
# ============================================

st.title("👨‍💼 Administration des Examens")
st.markdown("**Génération automatique, détection de conflits et optimisation**")

st.markdown("---")

# ============================================
# TABS PRINCIPALES
# ============================================

tab1, tab2, tab3 = st.tabs(["🚀 Génération EDT", "🔍 Détection Conflits", "⚙️ Configuration"])

# ============================================
# TAB 1 : GÉNÉRATION EDT
# ============================================

with tab1:
    st.header("🚀 Génération Automatique de l'Emploi du Temps")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Processus de Génération
        
        Le système va automatiquement :
        
        1. **Charger** tous les modules, étudiants, professeurs et salles
        2. **Optimiser** la répartition selon les contraintes
        3. **Assigner** les surveillances équitablement
        4. **Vérifier** l'absence de conflits
        5. **Sauvegarder** le planning dans la base de données
        
        **⏱️ Temps estimé :** < 45 secondes
        """)
        
        # Paramètres
        st.markdown("### ⚙️ Paramètres de Génération")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            date_debut = st.date_input(
                "Date de début des examens",
                value=datetime(2025, 1, 20),
                help="Premier jour de la période d'examens"
            )
        
        with col_b:
            date_fin = st.date_input(
                "Date de fin des examens",
                value=datetime(2025, 2, 15),
                help="Dernier jour de la période d'examens"
            )
        
        annee_academique = st.text_input(
            "Année académique",
            value="2024-2025",
            help="Format: YYYY-YYYY"
        )
        
        session = st.selectbox(
            "Session",
            ["Normale", "Rattrapage"],
            help="Type de session d'examens"
        )
    
    with col2:
        st.markdown("### 📊 Statistiques Actuelles")
        
        try:
            db = Database(db_config.DB_CONFIG)
            db.connect()
            
            # Compter les examens existants
            result = db.execute_query("""
                SELECT COUNT(*) as count FROM examens 
                WHERE annee_academique = %s AND session = %s
            """, (annee_academique, session))
            
            nb_examens_actuels = result[0]['count'] if result else 0
            
            st.metric("Examens planifiés", nb_examens_actuels)
            
            # Compter les modules
            result = db.execute_query("SELECT COUNT(*) as count FROM modules")
            nb_modules = result[0]['count'] if result else 0
            st.metric("Modules à planifier", nb_modules)
            
            # Salles disponibles
            result = db.execute_query("SELECT COUNT(*) as count FROM lieux_examen WHERE est_disponible = TRUE")
            nb_salles = result[0]['count'] if result else 0
            st.metric("Salles disponibles", nb_salles)
            
            db.disconnect()
            
        except Exception as e:
            st.error(f"Erreur: {e}")
        
        st.markdown("---")
        
        if nb_examens_actuels > 0:
            st.warning(f"⚠️ {nb_examens_actuels} examens déjà planifiés seront supprimés")
    
    st.markdown("---")
    
    # Bouton de génération
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 GÉNÉRER L'EMPLOI DU TEMPS", type="primary", use_container_width=True):
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialisation
                status_text.text("🔄 Initialisation de l'optimiseur...")
                progress_bar.progress(10)
                
                optimizer = ExamScheduleOptimizer(
                    db_config=db_config.DB_CONFIG,
                    annee_academique=annee_academique,
                    session=session
                )
                
                # Connexion
                status_text.text("🔌 Connexion à la base de données...")
                progress_bar.progress(20)
                optimizer.connect()
                
                # Génération
                status_text.text("⚙️ Génération du planning en cours...")
                progress_bar.progress(30)
                
                start_time = time.time()
                
                resultat = optimizer.generer_planning(
                    date_debut=date_debut.strftime("%Y-%m-%d"),
                    date_fin=date_fin.strftime("%Y-%m-%d")
                )
                
                elapsed = time.time() - start_time
                
                progress_bar.progress(70)
                status_text.text("💾 Sauvegarde dans la base de données...")
                
                # Sauvegarde
                optimizer.sauvegarder_planning()
                
                progress_bar.progress(100)
                optimizer.disconnect()
                
                # Résultats
                st.success(f"✅ Génération terminée en {elapsed:.2f} secondes!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Examens planifiés",
                        resultat['nb_planifies'],
                        f"{resultat['nb_planifies']/resultat['nb_total']*100:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Temps d'exécution",
                        f"{elapsed:.2f}s",
                        "✅ Objectif atteint" if elapsed < 45 else "⚠️ Dépassement"
                    )
                
                with col3:
                    st.metric(
                        "Non planifiés",
                        len(resultat['modules_non_planifies']),
                        "✅" if len(resultat['modules_non_planifies']) == 0 else "⚠️"
                    )
                
                if len(resultat['modules_non_planifies']) > 0:
                    with st.expander("⚠️ Modules non planifiés"):
                        for module in resultat['modules_non_planifies']:
                            st.write(f"- {module['code']}: {module['nom']} ({module['nb_etudiants']} étudiants)")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {e}")
                progress_bar.progress(0)

# ============================================
# TAB 2 : DÉTECTION CONFLITS
# ============================================

with tab2:
    st.header("🔍 Détection et Analyse des Conflits")
    
    st.markdown("""
    ### 📋 Types de Conflits Détectés
    
    - **🎓 Étudiants** : Plusieurs examens le même jour
    - **👨‍🏫 Professeurs** : Plus de 3 surveillances par jour
    - **🏛️ Salles** : Capacité dépassée
    - **⏰ Horaires** : Chevauchements
    """)
    
    st.markdown("---")
    
    # Paramètres
    col1, col2 = st.columns(2)
    
    with col1:
        annee_conflit = st.text_input(
            "Année académique",
            value="2024-2025",
            key="annee_conflit"
        )
    
    with col2:
        session_conflit = st.selectbox(
            "Session",
            ["Normale", "Rattrapage"],
            key="session_conflit"
        )
    
    if st.button("🔍 DÉTECTER LES CONFLITS", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Initialisation du détecteur...")
            progress_bar.progress(10)
            
            detector = ConflictDetector(
                db_config=db_config.DB_CONFIG,
                annee_academique=annee_conflit,
                session=session_conflit
            )
            
            status_text.text("🔌 Connexion à la base de données...")
            progress_bar.progress(20)
            detector.connect()
            
            status_text.text("🔍 Analyse en cours...")
            progress_bar.progress(40)
            
            rapport = detector.generer_rapport_complet()
            
            progress_bar.progress(100)
            detector.disconnect()
            
            # Affichage des résultats
            st.markdown("---")
            st.subheader("📊 Résultats de l'Analyse")
            
            # Résumé
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                nb_conflits_etudiants = len(rapport['conflits']['etudiants'])
                st.metric("Conflits Étudiants", nb_conflits_etudiants, 
                         "🟢" if nb_conflits_etudiants == 0 else "🔴")
            
            with col2:
                nb_surcharges_profs = len(rapport['conflits']['professeurs'])
                st.metric("Surcharges Profs", nb_surcharges_profs,
                         "🟢" if nb_surcharges_profs == 0 else "🟠")
            
            with col3:
                nb_depassements = len(rapport['conflits']['salles'])
                st.metric("Dépassements Salles", nb_depassements,
                         "🟢" if nb_depassements == 0 else "🔴")
            
            with col4:
                nb_chevauchements = len(rapport['conflits']['horaires'])
                st.metric("Chevauchements", nb_chevauchements,
                         "🟢" if nb_chevauchements == 0 else "🔴")
            
            st.markdown("---")
            
            # Détails des conflits
            if rapport['resume']['nb_conflits_critiques'] > 0:
                st.error(f"⚠️ {rapport['resume']['nb_conflits_critiques']} conflit(s) critique(s) détecté(s)")
                
                # Conflits étudiants
                if rapport['conflits']['etudiants']:
                    with st.expander(f"🎓 Conflits Étudiants ({len(rapport['conflits']['etudiants'])})", expanded=True):
                        df_conflits = pd.DataFrame(rapport['conflits']['etudiants'])
                        st.dataframe(
                            df_conflits[['etudiant_nom', 'etudiant_matricule', 'date', 'nb_examens', 'modules']],
                            use_container_width=True,
                            hide_index=True
                        )
                
                # Surcharges professeurs
                if rapport['conflits']['professeurs']:
                    with st.expander(f"👨‍🏫 Surcharges Professeurs ({len(rapport['conflits']['professeurs'])})", expanded=True):
                        df_surcharges = pd.DataFrame(rapport['conflits']['professeurs'])
                        st.dataframe(
                            df_surcharges[['professeur_nom', 'date', 'nb_surveillances', 'modules']],
                            use_container_width=True,
                            hide_index=True
                        )
                
                # Dépassements salles
                if rapport['conflits']['salles']:
                    with st.expander(f"🏛️ Dépassements Capacité ({len(rapport['conflits']['salles'])})", expanded=True):
                        df_salles = pd.DataFrame(rapport['conflits']['salles'])
                        st.dataframe(
                            df_salles[['module_code', 'module_nom', 'salle', 'capacite', 'nb_etudiants', 'depassement']],
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.success("✅ Aucun conflit détecté ! Le planning est valide.")
                st.balloons()
            
            # Statistiques surveillances
            st.markdown("---")
            st.subheader("📊 Statistiques des Surveillances")
            
            stats = rapport['statistiques']['surveillances']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Minimum", stats['min'])
            
            with col2:
                st.metric("Maximum", stats['max'])
            
            with col3:
                st.metric("Moyenne", f"{stats['moyenne']:.1f}")
            
            with col4:
                st.metric("Écart-type", f"{stats['ecart_type']:.2f}")
            
            if stats['profs_non_utilises']:
                with st.expander(f"👥 Professeurs non utilisés ({len(stats['profs_non_utilises'])})"):
                    for prof in stats['profs_non_utilises']:
                        st.write(f"- {prof['nom']} ({prof['departement']})")
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la détection: {e}")
            progress_bar.progress(0)

# ============================================
# TAB 3 : CONFIGURATION
# ============================================

with tab3:
    st.header("⚙️ Configuration et Paramètres")
    
    st.markdown("### 🔧 Contraintes Métier")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Max examens/jour (Étudiant)",
            min_value=1,
            max_value=3,
            value=1,
            help="Nombre maximum d'examens par jour pour un étudiant"
        )
        
        st.number_input(
            "Capacité max salle (Examen)",
            min_value=10,
            max_value=50,
            value=20,
            help="Capacité maximale d'une salle en période d'examen"
        )
    
    with col2:
        st.number_input(
            "Max surveillances/jour (Prof)",
            min_value=1,
            max_value=5,
            value=3,
            help="Nombre maximum de surveillances par jour pour un prof"
        )
        
        st.multiselect(
            "Créneaux horaires",
            ["08:00", "10:30", "13:00", "15:30", "18:00"],
            default=["08:00", "10:30", "13:00", "15:30"],
            help="Heures de début possibles pour les examens"
        )
    
    st.markdown("---")
    
    st.markdown("### 📊 Gestion de la Base de Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Rafraîchir les données", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache rafraîchi!")
    
    with col2:
        if st.button("📤 Exporter le planning", use_container_width=True):
            st.info("📄 Export en cours...")
    
    with col3:
        if st.button("🗑️ Supprimer le planning", use_container_width=True):
            st.warning("⚠️ Action irréversible!")

st.markdown("---")
st.caption("👨‍💼 Administration Examens | Dernière action : Aucune")