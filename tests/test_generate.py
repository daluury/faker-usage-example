"""Tests for the pure generation functions (no database needed)."""

import datetime

import pandas as pd
import pytest

from src import generate

N_FILMS = 20
N_ACTORS = 60
N_LINKS = 200


@pytest.fixture
def fake():
    return generate.make_faker(seed=1)


@pytest.fixture
def actors(fake):
    return generate.make_actors(fake, N_ACTORS)


@pytest.fixture
def films(fake):
    return generate.make_films(fake, N_FILMS)


def pairs(links: pd.DataFrame) -> pd.DataFrame:
    """(film_id, actor_id) as plain columns, whether they are columns or a MultiIndex."""
    return links.reset_index()[["film_id", "actor_id"]]


def build_all(seed: int):
    fake = generate.make_faker(seed)
    actors = generate.make_actors(fake, N_ACTORS)
    films = generate.make_films(fake, N_FILMS)
    links = generate.make_films_actors(fake, films, actors, N_LINKS)
    return actors, films, links


# ---------- make_faker and GenreProvider


def test_film_genre_is_one_of_genres(fake):
    assert all(fake.film_genre() in generate.GENRES for _ in range(50))


def test_make_faker_works_without_seed():
    fake = generate.make_faker()
    assert fake.film_genre() in generate.GENRES


# ---------- make_actors


def test_actors_columns_and_index(actors):
    assert list(actors.columns) == ["first_name", "last_name"]
    assert len(actors) == N_ACTORS
    assert list(actors.index) == list(range(1, N_ACTORS + 1))
    assert actors.index.name == "actor_id"


def test_actor_names_fit_the_schema(actors):
    assert actors.notna().all().all()
    assert actors["first_name"].str.len().max() <= 45
    assert actors["last_name"].str.len().max() <= 45


# ---------- make_films


def test_films_columns_and_index(films):
    assert list(films.columns) == ["title", "genre", "rating", "release_date"]
    assert len(films) == N_FILMS
    assert list(films.index) == list(range(1, N_FILMS + 1))
    assert films.index.name == "film_id"


def test_films_values_fit_the_schema(films):
    assert films["title"].notna().all()
    assert films["title"].str.len().max() <= 255
    assert films["genre"].isin(generate.GENRES).all()


def test_rating_in_range(films):
    assert films["rating"].between(1.0, 10.0).all()
    # only one decimal place (the DB column is NUMERIC(3, 1))
    assert ((films["rating"].round(1) - films["rating"]).abs() < 1e-9).all()


def test_release_date_is_date(films):
    # exact type check: isinstance would also accept datetime and pandas
    # Timestamp, because they are subclasses of date
    assert all(type(d) is datetime.date for d in films["release_date"])


# ---------- make_films_actors


def test_links_reference_existing_ids(fake, films, actors):
    links = pairs(generate.make_films_actors(fake, films, actors, N_LINKS))
    assert len(links) > 0
    assert links["film_id"].isin(films.index).all()
    assert links["actor_id"].isin(actors.index).all()


def test_links_have_no_duplicates(fake, films, actors):
    links = pairs(generate.make_films_actors(fake, films, actors, N_LINKS))
    assert not links.duplicated().any()


# ---------- reproducibility


def test_seed_makes_runs_reproducible():
    first = build_all(seed=7)
    second = build_all(seed=7)
    for one, two in zip(first, second):
        pd.testing.assert_frame_equal(one, two)


def test_different_seeds_give_different_data():
    first_actors, _, _ = build_all(seed=7)
    other_actors, _, _ = build_all(seed=8)
    assert not first_actors.equals(other_actors)
