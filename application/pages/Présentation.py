import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#st.image("image_data_analyse.png", width=150)

# Chemin pour accéder aux ressources
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df_display_path = os.path.join(BASE_DIR, '../ressources', 'df_display.csv')
df_final_path = os.path.join(BASE_DIR, '../ressources', 'df_final.csv')
df_v4_path = os.path.join(BASE_DIR, '../ressources', 'df_v4.csv')

# Charger le fichier CSV contenant les données à afficher
df_display = pd.read_csv(df_display_path, sep=';', encoding='utf-8')
df = pd.read_csv(df_final_path, sep=';', encoding='utf-8')
df_v4 = pd.read_csv(df_v4_path, sep=';', encoding='utf-8')

st.title("Étapes du projet")
st.write("Après notre étude de marché sur la consommation de cinéma dans la région de la Creuse, nous avons réalisé une analyse approndie de la base de données pour identifier les tendances et les préférences des spectateurs. ")
st.write("Ci-dessous, les étapes suivies.")

st.subheader("🌐​ Jeux de données utilisés")
st.write("Nous avons utilisé le jeu de données TMDB (The Movie Database) et IMDB (Internet Movie Database) pour notre analyse.")
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Tmdb.new.logo.svg/langfr-1024px-Tmdb.new.logo.svg.png" height="150">
            <p style="font-weight: ">TMDb</p>
        </div>
        <div style="text-align: justify;">
            <p>The Movie Database est une base de données collaborative de films, séries et acteurs. Elle fournit des informations détaillées comme les résumés, genres, dates de sortie, et plus encore, souvent utilisée par les développeurs via son API gratuite.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/69/IMDB_Logo_2016.svg" height="150">
            <p style="font-weight: ">IMDb</p>
        </div>
        <div style="text-align: justify;">
            <p>L'Internet Movie Database est l'une des plus grandes bases de données en ligne sur le cinéma et les séries. Elle contient des fiches complètes sur les films, les acteurs, les critiques et les notes attribuées par les utilisateurs du monde entier.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

st.subheader("🕵️​ Nettoyage des données")
st.write("Nous avons pré-filtré les données pour réduire notre jeu de données à ~17 000 lignes :")
st.write("- Jointure des deux bases de données avec les clés communes :green['tconst'] et :green['imdb_id'].")
st.write("- Suppression des films sans titre.")
st.write("- Suppression des genres : Documentary / Short / News / Talk-show / Game-Show / Reality-TV / Adult.")
st.write("- Passages des colonnes :green['runtimeMinutes'], :green['id'], :green['popularity'], :green['runtime'], :green['revenue'], :green['vote_average'], :green['vote_count'] en format numérique.")
st.write("- Passages des dates en format datetime.")
st.write("- Filtre la colonne :green['production_country'] pour ne garder que les films français, américain ou britannique (USA|GB|FR|US).")
st.write("- Suppression des films sans note.")
st.write("- Suppression des films sortis avant 1990 dont la note est inférieure à 7/10.")
st.write("- Suppression des films ayant moins de 1500 votes.")
st.write("- Suppression des films dont la durée est inférieure à 60 minutes et supérieure à 250 minutes. ")
st.write("- Filtre pour ne garder que les 3 principaux acteurs et 1 réalisateur par film.")
st.write("")
st.write("Aperçu du jeu après un premier nettoyage:") 
st.dataframe(df.head(5), use_container_width=True)
st.markdown(":orange-badge[⚠️ Note :] D'autres modifications ont été apportées au jeu de données par la suite pour améliorer l'apprentissage de notre modèle de Machine Learning.")
# st.write("À noter que d'autres modifications ont été apportées au jeu de données par la suite pour améliorer l'apprentissage du Machine Learning.") 
st.divider()

st.subheader("📊​ Analyse des données")
st.write("Nous avons réalisé une analyse des données pour identifier les tendances et les préférences des spectateurs. Voici quelques-unes de nos découvertes :")

tab1, tab2, tab3, tab4 = st.tabs(["Durée des films", "Production par pays", "Acteurs les plus présents", "Nombre de films par année"])

# Graphique de la distribution en fonction de la durée des films
with tab1:
    fig1 = plt.figure(figsize=(8, 6))
    sns.histplot(data=df,x='runtimeMinutes', bins=15, kde=True, legend=False, alpha=0.8)
    plt.title('Distribution de la durée des films')
    max_rt = df["runtimeMinutes"].max()
    plt.xticks(np.arange(60, max_rt + 15, 15))
    plt.xlabel('Durée (minutes)')
    plt.ylabel('Nombre de films')
    st.pyplot(fig1)
    st.write("On constate qu'une courbe de Gauss se créé lorsqu'on affiche la distribution de la durée des films. On peut voir le pic de la distribution autour de 90-95 minutes, ce qui correspond à la durée moyenne d'un film. On peut aussi voir que la majorité des films ont une durée comprise entre 60 et 150 minutes.")

