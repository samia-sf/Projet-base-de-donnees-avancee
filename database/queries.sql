-- ============================================
-- REQUETES SQL UTILES - PLATEFORME NUM_EXAM
-- ============================================

-- ============================================
-- STATISTIQUES GENERALES
-- ============================================

-- Nombre total d'entites
SELECT 
    'Departements' as entite, COUNT(*) as nombre FROM departements
UNION ALL
SELECT 'Formations', COUNT(*) FROM formations
UNION ALL
SELECT 'Etudiants', COUNT(*) FROM etudiants
UNION ALL
SELECT 'Professeurs', COUNT(*) FROM professeurs
UNION ALL
SELECT 'Modules', COUNT(*) FROM modules
UNION ALL
SELECT 'Lieux d''examen', COUNT(*) FROM lieux_examen
UNION ALL
SELECT 'Inscriptions', COUNT(*) FROM inscriptions
UNION ALL
SELECT 'Examens planifies', COUNT(*) FROM examens
UNION ALL
SELECT 'Surveillances', COUNT(*) FROM surveillances;

-- ============================================
-- EXAMENS
-- ============================================

-- Liste complete des examens avec details
SELECT 
    e.date_examen,
    e.heure_debut,
    e.duree_minutes,
    m.code as module_code,
    m.nom as module_nom,
    f.nom as formation,
    d.nom as departement,
    l.nom as lieu,
    l.type as type_lieu,
    e.nb_etudiants_inscrits,
    e.statut
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.departement_id = d.id
JOIN lieux_examen l ON e.lieu_id = l.id
ORDER BY e.date_examen, e.heure_debut;

-- Examens par departement
SELECT 
    d.nom as departement,
    COUNT(e.id) as nb_examens,
    MIN(e.date_examen) as premiere_date,
    MAX(e.date_examen) as derniere_date
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.departement_id = d.id
GROUP BY d.id, d.nom
ORDER BY nb_examens DESC;

-- Examens par jour
SELECT 
    date_examen,
    COUNT(*) as nb_examens,
    SUM(nb_etudiants_inscrits) as total_etudiants,
    COUNT(DISTINCT lieu_id) as nb_salles_utilisees
FROM examens
WHERE statut = 'Planifie'
GROUP BY date_examen
ORDER BY date_examen;

-- ============================================
-- ETUDIANTS
-- ============================================

-- Emploi du temps d'un etudiant
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
WHERE i.etudiant_id = 1  -- Remplacer par l'ID de l'etudiant
AND e.annee_academique = '2024-2025'
ORDER BY e.date_examen, e.heure_debut;

-- Etudiants par formation
SELECT 
    f.nom as formation,
    d.nom as departement,
    COUNT(e.id) as nb_etudiants
FROM etudiants e
JOIN formations f ON e.formation_id = f.id
JOIN departements d ON f.departement_id = d.id
GROUP BY f.id, f.nom, d.nom
ORDER BY nb_etudiants DESC;

-- ============================================
-- PROFESSEURS & SURVEILLANCES
-- ============================================

-- Surveillances d'un professeur
SELECT 
    e.date_examen,
    e.heure_debut,
    e.duree_minutes,
    m.code as module_code,
    m.nom as module_nom,
    l.nom as lieu,
    s.type_surveillance
FROM surveillances s
JOIN examens e ON s.examen_id = e.id
JOIN modules m ON e.module_id = m.id
JOIN lieux_examen l ON e.lieu_id = l.id
WHERE s.professeur_id = 1  -- Remplacer par l'ID du professeur
AND e.annee_academique = '2024-2025'
ORDER BY e.date_examen, e.heure_debut;

-- Charge de travail des professeurs
SELECT 
    p.matricule,
    p.nom,
    p.prenom,
    d.nom as departement,
    COUNT(s.id) as nb_surveillances,
    COUNT(DISTINCT e.date_examen) as nb_jours
FROM professeurs p
LEFT JOIN surveillances s ON p.id = s.professeur_id
LEFT JOIN examens e ON s.examen_id = e.id
LEFT JOIN departements d ON p.departement_id = d.id
WHERE e.statut = 'Planifie' OR e.id IS NULL
GROUP BY p.id, p.matricule, p.nom, p.prenom, d.nom
ORDER BY nb_surveillances DESC;

-- Professeurs les plus sollicites
SELECT 
    p.nom || ' ' || p.prenom as professeur,
    d.nom as departement,
    COUNT(s.id) as nb_surveillances
FROM surveillances s
JOIN professeurs p ON s.professeur_id = p.id
JOIN departements d ON p.departement_id = d.id
JOIN examens e ON s.examen_id = e.id
WHERE e.statut = 'Planifie'
GROUP BY p.id, p.nom, p.prenom, d.nom
HAVING COUNT(s.id) > 5
ORDER BY nb_surveillances DESC;

-- ============================================
-- CONFLITS
-- ============================================

-- Etudiants avec plusieurs examens le meme jour (CONFLIT!)
SELECT 
    et.matricule,
    et.nom,
    et.prenom,
    e.date_examen,
    COUNT(*) as nb_examens,
    string_agg(m.code, ', ' ORDER BY e.heure_debut) as modules
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN inscriptions i ON m.id = i.module_id
JOIN etudiants et ON i.etudiant_id = et.id
WHERE e.statut = 'Planifie'
GROUP BY et.id, et.matricule, et.nom, et.prenom, e.date_examen
HAVING COUNT(*) > 1
ORDER BY nb_examens DESC, e.date_examen;

