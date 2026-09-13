import sqlite3
import os

DB_FILE = "maintenance.db"
SCHEMA_FILE = "schema.sql"

# Start fresh each time this is run
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

with open(SCHEMA_FILE, "r") as f:
    cur.executescript(f.read())

conn.commit()

# Verify: list all tables and their columns
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row[0] for row in cur.fetchall()]

print(f"Database '{DB_FILE}' created successfully.")
print(f"Tables created: {len(tables)}\n")

for table in tables:
    cur.execute(f"PRAGMA table_info({table});")
    columns = cur.fetchall()
    print(f"{table}")
    for col in columns:
        # col: (cid, name, type, notnull, dflt_value, pk)
        pk = " [PK]" if col[5] else ""
        print(f"   - {col[1]} ({col[2]}){pk}")
    print()

conn.close()


