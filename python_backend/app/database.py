from typing import Any

import psycopg
from psycopg.rows import dict_row

from .config import settings


def query_db(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required to connect to Neon PostgreSQL.")

    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
