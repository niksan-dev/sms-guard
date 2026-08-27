import sqlite3
import os

DB_PATH = "data/security_guard.db"  # Change this to your actual database file

print("Looking for database:", os.path.abspath(DB_PATH))

if not os.path.exists(DB_PATH):
    print("\n❌ Database file not found!")
    print("Available .db files:")

    for file in os.listdir("."):
        if file.endswith(".db") or file.endswith(".sqlite"):
            print("  ", file)

else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)

    tables = cursor.fetchall()

    print("\n✅ Tables found:\n")

    for table in tables:
        print("📋", table[0])

    conn.close()