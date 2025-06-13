import os
import sys
import streamlit as st

# Vide le film courant à chaque chargement de la page Accueil
if "current_movie" in st.session_state:
    del st.session_state["current_movie"]


# Ajoute le chemin absolu vers le dossier racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from streamlit.components.v1 import html
from data.api.api_utils import *
from streamlit_searchbox import st_searchbox

# Ajoute le chemin absolu vers le dossier racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from machineLearning.ml_utils import pipeline, find_neighbors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_display_path = os.path.join(BASE_DIR, '..', 'ressources', 'df_display.csv')
df_ml_path = os.path.join(BASE_DIR, '..', 'ressources', 'df_ml.csv')

movies_dp = pd.read_csv(df_display_path, sep=';', encoding='utf-8')
movies_ml = pd.read_csv(df_ml_path, sep=';', encoding='utf-8')

st.set_page_config(
    page_title="Accueil",
    page_icon="👋",
)


def search_movies(query: str):
    filtered_movies = movies_dp[movies_dp['frenchTitle'].str.contains(
        query, case=False, na=False)]
    return [
        f"{row['frenchTitle']} ({row['startYear']})"
        for _, row in filtered_movies.iterrows()
    ]

selected_movie = st_searchbox(
    search_movies,
    key="accueil_movie_searchbox",
    placeholder="Rechercher un film..."
)

if selected_movie:
    st.session_state.current_movie = selected_movie
    # Réinitialise la searchbox d'accueil pour éviter la boucle
    del st.session_state["accueil_movie_searchbox"]
    st.switch_page("pages/Film.py")  # ou "Film" selon ta config multipage

# Ici, ne fais rien d'autre avec st.session_state.current_movie
# Affiche toujours la searchbox sur la page accueil

st.sidebar.success("Choisir une page au-dessus.")

# Affichage des dernières sorties de films
recent_movies = get_recent_movies(page_count=1)

if recent_movies:
    st.write("## Films récemment sortis")
    
    # Initialiser l'index de défilement dans la session
    if "movie_start_index" not in st.session_state:
        st.session_state.movie_start_index = 0

    # Nombre de films à afficher par groupe
    movies_per_page = 3
    start_index = st.session_state.movie_start_index
    end_index = start_index + movies_per_page

    # Afficher les films dans une grille de 3 colonnes
    cols = st.columns(3)
    for idx, movie in enumerate(recent_movies[start_index:end_index]):
        col = cols[idx % 3]
        with col:
            if movie.get("poster_path"):
                st.image(movie["poster_path"], width=150)
            st.write(f"**{movie['frenchTitle']}**")

    # Ajouter des boutons pour naviguer entre les groupes de films
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Précédent") and start_index > 0:
            st.session_state.movie_start_index -= movies_per_page
    with col2:
        if st.button("Suivant") and end_index < len(recent_movies):
            st.session_state.movie_start_index += movies_per_page
else:
    st.write("Aucun film récent trouvé.")

st.divider()

# Affichage des films les mieux notés par décennie
st.write("## Films les mieux notés par décennie")
options = [
    "1970", "1980", "1990", "2000", "2010", "2020"
]
selection = st.pills(
    "Sélectionner une décennie",
    options=options,
    selection_mode="single",
    default=options[0],
)


movies_decade = get_top_movies_decade(
    decade=int(selection),
    page_count=1
)


# On va afficher les films dans 5 colonnes
if movies_decade:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if len(movies_decade) > 0:
            if movies_decade[0].get('poster_path'):
                st.image(movies_decade[0]['poster_path'], width=200)
            st.write(
                f"{movies_decade[0]['frenchTitle']} ({movies_decade[0]['startYear']})")

    with col2:
        if len(movies_decade) > 1:
            if movies_decade[1].get('poster_path'):
                st.image(movies_decade[1]['poster_path'], width=200)
            st.write(
                f"{movies_decade[1]['frenchTitle']} ({movies_decade[1]['startYear']})")

    with col3:
        if len(movies_decade) > 2:
            if movies_decade[2].get('poster_path'):
                st.image(movies_decade[2]['poster_path'], width=200)
            st.write(
                f"{movies_decade[2]['frenchTitle']} ({movies_decade[2]['startYear']})")

    with col4:
        if len(movies_decade) > 3:
            if movies_decade[3].get('poster_path'):
                st.image(movies_decade[3]['poster_path'], width=200)
            st.write(
                f"{movies_decade[3]['frenchTitle']} ({movies_decade[3]['startYear']})")

    with col5:
        if len(movies_decade) > 4:
            if movies_decade[4].get('poster_path'):
                st.image(movies_decade[4]['poster_path'], width=200)
            st.write(
                f"{movies_decade[4]['frenchTitle']} ({movies_decade[4]['startYear']})")

else:
    st.write("Aucun film trouvé pour cette décennie.")
