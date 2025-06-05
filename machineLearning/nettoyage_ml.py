import pandas as pd
import os
from datetime import datetime
import sys

# Ajoute le chemin absolu vers le dossier contenant api_utils.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/api')))
from api_utils import get_movies, get_movie_details

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'ressources', 'df_final.csv')
# Chargement du dataset principal
df = pd.read_csv(DATA_PATH, sep=';', index_col=0)

# Ajout de la colonne decade
df['decade'] = (df['startYear'] // 10) * 10

# Concaténation des colonnes actors
def concat_actors(row):
    return [row['actor1'], row['actor2'], row['actor3']]
if all(col in df.columns for col in ['actor1', 'actor2', 'actor3']):
    df['actors'] = df.apply(concat_actors, axis=1)
    df = df.drop(columns=['actor1', 'actor2', 'actor3'])

# Suppression des colonnes inutiles
cols_to_drop = ['primaryTitle', 'title', 'production_countries', 'runtimeMinutes', 'revenue', 'tagline', 'overview', 'id', 'startYear']
df_clean = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

# Récupération des films manquants via l'API TMDB (2024/2025)
primary_release_date_gte = "2024-01-01"
primary_release_date_lte = datetime.now().strftime("%Y-%m-%d")
results = get_movies(page_count=500, primary_release_date_gte=primary_release_date_gte, primary_release_date_lte=primary_release_date_lte)

details_movie = []
for id in results:
    movie_details = get_movie_details(id)
    if movie_details:
        actors = movie_details.get('acteurs', '').split(', ')
        movie_details['actors'] = actors[:3]
        # Ajoute la colonne decade directement si startYear existe
        if 'startYear' in movie_details and movie_details['startYear']:
            try:
                movie_details['decade'] = (int(movie_details['startYear']) // 10) * 10
            except Exception:
                movie_details['decade'] = None
        else:
            movie_details['decade'] = None
        details_movie.append(movie_details)

df_movies = pd.DataFrame(details_movie)

# Sélectionne et renomme les colonnes pour correspondre à df_clean
columns_ml = [
    'frenchTitle', 'genres', 'averageRating', 'numVotes',
    'actors', 'directors', 'decade'
]
df_movies['decade'] = df_movies['startYear'].apply(lambda x: (int(x) // 10) * 10 if pd.notnull(x) else None)

df_movies = df_movies[columns_ml]

# Concaténation des nouveaux films au DataFrame principal
df_final = pd.concat([df_clean, df_movies], ignore_index=True, sort=False)
OUTPUT_PATH = os.path.join(BASE_DIR, 'ressources', 'df_ml.csv')
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df_final.to_csv(OUTPUT_PATH, sep=';', index=False)

