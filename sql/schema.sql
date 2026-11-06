-- Schema of the movies DB.
-- Inspired by https://www.codewars.com/kata/5818bde9559ff58bd90004a2/sql
-- (table names and some types are adapted).
-- Idempotent: safe to run several times.

CREATE TABLE IF NOT EXISTS films (
  film_id INTEGER NOT NULL,
  title CHARACTER VARYING(255) NOT NULL,
  genre CHARACTER VARYING(50),
  rating NUMERIC(3, 1) CHECK (rating BETWEEN 1.0 AND 10.0),
  release_date DATE,
  PRIMARY KEY (film_id)
);

CREATE TABLE IF NOT EXISTS actors (
  actor_id INTEGER NOT NULL,
  first_name CHARACTER VARYING(45) NOT NULL,
  last_name CHARACTER VARYING(45) NOT NULL,
  PRIMARY KEY (actor_id)
);

-- Many-to-many link between films and actors
CREATE TABLE IF NOT EXISTS films_actors (
  actor_id INTEGER NOT NULL,
  film_id INTEGER NOT NULL,
  PRIMARY KEY (actor_id, film_id),
  FOREIGN KEY (actor_id) REFERENCES actors (actor_id),
  FOREIGN KEY (film_id) REFERENCES films (film_id)
);
