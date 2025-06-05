import pandas as pd
from datetime import datetime
import sys
import os
from api_utils import get_movies, get_movie_details

# Liens vers les fichiers de données IMDb
link_title_basics = "https://datasets.imdbws.com/title.basics.tsv.gz"
link_title_akas = "https://datasets.imdbws.com/title.akas.tsv.gz"
link_title_crew = "https://datasets.imdbws.com/title.crew.tsv.gz"
link_title_principals = "https://datasets.imdbws.com/title.principals.tsv.gz"
link_title_ratings = "https://datasets.imdbws.com/title.ratings.tsv.gz"
link_name_basics = "https://datasets.imdbws.com/name.basics.tsv.gz"
output_tmdb = "../ressources/tmdb_movies.csv"

# Chargement des datasets
df_name_basics = pd.read_csv(link_name_basics, sep="\t", low_memory=False)
df_title_principals = pd.read_csv(link_title_principals, sep="\t", low_memory=False)
df_title_crew = pd.read_csv(link_title_crew, sep="\t", low_memory=False)
df_title_akas = pd.read_csv(link_title_akas, sep="\t", low_memory=False)
df_title_ratings = pd.read_csv(link_title_ratings, sep="\t", low_memory=False)
df_tmdb = pd.read_csv(output_tmdb, low_memory=False)
df_title_basics = pd.read_csv(link_title_basics, sep="\t", low_memory=False)

# Nettoyage des genres
df_title_basics["genres"] = df_title_basics["genres"].str.replace("\\N", "Unknown", regex=False)
df_title_basics["genres"] = df_title_basics["genres"].fillna("Unknown")
list_genre_to_drop = ["Documentary", "Short", "News", "Talk-show", "Game-Show", "Reality-TV", "Adult"]
regex_pattern = '|'.join(map(lambda x: f'({x})', list_genre_to_drop))
df_title_basics = df_title_basics[~df_title_basics['genres'].str.contains(regex_pattern, regex=True)]

# Filtrage des films
df_title_basics = df_title_basics[df_title_basics['titleType'] == 'movie']
df_title_basics = df_title_basics[df_title_basics['isAdult'] == '0']
df_title_basics['primaryTitle'] = df_title_basics['primaryTitle'].fillna('None.')

# Jointure avec TMDB
df_merged = pd.merge(df_title_basics, df_tmdb, left_on='tconst', right_on='imdb_id', how='left')
df_merged = df_merged.drop(columns=['isAdult', 'originalTitle', 'endYear', 'adult', 'budget', 'homepage', 'imdb_id', 'original_title', 'titleType', 'runtime'], errors='ignore')

# Conversion des types
df_merged['runtimeMinutes'] = pd.to_numeric(df_merged['runtimeMinutes'], errors='coerce', downcast='signed').astype('Int64')  
df_merged['id'] = pd.to_numeric(df_merged['id'], errors='coerce', downcast='integer').astype('Int64')  
df_merged['popularity'] = pd.to_numeric(df_merged['popularity'], errors='coerce', downcast='signed')
df_merged['revenue'] = pd.to_numeric(df_merged['revenue'], errors='coerce', downcast='signed')
df_merged['vote_average'] = pd.to_numeric(df_merged['vote_average'], errors='coerce', downcast='signed')
df_merged['vote_count'] = pd.to_numeric(df_merged['vote_count'], errors='coerce', downcast='signed').astype('Int64')
df_title_basics['startYear'] = pd.to_numeric(df_title_basics['startYear'], errors='coerce', downcast='signed').astype('Int64')
df_merged['startYear'] = pd.to_datetime(df_merged['startYear'], format='%Y', errors='coerce').dt.to_period('Y')
df_merged['release_date'] = pd.to_datetime(df_merged['release_date'], format='%Y-%m-%d', errors='coerce').dt.date

# Filtrage des pays de production
df_filtered = df_merged[df_merged['production_countries'].str.contains('USA|GB|FR|US', na=False)]

# Réorganisation et renommage des colonnes
df_filtered = df_filtered[['tconst', 'primaryTitle', 'title', 'startYear', 'release_date', 'genres_x', 'genres_y', 'production_countries', 'runtimeMinutes', 'vote_average', 'vote_count', 'popularity', 'revenue', 'tagline', 'overview', 'id']]
df_filtered = df_filtered.rename(columns={'genres_x': 'genres_df_title_basics', 'genres_y': 'genres_df_tmdb'})

# Nettoyage des titres français
df_title_akas_clean = df_title_akas.drop(columns=['ordering', 'language', 'types', 'attributes', 'isOriginalTitle'], errors='ignore')
df_title_akas_clean = df_title_akas_clean[df_title_akas_clean['region'] == 'FR']
df_title_akas_clean = df_title_akas_clean.rename(columns={'title': 'frenchTitle'})

