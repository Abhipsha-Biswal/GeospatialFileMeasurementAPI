import sqlite3
from pathlib import Path

DB_PATH = Path("geospatial.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            feature_count INTEGER NOT NULL,
            crs TEXT,
            status TEXT NOT NULL,
            error TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            feature_id INTEGER NOT NULL,
            geometry_type TEXT NOT NULL,
            measurement REAL,
            unit TEXT,
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
    """)
    conn.commit()
    conn.close()
