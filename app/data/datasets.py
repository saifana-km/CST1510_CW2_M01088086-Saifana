import sqlite3
import pandas as pd
from datetime import datetime

def insert_dataset(dataset_name, category, source, last_updated=None, record_count=None, file_size_mb=None):
    """Insert a new dataset metadata record."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()
    return dataset_id

def get_all_datasets():
    """Get all datasets as a DataFrame."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df

def get_dataset_by_id(dataset_id):
    """Get a single dataset by ID."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    df = pd.read_sql_query("SELECT * FROM datasets_metadata WHERE id = ?", conn, params=(dataset_id,))
    conn.close()
    return df

def update_dataset_last_updated(dataset_id, new_date=None):
    """Update the last_updated field for a dataset."""
    if new_date is None:
        new_date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE datasets_metadata SET last_updated = ? WHERE id = ?", (new_date, dataset_id))
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()
    return rowcount

def update_dataset_record_count(dataset_id, new_count):
    """Update the record_count for a dataset."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE datasets_metadata SET record_count = ? WHERE id = ?", (new_count, dataset_id))
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()
    return rowcount

def delete_dataset(dataset_id):
    """Delete a dataset by ID."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()
    return rowcount

def get_datasets_by_category():
    """Return count of datasets grouped by category."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    df = pd.read_sql_query("""
        SELECT category, COUNT(*) as count
        FROM datasets_metadata
        GROUP BY category
        ORDER BY count DESC
    """, conn)
    conn.close()
    return df

def get_large_datasets(min_size_mb=100):
    """Return datasets larger than a given size in MB."""
    conn = sqlite3.connect("DATA/intelligence_platform.db")
    df = pd.read_sql_query("""
        SELECT dataset_name, file_size_mb
        FROM datasets_metadata
        WHERE file_size_mb > ?
        ORDER BY file_size_mb DESC
    """, conn, params=(min_size_mb,))
    conn.close()
    return df