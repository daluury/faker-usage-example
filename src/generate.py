"""Fake data generation. Pure functions: no DB, no global state."""

import pandas as pd
from faker import Faker
from faker.providers import BaseProvider

GENRES = ["Documentary", "Thriller", "Mystery", "Horror",
          "Action", "Comedy", "Drama", "Romance"]


class GenreProvider(BaseProvider):
    """Custom Faker provider: fake.film_genre()."""

    def film_genre(self) -> str:
        raise NotImplementedError  # hint: self.random_element(GENRES)


def make_faker(seed: int | None = None) -> Faker:
    """Create a Faker with the custom provider added, optionally seeded.

    Hints:
    - fake.seed_instance(seed) makes runs reproducible and, unlike the
      class-level Faker.seed(), keeps the state inside this one object
      (no hidden global state; checked: two Fakers with the same seed
      give identical names and provider values)
    - fake.add_provider(GenreProvider)
    """
    raise NotImplementedError


def make_actors(fake: Faker, n: int) -> pd.DataFrame:
    """DataFrame indexed by actor_id (1..n) with first_name, last_name."""
    raise NotImplementedError


def make_films(fake: Faker, n: int) -> pd.DataFrame:
    """DataFrame indexed by film_id (1..n) with title, genre, rating, release_date.

    Hints:
    - rating in [1.0, 10.0], one decimal; release_date must be a datetime.date
    - take randomness from fake (e.g. fake.pyfloat / fake.random), not from
      the random module, otherwise the seed does not make the run reproducible
    """
    raise NotImplementedError


def make_films_actors(films: pd.DataFrame, actors: pd.DataFrame,
                      n_links: int) -> pd.DataFrame:
    """Pairs (film_id, actor_id) without duplicates, all ids exist in the inputs.

    Hints:
    - see the sample(..., replace=True) and drop_duplicates() cells in the notebook
    """
    raise NotImplementedError
