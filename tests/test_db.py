"""Integration tests for src/db.py (they need a running PostgreSQL).

TODO: write these together with src/db.py, after generate.py is done.

Setup (once):
    docker compose up -d
    docker compose exec db psql -U movies -d movies -c "CREATE DATABASE movies_test;"

Run only these tests / skip them:
    pytest -m integration
    pytest -m "not integration"

IMPORTANT: db.truncate_tables() wipes data. Never point these tests at the
working database `movies`: always use `movies_test`.

Plan (each test is a stub that is reported as "skipped" until it is written):

1. fixture `engine` (function scope, uses monkeypatch):
   - monkeypatch.setenv("POSTGRES_DB", "movies_test"), then db.get_engine()
     (load_dotenv does not override variables that are already set, so the
     test value wins over .env)
   - try engine.connect(); on sqlalchemy.exc.OperationalError call
     pytest.skip("PostgreSQL is not available") so the suite does not fail
     on a machine without Docker
   - clean state: DROP TABLE IF EXISTS films_actors, films, actors CASCADE,
     then db.apply_schema(engine)
   - yield engine, then engine.dispose()
   Add `engine` as an argument to a test only when the fixture is written,
   otherwise the test errors instead of being skipped.

2. data for the tests: small frames from src.generate
   (make_faker(seed=1), n = 5 films, 10 actors, 20 links), no new generators.

3. useful tools:
   - sqlalchemy.inspect(engine).get_table_names() / .get_columns("films")
   - with engine.connect() as conn: conn.execute(text("SELECT count(*) ...")).scalar_one()
   - with pytest.raises(sqlalchemy.exc.IntegrityError): ...
     (insert inside `with engine.begin() as conn:`, so the failed insert rolls back)
"""

import pytest

pytestmark = pytest.mark.integration


def test_get_engine_reads_env_without_connecting():
    # Not an integration test in spirit (no connection): create_engine is lazy.
    # Hints: monkeypatch.setenv for POSTGRES_USER / POSTGRES_DB / POSTGRES_HOST /
    # POSTGRES_PORT, then check engine.url.database, engine.url.host, engine.url.port.
    # Never print the password: engine.url.render_as_string(hide_password=True).
    pytest.skip("TODO")


def test_apply_schema_creates_three_tables():
    # Hint: inspect(engine).get_table_names() contains actors, films, films_actors
    pytest.skip("TODO")


def test_apply_schema_is_idempotent():
    # Hint: call db.apply_schema(engine) twice; it must not raise (IF NOT EXISTS)
    pytest.skip("TODO")


def test_load_writes_all_rows_and_id_columns():
    # Hints:
    # - row counts in the DB equal len(actors), len(films), len(links)
    # - the primary key must land in the actor_id / film_id columns, not in a
    #   column called "index" (index name in generate.py!): check get_columns(...)
    pytest.skip("TODO")


def test_truncate_then_load_does_not_duplicate_rows():
    # Hint: load, truncate_tables, load again -> the same counts as after the first load
    pytest.skip("TODO")


def test_rating_check_constraint_rejects_out_of_range():
    # Hint: INSERT a film with rating 11 -> IntegrityError (CHECK rating BETWEEN 1.0 AND 10.0)
    pytest.skip("TODO")


def test_foreign_key_rejects_unknown_ids():
    # Hint: INSERT INTO films_actors (actor_id, film_id) with ids that do not exist
    # -> IntegrityError (FOREIGN KEY)
    pytest.skip("TODO")
