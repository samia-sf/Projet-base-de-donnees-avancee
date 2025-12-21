"""
Génération de données réalistes pour la base de données d'examens
- 13 000 étudiants
- 7 départements
- 200+ formations
- 130k+ inscriptions
"""

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
from datetime import datetime, timedelta
import time

# Configuration
fake = Faker('fr_FR')
random.seed(42)

# Connexion à la base de données
DB_CONFIG = {
    'dbname': 'num_exam_db',
    'user': 'postgres',
    'password': 'votre_password',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    """Crée une connexion à la BD"""
    return psycopg2.connect(**DB_CONFIG)

def generate_departements(conn):
    """Génère 7 départements"""
    print(" Génération des départements...")
    
    departements = [
        ('Informatique', 'INFO', 'Dr. Benali Ahmed'),
        ('Mathématiques', 'MATH', 'Dr. Rahmouni Fatima'),
        ('Physique', 'PHYS', 'Dr. Khelifi Mohamed'),
        ('Chimie', 'CHIM', 'Dr. Mansouri Leila'),
        ('Biologie', 'BIO', 'Dr. Amrani Karim'),
        ('Génie Civil', 'GC', 'Dr. Bouazza Nadia'),
        ('Électronique', 'ELEC', 'Dr. Chaoui Hamza')
    ]
    
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO departements (nom, code, responsable_nom) VALUES (%s, %s, %s)",
        departements
    )
    conn.commit()
    print(f" {len(departements)} départements créés")
    return len(departements)

def generate_formations(conn):
    """Génère 200+ formations"""
    print(" Génération des formations...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements")
    dept_ids = [row[0] for row in cur.fetchall()]
    
    niveaux = ['L1', 'L2', 'L3', 'M1', 'M2']
    specialites = [
        'Systèmes d\'Information', 'Intelligence Artificielle', 'Réseaux et Sécurité',
        'Développement Web', 'Data Science', 'Cybersécurité', 'Cloud Computing',
        'Analyse Numérique', 'Algèbre Avancée', 'Topologie', 'Probabilités',
        'Mécanique Quantique', 'Optique', 'Thermodynamique', 'Astrophysique',
        'Chimie Organique', 'Chimie Analytique', 'Biochimie', 'Polymères',
        'Génétique', 'Microbiologie', 'Écologie', 'Biotechnologie',
        'Structures', 'Géotechnique', 'Hydraulique', 'Construction Durable',
        'Systèmes Embarqués', 'Télécommunications', 'Électronique de Puissance'
    ]
    
    formations = []
    formation_id = 1
    
    for dept_id in dept_ids:
        for niveau in niveaux:
            # 5-7 formations par niveau par département
            nb_formations = random.randint(5, 7)
            for i in range(nb_formations):
                specialite = random.choice(specialites)
                code = f"{dept_id}{niveau}{i+1:02d}"
                nom = f"{niveau} - {specialite}"
                nb_modules = random.randint(6, 9)
                formations.append((nom, code, dept_id, niveau, nb_modules))
                formation_id += 1
    
    cur.executemany(
        """INSERT INTO formations (nom, code, departement_id, niveau, nb_modules) 
           VALUES (%s, %s, %s, %s, %s)""",
        formations
    )
    conn.commit()
    print(f" {len(formations)} formations créées")
    return len(formations)

def generate_etudiants(conn, target=13000):
    """Génère ~13000 étudiants"""
    print(f" Génération de {target} étudiants...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM formations")
    formation_ids = [row[0] for row in cur.fetchall()]
    
    batch_size = 1000
    for batch in range(0, target, batch_size):
        etudiants = []
        for i in range(min(batch_size, target - batch)):
            matricule = f"E{2020 + random.randint(0, 5)}{batch + i + 1:06d}"
            nom = fake.last_name()
            prenom = fake.first_name()
            email = f"{prenom.lower()}.{nom.lower()}@univ.dz"
            formation_id = random.choice(formation_ids)
            promotion = random.randint(2020, 2025)
            
            etudiants.append((matricule, nom, prenom, email, formation_id, promotion))
        
        cur.executemany(
            """INSERT INTO etudiants (matricule, nom, prenom, email, formation_id, promotion) 
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (matricule) DO NOTHING""",
            etudiants
        )
        conn.commit()
        print(f"   ⏳ {batch + len(etudiants)}/{target} étudiants créés...")
    
    print(f" {target} étudiants créés")

