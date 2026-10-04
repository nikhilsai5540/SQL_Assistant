import sqlite3
from pathlib import Path


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def get_table_names(connection):
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """

    rows = connection.execute(query).fetchall()

    return [row[0] for row in rows]


def get_database_schema(database_path: Path):

    connection = sqlite3.connect(database_path)

    tables = []

    try:

        table_names = get_table_names(connection)

        for table_name in table_names:

            escaped_table = table_name.replace('"', '""')

            column_rows = connection.execute(
                f'PRAGMA table_info("{escaped_table}")'
            ).fetchall()

            columns = []

            for column in column_rows:

                columns.append(
                    {
                        "name": column[1],
                        "type": column[2] or "TEXT",
                        "not_null": bool(column[3]),
                        "default": column[4],
                        "primary_key": bool(column[5]),
                    }
                )

            foreign_key_rows = connection.execute(
                f'PRAGMA foreign_key_list("{escaped_table}")'
            ).fetchall()

            foreign_keys = []

            for foreign_key in foreign_key_rows:

                foreign_keys.append(
                    {
                        "column": foreign_key[3],
                        "references_table": foreign_key[2],
                        "references_column": foreign_key[4],
                    }
                )

            tables.append(
                {
                    "name": table_name,
                    "columns": columns,
                    "foreign_keys": foreign_keys,
                }
            )

    finally:
        connection.close()

    return tables


def get_schema_documents(database_path: Path):
    """
    Converts every table schema into a text document.

    These documents are embedded by Ollama and used
    for RAG retrieval.
    """

    connection = sqlite3.connect(database_path)

    documents = []

    try:

        tables = get_database_schema(database_path)

        for table in tables:

            table_name = table["name"]

            parts = [
                f"Table name: {table_name}",
                "Columns:",
            ]

            for column in table["columns"]:

                text = (
                    f'- "{column["name"]}" '
                    f'{column["type"]}'
                )

                if column["primary_key"]:
                    text += " PRIMARY KEY"

                if column["not_null"]:
                    text += " NOT NULL"

                parts.append(text)

            if table["foreign_keys"]:

                parts.append("Relationships:")

                for fk in table["foreign_keys"]:

                    parts.append(
                        f"- {table_name}.{fk['column']} "
                        f"references "
                        f"{fk['references_table']}."
                        f"{fk['references_column']}"
                    )

            # ----------------------------------
            # Add a few sample values
            # ----------------------------------

            try:

                quoted_table = quote_identifier(
                    table_name
                )

                cursor = connection.execute(
                    f"SELECT * FROM {quoted_table} LIMIT 3"
                )

                rows = cursor.fetchall()

                column_names = [
                    description[0]
                    for description in cursor.description
                ]

                if rows:

                    parts.append("Sample values:")

                    for row in rows:

                        values = []

                        for index, value in enumerate(row):

                            safe_value = str(value)

                            if len(safe_value) > 50:
                                safe_value = safe_value[:50]

                            values.append(
                                f"{column_names[index]}={safe_value}"
                            )

                        parts.append(
                            "- " + ", ".join(values)
                        )

            except sqlite3.Error:
                pass

            documents.append(
                {
                    "table": table_name,
                    "text": "\n".join(parts),
                }
            )

    finally:
        connection.close()

    return documents