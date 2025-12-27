"""
Algorithme d'optimisation pour la génération automatique des emplois du temps d'examens
Objectif : Générer un planning optimal en moins de 45 secondes
"""

import psycopg2
from datetime import datetime, timedelta, time
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import time as time_module

class ExamScheduleOptimizer:
    """Optimiseur pour la génération d'emplois du temps d'examens"""
    
    def __init__(self, db_config: dict, annee_academique: str = "2024-2025", session: str = "Normale"):
        self.db_config = db_config
        self.annee_academique = annee_academique
        self.session = session
        self.conn = None
        
        # Contraintes métier
        self.MAX_EXAMENS_PAR_JOUR_ETUDIANT = 1
        self.MAX_SURVEILLANCES_PAR_JOUR_PROF = 3
        self.CAPACITE_MAX_SALLE = 20
        
        # Créneaux horaires disponibles
        self.CRENEAUX_HORAIRES = [
            time(8, 0),
            time(10, 30),
            time(13, 0),
            time(15, 30)
        ]
        
        # Structures de données pour l'optimisation
        self.modules_a_planifier = []
        self.salles_disponibles = []
        self.professeurs_disponibles = []
        self.etudiants_par_module = {}
        
        # Suivi des planifications
        self.examens_planifies = []
        self.etudiants_par_jour = defaultdict(set)
        self.profs_par_jour = defaultdict(lambda: defaultdict(int))
        self.salles_occupees = defaultdict(set)
        
    def connect(self):
        """Établit la connexion à la base de données"""
        self.conn = psycopg2.connect(**self.db_config)
        
    def disconnect(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            
    def charger_donnees(self):
        """Charge toutes les données nécessaires depuis la BD"""
        print("⏳ Chargement des données...")
        
        cur = self.conn.cursor()
        
        # Charger les modules à planifier
        cur.execute("""
            SELECT m.id, m.code, m.nom, m.formation_id, m.duree_examen_minutes,
                   f.departement_id, m.professeur_responsable_id
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            ORDER BY m.formation_id, m.id
        """)
        
        for row in cur.fetchall():
            self.modules_a_planifier.append({
                'id': row[0],
                'code': row[1],
                'nom': row[2],
                'formation_id': row[3],
                'duree_minutes': row[4],
                'departement_id': row[5],
                'prof_responsable_id': row[6]
            })
        
        # Charger les salles disponibles
        cur.execute("""
            SELECT id, nom, type, capacite_examen, batiment
            FROM lieux_examen
            WHERE est_disponible = TRUE
            ORDER BY capacite_examen DESC
        """)
        
        for row in cur.fetchall():
            self.salles_disponibles.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'capacite': row[3],
                'batiment': row[4]
            })
        
        # Charger les professeurs
        cur.execute("""
            SELECT id, matricule, nom, prenom, departement_id
            FROM professeurs
            ORDER BY departement_id
        """)
        
        for row in cur.fetchall():
            self.professeurs_disponibles.append({
                'id': row[0],
                'matricule': row[1],
                'nom': row[2],
                'prenom': row[3],
                'departement_id': row[4]
            })
        
        # Charger le nombre d'étudiants par module
        cur.execute("""
            SELECT module_id, COUNT(DISTINCT etudiant_id) as nb_etudiants
            FROM inscriptions
            WHERE annee_academique = %s
            GROUP BY module_id
        """, (self.annee_academique,))
        
        for row in cur.fetchall():
            self.etudiants_par_module[row[0]] = row[1]
        
        # Charger les étudiants inscrits à chaque module
        cur.execute("""
            SELECT module_id, etudiant_id
            FROM inscriptions
            WHERE annee_academique = %s
        """, (self.annee_academique,))
        
        etudiants_modules = defaultdict(list)
        for row in cur.fetchall():
            etudiants_modules[row[0]].append(row[1])
        
        for module in self.modules_a_planifier:
            module['etudiants'] = etudiants_modules.get(module['id'], [])
            module['nb_etudiants'] = len(module['etudiants'])
        
        print(f"   ✓ {len(self.modules_a_planifier)} modules à planifier")
        print(f"   ✓ {len(self.salles_disponibles)} salles disponibles")
        print(f"   ✓ {len(self.professeurs_disponibles)} professeurs disponibles")
        
    def calculer_nb_salles_necessaires(self, nb_etudiants: int) -> int:
        """Calcule le nombre de salles nécessaires pour un nombre d'étudiants"""
        return (nb_etudiants + self.CAPACITE_MAX_SALLE - 1) // self.CAPACITE_MAX_SALLE
    
    def trouver_salles_disponibles(self, date: datetime.date, heure: time, nb_salles: int) -> List[dict]:
        """Trouve des salles disponibles pour un créneau donné"""
        cle_creneau = (date, heure)
        salles_occupees = self.salles_occupees[cle_creneau]
        
        salles_libres = [
            salle for salle in self.salles_disponibles 
            if salle['id'] not in salles_occupees
        ]
        
        if len(salles_libres) >= nb_salles:
            return salles_libres[:nb_salles]
        return []
    
    def verifier_disponibilite_etudiants(self, etudiants: List[int], date: datetime.date) -> bool:
        """Vérifie qu'aucun étudiant n'a déjà un examen ce jour-là"""
        for etudiant_id in etudiants:
            if etudiant_id in self.etudiants_par_jour[date]:
                return False
        return True
    
    def trouver_surveillants(self, date: datetime.date, nb_salles: int, 
                            departement_id: int, prof_responsable_id: Optional[int]) -> List[int]:
        """Trouve des professeurs disponibles pour surveiller"""
        surveillants = []
        
        # Prioriser le prof responsable du module
        if prof_responsable_id:
            prof = next((p for p in self.professeurs_disponibles if p['id'] == prof_responsable_id), None)
            if prof and self.profs_par_jour[date][prof_responsable_id] < self.MAX_SURVEILLANCES_PAR_JOUR_PROF:
                surveillants.append(prof_responsable_id)
        
        # Profs du même département
        profs_dept = [
            p for p in self.professeurs_disponibles 
            if p['departement_id'] == departement_id
            and p['id'] not in surveillants
            and self.profs_par_jour[date][p['id']] < self.MAX_SURVEILLANCES_PAR_JOUR_PROF
        ]
        
        profs_dept.sort(key=lambda p: self.profs_par_jour[date][p['id']])
        
        while len(surveillants) < nb_salles and profs_dept:
            surveillants.append(profs_dept.pop(0)['id'])
        
        # Si pas assez, prendre d'autres départements
        if len(surveillants) < nb_salles:
            autres_profs = [
                p for p in self.professeurs_disponibles
                if p['id'] not in surveillants
                and self.profs_par_jour[date][p['id']] < self.MAX_SURVEILLANCES_PAR_JOUR_PROF
            ]
            autres_profs.sort(key=lambda p: self.profs_par_jour[date][p['id']])
            
            while len(surveillants) < nb_salles and autres_profs:
                surveillants.append(autres_profs.pop(0)['id'])
        
        return surveillants if len(surveillants) == nb_salles else []
    
    def planifier_examen(self, module: dict, date: datetime.date, heure: time, 
                        salles: List[dict], surveillants: List[int]):
        """Enregistre la planification d'un examen"""
        
        cle_creneau = (date, heure)
        for salle in salles:
            self.salles_occupees[cle_creneau].add(salle['id'])
        
        for etudiant_id in module['etudiants']:
            self.etudiants_par_jour[date].add(etudiant_id)
        
        for prof_id in surveillants:
            self.profs_par_jour[date][prof_id] += 1
        
        self.examens_planifies.append({
            'module_id': module['id'],
            'module_code': module['code'],
            'module_nom': module['nom'],
            'date': date,
            'heure': heure,
            'duree_minutes': module['duree_minutes'],
            'salles': salles,
            'surveillants': surveillants,
            'nb_etudiants': module['nb_etudiants']
        })
    
    def generer_planning(self, date_debut: str = "2025-01-20", date_fin: str = "2025-02-15") -> dict:
        """Génère l'emploi du temps complet des examens"""
        start_time = time_module.time()
        
        print("\n" + "="*60)
        print("   GÉNÉRATION DE L'EMPLOI DU TEMPS DES EXAMENS")
        print("="*60)
        
        self.charger_donnees()
        
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d").date()
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d").date()
        
        dates_disponibles = []
        date_courante = date_debut_obj
        while date_courante <= date_fin_obj:
            if date_courante.weekday() < 5:
                dates_disponibles.append(date_courante)
            date_courante += timedelta(days=1)
        
        print(f"\n✓ Période: {date_debut} à {date_fin}")
        print(f"✓ {len(dates_disponibles)} jours disponibles")
        print(f"✓ {len(self.CRENEAUX_HORAIRES)} créneaux par jour\n")
        
        modules_tries = sorted(
            self.modules_a_planifier, 
            key=lambda m: m['nb_etudiants'], 
            reverse=True
        )
        
        nb_modules_planifies = 0
        modules_non_planifies = []
        
        print("⏳ Planification en cours...\n")
        
        for module in modules_tries:
            planifie = False
            nb_etudiants = module['nb_etudiants']
            nb_salles_necessaires = self.calculer_nb_salles_necessaires(nb_etudiants)
            
            for date in dates_disponibles:
                if planifie:
                    break
                
                if not self.verifier_disponibilite_etudiants(module['etudiants'], date):
                    continue
                
                for heure in self.CRENEAUX_HORAIRES:
                    salles = self.trouver_salles_disponibles(date, heure, nb_salles_necessaires)
                    if not salles:
                        continue
                    
                    surveillants = self.trouver_surveillants(
                        date, 
                        nb_salles_necessaires, 
                        module['departement_id'],
                        module['prof_responsable_id']
                    )
                    if not surveillants:
                        continue
                    
                    self.planifier_examen(module, date, heure, salles, surveillants)
                    planifie = True
                    nb_modules_planifies += 1
                    
                    if nb_modules_planifies % 50 == 0:
                        print(f"   ⏳ {nb_modules_planifies}/{len(modules_tries)} modules planifiés...")
                    
                    break
            
            if not planifie:
                modules_non_planifies.append(module)
        
        elapsed_time = time_module.time() - start_time
        
        print(f"\n✓ Planification terminée en {elapsed_time:.2f} secondes")
        print(f"\nSTATISTIQUES:")
        print(f"   - Modules planifiés: {nb_modules_planifies}/{len(modules_tries)}")
        print(f"   - Taux de réussite: {(nb_modules_planifies/len(modules_tries)*100):.1f}%")
        
        total_surveillances = sum(sum(profs.values()) for profs in self.profs_par_jour.values())
        nb_profs_utilises = len(set(prof_id for profs in self.profs_par_jour.values() for prof_id in profs.keys()))
        
        print(f"\nPROFESSEURS:")
        print(f"   - Total surveillances: {total_surveillances}")
        print(f"   - Professeurs utilisés: {nb_profs_utilises}/{len(self.professeurs_disponibles)}")
        
        objectif_atteint = "✓ OUI" if elapsed_time < 45 else "✗ NON"
        print(f"\nPERFORMANCE:")
        print(f"   - Temps: {elapsed_time:.2f}s / 45s")
        print(f"   - Objectif atteint: {objectif_atteint}")
        
        return {
            'success': True,
            'nb_planifies': nb_modules_planifies,
            'nb_total': len(modules_tries),
            'modules_non_planifies': modules_non_planifies,
            'temps_execution': elapsed_time,
            'examens': self.examens_planifies
        }
    
    def sauvegarder_planning(self):
        """Sauvegarde le planning généré dans la base de données"""
        print("\n⏳ Sauvegarde du planning dans la base de données...")
        
        cur = self.conn.cursor()
        
        try:
            # Supprimer les anciens examens
            cur.execute("""
                DELETE FROM surveillances 
                WHERE examen_id IN (
                    SELECT id FROM examens 
                    WHERE annee_academique = %s AND session = %s
                )
            """, (self.annee_academique, self.session))
            
            cur.execute("""
                DELETE FROM examens 
                WHERE annee_academique = %s AND session = %s
            """, (self.annee_academique, self.session))
            
            examens_crees = 0
            
            for examen in self.examens_planifies:
                salle_principale = examen['salles'][0]
                nb_etudiants = min(examen['nb_etudiants'], salle_principale['capacite'])
                
                cur.execute("""
                    INSERT INTO examens (
                        module_id, lieu_id, date_examen, heure_debut, 
                        duree_minutes, annee_academique, session, 
                        nb_etudiants_inscrits, statut
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Planifie')
                    RETURNING id
                """, (
                    examen['module_id'],
                    salle_principale['id'],
                    examen['date'],
                    examen['heure'],
                    examen['duree_minutes'],
                    self.annee_academique,
                    self.session,
                    nb_etudiants
                ))
                
                examen_id = cur.fetchone()[0]
                examens_crees += 1
                
                for i, prof_id in enumerate(examen['surveillants']):
                    type_surveillance = 'Principal' if i == 0 else 'Secondaire'
                    cur.execute("""
                        INSERT INTO surveillances (examen_id, professeur_id, type_surveillance)
                        VALUES (%s, %s, %s)
                    """, (examen_id, prof_id, type_surveillance))
                
                if examens_crees % 100 == 0:
                    print(f"   ⏳ {examens_crees}/{len(self.examens_planifies)} examens sauvegardés...")
            
            self.conn.commit()
            print(f"   ✅ {len(self.examens_planifies)} examens sauvegardés!")
            
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Erreur lors de la sauvegarde: {e}")
            raise