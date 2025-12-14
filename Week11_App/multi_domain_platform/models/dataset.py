import pandas as pd
from services.database_manager import DatabaseManager
from datetime import datetime
from typing import Optional


class Dataset:
    def __init__(self, dataset_id: int, dataset_name: str, category: str,
                 source: str, last_updated: str, record_count: int,
                 file_size_mb: float, created_at: str):
        self.__id = dataset_id
        self.__name = dataset_name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb
        self.__created_at = created_at

    # --- Factory method to build from DB row ---
    @classmethod
    def from_db_row(cls, row: tuple) -> "Dataset":
        return cls(*row)

    # --- Getters ---
    def get_id(self) -> int: return self.__id
    def get_name(self) -> str: return self.__name
    def get_category(self) -> str: return self.__category
    def get_source(self) -> str: return self.__source
    def get_last_updated(self) -> str: return self.__last_updated
    def get_record_count(self) -> int: return self.__record_count
    def get_file_size_mb(self) -> float: return self.__file_size_mb
    def get_created_at(self) -> str: return self.__created_at

    # --- Helpers ---
    def calculate_size_gb(self) -> float:
        return self.__file_size_mb / 1024

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "name": self.__name,
            "category": self.__category,
            "source": self.__source,
            "last_updated": self.__last_updated,
            "record_count": self.__record_count,
            "file_size_mb": self.__file_size_mb,
            "created_at": self.__created_at,
        }

    def __str__(self) -> str:
        return (f"Dataset {self.__id}: {self.__name} "
                f"({self.__file_size_mb:.2f} MB, {self.__record_count} records, "
                f"Category: {self.__category}, Source: {self.__source})")

    # -------------------------
    # Class-level DB operations using DatabaseManager
    # -------------------------
    @classmethod
    def insert_dataset(cls, db: "DatabaseManager", dataset_name: str, category: str, source: str,
                       last_updated: Optional[str] = None,
                       record_count: Optional[int] = None,
                       file_size_mb: Optional[float] = None) -> int:
        """Insert a new dataset metadata record and return generated id."""
        if last_updated is None:
            last_updated = datetime.now().strftime("%Y-%m-%d")
        cur = db.execute_query("""
            INSERT INTO datasets_metadata
            (dataset_name, category, source, last_updated, record_count, file_size_mb)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
        return cur.lastrowid

    @classmethod
    def get_all_datasets(cls, db: "DatabaseManager") -> pd.DataFrame:
        """Return all datasets as a pandas DataFrame ordered by id desc."""
        rows = db.fetch_all("SELECT * FROM datasets_metadata ORDER BY id DESC")
        return pd.DataFrame(rows, columns=[
            "id", "dataset_name", "category", "source",
            "last_updated", "record_count", "file_size_mb", "created_at"
        ])

    @classmethod
    def get_dataset_by_name(cls, db: "DatabaseManager", dataset_name: str) -> pd.DataFrame:
        """Return dataset(s) by name LIKE or by numeric id."""
        try:
            id_val = int(dataset_name)
            rows = db.fetch_all("SELECT * FROM datasets_metadata WHERE id = ?", (id_val,))
        except ValueError:
            rows = db.fetch_all(
                "SELECT * FROM datasets_metadata WHERE dataset_name LIKE ? ORDER BY id DESC",
                (f"%{dataset_name}%",))
        return pd.DataFrame(rows, columns=[
            "id", "dataset_name", "category", "source",
            "last_updated", "record_count", "file_size_mb", "created_at"
        ])

    @classmethod
    def update_dataset_last_updated(cls, db: "DatabaseManager", dataset_id: int,
                                    new_date: Optional[str] = None) -> int:
        """Update last_updated for a dataset identified by id. Returns affected rowcount."""
        if new_date is None:
            new_date = datetime.now().strftime("%Y-%m-%d")
        cur = db.execute_query("UPDATE datasets_metadata SET last_updated = ? WHERE id = ?",
                               (new_date, dataset_id))
        return cur.rowcount

    @classmethod
    def update_dataset_record_count(cls, db: "DatabaseManager", dataset_id: int, new_count: int) -> int:
        """Update record_count for a dataset identified by id. Returns affected rowcount."""
        cur = db.execute_query("UPDATE datasets_metadata SET record_count = ? WHERE id = ?",
                               (new_count, dataset_id))
        return cur.rowcount

    @classmethod
    def delete_dataset(cls, db: "DatabaseManager", dataset_id: int) -> int:
        """Delete a dataset by id and return number of deleted rows."""
        cur = db.execute_query("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
        return cur.rowcount

    @classmethod
    def get_datasets_by_category(cls, db: "DatabaseManager") -> pd.DataFrame:
        """Return counts of datasets grouped by category as DataFrame."""
        rows = db.fetch_all("""
            SELECT category, COUNT(*) as count
            FROM datasets_metadata
            GROUP BY category
            ORDER BY count DESC
        """)
        return pd.DataFrame(rows, columns=["category", "count"])

    @classmethod
    def get_large_datasets(cls, db: "DatabaseManager", min_size_mb: float = 100) -> pd.DataFrame:
        """Return datasets with file_size_mb > min_size_mb as DataFrame."""
        rows = db.fetch_all("""
            SELECT dataset_name, file_size_mb
            FROM datasets_metadata
            WHERE file_size_mb > ?
            ORDER BY file_size_mb DESC
        """, (min_size_mb,))
        return pd.DataFrame(rows, columns=["dataset_name", "file_size_mb"])