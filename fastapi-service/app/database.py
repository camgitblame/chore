import sqlite3
import json
from typing import List, Dict, Optional
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "chores.db")


def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create chores table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chores (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            items TEXT,  -- JSON array of items
            steps TEXT,  -- JSON array of steps
            time_min INTEGER
        )
    """
    )

    # Check if we need to populate with initial data
    cursor.execute("SELECT COUNT(*) FROM chores")
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert initial chores data
        initial_chores = [
            {
                "id": "microwave",
                "title": "Clean the microwave",
                "items": ["Bowl", "Water", "Vinegar or lemon", "Cloth"],
                "steps": [
                    "Fill a bowl with water and a splash of vinegar",
                    "Microwave on high for 3 minutes",
                    "Let sit 1 minute to steam",
                    "Wipe walls, ceiling, and plate",
                    "Dry with a cloth",
                ],
                "time_min": 8,
            },
            {
                "id": "desk",
                "title": "Organize your desk",
                "items": ["Trash bag", "Microfiber cloth"],
                "steps": [
                    "Put trash in the bag",
                    "Group pens, cables, and papers",
                    "Wipe the surface",
                    "Return only daily items to the desk",
                    "Stash the rest in a drawer or box",
                ],
                "time_min": 10,
            },
        ]

        for chore in initial_chores:
            cursor.execute(
                """
                INSERT INTO chores (id, title, items, steps, time_min)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    chore["id"],
                    chore["title"],
                    json.dumps(chore["items"]),
                    json.dumps(chore["steps"]),
                    chore["time_min"],
                ),
            )

    conn.commit()
    conn.close()


def get_all_chores() -> List[Dict]:
    """Get all chores from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, items, steps, time_min FROM chores")
    rows = cursor.fetchall()

    chores = []
    for row in rows:
        chore = {
            "id": row[0],
            "title": row[1],
            "items": json.loads(row[2]) if row[2] else [],
            "steps": json.loads(row[3]) if row[3] else [],
            "time_min": row[4],
        }
        chores.append(chore)

    conn.close()
    return chores


def get_chore_by_id(chore_id: str) -> Optional[Dict]:
    """Get a specific chore by ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, items, steps, time_min FROM chores WHERE id = ?", (chore_id,)
    )
    row = cursor.fetchone()

    if row:
        chore = {
            "id": row[0],
            "title": row[1],
            "items": json.loads(row[2]) if row[2] else [],
            "steps": json.loads(row[3]) if row[3] else [],
            "time_min": row[4],
        }
        conn.close()
        return chore

    conn.close()
    return None


def search_chores(query: str) -> List[Dict]:
    """Search chores by title."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, items, steps, time_min FROM chores WHERE title LIKE ?",
        (f"%{query}%",),
    )
    rows = cursor.fetchall()

    chores = []
    for row in rows:
        chore = {
            "id": row[0],
            "title": row[1],
            "items": json.loads(row[2]) if row[2] else [],
            "steps": json.loads(row[3]) if row[3] else [],
            "time_min": row[4],
        }
        chores.append(chore)

    conn.close()
    return chores


def add_chore(chore_data: Dict) -> bool:
    """Add a new chore to the database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO chores (id, title, items, steps, time_min)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                chore_data["id"],
                chore_data["title"],
                json.dumps(chore_data.get("items", [])),
                json.dumps(chore_data.get("steps", [])),
                chore_data.get("time_min", 0),
            ),
        )

        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_chore(chore_id: str, chore_data: Dict) -> bool:
    """Update an existing chore."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE chores 
            SET title = ?, items = ?, steps = ?, time_min = ?
            WHERE id = ?
        """,
            (
                chore_data["title"],
                json.dumps(chore_data.get("items", [])),
                json.dumps(chore_data.get("steps", [])),
                chore_data.get("time_min", 0),
                chore_id,
            ),
        )

        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except Exception:
        return False


def delete_chore(chore_id: str) -> bool:
    """Delete a chore from the database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM chores WHERE id = ?", (chore_id,))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except Exception:
        return False
