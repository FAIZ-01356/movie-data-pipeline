import pandas as pd
import requests
from sqlalchemy import create_engine, text
import re
import time
import numpy as np

# CONFIGURATION
OMDB_API_KEY = "647dc1df"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root$123"
MYSQL_HOST = "localhost"
MYSQL_DB = "movie_pipeline"

engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}", echo=False)

# STEP 1: EXTRACT — Read input files
movies_df = pd.read_csv("movies.csv")
ratings_df = pd.read_csv("ratings.csv")

# Process only first 100 movies
# movies_df = movies_df.head(100)

# Filter ratings only for the selected movies
ratings_df = ratings_df[ratings_df["movieId"].isin(movies_df["movieId"])]

# DATA CLEANING FUNCTIONS
def split_title_year(title):
    """Extract title and year from 'Movie Name (1995)' format."""
    match = re.search(r"^(.*)\s\((\d{4})\)$", title)
    if match:
        return match.group(1), int(match.group(2))
    return title, None


# Clean movies.csv
movies_df["Title"], movies_df["Year"] = zip(*movies_df["title"].map(split_title_year))
movies_df.drop(columns=["title"], inplace=True)
movies_df["genres"] = movies_df["genres"].str.split("|")   # list


# STEP 2: TRANSFORM — Ratings aggregation + feature engineering
# Calculate average rating
ratings_grouped = (
    ratings_df.groupby("movieId")["rating"]
    .mean()
    .reset_index()
    .rename(columns={"rating": "average_rating"})
)

movies_df = movies_df.merge(ratings_grouped, on="movieId", how="left")

# Handle missing values (if no rating exists)
movies_df["average_rating"] = movies_df["average_rating"].fillna(0)

# Feature Engineering → Add decade column
movies_df["decade"] = movies_df["Year"].apply(
    lambda x: f"{str(x)[:3]}0s" if pd.notna(x) else None
)


# STEP 3: EXTRACT — Call OMDb API for enrichment
def fetch_omdb_data(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()

        if data.get("Response") == "False":
            print(f"Not found in API: {title}")
            return {}

        print(f"API fetched: {title}")
        return {
            "Runtime": data.get("Runtime"),
            "Director": data.get("Director"),
            "Writer": data.get("Writer"),
            "Actors": data.get("Actors"),
            "Plot": data.get("Plot"),
            "imdbRating": data.get("imdbRating"),
            "imdbVotes": data.get("imdbVotes"),
            "BoxOffice": data.get("BoxOffice"),
        }
    except Exception as e:
        print(f"Error calling API for {title}: {e}")
        return {}



# API calls (rate limited)
api_results = movies_df.apply(lambda row: fetch_omdb_data(row["Title"]), axis=1)
api_df = pd.DataFrame(api_results.tolist())

movies_df = pd.concat([movies_df, api_df], axis=1)


# STEP 4: CLEAN TRANSFORMED DATA (Correct data types)
# Convert imdbRating to float
movies_df["imdbRating"] = (movies_df["imdbRating"].replace("N/A", None).astype(float))

# Convert BoxOffice from "$123,456,789" to numeric
movies_df["BoxOffice"] = (movies_df["BoxOffice"].replace("N/A", None).replace({'\$': '', ',': ''}, regex=True).astype(float))

# Replace missing values with defaults
movies_df = movies_df.fillna({
    "Runtime": "Not Available",
    "Director": "Unknown",
    "Writer": "Unknown",
    "Actors": "Unknown",
    "Plot": "Not Available",
    "imdbRating": 0,
    "imdbVotes": "0",
    "BoxOffice": 0
})


# STEP 5: LOAD INTO DATABASE (Idempotent)
with engine.begin() as conn:
    print("\n⚙ Clearing existing data (idempotent load)…")
    conn.execute(text("DELETE FROM movie_genres"))
    conn.execute(text("DELETE FROM genres"))
    conn.execute(text("DELETE FROM movies"))

# ---------- Load into movies table ----------
movies_to_insert = movies_df[[
    "movieId", "Title", "Year", "Runtime", "Director", "Writer",
    "Actors", "Plot", "imdbRating", "imdbVotes", "BoxOffice",
    "average_rating", "decade"
]]

movies_to_insert.to_sql("movies", con=engine, if_exists="append", index=False)

# ---------- Load genres + mapping ----------
genres = pd.DataFrame([(genre,) for sublist in movies_df["genres"] for genre in sublist], columns=["genre"])
genres.drop_duplicates(inplace=True)
genres.to_sql("genres", con=engine, if_exists="append", index=False)

# Now fetch genreId for mapping
genres_db = pd.read_sql("SELECT * FROM genres", engine)

movie_genre_map = []
for _, row in movies_df.iterrows():
    for g in row["genres"]:
        genreId = genres_db[genres_db["genre"] == g]["genreId"].values[0]
        movie_genre_map.append((row["movieId"], genreId))

pd.DataFrame(movie_genre_map, columns=["movieId", "genreId"])\
  .to_sql("movie_genres", con=engine, if_exists="append", index=False)

print("\nETL Pipeline completed successfully!")