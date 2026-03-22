from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "labrag",
    "user": "-",
    "password": "-",
}

TEXT_ROOTS = [
    ("text/Lab seminar", "lab_seminar"),
    ("text/weekly report by week", "weekly_report"),
]

SQL_DIR = Path("sql")

EMBED_MODEL_NAME = "BAAI/bge-m3"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
BATCH_SIZE = 16