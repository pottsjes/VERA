# closet_db.py
import sqlite3
from datetime import datetime
from typing import List, Optional
from models.constants import ITEM_TYPE

DB_NAME = "wardrobe.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            item_type TEXT,
            description TEXT,
            tags TEXT,  -- comma-separated tags
            image_path TEXT,
            available BOOLEAN DEFAULT 1,
            last_used TEXT,
            nfc_tag_id TEXT
        )
        """)
        conn.commit()

def add_item(name: str, item_type: ITEM_TYPE, description: str = "", tags: Optional[List[str]] = None,
             image_path: str = "", nfc_tag_id: Optional[str] = None):
    tag_str = ",".join(tags or [])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, item_type, description, tags, image_path, available, last_used, nfc_tag_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, item_type.value, description, tag_str, image_path, True, None, nfc_tag_id))
        conn.commit()

def delete_item(item_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id))
        conn.commit()

def list_items(only_available: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor()
        if only_available:
            cursor.execute("SELECT * FROM items WHERE available = 1")
        else:
            cursor.execute("SELECT * FROM items")
        return cursor.fetchall()

def toggle_item_availability(item_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT available, last_used FROM items WHERE id = ?", (item_id))
        row = cursor.fetchone()
        if row:
            new_status = not row[0]
            new_last_used = row[1]
            if new_status == 0:
                new_last_used = datetime.now().isoformat()
            cursor.execute("""
                UPDATE items
                SET available = ?, last_used = ?
                WHERE id = ?
            """, (new_status, new_last_used, item_id))
            conn.commit()
            return new_status
        return None

def mark_all_clean():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET available = 1")
        conn.commit()

def find_by_tag(tag: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE tags LIKE ?", (f"%{tag}%",))
        return cursor.fetchall()

def find_by_nfc(nfc_tag_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE nfc_tag_id = ?", (nfc_tag_id))
        return cursor.fetchall()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
