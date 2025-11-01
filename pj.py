import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate
import time  # Added for simulation

# =============================================================================
# CONFIG & CONSTANTS
# =============================================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") # (This looks like a sample key)
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"
MUSIC_DATA_FILE = "dataset.csv"  # Assumes dataset.csv is in the same folder

GENRE_LIST = [
    "Action", "Comedy", "Drama", "Horror", "Crime", "Romance", "Thriller",
    "Adventure", "Sci-Fi", "Fantasy", "Musical", "Documentary", "Mystery",
    "Animation", "Family", "War", "Western", "Sport", "Biography"
]

EMOTION_TO_IMDB_GENRE_MAP = {g: g.lower() for g in GENRE_LIST}

EMOTION_TO_MUSIC_GENRE_MAP = {
    "Action": "rock", "Comedy": "pop", "Drama": "blues", "Horror": "metal",
    "Crime": "hip-hop", "Romance": "jazz", "Thriller": "electronic",
    "Adventure": "folk", "Sci-Fi": "ambient", "Fantasy": "classical",
    "Musical": "soundtrack", "Documentary": "soundtrack", "Mystery": "experimental",
    "Animation": "kids", "Family": "pop", "War": "classical",
    "Western": "country", "Sport": "rap", "Biography": "soundtrack"
}

SYSTEM_PROMPT = (
    "You are a professional mood and media analyst. The user will describe how they feel "
    "or what kind of vibe they want. Analyze their message and output one or more genres "
    f"from this list: {', '.join(GENRE_LIST)}. If multiple genres fit, return several (e.g. ['Action','Drama']). "
    "Return result as a JSON array of strings."
)

# =============================================================================
# [OOP] OBJECT-ORIENTED PROGRAMMING (BCS306)
# =============================================================================

class MediaRecommender:
    """
    [OOP] This is a base "abstract" class.
    It defines a common interface (get_recommendations) that
    all child classes (like MovieRecommender) MUST implement.
    This demonstrates Abstraction and is the base for Inheritance.
    """
    def __init__(self, name):
        self.name = name # Used by the OS Scheduler

    def get_recommendations(self, genres):
        """This method must be overridden by child classes."""
        raise NotImplementedError("Subclass must implement abstract method")

class MovieRecommender(MediaRecommender):
    """
    [OOP] This class INHERITS from MediaRecommender.
    It provides a specific implementation for getting movie data.
    """
    def __init__(self):
        super().__init__("Movie Recommendation Task")

    def get_recommendations(self, genres):
        """
        This is the overridden method.
        It contains the original get_movies_for_genres logic.
        """
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
                
                links = soup.select(".ipc-title-link-wrapper") 
                titles = []
                for link in links:
                    tag = link.find("h3", class_="ipc-title__text") 
                    if tag:
                        title_text = tag.get_text(strip=True).split(".", 1)[-1].strip()
                        titles.append(title_text)
                
                for t in titles[:5]:
                    if t and t not in all_movies:
                        all_movies.append(t)
            except Exception as e:
                print(f"[ERROR] IMDb {genre}: {e}")
                
        return all_movies[:10] # Return a max of 10 movies total

class MusicRecommender(MediaRecommender):
    """
    [OOP] This class also INHERITS from MediaRecommender.
    It provides a specific implementation for getting music data.
    """
    def __init__(self, dataframe):
        super().__init__("Music Recommendation Task")
        self.dataframe = dataframe # Encapsulation: data is held inside the object

    def get_recommendations(self, emotion_genres):
        """
        This is the overridden method.
        It contains the original get_music_from_dataset logic.
        """
        try:
            music_genres = []
            for g in emotion_genres:
                csv_g = EMOTION_TO_MUSIC_GENRE_MAP.get(g)
                if csv_g and csv_g not in music_genres:
                    music_genres.append(csv_g)

            if not music_genres:
                return [("No valid music genres found", "N/A", "N/A")]

            print(f"[Debug] Searching CSV for genres: {music_genres}")
            filtered_df = self.dataframe[self.dataframe['track_genre'].isin(music_genres)]

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
# [OS] OPERATING SYSTEMS (BCS303)
# =============================================================================

class SimpleFCFSScheduler:
    """
    [OS] This class simulates a simple First-Come, First-Served (FCFS) CPU Scheduler.
    It maintains a 'task_queue' (a list acting as a queue).
    Tasks are added to the queue and processed in the order they were received.
    """
    def __init__(self):
        # A list is used as a Queue (FIFO)
        self.task_queue = []

    def add_task(self, task_object, genres):
        """Adds a 'job' to the task queue."""
        job = {
            'task': task_object,
            'genres': genres,
            'type': 'movie' if isinstance(task_object, MovieRecommender) else 'music'
        }
        self.task_queue.append(job)
        print(f"[OS] > Job '{task_object.name}' added to scheduler queue.")

    def run_and_get_results(self):
        """
        Processes the queue using FCFS.
        It 'pop(0)' to get the first item added.
        """
        all_results = {'movie': None, 'music': None}
        print("\n" + "─" * 30)
        print("🤖 [OS SIMULATION: FCFS SCHEDULER]")
        print(f"   Processing {len(self.task_queue)} job(s) in FCFS order...")
        
        while self.task_queue:
            # FCFS: Remove from the front of the queue
            current_job = self.task_queue.pop(0) 
            task = current_job['task']
            
            print(f"\n[OS] > Executing job: '{task.name}'...")
            time.sleep(0.5) # Simulate processing time
            
            # This is where the actual work (get_recommendations) happens
            results = task.get_recommendations(current_job['genres'])
            
            print(f"[OS] > Job '{task.name}' FINISHED.")
            all_results[current_job['type']] = results
        
        print("🤖 [OS SIMULATION COMPLETE]")
        print("─" * 30 + "\n")
        return all_results

# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class VibeRecommenderApp:
    """
    [OOP] This class encapsulates all the application logic.
    It holds the instances of the recommenders and the scheduler.
    """
    def __init__(self):
        self.music_dataframe = self._load_dataset()
        self.movie_recommender = MovieRecommender()
        self.music_recommender = MusicRecommender(self.music_dataframe) if self.music_dataframe is not None else None
        
        # [DS] Build the graph when the app starts
        self._build_genre_graph()

    def _load_dataset(self):
        """Loads the music dataset into memory."""
        print("📀 Loading music dataset (this may take a moment)...")
        try:
            dataframe = pd.read_csv(MUSIC_DATA_FILE)
            dataframe = dataframe.drop(columns=[
                'track_id', 'popularity', 'duration_ms', 'explicit', 'danceability',
                'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'
            ], errors='ignore')
            return dataframe
        except FileNotFoundError:
            print(f"🚨 FATAL ERROR: '{MUSIC_DATA_FILE}' not found!")
            print("Please make sure it is in the same folder as this script.")
            return None
        except Exception as e:
            print(f"🚨 FATAL ERROR: Could not load '{MUSIC_DATA_FILE}': {e}")
            return None

    def _get_vibe_from_gemini(self, user_text):
        """Calls the Gemini API to get genres from user text."""
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

    # =========================================================================
    # [DS] DATA STRUCTURES (BCS304)
    # =========================================================================
    def _build_genre_graph(self):
        """
        [DS] This function builds a Graph (using a dictionary of lists).
        This graph shows relationships between genres.
        It's used to recommend related genres.
        """
        self.genre_graph = {
            "Action": ["Thriller", "Adventure", "Sci-Fi", "War"],
            "Comedy": ["Romance", "Family", "Animation"],
            "Drama": ["Romance", "Crime", "War", "Biography"],
            "Horror": ["Thriller", "Mystery", "Fantasy"],
            "Crime": ["Drama", "Thriller", "Mystery"],
            "Romance": ["Comedy", "Drama", "Musical"],
            "Thriller": ["Horror", "Mystery", "Crime", "Action"],
            "Adventure": ["Action", "Sci-Fi", "Fantasy", "Family"],
            "Sci-Fi": ["Action", "Adventure", "Thriller", "Fantasy"],
            "Fantasy": ["Adventure", "Sci-Fi", "Musical"],
            "Animation": ["Family", "Comedy", "Adventure"],
            "War": ["Drama", "Action", "Biography"],
            "Biography": ["Drama", "War", "Sport"],
        }
        # Ensure all genres are in the graph for safe lookup
        for g in GENRE_LIST:
            if g not in self.genre_graph:
                self.genre_graph[g] = []

    def _get_related_genres(self, genres):
        """
        [DS] This function performs a 1-level traversal of the genre graph
        to find adjacent nodes (related genres).
        """
        related = set()
        for g in genres:
            # Graph traversal: Find all neighbors of the node 'g'
            neighbors = self.genre_graph.get(g, [])
            related.update(neighbors)
        
        # Return up to 3 related genres that weren't in the original list
        return [r for r in related if r not in genres][:3]

    def run(self):
        """The main application loop."""
        print("="*75)
        print(" Melons Multi-Genre Movie & Music Suggester (PBL Integrated Version) ")
        print("="*75)
        
        if self.music_dataframe is None:
            return # Exit if dataset failed to load

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
                genres = self._get_vibe_from_gemini(user_input)
                if not genres:
                    print("⚠️ AI could not determine your vibe. Try again.")
                    continue
            
            print(f"✅ Gemini suggests: {', '.join(genres)}")

            # --- [DS] Graph Feature ---
            related_genres = self._get_related_genres(genres)
            if related_genres:
                print(f"💡 [DS-GRAPH] Based on your vibe, you might also like: {', '.join(related_genres)}")
            # --- End DS Feature ---


            # Choice: Movies / Music / Both
            while True:
                choice = input("What would you like? (M=Movies, U=Music, B=Both): ").strip().lower()
                if choice in ['m', 'u', 'b']:
                    break
                print("❌ Invalid input. Try again.")

            # --- [OS] Scheduler Integration ---
            scheduler = SimpleFCFSScheduler()
            
            # Add tasks to the scheduler's queue
            if choice in ['m', 'b']:
                scheduler.add_task(self.movie_recommender, genres)
            if choice in ['u', 'b'] and self.music_recommender:
                scheduler.add_task(self.music_recommender, genres)
            
            # Run the scheduler to process tasks and get results
            results = scheduler.run_and_get_results()
            # --- End OS Integration ---

            # ---- MOVIES ----
            if results.get('movie'):
                print("\n🎬 Your movie mix for:", ", ".join(genres))
                print("═"*70)
                movies = results['movie']
                if movies:
                    for i, movie in enumerate(movies, 1):
                        print(f"{i}. {movie}")
                else:
                    print("🚫 No movie results found.")
                print("─"*70)

            # ---- MUSIC ----
            if results.get('music'):
                print(f"\n🎧 Your music mix for: {', '.join(genres)}")
                print("═"*70)
                music = results['music']
                print(tabulate(music, headers=["Track", "Artist", "Album"], tablefmt="fancy_grid"))
                print("─"*70)
            
            print("\n" + "="*75 + "\n") # Add separator for next round


if __name__ == "__main__":
    app = VibeRecommenderApp()
    app.run()