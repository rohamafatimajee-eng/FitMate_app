# seed_exercises.py
import requests
import json
from database import init_db, get_connection

EXERCISES_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"


def seed():
    print("⬇️  Downloading exercise data...")
    resp = requests.get(EXERCISES_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(f"   Got {len(data)} exercises")

    init_db()
    conn = get_connection()
    c = conn.cursor()

    count = 0
    for ex in data:
        try:
            c.execute("""
                INSERT OR REPLACE INTO exercises
                (id, name, force, level, mechanic, equipment,
                 primary_muscles, secondary_muscles, instructions, category, images)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ex.get("id"),
                ex.get("name"),
                ex.get("force"),
                ex.get("level"),
                ex.get("mechanic"),
                ex.get("equipment"),
                json.dumps(ex.get("primaryMuscles", [])),
                json.dumps(ex.get("secondaryMuscles", [])),
                json.dumps(ex.get("instructions", [])),
                ex.get("category"),
                json.dumps(ex.get("images", []))
            ))
            count += 1
        except Exception as e:
            print(f"   Skipped {ex.get('id')}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Seeded {count} exercises into fitmate.db")


if __name__ == "__main__":
    seed()