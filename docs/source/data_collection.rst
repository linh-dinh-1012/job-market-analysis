Collecte des données
====================

A) France Travail (API)
-----------------------

Objectif
^^^^^^^^
Collecter des offres d'emploi de manière reproductible via l'API officielle de France Travail,
en s'appuyant sur des requêtes paramétrables et un mécanisme d'authentification sécurisé.

Principe
^^^^^^^^
- Authentification via OAuth2 (``client_credentials``) avec récupération dynamique d'un
  **access token** à partir des variables d'environnement.
- Appels HTTP vers l'endpoint de recherche d'offres, avec paramètres contrôlés :
  mots-clés, localisation, type de contrat.
- Pagination explicite via le paramètre ``range`` afin d'itérer sur l'ensemble des résultats.
- Limitation volontaire du nombre d'offres collectées (``max_results``) pour maîtriser
  le volume et le temps d'exécution.
- Temporisation entre les requêtes (``sleep``) pour respecter les quotas et limiter
  les erreurs temporaires.

Implémentation
^^^^^^^^^^^^^^
La collecte est réalisée à l'aide de la bibliothèque ``requests``.  
Chaque réponse JSON est parsée et les résultats sont concaténés dans une structure tabulaire
(Pandas DataFrame).

Les principes suivants sont appliqués :
- arrêt de la pagination lorsqu'aucun résultat n'est retourné,
- arrêt anticipé si le nombre de résultats est inférieur à la taille de page demandée,
- gestion des erreurs HTTP via ``raise_for_status``.

Le résultat final est un DataFrame contenant les champs bruts fournis par l'API,
servant de point d'entrée au pipeline de prétraitement.

---

B) Welcome to the Jungle (web scraping)
---------------------------------------

Objectif
^^^^^^^^
Compléter l'exploration du marché avec une source non-API, en particulier pour les offres
publiées par des PME, moins représentées dans certaines bases institutionnelles.

Principe
^^^^^^^^
- Navigation automatisée des pages de résultats à l'aide de Selenium (mode headless).
- Construction dynamique des URLs de recherche à partir de mots-clés.
- Parcours paginé des pages liste, avec récupération des liens vers les offres individuelles.
- Déduplication des offres à partir de leur URL avant extraction détaillée.

Extraction des données
^^^^^^^^^^^^^^^^^^^^^^
Pour chaque offre, la page détail est analysée et les métadonnées sont extraites à partir
des blocs **JSON-LD** embarqués dans le HTML.

Les informations collectées incluent notamment :
- intitulé du poste,
- entreprise,
- localisation,
- type de contrat (normalisé),
- description,
- salaire (si disponible),
- expérience requise (convertie en années lorsque possible),
- secteur d'activité et informations sur l'entreprise.

Prétraitement léger lors de la collecte
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Certaines normalisations sont effectuées dès la phase de collecte :
- regroupement des types de contrat dans des catégories standardisées,
- extraction et harmonisation des années d'expérience,
- structuration des champs textuels.

Ces données issues de Welcome to the Jungle ne sont pas fusionnées directement
dans la base France Travail, mais utilisées comme source complémentaire.
