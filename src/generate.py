"""Fake data generation. Pure functions: no DB, no global state."""

import datetime

import pandas as pd
from faker import Faker
from faker.providers import BaseProvider

GENRES = (
    "Documentary",
    "Thriller",
    "Mystery",
    "Horror",
    "Action",
    "Comedy",
    "Drama",
    "Romance",
)

# fixed range, not "today", so the same seed gives the same data on any day
DATE_FROM = datetime.date(1990, 1, 1)
DATE_TO = datetime.date(2026, 10, 31)


class GenreProvider(BaseProvider):
    """Custom Faker provider: fake.film_genre()."""

    def film_genre(self) -> str:
        return self.random_element(GENRES)


def make_faker(seed: int | None = None) -> Faker:
    """Create a Faker with the custom provider added, optionally seeded."""
    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)
    fake.add_provider(GenreProvider)
    return fake


def make_actors(fake: Faker, n: int) -> pd.DataFrame:
    """DataFrame indexed by actor_id (1..n) with first_name, last_name."""
    actors = pd.DataFrame(index=range(1, n + 1))
    actors.index.name = "actor_id"

    actors["first_name"] = [fake.first_name() for _ in actors.index]
    actors["last_name"] = [fake.last_name() for _ in actors.index]

    return actors


def make_films(fake: Faker, n: int) -> pd.DataFrame:
    """DataFrame indexed by film_id (1..n) with title, genre, rating, release_date."""
    films = pd.DataFrame(index=range(1, n + 1))
    films.index.name = "film_id"

    films["title"] = [
        " ".join(w.capitalize() for w in fake.words(3)) for _ in films.index
    ]
    films["genre"] = [fake.film_genre() for _ in films.index]
    # 1.0 .. 10.0 with one decimal
    films["rating"] = [fake.random.randint(10, 100) / 10 for _ in films.index]
    films["release_date"] = [fake.date_between(DATE_FROM, DATE_TO) for _ in films.index]

    return films


def make_films_actors(
    fake: Faker, films: pd.DataFrame, actors: pd.DataFrame, n_links: int
) -> pd.DataFrame:
    """Random film-actor pairs, indexed by (film_id, actor_id), without duplicates.

    n_links pairs are drawn with repetition and duplicates are then dropped,
    so the result can be shorter than n_links. The index names are used as
    column names when the frame is written to the DB.
    """
    film_ids = list(films.index)
    actor_ids = list(actors.index)

    # use fake.random (not DataFrame.sample), so the seed controls the result
    films_actors = pd.DataFrame(
        {
            "film_id": fake.random.choices(film_ids, k=n_links),
            "actor_id": fake.random.choices(actor_ids, k=n_links),
        }
    )
    films_actors = films_actors.drop_duplicates().set_index(["film_id", "actor_id"])

    return films_actors
