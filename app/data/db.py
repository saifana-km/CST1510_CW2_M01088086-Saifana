import sqlite3
from pathlib import Path

# Database connection function
#-----------------------------------------------------------------------------
DB_PATH = Path("DATA") / "intelligence_platform.db"
def connect_database(db_path=DB_PATH):
    return sqlite3.connect(str(db_path))
