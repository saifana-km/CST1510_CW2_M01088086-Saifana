import sqlite3
import pandas as pd
from data.db import connect_database

def insert_it_ticket(conn, priority, status, category, subject, description, created_date, resolved_date, assigned_to):
    cursor = conn.cursor()
    # Auto-generate ticket_id with zero padding
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    count = cursor.fetchone()[0] + 1
    ticket_id = f"TCK-{count:04d}"

    cursor.execute("""
        INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, resolved_date or None, assigned_to))
    conn.commit()
    return ticket_id


def get_all_tickets():
    """Get all tickets as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def update_ticket_status(conn, ticket_id, new_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE it_tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    conn.commit()
    return ticket_id

def delete_ticket(conn, ticket_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    return cursor.rowcount

def get_tickets_by_category_count(conn):
    query = """
    SELECT category, COUNT(*) as count
    FROM it_tickets
    GROUP BY category
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_priority_by_status(conn):
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_tickets_category_with_many_cases(conn, min_count=5):
    query = """
    SELECT category, COUNT(*) as count
    FROM it_tickets
    GROUP BY category
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df

def search_ticket(conn, ticket_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    return cursor.fetchone()