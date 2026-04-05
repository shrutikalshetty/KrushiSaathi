import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crops table
cursor.execute("""
CREATE TABLE IF NOT EXISTS crops(
id INTEGER PRIMARY KEY AUTOINCREMENT,
crop_name TEXT,
season TEXT,
income INTEGER
)
""")

# Expenses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
amount INTEGER
)
""")

# Soil table
cursor.execute("""
CREATE TABLE IF NOT EXISTS soil(
id INTEGER PRIMARY KEY AUTOINCREMENT,
soil_type TEXT,
ph TEXT,
notes TEXT
)
""")

conn.commit()
conn.close()

print("Database tables created successfully")

