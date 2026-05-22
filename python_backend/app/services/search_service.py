from ..database import query_db
from ..utils.vector import to_vector_literal


def search_laws(query_embedding: list[float], match_count: int = 3) -> list[dict]:
    rows = query_db(
        """
        SELECT content, act, section, similarity
        FROM match_laws(%s::vector, %s::integer)
        """,
        (to_vector_literal(query_embedding), match_count),
    )
    return [law for law in rows if law.get("similarity", 0) >= 0.5]
