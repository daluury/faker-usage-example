"""Tests for the pure generation functions (no database needed)."""

import datetime

import pytest

from src import generate


@pytest.fixture
def fake():
    return generate.make_faker(seed=1)


def test_primary_keys_are_unique(fake):
    # TODO: make_actors / make_films -> index.is_unique
    ...


def test_rating_in_range(fake):
    # TODO: all ratings between 1.0 and 10.0
    ...


def test_release_date_is_date(fake):
    # TODO: every release_date is a datetime.date
    ...


def test_links_reference_existing_ids(fake):
    # TODO: every (film_id, actor_id) from make_films_actors exists in the parents
    ...


def test_links_have_no_duplicates(fake):
    # TODO: no repeated pairs
    ...


def test_seed_makes_runs_reproducible():
    # TODO: two Fakers with the same seed produce equal actors
    # (compare names only: release_date depends on today's date)
    ...
