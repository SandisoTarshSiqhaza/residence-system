import streamlit as st
import sqlite3
import hashlib
from assign_staff import assign_requests
from duplicate_check import find_possible_duplicate

DB_FILE = "maintenance.db"


# ---------------------------------------------------------------------
# Database + security helpers
# ---------------------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def verify_password(password, stored):
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return pwd_hash.hex() == hash_hex


def attempt_login(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT PasswordHash, Role FROM UserAccount WHERE Email = ?;", (email,))
    row = cur.fetchone()
    conn.close()
    if row and verify_password(password, row[0]):
        return row[1]  # the Role
    return None


# ---------------------------------------------------------------------
# Page setup + session state
# ---------------------------------------------------------------------
st.set_page_config(page_title="Residence Maintenance System", page_icon="Frame-427321864.webp")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None


def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None


# ---------------------------------------------------------------------
# Login screen
# ---------------------------------------------------------------------
def show_login():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("Frame-427321864.webp", width=90)
    with col2:
        st.title("Residence Maintenance System")
        st.caption("University of Fort Hare")
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):
        role = attempt_login(email, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Invalid email or password.")

    with st.expander("Demo accounts (for testing)"):
        st.write("**Student:** lindiwe.d@ufh.ac.za / student123")
        st.write("**Staff:** vusi.m@residence.ac.za / staffpass1")
        st.write("**Admin:** admin@residence.ac.za / adminpass1")


# ---------------------------------------------------------------------
# Student view
# ---------------------------------------------------------------------
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
    cur.execute("SELECT StudentID, RoomID, FullName FROM Student WHERE Email = ?;", (st.session_state.email,))
    row = cur.fetchone()
    if row is None:
        st.error("No student record is linked to this account.")
        conn.close()
        return
    student_id, room_id, full_name = row

    st.header(f"Welcome, {full_name}")

    tab1, tab2, tab3 = st.tabs(["Maintenance Requests", "Book a Facility", "Visitors"])

    # -----------------------------------------------------------------
    # Maintenance Requests
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("Submit a Maintenance Request")
        cur.execute("SELECT CategoryID, CategoryName FROM Category;")
        categories = cur.fetchall()
        cat_names = [c[1] for c in categories]

        cur.execute(
            """SELECT Description, CategoryID FROM MaintenanceRequest
               WHERE RoomID = ? AND Status NOT IN ('Resolved', 'Closed');""",
            (room_id,),
        )
        open_requests = cur.fetchall()

        with st.form("submit_request", clear_on_submit=True):
            category_name = st.selectbox("Category", cat_names)
            description = st.text_area("Describe the problem")
            submitted = st.form_submit_button("Submit Request")
            if submitted:
                if not description.strip():
                    st.warning("Please describe the problem before submitting.")
                else:
                    category_id = [c[0] for c in categories if c[1] == category_name][0]
                    match = find_possible_duplicate(description, open_requests)
                    if match:
                        matched_text, score = match
                        st.warning(
                            f"This looks similar (similarity {score:.0%}) to an open request "
                            f"for this room: \"{matched_text}\". Submitted anyway below — "
                            f"an admin can merge or close duplicates if needed."
                        )
                    cur.execute(
                        """INSERT INTO MaintenanceRequest
                           (StudentID, RoomID, CategoryID, Description, Priority, Status)
                           VALUES (?, ?, ?, ?, 'Unrated', 'Submitted');""",
                        (student_id, room_id, category_id, description),
                    )
                    conn.commit()
                    st.success("Request submitted successfully.")
                    st.rerun()

        st.subheader("My Requests")
        cur.execute(
            """SELECT r.RequestID, c.CategoryName, r.Description, r.Priority, r.Status, r.DateReported
               FROM MaintenanceRequest r
               JOIN Category c ON r.CategoryID = c.CategoryID
               WHERE r.StudentID = ?
               ORDER BY (r.Status = 'Closed'), r.DateReported DESC;""",
            (student_id,),
        )
        rows = cur.fetchall()

        if not rows:
            st.info("You haven't submitted any requests yet.")
        else:
            for request_id, category, description, priority, status, date_reported in rows:
                icon, color = STATUS_STYLE.get(status, ("⚫", "#333333"))
                with st.container(border=True):
                    top1, top2, top3 = st.columns([3, 2, 2])
                    with top1:
                        st.markdown(f"**#{request_id} — {category}**")
                    with top2:
                        st.markdown(f":gray[{date_reported}]")
                    with top3:
                        st.markdown(f"{icon} :{('orange' if status=='Submitted' else 'blue' if status=='In Progress' else 'green' if status=='Resolved' else 'gray')}[**{status}**] · {priority}")

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
                        with st.expander(f"Update history ({len(history)})"):
                            for update_date, new_status, note, staff_name in history:
                                who = staff_name or "Admin"
                                st.write(f"- {update_date} — **{new_status}** by {who}: {note}")

    # -----------------------------------------------------------------
    # Book a Facility
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("Book a Facility")
        cur.execute(
            """SELECT f.FacilityID, f.FacilityName, f.FacilityType
               FROM Facility f
               JOIN Room rm ON rm.RoomID = ?
               WHERE f.BuildingID = rm.BuildingID;""",
            (room_id,),
        )
        facilities = cur.fetchall()

        if not facilities:
            st.info("No facilities available for your residence yet.")
        else:
            facility_labels = [f"{f[1]} ({f[2]})" for f in facilities]
            facility_choice = st.selectbox("Facility", facility_labels, key="facility_pick")
            facility_id = facilities[facility_labels.index(facility_choice)][0]

            # Rule: can't book this facility again while an existing booking is still active
            cur.execute(
                """SELECT BookingDate, StartTime, EndTime FROM Booking
                   WHERE FacilityID = ? AND StudentID = ? AND Status = 'Booked'
                   ORDER BY BookingDate, StartTime;""",
                (facility_id, student_id),
            )
            active_booking = cur.fetchone()

            if active_booking:
                b_date, b_start, b_end = active_booking
                st.warning(
                    f"You already have an active booking for this facility: "
                    f"**{b_date}, {b_start}–{b_end}**. Cancel it below before booking another slot."
                )
            else:
                booking_date = st.date_input("Date", key="booking_date")
                date_str = booking_date.isoformat()

                cur.execute(
                    """SELECT StartTime, EndTime FROM Booking
                       WHERE FacilityID = ? AND BookingDate = ? AND Status = 'Booked';""",
                    (facility_id, date_str),
                )
                taken = set(cur.fetchall())

                available_slots = [f"{s}–{e}" for s, e in TIME_SLOTS if (s, e) not in taken]

                if not available_slots:
                    st.info("No slots left for this facility on this date. Try another date.")
                else:
                    with st.form("book_facility"):
                        slot_choice = st.selectbox("Available time slots", available_slots)
                        book_submitted = st.form_submit_button("Book This Slot")
                        if book_submitted:
                            start_str, end_str = slot_choice.split("–")
                            cur.execute(
                                """INSERT INTO Booking (FacilityID, StudentID, BookingDate, StartTime, EndTime)
                                   VALUES (?, ?, ?, ?, ?);""",
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
        if bookings:
            for booking_id, facility_name, b_date, b_start, b_end, b_status in bookings:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{facility_name}** — {b_date}, {b_start}–{b_end} ({b_status})")
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

    # -----------------------------------------------------------------
    # Visitors (self-service, replaces the old paper sign-in book)
    # -----------------------------------------------------------------
    with tab3:
        st.subheader("Sign In a Visitor")
        st.caption("Sign your visitor in here, then confirm with security at the front desk on arrival.")
        with st.form("sign_in_visitor", clear_on_submit=True):
            v_name = st.text_input("Visitor Full Name")
            v_phone = st.text_input("Visitor Phone")
            v_purpose = st.text_input("Purpose of Visit")
            if st.form_submit_button("Sign In"):
                if v_name.strip():
                    cur.execute(
                        """INSERT INTO Visitor (FullName, Phone, HostStudentID, Purpose)
                           VALUES (?, ?, ?, ?);""",
                        (v_name, v_phone, student_id, v_purpose),
                    )
                    conn.commit()
                    st.success(f"{v_name} signed in. Please verify with security at the front desk.")
                    st.rerun()
                else:
                    st.warning("Visitor name is required.")

        st.subheader("My Visitors Currently On Campus")
        cur.execute(
            """SELECT VisitorID, FullName, Purpose, SignInTime FROM Visitor
               WHERE HostStudentID = ? AND SignOutTime IS NULL
               ORDER BY SignInTime;""",
            (student_id,),
        )
        onsite = cur.fetchall()
        if onsite:
            for visitor_id, v_name, purpose, sign_in in onsite:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{v_name}** — {purpose} — signed in {sign_in}")
                with col2:
                    if st.button("Sign Out", key=f"signout_{visitor_id}"):
                        cur.execute(
                            "UPDATE Visitor SET SignOutTime = datetime('now') WHERE VisitorID = ?;",
                            (visitor_id,),
                        )
                        conn.commit()
                        st.success("Signed out. Please confirm with security on the way out.")
                        st.rerun()
        else:
            st.info("You have no visitors currently signed in.")

    conn.close()


# ---------------------------------------------------------------------
# Staff view
# ---------------------------------------------------------------------
def staff_view():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT StaffID, FullName, Specialty FROM Staff WHERE Email = ?;", (st.session_state.email,))
    row = cur.fetchone()
    if row is None:
        st.error("No staff record is linked to this account.")
        conn.close()
        return
    staff_id, full_name, specialty = row

    st.header(f"Welcome, {full_name}")
    st.caption(f"Specialty: {specialty}")

    st.subheader("My Assigned Requests")
    cur.execute(
        """SELECT r.RequestID, s.FullName, c.CategoryName, r.Description, r.Priority, r.Status,
                  b.BuildingName, rm.RoomNumber
           FROM MaintenanceRequest r
           JOIN Student s ON r.StudentID = s.StudentID
           JOIN Category c ON r.CategoryID = c.CategoryID
           JOIN Room rm ON r.RoomID = rm.RoomID
           JOIN Building b ON rm.BuildingID = b.BuildingID
           WHERE r.AssignedStaffID = ?
           ORDER BY
               (r.Status = 'Resolved'),
               CASE r.Priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2
                                WHEN 'Medium' THEN 3 ELSE 4 END;""",
        (staff_id,),
    )
    rows = cur.fetchall()

    if not rows:
        st.info("No requests currently assigned to you.")
    else:
        for request_id, student_name, category, description, priority, status, building, room in rows:
            icon, _ = STATUS_STYLE.get(status, ("⚫", "#333333"))
            priority_color = {"Urgent": "red", "High": "orange", "Medium": "blue", "Low": "gray"}.get(priority, "gray")

            with st.container(border=True):
                st.markdown(f"### 📍 {building} — Room {room}")
                top1, top2 = st.columns([3, 2])
                with top1:
                    st.markdown(f"**#{request_id} — {category}** · {student_name}")
                with top2:
                    st.markdown(f"{icon} **{status}** · :{priority_color}[{priority}]")

                st.write(description)

                staff_status_options = ["Submitted", "In Progress", "Resolved"]
                current_index = (
                    staff_status_options.index(status) if status in staff_status_options else 0
                )
                col1, col2 = st.columns([2, 3])
                with col1:
                    new_status = st.selectbox(
                        "Update status",
                        staff_status_options,
                        index=current_index,
                        key=f"status_{request_id}",
                    )
                with col2:
                    note = st.text_input("Note", key=f"note_{request_id}")

                if st.button("Save Update", key=f"save_{request_id}"):
                    cur.execute(
                        "UPDATE MaintenanceRequest SET Status = ? WHERE RequestID = ?;",
                        (new_status, request_id),
                    )
                    cur.execute(
                        """INSERT INTO StatusUpdate (RequestID, StaffID, Note, NewStatus)
                           VALUES (?, ?, ?, ?);""",
                        (request_id, staff_id, note or "Status updated", new_status),
                    )
                    conn.commit()
                    st.success("Updated.")
                    st.rerun()

    conn.close()


# ---------------------------------------------------------------------
# Admin view
# ---------------------------------------------------------------------
def admin_view():
    conn = get_connection()
    cur = conn.cursor()

    st.header("Admin Dashboard")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["All Requests", "Set Priority", "Verify & Close", "Run Staff Assignment",
         "Manage Reference Data", "Analytics"]
    )

    with tab1:
        cur.execute(
            """SELECT r.RequestID, s.FullName AS Student, b.BuildingName, rm.RoomNumber,
                      c.CategoryName, r.Priority, r.Status,
                      COALESCE(st.FullName, 'Unassigned') AS AssignedStaff,
                      (SELECT su.Note FROM StatusUpdate su
                       WHERE su.RequestID = r.RequestID
                       ORDER BY su.LogID DESC LIMIT 1) AS LatestNote
               FROM MaintenanceRequest r
               JOIN Student s ON r.StudentID = s.StudentID
               JOIN Room rm ON r.RoomID = rm.RoomID
               JOIN Building b ON rm.BuildingID = b.BuildingID
               JOIN Category c ON r.CategoryID = c.CategoryID
               LEFT JOIN Staff st ON r.AssignedStaffID = st.StaffID
               ORDER BY r.RequestID;"""
        )
        rows = cur.fetchall()
        data = [
            {"ID": r[0], "Student": r[1], "Building": r[2], "Room": r[3],
             "Category": r[4], "Priority": r[5], "Status": r[6], "Assigned To": r[7],
             "Latest Note": r[8] or "—"}
            for r in rows
        ]
        st.dataframe(data, width="stretch", hide_index=True)

    with tab2:
        st.write("Requests awaiting a priority rating. Set priority based on the description "
                 "before the assignment algorithm will pick them up.")
        cur.execute(
            """SELECT r.RequestID, c.CategoryName, r.Description, b.BuildingName, rm.RoomNumber
               FROM MaintenanceRequest r
               JOIN Category c ON r.CategoryID = c.CategoryID
               JOIN Room rm ON r.RoomID = rm.RoomID
               JOIN Building b ON rm.BuildingID = b.BuildingID
               WHERE r.Priority = 'Unrated'
               ORDER BY r.RequestID;"""
        )
        unrated = cur.fetchall()

        if not unrated:
            st.info("No requests waiting for a priority rating.")
        else:
            for request_id, category, description, building, room in unrated:
                with st.expander(f"#{request_id} — {category} — {building}, Room {room}"):
                    st.write(f"**Description:** {description}")
                    chosen_priority = st.selectbox(
                        "Set priority",
                        ["Low", "Medium", "High", "Urgent"],
                        key=f"priority_{request_id}",
                    )
                    if st.button("Save Priority", key=f"save_priority_{request_id}"):
                        cur.execute(
                            "UPDATE MaintenanceRequest SET Priority = ? WHERE RequestID = ?;",
                            (chosen_priority, request_id),
                        )
                        conn.commit()
                        st.success(f"Priority set to {chosen_priority}.")
                        st.rerun()

    with tab3:
        st.write("Requests marked Resolved by staff, awaiting Admin verification before closing.")
        cur.execute(
            """SELECT r.RequestID, c.CategoryName, r.Description, b.BuildingName, rm.RoomNumber,
                      COALESCE(st.FullName, 'Unassigned') AS StaffName
               FROM MaintenanceRequest r
               JOIN Category c ON r.CategoryID = c.CategoryID
               JOIN Room rm ON r.RoomID = rm.RoomID
               JOIN Building b ON rm.BuildingID = b.BuildingID
               LEFT JOIN Staff st ON r.AssignedStaffID = st.StaffID
               WHERE r.Status = 'Resolved'
               ORDER BY r.RequestID;"""
        )
        resolved = cur.fetchall()

        if not resolved:
            st.info("No requests currently awaiting verification.")
        else:
            for request_id, category, description, building, room, staff_name in resolved:
                with st.expander(f"#{request_id} — {category} — {building}, Room {room}"):
                    st.write(f"**Description:** {description}")
                    st.write(f"**Resolved by:** {staff_name}")
                    if st.button("Verify and Close", key=f"close_{request_id}"):
                        cur.execute(
                            "UPDATE MaintenanceRequest SET Status = 'Closed' WHERE RequestID = ?;",
                            (request_id,),
                        )
                        cur.execute(
                            """INSERT INTO StatusUpdate (RequestID, StaffID, Note, NewStatus)
                               VALUES (?, NULL, ?, 'Closed');""",
                            (request_id, "Verified and closed by Admin"),
                        )
                        conn.commit()
                        st.success("Request closed.")
                        st.rerun()

    with tab4:
        st.write("Automatically assigns unassigned, priority-rated requests to the best-matched, "
                 "least-busy staff member (see Algorithms section of the documentation).")
        cur.execute(
            """SELECT COUNT(*) FROM MaintenanceRequest
               WHERE AssignedStaffID IS NULL AND Priority != 'Unrated';"""
        )
        pending = cur.fetchone()[0]
        st.metric("Unassigned, priority-rated requests", pending)

        if st.button("Run Assignment Algorithm", type="primary"):
            conn.close()  # avoid a locked-database conflict with assign_requests()
            results = assign_requests()
            if results:
                st.success(f"{len(results)} request(s) assigned.")
                for request_id, staff_id, priority in results:
                    st.write(f"- Request {request_id} ({priority}) → Staff {staff_id}")
            else:
                st.info("No unassigned, priority-rated requests to process.")
            st.rerun()

    with tab5:
        st.write("**Add a Building**")
        with st.form("add_building", clear_on_submit=True):
            b_name = st.text_input("Building Name")
            b_addr = st.text_input("Address")
            if st.form_submit_button("Add Building"):
                if b_name.strip():
                    cur.execute("INSERT INTO Building (BuildingName, Address) VALUES (?, ?);",
                                (b_name, b_addr))
                    conn.commit()
                    st.success(f"Building '{b_name}' added.")
                    st.rerun()
                else:
                    st.warning("Building name is required.")

        st.write("**Add a Staff Member**")
        with st.form("add_staff", clear_on_submit=True):
            s_name = st.text_input("Full Name")
            s_email = st.text_input("Email")
            s_spec = st.text_input("Specialty (must match a Category name)")
            s_phone = st.text_input("Phone")
            if st.form_submit_button("Add Staff"):
                if s_name.strip() and s_email.strip():
                    cur.execute(
                        "INSERT INTO Staff (FullName, Email, Specialty, Phone) VALUES (?, ?, ?, ?);",
                        (s_name, s_email, s_spec, s_phone),
                    )
                    conn.commit()
                    st.success(f"Staff member '{s_name}' added.")
                    st.rerun()
                else:
                    st.warning("Name and email are required.")

        st.write("**Add a Facility**")
        cur.execute("SELECT BuildingID, BuildingName FROM Building;")
        buildings_list = cur.fetchall()
        with st.form("add_facility", clear_on_submit=True):
            f_name = st.text_input("Facility Name")
            f_type = st.selectbox("Facility Type", ["Printer", "Washing Machine", "Other"])
            f_building = st.selectbox(
                "Building", [b[1] for b in buildings_list]
            ) if buildings_list else None
            if st.form_submit_button("Add Facility"):
                if f_name.strip() and f_building:
                    building_id = [b[0] for b in buildings_list if b[1] == f_building][0]
                    cur.execute(
                        "INSERT INTO Facility (FacilityName, FacilityType, BuildingID) VALUES (?, ?, ?);",
                        (f_name, f_type, building_id),
                    )
                    conn.commit()
                    st.success(f"Facility '{f_name}' added.")
                    st.rerun()
                else:
                    st.warning("Facility name and building are required.")

    with tab6:
        st.markdown(
            "<h3 style='margin-bottom:0;'>📊 Maintenance Insights</h3>"
            "<p style='color:#888; margin-top:0;'>Data-driven view of where problems cluster and when they spike.</p>",
            unsafe_allow_html=True,
        )

        try:
            import pandas as pd
            import altair as alt
            from analytics import get_hotspots, get_daily_series, get_anomalies

            NAVY = "#1B3B6F"
            GOLD = "#D4A537"
            GREEN = "#3E8E5A"
            RED = "#B03A2E"

            hotspots = get_hotspots()
            daily_series = get_daily_series()
            anomalies = get_anomalies()
            anomaly_dates = {a["Date"] for a in anomalies}

            total_requests = sum(d["Count"] for d in daily_series)
            high_hotspots = sum(1 for h in hotspots if h.get("Activity Level") == "High")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Requests", total_requests)
            m2.metric("Buildings Monitored", len({h["Building"] for h in hotspots}))
            m3.metric("🔥 High-Activity Hotspots", high_hotspots)
            m4.metric("⚠️ Anomaly Days Detected", len(anomalies))

            st.divider()

            st.markdown("#### 🔥 Hotspots — Building × Category Activity")
            st.caption("Unsupervised clustering (KMeans) groups combinations by request volume into activity tiers.")

            if hotspots:
                hs_df = pd.DataFrame(hotspots)
                hs_df["Label"] = hs_df["Building"] + " — " + hs_df["Category"]

                top = hs_df.iloc[0]
                with st.container(border=True):
                    st.markdown(
                        f"**🏆 Top hotspot:** {top['Building']} — {top['Category']} "
                        f"&nbsp;·&nbsp; **{top['Requests']} requests** &nbsp;·&nbsp; "
                        f"activity tier: **{top['Activity Level']}**"
                    )

                color_scale = alt.Scale(domain=["Low", "Medium", "High"], range=[GREEN, GOLD, RED])
                chart = (
                    alt.Chart(hs_df)
                    .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8, size=18)
                    .encode(
                        x=alt.X("Requests:Q", title="Number of Requests", axis=alt.Axis(grid=True, gridOpacity=0.15)),
                        y=alt.Y("Label:N", sort="-x", title=None, axis=alt.Axis(labelLimit=280, labelFontSize=12)),
                        color=alt.Color("Activity Level:N", scale=color_scale, legend=alt.Legend(title="Activity", orient="right")),
                        tooltip=["Building", "Category", "Requests", "Activity Level"],
                    )
                    .properties(height=max(240, len(hs_df) * 36))
                    .configure_view(strokeWidth=0)
                    .configure_axis(labelColor="#444", titleColor="#444", domainColor="#ccc")
                )
                st.altair_chart(chart, width="stretch")

                st.markdown("**Heatmap view**")
                pivot = hs_df.pivot_table(index="Building", columns="Category", values="Requests", fill_value=0)

                def heat_color(val, vmin, vmax):
                    frac = 0.0 if vmax == vmin else (val - vmin) / (vmax - vmin)
                    r1, g1, b1 = (255, 250, 235)   # soft cream (low)
                    r2, g2, b2 = (176, 58, 46)     # deep red (high)
                    r = int(r1 + (r2 - r1) * frac)
                    g = int(g1 + (g2 - g1) * frac)
                    b = int(b1 + (b2 - b1) * frac)
                    text_color = "white" if frac > 0.55 else "#222"
                    return f"background-color: rgb({r},{g},{b}); color: {text_color}; font-weight: 600;"

                vmin, vmax = pivot.values.min(), pivot.values.max()
                styled = pivot.style.map(lambda v: heat_color(v, vmin, vmax)).format(precision=0)
                st.dataframe(styled, width="stretch")
            else:
                st.info("Not enough data yet to detect hotspots.")

            st.divider()

            st.markdown("#### 📈 Request Volume Over Time — Anomaly Detection")
            st.caption("Z-score method: flags days where volume is more than 2 standard deviations above average.")

            if daily_series:
                ts_df = pd.DataFrame(daily_series)
                ts_df["Anomaly"] = ts_df["Date"].apply(lambda d: "Anomaly" if d in anomaly_dates else "Normal")

                if anomalies:
                    worst = max(anomalies, key=lambda a: a["Z-Score"])
                    with st.container(border=True):
                        st.markdown(
                            f"**⚠️ Sharpest spike:** {worst['Date']} &nbsp;·&nbsp; "
                            f"**{worst['Request Count']} requests** in one day "
                            f"&nbsp;·&nbsp; Z-score **{worst['Z-Score']}**"
                        )

                base_scale = alt.Scale(domain=["Normal", "Anomaly"], range=[NAVY, RED])
                area = (
                    alt.Chart(ts_df)
                    .mark_area(color=NAVY, opacity=0.08)
                    .encode(x=alt.X("Date:T", title=None), y=alt.Y("Count:Q", title="Requests per Day"))
                )
                line = (
                    alt.Chart(ts_df)
                    .mark_line(color=NAVY, opacity=0.6, strokeWidth=2)
                    .encode(x="Date:T", y="Count:Q")
                )
                points = (
                    alt.Chart(ts_df)
                    .mark_circle(size=90, stroke="white", strokeWidth=1)
                    .encode(
                        x="Date:T",
                        y="Count:Q",
                        color=alt.Color("Anomaly:N", scale=base_scale, legend=alt.Legend(title=None, orient="top")),
                        tooltip=["Date:T", "Count:Q", "Anomaly:N"],
                    )
                )
                combo = (
                    (area + line + points)
                    .properties(height=340)
                    .configure_view(strokeWidth=0)
                    .configure_axis(labelColor="#444", titleColor="#444", domainColor="#ccc", gridOpacity=0.15)
                )
                st.altair_chart(combo, width="stretch")

                if anomalies:
                    st.markdown("**Flagged anomaly days:**")
                    st.dataframe(anomalies, width="stretch", hide_index=True)
                else:
                    st.info("No anomalies detected in the current data.")
            else:
                st.info("Not enough historical data yet — run generate_history.py for a fuller demo.")

        except ImportError as e:
            st.warning(f"Analytics dependency missing: {e}. Run: pip install scikit-learn pandas altair")
        except Exception as e:
            st.warning(f"Analytics unavailable: {e}")

    conn.close()


# ---------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------
if not st.session_state.logged_in:
    show_login()
else:
    with st.sidebar:
        st.write(f"Logged in as **{st.session_state.email}**")
        st.write(f"Role: **{st.session_state.role}**")
        if st.button("Log out"):
            logout()
            st.rerun()

    if st.session_state.role == "Student":
        student_view()
    elif st.session_state.role == "Staff":
        staff_view()
    elif st.session_state.role == "Admin":
        admin_view()