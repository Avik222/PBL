import os
import json
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from requests_oauthlib import OAuth1Session


# CONFIG
DISCOGS_SITE = "https://www.discogs.com"
DISCOGS_API_BASE = "https://api.discogs.com"

DISCOGS_REQUEST_TOKEN_URL = f"{DISCOGS_API_BASE}/oauth/request_token"
DISCOGS_AUTHORIZE_URL = f"{DISCOGS_SITE}/oauth/authorize"
DISCOGS_ACCESS_TOKEN_URL = f"{DISCOGS_API_BASE}/oauth/access_token"

# Paste the consumer key & secret shown on your Discogs app page.
# IMPORTANT: If you copy/paste into the file, ensure there are NO extra spaces/newlines.
DISCOGS_CONSUMER_KEY = os.environ.get("DISCOGS_CONSUMER_KEY")
DISCOGS_CONSUMER_SECRET = os.environ.get("DISCOGS_CONSUMER_SECRET")
DISCOGS_USER_AGENT = "MelonsVibeRecommender/1.1 +https://example.com"
TOKEN_FILE = "discogs_token.json"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

# =============================================================================
# GENRES & MAPPINGS
GENRE_LIST = [
    "Action", "Comedy", "Drama", "Horror", "Crime", "Romance", "Thriller",
    "Adventure", "Sci-Fi", "Fantasy", "Musical", "Documentary", "Mystery",
    "Animation", "Family", "War", "Western", "Sport", "Biography"
]

EMOTION_TO_IMDB_GENRE_MAP = {g: g.lower() for g in GENRE_LIST}

EMOTION_TO_MUSIC_GENRE_MAP = {
    "Action": "Rock",
    "Comedy": "Pop",
    "Drama": "Blues",
    "Horror": "Metal",
    "Crime": "Hip Hop",
    "Romance": "Jazz",
    "Thriller": "Electronic",
    "Adventure": "Folk, World, & Country",
    "Sci-Fi": "Ambient",
    "Fantasy": "Classical",
    "Musical": "Stage & Screen",
    "Documentary": "Soundtrack",
    "Mystery": "Experimental",
    "Animation": "Children's Music",
    "Family": "Pop",
    "War": "Orchestral",
    "Western": "Country",
    "Sport": "Rap",
    "Biography": "Soundtrack"
}

# =============================================================================
# GEMINI AI (now multi-genre)
# =============================================================================
SYSTEM_PROMPT = (
    "You are a professional mood and media analyst. The user will describe how they feel "
    "or what kind of vibe they want. Analyze their message and output one or more genres "
    f"from this list: {', '.join(GENRE_LIST)}. If multiple genres fit, return several (e.g. ['Action','Drama']). "
    "Return result as a JSON array of strings."
)

def get_vibe_from_text_gemini(user_text):
    payload = {
        "contents": [{"parts": [{"text": user_text}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {"type": "ARRAY", "items": {"type": "STRING"}}
        },
    }
    try:
        r = requests.post(GEMINI_API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=15)
        r.raise_for_status()
        data = r.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return json.loads(text) if text else []
    except Exception as e:
        print(f"[ERROR] Gemini API failed: {e}")
        return []

# =============================================================================
# MOVIES (multi-genre)
def get_movies_for_genres(genres):
    all_movies = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for genre in genres:
        g = EMOTION_TO_IMDB_GENRE_MAP.get(genre)
        if not g:
            continue
        url = f"https://www.imdb.com/search/title/?title_type=feature&genres={g}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")
            links = soup.select("a.ipc-title-link-wrapper")
            titles = []
            for link in links:
                tag = link.find("h3", class_="ipc-title__text")
                if tag:
                    titles.append(tag.get_text(strip=True).split(".", 1)[-1].strip())
            # Avoid duplicates
            for t in titles[:5]:
                if t not in all_movies:
                    all_movies.append(t)
        except Exception as e:
            print(f"[ERROR] IMDb {genre}: {e}")
    return all_movies[:10]

# =============================================================================
# MUSIC (NEEDS MORE ATTENTION AND WORK TO BE DONE)
def get_music_recommendations_discogs(emotion):
    genre = EMOTION_TO_MUSIC_GENRE_MAP.get(emotion)
    if not genre:
        return []

    params = {"genre": genre, "type": "release", "per_page": 10}
    headers = {"User-Agent": DISCOGS_USER_AGENT}
    try:
        qparams = params.copy()
        qparams.update({"key": DISCOGS_CONSUMER_KEY, "secret": DISCOGS_CONSUMER_SECRET})
        r = requests.get(f"{DISCOGS_API_BASE}/database/search", headers=headers, params=qparams, timeout=12)
        data = r.json()
        results = data.get("results", [])
        recs = []
        for entry in results[:5]:
            title = entry.get("title", "Unknown Release")
            if " - " in title:
                artist, album = title.split(" - ", 1)
            else:
                artist, album = "Various Artists", title
            recs.append((album, artist, genre))
        return recs or [("No releases found", "N/A", genre)]
    except Exception as e:
        print(f"[ERROR] Discogs API: {e}")
        return [("API Error", str(e), genre)]

# =============================================================================
# MAIN LOOP
def main():
    print("="*75)
    print(" Melons Multi-Genre Movie & Music Suggester ")
    print("="*75)
    print("Hey GANG Type your vibe, or type 'manual' to pick genres manually.\n")

    while True:
        user_input = input("Describe your vibe (or 'manual' / 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            print("👋 Goodbye! Keep your vibe rolling 🎬")
            break

        # Manual genre selection
        if user_input.lower() == "manual":
            print("Available genres:", ", ".join(GENRE_LIST))
            entered = input("Enter one or more genres separated by commas: ").strip()
            genres = [g.strip().capitalize() for g in entered.split(",") if g.strip().capitalize() in GENRE_LIST]
            if not genres:
                print("❌ No valid genres selected. Try again.")
                continue
        else:
            print("🔍 Analyzing your vibe with Gemini...")
            genres = get_vibe_from_text_gemini(user_input)
            if not genres:
                print("⚠️ AI could not determine your vibe. Try again.")
                continue
            print(f"✅ Gemini suggests: {', '.join(genres)}")

        # Choice: Movies / Music / Both
        while True:
            choice = input("What would you like? (M=Movies, U=Music, B=Both): ").strip().lower()
            if choice in ['m', 'u', 'b']:
                break
            print("❌ Invalid input. Try again.")

        # ---- MOVIES ----
        if choice in ['m', 'b']:
            print("\n🎬 Your movie mix for:", ", ".join(genres))
            print("═"*70)
            movies = get_movies_for_genres(genres)
            if movies:
                for i, movie in enumerate(movies, 1):
                    print(f"{i}. {movie}")
            else:
                print("🚫 No movie results found.")
            print("─"*70)

        # ---- MUSIC ----
        if choice in ['u', 'b']:
            print("\n🎧 Sample music for your vibe")
            print("═"*70)
            if len(genres) > 1:
                emotion = genres[0]
                print(f"(Using primary genre {emotion} for music.)")
            else:
                emotion = genres[0]
            music = get_music_recommendations_discogs(emotion)
            print(tabulate(music, headers=["Release Title", "Artist", "Genre"], tablefmt="fancy_grid"))
            print("─"*70)


if __name__ == "__main__":
    main()
