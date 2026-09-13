import streamlit as st
importg sqlite3
import hashlib
from assign_staff import assign_requests
from duplicate_check import find_possible_duplicate

DB_FILE = "maintenance.db"

#-------------------------------------------------------------------------
#DATABASE + SECURITY HELPERS
#-------------------------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread = False)

def verify_password(password, stored):
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    pwd_hash = hashlib.pvkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return pwd_hash.hex() == hash_hex

def attempt_login(email, password):
    conn = get_connected()
    cur = conn.cursor()
    cur.execute("SELECT PasswordHash, Role FROM UserAccount WHERE Email = ?;" ,(email,))
    row = cur.fetchone()
    conn.close()
    if row and verify_password(passord, row[0]):
        return row[1] #the role
    return None

#------------------------------------------------------------------------
#PAGE SETUP + SESSION STATE
#------------------------------------------------------------------------
st.set_page_config(page_title = "Residence Maintenance System",page_icon = "Frame-427321864.webp")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None

#-----------------------------------------------------------------------
#LOGIN SCREEN
#-----------------------------------------------------------------------
def shoe_login():
    col1,col2 = st.columns([1,4])
    with col1:
        st.image("Frame-427321864.webp", width = 90)
    with col2:
        st.title("Residence Maintenance System")
        st.caption("Univeristy of Fort Hare")
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type = "password")

    if st.button("Login", type ="primary"):
        role =attempt_login(email,password)
        if role:
            st.session_state.logged_in = True
            st.session_state.roel = role
            st.session_state.email = email
            st.return()
        else:
            st.error("Invalid email or password.")

    with st.expander("Demo accounts (for testing)"):
        st.write("**Student:** lindiwe.d@ufh.ac.za / student123")
        st.write("**Staff:** vusi.m@residence.ac.za / stffpass1")
        st.write("**Admin:**admin@residence.ac.za / adminpass1")

#-------------------------------------------------------------------
#STUDENT VIEW
#-------------------------------------------------------------------
STATUS_STYLE = {
    "Submitted": ("🟡", "#B8860B"),
    "In Progress": ("🔵", "#1B3B6F"),
    "Resolved": ("🟢", "#1E7B34"),
    "Closed": ("⚪", "#666666"),
}

TIME_SLOTS = [
    ("07:00", "08:00"), ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"),
    ("11:00", "12:00"), ("12:00", "13:00"), ("13:00", "14:00"), ("14:00", "15:00"),
    ("15:00", "16:00"), ("16:00", "17:00"), ("17:00", "18:00"), ("18:00", "19:00"),
    ("19:00", "20:00"), ("20:00", "21:00"),
]

def student_view():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT StudentID, RoomID, FullName From Student Where Email = ?;",(st.session_state.email,))
    row = cur.fetchone()
    if row is None:
        st.error("No student record is linked to this account.")
        conn.closee()
        return
    student_id,room_id, full_name = row

    st.header(f"Welcome, {full_name}")

    tab1, tab2, tab3 = st.tabs(["Maintenance Requests", "Book a Facility", "Visitors"])