# Graphique pour la répartition des productions par pays
# Créer un dataframe avec les pays
with tab2:
    df_country = df.copy().reset_index()
    df_country = df_country[['tconst', 'production_countries']]
    # Dupliquer le dataframe pour chaque pays
    df_country = (
        df_country
        .assign(production_countries = df_country['production_countries'].str.split(','))  # chaînage en liste
        .explode('production_countries')                                  # une ligne par pays
        .assign(production_countries = lambda d: d['production_countries'].str.strip()) # suppression des espaces en trop
        .query("production_countries != '' and production_countries == production_countries")
        )
    # Regrouper les pays par nombre de films
    df_country = df_country.groupby('production_countries').agg(
        count=('production_countries', 'size')
        ).reset_index()
    # Créer un graphique à barres pour le nombre de films par pays et n'afficher que les 10 premiers
    df_country = df_country.sort_values(by='count', ascending=False).head(10)
    fig2 = plt.figure(figsize=(10, 5))
    sns.barplot(data=df_country, x='count', y='production_countries')
    plt.title('Nombre de films par pays')
    plt.xlabel('Nombre de films')
    plt.ylabel('Pays')
    plt.show()
    st.pyplot(fig2)
    st.write("Ci-dessus, la répartition des productions par pays. Nous pouvons encore voir des pays différents de ceux que nous avons sélectionnés pour notre étude de marché car il est affiché les pays ayant collaborés avec des productions américaines, britanniques ou françaises. On peut voir que les États-Unis sont le pays qui produit le plus de films, suivi de la France et du Royaume-Uni.")

# Dataframe avec les acteurs les plus présents
with tab3:
    df_cast = df.copy().reset_index()
    df_cast = df_cast[['tconst', 'directors']]

    df_cast = (
        df_cast
        .assign(director = df_cast['directors'].str.split(','))  # chaînage en liste
        .explode('directors')                                  # une ligne par genre
        .assign(director = lambda d: d['directors'].str.strip()) # suppression des espaces en trop
        .query("directors != '' and directors == directors")
        )


    # Regrouper les acteurs par nombre de films
    df_cast = df_cast.groupby('directors').agg(
        count=('directors', 'size')
        ).reset_index()

    df_cast_sorted = df_cast.sort_values(by='count', ascending=False).head(10)

    fig3 = plt.figure(figsize=(10, 8))
    sns.barplot(data=df_cast_sorted, x='count', y='directors')
    plt.title('10 directeurs de films les plus présents')
    plt.xlabel('Nombre de films')
    plt.ylabel('Directeurs')
    plt.show()
    st.pyplot(fig3)
    st.write("Ci-dessus, les 10 directeurs de films les plus présents dans notre jeu de données. On peut voir que Woddy Allen est le directeur le plus présent, suivi de Steven Soderbergh et Clint Eastwood.")

with tab4:
    df['year'] = pd.to_datetime(df['startYear'], format='%Y')

    #On récupere uniquemente les années 90 et jusqu'à aujourd'hui
    df_nineties = df[df['year'].dt.year >= 1990].copy()
    df_nineties['year'] = df_nineties['year'].dt.year
    # Créer une nouvelle colonne pour la décennie
    df_nineties['decade'] = (df_nineties['year'] // 10) * 10
    df_nineties['decade'] = df_nineties['decade'].astype(str)
    df_evolution = df_nineties.copy().reset_index()

    df_evolution = df_evolution[['tconst', 'year', 'decade']]
    df_evolution = df_evolution.groupby(['year', 'decade']).agg(
        count=('year', 'size')
        ).reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))

    # pour chaque décennie, on trace son aire
    for dec in df_evolution['decade'].unique():
        sub = df_evolution[df_evolution['decade'] == dec]
        ax.fill_between(
            sub['year'],
            sub['count'],
            alpha=0.8,            # transparence pour voir le chevauchement
            label=dec,
            step='mid'            # optionnel : pour une marche par année
        )

    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de films")
    ax.set_title("Évolution du nombre de films par année et par décennie")
    ax.legend(title="Décennie")
    plt.tight_layout()
    st.pyplot(fig)
    st.write("Ci-dessus, l'évolution du nombre de films par année et par décennie. On peut voir que le nombre de films produits a considérablement augmenté depuis les années 90, avec un pic dans les années 2000.")

st.divider()

st.subheader("🤖​ Machine Learning")
st.write("Nous avons utilisé un modèle de Machine Learning pour prédire les recommandations en fonction d'un film. Pour entrainer notre modèle, nous avons décidé de ne garder que certaines colonnes de notre dataframe :")
st.write("- :green['frenchTitle'] : titre français")
st.write("- :green['genres'] : genre")
st.write("- :green['averageRating'] : note moyenne")
st.write("- :green['numVotes'] : nombre de votes")
st.write("- :green['actor1'] : acteur principal")
st.write("- :green['actor2'] : second acteur")
st.write("- :green['actor3'] : troisième acteur")
st.write("- :green['director'] : réalisateur")
st.write("- :green['decade'] : décennie de sortie du film")
st.write(" Aperçu du jeu de données utilisé pour l'entraînement du modèle :")
st.dataframe(df_v4.head(10), use_container_width=True)
st.write("Nous avons utilisé un MultilabelBinarizer pour transformer les colonnes :green['genres'], :green['actors'] et :green['director'] en colonnes binaires. Cela permet de transformer les genres et les acteurs en colonnes binaires, ce qui est nécessaire pour l'entraînement du modèle de Machine Learning.")
st.write("Nous avons ensuite utilisé le modèle de Machine Learning :green['KNN'] (K-Nearest Neighbors) pour prédire les recommandations en fonction d'un film.")
st.write("Nous avons aussi créé une fonction pour alourdir la valeur des colonnes, afin de donner plus de poids à certaines colonnes lors de l'entraînement du modèle")