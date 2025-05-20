# 🎬 Projet Data : Recommandation de Films pour un Cinéma de la Creuse

## Introduction

> « Netflix est un service de diffusion en streaming qui permet à ses membres de regarder une grande variété de séries TV, films, documentaires, etc. sur des milliers d’appareils connectés à Internet. »

Netflix, créé en 1998, est aujourd’hui un géant du streaming, reconnu pour son système de recommandation qui optimise l’expérience utilisateur et sa stratégie marketing grâce à la data. Notre client n’est pas Netflix, mais il a de grandes ambitions !

## Contexte & Objectif

Un cinéma indépendant de la Creuse, en perte de vitesse, souhaite se digitaliser et offrir à ses clients un site web moderne, enrichi d’un moteur de recommandation de films. L’objectif est double :
- Proposer des statistiques et KPI sur les films et acteurs à travers des dashboards interactifs.
- Mettre en place un système de recommandation personnalisée, même en situation de cold start (aucune préférence utilisateur connue).

Le client fournit une base de données issue d’IMDb, complétée par des données TMDB (pays de production, budget, recettes, posters…).

## Démarche & Planning

### 1. Étude de marché
Nous avons commencé par une étude de marché sur la consommation de cinéma dans la région de la Creuse (sources : CNC, Insee) pour mieux comprendre les attentes du public local et orienter l’analyse des données.

### 2. Exploration, nettoyage et réduction des données
- Import et fusion des datasets IMDb et TMDB (plusieurs millions de lignes initialement).
- Nettoyage, filtrage et création d’un dataframe réduit, pertinent pour la suite.
- Export d’un fichier allégé [ressources/df_final.csv](ressources/df_final.csv) pour accélérer les analyses.

### 3. Dashboarding & Analyses statistiques
- Visualisation de la répartition des films par genre, pays, décennie, durée, etc.
- Identification des acteurs/réalisateurs les plus présents, des films les mieux notés, etc.
- Outils utilisés : Pandas, Matplotlib, Seaborn, Plotly.

### 4. Machine Learning & Recommandation
- Mise en place d’un modèle de recommandation basé sur KNN (scikit-learn).
- Recommandation de films similaires à ceux appréciés par l’utilisateur.
- Préparation à l’intégration dans une application web.

### 5. Application Web
- Développement d’une interface utilisateur avec Streamlit pour rendre le système accessible et interactif.
- Affichage des recommandations et des KPI, possibilité de saisir un film pour obtenir des suggestions personnalisées.

## Ressources & Données

- Données IMDb : [https://datasets.imdbws.com/](https://datasets.imdbws.com/)
- Données TMDB complémentaires (budget, recettes, images)
- Documentation des colonnes et tables : [IMDb Datasets](https://www.imdb.com/interfaces/)

## Organisation du projet

- `data/nettoyage.ipynb` : Exploration, nettoyage et fusion des données.
- `data/analyse.ipynb` : Analyses statistiques, visualisations et premiers KPI.
- `ressources/df_final.csv` : Dataframe réduit, prêt pour l’analyse et la recommandation.
- `application/` : Scripts pour la partie application web (à venir).

## Prochaines étapes

- Finaliser le modèle de recommandation (KNN).
- Intégrer le modèle et les visualisations dans une application Streamlit.
- Préparer la présentation finale et les livrables pour le client.

## Livrables attendus

- Un notebook d’exploration/nettoyage avec visualisations et explications.
- Un dashboard interactif présentant les KPI.
- Un notebook dédié au système de recommandation (machine learning).
- Une application web testable par le client.

---

**Remarque technique** :  
Les datasets IMDb sont volumineux (plusieurs millions de lignes). Nous avons donc procédé à un important travail de filtrage et d’export de données allégées pour garantir la réactivité des analyses et de l’application.

---

## Auteurs
Imad - Jérémy - Vincent

Projet réalisé dans le cadre de la Wild Code School.
