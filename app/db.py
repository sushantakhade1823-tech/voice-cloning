import sqlite3
from contextlib import contextmanager
from .config import settings

DB = settings.data_dir / "voiceforge.db"

@contextmanager
def connection():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connection() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS voices (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, sample_path TEXT NOT NULL,
          consent_phrase TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS generations (
          id TEXT PRIMARY KEY, voice_id TEXT NOT NULL, text_preview TEXT NOT NULL,
          emotion TEXT NOT NULL, language TEXT NOT NULL, output_path TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)
