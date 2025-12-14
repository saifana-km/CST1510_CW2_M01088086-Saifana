import sqlite3
from pathlib import Path
DB_Path = Path(__file__).parent.parent.parent / "DATA" / "intelligence_platform.db"

def connect_database():
    # Go up from app/data/db.py -> app/data -> app -> Week07-10_App -> DATA
    DB_Path = Path(__file__).parent.parent.parent / "DATA" / "intelligence_platform.db"
    
    # Debug: print the resolved path
    print(f"DEBUG: Connecting to DB at: {DB_Path.resolve()}")
    
    if not DB_Path.exists():
        raise FileNotFoundError(f"Database file not found at: {DB_Path.resolve()}")
    
    return sqlite3.connect(str(DB_Path))
