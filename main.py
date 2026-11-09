"""Generate fake movies data and load it into PostgreSQL.

Run from the repo root:  python main.py  (or: uv run python main.py)
"""

from src import db, generate

FILMS_COUNT = 100
ACTORS_COUNT = 3 * FILMS_COUNT
LINKS_COUNT = 10 * FILMS_COUNT  # about 10 actors per film
SEED = 42


def main() -> None:
    fake = generate.make_faker(SEED)
    actors = generate.make_actors(fake, ACTORS_COUNT)
    films = generate.make_films(fake, FILMS_COUNT)
    films_actors = generate.make_films_actors(fake, films, actors, LINKS_COUNT)

    engine = db.get_engine()
    try:
        db.apply_schema(engine)
        db.truncate_tables(engine)
        db.load(
            engine, {"actors": actors, "films": films, "films_actors": films_actors}
        )
        print(
            f"Loaded {len(actors)} actors, {len(films)} films, "
            f"{len(films_actors)} film-actor links"
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
