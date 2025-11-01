import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate

# CONFIG
GEMINI_API_KEY = "AIzaSyAyDBAzE73RUbhOSU3LxNGoKQknpP8GVH4" # (This looks like a sample key)
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"
MUSIC_DATA_FILE = "dataset.csv"  # Assumes dataset.csv is in the same folder

# =============================================================================
# GENRES & MAPPINGS
# =============================================================================
GENRE_LIST = [
    "Action", "Comedy", "Drama", "Horror", "Crime", "Romance", "Thriller",
    "Adventure", "Sci-Fi", "Fantasy", "Musical", "Documentary", "Mystery",
    "Animation", "Family", "War", "Western", "Sport", "Biography"
]

EMOTION_TO_IMDB_GENRE_MAP = {g: g.lower() for g in GENRE_LIST}

EMOTION_TO_MUSIC_GENRE_MAP = {
    "Action": "rock",
    "Comedy": "pop",
    "Drama": "blues",
    "Horror": "metal",
    "Crime": "hip-hop",
    "Romance": "jazz",
    "Thriller": "electronic",
    "Adventure": "folk",
    "Sci-Fi": "ambient",
    "Fantasy": "classical",
    "Musical": "soundtrack",
    "Documentary": "soundtrack",
    "Mystery": "experimental",
    "Animation": "kids",
    "Family": "pop",
    "War": "classical",
    "Western": "country",
    "Sport": "rap",
    "Biography": "soundtrack"
}

# =============================================================================
# GEMINI AI
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
# MOVIES (with corrected URL)
# =============================================================================
def get_movies_for_genres(genres):
    all_movies = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for genre in genres:
        g = EMOTION_TO_IMDB_GENRE_MAP.get(genre)
        if not g:
            continue
        
        # --- CORRECTED URL ---
        url = f"https://www.imdb.com/search/title/?title_type=feature&genres={g}"
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")
            
            links = soup.select(".ipc-title-link-wrapper") 
            titles = []
            for link in links:
                tag = link.find("h3", class_="ipc-title__text") 
                if tag:
                    title_text = tag.get_text(strip=True).split(".", 1)[-1].strip()
                    titles.append(title_text)
            
            # Avoid duplicates and add the top 5
            for t in titles[:5]:
                if t and t not in all_movies:
                    all_movies.append(t)
        except Exception as e:
            print(f"[ERROR] IMDb {genre}: {e}")
            
    return all_movies[:10] # Return a max of 10 movies total

# =============================================================================
# MUSIC (from local CSV)
# =============================================================================
def get_music_from_dataset(emotion_genres, dataframe):
    try:
        music_genres = []
        for g in emotion_genres:
            csv_g = EMOTION_TO_MUSIC_GENRE_MAP.get(g)
            if csv_g and csv_g not in music_genres:
                music_genres.append(csv_g)

        if not music_genres:
            return [("No valid music genres found", "N/A", "N/A")]

        print(f"[Debug] Searching CSV for genres: {music_genres}")
        filtered_df = dataframe[dataframe['track_genre'].isin(music_genres)]

        if filtered_df.empty:
            return [("No songs found in dataset for these genres", "N/A", "N/A")]

        sample_size = min(len(filtered_df), 10)
        random_songs = filtered_df.sample(n=sample_size)

        recs = []
        for _, row in random_songs.iterrows():
            recs.append((row['track_name'], row['artists'], row['album_name']))
        
        return recs

    except Exception as e:
        print(f"[ERROR] Error reading music dataset: {e}")
        return [("Error", str(e), "N/A")]

# =============================================================================
# MAIN LOOP (Terminal-based)
# =============================================================================
def main():
    print("="*75)
    print(" Melons Multi-Genre Movie & Music Suggester ")
    print("="*75)

    # --- Load the dataset into memory ---
    print("📀 Loading music dataset (this may take a moment)...")
    try:
        music_dataframe = pd.read_csv(MUSIC_DATA_FILE)
        # Drop columns we won't use to save memory
        music_dataframe = music_dataframe.drop(columns=[
            'track_id', 'popularity', 'duration_ms', 'explicit', 'danceability',
            'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
            'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'
        ], errors='ignore')
    except FileNotFoundError:
        print(f"🚨 FATAL ERROR: '{MUSIC_DATA_FILE}' not found!")
        print("Please make sure it is in the same folder as this script.")
        return # Exit the function
    except Exception as e:
        print(f"🚨 FATAL ERROR: Could not load '{MUSIC_DATA_FILE}': {e}")
        return # Exit the function
        
    print("✅ Dataset loaded! Ready to find your vibe.")
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
            print(f"\n🎧 Your music mix for: {', '.join(genres)}")
            print("═"*70)
            
            music = get_music_from_dataset(genres, music_dataframe)
            
            print(tabulate(music, headers=["Track", "Artist", "Album"], tablefmt="fancy_grid"))
            print("─"*70)
        
        print("\n" + "="*75 + "\n") # Add separator for next round


if __name__ == "__main__":
    main()