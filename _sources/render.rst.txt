Déploiement de l'API sur Render (Docker)
=======================================

Objectif
--------

Déployer l'API développée avec **Django REST Framework** sous forme
de service web conteneurisé, et la connecter à une base PostgreSQL
hébergée sur **Supabase**.

Le déploiement repose sur **Docker**, garantissant la portabilité
et la reproductibilité de l'environnement d'exécution.
---

Architecture de déploiement
---------------------------

- Application : Django + Django REST Framework
- Conteneurisation : Docker (image construite à partir du ``Dockerfile``)
- Plateforme de déploiement : Render (Web Service)
- Base de données : PostgreSQL (Supabase)

.. image:: _static/render.png
   :alt: Architecture de déploiement Render
   :align: center
   :width: 90%

---

Configuration des variables d'environnement
-------------------------------------------

Les paramètres sensibles et dépendants de l'environnement sont injectés
via les variables d'environnement Render :

- Connexion PostgreSQL (Supabase) :
  - ``DB_HOST``
  - ``DB_NAME``
  - ``DB_USER``
  - ``DB_PASSWORD``
  - ``DB_PORT``
- Paramètres Django :
  - ``DJANGO_SECRET_KEY``
  - ``DEBUG``
  - ``ALLOWED_HOSTS``

Cette approche évite toute configuration en dur dans le code
et facilite le passage entre environnements.
---

Processus de déploiement
------------------------

Le déploiement est déclenché automatiquement à chaque nouveau commit
sur la branche principale du dépôt GitHub.

1) Phase de build
^^^^^^^^^^^^^^^^^
- Construction de l'image Docker à partir du ``Dockerfile``.
- Installation des dépendances Python définies dans les fichiers
  ``requirements``.
- Vérification de la cohérence de l'environnement d'exécution.

2) Phase de run
^^^^^^^^^^^^^^^
- Démarrage du conteneur.
- Exécution du script de démarrage :
  - application des migrations Django,
  - lancement du serveur d'application.
- Mise à disposition de l'API via l'URL publique fournie par Render.

---

Vérifications post-déploiement
------------------------------

Après le déploiement, plusieurs vérifications sont effectuées :

- Accessibilité de l'URL publique du service Render.
- Appel d'un endpoint API simple (ex. liste d'offres) pour valider :
  - la connexion à la base PostgreSQL,
  - le bon fonctionnement de l'ORM et des serializers.
- Consultation des logs Render pour détecter :
  - erreurs de migration,
  - problèmes de connexion à la base,
  - erreurs d'import ou de configuration.
---

Remarques
---------

Le service est déployé sur une instance gratuite Render, impliquant
un arrêt automatique après une période d'inactivité.
Ce comportement est pris en compte lors des tests de disponibilité
et n'impacte pas les objectifs fonctionnels du projet.
