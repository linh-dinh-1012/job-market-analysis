Mise en place de l'API Django
=============================

Objectif
--------

Mettre en place une **API REST robuste et reproductible** permettant :

- l'accès programmatique aux données stockées en base PostgreSQL,
- l'exposition des données à des applications externes (Streamlit, analyses),

Le framework **Django** est utilisé comme socle applicatif,
complété par **Django REST Framework** pour la construction de l'API.

---

Initialisation du projet Django
-------------------------------

Le projet a été initialisé à l'aide de la commande standard :

- ``django-admin startproject backend``

La structure repose sur :
- un projet principal ``backend`` (configuration globale),
- une application dédiée ``rest_api`` pour l'exposition des endpoints.

Le fichier ``manage.py`` sert de point d'entrée unique pour :
- les migrations,
- la gestion des utilisateurs,
- le lancement du serveur,
- les commandes d'administration.

---

Configuration ASGI et WSGI
--------------------------

Deux interfaces d'exécution sont configurées :

- **WSGI** (``backend.wsgi``) pour un déploiement classique synchrone,
- **ASGI** (``backend.asgi``) pour une compatibilité future avec
  des serveurs asynchrones.

Ces deux fichiers exposent un objet ``application`` initialisé
à partir du module de configuration ``backend.settings``.

Ce double support facilite l'adaptation à différents environnements
de déploiement sans modifier le code applicatif.

---

Gestion des paramètres et des secrets
-------------------------------------

Les paramètres sensibles ne sont jamais codés en dur dans la logique applicative.

Les variables suivantes sont injectées via l'environnement :

- paramètres de connexion PostgreSQL :
  ``DB_HOST``, ``DB_NAME``, ``DB_USER``, ``DB_PASSWORD``, ``DB_PORT`` ;
- paramètres Django :
  ``DEBUG``, ``ALLOWED_HOSTS``, ``CSRF_TRUSTED_ORIGINS``,
  ``CORS_ALLOWED_ORIGINS``.

Cette approche garantit :
- la séparation entre code et configuration,
- la portabilité entre environnements (local, Render),
- la sécurité des secrets.

---

Connexion à la base PostgreSQL
------------------------------

Django est configuré pour utiliser PostgreSQL comme moteur de base de données.

La configuration repose exclusivement sur les variables d'environnement,
permettant une connexion directe à une base distante hébergée sur Supabase.

Ce choix assure la cohérence avec :
- le pipeline d'ingestion Python,
- l'API REST,
- les outils d'analyse et de visualisation.

---

Applications et middleware
--------------------------

Les applications installées incluent :

- les modules Django standards (authentification, sessions, admin),
- **Django REST Framework** pour l'API,
- ``rest_api`` pour la logique métier,
- ``corsheaders`` pour la gestion des accès cross-origin.

Les middlewares sont configurés pour :
- autoriser les requêtes cross-origin depuis des applications externes,
- servir les fichiers statiques via **Whitenoise**,
- garantir la sécurité et la gestion des sessions.

---

Routage de l'API
----------------

Le routage global est défini dans ``backend.urls`` :

- ``/admin/`` : interface d'administration Django,
- ``/api/`` : point d'entrée de l'API REST.

Les routes détaillées de l'API sont définies dans l'application ``rest_api``,
permettant une séparation claire entre configuration globale
et logique métier.

---

Création automatisée du superutilisateur
----------------------------------------

Un script dédié permet la création automatique d'un superutilisateur
lors du déploiement.

Le comportement est contrôlé par des variables d'environnement :
- activation conditionnelle (``CREATE_SUPERUSER=true``),
- identifiants fournis via variables sécurisées.

Cette approche facilite :
- l'initialisation des environnements distants,
- l'accès à l'interface d'administration sans intervention manuelle,
- la reproductibilité des déploiements.

---

Rôle de Django dans l'architecture globale
------------------------------------------

Dans l'architecture du projet, Django joue le rôle de :

- **couche d'accès aux données** via l'ORM,
- **API REST** exposant les données normalisées,
- **point de jonction** entre la base PostgreSQL et les applications clientes.

Cette couche applicative constitue un composant central entre
l'ingestion des données et leur exploitation analytique.
