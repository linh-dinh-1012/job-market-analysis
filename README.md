# Job Market Analysis

Projet d’analyse du marché de l’emploi à partir des données de **France Travail** 
Les offres sont collectées, structurées et analysées, puis exposées via une **API REST** et un **dashboard interactif**.

---

## Fonctionnalités clés

- Collecte de données (API France Travail)
- Normalisation et stockage des données (PostgreSQL)
- Indicateurs analytiques : volumétrie, localisations, compétences, salaires
- Cartographie des offres et similarité sémantique des métiers
- API REST read-only pour l’accès aux données
- Tableau de bord interactif

---

## Stack

Python, PostgreSQL, Django REST Framework, Docker, Supabase, Render, Pandas, Plotly, Streamlit

## Exécution locale

Le projet peut être lancé localement via Docker :

```bash
docker build -t job-market-analysis .
docker run -p 8000:8000 job-market-analysis
