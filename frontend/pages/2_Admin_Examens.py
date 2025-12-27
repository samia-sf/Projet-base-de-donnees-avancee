"""
Interface d'Administration des Examens
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import Database
from config import db_config
from optimizer import ExamScheduleOptimizer
from conflict_detector import ConflictDetector

st.set_page_config(
    page_title="Administration des Examens",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #2980b9 0%, #2c3e50 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .admin-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .admin-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    
    .tool-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    .tool-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2980b9;
    }
    
    .config-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .config-section h5 {
        margin: 0 0 0.75rem 0;
        font-size: 0.95rem;
        color: #2c3e50;
        font-weight: 600;
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
    <div class="admin-header">
        <h1>Administration des Examens</h1>
        <p>Gestion et optimisation des emplois du temps d'examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "Génération Automatique",
        "Détection Conflits",
        "Configuration"
    ])
    
    with tab1:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Génération Automatique de l\'Emploi du Temps</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h5>Paramètres de Génération</h5>', unsafe_allow_html=True)
            
            annee_academique = st.selectbox(
                "Année Académique",
                ["2024-2025", "2025-2026", "2026-2027"],
                index=0
            )
            
            session = st.selectbox(
                "Session",
                ["Normale", "Rattrapage"],
                index=0
            )
            
            date_debut = st.date_input(
                "Date de début de la période",
                datetime(2025, 1, 20).date()
            )
            
            date_fin = st.date_input(
                "Date de fin de la période",
                datetime(2025, 2, 15).date()
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            st.markdown('<h5>Configuration des Contraintes</h5>', unsafe_allow_html=True)
            
            st.markdown("###### Contraintes Étudiants")
            max_exams_per_day = st.slider(
                "Maximum d'examens par jour",
                1, 2, 1
            )
            
            st.markdown("###### Contraintes Professeurs")
            max_surveillances = st.slider(
                "Maximum de surveillances par jour",
                1, 5, 3
            )
            
            st.markdown("###### Contraintes Salles")
            room_capacity = st.number_input(
                "Capacité maximale par salle",
                10, 50, 20
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        
        with col_gen2:
            if st.button("Lancer la Génération Automatique", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Initialisation de l'optimiseur...")
                    progress_bar.progress(10)
                    
                    optimizer = ExamScheduleOptimizer(
                        db_config=db_config.DB_CONFIG,
                        annee_academique=annee_academique,
                        session=session
                    )
                    
                    status_text.text("Connexion à la base de données...")
                    progress_bar.progress(20)
                    optimizer.connect()
                    
                    status_text.text("Génération du planning en cours...")
                    progress_bar.progress(30)
                    
                    start_time = time.time()
                    
                    resultat = optimizer.generer_planning(
                        date_debut=date_debut.strftime("%Y-%m-%d"),
                        date_fin=date_fin.strftime("%Y-%m-%d")
                    )
                    
                    elapsed = time.time() - start_time
                    
                    progress_bar.progress(70)
                    status_text.text("Sauvegarde dans la base de données...")
                    
                    optimizer.sauvegarder_planning()
                    
                    progress_bar.progress(100)
                    optimizer.disconnect()
                    
                    st.success(f"Génération terminée en {elapsed:.2f} secondes")
                    
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
                            "Objectif atteint" if elapsed < 45 else "Dépassement"
                        )
                    
                    with col3:
                        st.metric(
                            "Non planifiés",
                            len(resultat['modules_non_planifies'])
                        )
                    
                    if resultat['modules_non_planifies']:
                        with st.expander("Modules non planifiés"):
                            for module in resultat['modules_non_planifies']:
                                st.write(f"- {module['code']}: {module['nom']}")
                    
                except Exception as e:
                    st.error(f"Erreur lors de la génération: {e}")
                    progress_bar.progress(0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Détection et Analyse des Conflits</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            annee_conflit = st.text_input(
                "Année académique",
                value="2024-2025"
            )
        
        with col2:
            session_conflit = st.selectbox(
                "Session",
                ["Normale", "Rattrapage"],
                key="session_conflit"
            )
        
        if st.button("Détecter les Conflits", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Initialisation du détecteur...")
                progress_bar.progress(10)
                
                detector = ConflictDetector(
                    db_config=db_config.DB_CONFIG,
                    annee_academique=annee_conflit,
                    session=session_conflit
                )
                
                status_text.text("Connexion à la base de données...")
                progress_bar.progress(20)
                detector.connect()
                
                status_text.text("Analyse en cours...")
                progress_bar.progress(40)
                
                rapport = detector.generer_rapport_complet()
                
                progress_bar.progress(100)
                detector.disconnect()
                
                st.markdown("---")
                st.subheader("Résultats de l'Analyse")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    nb_conflits_etudiants = len(rapport['conflits']['etudiants'])
                    st.metric("Conflits Étudiants", nb_conflits_etudiants)
                
                with col2:
                    nb_surcharges_profs = len(rapport['conflits']['professeurs'])
                    st.metric("Surcharges Profs", nb_surcharges_profs)
                
                with col3:
                    nb_depassements = len(rapport['conflits']['salles'])
                    st.metric("Dépassements Salles", nb_depassements)
                
                with col4:
                    nb_chevauchements = len(rapport['conflits']['horaires'])
                    st.metric("Chevauchements", nb_chevauchements)
                
                if rapport['resume']['nb_conflits_critiques'] > 0:
                    st.error(f"{rapport['resume']['nb_conflits_critiques']} conflit(s) critique(s) détecté(s)")
                else:
                    st.success("Aucun conflit détecté")
                
            except Exception as e:
                st.error(f"Erreur lors de la détection: {e}")
                progress_bar.progress(0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown('<div class="tool-title">Configuration et Paramètres</div>', unsafe_allow_html=True)
        
        st.markdown("### Contraintes Métier")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input(
                "Maximum d'examens par jour (étudiant)",
                1, 3, 1
            )
            
            st.number_input(
                "Capacité max salle (examen)",
                10, 50, 20
            )
        
        with col2:
            st.number_input(
                "Maximum de surveillances par jour (prof)",
                1, 5, 3
            )
            
            st.multiselect(
                "Créneaux horaires",
                ["08:00", "10:30", "13:00", "15:30"],
                default=["08:00", "10:30", "13:00", "15:30"]
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()