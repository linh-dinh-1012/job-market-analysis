-- ============================================================
-- Requêtes Analyses descriptives reproductibles
-- Source : tables canoniques PostgreSQL
-- ============================================================


-- 0) Volume global du corpus
SELECT COUNT(*) AS nb_offres
FROM job_offer;


-- 1) Compétences les plus fréquentes 
SELECT
    s.category,
    s.name,
    COUNT(*) AS frequency
FROM job_offer_skill jos
JOIN skill s ON s.id = jos.skill_id
GROUP BY s.category, s.name
ORDER BY frequency DESC;


-- 2) Hard skills : required vs optional + % des offres
WITH total_jobs AS (
    SELECT COUNT(*) AS total FROM job_offer
)
SELECT
    s.name AS skill,
    jos.requirement_level,
    COUNT(DISTINCT jos.job_offer_id) AS job_count,
    ROUND(
        100.0 * COUNT(DISTINCT jos.job_offer_id) / NULLIF(t.total, 0),
        2
    ) AS pct_jobs
FROM job_offer_skill jos
JOIN skill s ON s.id = jos.skill_id
CROSS JOIN total_jobs t
WHERE s.category = 'hard'
GROUP BY s.name, jos.requirement_level, t.total
ORDER BY pct_jobs DESC;


-- 3) Soft skills : % des offres
WITH total_jobs AS (
    SELECT COUNT(*) AS total FROM job_offer
)
SELECT
    s.name AS skill,
    COUNT(DISTINCT jos.job_offer_id) AS job_count,
    ROUND(
        100.0 * COUNT(DISTINCT jos.job_offer_id) / NULLIF(t.total, 0),
        2
    ) AS pct_jobs
FROM job_offer_skill jos
JOIN skill s ON s.id = jos.skill_id
CROSS JOIN total_jobs t
WHERE s.category = 'soft'
GROUP BY s.name, t.total
ORDER BY pct_jobs DESC;


-- 4) Top localisations (villes)
SELECT
    l.ville,
    COUNT(*) AS nb_offres
FROM job_offer jo
JOIN location l ON l.id = jo.location_id
GROUP BY l.ville
ORDER BY nb_offres DESC;


-- 5) Géographie exploitable (coordonnées GPS)
SELECT
    l.ville,
    l.latitude,
    l.longitude,
    COUNT(*) AS nb_offres
FROM job_offer jo
JOIN location l ON l.id = jo.location_id
WHERE l.latitude IS NOT NULL
  AND l.longitude IS NOT NULL
GROUP BY l.ville, l.latitude, l.longitude
ORDER BY nb_offres DESC;


-- 6) Couverture GPS
SELECT
    COUNT(*) FILTER (
        WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
    ) AS with_gps,
    COUNT(*) AS total,
    ROUND(
        100.0
        * COUNT(*) FILTER (
            WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS pct_with_gps
FROM job_offer jo
LEFT JOIN location l ON l.id = jo.location_id;


-- 7) Répartition par type de contrat
SELECT
    c.type_contrat,
    COUNT(*) AS nb_offres
FROM job_offer jo
JOIN contract c ON c.id = jo.contract_id
GROUP BY c.type_contrat
ORDER BY nb_offres DESC;


-- 8) Répartition temporelle paramétrable
SELECT
  DATE_TRUNC('month', jo.date_posted) AS period,
  COUNT(*) AS nb_offres
FROM job_offer jo
WHERE jo.date_posted IS NOT NULL
GROUP BY 1
ORDER BY 1;


-- 9) Salary : couverture et bornes observées (min / max)
-- Exemple de filtre géographique (Paris)
SELECT
    COUNT(*) FILTER (WHERE salary_min_annual IS NOT NULL) AS offres_avec_salaire,
    COUNT(*) AS total_offres,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE salary_min_annual IS NOT NULL)
        / NULLIF(COUNT(*), 0),
        1
    ) AS pct_avec_salaire,
    MIN(salary_min_annual) AS salaire_min,
    MAX(salary_max_annual) AS salaire_max
FROM job_offer
WHERE location ILIKE '%paris%';

