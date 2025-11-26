import sqlite3

def insert_it_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date=None, assigned_to=None):
    try:
        cursor = conn.cursor()
        insert_sql = """
        INSERT INTO it_tickets (
            ticket_id, priority, status, category, subject, description, 
            created_date, resolved_date, assigned_to
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_sql, (
            ticket_id, priority, status, category, subject, description,
            created_date, resolved_date, assigned_to
        ))
        conn.commit()
        print(f"✅ Ticket {ticket_id} inserted successfully!")
    except Exception as e:
        print(f"❌ Error inserting ticket {ticket_id}: {e}")