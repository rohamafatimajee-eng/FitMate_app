# database.py
import sqlite3
import bcrypt
from datetime import date, timedelta

DB_PATH = "fitmate.db"


def get_connection():
    """Database se connection banata hai."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Pehli baar chalne pe saari tables bana deta hai."""
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        age INTEGER, height_cm REAL, weight_kg REAL,
        fitness_level TEXT, goal TEXT,
        target_body_parts TEXT, equipment TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    CREATE TABLE IF NOT EXISTS exercises (
        id TEXT PRIMARY KEY, name TEXT NOT NULL,
        force TEXT, level TEXT, mechanic TEXT, equipment TEXT,
        primary_muscles TEXT, secondary_muscles TEXT,
        instructions TEXT, category TEXT, images TEXT
    );
    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, exercise_id TEXT NOT NULL,
        date TEXT NOT NULL, sets INTEGER DEFAULT 0, reps INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    );
    CREATE TABLE IF NOT EXISTS body_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, date TEXT NOT NULL,
        weight_kg REAL, notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)
    conn.commit()
    conn.close()


# ---------- AUTH ----------
def register_user(username, password):
    """Naya user banao. Password ko hash karke save karo."""
    conn = get_connection()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hashed))
        conn.commit()
        user_id = c.lastrowid
        c.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return True, user_id
    except sqlite3.IntegrityError:
        return False, None
    finally:
        conn.close()


def login_user(username, password):
    """Password check karo aur user id return karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return True, row["id"]
    return False, None


# ---------- PROFILE ----------
def get_profile(user_id):
    """User ka profile fetch karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_profile(user_id, age, height_cm, weight_kg, fitness_level, goal,
                   target_body_parts, equipment):
    """Profile update karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE profiles
        SET age=?, height_cm=?, weight_kg=?, fitness_level=?, goal=?,
            target_body_parts=?, equipment=?, updated_at=CURRENT_TIMESTAMP
        WHERE user_id=?
    """, (age, height_cm, weight_kg, fitness_level, goal,
          ",".join(target_body_parts), ",".join(equipment), user_id))
    conn.commit()
    conn.close()


# ---------- EXERCISES ----------
def get_all_exercises():
    """Saare exercises return karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- WORKOUT LOGS ----------
def log_workout(user_id, exercise_id, date_str, sets, reps, completed=False):
    """Aaj ki exercise log karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO workout_logs (user_id, exercise_id, date, sets, reps, completed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, exercise_id, date_str, sets, reps, 1 if completed else 0))
    conn.commit()
    conn.close()


def update_workout_completion(log_id, completed):
    """Checkbox tick/uncheck karne pe update karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE workout_logs SET completed = ? WHERE id = ?",
              (1 if completed else 0, log_id))
    conn.commit()
    conn.close()


def delete_workout_log(log_id, user_id):
    """Workout log delete karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM workout_logs WHERE id = ? AND user_id = ?",
              (log_id, user_id))
    conn.commit()
    conn.close()


def get_today_workouts(user_id, date_str):
    """Aaj ke saare workouts fetch karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT wl.*, e.name as exercise_name, e.images as exercise_images
        FROM workout_logs wl
        JOIN exercises e ON wl.exercise_id = e.id
        WHERE wl.user_id = ? AND wl.date = ?
        ORDER BY wl.id ASC
    """, (user_id, date_str))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_workout_history(user_id, limit=200):
    """Purani history fetch karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT wl.*, e.name as exercise_name
        FROM workout_logs wl
        JOIN exercises e ON wl.exercise_id = e.id
        WHERE wl.user_id = ?
        ORDER BY wl.date DESC, wl.id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_current_streak(user_id):
    """Kitne din lagatar workout kiya - streak count karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT date FROM workout_logs
        WHERE user_id = ? AND completed = 1
        ORDER BY date DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()

    dates = {row["date"] for row in rows}
    if not dates:
        return 0

    check = date.today()
    if str(check) not in dates and str(check - timedelta(days=1)) not in dates:
        return 0
    if str(check) not in dates:
        check -= timedelta(days=1)

    streak = 0
    while str(check) in dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


# ---------- BODY METRICS ----------
def log_body_metric(user_id, date_str, weight_kg, notes=""):
    """Body weight save karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO body_metrics (user_id, date, weight_kg, notes)
        VALUES (?, ?, ?, ?)
    """, (user_id, date_str, weight_kg, notes))
    conn.commit()
    conn.close()


def get_body_metrics(user_id):
    """Saari weight entries fetch karo."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM body_metrics WHERE user_id = ? ORDER BY date ASC",
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]