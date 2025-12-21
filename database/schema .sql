-- ============================================
-- SCHEMA COMPLET - PLATEFORME EXAMENS
-- Base: PostgreSQL 14+
-- ============================================

-- Suppression des tables si elles existent
DROP TABLE IF EXISTS examens CASCADE;
DROP TABLE IF EXISTS inscriptions CASCADE;
DROP TABLE IF EXISTS surveillances CASCADE;
DROP TABLE IF EXISTS modules CASCADE;
DROP TABLE IF EXISTS professeurs CASCADE;
DROP TABLE IF EXISTS etudiants CASCADE;
DROP TABLE IF EXISTS lieux_examen CASCADE;
DROP TABLE IF EXISTS formations CASCADE;
DROP TABLE IF EXISTS departements CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- TABLE: DEPARTEMENTS
-- ============================================
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    responsable_nom VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: FORMATIONS
-- ============================================
CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    departement_id INT NOT NULL REFERENCES departements(id) ON DELETE CASCADE,
    niveau VARCHAR(20) CHECK (niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')),
    nb_modules INT DEFAULT 6 CHECK (nb_modules BETWEEN 6 AND 9),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: ETUDIANTS
-- ============================================
CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    formation_id INT NOT NULL REFERENCES formations(id) ON DELETE CASCADE,
    promotion INT NOT NULL CHECK (promotion >= 2020),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_formation UNIQUE (matricule, formation_id)
);

-- Index pour recherches fréquentes
CREATE INDEX idx_etudiants_formation ON etudiants(formation_id);
CREATE INDEX idx_etudiants_promo ON etudiants(promotion);

