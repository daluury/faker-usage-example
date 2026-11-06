"""Work with the PostgreSQL database: connection, schema, loading."""

from pathlib import Path

import pandas as pd
from sqlalchemy import Engine

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def get_engine() -> Engine:
    """Build a SQLAlchemy engine from POSTGRES_* environment variables.

    Hints:
    - call dotenv.load_dotenv() first, otherwise .env is not read outside Jupyter
    - reuse URL.create(...) from the notebook (cell with url_object)
    """
    raise NotImplementedError


def apply_schema(engine: Engine) -> None:
    """Run sql/schema.sql (it is idempotent: CREATE TABLE IF NOT EXISTS).

    Hints:
    - read the file with SCHEMA_FILE.read_text()
    - sqlalchemy.text(...) and engine.begin() (commits automatically)
    """
    raise NotImplementedError


def truncate_tables(engine: Engine) -> None:
    """Empty all three tables so a repeated run does not duplicate data.

    Hints:
    - one statement: TRUNCATE ... RESTART IDENTITY CASCADE
    - list all three tables, order does not matter with CASCADE
    """
    raise NotImplementedError


def load(engine: Engine, tables: dict[str, pd.DataFrame]) -> None:
    """Write DataFrames to the DB: {table_name: dataframe}.

    Hints:
    - parents first (actors, films), then films_actors (foreign keys!)
    - the notebook has a store() helper with df.to_sql(..., if_exists='append')
    - the primary key lives in the DataFrame index, so keep index=True
      (the default): to_sql writes the index as the actor_id / film_id column
    - optional: open one transaction (with engine.begin() as conn) and pass
      con=conn, then a failure in the middle does not leave half-loaded tables
    """
    raise NotImplementedError
