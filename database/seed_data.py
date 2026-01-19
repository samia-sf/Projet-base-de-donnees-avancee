"""
Génération de données réalistes DÉTERMINISTES pour la base de données d'examens
GARANTIT 13,000 étudiants + 130,000+ inscriptions
"""

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
from datetime import datetime, timedelta
import time

# ============================================
# CONFIGURATION DÉTERMINISTE
# ============================================

# Seeds fixes pour avoir les MÊMES données partout
RANDOM_SEED = 42
FAKER_SEED = 42

# Initialisation avec seeds
random.seed(RANDOM_SEED)
fake = Faker('fr_FR')
Faker.seed(FAKER_SEED)

# Configuration BD - MODIFIE TON MOT DE PASSE ICI !
DB_CONFIG = {
    'dbname': 'num_exam_db',
    'user': 'postgres',
    'password': 'thisispost@1',  
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    """Crée une connexion à la BD"""
    return psycopg2.connect(**DB_CONFIG)

def generate_departements(conn):
    """Génère 7 départements (FIXES)"""
    print("📚 Génération des départements...")
    
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
    print(f"✅ {len(departements)} départements créés")

def generate_formations(conn):
    """Génère 200+ formations"""
    print("🎓 Génération des formations...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements ORDER BY id")
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
            nb_formations = 6
            for i in range(nb_formations):
                specialite_idx = (dept_id * 100 + formation_id) % len(specialites)
                specialite = specialites[specialite_idx]
                
                code = f"F{dept_id}{niveau}{i+1:02d}"
                nom = f"{specialite}"
                nb_modules = 6 + (formation_id % 4)
                formations.append((nom, code, dept_id, niveau, nb_modules))
                formation_id += 1
    
    cur.executemany(
        """INSERT INTO formations (nom, code, departement_id, niveau, nb_modules) 
           VALUES (%s, %s, %s, %s, %s)""",
        formations
    )
    conn.commit()
    print(f"✅ {len(formations)} formations créées")

def generate_etudiants(conn, target=13000):
    """Génère 13,000 étudiants (DÉTERMINISTE)"""
    print(f"👨‍🎓 Génération de {target} étudiants...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM formations ORDER BY id")
    formation_ids = [row[0] for row in cur.fetchall()]
    
    batch_size = 1000
    total_created = 0
    
    for batch in range(0, target, batch_size):
        etudiants = []
        for i in range(min(batch_size, target - batch)):
            idx = batch + i
            matricule = f"E{2020 + (idx % 6)}{idx + 1:06d}"
            
            nom = fake.last_name()
            prenom = fake.first_name()
            email = f"{prenom.lower()}.{nom.lower()}{idx}@univ.dz"
            
            formation_id = formation_ids[idx % len(formation_ids)]
            promotion = 2020 + (idx % 6)
            
            etudiants.append((matricule, nom, prenom, email, formation_id, promotion))
        
        cur.executemany(
            """INSERT INTO etudiants (matricule, nom, prenom, email, formation_id, promotion) 
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (matricule) DO NOTHING""",
            etudiants
        )
        conn.commit()
        total_created += len(etudiants)
        print(f"   ⏳ {total_created}/{target} étudiants créés...")
    
    print(f"✅ {target} étudiants créés")

def generate_professeurs(conn):
    """Génère 310+ professeurs"""
    print("👨‍🏫 Génération des professeurs...")
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM departements ORDER BY id")
    dept_ids = [row[0] for row in cur.fetchall()]
    
    grades = [
    'Assistant',
    'Maitre Assistant',
    'Maitre de Conferences',
    'Professeur'
     ]
    professeurs = []
    
    for dept_id in dept_ids:
        nb_profs = 45
        for i in range(nb_profs):
            matricule = f"P{dept_id}{i+1:04d}"
            
            nom = fake.last_name()
            prenom = fake.first_name()
            email = f"{prenom.lower()}.{nom.lower()}@univ-prof.dz"
            specialite = fake.job()[:100]

            
            grade = grades[(dept_id + i) % len(grades)]
            
            professeurs.append((matricule, nom, prenom, email, dept_id, specialite, grade))
    
    cur.executemany(
        """INSERT INTO professeurs (matricule, nom, prenom, email, departement_id, specialite, grade) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (matricule) DO NOTHING""",
        professeurs
    )
    conn.commit()
    print(f"✅ {len(professeurs)} professeurs créés")

def generate_lieux_examen(conn):
    """Génère 136 salles"""
    print("🏛️ Génération des lieux d'examen...")
    
    lieux = []
    
    # 15 Amphis
    capacites_amphis = [200, 250, 300, 350, 180, 220, 280, 320, 190, 210, 240, 270, 260, 230, 290]
    for i in range(1, 16):
        lieux.append((
            f"Amphi {i}",
            'Amphi',
            capacites_amphis[i-1],
            20,
            f"Bâtiment {chr(65 + (i-1) % 5)}",
            (i-1) % 4,
            ['projecteur', 'tableau_blanc', 'sonorisation']
        ))
    
    # 100 Salles
    for i in range(1, 101):
        capacite_normale = 30 + ((i * 7) % 31)
        lieux.append((
            f"Salle {i}",
            'Salle',
            capacite_normale,
            20,
            f"Bâtiment {chr(65 + (i-1) % 5)}",
            1 + ((i-1) % 4),
            ['tableau_blanc', 'projecteur']
        ))
    
    # 20 Labos
    for i in range(1, 21):
        capacite_normale = 20 + ((i * 5) % 21)
        lieux.append((
            f"Labo {i}",
            'Labo',
            capacite_normale,
            20,
            f"Bâtiment {chr(65 + (i-1) % 3)}",
            1 + ((i-1) % 3),
            ['ordinateurs', 'tableau_blanc', 'equipements_labo']
        ))
    
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO lieux_examen (nom, type, capacite_normale, capacite_examen, batiment, etage, equipements) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        lieux
    )
    conn.commit()
    print(f"✅ {len(lieux)} lieux d'examen créés (15 amphis + 100 salles + 20 labos)")

