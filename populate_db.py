import sqlite3

DB_FILE = "maintenance.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# --- Buildings ---
buildings = [
    ("Kwame Nkrumah Residence", "12 Steve Biko Rd"),
    ("Oliver Tambo Residence", "5 Mandela Ave"),
]
cur.executemany("INSERT INTO Building (BuildingName, Address) VALUES (?, ?);", buildings)

# --- Rooms (BuildingID: 1 or 2) ---
rooms = [
    ("101", 1, 1), ("102", 1, 1), ("201", 2, 1),
    ("101", 1, 2), ("102", 1, 2), ("202", 2, 2),
]
cur.executemany("INSERT INTO Room (RoomNumber, Floor, BuildingID) VALUES (?, ?, ?);", rooms)

# --- Students (RoomID 1-6) ---
students = [
    ("Lindiwe Dlamini", "lindiwe.d@ufh.ac.za", "0721234567", 1),
    ("Thabo Nkosi",     "thabo.n@ufh.ac.za",   "0739876543", 2),
    ("Aphiwe Zondi",    "aphiwe.z@ufh.ac.za",  "0812345678", 3),
    ("Sipho Mahlangu",  "sipho.m@ufh.ac.za",   "0834567890", 4),
    ("Nomvula Khumalo", "nomvula.k@ufh.ac.za", "0765432109", 5),
    ("Bongani Radebe",  "bongani.r@ufh.ac.za", "0798765432", 6),
]
cur.executemany(
    "INSERT INTO Student (FullName, Email, Phone, RoomID) VALUES (?, ?, ?, ?);", students
)

# --- Categories ---
categories = [
    ("Plumbing",),
    ("Electrical",),
    ("Furniture",),
    ("Internet",),
]
cur.executemany("INSERT INTO Category (CategoryName) VALUES (?);", categories)

# --- Staff ---
staff = [
    ("Mr. Vusi Mkhize", "vusi.m@residence.ac.za", "Plumbing", "0711112222"),
    ("Ms. Ayanda Nene", "ayanda.n@residence.ac.za", "Electrical", "0722223333"),
    ("Mr. Karabo Sithole", "karabo.s@residence.ac.za", "Furniture", "0733334444"),
    ("Ms. Zanele Buthelezi", "zanele.b@residence.ac.za", "Internet", "0744445555"),
]
cur.executemany("INSERT INTO Staff (FullName, Email, Specialty, Phone) VALUES (?, ?, ?, ?);", staff)

# --- Maintenance Requests ---
# (StudentID, RoomID, CategoryID, Description, Priority, Status, AssignedStaffID)
requests = [
    (1, 1, 1, "Leaking tap in bathroom",         "Medium", "In Progress", 1),
    (2, 2, 2, "Light switch not working",        "High",   "Submitted",   None),
    (3, 3, 3, "Broken chair leg",                "Low",    "Resolved",    3),
    (4, 4, 4, "No internet connection in room",  "Urgent", "In Progress", 4),
    (5, 5, 1, "Blocked drain in sink",           "Medium", "Submitted",   None),
    (6, 6, 2, "Power outlet sparking",           "Urgent", "In Progress", 2),
]
cur.executemany(
    """INSERT INTO MaintenanceRequest
       (StudentID, RoomID, CategoryID, Description, Priority, Status, AssignedStaffID)
       VALUES (?, ?, ?, ?, ?, ?, ?);""",
    requests,
)

# --- Status Updates (audit trail) ---
# (RequestID, StaffID, Note, NewStatus)
status_updates = [
    (1, 1, "Assigned to plumber, awaiting parts", "In Progress"),
    (3, 3, "Chair leg replaced and tested",       "Resolved"),
    (4, 4, "Technician dispatched to check router","In Progress"),
    (6, 2, "Electrician inspecting outlet",        "In Progress"),
]
cur.executemany(
    """INSERT INTO StatusUpdate (RequestID, StaffID, Note, NewStatus)
       VALUES (?, ?, ?, ?);""",
    status_updates,
)

# --- Facilities (BuildingID 1 or 2) ---
facilities = [
    ("Printer - Ground Floor", "Printer", 1),
    ("Washing Machine 1", "Washing Machine", 1),
    ("Washing Machine 2", "Washing Machine", 1),
    ("Printer - Ground Floor", "Printer", 2),
    ("Washing Machine 1", "Washing Machine", 2),
]
cur.executemany(
    "INSERT INTO Facility (FacilityName, FacilityType, BuildingID) VALUES (?, ?, ?);", facilities
)

conn.commit()

# --- Verify ---
print("Sample data inserted successfully.\n")
for table in ["Building", "Room", "Student", "Category", "Staff", "MaintenanceRequest", "StatusUpdate", "Facility"]:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"{table}: {count} rows")

conn.close()