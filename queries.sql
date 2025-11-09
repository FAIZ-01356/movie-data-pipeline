-- 1. Which movie has the highest average rating?
select Title, average_rating
from movies
order by average_rating desc, imdbRating desc
limit 1;


-- 2. What are the top 5 movie genres that have the highest average rating? 
select g.genre, avg(m.average_rating) as avg_genre_rating
from movies m
join movie_genres mg on m.movieId = mg.movieId
join genres g on mg.genreId = g.genreId
group by g.genre
order by avg_genre_rating desc
limit 5;


-- 3. Who is the director with the most movies in this dataset?
select Director,count(*) as movie_count
from movies
where Director is not null and Director != 'Unknown' and Director != ''
group by Director
order by movie_count desc
limit 1;


-- 4. What is the average rating of movies released each year?
select Year,avg(average_rating) as avg_rating_per_year
from movies
where Year is not null
group by Year
order by Year;