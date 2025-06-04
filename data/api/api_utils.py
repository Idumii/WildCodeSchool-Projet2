# Import des bibliothèques nécessaires
import requests
from datetime import datetime
import pandas as pd
import time

# headers pour l'API de TMDB
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOWYxZmM4MjllODVmZjRiMzg4ZDJiZDYyZTkyZDU2OCIsIm5iZiI6MTc0NzgxMjIxNC4yMTIsInN1YiI6IjY4MmQ3Zjc2OWQwNzg5ZGZiMDhjMTA1NSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.d-Qt3ABIvB3iqZxWBhR5vvkc5cKkOuH9HeYsc2yFaTk"
}


# Récuperer les videos:
# https://api.themoviedb.org/3/movie/{movie_id}/videos?language=fr-FR"

link_ytb = "https://www.youtube.com/watch?v="

def get_movie_videos(movie_id: int):
    """
    Récupère les vidéos associées à un film donné par son ID.
    """
    # URL pour récupérer les vidéos du film
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?language=fr-FR"
    response = requests.get(url, headers=headers)

    # Si on a une réponse, on garde uniquement la premiere vidéo qui correspond à la bande annonce la plus récente
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        for ba in results:
            if ba.get('official') and ba.get('site') == 'YouTube' and ba.get('type') == 'Trailer':
                return link_ytb + ba.get('key')
        #print(f"Aucune bande annonce trouvée pour le film ID {movie_id}.")
    else:
        print(f"Erreur lors de la récupération des vidéos pour le film ID {movie_id}: {response.status_code}")
        return []


# Récuperer des id:
# https://api.themoviedb.org/3/movie/{movie_id}/external_ids

def get_movie_ids(movie_id: int):
    """
    Récupère les IDs externes d'un film spécifique.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/external_ids"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('imdb_id')
    else:
        print(f"Erreur lors de la récupération des IDs externes pour le film {movie_id}: {response.status_code}")
        return None


poster_url = "https://image.tmdb.org/t/p/original/"

def get_movies(page_count: int, primary_release_date_gte: str, primary_release_date_lte: str):
    """
    Récupère les films sortis entre deux dates, en français ou en anglais,
    avec au moins 100 votes, et retourne un DataFrame contenant les résultats
    de plusieurs pages.
    """
    all_movies_data = []  # Liste pour stocker les données de toutes les pages

    for page_number in range(1, page_count + 1):
        # Construire l'URL pour chaque page
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?include_adult=false&include_video=true&language=fr-FR"
            f"&page={page_number}&sort_by=primary_release_date.desc"
            f"&primary_release_date.gte={primary_release_date_gte}"
            f"&primary_release_date.lte={primary_release_date_lte}"
        )

        # Effectuer la requête
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])

            # Filtrer et ajouter les films à la liste
            for movie in movies:
                if movie.get('original_language') in ['fr', 'en'] and movie.get('vote_count') >= 100:
                    all_movies_data.append({
                        'id': movie.get('id'),
                        'poster_path': poster_url + movie.get('poster_path', ''),
                        'video': get_movie_videos(movie.get('id')),
                        'tconst': get_movie_ids(movie.get('id')),
                        'frenchOverview': movie.get('overview', ''),
                    })
        else:
            print(f"Erreur lors de la récupération des données pour la page {page_number}: {response.status_code}")
            break

    # Créer un DataFrame à partir de la liste
    df_movies = pd.DataFrame(all_movies_data)
    return df_movies


def complete_movie_data(imdb_id: str):
    """Récupere l'affiche, la bande annonce et la classification d'un film par son ID.

    Args:
        id (str): tconst du film à récupérer.
    Returns:
        dict: Dictionnaire contenant l'affiche, la bande annonce et la classification du film.
    """
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id&language=fr-FR"
    try:
        time.sleep(0.3)  # Pause pour éviter de surcharger l'API
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['movie_results'][0]:
                poster = data['movie_results'][0].get('poster_path', '')
                return {
                    'id': data['movie_results'][0].get('id'),
                    'poster_path': poster_url + poster if poster else None,
                    'video': get_movie_videos(data['movie_results'][0].get('id')),
                    'frenchOverview': data['movie_results'][0].get('overview', ''),
                }
        else:
            print(f"Pas de données trouvées pour l'ID {imdb_id}. Code d'erreur: {response.status_code}")
            
    except Exception as e:
        print(f"Exception lors de la récupération des données pour l'ID {imdb_id}: {e}")
    # Si aucune donnée n'est trouvée ou en cas d'erreur, retourner un dictionnaire vide    
        return {
            'id': None,
            'poster_path': None,
            'video': None,
            'frenchOverview': None
        }
        