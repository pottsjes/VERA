# closet_db.py
import sqlite3
from datetime import datetime
from typing import List, Optional
import os
from app.models.constants import ITEM_TYPE
from app.models.item import Item

# Resolve wardrobe.db relative to the project root, regardless of CWD
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_NAME = os.path.join(_PROJECT_ROOT, "data", "wardrobe.db")

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
            nfc_tag_id TEXT,
            fit TEXT,
            aesthetic TEXT,
            tone TEXT,
            layer TEXT,
            season TEXT,
            color TEXT,
            pattern_style TEXT,
            material TEXT,
            gender_expression TEXT,
            formality TEXT,
            use_case TEXT
        )
        """)
        conn.commit()

def map_item(row):
    return Item(
        item_id=row[0],
        name=row[1],
        item_type=row[2],
        description=row[3],
        tags=row[4].split(",") if row[4] else [],
        image_path=row[5],
        available=bool(row[6]),
        last_used=row[7],
        nfc_tag_id=row[8],
        fit=row[9],
        aesthetic=row[10],
        tone=row[11],
        layer=row[12],
        season=row[13],
        color=row[14],
        pattern_style=row[15],
        material=row[16],
        gender_expression=row[17],
        formality=row[18],
        use_case=row[19]
    )

def map_items(rows):
    return [map_item(row) for row in rows]

def add_item(name: str, item_type: str, description: str = "", tags: Optional[List[str]] = None,
             image_path: str = "", nfc_tag_id: Optional[str] = None, fit: str = "", aesthetic: str = "",
             tone: str = "", layer: str = "", season: str = "", color: str = "", pattern_style: str = "",
             material: str = "", gender_expression: str = "", formality: str = "", use_case: str = ""):
    tag_str = ",".join(tags or [])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, item_type, description, tags, image_path, available, last_used, nfc_tag_id,
                               fit, aesthetic, tone, layer, season, color, pattern_style, material,
                               gender_expression, formality, use_case)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, item_type, description, tag_str, image_path, True, None, nfc_tag_id, fit, aesthetic, tone,
              layer, season, color, pattern_style, material, gender_expression, formality, use_case))
        conn.commit()

def get_item(item_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        result = cursor.fetchall()
        return map_item(result[0])

def update_item(item_id: int, name: str, item_type: str, description: str = "", tags: str = "",
                image_path: str = "", nfc_tag_id: Optional[str] = None, fit: str = "", aesthetic: str = "",
                tone: str = "", layer: str = "", season: str = "", color: str = "", pattern_style: str = "",
                material: str = "", gender_expression: str = "", formality: str = "", use_case: str = ""):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE items
            SET name = ?, item_type = ?, description = ?, tags = ?, image_path = ?, nfc_tag_id = ?,
                fit = ?, aesthetic = ?, tone = ?, layer = ?, season = ?, color = ?, pattern_style = ?,
                material = ?, gender_expression = ?, formality = ?, use_case = ?
            WHERE id = ?
        """, (name, item_type, description, tags, image_path, nfc_tag_id, fit, aesthetic, tone, layer, season,
              color, pattern_style, material, gender_expression, formality, use_case, item_id))
        conn.commit()

def delete_item(item_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        
def list_items(only_available: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor()
        if only_available:
            cursor.execute("SELECT * FROM items WHERE available = 1")
        else:
            cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
    return map_items(rows)

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
        rows = cursor.fetchall()
    return map_items(rows)

def find_by_nfc(nfc_tag_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE nfc_tag_id = ?", (nfc_tag_id))
        rows = cursor.fetchall()
    return map_items(rows)

def get_items_by_type(item_type: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE item_type = ?", (item_type,))
        rows = cursor.fetchall()
    return map_items(rows)  # Use your existing `map_items` function

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
