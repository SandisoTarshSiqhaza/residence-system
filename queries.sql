-- Student Residence Maintenance Reporting System
-- Retrieval Queries

-- 1. All open requests (not yet resolved/closed), most urgent first
SELECT RequestID, Description, Priority, Status, DateReported
FROM MaintenanceRequest
WHERE Status NOT IN ('Resolved', 'Closed')
ORDER BY
    CASE Priority
        WHEN 'Urgent' THEN 1
        WHEN 'High'   THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low'    THEN 4
    END;

-- 2. Number of requests per category
SELECT c.CategoryName, COUNT(r.RequestID) AS TotalRequests
FROM Category c
LEFT JOIN MaintenanceRequest r ON c.CategoryID = r.CategoryID
GROUP BY c.CategoryName
ORDER BY TotalRequests DESC;

-- 3. Full details of every request: student, room, building, category, and assigned staff
SELECT
    r.RequestID,
    s.FullName      AS Student,
    b.BuildingName,
    rm.RoomNumber,
    c.CategoryName,
    r.Description,
    r.Priority,
    r.Status,
    st.FullName     AS AssignedStaff
FROM MaintenanceRequest r
JOIN Student s   ON r.StudentID = s.StudentID
JOIN Room rm     ON r.RoomID = rm.RoomID
JOIN Building b  ON rm.BuildingID = b.BuildingID
JOIN Category c  ON r.CategoryID = c.CategoryID
LEFT JOIN Staff st ON r.AssignedStaffID = st.StaffID
ORDER BY r.RequestID;

-- 4. Requests that are still unassigned (need staff to be allocated)
SELECT r.RequestID, s.FullName AS Student, c.CategoryName, r.Priority, r.DateReported
FROM MaintenanceRequest r
JOIN Student s  ON r.StudentID = s.StudentID
JOIN Category c ON r.CategoryID = c.CategoryID
WHERE r.AssignedStaffID IS NULL
ORDER BY r.DateReported;

-- 5. Current workload per staff member (active, non-resolved requests)
SELECT st.FullName, st.Specialty, COUNT(r.RequestID) AS ActiveRequests
FROM Staff st
LEFT JOIN MaintenanceRequest r
    ON st.StaffID = r.AssignedStaffID AND r.Status NOT IN ('Resolved', 'Closed')
GROUP BY st.FullName, st.Specialty
ORDER BY ActiveRequests DESC;

-- 6. Full audit trail (status history) for a specific request, e.g. RequestID = 1
SELECT su.UpdateDate, su.NewStatus, su.Note, st.FullName AS UpdatedBy
FROM StatusUpdate su
JOIN Staff st ON su.StaffID = st.StaffID
WHERE su.RequestID = 1
ORDER BY su.UpdateDate;

-- 7. Students who have logged more than one maintenance request
SELECT s.FullName, s.Email, COUNT(r.RequestID) AS RequestCount
FROM Student s
JOIN MaintenanceRequest r ON s.StudentID = r.StudentID
GROUP BY s.FullName, s.Email
HAVING COUNT(r.RequestID) > 1;

-- 8. Requests per building (which residence reports the most issues)
SELECT b.BuildingName, COUNT(r.RequestID) AS TotalRequests
FROM Building b
JOIN Room rm ON b.BuildingID = rm.BuildingID
JOIN MaintenanceRequest r ON rm.RoomID = r.RoomID
GROUP BY b.BuildingName
ORDER BY TotalRequests DESC;
