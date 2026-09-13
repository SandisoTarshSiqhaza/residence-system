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
    StudentID      INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName       TEXT NOT NULL,
    Email          TEXT NOT NULL UNIQUE,
    Phone          TEXT,
    RoomID         INTEGER NOT NULL,
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

CREATE TABLE Category (
    CategoryID     INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName   TEXT NOT NULL UNIQUE
);

CREATE TABLE Staff (
    StaffID        INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName       TEXT NOT NULL,
    Email          TEXT NOT NULL UNIQUE,
    Specialty      TEXT NOT NULL,
    Phone          TEXT
);

CREATE TABLE MaintenanceRequest (
    RequestID       INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID       INTEGER NOT NULL,
    RoomID          INTEGER NOT NULL,
    CategoryID      INTEGER NOT NULL,
    Description     TEXT NOT NULL,
    DateReported    TEXT NOT NULL DEFAULT (date('now')),
    Priority        TEXT NOT NULL DEFAULT 'Unrated'
                    CHECK (Priority IN ('Unrated', 'Low', 'Medium', 'High', 'Urgent')),
    Status          TEXT NOT NULL DEFAULT 'Submitted'
                    CHECK (Status IN ('Submitted', 'In Progress', 'Resolved', 'Closed')),
    AssignedStaffID INTEGER,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    FOREIGN KEY (AssignedStaffID) REFERENCES Staff(StaffID)
);

CREATE TABLE StatusUpdate (
    LogID          INTEGER PRIMARY KEY AUTOINCREMENT,
    RequestID      INTEGER NOT NULL,
    StaffID        INTEGER,
    Note           TEXT,
    UpdateDate     TEXT NOT NULL DEFAULT (date('now')),
    NewStatus      TEXT NOT NULL
                   CHECK (NewStatus IN ('Submitted', 'In Progress', 'Resolved', 'Closed')),
    FOREIGN KEY (RequestID) REFERENCES MaintenanceRequest(RequestID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
);

-- ---------------------------------------------------------------------
-- Facility Booking
-- ---------------------------------------------------------------------
CREATE TABLE Facility (
    FacilityID     INTEGER PRIMARY KEY AUTOINCREMENT,
    FacilityName   TEXT NOT NULL,
    FacilityType   TEXT NOT NULL CHECK (FacilityType IN ('Printer', 'Washing Machine', 'Other')),
    BuildingID     INTEGER NOT NULL,
    FOREIGN KEY (BuildingID) REFERENCES Building(BuildingID)
);

CREATE TABLE Booking (
    BookingID      INTEGER PRIMARY KEY AUTOINCREMENT,
    FacilityID     INTEGER NOT NULL,
    StudentID      INTEGER NOT NULL,
    BookingDate    TEXT NOT NULL,
    StartTime      TEXT NOT NULL,
    EndTime        TEXT NOT NULL,
    Status         TEXT NOT NULL DEFAULT 'Booked'
                   CHECK (Status IN ('Booked', 'Cancelled', 'Completed')),
    CreatedAt      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- ---------------------------------------------------------------------
-- Visitor Sign-In / Sign-Out
-- ---------------------------------------------------------------------
CREATE TABLE Visitor (
    VisitorID      INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName       TEXT NOT NULL,
    Phone          TEXT,
    HostStudentID  INTEGER NOT NULL,
    Purpose        TEXT,
    SignInTime     TEXT NOT NULL DEFAULT (datetime('now')),
    SignOutTime    TEXT,
    FOREIGN KEY (HostStudentID) REFERENCES Student(StudentID)
);