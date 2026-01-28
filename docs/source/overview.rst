Vue d'ensemble du projet
========================

Objectif
--------

Le projet vise à transformer des offres d'emploi brutes en données structurées et exploitables pour :

- comprendre les tendances du marché du travail,
- identifier les compétences prioritaires d'un métier cible,
- analyser les dynamiques territoriales (où sont les offres),
- estimer des fourchettes salariales crédibles,
- enrichir la recherche d'emploi via des intitulés proches (similarité sémantique).

Périmètre des données
---------------------

- France Travail : collecte via API, stockage et analyse principale (PostgreSQL).
- Welcome to the Jungle : collecte complémentaire (web scraping) pour enrichir l'exploration.
- Base relationnelle : uniquement France Travail (choix de reproductibilité et stabilité du schéma).

Pipeline du projet
----------------------------

.. image:: _static/schema_projet.png
   :alt: Schéma du pipeline du projet
   :align: center
   :width: 90%

Livrables
---------

- Base PostgreSQL (schéma documenté).
- API REST (Django REST Framework) pour exposer des endpoints de consultation.
- Application Streamlit prove-of-concept consommant l'API.
- Documentation technique (cette doc Sphinx).