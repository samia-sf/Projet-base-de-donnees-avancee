import psycopg2

conn = psycopg2.connect(
    dbname='num_exam_db',
    user='postgres', 
    password='itspost@1',
    host='localhost'
)

cur = conn.cursor()

tables = ['departements', 'formations', 'etudiants', 'professeurs', 
          'modules', 'lieux_examen', 'inscriptions', 'examens', 'surveillances']

print("\n📊 ÉTAT ACTUEL DE LA BASE DE DONNÉES")
print("="*60)

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    
    # Cibles
    targets = {
        'departements': 7,
        'formations': 200,
        'etudiants': 13000,
        'professeurs': 300,
        'modules': 1470,
        'lieux_examen': 136,
        'inscriptions': 130000,
        'examens': 0,  # Normal si pas encore généré
        'surveillances': 0
    }
    
    target = targets.get(table, 0)
    status = "✅" if count >= target or table in ['examens', 'surveillances'] else "❌"
    
    print(f"{status} {table:20} : {count:>10,} / {target:>10,}")

conn.close()