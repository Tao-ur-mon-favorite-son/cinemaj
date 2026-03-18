import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
API_KEY = "549b4711d77c0c64e702bc83d9be1cc7"
MOVIE_BASE_URL = "https://www.themoviedb.org/movie/"
# ---------------------

def get_movie_details(movie_id):
    """Récupère uniquement le réalisateur et les 3 premiers acteurs."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {"api_key": API_KEY, "language": "fr-FR"}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        director = next((m['name'] for m in data.get('crew', []) if m['job'] == 'Director'), "Inconnu")
        actors = [m['name'] for m in data.get('cast', [])[:3]]
        return director, ", ".join(actors)
    except:
        return "Inconnu", "Inconnu"

def get_french_movie_releases():
    """Récupère les films en salles en France (60 jours)."""
    url = "https://api.themoviedb.org/3/discover/movie"
    today = datetime.now()
    params = {
        "api_key": API_KEY,
        "region": "FR",
        "release_date.gte": today.strftime('%Y-%m-%d'),
        "release_date.lte": (today + timedelta(days=60)).strftime('%Y-%m-%d'),
        "with_release_type": "3",
        "language": "fr-FR",
        "sort_by": "popularity.desc"
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])

def create_calendar(movies):
    c = Calendar()
    for movie in movies:
        if not movie.get('release_date'): continue
        
        movie_id = movie['id']
        director, actors = get_movie_details(movie_id)
        
        e = Event()
        e.name = f"🎬 {movie['title']}"
        e.begin = movie['release_date']
        e.make_all_day()
        
        # DESCRIPTION EPURÉE
        e.description = f"🎥 Réalisateur : {director}\n🎭 Acteurs : {actors}"
        
        # LIEN UNIQUE DANS LE CHAMP URL
        e.url = f"{MOVIE_BASE_URL}{movie_id}"
        
        c.events.add(e)
        time.sleep(0.1)
    return c

if __name__ == "__main__":
    print("Génération du calendrier minimaliste...")
    movies = get_french_movie_releases()
    cal = create_calendar(movies)
    
    with open('sorties_cinema_fr.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
        
    print(f"✅ Terminé ! {len(movies)} films ajoutés à 'sorties_cinema_fr.ics'.")