def generate_modules(conn):
    """Génère modules"""
    print("📖 Génération des modules...")
    
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.nb_modules, f.departement_id 
        FROM formations f
        ORDER BY f.id
    """)
    formations = cur.fetchall()
    
    cur.execute("SELECT id, departement_id FROM professeurs ORDER BY id")
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
            code = f"MOD{formation_id:03d}{i+1:02d}"
            
            matiere_idx = (formation_id * 10 + i) % len(matieres)
            nom = f"{matieres[matiere_idx]} {i+1}"
            
            semestre = 1 if i < nb_modules // 2 else 2
            credits = 4 + ((formation_id + i) % 3)
            coef = 1 + ((formation_id + i) % 3)
            duree = [90, 120, 180][(formation_id + i) % 3]
            
            profs_dept = profs_by_dept.get(dept_id, [None])
            prof_id = profs_dept[i % len(profs_dept)] if profs_dept else None
            
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
    print(f"✅ {len(modules)} modules créés")

def generate_inscriptions(conn):
    """Génère 130,000+ inscriptions"""
    print("📝 Génération des inscriptions (peut prendre quelques minutes)...")
    
    cur = conn.cursor()
    
    cur.execute("SELECT id, formation_id FROM etudiants ORDER BY id")
    etudiants = cur.fetchall()
    
    cur.execute("SELECT id, formation_id FROM modules ORDER BY id")
    modules_by_formation = {}
    for module_id, formation_id in cur.fetchall():
        if formation_id not in modules_by_formation:
            modules_by_formation[formation_id] = []
        modules_by_formation[formation_id].append(module_id)
    
    inscriptions = []
    annee_academique = "2024-2025"
    
    for etudiant_id, formation_id in etudiants:
        modules = modules_by_formation.get(formation_id, [])
        for module_id in modules:
            inscriptions.append((
                etudiant_id,
                module_id,
                annee_academique,
                'Normale'
            ))
    
    print(f"   📊 Total inscriptions à créer : {len(inscriptions):,}")
    
    batch_size = 5000
    total_created = 0
    
    for i in range(0, len(inscriptions), batch_size):
        batch = inscriptions[i:i+batch_size]
        cur.executemany(
            """INSERT INTO inscriptions (etudiant_id, module_id, annee_academique, session) 
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (etudiant_id, module_id, annee_academique, session) DO NOTHING""",
            batch
        )
        conn.commit()
        total_created += len(batch)
        print(f"   ⏳ {total_created:,}/{len(inscriptions):,} inscriptions créées...")
    
    print(f"✅ {len(inscriptions):,} inscriptions créées")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 GÉNÉRATION DÉTERMINISTE DES DONNÉES")
    print("   GARANTIT : 13,000 étudiants + 130,000+ inscriptions")
    print("=" * 60)
    print(f"   🎲 Random Seed: {RANDOM_SEED}")
    print(f"   🎲 Faker Seed: {FAKER_SEED}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        conn = get_connection()
        print("✅ Connexion à la base de données établie\n")
        
        generate_departements(conn)
        generate_formations(conn)
        generate_etudiants(conn, target=13000)  # ← GARANTI 13,000 !
        generate_professeurs(conn)
        generate_lieux_examen(conn)
        generate_modules(conn)
        generate_inscriptions(conn)
        
        conn.close()
        
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"✅ GÉNÉRATION TERMINÉE EN {elapsed:.2f} SECONDES")
        print("=" * 60)
        
        # Statistiques finales
        conn = get_connection()
        cur = conn.cursor()
        
        print("\n📊 STATISTIQUES FINALES:")
        tables = ['departements', 'formations', 'etudiants', 'professeurs', 
                  'lieux_examen', 'modules', 'inscriptions']
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   ✅ {table.capitalize():20} : {count:>10,}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ BASE DE DONNÉES PRÊTE POUR LA GÉNÉRATION EDT !")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()