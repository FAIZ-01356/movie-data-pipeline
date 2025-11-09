-- create database movie_pipeline ;

use movie_pipeline ;

-- DATABASE SCHEMA FOR MOVIE DATA PIPELINE
-- 1. Movies table (from movies.csv + API enrichment later)
CREATE TABLE movies (
    movieId INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Year INT,
    Runtime VARCHAR(50),
    Director VARCHAR(255),
    Writer VARCHAR(255),
    Actors TEXT,
    Plot TEXT,
    imdbRating DECIMAL(3,1),
    imdbVotes VARCHAR(50),
    BoxOffice VARCHAR(50),
    average_rating DECIMAL(3,2) DEFAULT NULL,
    decade VARCHAR(10)
);

-- 2. Genres table (master genre list)
CREATE TABLE genres (
    genreId INT AUTO_INCREMENT PRIMARY KEY,
    genre VARCHAR(100) UNIQUE
);

-- 3. Relationship: Many-to-many => movie ↔ genre
CREATE TABLE movie_genres (
    movieId INT,
    genreId INT,
    PRIMARY KEY (movieId, genreId),
    FOREIGN KEY (movieId) REFERENCES movies(movieId),
    FOREIGN KEY (genreId) REFERENCES genres(genreId)
);