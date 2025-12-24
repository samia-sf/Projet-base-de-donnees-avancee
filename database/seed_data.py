"""
Generation de donnees realistes pour la base de donnees d'examens
- Version finale sans accents
"""

import psycopg2
from faker import Faker
import random
import time

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'num_exam_db',
    'user': 'postgres',
    'password': '123456'  # Votre mot de passe
}

fake = Faker('fr_FR')
random.seed(42)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def generate_departements(conn):
    """Genere 7 departements"""
    print(" Generation des departements...")
    
    departements = [
        ('Informatique', 'INFO', 'Dr. Benali Ahmed'),
        ('Mathematiques', 'MATH', 'Dr. Rahmouni Fatima'),
        ('Physique', 'PHYS', 'Dr. Khelifi Mohamed'),
        ('Chimie', 'CHIM', 'Dr. Mansouri Leila'),
        ('Biologie', 'BIO', 'Dr. Amrani Karim'),
        ('Genie Civil', 'GC', 'Dr. Bouazza Nadia'),
        ('Electronique', 'ELEC', 'Dr. Chaoui Hamza')
    ]
    
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO departements (nom, code, responsable_nom) VALUES (%s, %s, %s)",
        departements
    )
    conn.commit()
    print(f" 7 departements crees")
    return 7

def generate_formations(conn):
    """Genere des formations"""
    print(" Generation des formations...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements")
    dept_ids = [row[0] for row in cur.fetchall()]
    
    niveaux = ['L1', 'L2', 'L3', 'M1', 'M2']
    specialites = [
        'Systemes Information', 'Intelligence Artificielle', 'Reseaux Securite',
        'Developpement Web', 'Data Science', 'Cybersecurite', 'Cloud Computing',
        'Analyse Numerique', 'Algebre Avancee', 'Topologie', 'Probabilites',
        'Mecanique Quantique', 'Optique', 'Thermodynamique', 'Astrophysique',
        'Chimie Organique', 'Chimie Analytique', 'Biochimie', 'Polymeres',
        'Genetique', 'Microbiologie', 'Ecologie', 'Biotechnologie',
        'Structures', 'Geotechnique', 'Hydraulique', 'Construction Durable',
        'Systemes Embriques', 'Telecommunications', 'Electronique Puissance'
    ]
    
    formations = []
    for dept_id in dept_ids:
        for niveau in niveaux:
            nb_formations = random.randint(3, 4)
            for i in range(nb_formations):
                specialite = random.choice(specialites)
                code = f"D{dept_id}{niveau}{i+1:02d}"
                nom = f"{niveau} - {specialite}"
                nb_modules = random.randint(6, 8)
                formations.append((nom, code, dept_id, niveau, nb_modules))
    
    cur.executemany(
        """INSERT INTO formations (nom, code, departement_id, niveau, nb_modules) 
           VALUES (%s, %s, %s, %s, %s)""",
        formations
    )
    conn.commit()
    print(f" {len(formations)} formations creees")
    return len(formations)

def generate_etudiants(conn, target=200):
    """Genere des etudiants"""
    print(f" Generation de {target} etudiants...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM formations")
    formation_ids = [row[0] for row in cur.fetchall()]
    
    etudiants = []
    
    for i in range(target):
        matricule = f"E2024{i+1:06d}"
        nom = fake.last_name()
        prenom = fake.first_name()
        email = f"etudiant{i+1}@univ.dz"
        formation_id = random.choice(formation_ids)
        promotion = 2024
        
        etudiants.append((matricule, nom, prenom, email, formation_id, promotion))
    
    cur.executemany(
        """INSERT INTO etudiants (matricule, nom, prenom, email, formation_id, promotion) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        etudiants
    )
    conn.commit()
    print(f" {len(etudiants)} etudiants crees")
    return len(etudiants)

def generate_professeurs(conn):
    """Genere des professeurs"""
    print(" Generation des professeurs...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements")
    dept_ids = [row[0] for row in cur.fetchall()]
    
    # SANS ACCENTS - comme dans schema.sql
    grades = ['Assistant', 'Maitre Assistant', 'Maitre de Conferences', 'Professeur']
    
    professeurs = []
    
    for dept_id in dept_ids:
        nb_profs = random.randint(5, 8)
        for i in range(nb_profs):
            matricule = f"P{dept_id}{i+1:04d}"
            nom = fake.last_name()
            prenom = fake.first_name()
            email = f"prof{dept_id}{i+1}@univ.dz"
            specialite = "Informatique"
            grade = random.choice(grades)
            
            professeurs.append((matricule, nom, prenom, email, dept_id, specialite, grade))
    
    cur.executemany(
        """INSERT INTO professeurs (matricule, nom, prenom, email, departement_id, specialite, grade) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        professeurs
    )
    conn.commit()
    print(f" {len(professeurs)} professeurs crees")
    return len(professeurs)

