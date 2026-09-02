import os
from pathlib import Path

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

_conn: psycopg.Connection | None = None


def get_conn() -> psycopg.Connection:
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
        with _conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(_conn)
    return _conn


def init_schema() -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    with get_conn().cursor() as cur:
        cur.execute(schema_path.read_text(encoding="utf-8"))


def insert_chunks(rows: list[dict]) -> None:
    """rows: {dataset, source_file, source_format, chunk_index, content, embedding}"""
    rows = [{**r, "embedding": Vector(r["embedding"])} for r in rows]
    with get_conn().cursor() as cur:
        cur.executemany(
            """
            INSERT INTO chunks (dataset, source_file, source_format, chunk_index, content, embedding)
            VALUES (%(dataset)s, %(source_file)s, %(source_format)s, %(chunk_index)s, %(content)s, %(embedding)s)
            """,
            rows,
        )


def search(dataset: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(
            """
            SELECT source_file, source_format, chunk_index, content,
                   1 - (embedding <=> %(qe)s) AS score
            FROM chunks
            WHERE dataset = %(dataset)s
            ORDER BY embedding <=> %(qe)s
            LIMIT %(top_k)s
            """,
            {"qe": Vector(query_embedding), "dataset": dataset, "top_k": top_k},
        )
        cols = [c.name for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def clear_dataset(dataset: str) -> None:
    with get_conn().cursor() as cur:
        cur.execute("DELETE FROM chunks WHERE dataset = %s", (dataset,))