# Jointure pour les titres français
df_filtered_french_title = pd.merge(df_filtered, df_title_akas_clean, left_on='tconst', right_on='titleId', how='left')
df_filtered_french_title = df_filtered_french_title.drop(columns=['titleId', 'region'], errors='ignore')
df_filtered_french_title['frenchTitle'] = df_filtered_french_title['frenchTitle'].fillna(df_filtered_french_title['primaryTitle'])
df_filtered_french_title['genres_df_tmdb'] = df_filtered_french_title['genres_df_tmdb'].apply(lambda x: str(x).replace('[','').replace(']','').replace('\'', '').replace(' ',''))
df_filtered_french_title['production_countries'] = df_filtered_french_title['production_countries'].apply(lambda x: str(x).replace('[','').replace(']','').replace('\'', '').replace(' ',''))
df_filtered_french_title['genres'] = df_filtered_french_title.apply(lambda x: ', '.join(set(str(x['genres_df_title_basics']).split(',') + str(x['genres_df_tmdb']).split(','))), axis=1)
df_filtered_french_title = df_filtered_french_title.drop(columns=['genres_df_title_basics', 'genres_df_tmdb'], errors='ignore')
df_filtered_french_title = df_filtered_french_title[['tconst', 'primaryTitle', 'title', 'frenchTitle','startYear', 'genres', 'production_countries', 'runtimeMinutes', 'vote_average', 'vote_count', 'popularity', 'revenue', 'tagline', 'overview', 'id']]

# Jointure avec les ratings
df_title_ratings['numVotes'] = pd.to_numeric(df_title_ratings['numVotes'], errors='coerce', downcast='signed').astype('Int64')
df_filtered_ratings = pd.merge(df_filtered_french_title, df_title_ratings, on='tconst', how='left')
df_filtered_ratings = df_filtered_ratings.drop(columns=['vote_average', 'vote_count', 'popularity'], errors='ignore')
df_filtered_ratings['numVotes'] = df_filtered_ratings['numVotes'].astype('Int64')
df_filtered_ratings = df_filtered_ratings[df_filtered_ratings['averageRating'].notna()]
df_filtered_ratings = df_filtered_ratings[~((df_filtered_ratings['startYear'].dt.year < 1990) & (df_filtered_ratings['averageRating'] < 7))]
df_filtered_ratings = df_filtered_ratings[~(df_filtered_ratings['numVotes'] < 1500)]
df_filtered_ratings = df_filtered_ratings[(df_filtered_ratings['runtimeMinutes'] > 60) & (df_filtered_ratings['runtimeMinutes'] < 250)]

# Suppression des doublons
df_filtered_ratings = df_filtered_ratings.drop_duplicates(subset=['tconst'])

# Acteurs principaux
df_cast = df_title_principals.merge(df_name_basics[['nconst', 'primaryName']], on='nconst', how='left')
df_cast = df_cast.sort_values(by=['tconst', 'ordering'])
df_cast = df_cast.drop_duplicates(subset=['tconst', 'nconst'])
df_cast = df_cast.groupby('tconst').head(3)
df_cast = df_cast[['tconst', 'primaryName']]
df_cast['actor_num'] = df_cast.groupby('tconst').cumcount() + 1
df_cast_pivot = df_cast.pivot(index='tconst', columns='actor_num', values='primaryName')
df_cast_pivot.columns = [f'actor{i}' for i in df_cast_pivot.columns]
df_cast_pivot = df_cast_pivot.reset_index()

# Fusion acteurs
df_actors = pd.merge(df_filtered_ratings, df_cast_pivot, on='tconst', how='left')

# Réalisateurs
df_directors = df_title_crew[['tconst', 'directors']].copy()
df_directors['directors'] = df_directors['directors'].str.split(',')
df_directors = df_directors.explode('directors')
df_directors = df_directors.merge(df_name_basics[['nconst', 'primaryName']], left_on='directors', right_on='nconst', how='left')
df_directors['primaryName'] = df_directors['primaryName'].fillna('Unknown')
df_directors = df_directors.groupby('tconst').head(2)
df_directors_final = df_directors[['tconst', 'primaryName']].drop_duplicates()
df_directors_final = df_directors_final.groupby('tconst')['primaryName'].apply(lambda x: ', '.join(x)).reset_index()
df_directors_final = df_directors_final.rename(columns={'primaryName': 'directors'})

# Fusion finale
df_final = pd.merge(df_actors, df_directors_final, on='tconst', how='left')

# Export
df_final.to_csv('../ressources/df_nettoyage_principal.csv', index=False, sep=';')