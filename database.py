import sqlite3

DB_FILE = "snapshots.db"

def init_db():
    """Database initialize karta hai."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_snapshot(filepath):
    """Snapshot ka path database me store karta hai."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO snapshots (filepath) VALUES (?)", (filepath,))
    conn.commit()
    conn.close()

def get_latest_snapshot():
    """Database se latest snapshot ka path fetch karta hai."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM snapshots ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize DB
init_db()
