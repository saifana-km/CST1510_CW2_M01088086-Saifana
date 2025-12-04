import sqlite3
import os
import pandas as pd
from pathlib import Path
from app.data.db import connect_database 
from app.data.users import migrate_users_from_file
DB_PATH = Path("DATA") / "intelligence_platform.db"

def create_users_table(conn):
    cursor = conn.cursor()
    
    # SQL statement to create users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Users table created successfully!")

def create_cyber_incidents_table(conn):
    cursor = conn.cursor()
    
    # SQL statement to create cyber_incidents table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')) NOT NULL,
        status TEXT CHECK(status IN ('Open', 'Investigating', 'Resolved', 'Closed')) NOT NULL,
        description TEXT,
        reported_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Cyber Incidents table created successfully!")


def create_datasets_metadata_table(conn):
    cursor = conn.cursor()

    # SQL statement to create datasets_metadata table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        category TEXT NOT NULL,
        source TEXT NOT NULL,
        last_updated TEXT,
        record_count INTEGER,
        file_size_mb REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Datasets Metadata table created successfully!")

def create_it_tickets_table(conn):
    cursor = conn.cursor()
    
    # SQL statement to create it_tickets table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        priority TEXT CHECK(priority IN ('Critical', 'High', 'Medium', 'Low')),
        status TEXT CHECK(status IN ('Open', 'Investigating', 'Resolved', 'Closed')),
        category TEXT,
        subject TEXT NOT NULL,
        description TEXT,
        created_date TEXT NOT NULL,
        resolved_date TEXT,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ IT Tickets table created successfully!")

def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

def load_csv_to_table(conn, csv_path, table_name, if_exists='append'):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    df.to_sql(
        name=table_name,
        con=conn,
        if_exists=if_exists,  
        index=False          
    )
    row_count = len(df)
    print(f"✅ Successfully loaded {row_count} rows into '{table_name}'.")
    return row_count


def load_all_csv_data(conn, directory, if_exists='append'):
    results = {}
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for csv_file in directory.glob("*.csv"):
        table_name = csv_file.stem
        df = pd.read_csv(csv_file)

        df.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=False
        )

        row_count = len(df)
        results[table_name] = row_count
        print(f"✅ Loaded {row_count} rows into '{table_name}' from {csv_file.name}")

    return results


def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    load_csv_to_table(conn, "DATA","it_tickets")
    
    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    
    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")

setup_database_complete()