def generate_lieux_examen(conn):
    """Genere les salles et amphis"""
    print(" Generation des lieux d'examen...")
    
    lieux = []
    
    # Amphis
    for i in range(1, 4):
        lieux.append((
            f"Amphi {i}",
            'Amphi',
            random.randint(150, 300),
            20,
            f"Batiment {chr(65 + (i-1) % 3)}",
            random.randint(0, 2),
            ['projecteur', 'tableau_blanc', 'sonorisation']
        ))
    
    # Salles
    for i in range(1, 21):
        lieux.append((
            f"Salle {i}",
            'Salle',
            random.randint(30, 50),
            20,
            f"Batiment {chr(65 + (i-1) % 4)}",
            random.randint(1, 3),
            ['tableau_blanc', 'projecteur']
        ))
    
    # Labos
    for i in range(1, 6):
        lieux.append((
            f"Labo {i}",
            'Labo',
            random.randint(20, 35),
            20,
            f"Batiment {chr(65 + (i-1) % 2)}",
            random.randint(1, 2),
            ['ordinateurs', 'tableau_blanc']
        ))
    
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO lieux_examen (nom, type, capacite_normale, capacite_examen, batiment, etage, equipements) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        lieux
    )
    conn.commit()
    print(f" {len(lieux)} lieux d'examen crees")
    return len(lieux)

