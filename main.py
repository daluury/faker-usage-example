"""Generate fake movies data and load it into PostgreSQL.

Run from the repo root:  python main.py
"""

from src import db, generate

FILMS_COUNT = 100
ACTORS_COUNT = 3 * FILMS_COUNT
SEED = 42


def main() -> None:
    # 1. fake = generate.make_faker(SEED)
    # 2. actors, films, films_actors = ...  (generate.make_*)
    # 3. engine = db.get_engine(); db.apply_schema(engine); db.truncate_tables(engine)
    # 4. db.load(engine, {...}); engine.dispose()
    raise NotImplementedError


if __name__ == "__main__":
    main()
