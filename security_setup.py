import sqlite3
import hashlib
import os

DB_FILE = "maintenance.db"


def hash_password(password: str) -> str:
    """
    Turns a plain-text password into a secure, irreversible hash.
    A random 'salt' is added so that two users with the same password
    don't end up with the same stored hash.
    """
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    # Store salt + hash together, separated by a colon, so we can verify later
    return salt.hex() + ":" + pwd_hash.hex()


def verify_password(password: str, stored: str) -> bool:
    """Checks a plain-text password attempt against a stored hash."""
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return pwd_hash.hex() == hash_hex


def add_login_table():
    """
    Adds a UserAccount table to the existing database:
    - links to either a Student or a Staff member
    - stores a hashed password, never plain text
    - stores a role, used to control what the account can access
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserAccount (
            UserID         INTEGER PRIMARY KEY AUTOINCREMENT,
            Email          TEXT NOT NULL UNIQUE,
            PasswordHash   TEXT NOT NULL,
            Role           TEXT NOT NULL CHECK (Role IN ('Student', 'Staff', 'Admin'))
        );
    """)
    conn.commit()
    conn.close()
    print("UserAccount table ready.")


def create_demo_accounts():
    """Creates a few demo accounts so login can be tested end-to-end."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    demo_users = [
        ("lindiwe.d@ufh.ac.za", "student123", "Student"),
        ("vusi.m@residence.ac.za", "staffpass1", "Staff"),
        ("admin@residence.ac.za", "adminpass1", "Admin"),
    ]

    for email, plain_password, role in demo_users:
        hashed = hash_password(plain_password)
        try:
            cur.execute(
                "INSERT INTO UserAccount (Email, PasswordHash, Role) VALUES (?, ?, ?);",
                (email, hashed, role),
            )
        except sqlite3.IntegrityError:
            pass  # account already exists, skip

    conn.commit()
    conn.close()
    print("Demo accounts created (or already existed).")


def test_login(email: str, attempt: str):
    """Simulates a login attempt against the stored hash."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT PasswordHash, Role FROM UserAccount WHERE Email = ?;", (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        print(f"No account found for {email}")
        return

    stored_hash, role = row
    if verify_password(attempt, stored_hash):
        print(f"Login successful for {email} (Role: {role})")
    else:
        print(f"Login FAILED for {email}")


if __name__ == "__main__":
    add_login_table()
    create_demo_accounts()

    print("\n--- Testing logins ---")
    test_login("lindiwe.d@ufh.ac.za", "student123")   # correct password
    test_login("lindiwe.d@ufh.ac.za", "wrongpass")    # wrong password
    test_login("admin@residence.ac.za", "adminpass1") # correct password