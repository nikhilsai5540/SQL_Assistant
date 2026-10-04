import re


BLOCKED_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
]


def validate_sql(sql: str):

    if not sql:
        raise ValueError(
            "Generated SQL is empty."
        )

    query = sql.strip()

    # Remove one final semicolon
    if query.endswith(";"):
        query = query[:-1].strip()

    # Reject multiple SQL statements

    if ";" in query:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    # Block comments

    if "--" in query or "/*" in query:
        raise ValueError(
            "SQL comments are not allowed."
        )

    first_word_match = re.match(
        r"^\s*([A-Za-z]+)",
        query
    )

    if not first_word_match:
        raise ValueError(
            "Unable to understand generated SQL."
        )

    first_word = (
        first_word_match.group(1).upper()
    )

    if first_word not in {
        "SELECT",
        "WITH",
    }:
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    upper_query = query.upper()

    for keyword in BLOCKED_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            upper_query
        ):
            raise ValueError(
                f"Unsafe SQL keyword detected: {keyword}"
            )

    return query