def generate_modules(conn):
    """Genere les modules pour chaque formation"""
    print(" Generation des modules...")
    
    cur = conn.cursor()
    cur.execute("SELECT f.id, f.nb_modules, f.departement_id FROM formations f")
    formations = cur.fetchall()
    
    cur.execute("SELECT id, departement_id FROM professeurs")
    profs_by_dept = {}
    for prof_id, dept_id in cur.fetchall():
        if dept_id not in profs_by_dept:
            profs_by_dept[dept_id] = []
        profs_by_dept[dept_id].append(prof_id)
    
    matieres = [
        'Analyse', 'Algebre', 'Probabilites', 'Statistiques', 'Optimisation',
        'Programmation', 'Bases Donnees', 'Reseaux', 'Systemes', 'Algorithmes',
        'Intelligence Artificielle', 'Machine Learning', 'Web', 'Mobile',
        'Mecanique', 'Thermodynamique', 'Optique', 'Electronique',
        'Chimie Organique', 'Chimie Minerale', 'Biologie Cellulaire'
    ]
    
    modules = []
    for formation_id, nb_modules, dept_id in formations:
        for i in range(nb_modules):
            code = f"M{formation_id}{i+1:03d}"
            nom = f"{random.choice(matieres)} {i+1}"
            semestre = 1 if i < nb_modules // 2 else 2
            credits = random.choice([4, 5, 6])
            coef = random.randint(1, 3)
            duree = random.choice([90, 120])
            
            prof_id = random.choice(profs_by_dept.get(dept_id, [None])) if profs_by_dept.get(dept_id) else None
            
            modules.append((
                code, nom, formation_id, semestre, credits, coef,
                None, prof_id, duree, ['calculatrice']
            ))
    
    cur.executemany(
        """INSERT INTO modules (code, nom, formation_id, semestre, credits, coefficient, 
           prerequis_id, professeur_responsable_id, duree_examen_minutes, necessite_equipement) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        modules
    )
    conn.commit()
    print(f" {len(modules)} modules crees")
    return len(modules)

def generate_inscriptions(conn):
    """Genere des inscriptions (etudiants -> modules)"""
    print(" Generation des inscriptions...")
    
    cur = conn.cursor()
    
    # Recuperer tous les etudiants
    cur.execute("SELECT id, formation_id FROM etudiants")
    etudiants = cur.fetchall()
    
    # Recuperer tous les modules par formation
    cur.execute("SELECT id, formation_id FROM modules")
    modules_by_formation = {}
    for module_id, formation_id in cur.fetchall():
        if formation_id not in modules_by_formation:
            modules_by_formation[formation_id] = []
        modules_by_formation[formation_id].append(module_id)
    
    inscriptions = []
    annee_academique = "2024-2025"
    
    for etudiant_id, formation_id in etudiants:
        modules = modules_by_formation.get(formation_id, [])
        # Chaque etudiant s'inscrit à 3-5 modules de sa formation
        if modules:
            modules_inscription = random.sample(modules, min(len(modules), random.randint(3, 5)))
            for module_id in modules_inscription:
                inscriptions.append((
                    etudiant_id,
                    module_id,
                    annee_academique,
                    'Normale'
                ))
    
    # Insertion par batch
    batch_size = 500
    total = len(inscriptions)
    
    for i in range(0, total, batch_size):
        batch = inscriptions[i:i+batch_size]
        cur.executemany(
            """INSERT INTO inscriptions (etudiant_id, module_id, annee_academique, session) 
               VALUES (%s, %s, %s, %s)""",
            batch
        )
        conn.commit()
        print(f"   {min(i+batch_size, total)}/{total} inscriptions creees...")
    
    print(f" {total} inscriptions creees")
    return total

def generate_examens(conn):
    """Genere quelques examens de test"""
    print(" Generation des examens...")
    
    cur = conn.cursor()
    
    # Recuperer quelques modules
    cur.execute("SELECT id FROM modules LIMIT 10")
    modules = [row[0] for row in cur.fetchall()]
    
    # Recuperer quelques lieux
    cur.execute("SELECT id FROM lieux_examen WHERE type = 'Salle' LIMIT 5")
    lieux = [row[0] for row in cur.fetchall()]
    
    examens = []
    annee_academique = "2024-2025"
    
    # Creer 5 examens de test
    for i in range(5):
        module_id = modules[i % len(modules)]
        lieu_id = lieux[i % len(lieux)]
        date_examen = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        heure_debut = f"{random.randint(8, 16):02d}:00:00"
        duree = random.choice([90, 120, 180])
        
        # SANS ACCENTS - comme dans schema.sql
        examens.append((
            module_id, lieu_id, date_examen, heure_debut, duree,
            annee_academique, 'Normale', 0, 'Planifie', f"Examen test {i+1}"
        ))
    
    cur.executemany(
        """INSERT INTO examens (module_id, lieu_id, date_examen, heure_debut, duree_minutes, 
           annee_academique, session, nb_etudiants_inscrits, statut, observations) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        examens
    )
    
    conn.commit()
    print(f" {len(examens)} examens crees")
    return len(examens)

def main():
    """Fonction principale"""
    print("=" * 60)
    print(" GENERATION DES DONNEES - PLATEFORME EXAMENS")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        conn = get_connection()
        print(" Connexion à la base de donnees etablie\n")
        
        # Generation dans l'ordre
        generate_departements(conn)
        generate_formations(conn)
        generate_etudiants(conn, 100)  # 100 etudiants
        generate_professeurs(conn)
        generate_lieux_examen(conn)
        generate_modules(conn)
        generate_inscriptions(conn)
        generate_examens(conn)
        
        conn.close()
        
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f" GENERATION TERMINEE EN {elapsed:.2f} SECONDES")
        print("=" * 60)
        
        # Statistiques finales
        conn = get_connection()
        cur = conn.cursor()
        
        print("\n STATISTIQUES FINALES:")
        tables = ['departements', 'formations', 'etudiants', 'professeurs', 
                  'lieux_examen', 'modules', 'inscriptions', 'examens']
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   - {table.capitalize()}: {count}")
            except Exception as e:
                print(f"   - {table.capitalize()}: Erreur ({e})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()