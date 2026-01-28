Prétraitement et normalisation
==============================

Objectif
--------

Transformer des données hétérogènes issues de plusieurs sources en tables cohérentes,
comparables et exploitables pour l’analyse, tout en améliorant la qualité des données
et la reproductibilité du pipeline.

Les étapes de prétraitement sont conçues pour :
- réduire l’hétérogénéité des formats,
- expliciter les hypothèses de transformation,
- préparer les données à la modélisation relationnelle et à l’analyse statistique.

Étapes principales
------------------

1) Normalisation des champs textuels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Garantir une comparaison fiable des textes (intitulés, descriptions, libellés)
en limitant les variations purement typographiques.

Méthodes
""""""""
- Passage systématique en minuscules.
- Suppression des espaces multiples et des caractères invisibles (ex. ``\u00a0``).
- Nettoyage des caractères non alphabétiques non pertinents.
- Normalisation spécifique des intitulés de poste :
  suppression des contenus entre parenthèses et de la ponctuation.

Ces traitements permettent d’améliorer :
- le comptage des intitulés similaires,
- les calculs de similarité sémantique,
- la déduplication partielle.

2) Localisation et référentiel géographique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Extraire des informations géographiques exploitables à partir de libellés textuels
souvent hétérogènes.

Méthodes
""""""""
- Normalisation Unicode pour corriger les problèmes d’encodage.
- Extraction du code département et du nom de ville à partir de libellés
  de type ``"75 - Paris"``.
- Nettoyage des noms de villes (suppression des arrondissements et variantes).
- Appariement avec un référentiel départemental externe (CSV) pour enrichir
  les offres avec des coordonnées géographiques (latitude, longitude).

Comportement dégradé
""""""""""""""""""""
- En l’absence de référentiel ou de correspondance valide, la ville issue de la
  source est conservée sans coordonnées GPS.
- Cette approche permet de ne pas bloquer le pipeline en cas de données incomplètes.

3) Normalisation des types de contrat
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Réduire la diversité des libellés contractuels à un ensemble de catégories
comparables.

Méthodes
""""""""
- Regroupement heuristique des libellés vers des catégories normalisées
  (ex. ``FULL_TIME``, ``TEMPORAIN``, ``INTERN``).
- Conservation des libellés bruts en parallèle pour audit ou analyses ultérieures.

4) Parsing et harmonisation des salaires (France Travail)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Extraire des bornes salariales numériques exploitables à partir de champs textuels
peu structurés.

Méthodes
""""""""
- Extraction des valeurs numériques présentes dans les libellés de salaire.
- Détection heuristique de l’unité (horaire, mensuelle, annuelle).
- Conversion des montants vers une unité annuelle lorsque possible.
- Traitement spécifique des valeurs annuelles exprimées en milliers.
- Exclusion des salaires non informatifs (zéro ou absence de chiffres).

Résultat
""""""""
- Deux bornes numériques : salaire minimum et salaire maximum (annuels).
- Valeurs ``NULL`` si l’information n’est pas exploitable.

5) Compétences et langues
^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Structurer les compétences et langues associées aux offres pour permettre
des analyses quantitatives.

France Travail
""""""""""""""
- Distinction explicite entre compétences **requises** et **souhaitées**
  à partir du champ ``exigence`` (``E`` / ``S``).
- Séparation des compétences techniques (hard skills) et des qualités
  professionnelles (soft skills).
- Même logique appliquée aux langues.

Welcome to the Jungle
"""""""""""""""""""""
- Absence de hiérarchisation requise/souhaitée dans la source.
- Regroupement des compétences techniques et savoir-faire dans une liste unique.
- Conservation des soft skills et langues lorsque disponibles.

6) Harmonisation multi-sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objectif
""""""""
Produire un schéma commun minimal permettant :
- des analyses transversales,
- des visualisations comparables,
- sans fusionner artificiellement des sources hétérogènes dans la base principale.

Méthodes
""""""""
- Transformation des jeux de données France Travail et Welcome to the Jungle
  vers une structure commune.
- Concaténation contrôlée des sources.
- Remplissage défensif des champs textuels manquants pour éviter les erreurs
  lors des traitements analytiques.

7) Qualité et sécurité des données
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Indicateurs suivis
""""""""""""""""""
- Taux de valeurs manquantes par champ (salaire, localisation, compétences).
- Détection de doublons via :
  URL d’origine,
  identifiant source lorsque disponible.

Principes
"""""""""
- Préserver les données brutes autant que possible.
- Rendre explicites les transformations appliquées.
- Garantir la reproductibilité des étapes de prétraitement.
