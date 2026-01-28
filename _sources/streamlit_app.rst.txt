Application Streamlit (exploration et validation)
=================================================

Objectif
--------

Développer une application interactive permettant :

- de valider le bon fonctionnement de la chaîne
  **PostgreSQL → API → accès applicatif**,
- d'explorer visuellement les données ingérées,
- de répondre aux principales questions analytiques du projet.

L'application est construite avec le framework **Streamlit**,
offrant une interface web simple à déployer et à utiliser.

---

Connexion aux données
---------------------

L'application se connecte directement à la base PostgreSQL hébergée
sur Supabase.

La connexion utilise les mêmes paramètres que ceux configurés pour l'API Django REST,
assurant la cohérence des accès.
---

Structure de l'application
--------------------------

L'interface est organisée en **onglets thématiques**, chacun
correspondant à une question d'analyse.

.. image:: _static/streamlit_0.png
   :alt: Vue d'ensemble des onglets Streamlit
   :align: center
   :width: 90%


---

Onglet « Marché »
-----------------

Objectif
^^^^^^^^
Fournir une vue globale du marché de l'emploi étudié.

.. image:: _static/streamlit_marche.png
   :alt: Vue d'ensemble des onglets Streamlit
   :align: center
   :width: 90%

.. image:: _static/streamlit_2.png
   :alt: Top 5 des villes avec le plus d'offres d'emploi
   :align: center
   :width: 90%


Fonctionnalités
^^^^^^^^^^^^^^^
- Calcul du nombre total d'offres distinctes.
- Affichage tabulaire des offres. 
- Identification des localisations les plus représentées
  via un classement des villes.

Cette vue permet de répondre à la question :
*« Dans quelles zones géographiques se concentrent les offres ? »*

---

Onglet « Compétences »
---------------------

Objectif
^^^^^^^^
Identifier les compétences les plus demandées et leur priorité relative.

.. image:: _static/streamlit_4.png
   :alt: Top 5 hard-skills les plus demandées
   :align: center
   :width: 90%

.. image:: _static/streamlit_5.png
   :alt: Top 5 soft-skills les plus demandées
   :align: center
   :width: 90%

Fonctionnalités
^^^^^^^^^^^^^^^
- Agrégation des compétences par catégorie :
  - compétences techniques (hard skills),
  - compétences comportementales (soft skills).
- Comptage du nombre d'offres associées à chaque compétence.
- Calcul du pourcentage d'offres concernées.
- Visualisation des compétences dominantes (tableaux et graphiques).

Cet onglet répond à la question :
*« Quelles compétences sont les plus fréquemment requises,
et doivent être priorisées dans la préparation du profil ? »*

---

Onglet « Salaire »
-----------------

Objectif
^^^^^^^^
Explorer la disponibilité et les bornes salariales.

.. image:: _static/streamlit_6.png
   :alt: Salaire minimum et maximum des offres d'emploi
   :align: center
   :width: 90%

Fonctionnalités
^^^^^^^^^^^^^^^
- Calcul du nombre d'offres contenant une information salariale exploitable.
- Comparaison entre volume total d'offres et volume avec salaire renseigné.
- Affichage des bornes salariales annuelles lorsque disponibles.

Cet onglet permet de répondre à la question :
*« Quels niveaux de salaire minimum et maximum apparaissent dans les offres,
afin de préparer les échanges avec les recruteurs ? »*

---

Onglet « Géographie »
--------------------

Objectif
^^^^^^^^
Visualiser la répartition spatiale des offres d'emploi.

.. image:: _static/streamlit_3.png
   :alt: Répartition géographique des offres d'emploi
   :align: center
   :width: 90%

Fonctionnalités
^^^^^^^^^^^^^^^
- Filtrage des offres disposant de coordonnées géographiques.
- Affichage cartographique interactif à l'aide de Plotly et OpenStreetMap.
- Exploration visuelle par survol (intitulé, ville, type de contrat).

Cette visualisation facilite l'analyse :
*« Où se situent géographiquement les opportunités identifiées ? »*

---

Onglet « Métiers proches »
-------------------------

Objectif
^^^^^^^^
Identifier des intitulés de postes proches sémantiquement
afin d'élargir le champ de recherche.

.. image:: _static/streamlit_7.png
   :alt: Répartition géographique des offres d'emploi
   :align: center
   :width: 90%

Méthode
^^^^^^^
- Nettoyage et normalisation des intitulés de postes.
- Calcul d'embeddings multilingues à l'aide d'un modèle
  ``SentenceTransformer``.
- Mesure de similarité cosinus entre un intitulé de référence
  et les intitulés présents dans la base.
- Restitution des intitulés proches au-dessus d'un seuil de similarité (70%).

Résultat
^^^^^^^^
Pour chaque métier proche :
- score de similarité sémantique,
- nombre d'offres associées.

Cet onglet répond à la question :
*« Quels intitulés alternatifs ou voisins peuvent être utilisés
comme mots-clés pour élargir la recherche d'emploi ? »*

---

Rôle dans l'architecture globale
--------------------------------

L'application Streamlit joue un double rôle :

- **outil d'exploration analytique**, facilitant l'interprétation des données,
- **outil de validation technique**, confirmant :
  - la cohérence des données stockées,
  - l'accessibilité de la base depuis un service externe,
  - la stabilité du pipeline après déploiement.
Elle constitue la dernière étape visible de la chaîne
**collecte → prétraitement → base → API → exploration**.
