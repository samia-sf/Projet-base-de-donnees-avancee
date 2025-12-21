"""
Détecteur de conflits pour les emplois du temps d'examens
Vérifie toutes les contraintes et identifie les problèmes
"""

import psycopg2
from collections import defaultdict
from typing import List, Dict, Tuple
from datetime import datetime

class ConflictDetector:
    """Détecte les conflits dans un planning d'examens"""
    
    def __init__(self, db_config: dict, annee_academique: str = "2024-2025", session: str = "Normale"):
        """
        Initialise le détecteur de conflits
        
        Args:
            db_config: Configuration de la base de données
            annee_academique: Année académique
            session: Session d'examens
        """
        self.db_config = db_config
        self.annee_academique = annee_academique
        self.session = session
        self.conn = None
        
        # Contraintes
        self.MAX_EXAMENS_PAR_JOUR_ETUDIANT = 1
        self.MAX_SURVEILLANCES_PAR_JOUR_PROF = 3
        self.CAPACITE_MAX_SALLE = 20
        
        # Stockage des conflits
        self.conflits = {
            'etudiants': [],
            'professeurs': [],
            'salles': [],
            'horaires': []
        }
        
    def connect(self):
        """Établit la connexion à la base de données"""
        self.conn = psycopg2.connect(**self.db_config)
        
    def disconnect(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
    
    def detecter_conflits_etudiants(self) -> List[dict]:
        """
        Détecte les étudiants ayant plusieurs examens le même jour
        
        Returns:
            Liste des conflits détectés
        """
        print(" Détection des conflits étudiants...")
        
        cur = self.conn.cursor()
        
        # Trouver les étudiants avec plusieurs examens le même jour
        cur.execute("""
            WITH examens_etudiants AS (
                SELECT 
                    e.id as examen_id,
                    e.date_examen,
                    e.heure_debut,
                    m.code as module_code,
                    m.nom as module_nom,
                    i.etudiant_id,
                    et.nom as etudiant_nom,
                    et.prenom as etudiant_prenom,
                    et.matricule as etudiant_matricule
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN inscriptions i ON m.id = i.module_id
                JOIN etudiants et ON i.etudiant_id = et.id
                WHERE e.annee_academique = %s 
                AND e.session = %s
                AND e.statut = 'Planifié'
            )
            SELECT 
                etudiant_id,
                etudiant_matricule,
                etudiant_nom,
                etudiant_prenom,
                date_examen,
                COUNT(*) as nb_examens,
                array_agg(module_code ORDER BY heure_debut) as modules
            FROM examens_etudiants
            GROUP BY etudiant_id, etudiant_matricule, etudiant_nom, etudiant_prenom, date_examen
            HAVING COUNT(*) > 1
            ORDER BY date_examen, nb_examens DESC
        """, (self.annee_academique, self.session))
        
        conflits = []
        for row in cur.fetchall():
            conflit = {
                'type': 'etudiant_multiple_examens',
                'etudiant_id': row[0],
                'etudiant_matricule': row[1],
                'etudiant_nom': f"{row[2]} {row[3]}",
                'date': row[4],
                'nb_examens': row[5],
                'modules': row[6],
                'severite': 'CRITIQUE'
            }
            conflits.append(conflit)
        
        self.conflits['etudiants'] = conflits
        print(f"   {'✅' if len(conflits) == 0 else '⚠️'} {len(conflits)} conflit(s) détecté(s)")
        
        return conflits
    
    def detecter_surcharge_professeurs(self) -> List[dict]:
        """
        Détecte les professeurs avec plus de 3 surveillances par jour
        
        Returns:
            Liste des surcharges détectées
        """
        print(" Détection des surcharges professeurs...")
        
        cur = self.conn.cursor()
        
        cur.execute("""
            SELECT 
                p.id,
                p.matricule,
                p.nom,
                p.prenom,
                e.date_examen,
                COUNT(*) as nb_surveillances,
                array_agg(m.code ORDER BY e.heure_debut) as modules
            FROM surveillances s
            JOIN examens e ON s.examen_id = e.id
            JOIN professeurs p ON s.professeur_id = p.id
            JOIN modules m ON e.module_id = m.id
            WHERE e.annee_academique = %s 
            AND e.session = %s
            AND e.statut = 'Planifié'
            GROUP BY p.id, p.matricule, p.nom, p.prenom, e.date_examen
            HAVING COUNT(*) > 3
            ORDER BY nb_surveillances DESC, e.date_examen
        """, (self.annee_academique, self.session))
        
        conflits = []
        for row in cur.fetchall():
            conflit = {
                'type': 'professeur_surcharge',
                'professeur_id': row[0],
                'professeur_matricule': row[1],
                'professeur_nom': f"{row[2]} {row[3]}",
                'date': row[4],
                'nb_surveillances': row[5],
                'modules': row[6],
                'severite': 'HAUTE'
            }
            conflits.append(conflit)
        
        self.conflits['professeurs'] = conflits
        print(f"   {'✅' if len(conflits) == 0 else '⚠️'} {len(conflits)} surcharge(s) détectée(s)")
        
        return conflits
    
    def detecter_depassement_capacite_salles(self) -> List[dict]:
        """
        Détecte les examens où le nombre d'étudiants dépasse la capacité de la salle
        
        Returns:
            Liste des dépassements détectés
        """
        print(" Détection des dépassements de capacité...")
        
        cur = self.conn.cursor()
        
        cur.execute("""
            SELECT 
                e.id,
                m.code,
                m.nom,
                e.date_examen,
                e.heure_debut,
                l.nom as salle_nom,
                l.capacite_examen,
                e.nb_etudiants_inscrits,
                (e.nb_etudiants_inscrits - l.capacite_examen) as depassement
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN lieux_examen l ON e.lieu_id = l.id
            WHERE e.annee_academique = %s 
            AND e.session = %s
            AND e.statut = 'Planifié'
            AND e.nb_etudiants_inscrits > l.capacite_examen
            ORDER BY depassement DESC
        """, (self.annee_academique, self.session))
        
        conflits = []
        for row in cur.fetchall():
            conflit = {
                'type': 'depassement_capacite',
                'examen_id': row[0],
                'module_code': row[1],
                'module_nom': row[2],
                'date': row[3],
                'heure': row[4],
                'salle': row[5],
                'capacite': row[6],
                'nb_etudiants': row[7],
                'depassement': row[8],
                'severite': 'CRITIQUE'
            }
            conflits.append(conflit)
        
        self.conflits['salles'] = conflits
        print(f"   {'✅' if len(conflits) == 0 else '⚠️'} {len(conflits)} dépassement(s) détecté(s)")
        
        return conflits
    
    def detecter_chevauchements_horaires(self) -> List[dict]:
        """
        Détecte les salles utilisées simultanément pour plusieurs examens
        
        Returns:
            Liste des chevauchements détectés
        """
        print(" Détection des chevauchements horaires...")
        
        cur = self.conn.cursor()
        
        cur.execute("""
            WITH examens_avec_fin AS (
                SELECT 
                    e.id,
                    e.lieu_id,
                    l.nom as salle_nom,
                    e.date_examen,
                    e.heure_debut,
                    (e.heure_debut + (e.duree_minutes || ' minutes')::INTERVAL) as heure_fin,
                    m.code as module_code,
                    m.nom as module_nom
                FROM examens e
                JOIN lieux_examen l ON e.lieu_id = l.id
                JOIN modules m ON e.module_id = m.id
                WHERE e.annee_academique = %s 
                AND e.session = %s
                AND e.statut = 'Planifié'
            )
            SELECT DISTINCT
                e1.id as examen1_id,
                e1.module_code as module1,
                e1.module_nom as module1_nom,
                e2.id as examen2_id,
                e2.module_code as module2,
                e2.module_nom as module2_nom,
                e1.salle_nom,
                e1.date_examen,
                e1.heure_debut as heure1,
                e2.heure_debut as heure2
            FROM examens_avec_fin e1
            JOIN examens_avec_fin e2 ON 
                e1.lieu_id = e2.lieu_id 
                AND e1.date_examen = e2.date_examen
                AND e1.id < e2.id
                AND (
                    (e1.heure_debut < e2.heure_fin AND e1.heure_fin > e2.heure_debut)
                )
            ORDER BY e1.date_examen, e1.heure_debut
        """, (self.annee_academique, self.session))
        
        conflits = []
        for row in cur.fetchall():
            conflit = {
                'type': 'chevauchement_salle',
                'examen1_id': row[0],
                'module1': row[1],
                'module1_nom': row[2],
                'examen2_id': row[3],
                'module2': row[4],
                'module2_nom': row[5],
                'salle': row[6],
                'date': row[7],
                'heure1': row[8],
                'heure2': row[9],
                'severite': 'CRITIQUE'
            }
            conflits.append(conflit)
        
        self.conflits['horaires'] = conflits
        print(f"   {'' if len(conflits) == 0 else '⚠️'} {len(conflits)} chevauchement(s) détecté(s)")
        
        return conflits
    
    def analyser_equilibrage_surveillances(self) -> dict:
        """
        Analyse l'équilibrage des surveillances entre professeurs
        
        Returns:
            Statistiques sur la répartition des surveillances
        """
        print(" Analyse de l'équilibrage des surveillances...")
        
        cur = self.conn.cursor()
        
        # Statistiques globales
        cur.execute("""
            WITH stats_profs AS (
                SELECT 
                    p.id,
                    p.nom,
                    p.prenom,
                    d.nom as departement,
                    COUNT(s.id) as nb_surveillances
                FROM professeurs p
                LEFT JOIN surveillances s ON p.id = s.professeur_id
                LEFT JOIN examens e ON s.examen_id = e.id
                LEFT JOIN departements d ON p.departement_id = d.id
                WHERE e.annee_academique = %s 
                AND e.session = %s
                AND e.statut = 'Planifié'
                OR e.id IS NULL
                GROUP BY p.id, p.nom, p.prenom, d.nom
            )
            SELECT 
                MIN(nb_surveillances) as min_surv,
                MAX(nb_surveillances) as max_surv,
                AVG(nb_surveillances) as avg_surv,
                STDDEV(nb_surveillances) as stddev_surv,
                COUNT(*) as nb_profs
            FROM stats_profs
        """, (self.annee_academique, self.session))
        
        row = cur.fetchone()
        stats = {
            'min': row[0] or 0,
            'max': row[1] or 0,
            'moyenne': float(row[2] or 0),
            'ecart_type': float(row[3] or 0),
            'nb_professeurs': row[4]
        }
        
        # Profs sous-utilisés (0 surveillances)
        cur.execute("""
            SELECT p.id, p.nom, p.prenom, d.nom as departement
            FROM professeurs p
            JOIN departements d ON p.departement_id = d.id
            WHERE NOT EXISTS (
                SELECT 1 FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                WHERE s.professeur_id = p.id
                AND e.annee_academique = %s 
                AND e.session = %s
                AND e.statut = 'Planifié'
            )
            LIMIT 10
        """, (self.annee_academique, self.session))
        
        stats['profs_non_utilises'] = [
            {
                'id': row[0],
                'nom': f"{row[1]} {row[2]}",
                'departement': row[3]
            }
            for row in cur.fetchall()
        ]
        
        print(f"   Min: {stats['min']} | Max: {stats['max']} | Moyenne: {stats['moyenne']:.1f}")
        print(f"   Profs non utilisés: {len(stats['profs_non_utilises'])}")
        
        return stats
    
    def generer_rapport_complet(self) -> dict:
        """
        Génère un rapport complet de tous les conflits détectés
        
        Returns:
            Rapport complet avec tous les conflits et statistiques
        """
        print("\n" + "="*60)
        print(" DÉTECTION COMPLÈTE DES CONFLITS")
        print("="*60 + "\n")
        
        # Détecter tous les types de conflits
        conflits_etudiants = self.detecter_conflits_etudiants()
        surcharges_profs = self.detecter_surcharge_professeurs()
        depassements_salles = self.detecter_depassement_capacite_salles()
        chevauchements = self.detecter_chevauchements_horaires()
        stats_surveillances = self.analyser_equilibrage_surveillances()
        
        # Compter les conflits critiques
        nb_critiques = len(conflits_etudiants) + len(depassements_salles) + len(chevauchements)
        nb_warnings = len(surcharges_profs)
        
        print("\n" + "="*60)
        print(" RÉSUMÉ")
        print("="*60)
        print(f"\n{' AUCUN CONFLIT' if nb_critiques == 0 else f'⚠️  {nb_critiques} CONFLIT(S) CRITIQUE(S)'}")
        print(f"{' AUCUN AVERTISSEMENT' if nb_warnings == 0 else f'⚠️  {nb_warnings} AVERTISSEMENT(S)'}")
        
        rapport = {
            'timestamp': datetime.now().isoformat(),
            'annee_academique': self.annee_academique,
            'session': self.session,
            'resume': {
                'nb_conflits_critiques': nb_critiques,
                'nb_avertissements': nb_warnings,
                'statut': 'OK' if nb_critiques == 0 else 'CONFLITS_DETECTES'
            },
            'conflits': {
                'etudiants': conflits_etudiants,
                'professeurs': surcharges_profs,
                'salles': depassements_salles,
                'horaires': chevauchements
            },
            'statistiques': {
                'surveillances': stats_surveillances
            }
        }
        
        return rapport

def main():
    """Fonction de test"""
    from config import db_config
    
    detector = ConflictDetector(
        db_config=db_config.DB_CONFIG,
        annee_academique="2024-2025",
        session="Normale"
    )
    
    try:
        detector.connect()
        rapport = detector.generer_rapport_complet()
        
        # Afficher quelques détails
        if rapport['conflits']['etudiants']:
            print("\n⚠️  Exemples de conflits étudiants:")
            for c in rapport['conflits']['etudiants'][:3]:
                print(f"   - {c['etudiant_nom']} ({c['etudiant_matricule']}): {c['nb_examens']} examens le {c['date']}")
        
    finally:
        detector.disconnect()

if __name__ == "__main__":
    main()