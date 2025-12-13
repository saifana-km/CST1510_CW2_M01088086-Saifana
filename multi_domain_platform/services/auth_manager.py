from typing import Optional
from models.user import User
from services.database_manager import DatabaseManager
from pathlib import Path
import sqlite3
import bcrypt
import streamlit as st   # only if you’re using Streamlit session state

DATA_DIR = Path("DATA")

class BcryptHasher:
    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class AuthManager:
    """Handles user registration, login, and migration."""

    def __init__(self, db: DatabaseManager):
        self._db = db

    # --- Registration ---
    def register_user(self, username: str, password: str, role: str = "user") -> tuple[bool, str]:
        """Register a new user with hashed password. Returns (success, message)."""
        existing = self.get_user_by_username(username)
        if existing:
            return False, f"Username '{username}' is already taken."

        password_hash = BcryptHasher.hash_password(password)
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return True, f"User '{username}' registered successfully."

    # --- Login ---
    def login_user(self, username: str, password: str) -> Optional[User]:
        """Attempt to log in a user. Returns User object if successful, else None."""
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        if row is None:
            return None

        username_db, password_hash_db, role_db = row
        if BcryptHasher.check_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)
        return None

    # --- Get user by username ---
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Look up a user by username and return a User object."""
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        if row:
            return User(row[0], row[1], row[2])
        return None

    # --- Insert user with pre-hashed password ---
    def insert_user(self, username: str, password_hash: str, role: str = "user") -> None:
        """Insert a user when you already have a hashed password (e.g. migration)."""
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )

    # --- Migrate users from file ---
    def migrate_users_from_file(self, filepath: Path = DATA_DIR / "users.txt") -> None:
        """Bulk import users from a text file (username,password_hash)."""
        if not filepath.exists():
            print(f"⚠️ File not found: {filepath}")
            print("   No users to migrate.")
            return

        conn = sqlite3.connect(self._db._db_path)  # direct sqlite3 for bulk ops
        cursor = conn.cursor()
        migrated_count = 0

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(",")
                if len(parts) >= 2:
                    username = parts[0]
                    password_hash = parts[1]

                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                            (username, password_hash, "user"),
                        )
                        if cursor.rowcount > 0:
                            migrated_count += 1
                    except sqlite3.Error as e:
                        print(f"Error migrating user {username}: {e}")

        conn.commit()
        conn.close()
        print(f"✅ Migrated {migrated_count} users from {filepath.name}")

    # --- Logout (for Streamlit apps) ---
    def logout_user(self) -> None:
        """Clear current user from Streamlit session state."""
        if "current_user" in st.session_state:
            del st.session_state["current_user"]
        if "current_role" in st.session_state:
            del st.session_state["current_role"]
        st.success("You have been logged out.")