from services.database_manager import DatabaseManager
from datetime import datetime
from typing import Optional
import pandas as pd

class ITTicket:
    def __init__(self, ticket_id: str, title: str, priority: str,
                 status: str, assigned_to: str,
                 category: Optional[str] = None,
                 description: Optional[str] = None,
                 created_date: Optional[str] = None,
                 resolved_date: Optional[str] = None):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assigned_to
        self.__category = category
        self.__description = description
        self.__created_date = created_date
        self.__resolved_date = resolved_date

    # --- Instance methods ---
    def assign_to(self, staff: str) -> None:
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        self.__status = "Closed"
        self.__resolved_date = datetime.now().strftime("%Y-%m-%d")

    def get_status(self) -> str:
        return self.__status

    def __str__(self) -> str:
        return (f"Ticket {self.__id}: {self.__title} "
                f"[{self.__priority}] – {self.__status} "
                f"(assigned to: {self.__assigned_to})")

    def to_dict(self) -> dict:
        return {
            "ticket_id": self.__id,
            "title": self.__title,
            "priority": self.__priority,
            "status": self.__status,
            "assigned_to": self.__assigned_to,
            "category": self.__category,
            "description": self.__description,
            "created_date": self.__created_date,
            "resolved_date": self.__resolved_date,
        }

    # -------------------------
    # Class-level DB operations
    # -------------------------
    @classmethod
    def insert_ticket(cls, db: "DatabaseManager", priority: str, status: str,
                      category: str, subject: str, description: str,
                      created_date: Optional[str], resolved_date: Optional[str],
                      assigned_to: str) -> str:
        """Insert a new IT ticket and return generated ticket_id."""
        count_row = db.fetch_one("SELECT COUNT(*) FROM it_tickets")
        count = count_row[0] + 1
        ticket_id = f"TCK-{count:04d}"

        db.execute_query("""
            INSERT INTO it_tickets
            (ticket_id, priority, status, category, subject, description,
             created_date, resolved_date, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, priority, status, category, subject,
              description, created_date, resolved_date or None, assigned_to))
        return ticket_id

    @classmethod
    def get_all_tickets(cls, db: "DatabaseManager") -> pd.DataFrame:
        """Return tickets as DataFrame using DB helper (keeps DB schema columns)."""
        sql = "SELECT * FROM it_tickets ORDER BY id DESC"
        try:
            df = db.fetch_df(sql)
        except Exception:
            # fallback: return empty dataframe
            df = pd.DataFrame()
        return df

    @classmethod
    def update_ticket_status(cls, db: "DatabaseManager", ticket_id: str, new_status: str) -> str:
        db.execute_query("UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
                         (new_status, ticket_id))
        return ticket_id

    @classmethod
    def delete_ticket(cls, db: "DatabaseManager", ticket_id: str) -> int:
        cur = db.execute_query("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
        return cur.rowcount

    @classmethod
    def search_ticket(cls, db: "DatabaseManager", ticket_id: str) -> Optional["ITTicket"]:
        row = db.fetch_one("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
        if row:
            return ITTicket(
                ticket_id=row[1],  # ticket_id
                title=row[5],      # subject
                priority=row[2],
                status=row[3],
                assigned_to=row[9],
                category=row[4],
                description=row[6],
                created_date=row[7],
                resolved_date=row[8]
            )
        return None