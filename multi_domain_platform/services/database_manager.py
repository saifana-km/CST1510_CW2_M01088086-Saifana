import sqlite3
from typing import Any, Iterable
class DatabaseManager:
    """Handles SQLite database connections and queries."""
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
    def connect(self) -> None:
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur
    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()
    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))   # <-- missing line
        return cur.fetchall()