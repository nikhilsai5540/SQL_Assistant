import sqlite3

from database import DATA_DIR


database_path = (
    DATA_DIR / "college.db"
)


connection = sqlite3.connect(
    database_path
)

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT NOT NULL,
    year INTEGER NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    subject TEXT,
    marks REAL,
    FOREIGN KEY(student_id)
    REFERENCES students(id)
)
""")


cursor.execute(
    "DELETE FROM marks"
)

cursor.execute(
    "DELETE FROM students"
)


students = [
    (1, "Nikhil", "IoT", 4),
    (2, "Vignesh", "ECE", 4),
    (3, "Rahul", "CSE", 3),
    (4, "Sai", "IoT", 4),
    (5, "Ajay", "CSE", 2),
]


marks = [
    (1, 1, "Java", 92),
    (2, 1, "Python", 88),
    (3, 2, "Java", 78),
    (4, 2, "Python", 82),
    (5, 3, "Java", 95),
    (6, 3, "Python", 91),
    (7, 4, "Java", 81),
    (8, 4, "Python", 86),
    (9, 5, "Java", 76),
    (10, 5, "Python", 79),
]


cursor.executemany(
    """
    INSERT INTO students
    (id, name, branch, year)
    VALUES (?, ?, ?, ?)
    """,
    students
)


cursor.executemany(
    """
    INSERT INTO marks
    (id, student_id, subject, marks)
    VALUES (?, ?, ?, ?)
    """,
    marks
)


connection.commit()

connection.close()


print(
    f"Sample database created at: "
    f"{database_path}"
)