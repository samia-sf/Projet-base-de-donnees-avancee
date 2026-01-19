"""
Configuration de la base de données et paramètres globaux
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ============================================
# CONFIGURATION BASE DE DONNÉES
# ============================================

class DatabaseConfig:
    """Configuration PostgreSQL"""
    
    # Vérifier si on est sur Streamlit Cloud
    import streamlit as st
import psycopg2
import re

DATABASE_URL = st.secrets["DATABASE_URL"]

match = re.match(r'postgres(?:ql)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
if match:
    DB_USER = match.group(1)
    DB_PASSWORD = match.group(2)
    DB_HOST = match.group(3)
    DB_PORT = match.group(4)
    DB_NAME = match.group(5).split('?')[0]
else:
    raise ValueError("❌ Impossible de parser DATABASE_URL depuis Streamlit Secrets")

DB_CONFIG = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

# Test rapide
try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.close()
    print("✅ Connexion PostgreSQL OK!")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")

        
    
    # URL de connexion psycopg2
    DB_CONFIG = {
        'dbname': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }

# ============================================
# PARAMÈTRES MÉTIER
# ============================================

class BusinessRules:
    """Règles métier pour la génération d'emplois du temps"""
    
    # Contraintes étudiants
    MAX_EXAMENS_PAR_JOUR_ETUDIANT = 1
    
    # Contraintes professeurs
    MAX_SURVEILLANCES_PAR_JOUR_PROF = 3
    MIN_SURVEILLANCES_PAR_JOUR_PROF = 0
    
    # Contraintes salles
    CAPACITE_MAX_SALLE_EXAMEN = 20
    
    # Durées examens (en minutes)
    DUREE_MIN_EXAMEN = 60
    DUREE_MAX_EXAMEN = 240
    DUREE_DEFAULT_EXAMEN = 90
    
    # Créneaux horaires disponibles
    HEURES_DEBUT_POSSIBLES = [
        '08:00', '10:30', '13:00', '15:30'
    ]
    
    # Période d'examens
    DATE_DEBUT_EXAMENS = "2025-01-20"
    DATE_FIN_EXAMENS = "2025-02-15"
    
    # Sessions
    SESSIONS = ['Normale', 'Rattrapage']
    
    # Année académique courante
    ANNEE_ACADEMIQUE = "2024-2025"
    
    # Performance cible
    TEMPS_MAX_GENERATION_SECONDES = 45

# ============================================
# CONFIGURATION STREAMLIT
# ============================================

class StreamlitConfig:
    """Configuration de l'interface Streamlit"""
    
    PAGE_TITLE = "Num_Exam - Plateforme d'Optimisation des Examens"
    PAGE_ICON = "📚"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # Thème
    THEME = {
        'primaryColor': '#FF4B4B',
        'backgroundColor': '#FFFFFF',
        'secondaryBackgroundColor': '#F0F2F6',
        'textColor': '#262730',
        'font': 'sans serif'
    }

# ============================================
# RÔLES UTILISATEURS
# ============================================

class UserRoles:
    """Rôles et permissions"""
    
    ROLES = {
        'Doyen': {
            'label': 'Doyen/Vice-doyen',
            'permissions': ['view_global_stats', 'validate_schedule', 'view_all_departments']
        },
        'Admin': {
            'label': 'Administrateur Examens',
            'permissions': ['generate_schedule', 'detect_conflicts', 'manage_resources', 'view_all']
        },
        'Chef_Dept': {
            'label': 'Chef de Département',
            'permissions': ['view_department_stats', 'validate_department', 'view_department_conflicts']
        },
        'Etudiant': {
            'label': 'Étudiant',
            'permissions': ['view_personal_schedule']
        },
        'Professeur': {
            'label': 'Professeur',
            'permissions': ['view_surveillance_schedule', 'confirm_surveillance']
        }
    }

# ============================================
# LOGGING
# ============================================

class LoggingConfig:
    """Configuration des logs"""
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/num_exam.log'

# ============================================
# EXPORT
# ============================================

# Instances globales de configuration
db_config = DatabaseConfig()
business_rules = BusinessRules()
streamlit_config = StreamlitConfig()
user_roles = UserRoles()
logging_config = LoggingConfig()

# Test de connexion
def test_connection():
    """Teste la connexion à la base de données"""
    import psycopg2
    try:
        conn = psycopg2.connect(**db_config.DB_CONFIG)
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Configuration du projet Num_Exam")
    print(f"📊 Base de données: {db_config.DB_NAME}")
    print(f"🖥️  Hôte: {db_config.DB_HOST}:{db_config.DB_PORT}")
    print(f"👤 Utilisateur: {db_config.DB_USER}")
    print("\n🔌 Test de connexion...")
    if test_connection():
        print("✅ Connexion réussie!")
    else:
        print("❌ Échec de la connexion!")