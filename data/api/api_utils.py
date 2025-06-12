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

# Fonction qui va récuperer les films en fonction de la date de sortie et du nombre de votes
def get_movies(page_count: int, primary_release_date_gte: str, primary_release_date_lte: str):
    all_movies_data = []
    for page_number in range(1, page_count + 1):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?include_adult=false&include_video=true&language=fr-FR"
            f"&page={page_number}&sort_by=vote_count.desc"
            f"&primary_release_date.gte={primary_release_date_gte}"
            f"&primary_release_date.lte={primary_release_date_lte}"
        )
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])
            for movie in movies:
                if movie.get('original_language') in ['fr', 'en'] and movie.get('vote_count', 0) >= 500:
                    all_movies_data.append(movie.get('id'))
        else:
            print(f"Erreur lors de la récupération des données pour la page {page_number}: {response.status_code}")
            break
    return all_movies_data


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
        
        
        
# Récuperer les details des films pour notre df de ML et Display
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=fr-FR&append_to_response=videos,credits"
    response = requests.get(url, headers=headers)
    time.sleep(0.25)  # Respect du rate limit
    if response.status_code == 200:
        data = response.json()
        # Récupération des réalisateurs
        directors = [crew['name'] for crew in data.get('credits', {}).get('crew', []) if crew.get('job') == 'Director']
        # Récupération des 3 premiers acteurs
        actors = [cast['name'] for cast in data.get('credits', {}).get('cast', [])][:3]
        # Récupération de la bande-annonce (YouTube)
        video = None
        for v in data.get('videos', {}).get('results', []):
            if v.get('type') == 'Trailer' and v.get('site') == 'YouTube':
                video = f"https://www.youtube.com/watch?v={v.get('key')}"
                break
        # Récupération des genres
        genres = [g['name'] for g in data.get('genres', [])]
        return {
            'frenchTitle': data.get('title'),
            'primaryTitle': data.get('original_title'),
            'averageRating': data.get('vote_average'),
            'numVotes': data.get('vote_count'),
            'runtimeMinutes': data.get('runtime'),
            'genres': ', '.join(genres),
            'startYear': int(data.get('release_date', '0000')[:4]) if data.get('release_date') else None,
            'overview': data.get('overview'),
            'directors': ', '.join(directors),
            'acteurs': ', '.join(actors),
            'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
            'video': video,
            'frenchOverview': data.get('overview'),  # ou autre champ si tu veux une version différente
        }
    else:
        print(f"Erreur détails film ID {movie_id} : code {response.status_code}")
        return None
    
    
# Récupere les films les mieux notés d'une décennie spécifique    
def get_top_movies_decade(decade: int, page_count: int = 1):
    """
    Récupère les 5 films les mieux notés d'une décennie spécifique.
    
    Args:
        decade (int): La décennie à rechercher (ex: 1990, 2000).
        page_count (int): Nombre de pages à récupérer. Par défaut 1 car on trie par note et on limite à 5 films.
        
    Returns:
        list: Liste des films avec leurs détails.
    """
    primary_release_date_gte = f"{decade}-01-01"
    primary_release_date_lte = f"{decade + 10}-01-01"
    print(f"Récupération des films pour la décennie {decade} de {primary_release_date_gte} à {primary_release_date_lte}")
    url = (
        f"https://api.themoviedb.org/3/discover/movie"
        f"?include_adult=false&include_video=false&language=fr-FR"
        f"&sort_by=vote_average.desc&vote_count.gte=500"
        f"&primary_release_date.gte={primary_release_date_gte}"
        f"&primary_release_date.lte={primary_release_date_lte}"
        f"&page=1"
    )
    
    response = requests.get(url, headers=headers)
    movies_details = []  
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])
        
        for movie in movies[:5]:
            movies_details.append({
                'frenchTitle': movie.get('title', 'Titre inconnu'),
                'startYear': int(movie.get('release_date', '0000')[:4]) if movie.get('release_date') else 'Année inconnue',
                'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None,
            })
    else:
        print(f"Erreur lors de la récupération des films pour la décennie {decade}: {response.status_code}")
    
    return movies_details
