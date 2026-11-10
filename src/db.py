"""Work with the PostgreSQL database: connection, schema, loading."""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, Engine, create_engine, text

# path to sql/schema.sql, built from this file, so it works from any folder
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

REQUIRED_ENV_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
]


def get_engine() -> Engine:
    """Build a SQLAlchemy engine from POSTGRES_* environment variables.

    It does not connect yet: the connection opens on the first query.
    Raises RuntimeError if some of the variables are not set.
    """
    load_dotenv()
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill it in."
        )
    url = URL.create(
        "postgresql",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
    )
    return create_engine(url)


def apply_schema(engine: Engine) -> None:
    """Run sql/schema.sql (it is idempotent: CREATE TABLE IF NOT EXISTS)."""
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_FILE.read_text(encoding="utf-8")))


def truncate_tables(engine: Engine) -> None:
    """Empty all three tables so a repeated run does not duplicate data."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE actors, films, films_actors"))


def load(engine: Engine, tables: dict[str, pd.DataFrame]) -> None:
    """Write DataFrames to the DB: {table_name: dataframe}.

    Tables are loaded in the given order, so put parent tables first
    (actors, films, then films_actors). The DataFrame index is written too:
    it holds the primary key. Everything is saved in one transaction, so if
    one table fails, nothing is saved.
    """
    with engine.begin() as conn:
        for table_name, frame in tables.items():
            frame.to_sql(table_name, con=conn, if_exists="append")
