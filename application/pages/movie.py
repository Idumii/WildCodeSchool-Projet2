import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
import os
import sys

# Ajoute le chemin absolu vers le dossier racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from machineLearning.ml_utils import pipeline, find_neighbors

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

# Vérification de l'existence du fichier df_display.csv
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
    
    
# Barre de recherche avec suggestions dynamiques
st.write("# Rechercher un film 🎬")
# Nettoyage de l'état de la searchbox si besoin
if "movie_searchbox" in st.session_state and st.session_state["movie_searchbox"] is None:
    del st.session_state["movie_searchbox"]

selected_movie = st_searchbox(
    search_movies,
    key="movie_searchbox",
    placeholder="Tapez le titre du film..."
)

# Utiliser session_state pour gérer la navigation
if "current_movie" not in st.session_state:
    st.session_state.current_movie = None

# Si on clique sur une suggestion, on met à jour current_movie et on vide la searchbox
def select_suggestion(movie_label):
    st.session_state.current_movie = movie_label
    if "movie_searchbox" in st.session_state:
        del st.session_state["movie_searchbox"]
    st.rerun()
    # Ce code ne sera pas exécuté après rerun, donc il faut l'ajouter juste après l'appel du bouton

# Si on sélectionne un film dans la searchbox, on l'affiche (sauf si déjà modifié par un bouton)
if selected_movie and st.session_state.current_movie != selected_movie:
    st.session_state.current_movie = selected_movie

if not st.session_state.current_movie:
    st.info("Veuillez sélectionner un film pour afficher ses détails.")
    st.stop()

# Extraire le titre et l'année
titre_clean = st.session_state.current_movie.split(" (")[0]
year_clean = int(st.session_state.current_movie.split(" (")[1].replace(")", ""))
movie = movie_info(titre_clean, year_clean)

if movie:
    st.markdown(f"## 🎬 {movie['frenchTitle']} ({movie['year']})")

    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        if movie['posterUrl']:
            st.image(movie['posterUrl'], width=200)
    
    with col_right:
        note = f"{movie['averageRating']} / 10"
        try:
            minutes = int(movie['runtimeMinutes'])
            hours = minutes // 60
            mins = minutes % 60
            duree = f"{hours}h {mins}min"
        except:
            duree = movie['runtimeMinutes']
        
        genres = ', '.join(movie['genres']) if isinstance(movie['genres'], list) else movie['genres']
        resume = movie['frenchOverview']

        st.markdown(f"**⭐ Note :** {note}")
        st.markdown(f"**⏱️ Durée :** {duree}")
        st.markdown(f"**🎭 Genres :** {genres}")
        st.markdown("**📝 Résumé :**")
        st.write(resume)

    # Acteurs et Réalisateurs
    st.markdown("---")
    st.markdown("### 👥 Acteurs principaux")
    st.write(', '.join(movie['actors']) if isinstance(movie['actors'], list) else movie['actors'])

    st.markdown("### 🎬 Réalisateur(s)")
    st.write(', '.join(movie['directors']) if isinstance(movie['directors'], list) else movie['directors'])

    # Bande-annonce
    st.markdown("---")
    st.markdown("### 🎞️ Bande annonce")
    trailer = movie.get('trailerUrl', '')
    if trailer and isinstance(trailer, str) and trailer.strip():
        try:
            st.video(trailer, autoplay=True, muted=True)
        except Exception as e:
            st.info("Aucune bande annonce disponible pour ce film.")
    else:
        st.info("Aucune bande annonce disponible pour ce film.")

else:
    st.warning("Aucune information disponible pour ce film.")

st.divider()

# Suggestions cliquables
st.write("## 🎥 Films similaires suggérés")
suggestions = movies_suggestions(titre_clean, year_clean)
st.markdown(f"Des films qui pourraient vous plaire si vous aimez **{movie['frenchTitle']}** :")

if suggestions:
    suggestions = suggestions[:9]
    columns_per_row = 3
    rows = (len(suggestions) + columns_per_row - 1) // columns_per_row

    # Assurer l'unicité des suggestions
    seen = set()
    unique_suggestions = []
    for row in suggestions:
        title = row['frenchTitle']
        if title not in seen:
            seen.add(title)
            unique_suggestions.append(row)

    for row_index in range(rows):
        cols = st.columns(columns_per_row)
        for col_index in range(columns_per_row):
            suggestion_index = row_index * columns_per_row + col_index
            if suggestion_index < len(unique_suggestions):
                row = unique_suggestions[suggestion_index]
                poster = None
                try:
                    poster = movies_dp[movies_dp['frenchTitle'] == row['frenchTitle']]['poster_path'].values[0]
                except:
                    pass
                try:
                    year = movies_dp[movies_dp['frenchTitle'] == row['frenchTitle']]['startYear'].values[0]
                except:
                    year = "?"
                with cols[col_index]:
                    image_url = poster if poster else "https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg"
                    st.image(image_url, width=150)
                    movie_label = f"{row['frenchTitle']} ({year})"
                    if st.button(movie_label, key=f"sugg_{row['frenchTitle']}_{year}_{suggestion_index}"):
                        select_suggestion(movie_label)
                        # Ajoute ce script juste après le bouton (il sera exécuté au prochain affichage)
                        st.markdown(
                            """
                            <script>
                            window.scrollTo({top: 0, behavior: "smooth"});
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
                    st.markdown(f"⭐ {row['averageRating']} / 10")
                    genres = ', '.join(row['genres']) if isinstance(row['genres'], list) else row['genres']
                    st.markdown(f"🎭 {genres}")
        if row_index < rows - 1:
            st.markdown(
                "<div style='margin: 20px 0; border-bottom: 1px dotted #111;'></div>",
                unsafe_allow_html=True
            )
else:
    st.info("Aucune suggestion de film similaire disponible.")
