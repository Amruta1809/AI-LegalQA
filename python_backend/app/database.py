from __future__ import annotations

import ssl
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

try:
    import psycopg
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    psycopg = None
    dict_row = None

try:
    import pg8000.dbapi as pg8000
except ModuleNotFoundError:
    pg8000 = None

from .config import settings


def _query_with_psycopg(sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    if psycopg is None or dict_row is None:
        raise RuntimeError("psycopg is not available.")

    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def _build_pg8000_connect_args() -> dict[str, Any]:
    parsed = urlparse(settings.database_url)
    query = parse_qs(parsed.query)

    connect_args: dict[str, Any] = {
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "host": parsed.hostname or "",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "timeout": 30,
    }

    if query.get("sslmode", [""])[0] == "require":
        connect_args["ssl_context"] = ssl.create_default_context()

    return connect_args


def _query_with_pg8000(sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    if pg8000 is None:
        raise RuntimeError("pg8000 is not available.")

    conn = pg8000.connect(**_build_pg8000_connect_args())
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            rows = cur.fetchall()
            columns = [column[0] for column in cur.description or []]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cur.close()
    finally:
        conn.close()


def query_db(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required to connect to Neon PostgreSQL.")

    last_error: Exception | None = None

    for query_impl in (_query_with_psycopg, _query_with_pg8000):
        try:
            return query_impl(sql, params)
        except Exception as error:
            last_error = error

    raise RuntimeError(f"Unable to query PostgreSQL: {last_error}") from last_error
