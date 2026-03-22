import psycopg
from pgvector.psycopg import register_vector

from config import DB_CONFIG, SQL_DIR


def load_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def connect_db():
    conn = psycopg.connect(**DB_CONFIG)
    register_vector(conn)
    return conn


def ensure_schema(conn):
    sql = load_sql("schema.sql")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def get_existing_filepaths(conn) -> set[str]:
    sql = load_sql("select_existing_filepaths.sql")
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return {row[0] for row in rows}