import sqlite3


def make_json_safe(value):

    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool)
    ):
        return value

    if isinstance(value, bytes):
        return value.hex()

    return str(value)


def execute_query(
    database_path,
    sql,
    max_rows=200
):

    database_uri = (
        database_path.resolve().as_uri()
        + "?mode=ro"
    )

    connection = sqlite3.connect(
        database_uri,
        uri=True,
        timeout=5,
    )

    try:

        # Extra SQLite protection
        connection.execute(
            "PRAGMA query_only = ON"
        )

        progress = {
            "count": 0
        }

        def stop_long_query():

            progress["count"] += 1

            if progress["count"] > 100000:
                return 1

            return 0

        connection.set_progress_handler(
            stop_long_query,
            1000
        )

        cursor = connection.execute(sql)

        if cursor.description:

            columns = [
                description[0]
                for description
                in cursor.description
            ]

        else:
            columns = []

        raw_rows = cursor.fetchmany(
            max_rows + 1
        )

        truncated = (
            len(raw_rows) > max_rows
        )

        raw_rows = raw_rows[:max_rows]

        rows = []

        for row in raw_rows:

            rows.append(
                [
                    make_json_safe(value)
                    for value in row
                ]
            )

        return {
            "columns": columns,
            "rows": rows,
            "truncated": truncated,
        }

    except sqlite3.Error as error:

        raise ValueError(
            f"SQL execution failed: {error}"
        )

    finally:

        connection.close()