-- Professeurs avec trop de surveillances un meme jour (> 3)
SELECT 
    p.matricule,
    p.nom,
    p.prenom,
    e.date_examen,
    COUNT(*) as nb_surveillances,
    string_agg(m.code, ', ' ORDER BY e.heure_debut) as modules
FROM surveillances s
JOIN professeurs p ON s.professeur_id = p.id
JOIN examens e ON s.examen_id = e.id
JOIN modules m ON e.module_id = m.id
WHERE e.statut = 'Planifie'
GROUP BY p.id, p.matricule, p.nom, p.prenom, e.date_examen
HAVING COUNT(*) > 3
ORDER BY nb_surveillances DESC;

-- Salles avec depassement de capacité
SELECT 
    l.nom as salle,
    l.capacite_examen,
    e.nb_etudiants_inscrits,
    (e.nb_etudiants_inscrits - l.capacite_examen) as depassement,
    m.code as module_code,
    e.date_examen
FROM examens e
JOIN lieux_examen l ON e.lieu_id = l.id
JOIN modules m ON e.module_id = m.id
WHERE e.nb_etudiants_inscrits > l.capacite_examen
ORDER BY depassement DESC;

-- Chevauchements de salles (meme salle, meme créneau)
SELECT 
    l.nom as salle,
    e1.date_examen,
    e1.heure_debut,
    m1.code as module1,
    m2.code as module2
FROM examens e1
JOIN examens e2 ON 
    e1.lieu_id = e2.lieu_id 
    AND e1.date_examen = e2.date_examen
    AND e1.heure_debut = e2.heure_debut
    AND e1.id < e2.id
JOIN lieux_examen l ON e1.lieu_id = l.id
JOIN modules m1 ON e1.module_id = m1.id
JOIN modules m2 ON e2.module_id = m2.id
WHERE e1.statut = 'Planifie' AND e2.statut = 'Planifie';

-- ============================================
-- OCCUPATION DES RESSOURCES
-- ============================================

-- Taux d'occupation des salles par jour
SELECT 
    e.date_examen,
    COUNT(DISTINCT e.lieu_id) as salles_utilisees,
    (SELECT COUNT(*) FROM lieux_examen WHERE est_disponible = TRUE) as salles_disponibles,
    ROUND(
        COUNT(DISTINCT e.lieu_id)::numeric / 
        (SELECT COUNT(*) FROM lieux_examen WHERE est_disponible = TRUE) * 100, 
        2
    ) as taux_occupation_pct
FROM examens e
WHERE e.statut = 'Planifie'
GROUP BY e.date_examen
ORDER BY e.date_examen;

-- Salles les plus utilisees
SELECT 
    l.nom as salle,
    l.type,
    COUNT(e.id) as nb_utilisations,
    SUM(e.nb_etudiants_inscrits) as total_etudiants
FROM lieux_examen l
LEFT JOIN examens e ON l.id = e.lieu_id AND e.statut = 'Planifie'
GROUP BY l.id, l.nom, l.type
ORDER BY nb_utilisations DESC;

-- ============================================
-- STATISTIQUES PAR DEPARTEMENT
-- ============================================

-- Vue complete par departement
SELECT 
    d.nom as departement,
    COUNT(DISTINCT f.id) as nb_formations,
    COUNT(DISTINCT m.id) as nb_modules,
    COUNT(DISTINCT et.id) as nb_etudiants,
    COUNT(DISTINCT p.id) as nb_professeurs,
    COUNT(DISTINCT e.id) as nb_examens
FROM departements d
LEFT JOIN formations f ON d.id = f.departement_id
LEFT JOIN modules m ON f.id = m.formation_id
LEFT JOIN etudiants et ON f.id = et.formation_id
LEFT JOIN professeurs p ON d.id = p.departement_id
LEFT JOIN examens e ON m.id = e.module_id AND e.statut = 'Planifie'
GROUP BY d.id, d.nom
ORDER BY d.nom;

-- ============================================
-- VALIDATION ET VERIFICATION
-- ============================================

-- Verifier l'integrite des donnees
SELECT 
    'Etudiants sans formation' as verification,
    COUNT(*) as nombre
FROM etudiants
WHERE formation_id IS NULL
UNION ALL
SELECT 
    'Modules sans responsable',
    COUNT(*) 
FROM modules
WHERE professeur_responsable_id IS NULL
UNION ALL
SELECT 
    'Examens sans surveillants',
    COUNT(DISTINCT e.id)
FROM examens e
LEFT JOIN surveillances s ON e.id = s.examen_id
WHERE e.statut = 'Planifie' AND s.id IS NULL;

-- Resume global pour validation
SELECT 
    'Total examens planifies' as indicateur,
    COUNT(*)::text as valeur
FROM examens
WHERE statut = 'Planifie'
UNION ALL
SELECT 
    'Modules sans examen',
    COUNT(*)::text
FROM modules m
WHERE NOT EXISTS (
    SELECT 1 FROM examens e 
    WHERE e.module_id = m.id AND e.statut = 'Planifie'
)
UNION ALL
SELECT 
    'Conflits etudiants',
    COUNT(DISTINCT etudiant_id || '-' || date_examen)::text
FROM (
    SELECT i.etudiant_id, e.date_examen
    FROM examens e
    JOIN modules m ON e.module_id = m.id
    JOIN inscriptions i ON m.id = i.module_id
    WHERE e.statut = 'Planifie'
    GROUP BY i.etudiant_id, e.date_examen
    HAVING COUNT(*) > 1
) conflits
UNION ALL
SELECT 
    'Professeurs mobilises',
    COUNT(DISTINCT professeur_id)::text
FROM surveillances s
JOIN examens e ON s.examen_id = e.id
WHERE e.statut = 'Planifie';