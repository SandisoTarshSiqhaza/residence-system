import sqlite3
DB_FILE = "maintainance.db"
PRIORITY_ORDER = {"Urgent":1, "High":2, "Medium":3, "Low":4}

def get_staff_workload(cur):
"""
Returns a dict{StaffID:active_request_count} for every staff member,
Conting only requests that are not yet Resolved or Closed.
"""
cur.execute("""
SELECT st.STAFFID,COUNT(R.RequestID)
FROM Staff st
LEFT JOIN MaintainanceRequest r
On st.StaffID = r.AssignStaffID
AND r.Status NOT IN('Resolved', 'Closed')
GROUP BY st.STAFFiD;
""")
return dict(cur.fetchall())

def get_unassigned_request(cur):
 """Returns unassigned requests, most urgent first, oldest first within a priority."""
  cur.execute("""
  SELECT RequestID, CategoryID, Priority, DateReported
  FROM MaintainanceRequest
  WHERE AssignedStaffID IS NULL AND Priority != 'Unrated';
  """)
requests = cur.fetchall()
# Sort in Python using the priority order above, then by date
requests.sort(key=lambda r:(PRIORITY_ORDER[r[2]], r[3]))
return requests

def get_staff_by_category(cur):
  """
  Returns{CategoryID:[StaffID,...]} by matching Category name to Staff speciality
  Assumes category names line up with stuff specialties (e.g 'Plumbing' = 'Plumbing').
  """
  cur.execute("SELECT CategoryID, CategoryName FROM Category;")
  categories=cur.fetchall()

cur.execute("SELECT StaffID, Specialty FROM Staff;")
staff=cur.fetchall()

mapping ={}
for cat_id, cat_name in categories:
  mapping[cat_id]=[s_id for s_id, specialty in staff if specialty == cat_name]
  return mapping

def assign_requests():
  """
  Greedy assignment algorithm:
  1. Take unassigned requests, most urgent first.
  2. For each, find staff matching the request's category/specialty.
  3. Among matching staff, pick the one with the lowest currrent workload.
  4. Assign, log the change, and update that staff member's workoad in 
     memory so the next request sees the updated balance.
     """
  conn=splite3.connect(DB_FILE)
  cur=conn.cursor()

workload=get_staff_workload(cur)
staff_by_category=get_staff_by_category(cur)
requests =get_unassigned_requests(cur)

assignment_made[]

for requests_id, category_id, priority, date_reported in requests:
  candidates = staff_by_category.get(category_id[])
  if not candidates:
    print(f"Request{request_id}: no staff available for this category. Skipped.")
    continue

#Pick the candidate with the lowest current workload
chosen_staff=min(candidates, key=lambda s_id:workload.get(s_id, 0))

cur.execute(
  "UPDATE MaintananceRequest SET AssignedStaffID=? WHERE RequestID=?:",
  (chosen_staff, request_id),
)
cur.execute(
  """INSERT INTO StatusUpdate(RequestID, StaffID, Note, NewStatus)
  VALUES(?,?,?,?);""",
  (request_id, chosen_staff, "Auto-assigned by staff alloaction algorithm","In Progress"),
)
cur.execute(
  "UPDATE MaintanceRequest SET Status='In Progress'WHERE RequestID = ?;",
  (request_id,),
)

workload[chosen_staff]=workload.get(chosen_staff,0)+1
assignments_made.append((requests_id, chosen_staff,priority))

conn.commit()
conn.close()
return assignments_made

if_name_=="_main_":
results =assign_requests()
if not results:
  print("No unassigned requests found")
else:
print(f"{len(results)} request(s) assigned:\n")
for request_id, staff_id, priority in results:
print(f"Request{request_id}({priority})->Staff {staff_id}")

                        

  
  
