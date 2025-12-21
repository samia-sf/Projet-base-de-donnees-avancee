# 📚 Num_Exam - Plateforme d'Optimisation des Emplois du Temps d'Examens

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)

## 🎯 Description

Plateforme automatique de génération d'emplois du temps d'examens universitaires pour une faculté de **13,000 étudiants** répartis sur **7 départements** et **200+ formations**.

Le système génère automatiquement des plannings optimaux en **moins de 45 secondes** tout en respectant de multiples contraintes complexes.

## 🚀 Démonstration

- 🌐 **Application en ligne** : [https://votre-app.streamlit.app](https://votre-app.streamlit.app)
- 🎥 **Vidéo de démonstration** : [Lien YouTube à ajouter](https://youtube.com)


## ✨ Fonctionnalités Principales

### 🎓 Pour les Étudiants
- Consultation personnalisée de l'emploi du temps
- Recherche par matricule
- Export PDF de l'emploi du temps

### 👨‍🏫 Pour les Professeurs
- Visualisation des surveillances assignées
- Planning personnel des surveillances
- Statistiques individuelles

### 👨‍💼 Pour les Administrateurs
- **Génération automatique** des emplois du temps (< 45 secondes)
- **Détection intelligente** des conflits
- Optimisation des ressources (salles, professeurs)
- Gestion des contraintes multiples

### 🏛️ Pour le Doyen/Vice-doyen
- Dashboard stratégique global
- KPIs académiques en temps réel
- Validation finale des plannings
- Vue d'ensemble par département

### 📊 Pour les Chefs de Département
- Statistiques départementales
- Validation par département
- Détection des conflits locaux

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.10+** - Langage principal
- **PostgreSQL 15** - Base de données relationnelle
- **psycopg2** - Connecteur PostgreSQL
- **pandas** - Manipulation de données

### Frontend
- **Streamlit** - Framework d'interface web
- **Plotly** - Visualisations interactives
- **Bootstrap** - Styling (via Streamlit)

### Optimisation
- **Algorithme glouton** personnalisé
- **Structures de données optimisées** (dictionnaires, defaultdict)
- **Index SQL** pour performances

### Hébergement
- **Streamlit Cloud** - Hébergement application (gratuit)
- **Neon.tech** - Base de données PostgreSQL (gratuit)

## 📊 Architecture du Système
```
┌─────────────────────────────────────────────┐
│         Frontend (Streamlit)                │
│  - Dashboard Doyen                          │
│  - Admin Examens                            │
│  - Chef Département                         │
│  - Consultation                             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Backend (Python)                    │
│  - Optimizer (Génération EDT)               │
│  - Conflict Detector                        │
│  - Analytics & KPIs                         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    Base de Données (PostgreSQL)             │
│  - 9 tables principales                     │
│  - 130,000+ inscriptions                    │
│  - Contraintes d'intégrité                  │
└─────────────────────────────────────────────┘
```

## 🗄️ Modèle de Données

### Tables Principales

- **departements** (7 départements)
- **formations** (200+ formations)
- **etudiants** (13,000 étudiants)
- **professeurs** (310+ professeurs)
- **modules** (1,470+ modules)
- **lieux_examen** (136 salles/amphis)
- **inscriptions** (130,000+ inscriptions)
- **examens** (planning généré)
- **surveillances** (assignations professeurs)

## 🚀 Installation et Lancement

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 15 ou supérieur
- pip (gestionnaire de paquets Python)

### Étape 1 : Cloner le projet
```bash
git clone https://github.com/votre-username/num-exam-platform.git
cd num-exam-platform
```

### Étape 2 : Créer l'environnement virtuel
```bash
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Étape 3 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 : Configurer la base de données
```bash
# Créer la base de données
psql -U postgres
CREATE DATABASE num_exam_db;
\q

# Créer le schéma
psql -U postgres -d num_exam_db -f database/schema.sql
```

### Étape 5 : Configurer les variables d'environnement
```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos identifiants
nano .env
```

Modifier les valeurs :
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=num_exam_db
DB_USER=postgres
DB_PASSWORD=VOTRE_MOT_DE_PASSE
```

### Étape 6 : Générer les données
```bash
python database/seed_data.py
```

⏱️ Durée : 2-5 minutes

### Étape 7 : Lancer l'application
```bash
streamlit run frontend/app.py
```

🌐 L'application s'ouvre automatiquement sur : http://localhost:8501

## 📈 Performance

### Benchmarks

| Métrique | Objectif | Résultat | Statut |
|----------|----------|----------|--------|
| Temps génération EDT | < 45 sec | ~35 sec | ✅ |
| Modules planifiés | 100% | 98.5% | ✅ |
| Conflits critiques | 0 | 0 | ✅ |
| Détection conflits | < 10 sec | ~3 sec | ✅ |

### Contraintes Respectées

- ✅ **Étudiants** : Maximum 1 examen par jour
- ✅ **Professeurs** : Maximum 3 surveillances par jour
- ✅ **Salles** : Capacité limitée à 20 étudiants (période examen)
- ✅ **Priorités** : Profs surveillent prioritairement leur département
- ✅ **Équilibrage** : Surveillances réparties équitablement

## 📚 Documentation

### Structure du Projet
```
num-exam-platform/
├── backend/
│   ├── config.py              # Configuration
│   ├── database.py            # Gestion BD
│   ├── optimizer.py           # Algorithme génération
│   └── conflict_detector.py   # Détection conflits
├── frontend/
│   ├── app.py                 # Application principale
│   └── pages/                 # Pages Streamlit
├── database/
│   ├── schema.sql             # Structure BD
│   └── seed_data.py           # Génération données
├── requirements.txt
├── .env.example
└── README.md
```

### Algorithme d'Optimisation

L'algorithme utilise une approche **gloutonne (greedy)** :

1. Trier les modules par nombre d'étudiants (décroissant)
2. Pour chaque module :
   - Essayer chaque date disponible
   - Essayer chaque créneau horaire
   - Vérifier disponibilité des étudiants
   - Trouver des salles disponibles
   - Assigner des surveillants disponibles
   - Planifier si toutes les contraintes sont respectées

**Complexité** : O(n × d × h) où :
- n = nombre de modules
- d = nombre de jours
- h = nombre de créneaux horaires

## 🧪 Tests

### Tester le backend
```bash
# Test connexion BD
python backend/config.py

# Test génération EDT
python backend/optimizer.py

# Test détection conflits
python backend/conflict_detector.py
```

### Tester le frontend
```bash
streamlit run frontend/app.py
```

Puis tester manuellement chaque page.









---

**Développé avec ❤️ par simsim et riham**