"""
Utilitaires pour la gestion de la base de données
Connexion, requêtes, transactions
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Gestionnaire de connexion à la base de données"""
    
    def __init__(self, config: dict):
        """
        Initialise le gestionnaire de BD
        
        Args:
            config: Dictionnaire de configuration (dbname, user, password, host, port)
        """
        self.config = config
        self.conn = None
        
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.conn = psycopg2.connect(**self.config)
            logger.info(" Connexion à la base de données établie")
            return self.conn
        except psycopg2.Error as e:
            logger.error(f"❌ Erreur de connexion: {e}")
            raise
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            logger.info(" Connexion fermée")
    
    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """
        Context manager pour obtenir un curseur
        
        Args:
            dict_cursor: Si True, retourne un RealDictCursor (résultats en dict)
        
        Yields:
            Curseur psycopg2
        """
        if not self.conn or self.conn.closed:
            self.connect()
        
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = self.conn.cursor(cursor_factory=cursor_factory)
        
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Erreur lors de l'exécution: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, dict_cursor=True) -> List[Dict]:
        """
        Exécute une requête SELECT et retourne les résultats
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            dict_cursor: Si True, retourne des dictionnaires
        
        Returns:
            Liste de résultats
        """
        with self.get_cursor(dict_cursor=dict_cursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Exécute une requête INSERT/UPDATE/DELETE
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
        
        Returns:
            Nombre de lignes affectées
        """
        with self.get_cursor(dict_cursor=False) as cur:
            cur.execute(query, params)
            return cur.rowcount
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """
        Exécute une requête pour plusieurs enregistrements
        
        Args:
            query: Requête SQL
            data: Liste de tuples de paramètres
        
        Returns:
            Nombre de lignes affectées
        """
        with self.get_cursor(dict_cursor=False) as cur:
            cur.executemany(query, data)
            return cur.rowcount
    
    def execute_values(self, query: str, data: List[tuple], template: str = None) -> int:
        """
        Insertion en masse plus efficace avec execute_values
        
        Args:
            query: Requête SQL avec VALUES %s
            data: Liste de tuples de paramètres
            template: Template SQL personnalisé
        
        Returns:
            Nombre de lignes affectées
        """
        with self.get_cursor(dict_cursor=False) as cur:
            execute_values(cur, query, data, template=template)
            return cur.rowcount
    
    def call_function(self, function_name: str, params: tuple = None) -> Any:
        """
        Appelle une fonction PL/pgSQL
        
        Args:
            function_name: Nom de la fonction
            params: Paramètres de la fonction
        
        Returns:
            Résultat de la fonction
        """
        placeholders = ','.join(['%s'] * len(params)) if params else ''
        query = f"SELECT {function_name}({placeholders})"
        
        with self.get_cursor(dict_cursor=False) as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result[0] if result else None

# ============================================
# REQUÊTES PRÉDÉFINIES
# ============================================

class ExamQueries:
    """Requêtes SQL courantes pour les examens"""
    
    @staticmethod
    def get_examens_by_date(db: Database, date_debut: str, date_fin: str) -> List[Dict]:
        """Récupère tous les examens entre deux dates"""
        query = """
            SELECT 
                e.id,
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                f.nom as formation,
                d.nom as departement,
                l.nom as lieu,
                e.nb_etudiants_inscrits,
                e.statut
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.departement_id = d.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE e.date_examen BETWEEN %s AND %s
            ORDER BY e.date_examen, e.heure_debut
        """
        return db.execute_query(query, (date_debut, date_fin))
    
    @staticmethod
    def get_examens_etudiant(db: Database, etudiant_id: int, annee: str) -> List[Dict]:
        """Récupère les examens d'un étudiant"""
        query = """
            SELECT 
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                l.nom as lieu,
                e.statut
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN inscriptions i ON m.id = i.module_id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE i.etudiant_id = %s
            AND e.annee_academique = %s
            ORDER BY e.date_examen, e.heure_debut
        """
        return db.execute_query(query, (etudiant_id, annee))
    
    @staticmethod
    def get_surveillances_prof(db: Database, prof_id: int, annee: str) -> List[Dict]:
        """Récupère les surveillances d'un professeur"""
        query = """
            SELECT 
                e.date_examen,
                e.heure_debut,
                e.duree_minutes,
                m.code as module_code,
                m.nom as module_nom,
                l.nom as lieu,
                s.type_surveillance,
                e.statut
            FROM surveillances s
            JOIN examens e ON s.examen_id = e.id
            JOIN modules m ON e.module_id = m.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE s.professeur_id = %s
            AND e.annee_academique = %s
            ORDER BY e.date_examen, e.heure_debut
        """
        return db.execute_query(query, (prof_id, annee))
    
    @staticmethod
    def get_stats_departement(db: Database, dept_id: int, annee: str) -> Dict:
        """Statistiques pour un département"""
        query = """
            SELECT 
                COUNT(DISTINCT e.id) as nb_examens,
                COUNT(DISTINCT m.id) as nb_modules,
                COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
                SUM(e.nb_etudiants_inscrits) as total_places,
                COUNT(DISTINCT s.professeur_id) as nb_profs_utilises
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN inscriptions i ON m.id = i.module_id
            LEFT JOIN surveillances s ON e.id = s.examen_id
            WHERE f.departement_id = %s
            AND e.annee_academique = %s
        """
        result = db.execute_query(query, (dept_id, annee))
        return result[0] if result else {}

class DashboardQueries:
    """Requêtes pour les dashboards"""
    
    @staticmethod
    def get_kpis_globaux(db: Database, annee: str) -> Dict:
        """KPIs pour le dashboard doyen"""
        query = """
            SELECT 
                COUNT(DISTINCT e.id) as total_examens,
                COUNT(DISTINCT m.id) as total_modules,
                COUNT(DISTINCT f.id) as total_formations,
                COUNT(DISTINCT et.id) as total_etudiants,
                COUNT(DISTINCT s.professeur_id) as profs_mobilises,
                COUNT(DISTINCT e.lieu_id) as salles_utilisees,
                SUM(e.nb_etudiants_inscrits) as total_places_examens
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN inscriptions i ON m.id = i.module_id
            JOIN etudiants et ON i.etudiant_id = et.id
            LEFT JOIN surveillances s ON e.id = s.examen_id
            WHERE e.annee_academique = %s
            AND e.statut = 'Planifié'
        """
        result = db.execute_query(query, (annee,))
        return result[0] if result else {}
    
    @staticmethod
    def get_occupation_salles_par_jour(db: Database, annee: str) -> List[Dict]:
        """Taux d'occupation des salles par jour"""
        query = """
            WITH salles_total AS (
                SELECT COUNT(*) as total FROM lieux_examen WHERE est_disponible = TRUE
            )
            SELECT 
                e.date_examen,
                COUNT(DISTINCT e.lieu_id) as salles_occupees,
                st.total as salles_disponibles,
                ROUND(COUNT(DISTINCT e.lieu_id)::NUMERIC / st.total * 100, 2) as taux_occupation
            FROM examens e
            CROSS JOIN salles_total st
            WHERE e.annee_academique = %s
            AND e.statut = 'Planifié'
            GROUP BY e.date_examen, st.total
            ORDER BY e.date_examen
        """
        return db.execute_query(query, (annee,))
    
    @staticmethod
    def get_repartition_examens_par_dept(db: Database, annee: str) -> List[Dict]:
        """Répartition des examens par département"""
        query = """
            SELECT 
                d.nom as departement,
                COUNT(e.id) as nb_examens,
                COUNT(DISTINCT m.id) as nb_modules,
                SUM(e.nb_etudiants_inscrits) as nb_etudiants_total
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.departement_id = d.id
            WHERE e.annee_academique = %s
            AND e.statut = 'Planifié'
            GROUP BY d.id, d.nom
            ORDER BY nb_examens DESC
        """
        return db.execute_query(query, (annee,))

# ============================================
# HELPERS
# ============================================

def test_connection(config: dict) -> bool:
    """
    Teste la connexion à la base de données
    
    Args:
        config: Configuration de connexion
    
    Returns:
        True si la connexion réussit, False sinon
    """
    try:
        db = Database(config)
        db.connect()
        
        # Test simple
        with db.get_cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        
        db.disconnect()
        return True
    except Exception as e:
        logger.error(f"Test de connexion échoué: {e}")
        return False

def main():
    """Fonction de test"""
    from config import db_config
    
    print(" Test de connexion à la base de données...")
    
    if test_connection(db_config.DB_CONFIG):
        print("Connexion réussie!\n")
        
        # Test de quelques requêtes
        db = Database(db_config.DB_CONFIG)
        db.connect()
        
        try:
            # KPIs globaux
            kpis = DashboardQueries.get_kpis_globaux(db, "2024-2025")
            print(" KPIs Globaux:")
            for key, value in kpis.items():
                print(f"   - {key}: {value}")
            
            # Stats par département
            print("\n Répartition par département:")
            repartition = DashboardQueries.get_repartition_examens_par_dept(db, "2024-2025")
            for dept in repartition[:5]:
                print(f"   - {dept['departement']}: {dept['nb_examens']} examens")
        
        finally:
            db.disconnect()
    else:
        print("❌ Échec de connexion")

if __name__ == "__main__":
    main()