-- ============================================
-- TABLE: PROFESSEURS
-- ============================================
CREATE TABLE professeurs (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    departement_id INT NOT NULL REFERENCES departements(id) ON DELETE CASCADE,
    specialite VARCHAR(100),
    grade VARCHAR(50) CHECK (grade IN ('Assistant', 'Maître Assistant', 'Maître de Conférences', 'Professeur')),
    max_surveillances_par_jour INT DEFAULT 3 CHECK (max_surveillances_par_jour <= 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_professeurs_dept ON professeurs(departement_id);

-- ============================================
-- TABLE: LIEUX D'EXAMEN
-- ============================================
CREATE TABLE lieux_examen (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) CHECK (type IN ('Amphi', 'Salle', 'Labo')),
    capacite_normale INT NOT NULL CHECK (capacite_normale > 0),
    capacite_examen INT NOT NULL CHECK (capacite_examen > 0 AND capacite_examen <= 20),
    batiment VARCHAR(50),
    etage INT,
    equipements TEXT[], -- {projecteur, tableau_blanc, ordinateurs}
    est_disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lieux_type ON lieux_examen(type);
CREATE INDEX idx_lieux_disponible ON lieux_examen(est_disponible);

-- ============================================
-- TABLE: MODULES
-- ============================================
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(200) NOT NULL,
    formation_id INT NOT NULL REFERENCES formations(id) ON DELETE CASCADE,
    semestre INT CHECK (semestre IN (1, 2)),
    credits INT DEFAULT 5 CHECK (credits BETWEEN 1 AND 10),
    coefficient INT DEFAULT 1 CHECK (coefficient >= 1),
    prerequis_id INT REFERENCES modules(id) ON DELETE SET NULL,
    professeur_responsable_id INT REFERENCES professeurs(id) ON DELETE SET NULL,
    duree_examen_minutes INT DEFAULT 90 CHECK (duree_examen_minutes BETWEEN 60 AND 240),
    necessite_equipement TEXT[], -- {ordinateur, calculatrice, internet}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_modules_formation ON modules(formation_id);
CREATE INDEX idx_modules_prof ON modules(professeur_responsable_id);

-- ============================================
-- TABLE: INSCRIPTIONS (Étudiants -> Modules)
-- ============================================
CREATE TABLE inscriptions (
    id SERIAL PRIMARY KEY,
    etudiant_id INT NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    annee_academique VARCHAR(9) NOT NULL, -- Format: 2024-2025
    session VARCHAR(20) CHECK (session IN ('Normale', 'Rattrapage')),
    note DECIMAL(4,2) CHECK (note >= 0 AND note <= 20),
    est_valide BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_inscription UNIQUE (etudiant_id, module_id, annee_academique, session)
);

CREATE INDEX idx_inscriptions_etudiant ON inscriptions(etudiant_id);
CREATE INDEX idx_inscriptions_module ON inscriptions(module_id);
CREATE INDEX idx_inscriptions_annee ON inscriptions(annee_academique);

-- ============================================
-- TABLE: EXAMENS
-- ============================================
CREATE TABLE examens (
    id SERIAL PRIMARY KEY,
    module_id INT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    lieu_id INT NOT NULL REFERENCES lieux_examen(id) ON DELETE RESTRICT,
    date_examen DATE NOT NULL,
    heure_debut TIME NOT NULL,
    duree_minutes INT NOT NULL CHECK (duree_minutes BETWEEN 60 AND 240),
    annee_academique VARCHAR(9) NOT NULL,
    session VARCHAR(20) CHECK (session IN ('Normale', 'Rattrapage')),
    nb_etudiants_inscrits INT DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Planifié' CHECK (statut IN ('Planifié', 'En cours', 'Terminé', 'Annulé')),
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_examen_planification UNIQUE (module_id, annee_academique, session),
    CONSTRAINT check_capacite CHECK (nb_etudiants_inscrits <= (SELECT capacite_examen FROM lieux_examen WHERE id = lieu_id))
);

CREATE INDEX idx_examens_date ON examens(date_examen);
CREATE INDEX idx_examens_module ON examens(module_id);
CREATE INDEX idx_examens_lieu ON examens(lieu_id);
CREATE INDEX idx_examens_session ON examens(annee_academique, session);

-- ============================================
-- TABLE: SURVEILLANCES (Profs -> Examens)
-- ============================================
CREATE TABLE surveillances (
    id SERIAL PRIMARY KEY,
    examen_id INT NOT NULL REFERENCES examens(id) ON DELETE CASCADE,
    professeur_id INT NOT NULL REFERENCES professeurs(id) ON DELETE CASCADE,
    type_surveillance VARCHAR(20) CHECK (type_surveillance IN ('Principal', 'Secondaire')),
    est_confirme BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_surveillance UNIQUE (examen_id, professeur_id)
);

CREATE INDEX idx_surveillances_examen ON surveillances(examen_id);
CREATE INDEX idx_surveillances_prof ON surveillances(professeur_id);

-- ============================================
-- TABLE: USERS (Authentification)
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('Doyen', 'Admin', 'Chef_Dept', 'Etudiant', 'Professeur')),
    departement_id INT REFERENCES departements(id) ON DELETE SET NULL,
    etudiant_id INT REFERENCES etudiants(id) ON DELETE CASCADE,
    professeur_id INT REFERENCES professeurs(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- VUES UTILES
-- ============================================

-- Vue: Examens avec détails complets
CREATE OR REPLACE VIEW v_examens_details AS
SELECT 
    e.id AS examen_id,
    m.code AS module_code,
    m.nom AS module_nom,
    f.nom AS formation,
    f.niveau,
    d.nom AS departement,
    l.nom AS lieu,
    l.type AS type_lieu,
    l.capacite_examen,
    e.date_examen,
    e.heure_debut,
    e.duree_minutes,
    e.nb_etudiants_inscrits,
    e.statut,
    e.annee_academique,
    e.session
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.departement_id = d.id
JOIN lieux_examen l ON e.lieu_id = l.id;

-- Vue: Charge de travail des professeurs
CREATE OR REPLACE VIEW v_charge_professeurs AS
SELECT 
    p.id AS professeur_id,
    p.nom || ' ' || p.prenom AS professeur,
    d.nom AS departement,
    COUNT(s.id) AS nb_surveillances,
    COUNT(DISTINCT e.date_examen) AS nb_jours_surveillance
FROM professeurs p
LEFT JOIN surveillances s ON p.id = s.professeur_id
LEFT JOIN examens e ON s.examen_id = e.id
JOIN departements d ON p.departement_id = d.id
WHERE e.statut = 'Planifié'
GROUP BY p.id, p.nom, p.prenom, d.nom;

-- ============================================
-- FONCTIONS UTILES
-- ============================================

-- Fonction: Vérifier conflits étudiants (même jour)
CREATE OR REPLACE FUNCTION check_student_conflict(
    p_etudiant_id INT,
    p_date DATE
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN inscriptions i ON m.id = i.module_id
        WHERE i.etudiant_id = p_etudiant_id
        AND e.date_examen = p_date
        AND e.statut = 'Planifié'
    );
END;
$$ LANGUAGE plpgsql;

-- Fonction: Compter surveillances prof par jour
CREATE OR REPLACE FUNCTION count_prof_surveillances(
    p_prof_id INT,
    p_date DATE
) RETURNS INT AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        WHERE s.professeur_id = p_prof_id
        AND e.date_examen = p_date
        AND e.statut = 'Planifié'
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Mettre à jour nb_etudiants_inscrits automatiquement
CREATE OR REPLACE FUNCTION update_exam_student_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE examens
    SET nb_etudiants_inscrits = (
        SELECT COUNT(DISTINCT i.etudiant_id)
        FROM inscriptions i
        WHERE i.module_id = NEW.module_id
        AND i.annee_academique = NEW.annee_academique
        AND i.session = NEW.session
    )
    WHERE module_id = NEW.module_id
    AND annee_academique = NEW.annee_academique
    AND session = NEW.session;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_exam_count
AFTER INSERT OR UPDATE ON examens
FOR EACH ROW
EXECUTE FUNCTION update_exam_student_count();

-- ============================================
-- COMMENTAIRES POUR DOCUMENTATION
-- ============================================
COMMENT ON TABLE examens IS 'Table principale des examens planifiés';
COMMENT ON TABLE surveillances IS 'Attribution des professeurs aux surveillances';
COMMENT ON COLUMN lieux_examen.capacite_examen IS 'Capacité max en période examen (20 étudiants)';
COMMENT ON FUNCTION check_student_conflict IS 'Vérifie si un étudiant a déjà un examen ce jour-là';

-- ============================================
-- FIN DU SCHEMA
-- ============================================