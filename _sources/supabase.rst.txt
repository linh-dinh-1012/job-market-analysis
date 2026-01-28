Hébergement PostgreSQL sur Supabase
==================================

Objectif
--------
Utiliser Supabase comme hébergement PostgreSQL managé pour faciliter :
- l'accès distant,
- la stabilité de la base en production,
- l'intégration avec l'API déployée.

.. image:: _static/supabase_1.png
   :alt: Schéma relationnel PostgreSQL - vue d'ensemble
   :align: center
   :width: 90%

---

Étapes
------

1) Créer un projet Supabase
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Créer un projet.
- Récupérer les informations de connexion (host, port, db, user, password).

2) Créer le schéma
^^^^^^^^^^^^^^^^^^
- Exécuter le script SQL (tables + contraintes) dans l'éditeur SQL Supabase.

3) Charger les données
^^^^^^^^^^^^^^^^^^^^^^
- Ingestion via le pipeline Python.
