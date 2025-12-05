import sqlite3
import pandas as pd
from app.data.db import connect_database

def insert_it_ticket(ticket_id, priority, status, category, subject, description, created_date, resolved_date=None, assigned_to=None):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    conn.commit()
    itticket_id = cursor.lastrowid
    conn.close()
    return itticket_id

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
    sql = "UPDATE it_tickets SET status = ? WHERE id = ?"
    cursor.execute(sql, (new_status, ticket_id))
    conn.commit()
    return cursor.rowcount

def delete_ticket(conn, ticket_id):
    cursor = conn.cursor()
    sql = "DELETE FROM it_tickets WHERE id = ?"
    cursor.execute(sql, (ticket_id,))
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