SELECT RequestID, Description, Priority, Status, DateReported
FROM MaintenanceRequest
WHERE Status NOT IN ('Resolved','Closed')
ORDER BY
    CASE Priority
        WHEN 'Urgent' THEN 1
        WHEN 'High'   THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low'    THEN 4
    END;

SELECT c.CategoryName, COUNT(r.RequestID) AS TotalRequests
FROM Category c
LEFT JOIN MaintenanceRequest r ON c.CategoryID = r.CategoryID
GROUP BY c. CategoryName
ORDER BY TotalRequests DESC;

SELECT
    r.RequestID,
    s.FullName      AS Student,
    b.BuildingName,
    rm.RoomNumber,
    c.CategoryName,
    r.Description,
    r.Priority,
    r.Status,
    st.FullNane    AS AssignedStaff
FROM MaintenanceRequest r
JOIN Student s   ON r.StudentID = s.StudentID
JOIN Room rm     ON r.RoomID = rm.RoomID
JOIN Building b  ON rm.BuildingID = b.BuildingID
JOIN Category c  ON r.CategoryID = c.CategoryID
LEFT JOIN Staff st ON rAssignedStaffID = st.StaffID
ORDER BY r.RequestID;

SELECT r.RequestID, s.FullName AS Student, c.CategoryName, r.Priority, r.DateReported
FROM MaintenanceRequest r
JOIN Student s  ON r.StudentID = s.StudentID
JOIN Category c ON r.CategoryID = c.CategoryID
WHERE r.AssignedStaffID IS NULL
ORDER BY r.DateReported;

SELECT st.FullName, st.Speciality, COUNT(r.RequestID) AS ActiveRequests
FROM Staff st
LEFT JOIN MaintenanceRequest r
    ON st.StaffID = r.AssignedStaffID AND rStatus NOT IN ('Resolved', 'Closed')
GROUP BY st.FullName, stSpeciality
ORDER BY ActiveRequests DESC;

SELECT su.UpdateDate, su.NewStatus, su.Note, st.FullName AS UpdatedBy
FROM StatusUpdate su
JOIN Staff st ON su.StaffID = st.StaffID
WHERE su.RequestID = 1
ORDER BY su.UpdateDate;

SELECT s.FullName, s.Email, COUNT(r.RequestID) AS RequestCount
From Student s
JOIN MaintenanceRequest r ON s.StudentID = r.StudentID
GROUP BY s.FullName, s.Email
HAVING COUNT(r.RequestID) > 1;

SELECT b.BuildingName, COUNT(r.RequestID) AS TotalRequests
FROM Building b
JOIN Room rm ON b.BuildingID = rm.BuildingID
JOIN MaintenanceRequest r ON rm.RoomID = r.RoomID
GROUP BY b.BuildingName
ORDER BY TotalRequests DESC;
