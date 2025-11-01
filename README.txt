# 🤖 AI-Integrated Media Recommender

This is a Python-based command-line tool that provides movie and music recommendations based on a user's described vibe or mood. It uses the Google Gemini API to understand natural language input, scrapes IMDb for movie suggestions, and searches a local song dataset for music tracks.

This project also integrates key academic concepts from **Object-Oriented Programming**, **Operating Systems**, and **Data Structures** as part of a university project.

---

## 🌟 Core Features

* 🎭 **AI Vibe Analysis:** Uses the Google Gemini API to translate a user's "vibe" (e.g., "I'm sad and want to think about life") into a list of formal genres (e.g., `["Drama", "Biography"]`).
* 🎬 **Movie Recommendations:** Scrapes IMDb in real time for currently popular movies that match the suggested genres.
* 🎧 **Music Recommendations:** Searches a large local `dataset.csv` to find songs that match the suggested genres.
* 💻 **Manual Mode:** Allows users to bypass the AI and manually input one or more genres.

---

## 🧠 Academic Concepts Demonstrated

This script was built to demonstrate several key computer science concepts:

### 🧩 Object-Oriented Programming (OOP)
* **Inheritance:** Uses a base `MediaRecommender` class, with `MovieRecommender` and `MusicRecommender` as child classes that inherit from it.  
* **Polymorphism:** Both child classes override the `get_recommendations` method with their own specific logic.  
* **Encapsulation:** The `VibeRecommenderApp` class bundles all application logic, and the `MusicRecommender` holds the music dataframe internally.  

### ⚙️ Operating Systems (OS) Simulation
* **CPU Scheduling:** A `SimpleFCFSScheduler` class simulates a First-Come, First-Served (FCFS) scheduler. Recommendation "jobs" (for movies or music) are added to a task queue and executed in the order they were received.  

### 🧮 Data Structures (DS)
* **Graph:** A genre relationship graph (implemented as a dictionary) is used to find and suggest related genres. When you select “Action,” the graph suggests “Thriller” or “Adventure.”  

---

## 🛠️ Setup & Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
* Python 3.7+  
* The `git` command-line tool  

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git
cd YOUR-REPOSITORY-NAME
```

### 3. Set Up Virtual Environment
It's highly recommended to use a virtual environment.

# Create the environment
 python -m venv env

# Activate the environment
# On macOS/Linux:
source env/bin/activate
# On Windows:
.\env\Scripts\activate


### 4. Install Dependencies

pip install -r requirements.txt


### 5. Set Up Your API Key

This project requires a Google Gemini API Key. Get your key from **Google AI Studio**.

Set your API key as an environment variable before running the script:

**On macOS/Linux:**
 bash
 export GEMINI_API_KEY="YOUR_API_KEY_HERE"


**On Windows (Command Prompt):**

set GEMINI_API_KEY="YOUR_API_KEY_HERE"


**On Windows (PowerShell):**

$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"


> 💡 Note: You must do this every time you open a new terminal session, or set it permanently in your system's environment variables.

### 6. Add the Music Dataset
Place a CSV file named `dataset.csv` in the same directory as `pj.py`.

### 7. How to Run
Once setup is complete (environment activated, API key set, `dataset.csv` in place), run:

python pj.py

---
✨ **Enjoy generating vibe-based media recommendations using AI!**
