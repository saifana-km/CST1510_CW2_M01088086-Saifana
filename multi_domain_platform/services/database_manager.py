import sqlite3
from typing import Any, Iterable, Optional
from pathlib import Path
import pandas as pd

class DatabaseManager:
    """Lightweight SQLite DB helper exposing execute / fetch / df helpers.
    This implementation will NOT create the database file or parent folders.
    It raises an error if the DB file does not already exist.
    """

    def __init__(self, db_path: str):
        self._db_path = str(db_path)
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        # Do not create parent folder or new DB file. Require existing file.
        db_file = Path(self._db_path)
        if not db_file.is_file():
            raise sqlite3.OperationalError(f"Database file not found: {db_file.resolve()}")
        # allow use from Streamlit threads
        self._connection = sqlite3.connect(str(db_file.resolve()), check_same_thread=False)

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
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    def fetch_df(self, sql: str, params: Iterable[Any] = ()):
        """Return query as pandas DataFrame with proper column names."""
        if self._connection is None:
            self.connect()
        return pd.read_sql_query(sql, self._connection, params=tuple(params))

    @property
    def db_path(self) -> str:
        return self._db_path