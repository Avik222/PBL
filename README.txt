# 🎬 Vibe-Based Movie & Music Suggester

This is a Python-based command-line tool that provides movie and music recommendations based on a user's described vibe or mood.

It uses the Gemini API to understand natural language input, scrapes IMDb for movie suggestions, and searches a local song dataset for music tracks.

## ✨ Features

* **Vibe Analysis:** Uses the Google Gemini API to translate a user's "vibe" (e.g., "I'm sad and want to think about life") into a list of formal genres (e.g., `["Drama", "Biography"]`).
* **Movie Recommendations:** Scrapes IMDb in real-time for currently popular movies that match the suggested genres.
* **Music Recommendations:** Searches a large local `dataset.csv` to find songs that match the suggested genres.
* **Manual Mode:** Allows users to bypass the AI and manually input one or more genres.
* **Combined Output:** Can provide movies, music, or both in one query.

---

## 🚀 How It Works

1.  The user is prompted to describe their vibe or choose 'manual' mode.
2.  **AI Mode:** The text is sent to the **Gemini API**, which returns a JSON array of genres (e.g., `["Action", "Thriller"]`).
3.  **For Movies:** The script scrapes `imdb.com` for the top movies listed under the "Action" and "Thriller" genres.
4.  **For Music:** The script maps the genres (e.g., "Action" -> "rock") and searches the `dataset.csv` for 10 random songs with that genre.
5.  The results are formatted and printed to the terminal.

---

## 🔧 Setup & Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

* Python 3.7+
* The `git` command-line tool

### 2. Clone the Repository

Open your terminal and run the following command to clone the project:
git clone [https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git)
cd YOUR-REPOSITORY-NAME

### 3. Set Up Virtual Environment
It's highly recommended to use a virtual environment.

		# Create the environment
		python -m venv env2

		# Activate the environment
		# On macOS/Linux:
		source env2/bin/activate
		# On Windows:
		.\env2\Scripts\activate

### 4. Install Dependencies
Install all the required Python packages from the requirements.txt file.
		pip install -r requirements.txt

### 5. Set Up Your API Key
This project requires a Google Gemini API Key.

Get your key from Google AI Studio.

### 6. Add the Music Dataset
This script requires a CSV file named dataset.csv to be in the same folder as pj.py.

### 7. How to Run
Once your setup is complete (environment activated, API key set, dataset.csv in place), run the script from your terminal:
python pj.py