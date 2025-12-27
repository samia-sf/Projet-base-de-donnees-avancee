# Num_Exam - Plateforme d'Optimisation des Examens Universitaires

## Description

Système intelligent de génération et d'optimisation automatique des emplois du temps d'examens pour une université de 13,000 étudiants, 7 départements et 200+ formations.

**Objectif:** Générer un planning optimal en moins de 45 secondes.

## Architecture

```
num_exam/
├── backend/
│   ├── config.py              # Configuration générale
│   ├── database.py            # Gestion base de données
│   ├── optimizer.py           # Algorithme d'optimisation
│   ├── conflict_detector.py   # Détection de conflits
│   └── seed_data.py           # Génération données test
├── frontend/
│   ├── app.py                 # Interface principale
│   └── pages/
│       ├── 1_Dashboard_Doyen.py
│       ├── 2_Admin_Examens.py
│       ├── 3_Chef_Departement.py
│       ├── 4_Consultation.py
│       └── 5_visualisation_planning.py
└── sql/
    ├── schema.sql             # Schéma de base de données
    └── queries.sql            # Requêtes utiles
```

## Technologies

- **Backend:** Python 3.9+
- **Base de données:** PostgreSQL 14+
- **Frontend:** Streamlit
- **Visualisation:** Plotly
- **Optimisation:** Algorithme glouton avec contraintes

## Installation

### 1. Prérequis

```bash
# Python 3.9 ou supérieur
python --version

# PostgreSQL 14 ou supérieur
psql --version
```

### 2. Cloner le projet

```bash
git clone https://github.com/votre-username/num_exam.git
cd num_exam
```

### 3. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
streamlit>=1.28.0
psycopg2-binary>=2.9.9
plotly>=5.17.0
pandas>=2.1.0
python-dotenv>=1.0.0
faker>=19.6.2
```

### 5. Configuration de la base de données

#### A. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base
CREATE DATABASE num_exam_db;

# Se connecter à la base
\c num_exam_db
```

#### B. Créer le schéma

```bash
# Exécuter le script SQL
psql -U postgres -d num_exam_db -f sql/schema.sql
```

#### C. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=num_exam_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

**IMPORTANT:** Modifier également `backend/seed_data.py` ligne 21 avec votre mot de passe PostgreSQL.

### 6. Générer les données de test

```bash
cd backend
python seed_data.py
```

Cette commande génère:
- 7 départements
- 200+ formations
- 13,000 étudiants
- 310+ professeurs
- 1,470 modules
- 136 salles
- 130,000+ inscriptions

**Durée:** ~2-3 minutes

## Utilisation

### 1. Lancer l'application

```bash
cd frontend
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

### 2. Workflow recommandé

1. **Connexion:** Sélectionner votre rôle dans la barre latérale
2. **Admin:** Générer l'emploi du temps automatique
3. **Admin:** Détecter et corriger les conflits
4. **Chef Département:** Valider les plannings par département
5. **Doyen:** Validation finale du planning global
6. **Étudiants/Profs:** Consultation des emplois du temps

### 3. Pages disponibles

| Page | Rôle | Description |
|------|------|-------------|
| Dashboard Doyen | Doyen/Vice-doyen | Vue stratégique globale, KPIs |
| Admin Examens | Administrateur | Génération EDT, détection conflits |
| Chef Département | Chef de Département | Statistiques et validation locale |
| Consultation | Étudiants/Professeurs | Emplois du temps personnalisés |
| Visualisation | Tous | Affichage type planning université |

## Déploiement en Production

### Option 1: Streamlit Cloud (Gratuit)

1. Créer un compte sur [share.streamlit.io](https://share.streamlit.io)
2. Connecter votre dépôt GitHub
3. Configurer les secrets dans Settings > Secrets:

```toml
[database]
DB_HOST = "votre-serveur.postgres.cloud"
DB_PORT = "5432"
DB_NAME = "num_exam_db"
DB_USER = "postgres"
DB_PASSWORD = "votre_mot_de_passe"
```

4. Déployer l'application

### Option 2: Heroku

```bash
# Installer Heroku CLI
heroku login

# Créer l'application
heroku create num-exam-app

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Déployer
git push heroku main

# Exécuter les migrations
heroku run python backend/seed_data.py
```

### Option 3: VPS (DigitalOcean, AWS, Azure)

```bash
# Se connecter au VPS
ssh root@votre-ip

# Installer dépendances
apt update
apt install python3-pip postgresql nginx

# Cloner le projet
git clone https://github.com/votre-username/num_exam.git

# Configuration
cd num_exam
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer PostgreSQL
sudo -u postgres psql
CREATE DATABASE num_exam_db;
\c num_exam_db
\i sql/schema.sql

# Générer données
python backend/seed_data.py

# Lancer avec screen
screen -S numexam
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

# Détacher: Ctrl+A puis D
```

## Contraintes Métier Implémentées

### Étudiants
- Maximum 1 examen par jour
- Pas de chevauchement entre modules d'une même formation

### Professeurs
- Maximum 3 surveillances par jour
- Équilibrage automatique des charges
- Priorité aux professeurs du même département

### Salles
- Capacité maximale: 20 étudiants en période d'examen
- Pas de double affectation sur un même créneau
- Types: Amphis (200-350), Salles (30-60), Labos (20-40)

### Horaires
- 4 créneaux par jour: 08h00, 10h30, 13h00, 15h30
- Jours ouvrables uniquement (Lundi-Vendredi)

## Performance

- **Génération:** < 45 secondes pour 1,470 modules
- **Détection conflits:** < 10 secondes
- **Taux de planification:** > 95%

## Dépannage

### Problème de connexion à la base

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Tester la connexion
psql -U postgres -d num_exam_db
```

### Erreur "Module not found"

```bash
# Vérifier l'environnement virtuel
which python
# Doit pointer vers venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Planning vide après génération

1. Vérifier que les données sont bien chargées:
```sql
SELECT COUNT(*) FROM etudiants;  -- Doit retourner 13000
SELECT COUNT(*) FROM modules;    -- Doit retourner ~1470
```

2. Vérifier les logs dans la console Streamlit



## Licence

© 2025 Université M'Hamed Bougara - Tous droits réservés

## Auteurs

Projet académique réalisé dans le cadre du cours de Bases de Données Avancées.

---

**Version:** 1.0.0  
**Dernière mise à jour:** Décembre 2025