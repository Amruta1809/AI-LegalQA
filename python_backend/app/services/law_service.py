from ..database import query_db


def fetch_laws_from_db(search: str = "") -> list[dict]:
    params: list[str] = []
    sql = """
        SELECT id, act, section, title, content, keywords
        FROM laws
    """

    if search.strip():
        params.append(f"%{search.strip()}%")
        sql += """
            WHERE title ILIKE %s
               OR content ILIKE %s
               OR act ILIKE %s
               OR section ILIKE %s
        """
        params = params * 4

    sql += " ORDER BY act ASC, section ASC"
    return query_db(sql, tuple(params))