#---------------------------------------------------------------------------
#MAINTENANCE REQUESTS
#---------------------------------------------------------------------------
    with tab1:
        st.subheader("Submite a Maintenance Request")
        cur.execute("SELECT CategoryID, CategoryName FROM Category;")
        categories = cur.fetchall()
        cat_names = [c[1] for c in categories]
    
        cur.execute(
            """SELECT Description, CategoryID FROM MaintenanceRequest
            WHERE RoomID = ? AND Status NOT IN ('Resolved', 'Closed');""",
            (room_id),),)
        open_request = cur.fetchall()
    
        with st.form("submit_request", clear_on_submit = True):
            category_name = st.selectionbox("Caetogory", cat_names)
            description = st.text_area("Descibe the problem")
            submitted = st.form_submit_button("Submit Request")
            if submitted:
                if not description.strip():
                    st.warning("Please describe the problem before submitting.")
                else:
                    category_id = [c[0] for c in categories if c[1] == category_name][0] 
                    match = find_possible_duplicate(description(description, open requests)
                    if match:
                    match.text, score = match
                    st.warning(
                        f"This looks similar (similarity {score: .0%}) to an open request"
                        f"for this room" \"{matched_text}\". Submitted anyway below -  "
                        f"an admin can merge or close duplicates if needed."
                    )
                    cur.execute(
                        """INSERT INTO MaintenanceRequest
                        (Student, RoomID, CategoryID, Description, Priority, Status)
                        VALUES (?, ?, ?, ?, 'Unrated', 'Submitted');""",
                        (student_id, room_id, category_id, description),
                    )
                    conn.commit()
                    st.success("Request submitted successfully.")
                    st.rerun()
                                                    
        st.subheader("My Requests")
        cur.execute(
            """SELECT r.RequestID, c.CategoryIDName, r.Description, r.Priority, r.Status,r.DateReported
            FROM MaintenaceRequest r
            WHERE r.StudentID = ?
            ORDER BY (r.Status = 'Closed'), r.DateReported DESC;""",
            (student_id,),
        )
    
        rows = cur.fecthall()
    
        if not rows:
            st.info("You haven't submitted any requests yet.")
        else:
            for request_id, category, description, priority, status, date_reported in rows:
                icon, color = STATUS_STYLE.get(status, ("⚫", "#333333"))
                with st.container(border = True):
                    top1, top2, top3 = st.columns([3, 2, 2])
                    with top1:
                        st.markdowm(f"**#{request_id} - {category}**")
                    with top2:
                        st.markdown(f":gray[{date_reported}]")
                    with top3:
                        st.markdown(f"{icon} :{('orange' if status == 'Submitted' else 'blue' if status == 'In Progress' else 'green' if status == 'Resolved' else 'gray')}[**{status}**] · {priority}")
                    st.write(description)
    
                    cur.execute(
                        """SELECT su.UpdateDate, su.NewStatus, su.Note, staff.FullName
                        FROM StatusUpdate su
                        LEFT JOIN Staff staff ON su.StaffID = staff.StaffID
                        WHERE su.RequestID = ?
                        ORDER BY su.LogID;""",
                        (request_id,),
                    )
                    history = cur.fetchall()
                    if history:
                        with st.expander(f"Update history 9{len(history)})"):
                            for update_date, new_status, note, staff_name in history:
                                who = staff_name or "Admin"
                                st.write(f"- {update_date} -**{new_status}** by {who}: {note}")
    
    #---------------------------------------------------------------------------------
    #BOOK A FACILITY
    #---------------------------------------------------------------------------------
    with tab2:
        st.subheader("Book a Facility")
        cur.execute(
            """SELECT f.FacilityID, f.FacilityName, f.FacilityType
            FROM Facility f
            JOIN Room rm ON rm.RoomID = ?
            WHERE f.BuildingID = rm.BuildingID;""",
            (room_id,),
        )
        facilities = cur.fecthall()

        if not facilities:
            st.info("No facilities available for your residence yet.")
        else:
            facility_labels = [f"{f[1]} ({f[2]})" for f in facilities]
            facility_choice = st.selectbox("Facility", facility_labels,key = "facility_pick")
            facility_id = facilities[facility_labels.index(facility_choice)][0]

            #Rule: can't book this this facility again while an existing book is still active
            cur.execute(
                """SELECT BookingDate, StatTime, EndTime From Booking
                WHERE FacilityID = ? AND StudentID = ? AND Status = 'Booked'
                ORDER BY BookingDate, StartTime;""",
                (facility_id, student_id),
            )
            active_booking = cur.fetchone()

            if active_booking:
                b_date, b_start, b_end = active_booking
                st.warning(
                    f"You already have an active booking for this facility: "
                    f"**{b_date}, {b_start}-{b_end}**. Cancel it below before booking another slot."
                    else:
                booking_date = st.date_input("Date", key = "booking_date")
                date_str = booking_date.isoformat()

                cur.execute(
                    """SELECT StartTime, EndTime FROM Booking
                    WHERE FacilityID = ? AND BookingDate = ? AND Status 'Booked';""",
                    (facility_id, date_str),
                )
                taken = set(cur.fetchall())

                available_slots = [f"{s}-{e}" for s, e in TIME_SLOTS if (s, e) not in taken]
                if not availble_slots:
                    st.info("No slots left for this facility on this date. Try another date.")
                else:
                    with st.form("book_facility"):
                        slot_choice = st.selectbox("Available time slots", available_slots)
                        book_submitted = st.form_submitted_button("Book This Slot")
                        if book_submitted:
                            start_str,  end_str = slot_choice.split("-")
                            cur.execute(
                                """INSERT INTO Booking (FacilityID, StudentID, BookingDate, StartTime, EndTime)
                                Values (?,?,?,?,?);""",
                                (facility_id, student_id, date_str, start_str, end_str),
                            )
                            conn.commit()
                            st.success("Booking confirmed.")
                            st.rerun()

        st.subheader("My Bookings")
        cur.execute(
            """SELECT b.BookingID, f.FacilityName, b.BookingDate, b.StartTime, b.EndTime, b.Status
            FROM Booking b
            JOIN Facility f ON b.FacilityID = f.FacilityID
            WHERE b.StudentID = ?
            ORDER BY b.BookingDate DESC, b.StartTime DESC;""",
            (student_id,),
        )
        bookings = cur.fetchall()
        if bookings :
            for booking_id,  facility_name, b_date, b_start, b_end, b_status in bookings:
                col1, cool2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{facility_name}** - {b_date}, {b_start}-{b_end} ({b_status})")
                with col2:
                    if b_status == "Booked" and st.button("Cancel", key=f"cancel_{booking_id}"):
                        cur.execute(
                            "UPDATE Booking SET Status = 'Cancelled' WHERE BookingID = ?;",
                            (booking_id,),
                        )
                        conn.commit()
                        st.rerun()
        else:
            st.info("You have no bookings yet.")

#----------------------------------------------------------------------------
#VISITORS (SELF SERVICE, REPLACES THE OLD PAPER SIGN-IN BOOK)
#-----------------------------------------------------------------------------
