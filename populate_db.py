Import sqlite3
DB_FILE = "maintenance.db"
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("PRAGMA foreign_key= ON") 
#---Buildings---#
buildings = [ 
             ("Kwame Nkrumah Residence","12 Steve Biko Rd"),
             ("Oliver Tambo Residence","5 Mandela Ave"),]
cur.executemany("INSERT INTO Room
                (RoomNumber, Floor, BuildingID)VALUES(?,?,?);",rooms)
#---Students(RoomID 1-6)---#
students=[ 
  ("Lindiwe Dlamini","lindiwe.d@ufh.ac.za","0721234567",1),
  ("Thabo Nkosi","thabo.n@ufh.ac.za","0739876543",2),
  ("Aphiwe Zondi","aphile.z@ufh.ac.za","0812345678",3),
  ("Sipho Mahlangu","sipho.m@ufh.ac.za","0834567890",4),
  ("Nomvula Khumalo","nomvula.k@ufh.ac.za","0765432109",5),
  ("Bongani Radebe","bongani.r@ufh.ac.za","0798765432",6)
]
cur.executemany(
  "INSERT INTO Student(FullName, Email,
  Phone, RoomID) VALUES(?,?,?,?);",students)
#---Categories---#
categories=[
  ("Plumbing",),
  ("Electrical",),
  ("Furniture",),
  ("Internet",),
]
cur.executemany(INSERT INTO Category 
(CategoryName)VALUES(?);",categories)

#---Staff---#
staff=[
  ("Mr.Vusi Mkhize","vusi.m@residence.ac.za",
   "Plumbing","0711112222"),
  ("Ms.Ayanda Nene","Ayanda.n@residence.ac.za",
   "Eletrical","0722223333"),
  ("Mr.Karabo Sithole","karabo.s@residence.ac.za",
   "Furniture","0733334444"),
("Ms.Zanele Buthelezi","zanele.b@residence.ac.za",
 "Internet","0744445555"),
]
cur.executemany("INSERT INTO Staff(FullName, 
Email, Speciality, Phone)VALUES(?,?,?,?);",staff)
#---Maintenance Request---#
(StudentID, RoomID, CategoryID, Description, 
 Priority, Status, AssignedstaffID)
request =[
  (1,1,1,"Leaking tap in bathroom","Medium"," In progress",1),
  (2,2,2, " Light switch not working","High",
   "Submitted",None),
  (3,3,3, "Broken chair leg","low",
   "Resolved",3),
  (4,4,4, "No internet connection in room","Urgent",
   "In progress",4)
  (5,5,1, "Blocked drain in sink","Medium",
   "Submitted", None)
  (6,6,2, "Power outlet sparking","Urgent",
   "In progress",2),
]
cur.executemany(
  """"INSERT INTO MaintenanceRequest  
  (StudentID, RoomID, CategoryID,
  Description, Priority, Status, AssignedStaffID)
  VALUES(?,?,?,?,?,?,?);""",
  request,)
#---Status Updates(audit trail)----#
(RequestID, staffID, Note, NewStatus)
status_updates=[
  (1,1,"Assigned to plumber,awaiting parts","In progress"),
  (3,3,"Chair leg replaced and tested","Resolved"),
  (4,4, "Technician dispatched to check router", "In progress"),
  (6,2, "Electrician inspecting outlet","In progress"),
]
cur.executemany (
  """INSERT INTO StatusUpdate(RequestID, staffID, Note, NewStatus)
  VALUES(?,?,?,?);""",
  status_update,
)
#---Facilities(BuildingID 1 or 2)---#
("Printer-Ground Floor","Printer",1),
("Washing Machine 1","Washing Machine",1),
("Washing Machine 2","Washing Machine",1),
("Printer-Ground Floor","Printer",2),
("Washing Machine 1","Washing Machine",2),
]
conn.commit()
#---Verify---#
print("Sample data inserted successfully.\n")
for table in["Building","Room","Student",
             "Category","Staff","MaintenanceRequest",
             "StatusUpdate","Facility"]:
  cur.execute(f"SELECT COUNT(*) FROM {table};)
  count=cur.fetchone()[0]
  print (f"{table}:{count}rows")
  conn.close() 
  

  
