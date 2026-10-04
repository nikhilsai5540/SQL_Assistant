import io
import re
import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "databases"

DATA_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}


def sanitize_identifier(value: str) -> str:
    """
    Convert filenames/sheet names into safe SQLite identifiers.
    """
    value = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())

    if not value:
        value = "data"

    if value[0].isdigit():
        value = f"table_{value}"

    return value.lower()


def get_unique_database_path(name: str) -> Path:
    name = sanitize_identifier(name)

    path = DATA_DIR / f"{name}.db"

    counter = 1

    while path.exists():
        path = DATA_DIR / f"{name}_{counter}.db"
        counter += 1

    return path


def validate_sqlite_database(path: Path) -> bool:
    try:
        connection = sqlite3.connect(path)

        result = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        connection.close()

        return bool(result and result[0].lower() == "ok")

    except sqlite3.Error:
        return False


def save_uploaded_database(filename: str, content: bytes) -> str:
    if not filename:
        raise ValueError("Filename is missing.")

    original_path = Path(filename)

    extension = original_path.suffix.lower()

    database_name = sanitize_identifier(original_path.stem)

    target_path = get_unique_database_path(database_name)

    # -----------------------------------------
    # SQLite database upload
    # -----------------------------------------

    if extension in SQLITE_EXTENSIONS:

        target_path.write_bytes(content)

        if not validate_sqlite_database(target_path):
            target_path.unlink(missing_ok=True)

            raise ValueError(
                "The uploaded file is not a valid SQLite database."
            )

    # -----------------------------------------
    # CSV -> SQLite
    # -----------------------------------------

    elif extension == ".csv":

        try:
            dataframe = pd.read_csv(
                io.BytesIO(content)
            )
        except Exception as error:
            raise ValueError(
                f"Unable to read CSV file: {error}"
            )

        table_name = sanitize_identifier(
            original_path.stem
        )

        connection = sqlite3.connect(target_path)

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

        connection.close()

    # -----------------------------------------
    # Excel -> SQLite
    # -----------------------------------------

    elif extension == ".xlsx":

        try:
            sheets = pd.read_excel(
                io.BytesIO(content),
                sheet_name=None,
            )
        except Exception as error:
            raise ValueError(
                f"Unable to read Excel file: {error}"
            )

        connection = sqlite3.connect(target_path)

        for sheet_name, dataframe in sheets.items():

            table_name = sanitize_identifier(
                sheet_name
            )

            dataframe.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False,
            )

        connection.close()

    else:
        raise ValueError(
            "Only .db, .sqlite, .sqlite3, .csv and .xlsx files are supported."
        )

    return target_path.name


def list_databases():
    databases = []

    for file in sorted(DATA_DIR.glob("*.db")):

        databases.append(
            {
                "name": file.name,
                "size": file.stat().st_size,
            }
        )

    return databases


def get_database_path(database_name: str) -> Path:

    # Prevent directory traversal
    if Path(database_name).name != database_name:
        raise ValueError("Invalid database name.")

    database_path = DATA_DIR / database_name

    if not database_path.exists():
        raise ValueError(
            f"Database '{database_name}' does not exist."
        )

    return database_path