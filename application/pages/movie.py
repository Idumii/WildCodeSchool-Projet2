from machineLearning.ml_utils import pipeline, find_neighbors
import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
import os
import sys

# Ajoute le chemin absolu vers le dossier racine du projet
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df_display_path = os.path.join(BASE_DIR, '../ressources', 'df_display.csv')
df_ml_path = os.path.join(BASE_DIR, '../ressources', 'df_ml.csv')

movies_dp = pd.read_csv(df_display_path, sep=';', encoding='utf-8')
# print(movies_dp.info())
movies_ml = pd.read_csv(df_ml_path, sep=';', encoding='utf-8')

# On récupère la colonne 'startYear' de movies_dp pour l'avoir dans movies_ml, ce qui permettra de gérer les films qui ont exactement le même titre mais des années différentes.
movies_ml = movies_ml.merge(
    movies_dp[['frenchTitle', 'startYear']],
    on='frenchTitle',
    how='left',)



if not os.path.exists(df_display_path):
    raise FileNotFoundError(
        f"Le fichier df_display.csv est introuvable à l'emplacement : {df_display_path}")

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Films",
    page_icon="🎬",
)

st.sidebar.header("Recherche de films")


# Fonction pour récupérer les suggestions dynamiques
def search_movies(query: str):
    filtered_movies = movies_dp[movies_dp['frenchTitle'].str.contains(
        query, case=False, na=False)]
    return [
        f"{row['frenchTitle']} ({row['startYear']})"
        for _, row in filtered_movies.iterrows()
    ]


# Barre de recherche avec suggestions dynamiques
st.write("# Rechercher un film 🎬")
selected_movie = st_searchbox(
    search_movies,
    key="movie_searchbox",
    placeholder="Tapez le titre du film..."
)


def movie_info(titre: str, year: int) -> dict:
    """
    Récuperer les informations d'un film à partir de notre df_display.
    Cette fonction est utilisée pour afficher les informations d'un film spécifique
    dans l'application Streamlit.

    Args:
        titre (str): Titre du film à rechercher.
        year (int): Année de sortie du film.

    Returns:
        dict: Dictionnaire contenant les informations du film.
    """
    filtered_movies_dp = movies_dp[
        (movies_dp['frenchTitle'].str.contains(titre, case=False, na=False)) &
        (movies_dp['startYear'] == year)
    ]
    try:
        if not filtered_movies_dp.empty:
            movie = filtered_movies_dp.iloc[0]
            return {
                'frenchTitle': movie['frenchTitle'],
                'originalTitle': movie['primaryTitle'],
                'year': movie['startYear'],
                'averageRating': movie['averageRating'],
                'runtimeMinutes': movie['runtimeMinutes'],
                'genres': movie['genres'],
                'frenchOverview': movie['frenchOverview'],
                'actors': movie['acteurs'],
                'directors': movie['directors'],
                'posterUrl': movie['poster_path'],
                'trailerUrl': movie['video']
            }
        else:
            return {}
    except Exception as e:
        st.error(f"Erreur lors de la récupération des informations du film : {e}")
        return {}


def movies_suggestions(titre: str, year: int) -> list:
    """
    Récupérer les suggestions de films similaires à partir du DataFrame `movies_ml`.
    Cette fonction exclut le premier film correspondant au titre recherché et retourne une liste de dictionnaires
    contenant les informations des films similaires.

    Args:
        titre (str): Titre du film à rechercher.
        year (int): Année de sortie du film.

    Returns:
        list: Liste de dictionnaires contenant les informations des films similaires.
    """
    try:
        # Filtrer les films dans movies_ml en utilisant les colonnes de movies_ml
        filtered_movies_ml = movies_ml[
            (movies_ml['frenchTitle'].str.contains(titre, case=False, na=False)) &
            (movies_ml['startYear'] == year)
        ]

        if not filtered_movies_ml.empty:
            # Entraîne le pipeline
            pipeline.fit(movies_ml.drop(columns=['frenchTitle', 'startYear']))

            # Trouve les voisins
            neighbors = find_neighbors(movies_ml, pipeline, titre)

            # Vérifiez si `neighbors` est un tuple et extrayez le DataFrame
            if isinstance(neighbors, tuple):
                neighbors = neighbors[0]  # Adaptez selon la structure du tuple

            # Vérifie si des voisins ont été trouvés
            if neighbors is not None and not neighbors.empty:
                suggestions = []
                for _, neighbor in neighbors.iterrows():
                    # Exclure le premier film correspondant au titre recherché
                    if neighbor['frenchTitle'].lower() != titre.lower():
                        movie_info = {
                            'frenchTitle': neighbor['frenchTitle'],
                            'averageRating': neighbor['averageRating'],
                            'genres': neighbor['genres'],
                        }
                        suggestions.append(movie_info)
                return suggestions
            else:
                return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des suggestions de films : {e}")
        return []

# Afficher les informations du film sélectionné
if selected_movie:
    # Extraire le titre et l'année
    titre_clean = selected_movie.split(" (")[0]
    year_clean = int(selected_movie.split(" (")[1].replace(")", ""))
    movie = movie_info(titre_clean, year_clean)
    if movie:
        st.write(f"**Titre en français :** {movie['frenchTitle']}")
        st.write(f"**Titre original :** {movie['originalTitle']}")
        st.write(f"**Année de sortie :** {movie['year']}")
        st.write(f"**Note moyenne :** {movie['averageRating']}")
        st.write(f"**Durée du film :** {movie['runtimeMinutes']} minutes")
        st.write(f"**Genres :** {', '.join(movie['genres']) if isinstance(movie['genres'], list) else movie['genres']}")
        st.write(f"**Résumé :** {movie['frenchOverview']}")
        st.write(f"**Acteurs :** {', '.join(movie['actors']) if isinstance(movie['actors'], list) else movie['actors']}")
        st.write(f"**Réalisateurs :** {', '.join(movie['directors']) if isinstance(movie['directors'], list) else movie['directors']}")
        # Afficher l'affiche et la bande annonce si elles existent       
        if movie['posterUrl']:
            st.image(movie['posterUrl'], caption=movie['frenchTitle'])
        else:
            pass
        
        try:
            
            if movie['trailerUrl']:
                st.write("**Bande annonce :**")
                st.video(movie['trailerUrl'])
            else:
                pass
        except Exception as e:
            st.error(f"Bande annonce non disponible")
    else:
        st.write("Aucune information disponible pour ce film.")

    # Film similaires suggérés
    st.write("### Films similaires suggérés")
    suggestions = movies_suggestions(titre_clean, year_clean)
    st.write(f"Des films qui pourrait vous plaire si vous aimez {movie['frenchTitle']}:")
    if suggestions:
        for row in suggestions:
            st.write(f"**Titre :** {row['frenchTitle']}")
            st.write(f"**Note moyenne :** {row['averageRating']}")
            st.write(
                f"**Genres :** {', '.join(row['genres']) if isinstance(row['genres'], list) else row['genres']}")
            st.write("---")
    else:
        st.write("Aucune suggestion de film similaire disponible.")
