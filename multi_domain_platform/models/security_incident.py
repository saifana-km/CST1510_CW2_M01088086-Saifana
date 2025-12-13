from typing import List, Optional
from services.database_manager import DatabaseManager
from datetime import datetime

class SecurityIncident:
    def __init__(self, incident_id: int, date: str, incident_type: str,
                 severity: str, status: str, description: str,
                 reported_by: str, created_at: str):
        self.__id = incident_id
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
        self.__created_at = created_at

    # --- Getters ---
    def get_id(self) -> int: return self.__id
    def get_date(self) -> str: return self.__date
    def get_incident_type(self) -> str: return self.__incident_type
    def get_severity(self) -> str: return self.__severity
    def get_status(self) -> str: return self.__status
    def get_description(self) -> str: return self.__description
    def get_reported_by(self) -> str: return self.__reported_by
    def get_created_at(self) -> str: return self.__created_at

    # --- Update status in memory ---
    def update_status(self, new_status: str) -> None:
        self.__status = new_status

    # --- Severity mapping ---
    def get_severity_level(self) -> int:
        mapping = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return mapping.get(self.__severity.lower(), 0)

    # --- String representation ---
    def __str__(self) -> str:
        return (
            f"Incident {self.__id} | Date: {self.__date} | Type: {self.__incident_type} | "
            f"Severity: {self.__severity.upper()} | Status: {self.__status} | "
            f"Reported by: {self.__reported_by} | Description: {self.__description}"
        )

    # --- Class methods for CRUD ---
    @classmethod
    def load_all(cls, db: DatabaseManager) -> List["SecurityIncident"]:
        rows = db.fetch_all(
            "SELECT id, date, incident_type, severity, status, description, reported_by, created_at FROM cyber_incidents"
        )
        return [cls(*row) for row in rows] if rows else []

    @classmethod
    def search(cls, db: DatabaseManager, query: str) -> List["SecurityIncident"]:
        q = query.strip()
        try:
            iid = int(q)
            rows = db.fetch_all(
                "SELECT id, date, incident_type, severity, status, description, reported_by, created_at FROM cyber_incidents WHERE id = ?",
                (iid,)
            )
        except ValueError:
            q_like = f"%{q}%"
            rows = db.fetch_all(
                "SELECT id, date, incident_type, severity, status, description, reported_by, created_at FROM cyber_incidents WHERE incident_type LIKE ? OR reported_by LIKE ? OR description LIKE ?",
                (q_like, q_like, q_like)
            )
        return [cls(*row) for row in rows] if rows else []

    @classmethod
    def insert(cls, db: DatabaseManager, date: str, incident_type: str,
               severity: str, status: str, description: str, reported_by: str) -> Optional[int]:
        db.execute_query(
            "INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (date, incident_type, severity, status, description, reported_by, datetime.utcnow().isoformat())
        )
        last = db.fetch_one("SELECT id FROM cyber_incidents ORDER BY id DESC LIMIT 1")
        return last[0] if last else None

    @classmethod
    def update_status_in_db(cls, db: DatabaseManager, incident_id: int, new_status: str) -> bool:
        db.execute_query("UPDATE cyber_incidents SET status = ? WHERE id = ?", (new_status, incident_id))
        res = db.fetch_one("SELECT id FROM cyber_incidents WHERE id = ?", (incident_id,))
        return bool(res)

    @classmethod
    def delete(cls, db: DatabaseManager, incident_id: int) -> int:
        pre = db.fetch_one("SELECT id FROM cyber_incidents WHERE id = ?", (incident_id,))
        if not pre:
            return 0
        db.execute_query("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
        return 1