import sqlite3

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

# Connect to the database
conn = sqlite3.connect('DATA/intelligence_platform.db')

# Create all tables
create_all_tables(conn)

# Close the connection
conn.close()