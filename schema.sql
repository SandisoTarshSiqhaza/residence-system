-- Student Residence Maintenance Reporting System
-- Database schema (SQLite syntax; portable to MySQL/PostgreSQL with minor tweaks)

PRAGMA foreign_keys = ON;

CREATE TABLE Building (
    BuildingID     INTEGER PRIMARY KEY AUTOINCREMENT,
    BuildingName   TEXT NOT NULL UNIQUE,
    Address        TEXT
);

CREATE TABLE Room (
    RoomID         INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomNumber     TEXT NOT NULL,
    Floor          INTEGER,
    BuildingID     INTEGER NOT NULL,
    FOREIGN KEY (BuildingID) REFERENCES Building(BuildingID),
    UNIQUE (BuildingID, RoomNumber)
); 

CREATE TABLE Student (
StudentID  INTEGER PRIMARY KEY AUTOINCREMENT,
FullName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Phone TEXT,
    RoomID INTEGER NOT NULL,
    FOREIGN KEY (RoomID) REFERENCES
    Room (RoomID)
    );

CREATE TABLE Category(
    CategoryID  INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL UNIQUE
    );

CREATE TABLE Staff (
    StaffID  INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Speciality TEXT NOT NULL,
    Phone TEXT 
    );

CREATE TABLE MaintenanceRequest(
    RequestID  INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID  INTEGER NOT NULL,
    RoomID  INTEGER NOT NULL,
    CategoryID INTEGER NOT NULL,
    Description TEXT NOT NULL, 
    DateReported  TEXT NOT NULL DEFAULT (date('now')),
    Priority  TEXT NOT NULL DEFAULT 'Unrated', 'Low', 'Medium', 'High', 'Urgent')),
Status  TEXT NOT NULL DEFAULT 'Submitted'
CHECK (Status IN ('Submitted', 'In Progress', 'Resolved', 'Closed')),
Assigned StaffID INTEGER,
FOREIGN KEY (StudentID) REFERENCES
Student (StudentID)
FOREIGN KEY (RoomID) REFERENCES
Room(RoomID),
FOREIGN KEY (CategoryID) REFERENCES 
Category(CategoryID),
FOREIGN KEY (AssignedStaffID) REFERENCES 
Staff(StaffID0
    );

CREATE TABLE StatusUpdate (
    LogID  INTEGER PRIMARY KEY AUTOINCREMENT,
    Request ID  INTEGER NOT NULL,
    StaffID  INTEGER,
    Note  TEXT,
    UpdateDAte  TEXT NOT N ULL DEFAULT (date ('now')),
    NewStatus  TEXT NOT NULL 
    CHECK (NewStatus IN ('Submitted', 'In Progress', 'Resolved', 'Closed')),
    FOREIGN KEY(RequestID) REFERENCES  
    MaintainceRequest (RequestID),
    FOREIGN KEY (StaffID ) REFERENCES
    Staff(StaffID)
    );

--------------------------------------------------------------------
--Facility Booking
--------------------------------------------------------------------
CREATE TABLE Facility (
    Facility


    
    
    