def generate_professeurs(conn):
    """Génère des professeurs (environ 300)"""
    print(" Génération des professeurs...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements")
    dept_ids = [row[0] for row in cur.fetchall()]
    
    grades = ['Assistant', 'Maître Assistant', 'Maître de Conférences', 'Professeur']
    professeurs = []
    
    for dept_id in dept_ids:
        # 40-50 profs par département
        nb_profs = random.randint(40, 50)
        for i in range(nb_profs):
            matricule = f"P{dept_id}{i+1:04d}"
            nom = fake.last_name()
            prenom = fake.first_name()
            email = f"{prenom.lower()}.{nom.lower()}@univ-prof.dz"
            specialite = fake.job()
            grade = random.choice(grades)
            
            professeurs.append((matricule, nom, prenom, email, dept_id, specialite, grade))
    
    cur.executemany(
        """INSERT INTO professeurs (matricule, nom, prenom, email, departement_id, specialite, grade) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (matricule) DO NOTHING""",
        professeurs
    )
    conn.commit()
    print(f"{len(professeurs)} professeurs créés")

def generate_lieux_examen(conn):
    """Génère les salles et amphis"""
    print(" Génération des lieux d'examen...")
    
    lieux = []
    
    # Amphis (grande capacité normale, limitée à 20 en examen)
    for i in range(1, 16):
        lieux.append((
            f"Amphi {i}",
            'Amphi',
            random.randint(150, 400),  # capacité normale
            20,  # capacité examen (20 max)
            f"Bâtiment {chr(65 + i % 5)}",
            random.randint(0, 3),
            ['projecteur', 'tableau_blanc', 'sonorisation']
        ))
    
    # Salles classiques
    for i in range(1, 101):
        lieux.append((
            f"Salle {i}",
            'Salle',
            random.randint(30, 60),  # capacité normale
            20,  # capacité examen
            f"Bâtiment {chr(65 + i % 5)}",
            random.randint(1, 4),
            ['tableau_blanc', 'projecteur']
        ))
    
    # Labos
    for i in range(1, 21):
        lieux.append((
            f"Labo {i}",
            'Labo',
            random.randint(20, 40),
            20,  # capacité examen
            f"Bâtiment {chr(65 + i % 3)}",
            random.randint(1, 3),
            ['ordinateurs', 'tableau_blanc', 'equipements_labo']
        ))
    
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO lieux_examen (nom, type, capacite_normale, capacite_examen, batiment, etage, equipements) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        lieux
    )
    conn.commit()
    print(f" {len(lieux)} lieux d'examen créés")

