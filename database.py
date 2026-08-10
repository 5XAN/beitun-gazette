import os
import sqlite3
from contextlib import contextmanager
from typing import Iterable

from config import DB_PATH
from models import Item

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    store_name TEXT,
    url TEXT NOT NULL,
    date_start TEXT,
    date_end TEXT,
    published_at TEXT,
    scraped_at TEXT NOT NULL,
    first_seen_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_items_source ON items(source);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
"""


@contextmanager
def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)


def upsert_items(items: Iterable[Item]) -> int:
    """新增新項目,已存在的項目只更新 scraped_at,不覆寫 first_seen_at。回傳新增筆數。"""
    items = list(items)
    with connect() as conn:
        existing_ids = {row[0] for row in conn.execute("SELECT id FROM items")}
        new_count = sum(1 for item in items if item.id not in existing_ids)
        for item in items:
            conn.execute(
                """
                INSERT INTO items (
                    id, source, category, title, description, store_name,
                    url, date_start, date_end, published_at, scraped_at, first_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    scraped_at = excluded.scraped_at,
                    title = excluded.title,
                    description = excluded.description
                """,
                (
                    item.id, item.source, item.category, item.title, item.description,
                    item.store_name, item.url, item.date_start, item.date_end,
                    item.published_at, item.scraped_at, item.scraped_at,
                ),
            )
    return new_count
