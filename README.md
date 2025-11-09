# Movie Data Pipeline

## Overview
This project implements an ETL pipeline to process and store movie data into a relational database.

Extract:
  - Reads movies.csv and ratings.csv using Pandas.
  - Fetches additional movie information (Runtime, Director, Actors, Plot, IMDb rating, Box Office, etc.) from the OMDb API using the movie title.

Transform:
  - Splits the movie title into Title and Year using regex.
  - Calculates the average rating per movie from ratings.csv.
  - Splits genre values into a list and generates a new decade field based on the release year.
  - Cleans data (handles missing values, converts IMDb rating & Box Office to numeric).

Load:
  - Loads final transformed data into MySQL into three tables:
      - movies
      - genres
      - movie_genres (relationship table for mapping movies to genres)
  - ETL script is idempotent — deletes previous data before inserting new data to avoid duplication.

Design Choices & Assumptions

I used a normalized database structure with three tables (movies, genres, movie_genres) because a movie can belong to multiple genres, and storing them in separate tables avoids duplication and makes querying easier.

Instead of storing all user ratings, I only stored the average rating per movie. The raw user ratings were not required for the analysis, so calculating the average helped reduce database size.

Movie metadata (runtime, director, actors, IMDb ratings, etc.) was fetched from the OMDb API using the movie title since the dataset did not contain IMDb IDs.

The ETL script was built to be idempotent — it deletes existing data before inserting new data to avoid duplicates when the script runs multiple times.

When the API does not return complete data or fields, I replaced missing values with default placeholders (e.g., "Unknown", 0, "Not Available").


Challenges & How They Were Overcome

Problem: Some movie titles from CSV were not found in the OMDb API.
Solution: Logged those cases and continued execution with default values.

Problem: API sometimes returned "N/A" for IMDb rating and Box Office, causing type conversion errors.
Solution: Replaced "N/A" with None and converted fields to numeric safely.

Problem: Movies have multiple genres, making it difficult to store directly in a column.
Solution: Created a many-to-many relationship using genres and movie_genres tables.

Problem: Re-running ETL caused duplicate rows.
Solution: Added delete statements before the load phase to make the script idempotent.le genres from CSV to database schema	Created separate genres table and movie_genres bridge table
Preventing duplicate inserts when script re-runs	Used idempotent delete before insert logic in ETL
