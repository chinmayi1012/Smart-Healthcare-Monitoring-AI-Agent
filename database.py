import sqlite3

conn = sqlite3.connect("health.db",check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS medication(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS health_logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
weight REAL,
height REAL,
bmi REAL,
date TEXT
)
""")

conn.commit()