def generate_modules(conn):
    """Génère les modules pour chaque formation"""
    print(" Génération des modules...")
    
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.nb_modules, f.departement_id 
        FROM formations f
    """)
    formations = cur.fetchall()
    
    cur.execute("SELECT id, departement_id FROM professeurs")
    profs_by_dept = {}
    for prof_id, dept_id in cur.fetchall():
        if dept_id not in profs_by_dept:
            profs_by_dept[dept_id] = []
        profs_by_dept[dept_id].append(prof_id)
    
    matieres = [
        'Analyse', 'Algèbre', 'Probabilités', 'Statistiques', 'Optimisation',
        'Programmation', 'Bases de Données', 'Réseaux', 'Systèmes', 'Algorithmes',
        'Intelligence Artificielle', 'Machine Learning', 'Web', 'Mobile',
        'Mécanique', 'Thermodynamique', 'Optique', 'Électronique',
        'Chimie Organique', 'Chimie Minérale', 'Biologie Cellulaire'
    ]
    
    modules = []
    for formation_id, nb_modules, dept_id in formations:
        for i in range(nb_modules):
            code = f"MOD{formation_id}{i+1:02d}"
            nom = f"{random.choice(matieres)} {i+1}"
            semestre = 1 if i < nb_modules // 2 else 2
            credits = random.choice([4, 5, 6])
            coef = random.randint(1, 3)
            duree = random.choice([90, 120, 180])
            
            # Assigner un prof du même département
            prof_id = random.choice(profs_by_dept.get(dept_id, [None]))
            
            modules.append((
                code, nom, formation_id, semestre, credits, coef,
                None, prof_id, duree, ['calculatrice']
            ))
    
    cur.executemany(
        """INSERT INTO modules (code, nom, formation_id, semestre, credits, coefficient, 
           prerequis_id, professeur_responsable_id, duree_examen_minutes, necessite_equipement) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (code) DO NOTHING""",
        modules
    )
    conn.commit()
    print(f" {len(modules)} modules créés")

def generate_inscriptions(conn):
    """Génère ~130k inscriptions (étudiants -> modules)"""
    print(" Génération des inscriptions (peut prendre quelques minutes)...")
    
    cur = conn.cursor()
    
    # Récupérer tous les étudiants avec leur formation
    cur.execute("SELECT id, formation_id FROM etudiants")
    etudiants = cur.fetchall()
    
    # Récupérer tous les modules par formation
    cur.execute("SELECT id, formation_id FROM modules")
    modules_by_formation = {}
    for module_id, formation_id in cur.fetchall():
        if formation_id not in modules_by_formation:
            modules_by_formation[formation_id] = []
        modules_by_formation[formation_id].append(module_id)
    
    inscriptions = []
    annee_academique = "2024-2025"
    
    for etudiant_id, formation_id in etudiants:
        # Chaque étudiant s'inscrit à tous les modules de sa formation
        modules = modules_by_formation.get(formation_id, [])
        for module_id in modules:
            inscriptions.append((
                etudiant_id,
                module_id,
                annee_academique,
                'Normale'
            ))
    
    # Insertion par batch de 5000
    batch_size = 5000
    for i in range(0, len(inscriptions), batch_size):
        batch = inscriptions[i:i+batch_size]
        cur.executemany(
            """INSERT INTO inscriptions (etudiant_id, module_id, annee_academique, session) 
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (etudiant_id, module_id, annee_academique, session) DO NOTHING""",
            batch
        )
        conn.commit()
        print(f"    {min(i+batch_size, len(inscriptions))}/{len(inscriptions)} inscriptions créées...")
    
    print(f" {len(inscriptions)} inscriptions créées")

def main():
    """Fonction principale"""
    print("=" * 60)
    print(" GÉNÉRATION DES DONNÉES - PLATEFORME EXAMENS")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        conn = get_connection()
        print(" Connexion à la base de données établie\n")
        
        # Génération dans l'ordre (respect des clés étrangères)
        generate_departements(conn)
        generate_formations(conn)
        generate_etudiants(conn)
        generate_professeurs(conn)
        generate_lieux_examen(conn)
        generate_modules(conn)
        generate_inscriptions(conn)
        
        conn.close()
        
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f" GÉNÉRATION TERMINÉE EN {elapsed:.2f} SECONDES")
        print("=" * 60)
        
        # Statistiques finales
        conn = get_connection()
        cur = conn.cursor()
        
        print("\n STATISTIQUES FINALES:")
        tables = ['departements', 'formations', 'etudiants', 'professeurs', 
                  'lieux_examen', 'modules', 'inscriptions']
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   - {table.capitalize()}: {count:,}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        raise

if __name__ == "__main__":
    main()