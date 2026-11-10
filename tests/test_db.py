"""Tests for src/db.py and main.py. Most of them need a running PostgreSQL.

Setup (once):
    docker compose up -d
    docker compose exec db psql -U movies -d movies -c "CREATE DATABASE movies_test;"

Run:
    pytest                         # everything; DB tests are skipped without PostgreSQL
    pytest -m "not integration"    # without the database
    pytest -m integration          # only the database tests

IMPORTANT: these tests delete tables and data. They use the test database
`movies_test` (on the same server), never the working database `movies`.

Scope: the tests check the project code (get_engine, apply_schema, load,
truncate_tables, main), not PostgreSQL itself. Only one schema rule (the
rating CHECK) is tested, as an example. This is on purpose for a small
demo project.
"""

import pandas as pd
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError, OperationalError

import main
from src import db, generate

TABLES = ["actors", "films", "films_actors"]


@pytest.fixture
def engine(monkeypatch):
    """Engine for an EMPTY test database `movies_test` (no tables)."""
    # load_dotenv() does not override variables that are already set,
    # so this value wins over .env
    monkeypatch.setenv("POSTGRES_DB", "movies_test")
    engine = db.get_engine()
    try:
        with engine.connect():
            pass
    except OperationalError:
        engine.dispose()
        pytest.skip(
            "PostgreSQL or database movies_test is not available (see setup above)"
        )
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS films_actors, films, actors CASCADE"))
    yield engine
    engine.dispose()


@pytest.fixture
def tables():
    """Small test data: 10 actors, 5 films, up to 20 film-actor pairs.

    Returned as {table_name: DataFrame} in the order they must be loaded
    (parents first). The sizes are small on purpose: the tests run fast and
    the data is easy to check. Duplicate pairs are dropped, so there can be
    fewer than 20 links.
    """
    fake = generate.make_faker(seed=1)
    actors = generate.make_actors(fake, 10)
    films = generate.make_films(fake, 5)
    links = generate.make_films_actors(fake, films, actors, 20)
    return {"actors": actors, "films": films, "films_actors": links}


def count(engine, table: str) -> int:
    """Number of rows in a table (table names here are constants, not user input)."""
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


def column_names(engine, table: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table)}


# ---------- get_engine (no connection needed)


def test_get_engine_reads_env_without_connecting(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "some_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "some_password")
    monkeypatch.setenv("POSTGRES_HOST", "db.example")
    monkeypatch.setenv("POSTGRES_PORT", "5555")
    monkeypatch.setenv("POSTGRES_DB", "some_db")

    engine = db.get_engine()  # create_engine is lazy: nothing is connected here

    assert engine.url.get_backend_name() == "postgresql"
    assert engine.url.username == "some_user"
    assert engine.url.host == "db.example"
    assert engine.url.port == 5555
    assert engine.url.database == "some_db"


def test_get_engine_reports_missing_variables(monkeypatch):
    # do not let load_dotenv() read the real .env and fill the variables back
    monkeypatch.setattr(db, "load_dotenv", lambda: None)
    for name in db.REQUIRED_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("POSTGRES_DB", "some_db")

    with pytest.raises(RuntimeError) as error:
        db.get_engine()

    message = str(error.value)
    assert "POSTGRES_USER" in message
    # POSTGRES_DB is set, so it must not be in the list of missing ones
    assert "POSTGRES_DB" not in message
    assert ".env.example" in message


# ---------- apply_schema


@pytest.mark.integration
def test_apply_schema_creates_three_tables(engine):
    db.apply_schema(engine)
    assert set(inspect(engine).get_table_names()) == set(TABLES)


@pytest.mark.integration
def test_apply_schema_is_idempotent(engine):
    db.apply_schema(engine)
    db.apply_schema(engine)  # IF NOT EXISTS: the second run must not fail
    assert set(inspect(engine).get_table_names()) == set(TABLES)


# ---------- load


@pytest.mark.integration
def test_load_writes_all_rows(engine, tables):
    db.apply_schema(engine)
    db.load(engine, tables)
    for name, frame in tables.items():
        assert count(engine, name) == len(frame)


@pytest.mark.integration
def test_load_puts_keys_into_id_columns(engine, tables):
    db.apply_schema(engine)
    db.load(engine, tables)
    # The keys (actor_id, film_id) are stored in the DataFrame index. to_sql
    # writes the index as a column with the index name. If the name was lost,
    # the column would be called "index"; with index=False the key would be lost.
    assert column_names(engine, "actors") == {"actor_id", "first_name", "last_name"}
    assert column_names(engine, "films") == {
        "film_id",
        "title",
        "genre",
        "rating",
        "release_date",
    }
    assert column_names(engine, "films_actors") == {"film_id", "actor_id"}


@pytest.mark.integration
def test_load_is_atomic_on_failure(engine, tables):
    """If films_actors is broken, actors and films must not stay half-loaded."""
    db.apply_schema(engine)
    # ids that are not in the loaded films and actors tables
    missing_film = tables["films"].index.max() + 1
    missing_actor = tables["actors"].index.max() + 1
    broken_links = pd.DataFrame(
        {"film_id": [missing_film], "actor_id": [missing_actor]}
    )
    broken = {**tables, "films_actors": broken_links.set_index(["film_id", "actor_id"])}

    # foreign key violation: this film does not exist. Depending on how load()
    # writes the frames, the error is a SQLAlchemy IntegrityError or the same
    # error wrapped by pandas in its own DatabaseError
    with pytest.raises((IntegrityError, pd.errors.DatabaseError)):
        db.load(engine, broken)

    assert count(engine, "actors") == 0
    assert count(engine, "films") == 0


# ---------- truncate_tables


@pytest.mark.integration
def test_truncate_then_load_does_not_duplicate_rows(engine, tables):
    db.apply_schema(engine)
    db.load(engine, tables)

    db.truncate_tables(engine)
    assert [count(engine, name) for name in TABLES] == [0, 0, 0]

    db.load(engine, tables)
    for name, frame in tables.items():
        assert count(engine, name) == len(frame)


# ---------- constraints from sql/schema.sql (one example)


@pytest.mark.integration
def test_rating_check_constraint_rejects_out_of_range(engine):
    db.apply_schema(engine)
    insert = text("INSERT INTO films (film_id, title, rating) VALUES (1, 'x', 11)")
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(insert)


# ---------- main.py end to end


@pytest.mark.integration
def test_main_is_repeatable(engine):
    """Two runs in a row give the same row counts (no duplicates, no errors)."""
    main.main()
    first = {name: count(engine, name) for name in TABLES}

    main.main()
    second = {name: count(engine, name) for name in TABLES}

    assert second == first
    assert first["actors"] == main.ACTORS_COUNT
    assert first["films"] == main.FILMS_COUNT
    assert 0 < first["films_actors"] <= main.LINKS_COUNT
