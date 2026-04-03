import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load .env from the repo root when running locally.
# docker-compose already injects the vars, so this is a safe no-op in prod.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _conn_kwargs() -> dict:
    return dict(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


@contextmanager
def cursor() -> Generator[psycopg2.extras.RealDictCursor, None, None]:
    conn = psycopg2.connect(**_conn_kwargs())
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    finally:
        conn.close()
