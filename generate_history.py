import sqlite3
import random
from datetime import date,timedelda
DB_FILE="maintenance.db"
random.seed(42) #reproducible demo data 

conn=sqlite3.connect(DB_FILE)
cur=conn.cursor()

cur.execute("SELECT StudentID, RoomID FROM Student;")
students = cur.fetchall()
cur.execute("SELECT CategoryID, CategoryName FROM Category;")
categories = cur.fetchall()
cur.execute("SELECT RoomID, BuildingID FROM Room;")
rooms = cur.fetchall()

if not students or not categories 
print("No students/categories found. Run populate_db.py first")
raise SystemExit(1)

descriptions_by_category={
  "Plumbing":[Leaking tap","Blocked drain", "Toilet not flushing", "Low water pressure"],
  "Electrical":: ["Power outlet not working", "Light flickering", "Circuit tripping", "No power in room"],
    "Furniture": ["Broken chair", "Wardrobe door off hinge", "Desk leg loose", "Bed frame broken"],
    "Internet": ["No WiFi signal", "Slow internet", "Router not working", "Ethernet port dead"],
}
today = date.today()
start_day = today - timedelta(days=89)  # ~3 months of history

rows_to_insert = []
building1_room_ids = [r[0] for r in rooms if r[1] == 1]

for day_offset in range(90):
    current_date = start_day + timedelta(days=day_offset)

    # Baseline: 1-4 requests on a normal day
    daily_count = random.randint(1, 4)

    # Deliberate anomaly: one specific day gets a big spike (simulates e.g. a burst pipe)
    if day_offset == 45:
        daily_count = 14

    for _ in range(daily_count):
        student_id, room_id = random.choice(students)

        # Deliberate hotspot bias: Building 1 rooms get 3x more Electrical issues
        if room_id in building1_room_ids and random.random() < 0.5:
            category_id, category_name = next(c for c in categories if c[1] == "Electrical")
        else:
            category_id, category_name = random.choice(categories)

        description = random.choice(descriptions_by_category.get(category_name, ["Issue reported"]))
        priority = random.choice(["Low", "Medium", "High", "Urgent"])
        status = random.choice(["Resolved", "Closed", "Resolved", "In Progress"])

        rows_to_insert.append((student_id, room_id, category_id, description, priority, status, current_date.isoformat()))

cur.executemany(
    """INSERT INTO MaintenanceRequest
       (StudentID, RoomID, CategoryID, Description, Priority, Status, DateReported)
       VALUES (?, ?, ?, ?, ?, ?, ?);""",
    rows_to_insert,
)
conn.commit()

print(f"Inserted {len(rows_to_insert)} synthetic historical requests.")
print(f"Hotspot bias: Building 1 rooms skewed toward Electrical issues.")
print(f"Anomaly: day {start_day + timedelta(days=45)} has an artificial spike (14 requests).")

conn.close()


              
  
