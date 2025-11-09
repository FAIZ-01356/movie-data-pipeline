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
Design Choice	Reason
Normalized schema (movies, genres, movie_genres tables)	Allows storing multiple genres per movie (many-to-many relationship)
Store only average rating instead of storing every user rating	Simplifies stored dataset and matches business need
API enrichment using movie title	movieId does not exist on OMDb, but title matching works
Idempotent loading (DELETE → INSERT)	Ensures re-running ETL does not insert duplicate records
Default values when API returns missing data	Prevents failure of script and ensures consistent data loading

Assumptions:

Movie titles in CSV generally match OMDb titles.

Average rating per movie is enough for analytical queries (raw user rating is not required).

Challenges & How They Were Overcome
Challenge	Solution
Some movies not found in OMDb API	Script logs them and fills blank values with defaults
OMDb API returns "N/A" for numeric fields (e.g., IMDb rating, Box Office) causing conversion errors	Replaced "N/A" with None and then converted safely
Mapping multiple genres from CSV to database schema	Created separate genres table and movie_genres bridge table
Preventing duplicate inserts when script re-runs	Used idempotent delete before insert logic in ETL
