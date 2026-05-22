def filter_and_group_laws(laws: list[dict], search: str = "") -> tuple[dict[str, list[dict]], int]:
    normalized_search = search.strip().lower()

    if normalized_search:
        filtered = []
        for law in laws:
            keywords = law.get("keywords") or []
            haystack = " ".join(
                str(value)
                for value in [law.get("act"), law.get("section"), law.get("title"), law.get("content"), *keywords]
                if value
            ).lower()
            if normalized_search in haystack:
                filtered.append(law)
    else:
        filtered = laws

    grouped: dict[str, list[dict]] = {}
    for law in filtered:
        grouped.setdefault(law["act"], []).append(law)

    return grouped, len(filtered)
